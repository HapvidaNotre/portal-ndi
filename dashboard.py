import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="NDI Intelligence", layout="wide", page_icon="📊")

# 2. ESTILO CSS - REVOLUÇÃO ESTÉTICA (GLASSMORPHISM 2.0)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    .stApp {
        background: radial-gradient(circle at 20% 20%, #1a2a6c 0%, #b21f1f 50%, #fdbb2d 100%);
        background-attachment: fixed;
    }

    /* Título Futurista */
    .hero-section {
        text-align: center;
        padding: 80px 0 50px 0;
    }
    .hero-title {
        font-size: 72px;
        font-weight: 800;
        color: white;
        letter-spacing: -3px;
        margin-bottom: 0;
        text-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .hero-subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 22px;
        font-weight: 300;
    }

    /* Cartões do Hub (O Novo Hub) */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        backdrop-filter: blur(25px) !important;
        -webkit-backdrop-filter: blur(25px) !important;
        border-radius: 40px !important;
        height: 320px !important;
        width: 100% !important;
        transition: all 0.6s cubic-bezier(0.23, 1, 0.32, 1) !important;
        color: white !important;
        font-size: 26px !important;
        font-weight: 600 !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2) !important;
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.2) !important;
        transform: scale(1.05) translateY(-15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        box-shadow: 0 40px 80px rgba(0,0,0,0.4) !important;
    }

    /* Sidebar Estilizada */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.4) !important;
        backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255,255,255,0.1);
    }

    /* Cards de Métricas (Dashboard Interno) */
    .metric-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 30px;
        padding: 30px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-label { color: rgba(255,255,255,0.6); font-size: 14px; text-transform: uppercase; letter-spacing: 2px; }
    .metric-value { color: white; font-size: 38px; font-weight: 800; margin: 10px 0; }

    /* Ajuste de abas */
    .stTabs [data-baseweb="tab-list"] { background: transparent; }
    .stTabs [data-baseweb="tab"] { 
        color: white; 
        background: rgba(255,255,255,0.05); 
        border-radius: 20px; 
        margin-right: 10px;
        padding: 10px 30px;
    }
    </style>
""", unsafe_allow_html=True)

# Lógica de Sessão
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 3. DICIONÁRIO DE METAS E PROCESSAMENTO (MANTIDOS E ROBUSTOS)
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# Funções auxiliares (Limpeza e Conversão)
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
    if val is None: return "rgba(255,255,255,0.2)"
    c = metas.get(met)
    if not c: return "white"
    m, tol, menor = c['valor'], c['margem'], c['menor_melhor']
    if menor:
        return "#00ff88" if val <= m else ("#ffcc00" if val <= m + tol else "#ff3333")
    return "#00ff88" if val >= m else ("#ffcc00" if val >= m - tol else "#ff3333")

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

# --- HUB INICIAL (REINVENTADO) ---
if st.session_state.servico is None:
    st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">NDI Intelligence</h1>
            <p class="hero-subtitle">Analytics e Performance Estratégica</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("🏛️\n\nSAC NDI"):
            st.session_state.servico = "SAC NDI"; st.rerun()
    with col_b:
        if st.button("🏦\n\nSAC PPO"):
            st.session_state.servico = "SAC PPO"; st.rerun()
    with col_c:
        if st.button("🏥\n\nSAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"; st.rerun()

else:
    # --- DASHBOARD INTERNO ---
    with st.sidebar:
        st.markdown(f"<h1 style='color:white; font-size: 28px;'>{st.session_state.servico}</h1>", unsafe_allow_html=True)
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        sup = st.selectbox("Gestão:", lista)
        st.markdown("<br>"*10, unsafe_allow_html=True)
        if st.button("🏠 Retornar"):
            st.session_state.servico = None; st.rerun()

    if sup != "Selecione...":
        df, col_op, col_mat = load_data(sup)
        if df is not None:
            m_atuais = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in sup or "Beatriz" in sup) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            m_atuais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            t = st.tabs(["👤 AGENTE", "👥 TIME", "🏆 ELITE", "🩺 STATUS"])

            with t[0]: # INDIVIDUAL
                mat = st.text_input("Identificação (Matrícula):")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"<h2 style='color:white;'>Dashboard: {r[col_op]}</h2>", unsafe_allow_html=True)
                        c1, c2, c3 = st.columns(3)
                        metrics = [('Aderencia', ''), ('Silencio', '🔇'), ('Resolutividade', ''), ('Pausa Total', '⏱️'), ('TMA Voz', '📞'), ('Pesquisa', '⭐')]
                        for i, (m, icon) in enumerate(metrics):
                            with [c1, c2, c3][i % 3]:
                                color = cor_kpi(r[f'{m}_num'], m, m_atuais)
                                st.markdown(f"""<div class='metric-box' style='border-bottom: 5px solid {color}'>
                                    <div class='metric-label'>{m}</div>
                                    <div class='metric-value' style='color:{color}'>{icon} {r[m]}</div>
                                </div><br>""", unsafe_allow_html=True)

            with t[1]: # TIME
                eq = df[df[col_op].astype(str).str.upper() == 'EQUIPE']
                if not eq.empty:
                    eq = eq.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    for i, m in enumerate(['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']):
                        with [c1, c2, c3][i % 3]:
                            color = cor_kpi(eq[f'{m}_num'], m, m_atuais)
                            st.markdown(f"""<div class='metric-box' style='border-bottom: 5px solid {color}'>
                                <div class='metric-label'>{m} Equipe</div>
                                <div class='metric-value' style='color:{color}'>{eq[m]}</div>
                            </div><br>""", unsafe_allow_html=True)

            with t[2]: # RANKING
                m_rank = st.selectbox("Critério de Elite:", list(m_atuais.keys()))
                df_r = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_rank}_num'].notna())].copy()
                if not df_r.empty:
                    top = df_r.nsmallest(5, f'{m_rank}_num') if m_atuais[m_rank]['menor_melhor'] else df_r.nlargest(5, f'{m_rank}_num')
                    for i, row in enumerate(top.itertuples()):
                        color = cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, m_atuais)
                        st.markdown(f"""<div class='metric-box' style='padding:15px; margin-bottom:10px; border-left: 10px solid {color}'>
                            <div style='display:flex; justify-content:space-between; align-items:center;'>
                                <span style='color:white; font-weight:800;'>{i+1}º {getattr(row, col_op)}</span>
                                <span style='color:{color}; font-size:20px;'>{getattr(row, m_rank)}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

            with t[3]: # SAÚDE
                m_s = st.selectbox("Diagnóstico Global:", list(m_atuais.keys()), key="s_box")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (df[f'{m_s}_num'].notna())].copy()
                if not df_s.empty:
                    conf = m_atuais[m_s]
                    df_s['Status'] = df_s[f'{m_s}_num'].apply(lambda x: 'Meta Atingida' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Abaixo da Meta')
                    fig = px.pie(df_s, names='Status', hole=0.7, color='Status', color_discrete_map={'Meta Atingida':'#00ff88','Abaixo da Meta':'#ff3333'})
                    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white', showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df_s[[col_op, m_s, 'Status']], hide_index=True, use_container_width=True)
