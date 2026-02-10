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
    section[data-testid="stSidebar"] div.stButton > button {
        height: auto !important; padding: 10px 15px; font-size: 14px !important; border-radius: 10px;
    }
    .metric-card {
        background-color: white; padding: 15px; border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 15px; border-left: 8px solid;
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
    if pd.isna(valor) or str(valor).strip() == "": return None
    try:
        s_val = str(valor).replace('%', '').replace(',', '.').replace(' ', '').strip()
        return float(s_val) if s_val else None
    except: return None

def converter_tma_minutos(tempo_str):
    if pd.isna(tempo_str) or str(tempo_str).strip() in ["0", "00:00:00", "", "None"]: return None
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return float(str(tempo_str).replace(',', '.'))
    except: return None

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    if valor is None: return "#999" # Cor cinza para sem dados
    config = metas_atuais.get(metrica_key)
    if not config: return "#333"
    
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        return "#28a745" if valor <= m else ("#ffc107" if valor <= m + tol else "#dc3545")
    return "#28a745" if valor >= m else ("#ffc107" if valor >= m - tol else "#dc3545")

def exibir_card(label, valor, cor="#333", icon=""):
    # Garante que 'None' apareça como '0' ou '---'
    v_fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else str(valor)
    if v_fmt == "None": v_fmt = "---"
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
        
        metricas_processar = list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']
        for m in metricas_processar:
            # Busca flexível por "Silencio (%)" conforme sua imagem
            col_origem = col_map.get('silencio (%)') if m == 'Silencio' else col_map.get(m.lower())
            
            if col_origem:
                df[f'{m}_num'] = df[col_origem].apply(converter_tma_minutos if 'TMA' in m or 'Pausa' in m else converter_para_numero)
                if m not in df.columns: df[m] = df[col_origem]
            else:
                df[f'{m}_num'] = None
                df[m] = "---"
        return df, target_op, target_mat
    except: return None, None, None

# --- HUB INICIAL ---
if st.session_state.servico is None:
    st.markdown("<br><div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p style='color: #666;'>Gestão de Indicadores em Tempo Real</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢\n\nSAC NDI", use_container_width=True): st.session_state.servico = "SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦\n\nSAC PPO", use_container_width=True): st.session_state.servico = "SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥\n\nSAC HAPVIDA", use_container_width=True): st.session_state.servico = "SAC HAPVIDA"; st.rerun()
else:
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        opcoes = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        supervisor = st.selectbox("Supervisor:", opcoes)
        if st.button("⬅️ Voltar ao Hub"): st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            metas_s = METAS_BASE.copy()
            meta_p = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if st.session_state.servico == "SAC NDI" else 21.75)
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[1]: # ABA EQUIPE (CORRIGIDA)
                eq_row = df[df[col_op].astype(str).str.strip().str.upper() == 'EQUIPE']
                if not eq_row.empty:
                    e = eq_row.iloc[0]
                    c1, c2, c3 = st.columns(3)
                    m_eq = ['Aderencia', 'Resolutividade', 'Pausa Total', 'TMA Voz', 'Pesquisa', 'Silencio']
                    for i, m in enumerate(m_eq):
                        with [c1, c2, c3][i % 3]:
                            # Proteção contra erro de cálculo na equipe
                            val_num = e.get(f'{m}_num')
                            exibir_card(f"{m} (Equipe)", e.get(m, '---'), definir_cor_kpi(val_num, m, metas_s))

            with tabs[2]: # RANKING (FILTRO DE NULOS APLICADO)
                st.subheader("🏆 Melhores Performances")
                metrica_rank = st.selectbox("Rankear por:", list(metas_s.keys()))
                
                # FILTRO CRÍTICO: Remove quem não tem o número da métrica (evita o TypeError)
                df_rank = df[
                    (df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{metrica_rank}_num'].notna()) # Remove quem não tem valor
                ].copy()
                
                if not df_rank.empty:
                    is_menor = metas_s[metrica_rank]['menor_melhor']
                    top = df_rank.nsmallest(5, f'{metrica_rank}_num') if is_menor else df_rank.nlargest(5, f'{metrica_rank}_num')
                    
                    for idx, row in enumerate(top.itertuples()):
                        val_num = getattr(row, f'{metrica_rank}_num')
                        val_txt = getattr(row, metrica_rank)
                        exibir_card(f"{idx+1}º Lugar - {getattr(row, col_op)}", val_txt, definir_cor_kpi(val_num, metrica_rank, metas_s))
                else:
                    st.warning("Não existem dados válidos para gerar este ranking.")

            with tabs[3]: # SAÚDE (ESTABILIZADA)
                st.subheader("📊 Diagnóstico de Metas")
                m_saude = st.selectbox("Analisar Status:", list(metas_s.keys()), key="sb_saude")
                
                df_saude = df[
                    (df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{m_saude}_num'].notna())
                ].copy()
                
                if not df_saude.empty:
                    c = metas_s[m_saude]
                    df_saude['Status'] = df_saude[f'{m_saude}_num'].apply(
                        lambda x: 'Dentro da Meta' if (x <= c['valor'] if c['menor_melhor'] else x >= c['valor']) else 'Fora da Meta'
                    )
                    c_pie, c_list = st.columns([1, 1])
                    with c_pie:
                        st.plotly_chart(px.pie(df_saude, names='Status', hole=0.5, color='Status', 
                                             color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}), use_container_width=True)
                    with c_list:
                        st.dataframe(df_saude[[col_op, m_saude, 'Status']], hide_index=True, use_container_width=True)
                else:
                    st.info("Nenhum operador possui dados para esta análise.")

            with tabs[0]: # INDIVIDUAL
                mat_in = st.text_input("Sua Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r.get('Aderencia', '---'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                            exibir_card("Silêncio", r.get('Silencio', '---'), definir_cor_kpi(r['Silencio_num'], 'Silencio', metas_s), "🔇")
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', '---'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                            exibir_card("Pausa Total", r.get('Pausa Total', '---'), definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', metas_s), "⏱️")
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', '---'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                            exibir_card("Pesquisa", r.get('Pesquisa', '---'), definir_cor_kpi(r['Pesquisa_num'], 'Pesquisa', metas_s), "⭐")
