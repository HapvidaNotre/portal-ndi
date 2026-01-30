import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ESTILO CSS (O PAINEL QUE FICOU PERFEITO)
st.markdown("""
    <style>
    /* Estilo para os botões do Lobby (Grandes e Largos) */
    div.stButton > button {
        height: 5.5em; /* Altura generosa */
        font-size: 22px !important;
        font-weight: bold;
        width: 100%;
        border-radius: 15px;
        background-color: #ffffff;
        border: 2px solid #d1d5db;
        transition: all 0.3s;
        color: #004a99;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    div.stButton > button:hover {
        background-color: #f8fafc;
        border-color: #004a99;
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
    }

    /* Ajuste para o botão 'Voltar' na Sidebar (Não deve ser gigante) */
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        font-size: 14px !important;
        padding: 10px !important;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. METAS E CONFIGURAÇÕES
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 5. FUNÇÕES DE LIMPEZA (CORREÇÃO PARA 'NONE' E VALORES VAZIOS)
def limpar_valor(valor, is_time=False):
    """Transforma 'None', vazios e sujeira em nulo real ou número."""
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    
    # Se for texto de erro ou nulo na planilha, retorna None
    if s in ['none', '', 'nan', 'null', '0', '0%', '00:00:00']:
        return None

    if is_time and ':' in s:
        try:
            p = s.split(':')
            if len(p) == 3: return int(p[0]) * 60 + int(p[1]) + int(p[2]) / 60
            if len(p) == 2: return int(p[0]) + int(p[1]) / 60
        except: return None
    
    try:
        limpo = re.sub(r'[^\d,.-]', '', s).replace(',', '.')
        val = float(limpo)
        return val if val != 0 else None
    except: return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        sheet_id = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        c_op = next(c for c in df.columns if 'operador' in c.lower())
        c_mat = next(c for c in df.columns if 'matricula' in c.lower())

        for m in METAS_BASE.keys():
            col_origem = next((c for c in df.columns if m.lower() in c.lower()), None)
            if col_origem:
                df[f'{m}_num'] = df[col_origem].apply(lambda x: limpar_valor(x, 'TMA' in m))
            else:
                df[f'{m}_num'] = None
        return df, c_op, c_mat
    except: return None, None, None

# --- LOBBY (O PAINEL PERFEITO) ---
if st.session_state.servico is None:
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3 = st.columns(3)
    # O segredo do tamanho está aqui: st.button + use_container_width=True
    if c1.button("🏢 SAC NDI", use_container_width=True): 
        st.session_state.servico = "SAC NDI"; st.rerun()
    if c2.button("🏦 SAC PPO", use_container_width=True): 
        st.session_state.servico = "SAC PPO"; st.rerun()
    if c3.button("🏥 SAC HAPVIDA", use_container_width=True): 
        st.session_state.servico = "SAC HAPVIDA"; st.rerun()

else:
    # --- DASHBOARD INTERNO ---
    with st.sidebar:
        st.header(f"📍 {st.session_state.servico}")
        if "NDI" in st.session_state.servico:
            lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif "PPO" in st.session_state.servico:
            lista = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            lista = ["Selecione...", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Supervisor:", lista)
        if st.button("⬅️ Voltar ao Lobby"): 
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        
        if df is not None:
            t_ind, t_sau = st.tabs(["👤 Individual", "📊 Saúde da Equipe"])

            with t_sau:
                sel_m = st.selectbox("Escolha o Indicador:", list(METAS_BASE.keys()))
                
                # --- FILTRO ANTIBUG (CASO LUDMILA) ---
                # Remove quem é 'EQUIPE', quem é 'BACKOFFICE' e quem está com valor NULO/NONE
                df_saude = df[
                    (df[f'{sel_m}_num'].notna()) & 
                    (df[col_op].str.upper() != 'EQUIPE') &
                    (~df[col_mat].astype(str).str.contains('|'.join(MATRICULAS_BACKOFFICE)))
                ].copy()

                if not df_saude.empty:
                    meta = METAS_BASE[sel_m]['valor']
                    inv = METAS_BASE[sel_m]['menor_melhor']
                    
                    df_saude['Status'] = df_saude[f'{sel_m}_num'].apply(
                        lambda x: 'Dentro da Meta' if (x <= meta if inv else x >= meta) else 'Fora da Meta'
                    )
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        fig = px.pie(df_saude, names='Status', hole=0.5, 
                                     color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.dataframe(df_saude[[col_op, 'Status']], use_container_width=True, hide_index=True)
                else:
                    st.warning("Não há dados válidos para gerar o gráfico deste indicador.")
