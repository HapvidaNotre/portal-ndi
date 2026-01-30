import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# Estilo CSS
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
    }
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        font-size: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. DICIONÁRIO DE METAS BASE
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
    if pd.isna(valor): return 0.0
    try:
        s_val = str(valor).replace('%', '').replace(',', '.').replace(' ', '').strip()
        return float(s_val) if s_val else 0.0
    except: return 0.0

def converter_tma_minutos(tempo_str):
    if pd.isna(tempo_str) or str(tempo_str).strip() == "0": return 0.0
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return float(str(tempo_str).replace(',', '.'))
    except: return 0.0

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if valor == 0: return "#333"
    if menor_melhor:
        return "#28a745" if valor <= m else ("#ffc107" if valor <= m + tol else "#dc3545")
    return "#28a745" if valor >= m else ("#ffc107" if valor >= m - tol else "#dc3545")

def exibir_card(label, valor, cor="#333", icon=""):
    v_fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {v_fmt}</h2>
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
        
        for metrica in list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']:
            real_col = col_map.get(metrica.lower())
            if real_col:
                df[f'{metrica}_num'] = df[real_col].apply(converter_tma_minutos if 'TMA' in metrica or 'Pausa' in metrica else converter_para_numero)
            else:
                df[f'{metrica}_num'] = 0.0
        return df, target_op, target_mat
    except: return None, None, None

# --- LOGICA DE NAVEGAÇÃO ---
if st.session_state.servico is None:
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🏢 SAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    if c2.button("🏦 SAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    if c3.button("🏥 SAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()
else:
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        supervisor = st.selectbox("Supervisor:", lista)
        if st.button("⬅️ Voltar"): st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            # --- AJUSTE DE METAS (ERIK E BEATRIZ) ---
            metas_s = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if st.session_state.servico == "SAC NDI" else 21.75)
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[1]: # ABA EQUIPE CORRIGIDA
                # Filtro robusto para achar a linha da equipe
                eq_row = df[df[col_op].astype(str).str.strip().str.upper() == 'EQUIPE']
                if not eq_row.empty:
                    e = eq_row.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    metrics_to_show = ['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Produtividade']
                    for i, m in enumerate(metrics_to_show):
                        with [c1, c2, c3][i % 3]:
                            val_label = e.get(next((c for c in df.columns if m.lower() in c.lower()), m), "0")
                            exibir_card(f"{m} (Equipe)", val_label, definir_cor_kpi(e[f'{m}_num'], m, metas_s))
                else:
                    st.error("ERRO: Linha 'EQUIPE' não encontrada na planilha. Verifique o nome na coluna Operador.")

            with tabs[0]: # INDIVIDUAL
                mat_in = st.text_input("Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1: 
                            exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                            exibir_card("Pesquisa", r.get('Pesquisa', 0), definir_cor_kpi(converter_para_numero(r.get('Pesquisa')), 'Pesquisa', metas_s), "⭐")
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                            exibir_card("Pausa Total", r.get('Pausa Total', '00:00'), definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', metas_s), "⏱️")
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                            exibir_card("Absenteísmo", r.get('Absenteismo', '0%'), definir_cor_kpi(r['Absenteismo_num'], 'Absenteismo', metas_s))

            with tabs[3]: # SAÚDE (GRÁFICO)
                # Remove equipe e backoffice para o gráfico não mentir
                df_clean = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE))].copy()
                sel = st.selectbox("Métrica para análise:", list(metas_s.keys()))
                mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                df_clean['Status'] = df_clean[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                st.plotly_chart(px.pie(df_clean, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}))
