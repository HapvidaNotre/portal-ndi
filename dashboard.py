import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ESTILO CSS (HUB MODERNO + CARDS)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { text-align: center; color: #004a99; font-family: 'Segoe UI', sans-serif; margin-bottom: 40px; }
    
    /* Estilo dos Botões do Hub Inicial */
    div.stButton > button {
        border: none; border-radius: 20px; background: white; padding: 40px 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05); transition: all 0.3s ease-in-out;
        height: 220px !important; display: flex; flex-direction: column;
        align-items: center; justify-content: center; color: #1f3a5f !important;
        font-size: 20px !important; font-weight: 600 !important;
    }
    div.stButton > button:hover {
        transform: translateY(-10px); box-shadow: 0 12px 25px rgba(0,74,153,0.15);
        border: 1px solid #004a99; color: #004a99 !important;
    }

    /* Estilo dos Cards de Métrica */
    .metric-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 3. DICIONÁRIO DE METAS
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

# 4. FUNÇÕES DE TRATAMENTO
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
    if valor_num is None: return "#999"
    conf = metas.get(metrica)
    if not conf: return "#333"
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']
    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m + tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m - tol else "#dc3545")

def exibir_card(label, valor_display, cor="#333", icon=""):
    txt = "---" if valor_display is None or str(valor_display).strip() in ["nan", "None", ""] else str(valor_display)
    st.markdown(f"""
        <div class="metric-card" style="border-left-color: {cor};">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {txt}</h2>
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
            # Mapeamento para Silencio ou Silencio (%)
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

# --- NAVEGAÇÃO / UI ---
if st.session_state.servico is None:
    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p>Selecione sua operação</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("🏢\n\nSAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    if c2.button("🏦\n\nSAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    if c3.button("🏥\n\nSAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()
else:
    with st.sidebar:
        st.write(f"📍 Operação: **{st.session_state.servico}**")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        supervisor = st.selectbox("Escolha o Supervisor:", lista)
        if st.button("⬅️ Voltar ao Hub"): st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)
        if df is not None:
            # Metas Dinâmicas (Regra Pausa)
            metas_atuais = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            metas_atuais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[0]: # INDIVIDUAL
                mat = st.text_input("Digite sua Matrícula:")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
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

            with tabs[1]: # EQUIPE
                eq = df[df[col_op].astype(str).str.upper() == 'EQUIPE']
                if not eq.empty:
                    eq = eq.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    for i, m in enumerate(['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']):
                        with [c1, c2, c3][i % 3]:
                            exibir_card(f"{m} (Equipe)", eq[m], definir_cor_kpi(eq[f'{m}_num'], m, metas_atuais))

            with tabs[2]: # RANKING (FILTRO DE NULOS)
                m_rank = st.selectbox("Rankear por:", list(metas_atuais.keys()))
                df_r = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                          (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                          (df[f'{m_rank}_num'].notna())].copy()
                
                if not df_r.empty:
                    is_menor = metas_atuais[m_rank]['menor_melhor']
                    top = df_r.nsmallest(5, f'{m_rank}_num') if is_menor else df_r.nlargest(5, f'{m_rank}_num')
                    for i, row in enumerate(top.itertuples()):
                        exibir_card(f"{i+1}º Lugar - {getattr(row, col_op)}", getattr(row, m_rank), definir_cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, metas_atuais))
                else: st.info("Sem dados válidos para gerar este ranking.")

            with tabs[3]: # SAÚDE
                m_s = st.selectbox("Analisar Saúde de:", list(metas_atuais.keys()), key="saude_key")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                          (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                          (df[f'{m_s}_num'].notna())].copy()
                
                if not df_s.empty:
                    conf = metas_atuais[m_s]
                    df_s['Status'] = df_s[f'{m_s}_num'].apply(lambda x: 'Dentro da Meta' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                    st.plotly_chart(px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}))
                    st.dataframe(df_s[[col_op, m_s, 'Status']], hide_index=True, use_container_width=True)
                else: st.warning("Dados insuficientes para análise nesta métrica.")
