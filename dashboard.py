import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="NDI Intelligence | Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# 2. ESTILO CSS - FOCO EM LEGIBILIDADE E DESIGN PREMIUM
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #1E3A8A;
        --secondary: #64748B;
        --background: #F8FAFC;
        --card-bg: #FFFFFF;
        --text-main: #0F172A;
    }

    /* Fundo da App */
    .stApp {
        background-color: var(--background);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* --- ESTILO DO HUB CENTRAL --- */
    .hub-container {
        padding: 60px 20px;
        text-align: center;
    }

    .main-title {
        font-size: 56px;
        font-weight: 800;
        color: var(--primary);
        letter-spacing: -2px;
        margin-bottom: 10px;
    }

    .main-subtitle {
        font-size: 20px;
        color: var(--secondary);
        margin-bottom: 50px;
        font-weight: 400;
    }

    /* Botões Horizontais do Hub */
    div.stButton > button {
        background-color: var(--card-bg) !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 24px !important;
        padding: 40px 20px !important;
        width: 100% !important;
        min-height: 160px !important;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1) !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }

    div.stButton > button p {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }

    div.stButton > button:hover {
        border-color: var(--primary) !important;
        transform: translateY(-8px) !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
        background-color: #F1F5F9 !important;
    }

    /* --- DASHBOARD INTERNO --- */
    /* Títulos de Seção */
    .section-header {
        color: var(--text-main);
        font-size: 28px;
        font-weight: 700;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid #E2E8F0;
    }

    /* Cards de Metricas */
    .kpi-card {
        background-color: var(--card-bg);
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }

    .kpi-label {
        color: var(--secondary);
        font-size: 14px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 15px;
    }

    .kpi-value {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #E2E8F0;
        border-radius: 12px;
        padding: 0 30px;
        font-weight: 600;
        color: var(--secondary);
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }

    /* Tabelas e Dataframes */
    .stDataFrame {
        border-radius: 15px;
        overflow: hidden;
        border: 1px solid #E2E8F0;
    }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE NEGÓCIO E METAS
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# Funções de Processamento
def tratar_num(v):
    if pd.isna(v) or str(v).strip() in ["", "None", "nan", "0", "00:00:00"]: return None
    try:
        if ':' in str(v):
            p = str(v).split(':')
            return int(p[0]) * 60 + int(p[1]) + (int(p[2])/60 if len(p)>2 else 0)
        return float(str(v).replace('%', '').replace(',', '.').strip())
    except: return None

def get_color(val, met, metas):
    if val is None: return "#94A3B8"
    c = metas.get(met)
    if not c: return "#0F172A"
    m, tol, menor = c['valor'], c['margem'], c['menor_melhor']
    if menor:
        return "#10B981" if val <= m else ("#F59E0B" if val <= m + tol else "#EF4444")
    return "#10B981" if val >= m else ("#F59E0B" if val >= m - tol else "#EF4444")

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{ID}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        cols = {c.lower(): c for c in df.columns}
        for m in list(METAS_BASE.keys()) + ['Pausa Total']:
            orig = cols.get('silencio (%)') if m == 'Silencio' else cols.get(m.lower())
            if not orig: orig = next((c for c in df.columns if m.lower() in c.lower()), None)
            if orig:
                df[f'{m}_num'] = df[orig].apply(tratar_num)
                df[m] = df[orig].astype(str).replace(['nan', 'None'], '---')
        return df, cols.get('operador', 'Operador'), cols.get('matricula', 'Matricula')
    except: return None, None, None

# --- NAVEGAÇÃO ---
if 'servico' not in st.session_state:
    st.session_state.servico = None

# --- TELA: HUB CENTRAL ---
if st.session_state.servico is None:
    st.markdown("""
        <div class="hub-container">
            <h1 class="main-title">NDI Intelligence</h1>
            <p class="main-subtitle">Selecione uma operação para iniciar o monitoramento</p>
        </div>
    """, unsafe_allow_html=True)

    _, c1, c2, c3, _ = st.columns([0.1, 1, 1, 1, 0.1])
    with c1:
        if st.button("🏢\n\nSAC NDI"):
            st.session_state.servico = "SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦\n\nSAC PPO"):
            st.session_state.servico = "SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥\n\nSAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"; st.rerun()

# --- TELA: DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"<h1 style='color:#1E3A8A; font-size: 24px;'>📍 {st.session_state.servico}</h1>", unsafe_allow_html=True)
        opcoes = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        supervisor = st.selectbox("Gestor Responsável:", opcoes)
        st.markdown("<br>"*5, unsafe_allow_html=True)
        if st.button("⬅️ Voltar ao Portal Principal"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            # Metas Dinâmicas
            m_atuais = METAS_BASE.copy()
            mp = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            m_atuais['Pausa Total'] = {'valor': mp, 'margem': 3.0, 'menor_melhor': True}

            tab1, tab2, tab3, tab4 = st.tabs(["👤 VISÃO INDIVIDUAL", "👥 PERFORMANCE TIME", "🏆 ELITE DO MÊS", "🩺 SAÚDE DA OPERAÇÃO"])

            with tab1:
                col_search1, col_search2 = st.columns([2, 1])
                with col_search1:
                    matricula = st.text_input("Busca rápida por Matrícula:", placeholder="Ex: 1210...")
                
                if matricula:
                    user_data = df[df[col_mat].astype(str).str.contains(matricula.strip())]
                    if not user_data.empty:
                        row = user_data.iloc[0]
                        st.markdown(f"<div class='section-header'>Resultados: {row[col_op]}</div>", unsafe_allow_html=True)
                        
                        c1, c2, c3 = st.columns(3)
                        indicadores = [
                            ('Aderencia', '📈 Aderência'), ('Silencio', '🔇 Silêncio'),
                            ('Resolutividade', '✅ Resolutividade'), ('Pausa Total', '⏱️ Pausa Total'),
                            ('TMA Voz', '📞 TMA Voz'), ('Pesquisa', '⭐ Pesquisa')
                        ]
                        
                        for i, (m, label) in enumerate(indicadores):
                            with [c1, c2, c3][i % 3]:
                                cor = get_color(row[f'{m}_num'], m, m_atuais)
                                st.markdown(f"""
                                    <div class='kpi-card' style='border-top: 6px solid {cor}'>
                                        <div class='kpi-label'>{label}</div>
                                        <div class='kpi-value' style='color:{cor}'>{row[m]}</div>
                                    </div><br>
                                """, unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Matrícula não encontrada nesta equipe.")

            with tab2:
                team_data = df[df[col_op].astype(str).str.upper() == 'EQUIPE']
                if not team_data.empty:
                    tr = team_data.iloc[0]
                    st.markdown("<div class='section-header'>Médias Consolidadas da Equipe</div>", unsafe_allow_html=True)
                    c1, c2, c3 = st.columns(3)
                    for i, m in enumerate(['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']):
                        with [c1, c2, c3][i % 3]:
                            cor = get_color(tr[f'{m}_num'], m, m_atuais)
                            st.markdown(f"""
                                <div class='kpi-card' style='border-top: 6px solid {cor}'>
                                    <div class='kpi-label'>{m}</div>
                                    <div class='kpi-value' style='color:{cor}'>{tr[m]}</div>
                                </div><br>
                            """, unsafe_allow_html=True)

            with tab3:
                m_rank = st.selectbox("Selecione a Métrica para o Ranking:", list(m_atuais.keys()))
                df_rank = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                             (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & 
                             (df[f'{m_rank}_num'].notna())].copy()
                
                if not df_rank.empty:
                    top = df_rank.nsmallest(5, f'{m_rank}_num') if m_atuais[m_rank]['menor_melhor'] else df_rank.nlargest(5, f'{m_rank}_num')
                    st.markdown(f"<div class='section-header'>Top 5 Performance: {m_rank}</div>", unsafe_allow_html=True)
                    for i, r in enumerate(top.itertuples()):
                        cor = get_color(getattr(r, f'{m_rank}_num'), m_rank, m_atuais)
                        st.markdown(f"""
                            <div class='kpi-card' style='text-align: left; padding: 15px 30px; margin-bottom: 10px; border-left: 10px solid {cor};'>
                                <span style='font-size: 20px; font-weight: 800; color: #1E293B;'>{i+1}º {getattr(r, col_op)}</span>
                                <span style='float: right; font-size: 24px; font-weight: 800; color: {cor};'>{getattr(r, m_rank)}</span>
                            </div>
                        """, unsafe_allow_html=True)

            with tab4:
                m_saude = st.selectbox("Métrica de Análise Crítica:", list(m_atuais.keys()), key="saude_box")
                df_saude = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (df[f'{m_saude}_num'].notna())].copy()
                
                if not df_saude.empty:
                    conf = m_atuais[m_saude]
                    def check(x): return 'Dentro da Meta' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta'
                    df_saude['Status'] = df_saude[f'{m_saude}_num'].apply(check)
                    
                    c_chart, c_table = st.columns([1, 1])
                    with c_chart:
                        fig = px.pie(df_saude, names='Status', hole=0.7, color='Status', 
                                    color_discrete_map={'Dentro da Meta':'#10B981','Fora da Meta':'#EF4444'})
                        fig.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with c_table:
                        st.markdown("<br><br>", unsafe_allow_html=True)
                        st.dataframe(df_saude[[col_op, m_saude, 'Status']], use_container_width=True, hide_index=True)
