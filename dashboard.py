import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ESTILO CSS - DESIGN PREMIUM (MODERN HUB)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    .stApp {
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
        font-family: 'Inter', sans-serif;
    }

    /* Título e Subtítulo */
    .header-container {
        text-align: center;
        padding: 60px 0 40px 0;
    }
    .main-title {
        font-size: 60px;
        font-weight: 800;
        letter-spacing: -2px;
        background: linear-gradient(135deg, #fff 30%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    .sub-title {
        color: #64748b;
        font-size: 20px;
        font-weight: 400;
    }

    /* Container dos Botões */
    .hub-grid {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
    }

    /* Estilização Geral dos Botões do Streamlit para o Hub */
    div.stButton > button {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 32px !important;
        height: 280px !important;
        width: 100% !important;
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        color: white !important;
        display: flex;
        flex-direction: column;
        padding: 40px !important;
    }

    div.stButton > button:hover {
        background: rgba(255, 255, 255, 0.07) !important;
        border-color: rgba(59, 130, 246, 0.5) !important;
        transform: translateY(-12px);
        box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
    }

    /* Estilo Interno dos Botões (Texto) */
    .btn-label {
        font-size: 24px;
        font-weight: 700;
        margin-top: 20px;
        display: block;
    }
    .btn-desc {
        font-size: 14px;
        color: #94a3b8;
        font-weight: 400;
        margin-top: 8px;
        display: block;
    }

    /* Cards de Métricas Internas */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 24px;
        padding: 24px;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 3. DICIONÁRIO DE METAS E TRATAMENTO (ROBUSTEZ MANTIDA)
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

def limpar_valor_numerico(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "None", "---", "nan"]: return None
    try:
        s = str(valor).replace('%', '').replace(',', '.').strip()
        return float(s)
    except: return None

def converter_tma_segundos(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "0", "00:00:00", "None"]: return None
    try:
        partes = str(valor).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        return float(str(valor).replace(',', '.'))
    except: return None

def definir_cor_kpi(valor_num, metrica, metas):
    if valor_num is None: return "#475569"
    conf = metas.get(metrica)
    if not conf: return "#f8fafc"
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']
    if menor:
        return "#22c55e" if valor_num <= m else ("#eab308" if valor_num <= m + tol else "#ef4444")
    return "#22c55e" if valor_num >= m else ("#eab308" if valor_num >= m - tol else "#ef4444")

def exibir_card(label, valor_display, cor="#f8fafc", icon=""):
    txt = "---" if valor_display is None or str(valor_display).strip() in ["nan", "None", ""] else str(valor_display)
    st.markdown(f"""
        <div class="metric-card" style="border-top: 4px solid {cor};">
            <p style="margin: 0; font-size: 12px; color: #94a3b8; font-weight: 600; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 10px 0 0 0; color: #fff; font-size: 28px;">{icon} {txt}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        cols_originais = {c.lower(): c for c in df.columns}
        target_op = cols_originais.get('operador', 'Operador')
        target_mat = cols_originais.get('matricula', 'Matricula')
        for m in list(METAS_BASE.keys()) + ['Pausa Total']:
            if m == 'Silencio':
                origem = cols_originais.get('silencio (%)') or cols_originais.get('silencio') or next((c for c in df.columns if 'silencio' in c.lower()), None)
            else:
                origem = cols_originais.get(m.lower())
            if origem:
                df[f'{m}_num'] = df[origem].apply(converter_tma_segundos if 'TMA' in m or 'Pausa' in m else limpar_valor_numerico)
                df[m] = df[origem].astype(str).replace(['nan', 'None'], '---')
            else:
                df[f'{m}_num'] = None
                df[m] = "---"
        return df, target_op, target_mat
    except: return None, None, None

# --- HUB INICIAL PREMIUM ---
if st.session_state.servico is None:
    st.markdown("""
        <div class="header-container">
            <h1 class="main-title">NDI Performance</h1>
            <p class="sub-title">Selecione a unidade de negócio para visualizar os indicadores</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_hub1, col_hub2, col_hub3 = st.columns(3)
    
    with col_hub1:
        if st.button("🏢\n\nSAC NDI"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with col_hub2:
        if st.button("🏦\n\nSAC PPO"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with col_hub3:
        if st.button("🏥\n\nSAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    # --- ÁREA INTERNA ---
    with st.sidebar:
        st.markdown(f"### 📍 {st.session_state.servico}")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        supervisor = st.selectbox("Supervisor:", lista)
        st.write("---")
        if st.sidebar.button("🏠 Voltar ao Início"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)
        if df is not None:
            metas_atuais = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            metas_atuais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[0]:
                mat = st.text_input("Digite a Matrícula:", placeholder="Ex: 1210...")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"#### Bem-vindo, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_atuais))
                            exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'], 'Silencio', metas_atuais), "🔇")
                        with c2:
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_atuais))
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', metas_atuais), "⏱️")
                        with c3:
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_atuais), "📞")
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'], 'Pesquisa', metas_atuais), "⭐")

            with tabs[1]:
                eq = df[df[col_op].astype(str).str.upper() == 'EQUIPE']
                if not eq.empty:
                    eq = eq.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    for i, m in enumerate(['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']):
                        with [c1, c2, c3][i % 3]:
                            exibir_card(f"{m} (Equipe)", eq[m], definir_cor_kpi(eq[f'{m}_num'], m, metas_atuais))

            with tabs[2]:
                m_rank = st.selectbox("Selecione a métrica:", list(metas_atuais.keys()))
                df_r = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                          (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                          (df[f'{m_rank}_num'].notna())].copy()
                if not df_r.empty:
                    top = df_r.nsmallest(5, f'{m_rank}_num') if metas_atuais[m_rank]['menor_melhor'] else df_r.nlargest(5, f'{m_rank}_num')
                    for i, row in enumerate(top.itertuples()):
                        exibir_card(f"{i+1}º Lugar - {getattr(row, col_op)}", getattr(row, m_rank), definir_cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, metas_atuais))

            with tabs[3]:
                m_s = st.selectbox("Análise de Meta:", list(metas_atuais.keys()), key="s_box")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                          (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                          (df[f'{m_s}_num'].notna())].copy()
                if not df_s.empty:
                    conf = metas_atuais[m_s]
                    df_s['Status'] = df_s[f'{m_s}_num'].apply(lambda x: 'Dentro da Meta' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                    st.plotly_chart(px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#22c55e','Fora da Meta':'#ef4444'}))
                    st.dataframe(df_s[[col_op, m_s, 'Status']], hide_index=True, use_container_width=True)
