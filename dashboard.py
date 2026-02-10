import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="NDI Intelligence", layout="wide", page_icon="📊")

# 2. ESTILO CSS REFORMULADO (FOCO EM LEITURA E PROPORÇÃO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* Fundo Global */
    .stApp { background-color: #FFFFFF; }

    /* TÍTULO DO HUB - CORRIGIDO PARA VISIBILIDADE */
    .hub-title {
        font-size: 52px;
        font-weight: 800;
        color: #0F172A !important; /* Azul quase preto para contraste total */
        text-align: center;
        margin-top: 60px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .hub-subtitle {
        font-size: 18px;
        color: #64748B;
        text-align: center;
        margin-bottom: 50px;
    }

    /* BOTÕES DO HUB (RETANGULARES E CLAROS) */
    div.stButton > button {
        background: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important;
        border-radius: 16px !important;
        height: 100px !important;
        width: 100% !important;
        color: #1E3A8A !important;
        font-size: 18px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    div.stButton > button:hover {
        border-color: #3B82F6 !important;
        transform: translateY(-3px);
        box-shadow: 0 10px 15px rgba(0,0,0,0.1);
    }

    /* BOTÃO VOLTAR (SIDEBAR) - TAMANHO REDUZIDO E COMPACTO */
    section[data-testid="stSidebar"] div.stButton > button {
        height: 45px !important;
        font-size: 14px !important;
        padding: 0px 15px !important;
        margin-top: 20px !important;
        border-radius: 10px !important;
        background: #F1F5F9 !important;
    }

    /* CARDS DE MÉTRICAS - LEITURA OTIMIZADA */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        margin-bottom: 15px;
    }
    .metric-label {
        color: #475569;
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .metric-value {
        font-size: 34px;
        font-weight: 800;
        color: #0F172A; /* Cor escura para leitura imediata */
    }

    /* SIDEBAR */
    [data-testid="stSidebar"] { background-color: #F8FAFC !important; border-right: 1px solid #E2E8F0; }
    
    /* ABAS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #F1F5F9;
        border-radius: 8px;
        padding: 8px 16px;
        color: #475569 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E3A8A !important;
        color: white !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. LÓGICA DE DADOS
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

def cor_kpi(val, met, metas):
    if val is None: return "#94A3B8"
    c = metas.get(met)
    if not c: return "#0F172A"
    m, tol, menor = c['valor'], c['margem'], c['menor_melhor']
    if menor:
        return "#16A34A" if val <= m else ("#D97706" if val <= m + tol else "#DC2626")
    return "#16A34A" if val >= m else ("#D97706" if val >= m - tol else "#DC2626")

@st.cache_data(ttl=60)
def load_data(sheet_name):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/gviz/tq?tqx=out:csv&sheet={sheet_name.replace(' ', '%20')}"
        df = pd.read_csv(url)
        # Limpeza e conversão (Lógica interna simplificada para o exemplo)
        for col in df.columns:
            if 'num' not in col:
                df[f'{col}_num'] = pd.to_numeric(df[col].astype(str).str.replace('%','').str.replace(',','.'), errors='coerce')
        return df
    except: return None

# --- ESTADO DA SESSÃO ---
if 'servico' not in st.session_state:
    st.session_state.servico = None

# --- HUB CENTRAL ---
if st.session_state.servico is None:
    st.markdown('<h1 class="hub-title">Portal de Performance NDI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="hub-subtitle">Selecione uma operação para monitorar os indicadores</p>', unsafe_allow_html=True)
    
    _, col1, col2, col3, _ = st.columns([0.1, 1, 1, 1, 0.1])
    with col1:
        if st.button("🏢\nSAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    with col2:
        if st.button("🏦\nSAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    with col3:
        if st.button("🏥\nSAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()

# --- ÁREA INTERNA ---
else:
    with st.sidebar:
        st.markdown(f"## 📍 {st.session_state.servico}")
        supervisor = st.selectbox("Selecione o Supervisor:", ["Equipe Ellen", "Equipe Alex", "Equipe Magno"]) # Exemplo
        
        # Botão Voltar Compacto
        if st.button("⬅️ Voltar ao Hub"):
            st.session_state.servico = None
            st.rerun()

    st.markdown(f"### Dashboard: {supervisor}")
    
    # Exemplo de Cards de Métrica com Leitura Clara
    c1, c2, c3 = st.columns(3)
    metrics = [("Aderência", "88%", 88, "Aderencia"), ("Silêncio", "12%", 12, "Silencio"), ("TMA", "06:40", 6.6, "TMA Voz")]
    
    for i, (label, display, val, key) in enumerate(metrics):
        cor = cor_kpi(val, key, METAS_BASE)
        with [c1, c2, c3][i]:
            st.markdown(f"""
                <div class="metric-card" style="border-top: 5px solid {cor}">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value" style="color: {cor}">{display}</div>
                </div>
            """, unsafe_allow_html=True)
