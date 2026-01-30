import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CSS "DO ZERO" - REESTRUTURAÇÃO VISUAL TOTAL
st.markdown("""
    <style>
    /* 1. EXPANSÃO DA TELA: Removemos o espaço branco inútil nas laterais e topo */
    .block-container {
        max-width: 100% !important;
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* 2. BOTÕES GIGANTES (LOBBY) - Alvo específico: Botões dentro das colunas principais */
    div[data-testid="column"] button {
        background-color: white !important;
        
        /* DIMENSÕES - AQUI ESTÁ O SEGREDO DO TAMANHO */
        height: 350px !important;  /* Altura de um painel */
        width: 100% !important;    /* Largura total da coluna */
        
        /* TIPOGRAFIA */
        font-size: 40px !important;
        font-weight: 900 !important;
        text-transform: uppercase;
        color: #1f3a5f !important;
        
        /* BORDA E ACABAMENTO */
        border: 2px solid #e6e6e6 !important;
        border-radius: 25px !important;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05) !important;
        
        /* FLEXBOX PARA CENTRALIZAR O TEXTO E ÍCONE */
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        transition: transform 0.3s ease, box-shadow 0.3s ease !important;
    }

    /* 3. EFEITO AO PASSAR O MOUSE (HOVER) */
    div[data-testid="column"] button:hover {
        transform: scale(1.02) !important; /* Cresce levemente */
        border-color: #004a99 !important;
        color: #004a99 !important;
        background-color: #f8faff !important;
        box-shadow: 0 20px 40px rgba(0, 74, 153, 0.15) !important;
        z-index: 99 !important;
    }

    /* 4. BOTÃO VOLTAR (SIDEBAR) - RESETA O ESTILO PARA NÃO FICAR GIGANTE */
    section[data-testid="stSidebar"] button {
        height: 50px !important;
        width: 100% !important;
        font-size: 16px !important;
        font-weight: normal !important;
        background-color: #e9ecef !important;
        border: 1px solid #ced4da !important;
        box-shadow: none !important;
        margin-top: 20px !important;
        border-radius: 8px !important;
        display: block !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #dee2e6 !important;
        transform: none !important;
    }

    /* AJUSTES FINAIS DE FONTE NAS TABELAS E ABAS */
    .stTabs [data-baseweb="tab"] { font-size: 20px !important; }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. TRATAMENTO DE DADOS (IMPEDE ERRO LUDMILLA/NONE)
def limpar_dados(valor, is_time=False):
    """
    Remove estritamente qualquer valor que não seja um número válido.
    Converte 'None', 'nan', '0', '' para None do Python.
    """
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    
    # Lista de exclusão
    if s in ['none', '', 'nan', 'null', '#n/a', '-', '0', '0.0', '0%', '0,0']:
        return None

    if is_time and ':' in s:
        try:
            p = s.split(':')
            return int(p[0])*60 + int(p[1]) + (float(p[2])/60 if len(p)==3 else 0)
        except: return None
    
    try:
        num = re.sub(r'[^\d,.-]', '', s).replace(',', '.')
        val = float(num)
        return val if val != 0 else None
    except: return None

# Regras de Metas
METAS = {
    'Aderencia': {'v': 85.0, 'tol': 5.0, 'inv': False},
    'TMA Voz': {'v': 8.0, 'tol': 1.0, 'inv': True},
    'Resolutividade': {'v': 75.0, 'tol': 5.0, 'inv': False},
    'Pesquisa': {'v': 4.5, 'tol': 0.5, 'inv': False}
}
BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

@st.cache_data(ttl=60)
def carregar(aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        c_op = next(c for c in df.columns if 'operador' in c.lower())
        c_mat = next(c for c in df.columns if 'matricula' in c.lower())
        
        for k in METAS.keys():
            orig = next((c for c in df.columns if k.lower() in c.lower()), None)
            if orig: df[f'{k}_num'] = df[orig].apply(lambda x: limpar_dados(x, 'TMA' in k))
            else: df[f'{k}_num'] = None
        return df, c_op, c_mat
    except: return None, None, None

def get_cor(val, meta):
    if val is None: return "#6c757d"
    v, t, inv = meta['v'], meta['tol'], meta['inv']
    if inv: return "#28a745" if val<=v else ("#ffc107" if val<=v+t else "#dc3545")
    return "#28a745" if val>=v else ("#ffc107" if val>=v-t else "#dc3545")

def card(lbl, val, cor, icon=""):
    fmt = f"{val:.2f}" if isinstance(val, (float, int)) else "N/A"
    st.markdown(f"""
    <div style="background:white;padding:20px;border-radius:15px;border-left:10px solid {cor};box-shadow:0 5px 15px rgba(0,0,0,0.08);margin-bottom:15px">
        <div style="font-size:12px;color:#888;font-weight:bold;text-transform:uppercase">{lbl}</div>
        <div style="font-size:26px;color:{cor};font-weight:bold">{icon} {fmt}</div>
    </div>""", unsafe_allow_html=True)

# --- FLUXO PRINCIPAL ---

if st.session_state.servico is None:
    # LOBBY - BOTÕES GIGANTES
    st.markdown("<br><h1 style='text-align:center;color:#0f2c4c;font-size:42px'>PORTAL DE PERFORMANCE</h1><br>", unsafe_allow_html=True)
    
    # Grid com gap (espaço) generoso entre os botões
    c1, c2, c3 = st.columns(3, gap="large")
    
    # O texto dentro do botão inclui quebras de linha (\n) e emoji grande para compor o visual
    with c1:
        if st.button("🏢\n\nSAC NDI"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with c2:
        if st.button("🏦\n\nSAC PPO"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with c3:
        if st.button("🏥\n\nSAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    # ÁREA INTERNA
    with st.sidebar:
        st.header(f"📍 {st.session_state.servico}")
        opcoes = ["Selecione..."] + (["Equipe Erik", "Equipe Davi", "Equipe Elaine"] if "NDI" in st.session_state.servico else ["Equipe Ellen", "Equipe Carla"])
        sup = st.selectbox("Supervisor:", opcoes)
        st.write("")
        if st.button("⬅️ Voltar ao Lobby"): # Este botão será pequeno devido ao CSS específico
            st.session_state.servico = None
            st.rerun()

    if sup != "Selecione...":
        df, col_op, col_mat = carregar(sup)
        if df is not None:
            t1, t2, t3 = st.tabs(["👤 INDIVIDUAL", "🏆 RANKING", "📊 SAÚDE"])
            
            with t3: # ABA SAÚDE - CORRIGIDA
                metrica = st.selectbox("Indicador:", list(METAS.keys()))
                # FILTRO DE SEGURANÇA: Remove quem não tem nota (Ludmilla)
                df_s = df[
                    (df[f'{metrica}_num'].notna()) & 
                    (~df[col_mat].astype(str).str.contains('|'.join(BACKOFFICE))) &
                    (df[col_op].str.upper() != 'EQUIPE')
                ].copy()
                
                if not df_s.empty:
                    m = METAS[metrica]
                    df_s['Status'] = df_s[f'{metrica}_num'].apply(lambda x: 'Meta Batida' if (x<=m['v'] if m['inv'] else x>=m['v']) else 'Fora da Meta')
                    
                    c_g, c_t = st.columns([1, 1])
                    with c_g: 
                        st.plotly_chart(px.pie(df_s, names='Status', hole=0.6, color='Status', color_discrete_map={'Meta Batida':'#28a745','Fora da Meta':'#dc3545'}), use_container_width=True)
                    with c_t: 
                        st.dataframe(df_s[[col_op, f'{metrica}_num', 'Status']], use_container_width=True, hide_index=True)
                else:
                    st.warning("Sem dados válidos para exibir.")
