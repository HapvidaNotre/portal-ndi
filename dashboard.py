import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ESTILO CSS (HUB MODERNO + CARDS)
st.markdown("""
    <style>
    /* Fundo da aplicação */
    .stApp {
        background-color: #f8f9fa;
    }

    /* Título do Hub */
    .main-title {
        text-align: center;
        color: #004a99;
        font-family: 'Segoe UI', sans-serif;
        margin-bottom: 40px;
    }

    /* Cards do Hub Inicial */
    div.stButton > button {
        border: none;
        border-radius: 20px;
        background: white;
        padding: 40px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s ease-in-out;
        height: 220px !important;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        color: #1f3a5f !important;
        font-size: 20px !important;
        font-weight: 600 !important;
    }

    div.stButton > button:hover {
        transform: translateY(-10px);
        box-shadow: 0 12px 25px rgba(0,74,153,0.15);
        border: 1px solid #004a99;
        color: #004a99 !important;
    }

    /* Ajuste para botões da Sidebar não ficarem gigantes */
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important;
        padding: 10px 15px;
        font-size: 14px !important;
        border-radius: 10px;
    }

    /* Estilo dos Cards de Métrica */
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        border-left: 8px solid;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 3. DICIONÁRIO DE METAS BASE
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'ShortCall': {'valor': 5.0, 'margem': 2.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 4. FUNÇÕES DE SUPORTE
def converter_para_numero(valor):
    if pd.isna(valor): return 0.0
    try:
        s_val = str(valor).replace('%', '').replace(',', '.').replace(' ', '').strip()
        return float(s_val) if s_val else 0.0
    except: return 0.0

def converter_tma_minutos(tempo_str):
    if pd.isna(tempo_str) or str(tempo_str).strip() in ["0", "00:00:00", ""]: return 0.0
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return float(str(tempo_str).replace(',', '.'))
    except: return 0.0

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config or valor == 0: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        return "#28a745" if valor <= m else ("#ffc107" if valor <= m + tol else "#dc3545")
    return "#28a745" if valor >= m else ("#ffc107" if valor >= m - tol else "#dc3545")

def exibir_card(label, valor, cor="#333", icon=""):
    v_fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {cor};">
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
        
        # Processamento das métricas incluindo Silêncio
        metricas_list = list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']
        for m in metricas_list:
            # Busca flexível para Silencio ou Silencio (%)
            real_col = col_map.get(m.lower()) if m != 'Silencio' else (col_map.get('silencio (%)') or col_map.get('silencio'))
            if real_col:
                df[f'{m}_num'] = df[real_col].apply(converter_tma_minutos if 'TMA' in m or 'Pausa' in m else converter_para_numero)
            else:
                df[f'{m}_num'] = 0.0
        return df, target_op, target_mat
    except: return None, None, None

# --- LÓGICA DO HUB INICIAL ---
if st.session_state.servico is None:
    st.markdown("<br><div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p style='color: #666;'>Gestão de Indicadores em Tempo Real</p></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢\n\nSAC NDI", use_container_width=True):
            st.session_state.servico = "SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦\n\nSAC PPO", use_container_width=True):
            st.session_state.servico = "SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥\n\nSAC HAPVIDA", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"; st.rerun()
    
    st.markdown("<br><br><p style='text-align: center; color: #aaa; font-size: 12px;'>NDI Operações © 2026</p>", unsafe_allow_html=True)

# --- LÓGICA DAS OPERAÇÕES ---
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
        if st.button("⬅️ Voltar ao Hub"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            # --- AJUSTE DE METAS (ERIK E BEATRIZ) ---
            metas_s = METAS_BASE.copy()
            if "Erik" in supervisor or "Beatriz" in supervisor:
                meta_p = 21.75
            elif st.session_state.servico == "SAC NDI":
                meta_p = 16.60
            else:
                meta_p = 21.75
            
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[1]: # 👥 EQUIPE
                eq_row = df[df[col_op].astype(str).str.strip().str.upper() == 'EQUIPE']
                if not eq_row.empty:
                    e = eq_row.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    # Exibição incluindo Silêncio e Pausa Total
                    m_list = ['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']
                    for i, m in enumerate(m_list):
                        with [c1, c2, c3][i % 3]:
                            # Tenta pegar o valor original da planilha para o label
                            label_val = e.get(m, e.get('Silencio (%)', '0'))
                            exibir_card(f"{m} (Equipe)", label_val, definir_cor_kpi(e[f'{m}_num'], m, metas_s))

            with tabs[0]: # 👤 INDIVIDUAL
                mat_in = st.text_input("Sua Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                            exibir_card("Silêncio", r.get('Silencio (%)', '0%'), definir_cor_kpi(r['Silencio_num'], 'Silencio', metas_s), "🔇")
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                            exibir_card("Pausa Total", r.get('Pausa Total', '00:00'), definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', metas_s), "⏱️")
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                            exibir_card("Pesquisa", r.get('Pesquisa', 0), definir_cor_kpi(converter_para_numero(r.get('Pesquisa')), 'Pesquisa', metas_s), "⭐")

            with tabs[3]: # 📊 SAÚDE
                df_saude = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE))].copy()
                sel = st.selectbox("Selecione a Métrica:", list(metas_s.keys()))
                mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                df_saude['Status'] = df_saude[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                st.plotly_chart(px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}))
