import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ENGENHARIA DE INTERFACE (CSS INJECTED)
# Aqui forçamos o dimensionamento horizontal/vertical e as animações solicitadas
st.markdown("""
    <style>
    /* Expande a área útil da página ao máximo */
    .block-container {
        max-width: 98% !important;
        padding-top: 1.5rem !important;
        padding-bottom: 0rem !important;
    }

    /* ESTILO DOS BOTÕES DO LOBBY (GIGANTES E LARGOS) */
    /* Seleciona botões dentro das colunas do corpo principal */
    div[data-testid="column"] div.stButton > button {
        width: 100% !important;
        height: 280px !important; /* Altura massiva para preenchimento vertical */
        font-size: 30px !important; /* Texto grande para impacto */
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        border-radius: 25px !important;
        background: linear-gradient(145deg, #f8f9fa, #ffffff) !important;
        border: 2px solid #dee2e6 !important;
        color: #1f3a5f !important;
        /* Animação fluida de 0.4s */
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        box-shadow: 8px 8px 15px rgba(0,0,0,0.05), -8px -8px 15px rgba(255,255,255,0.8) !important;
    }

    /* ANIMAÇÃO AO PASSAR O CURSOR (HOVER) */
    div[data-testid="column"] div.stButton > button:hover {
        transform: translateY(-15px) scale(1.02) !important; /* Sobe e cresce levemente */
        border-color: #004a99 !important;
        color: #004a99 !important;
        background-color: #ffffff !important;
        box-shadow: 0 25px 50px rgba(0,74,153,0.15) !important;
    }

    /* BOTÃO VOLTAR (SIDEBAR) - DISCRETO E MENOR */
    section[data-testid="stSidebar"] div.stButton > button {
        height: 45px !important;
        width: 150px !important; /* Largura fixa menor */
        font-size: 15px !important;
        font-weight: 500 !important;
        border-radius: 10px !important;
        background: #f1f3f5 !important;
        color: #495057 !important;
        border: 1px solid #ced4da !important;
        transform: none !important; /* Remove animação de subida aqui */
        box-shadow: none !important;
    }
    
    section[data-testid="stSidebar"] div.stButton > button:hover {
        background: #e9ecef !important;
        border-color: #adb5bd !important;
    }

    /* Ajuste de Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 30px; }
    .stTabs [data-baseweb="tab"] { font-size: 20px !important; font-weight: 600 !important; }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. REGRAS DE NEGÓCIO
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'ShortCall': {'valor': 5.0, 'margem': 2.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 5. FUNÇÕES DE TRATAMENTO DE DADOS (ANTI-ERRO)
def limpar_valor(valor, is_time=False):
    """Garante que 'None', '0' ou vazios sejam tratados como nulos reais."""
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    if s in ['none', '', 'nan', '0', '00:00:00', '0%', '0.0', '0,0']: return None
    
    if is_time and ':' in s:
        p = s.split(':')
        try:
            return int(p[0])*60 + int(p[1]) + (int(p[2])/60 if len(p)==3 else 0)
        except: return None
    
    try:
        # Remove caracteres não numéricos exceto separadores
        num = re.sub(r'[^\d,.-]', '', s).replace(',', '.')
        return float(num) if float(num) != 0 else None
    except: return None

@st.cache_data(ttl=60)
def carregar_dados_planilha(aba):
    try:
        sid = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Identificação dinâmica de colunas
        c_op = next((c for c in df.columns if 'operador' in c.lower()), df.columns[0])
        c_mat = next((c for c in df.columns if 'matricula' in c.lower()), df.columns[1])

        # Criação de colunas limpas para cálculos
        for metrica in list(METAS_BASE.keys()) + ['Pausa Total']:
            col_original = next((c for c in df.columns if metrica.lower() in c.lower()), None)
            if col_original:
                df[f'{metrica}_num'] = df[col_original].apply(lambda x: limpar_valor(x, 'TMA' in metrica or 'Pausa' in metrica))
            else:
                df[f'{metrica}_num'] = None
        return df, c_op, c_mat
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None, None, None

# --- FLUXO DE NAVEGAÇÃO ---

if st.session_state.servico is None:
    # LOBBY INICIAL
    st.markdown("<br><h1 style='text-align: center; color: #1f3a5f;'>🚀 PORTAL DE PERFORMANCE NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Grid de 3 colunas para botões ultra largos
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
        st.markdown(f"# 📍 {st.session_state.servico}")
        
        # Seleção de equipe baseada no serviço
        if st.session_state.servico == "SAC NDI":
            equipes = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            equipes = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            equipes = ["Selecione...", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Selecione o Supervisor:", equipes)
        st.write("---")
        if st.button("⬅️ VOLTAR"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_planilha(supervisor)
        
        if df is not None:
            # Ajuste de metas de pausa
            metas_atuais = METAS_BASE.copy()
            pausas_especificas = {"Carla": 17.27, "Ellen": 19.06, "Alex": 17.17, "Magno": 19.18}
            m_pausa = next((v for k, v in pausas_especificas.items() if k in supervisor), 21.75)
            metas_atuais['Pausa Total'] = {'valor': m_pausa, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 INDIVIDUAL", "🏆 RANKING EQUIPE", "📊 ANÁLISE DE SAÚDE"])

            with tabs[2]: # ABA SAÚDE - RESOLUÇÃO DO ERRO 'NONE'
                escolha = st.selectbox("Métrica para Análise:", list(metas_atuais.keys()))
                
                # FILTRO RIGOROSO: Remove 'Equipe', 'Backoffice' e qualquer valor que seja 'None' (Nulo)
                # Isso impede que pessoas como a 'Ludmila' (sem nota) entrem no gráfico.
                df_filtrado = df[
                    (df[col_op].str.strip().upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{escolha}_num'].notna()) 
                ].copy()

                if not df_filtrado.empty:
                    m_val = metas_atuais[escolha]['valor']
                    m_inv = metas_atuais[escolha]['menor_melhor']
                    
                    df_filtrado['Status'] = df_filtrado[f'{escolha}_num'].apply(
                        lambda x: 'Dentro da Meta' if (x <= m_val if m_inv else x >= m_val) else 'Fora da Meta'
                    )
                    
                    c_g1, c_g2 = st.columns([1, 1])
                    with c_g1:
                        fig = px.pie(df_filtrado, names='Status', hole=0.5, 
                                     color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    with c_g2:
                        st.dataframe(df_filtrado[[col_op, 'Status']], use_container_width=True, hide_index=True)
                else:
                    st.info("Não existem dados válidos para esta métrica nesta equipe.")
