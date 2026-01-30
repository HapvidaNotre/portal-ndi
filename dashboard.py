import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. TOOLKIT DE CSS (O PAINEL PERFEITO)
st.markdown("""
    <style>
    /* Expansão de tela para preenchimento total */
    .block-container {
        padding-top: 1.5rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* ESTILO DOS BOTÕES DO LOBBY (GIGANTES E LARGOS) */
    /* Este alvo garante que apenas os botões da tela principal sejam afetados */
    div[data-testid="stAppViewContainer"] div[data-testid="column"] button {
        width: 100% !important;
        height: 180px !important; /* Altura ideal para painel retangular */
        font-size: 26px !important;
        font-weight: 800 !important;
        border-radius: 15px !important;
        background-color: #ffffff !important;
        border: 2px solid #e9ecef !important;
        color: #1f3a5f !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
    }

    /* Efeito de hover nos botões do Lobby */
    div[data-testid="stAppViewContainer"] div[data-testid="column"] button:hover {
        transform: translateY(-8px) !important;
        border-color: #004a99 !important;
        color: #004a99 !important;
        box-shadow: 0 12px 24px rgba(0,74,153,0.15) !important;
        background-color: #f8faff !important;
    }

    /* BOTÃO VOLTAR (SIDEBAR) - DISCRETO E PEQUENO */
    section[data-testid="stSidebar"] button {
        height: 45px !important;
        width: 100% !important;
        font-size: 15px !important;
        font-weight: normal !important;
        border-radius: 8px !important;
        background-color: #f1f3f5 !important;
        color: #495057 !important;
        border: 1px solid #dee2e6 !important;
        box-shadow: none !important;
        transform: none !important;
        margin-top: 20px !important;
    }

    section[data-testid="stSidebar"] button:hover {
        background-color: #e9ecef !important;
        border-color: #adb5bd !important;
    }

    /* Títulos e Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 25px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. REGRAS DE NEGÓCIO
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 5. FUNÇÕES DE TRATAMENTO (CORREÇÃO DE NONE/LUDMILLA)
def tratar_valor(valor, is_time=False):
    """Converte strings sujas, 'None' e vazios em nulo real ou float."""
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    if s in ['none', '', 'nan', '0', '00:00:00', '0%', '0.0']: return None
    
    if is_time and ':' in s:
        try:
            partes = s.split(':')
            if len(partes) == 3: return int(partes[0])*60 + int(partes[1]) + int(partes[2])/60
            if len(partes) == 2: return int(partes[0]) + int(partes[1])/60
        except: return None
    
    try:
        limpo = re.sub(r'[^\d,.-]', '', s).replace(',', '.')
        return float(limpo) if float(limpo) != 0 else None
    except: return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        sid = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        c_op = next(c for c in df.columns if 'operador' in c.lower())
        c_mat = next(c for c in df.columns if 'matricula' in c.lower())
        
        for m in METAS_BASE.keys():
            col_orig = next((c for c in df.columns if m.lower() in c.lower()), None)
            df[f'{m}_clean'] = df[col_orig].apply(lambda x: tratar_valor(x, 'TMA' in m)) if col_orig else None
        return df, c_op, c_mat
    except: return None, None, None

# --- FLUXO DE NAVEGAÇÃO ---

if st.session_state.servico is None:
    # TELA DE LOBBY (PAINEL DE BOTÕES LARGOS)
    st.markdown("<br><h1 style='text-align: center; color: #1f3a5f;'>PORTAL DE PERFORMANCE NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Grid de 3 colunas para garantir que os botões se estiquem horizontalmente
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢 SAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦 SAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥 SAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()

else:
    # DASHBOARD INTERNO
    with st.sidebar:
        st.markdown(f"## 📍 {st.session_state.servico}")
        if "NDI" in st.session_state.servico:
            sups = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif "PPO" in st.session_state.servico:
            sups = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            sups = ["Selecione...", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Supervisor:", sups)
        if st.button("⬅️ VOLTAR AO LOBBY"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, c_op, c_mat = carregar_dados(supervisor)
        if df is not None:
            tab1, tab2 = st.tabs(["👤 INDIVIDUAL", "📊 SAÚDE DA EQUIPE"])
            
            with tab2:
                metrica = st.selectbox("Selecione o Indicador:", list(METAS_BASE.keys()))
                
                # FILTRO CRÍTICO: Remove 'Equipe', 'Backoffice' e qualquer valor Nulo/None (Ludmilla)
                df_filtrado = df[
                    (df[f'{metrica}_clean'].notna()) & 
                    (df[c_op].str.upper() != 'EQUIPE') &
                    (~df[c_mat].astype(str).str.contains('|'.join(MATRICULAS_BACKOFFICE)))
                ].copy()
                
                if not df_filtrado.empty:
                    m_val = METAS_BASE[metrica]['valor']
                    m_inv = METAS_BASE[metrica]['menor_melhor']
                    df_filtrado['Status'] = df_filtrado[f'{metrica}_clean'].apply(
                        lambda x: 'Dentro da Meta' if (x <= m_val if m_inv else x >= m_val) else 'Fora da Meta'
                    )
                    
                    c_g1, c_g2 = st.columns([1, 1])
                    with c_g1:
                        fig = px.pie(df_filtrado, names='Status', hole=0.5, color='Status', 
                                     color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    with c_g2:
                        st.dataframe(df_filtrado[[c_op, 'Status']], use_container_width=True, hide_index=True)
