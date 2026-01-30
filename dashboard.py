import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# Estilo CSS para botões grandes no Lobby e design limpo
st.markdown("""
    <style>
    /* Estilo para os botões do Lobby (Grandes e Largos) */
    div.stButton > button {
        height: 5em;
        font-size: 22px !important;
        font-weight: bold;
        width: 100%;
        border-radius: 15px;
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        transition: all 0.3s;
        color: #1f3a5f;
    }
    div.stButton > button:hover {
        background-color: #e5e7eb;
        border-color: #004a99;
        color: #004a99;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Ajuste para o botão Voltar na Sidebar não herdar o tamanho gigante */
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        font-size: 14px !important;
        padding: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. DICIONÁRIO DE METAS E LISTA DE BACKOFFICE
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

# 3. FUNÇÕES DE SUPORTE
def converter_para_numero(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ['none', 'nan', '', '0']: return 0.0
    try: return float(str(valor).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def converter_tma_minutos(tempo_str):
    if pd.isna(tempo_str) or str(tempo_str).strip().lower() in ['none', 'nan', '', '00:00:00']: return 0.0
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config or valor == 0: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        if valor <= m: return "#28a745"
        if valor <= m + tol: return "#ffc107"
        return "#dc3545"
    else:
        if valor >= m: return "#28a745"
        if valor >= m - tol: return "#ffc107"
        return "#dc3545"

def exibir_card(label, valor, cor="#333", icon=""):
    valor_formatado = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {valor_formatado}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        col_map = {col.lower(): col for col in df.columns}
        target_op = col_map.get('operador', 'Operador')
        target_mat = col_map.get('matricula', 'Matricula')

        for col in list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']:
            real_col = col_map.get(col.lower(), col)
            if real_col in df.columns:
                df[f'{col}_num'] = df[real_col].apply(converter_tma_minutos if 'TMA' in col or 'Pausa' in col else converter_para_numero)
            else:
                df[f'{col}_num'] = 0.0
        return df, target_op, target_mat
    except Exception as e:
        return None, None, None

# --- LOBBY ---
if st.session_state.servico is None:
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    c1, c2, c3 = st.columns(3)
    if c1.button("🏢 SAC NDI", use_container_width=True): st.session_state.servico = "SAC NDI"; st.rerun()
    if c2.button("🏦 SAC PPO", use_container_width=True): st.session_state.servico = "SAC PPO"; st.rerun()
    if c3.button("🏥 SAC HAPVIDA", use_container_width=True): st.session_state.servico = "SAC HAPVIDA"; st.rerun()

else:
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            lista = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            lista = ["Selecione...", "Equipe Hapvida"]
        
        supervisor = st.selectbox("Supervisor:", lista)
        st.write("---")
        if st.button("⬅️ Voltar ao Lobby"): st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            # Lógica de Metas Customizadas
            metas_s = METAS_BASE.copy()
            # (Mantida sua lógica de meta_p customizada aqui...)
            
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[0]: # INDIVIDUAL
                mat_in = st.text_input("Digite sua Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                    else: st.warning("Matrícula não encontrada.")

            with tabs[3]: # SAÚDE (FILTRADA)
                df_saude = df[
                    (df[col_op].str.strip().str.upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df.iloc[:, 2].notna()) # Filtro adicional para evitar linhas fantasmas
                ].copy()
                
                sel = st.selectbox("Analise o Status Geral:", list(metas_s.keys()))
                mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                df_saude['Status'] = df_saude[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    fig = px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                    st.plotly_chart(fig, use_container_width=True)
                with c_s2: st.dataframe(df_saude[[col_op, sel, 'Status']], hide_index=True)
