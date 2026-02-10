import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="NDI Intelligence", layout="wide", page_icon="📊")

# 2. ESTILO CSS - FUNDO DEGRADÊ E BOTÕES HORIZONTAIS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Fundo em degradê Azul, Laranja e Amarelo */
    .stApp {
        background: linear-gradient(135deg, #1e3a8a 0%, #f97316 50%, #eab308 100%);
        background-attachment: fixed;
    }

    /* Cabeçalho */
    .hero-section {
        text-align: center;
        padding: 60px 0 40px 0;
    }
    .hero-title {
        font-size: 52px;
        font-weight: 800;
        color: white;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 20px;
    }

    /* --- BOTÕES DO HUB (HORIZONTAIS E VIDRO) --- */
    .hub-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
    }

    div.stButton > button {
        background: rgba(255, 255, 255, 0.15) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-radius: 20px !important;
        height: 100px !important;
        width: 100% !important;
        transition: all 0.4s ease !important;
        color: white !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.25) !important;
        transform: translateY(-5px) !important;
        border-color: white !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.2) !important;
    }

    /* Dashboard Interno */
    .metric-box {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 24px;
        padding: 25px;
        text-align: center;
        color: white;
    }
    .metric-label { color: rgba(255,255,255,0.7); font-size: 12px; font-weight: 700; text-transform: uppercase; }
    .metric-value { font-size: 32px; font-weight: 800; margin-top: 8px; }

    /* Estilo das Tabs para combinar com o Vidro */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] {
        color: white !important;
        background: rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 8px 25px;
        margin-right: 5px;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 3. METAS E TRATAMENTO DE DADOS (CONSERVADOS)
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

def limpar_valor(v):
    if pd.isna(v) or str(v).strip() in ["", "None", "nan"]: return None
    try: return float(str(v).replace('%', '').replace(',', '.').strip())
    except: return None

def tma_to_float(v):
    if pd.isna(v) or str(v).strip() in ["", "0", "00:00:00"]: return None
    try:
        p = str(v).split(':')
        if len(p) == 3: return int(p[0]) * 60 + int(p[1]) + int(p[2]) / 60
        return float(str(v).replace(',', '.'))
    except: return None

def cor_kpi(val, met, metas):
    if val is None: return "rgba(255,255,255,0.4)"
    c = metas.get(met)
    if not c: return "white"
    m, tol, menor = c['valor'], c['margem'], c['menor_melhor']
    if menor:
        return "#4ade80" if val <= m else ("#fbbf24" if val <= m + tol else "#f87171")
    return "#4ade80" if val >= m else ("#fbbf24" if val >= m - tol else "#f87171")

@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        cols = {c.lower(): c for c in df.columns}
        for m in list(METAS_BASE.keys()) + ['Pausa Total']:
            orig = cols.get('silencio (%)') if m == 'Silencio' else cols.get(m.lower())
            if not orig: orig = next((c for c in df.columns if m.lower() in c.lower()), None)
            if orig:
                df[f'{m}_num'] = df[orig].apply(tma_to_float if 'TMA' in m or 'Pausa' in m else limpar_valor)
                df[m] = df[orig].astype(str).replace(['nan', 'None'], '---')
        return df, cols.get('operador', 'Operador'), cols.get('matricula', 'Matricula')
    except: return None, None, None

# --- HUB INICIAL ---
if st.session_state.servico is None:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">NDI Performance</h1>
            <p class="hero-subtitle">Gestão Estratégica de Canais</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Alinhamento Horizontal usando colunas
    _, col1, col2, col3, _ = st.columns([0.5, 2, 2, 2, 0.5])
    
    with col1:
        if st.button("🏢 SAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    with col2:
        if st.button("🏦 SAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    with col3:
        if st.button("🏥 SAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()

else:
    # --- ÁREA INTERNA ---
    with st.sidebar:
        st.markdown(f"<h2 style='color:white;'>📍 {st.session_state.servico}</h2>", unsafe_allow_html=True)
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        sup = st.selectbox("Supervisor:", lista)
        st.markdown("<br>"*5, unsafe_allow_html=True)
        if st.button("🏠 Retornar ao Início"):
            st.session_state.servico = None; st.rerun()

    if sup != "Selecione...":
        df, col_op, col_mat = load_data(sup)
        if df is not None:
            m_atuais = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in sup or "Beatriz" in sup) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            m_atuais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["Individual", "Equipe", "Ranking", "Saúde"])

            with tabs[0]:
                mat = st.text_input("Matrícula:", placeholder="Digite sua matrícula...")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"### Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        indicadores = [('Aderencia', '📈'), ('Silencio', '🔇'), ('Resolutividade', '✅'), ('Pausa Total', '⏱️'), ('TMA Voz', '📞'), ('Pesquisa', '⭐')]
                        for i, (m, icon) in enumerate(indicadores):
                            with [c1, c2, c3][i % 3]:
                                color = cor_kpi(r[f'{m}_num'], m, m_atuais)
                                st.markdown(f"""<div class='metric-box' style='border-left: 6px solid {color}'>
                                    <div class='metric-label'>{m}</div>
                                    <div class='metric-value' style='color:{color}'>{icon} {r[m]}</div>
                                </div><br>""", unsafe_allow_html=True)

            with tabs[1]:
                eq = df[df[col_op].astype(str).str.upper() == 'EQUIPE']
                if not eq.empty:
                    eq = eq.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    for i, m in enumerate(['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']):
                        with [c1, c2, c3][i % 3]:
                            color = cor_kpi(eq[f'{m}_num'], m, m_atuais)
                            st.markdown(f"""<div class='metric-box' style='border-left: 6px solid {color}'>
                                <div class='metric-label'>{m} Equipe</div>
                                <div class='metric-value' style='color:{color}'>{eq[m]}</div>
                            </div><br>""", unsafe_allow_html=True)

            with tabs[2]:
                m_rank = st.selectbox("Ranking de:", list(m_atuais.keys()))
                df_r = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_rank}_num'].notna())].copy()
                if not df_r.empty:
                    top = df_r.nsmallest(5, f'{m_rank}_num') if m_atuais[m_rank]['menor_melhor'] else df_r.nlargest(5, f'{m_rank}_num')
                    for i, row in enumerate(top.itertuples()):
                        color = cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, m_atuais)
                        st.markdown(f"""<div class='metric-box' style='padding:15px; margin-bottom:10px; border-left: 8px solid {color}; text-align: left;'>
                            <span style='font-weight:800;'>{i+1}º {getattr(row, col_op)}</span>
                            <span style='float:right; color:{color};'>{getattr(row, m_rank)}</span>
                        </div>""", unsafe_allow_html=True)

            with tabs[3]:
                m_s = st.selectbox("Análise Global:", list(m_atuais.keys()), key="s_box")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (df[f'{m_s}_num'].notna())].copy()
                if not df_s.empty:
                    conf = m_atuais[m_s]
                    df_s['Status'] = df_s[f'{m_s}_num'].apply(lambda x: 'Meta' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Abaixo')
                    fig = px.pie(df_s, names='Status', hole=0.6, color='Status', color_discrete_map={'Meta':'#4ade80','Abaixo':'#f87171'})
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white', height=350)
                    st.plotly_chart(fig, use_container_width=True)
