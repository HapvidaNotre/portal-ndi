import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# Estilo CSS (O seu favorito)
st.markdown("""
    <style>
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
    }
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        font-size: 14px !important;
        padding: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. CONFIGURAÇÕES DE METAS
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
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
        p = str(tempo_str).split(':')
        return int(p[0])*60 + int(p[1]) + (int(p[2])/60 if len(p)==3 else 0)
    except: return 0.0

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config or valor == 0: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        return "#28a745" if valor <= m else ("#ffc107" if valor <= m + tol else "#dc3545")
    return "#28a745" if valor >= m else ("#ffc107" if valor >= m - tol else "#dc3545")

def exibir_card(label, valor, cor="#333", icon=""):
    val_fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {val_fmt}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        c_op = next(c for c in df.columns if 'operador' in c.lower())
        c_mat = next(c for c in df.columns if 'matricula' in c.lower())
        for m in METAS_BASE.keys():
            col_orig = next((c for c in df.columns if m.lower() in c.lower()), None)
            df[f'{m}_num'] = df[col_orig].apply(converter_tma_minutos if 'TMA' in m else converter_para_numero) if col_orig else 0.0
        return df, c_op, c_mat
    except: return None, None, None

# --- NAVEGAÇÃO ---
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
        sups = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if "NDI" in st.session_state.servico else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        supervisor = st.selectbox("Supervisor:", sups)
        if st.button("⬅️ Voltar ao Lobby"): st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            # TABELA EQUIPE (A QUE ESTAVA FALTANDO)
            with tabs[1]:
                st.subheader(f"Resumo Consolidado: {supervisor}")
                # Busca a linha onde o nome do operador contém "EQUIPE"
                linha_equipe = df[df[col_op].str.strip().str.upper() == 'EQUIPE']
                
                if not linha_equipe.empty:
                    eq = linha_equipe.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    metrics_list = list(METAS_BASE.keys())
                    for i, m in enumerate(metrics_list):
                        with [c1, c2, c3][i % 3]:
                            # Pega o valor textual original da planilha para exibir (ex: 88%)
                            val_texto = eq.get(next(c for c in df.columns if m.lower() in c.lower()), "0")
                            exibir_card(f"{m} (Média)", val_texto, definir_cor_kpi(eq[f'{m}_num'], m, METAS_BASE))
                else:
                    st.warning("Linha 'EQUIPE' não encontrada nesta planilha.")

            with tabs[0]: # INDIVIDUAL
                mat_in = st.text_input("Digite sua Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1: exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', METAS_BASE))
                        with c2: exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', METAS_BASE))
                        with c3: exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', METAS_BASE), "⏱️")
                    else: st.warning("Matrícula não encontrada.")

            with tabs[3]: # SAÚDE
                df_saude = df[(df[col_op].str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE))].copy()
                sel = st.selectbox("Analise o Status Geral:", list(METAS_BASE.keys()))
                mv, inv = METAS_BASE[sel]['valor'], METAS_BASE[sel]['menor_melhor']
                df_saude['Status'] = df_saude[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                c_s1, c_s2 = st.columns(2)
                with c_s1: st.plotly_chart(px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}), use_container_width=True)
                with c_s2: st.dataframe(df_saude[[col_op, sel, 'Status']], hide_index=True)
