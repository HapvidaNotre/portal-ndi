import streamlit as st
import pandas as pd
import plotly.express as px
import copy

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. ESTILO CSS (CORREÇÕES DE VISIBILIDADE E PROPORÇÃO)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #f8f9fa; }

    /* Título do Hub - Garantindo visibilidade */
    .main-title { 
        text-align: center; 
        color: #004a99 !important; 
        margin-bottom: 30px; 
        padding-top: 20px;
    }
    .main-title h1 { font-weight: 800; font-size: 42px; color: #004a99 !important; }

    /* Botões do Hub Inicial */
    div.stButton > button {
        border: 1px solid #e2e8f0; 
        border-radius: 24px; 
        background: white; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        transition: all 0.3s ease;
        height: 180px !important; 
        color: #1f3a5f !important;
        font-size: 20px !important; 
        font-weight: 700 !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-5px); 
        border: 2px solid #004a99; 
        background-color: #f0f7ff !important;
    }

    /* BOTÃO VOLTAR (SIDEBAR) - TAMANHO CORRIGIDO */
    section[data-testid="stSidebar"] div.stButton > button {
        height: 45px !important;
        font-size: 14px !important;
        padding: 0 15px !important;
        border-radius: 10px !important;
        background: #f1f5f9 !important;
    }

    /* Cards de Métricas - Leitura Otimizada */
    .metric-card {
        background-color: white; 
        padding: 22px; 
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); 
        margin-bottom: 16px; 
        border-left: 8px solid;
    }
    .metric-label { margin: 0; font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase; }
    .metric-value { margin: 5px 0 0 0; color: #0f172a; font-size: 30px; font-weight: 800; }
    </style>
""", unsafe_allow_html=True)

# 3. DICIONÁRIO DE METAS
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True},
    'Pausa Total': {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# 4. FUNÇÕES DE TRATAMENTO DE DADOS
def limpar_valor_numerico(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "None", "---", "nan"]: return None
    try: return float(str(valor).replace('%','').replace(',','.'))
    except: return None

def converter_tma_segundos(valor):
    if pd.isna(valor) or str(valor).strip() in ["","0","00:00:00","None"]: return None
    try:
        p = str(valor).split(':')
        if len(p) == 3: return int(p[0])*60 + int(p[1]) + int(p[2])/60
        return float(str(valor).replace(',','.'))
    except: return None

def definir_cor_kpi(valor_num, metrica, metas):
    if valor_num is None: return "#cbd5e1"
    conf = metas.get(metrica, metas['Pausa Total'])
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']
    if menor:
        return "#10b981" if valor_num <= m else ("#f59e0b" if valor_num <= m + tol else "#ef4444")
    return "#10b981" if valor_num >= m else ("#f59e0b" if valor_num >= m - tol else "#ef4444")

def exibir_card(label, valor_display, cor="#cbd5e1", icon=""):
    txt = "---" if valor_display in [None,"nan","None","","---"] else str(valor_display)
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p class="metric-label">{label}</p>
        <h2 class="metric-value">{icon} {txt}</h2>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        cols_low = {c.lower(): c for c in df.columns}
        target_op = cols_low.get('operador', 'Operador')
        target_mat = cols_low.get('matricula', 'Matricula')

        for m in list(METAS_BASE.keys()):
            # Busca flexível para encontrar colunas (ex: busca 'pausa' dentro dos nomes das colunas)
            origem = None
            if 'Pausa' in m:
                origem = next((c for c in df.columns if 'pausa' in c.lower()), None)
            else:
                origem = cols_low.get(m.lower()) or next((c for c in df.columns if m.lower() in c.lower()), None)

            if origem:
                df[f'{m}_num'] = df[origem].apply(converter_tma_segundos if ('TMA' in m or 'Pausa' in m) else limpar_valor_numerico)
                df[m] = df[origem].astype(str).replace(['nan','None'],'---')
            else:
                df[f'{m}_num'] = None
                df[m] = "---"
        return df, target_op, target_mat
    except: return None, None, None

# 5. LOGICA DO HUB E NAVEGAÇÃO
if 'servico' not in st.session_state: st.session_state.servico = None

if st.session_state.servico is None:
    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p style='color:#64748b;'>Selecione a operação</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢\n\nSAC NDI"): st.session_state.servico="SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦\n\nSAC PPO"): st.session_state.servico="SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥\n\nSAC HAPVIDA"): st.session_state.servico="SAC HAPVIDA"; st.rerun()

else:
    with st.sidebar:
        st.markdown(f"### 📍 {st.session_state.servico}")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico=="SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        supervisor = st.selectbox("Escolha o Supervisor:", lista)
        
        if st.button("⬅️ Voltar ao Hub"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)
        
        if df is not None:
            # Metas dinâmicas
            metas_atuais = copy.deepcopy(METAS_BASE)
            meta_p = 21.75 if ("Erik" in supervisor or "Beatriz" in supervisor) else (16.60 if "NDI" in st.session_state.servico else 21.75)
            metas_atuais['Pausa Total']['valor'] = meta_p

            tabs = st.tabs(["👤 Individual", "🏆 Ranking", "📊 Saúde"])

            with tabs[0]:
                mat = st.text_input("Digite sua Matrícula:", placeholder="Ex: 123456")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'],'Aderencia', metas_atuais))
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'],'Pausa Total', metas_atuais), "⏱️")
                        with c2:
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'],'Resolutividade', metas_atuais))
                            exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'],'Silencio', metas_atuais), "🔇")
                        with c3:
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'],'TMA Voz', metas_atuais), "📞")
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'],'Pesquisa', metas_atuais), "⭐")
            
            with tabs[1]: # RANKING
                m_rank = st.selectbox("Ranking por:", list(metas_atuais.keys()))
                df_rank = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                             (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & 
                             (df[f'{m_rank}_num'].notna())].copy()
                if not df_rank.empty:
                    top = df_rank.sort_values(by=f'{m_rank}_num', ascending=metas_atuais[m_rank]['menor_melhor']).head(5)
                    for i, row in enumerate(top.itertuples()):
                        exibir_card(f"{i+1}º Lugar - {getattr(row, col_op)}", getattr(row, m_rank), definir_cor_kpi(getattr(row, f'{m_rank}_num'), m_rank, metas_atuais))

            with tabs[2]: # SAÚDE
                m_saude = st.selectbox("Analisar Indicador:", list(metas_atuais.keys()), key="saude_box")
                df_saude = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (df[f'{m_saude}_num'].notna())].copy()
                if not df_saude.empty:
                    conf = metas_atuais[m_saude]
                    df_saude['Status'] = df_saude[f'{m_saude}_num'].apply(lambda x: 'Meta OK' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                    st.plotly_chart(px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Meta OK':'#10b981','Fora da Meta':'#ef4444'}))
                    st.dataframe(df_saude[[col_op, m_saude, 'Status']], hide_index=True, use_container_width=True)
