import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="NDI Intelligence", layout="wide", page_icon="📊")

# 2. ESTILO CSS - WHITE MINIMALIST DESIGN
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap');

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Fundo Branco Sólido */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Cabeçalho com contraste em azul marinho */
    .hero-section {
        text-align: center;
        padding: 50px 0 30px 0;
    }
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        color: #1e3a8a; /* Azul Marinho */
        margin-bottom: 5px;
    }
    .hero-subtitle {
        color: #64748b;
        font-size: 18px;
    }

    /* --- BOTÕES DO HUB (HORIZONTAIS - WHITE GLASS) --- */
    div.stButton > button {
        background: rgba(248, 250, 252, 0.8) !important;
        border: 1px solid #e2e8f0 !important;
        backdrop-filter: blur(10px);
        border-radius: 16px !important;
        height: 90px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        color: #1e3a8a !important;
        font-size: 17px !important;
        font-weight: 700 !important;
        text-transform: uppercase;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }

    div.stButton > button:hover {
        background: #ffffff !important;
        transform: translateY(-4px) !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        color: #3b82f6 !important;
    }

    /* Dashboard Interno - Cards Claros */
    .metric-box {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 22px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-label { color: #64748b; font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 30px; font-weight: 800; margin-top: 5px; color: #1e293b; }

    /* Customização de Inputs e Sidebar para Fundo Branco */
    [data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #64748b !important;
    }
    
    /* Cor dos ícones e textos na sidebar */
    .css-17l695f { color: #1e3a8a; }
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
    if val is None: return "#94a3b8" # Cinza neutro
    c = metas.get(met)
    if not c: return "#1e293b"
    m, tol, menor = c['valor'], c['margem'], c['menor_melhor']
    if menor:
        return "#16a34a" if val <= m else ("#ca8a04" if val <= m + tol else "#dc2626")
    return "#16a34a" if val >= m else ("#ca8a04" if val >= m - tol else "#dc2626")

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
            <p class="hero-subtitle">Selecione o canal para análise de indicadores</p>
        </div>
    """, unsafe_allow_html=True)
    
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
        st.markdown(f"### 📍 {st.session_state.servico}")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        sup = st.selectbox("Supervisor:", lista)
        st.markdown("<br>"*5, unsafe_allow_html=True)
        if st.button("🏠 Voltar ao Hub"):
            st.session_state.servico = None; st.rerun()

    if sup != "Selecione...":
        df, col_op, col_mat = load_data(sup)
        if df is not None:
            m_atuais = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in sup or "Beatriz" in sup) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            m_atuais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["Individual", "Equipe", "Ranking", "Saúde"])

            with tabs[0]:
                mat = st.text_input("Matrícula:")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"#### Agente: {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        indicadores = [('Aderencia', '📈'), ('Silencio', '🔇'), ('Resolutividade', '✅'), ('Pausa Total', '⏱️'), ('TMA Voz', '📞'), ('Pesquisa', '⭐')]
                        for i, (m, icon) in enumerate(indicadores):
                            with [c1, c2, c3][i % 3]:
                                color = cor_kpi(r[f'{m}_num'], m, m_atuais)
                                st.markdown(f"""<div class='metric-box' style='border-top: 4px solid {color}'>
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
                            st.markdown(f"""<div class='metric-box' style='border-top: 4px solid {color}'>
                                <div class='metric-label'>{m} Equipe</div>
                                <div class='metric-value' style='color:{color}'>{eq[m]}</div>
                            </div><br>""", unsafe_allow_html=True)

            with tabs[2]:
                m_rank = st.selectbox("Ranking por:", list(m_atuais.keys()))
                df_r = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_rank}_num'].notna())].copy()
                if not df_r.empty:
                    top = df_r.nsmallest(5, f'{m_rank}_num') if m_atuais[m_rank]['menor_melhor'] else df_r.nlargest(5, f'{m_rank}_num')
                    for i, row in enumerate(top.itertuples()):
                        color = cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, m_atuais)
                        st.markdown(f"""<div class='metric-box' style='padding:15px; margin-bottom:10px; border-left: 8px solid {color}; text-align: left; background: white;'>
                            <span style='font-weight:700; color: #1e293b;'>{i+1}º {getattr(row, col_op)}</span>
                            <span style='float:right; color:{color}; font-weight:800;'>{getattr(row, m_rank)}</span>
                        </div>""", unsafe_allow_html=True)

            with tabs[3]:
                m_s = st.selectbox("Status Geral:", list(m_atuais.keys()), key="s_box")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (df[f'{m_s}_num'].notna())].copy()
                if not df_s.empty:
                    conf = m_atuais[m_s]
                    df_s['Status'] = df_s[f'{m_s}_num'].apply(lambda x: 'Meta' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora')
                    fig = px.pie(df_s, names='Status', hole=0.6, color='Status', color_discrete_map={'Meta':'#16a34a','Fora':'#dc2626'})
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#1e293b', height=350)
                    st.plotly_chart(fig, use_container_width=True)
