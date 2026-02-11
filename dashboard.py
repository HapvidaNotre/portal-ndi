import streamlit as st
import pandas as pd
import plotly.express as px
import time
import traceback
from datetime import datetime

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# =====================================================
# CSS + LOADING SKELETON
# =====================================================
st.markdown("""
<style>
.stApp { background-color: #f8f9fa; }

@keyframes pulse {
    0% {opacity: 0.6;}
    50% {opacity: 1;}
    100% {opacity: 0.6;}
}

.metric-card {
    background-color: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 15px;
    border-left: 8px solid;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# SKELETON LOADING
# =====================================================
def skeleton_cards(qtd=3):
    cols = st.columns(qtd)
    for c in cols:
        with c:
            st.markdown("""
            <div style="
                background:#f0f2f6;
                height:120px;
                border-radius:12px;
                animation:pulse 1.5s infinite;">
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# SESSION
# =====================================================
if 'servico' not in st.session_state:
    st.session_state.servico = None

# =====================================================
# METAS
# =====================================================
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

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110']

# =====================================================
# FUNÇÕES DE TRATAMENTO
# =====================================================
def limpar_valor_numerico(valor):
    if pd.isna(valor): return None
    try:
        return float(str(valor).replace('%','').replace(',','.'))
    except:
        return None

def converter_tma_segundos(valor):
    if pd.isna(valor): return None
    try:
        partes = str(valor).split(':')
        if len(partes)==3:
            return int(partes[0])*60 + int(partes[1]) + int(partes[2])/60
        return float(str(valor).replace(',','.'))
    except:
        return None

# =====================================================
# KPI COR
# =====================================================
def definir_cor_kpi(valor, metrica, metas):
    if valor is None:
        return "#999"

    conf = metas.get(metrica)
    if not conf:
        return "#333"

    meta = conf['valor']
    margem = conf['margem']
    menor = conf['menor_melhor']

    if menor:
        if valor <= meta:
            return "#28a745"
        elif valor <= meta + margem:
            return "#ffc107"
        else:
            return "#dc3545"
    else:
        if valor >= meta:
            return "#28a745"
        elif valor >= meta - margem:
            return "#ffc107"
        else:
            return "#dc3545"

# =====================================================
# CARD
# =====================================================
def exibir_card(label, valor_display, cor="#333"):
    txt = "---" if valor_display is None else str(valor_display)

    st.markdown(f"""
        <div class="metric-card" style="border-left-color:{cor};">
            <p style="font-size:12px;color:#666">{label}</p>
            <h2 style="color:#1f3a5f">{txt}</h2>
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# INSIGHTS AUTOMÁTICOS
# =====================================================
def gerar_insights(row, metas):
    insights = []

    for m, conf in metas.items():
        val = row.get(f"{m}_num")

        if val is None:
            continue

        meta = conf['valor']
        menor = conf['menor_melhor']

        if menor and val > meta:
            insights.append(f"⚠️ {m} acima da meta")
        elif not menor and val < meta:
            insights.append(f"⚠️ {m} abaixo da meta")
        elif menor and val < meta * 0.85:
            insights.append(f"🏆 Excelente desempenho em {m}")
        elif not menor and val > meta * 1.15:
            insights.append(f"🏆 Destaque em {m}")

    return insights

# =====================================================
# CARREGAMENTO SEGURO
# =====================================================
@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):

    try:
        with st.spinner("📡 Carregando dados..."):
            time.sleep(1)

            SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
            url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba}"

            df = pd.read_csv(url)
            df.columns = df.columns.str.strip()

            for m in METAS_BASE.keys():
                if m in df.columns:
                    if "TMA" in m:
                        df[f"{m}_num"] = df[m].apply(converter_tma_segundos)
                    else:
                        df[f"{m}_num"] = df[m].apply(limpar_valor_numerico)

            st.session_state["ultima_atualizacao"] = datetime.now()

            return df, None

    except Exception:
        return None, traceback.format_exc()

# =====================================================
# HUB
# =====================================================
if st.session_state.servico is None:

    st.title("🚀 Portal de Performance NDI")

    c1,c2,c3 = st.columns(3)

    if c1.button("SAC NDI"):
        st.session_state.servico = "SAC NDI"
        st.rerun()

    if c2.button("SAC PPO"):
        st.session_state.servico = "SAC PPO"
        st.rerun()

    if c3.button("SAC HAPVIDA"):
        st.session_state.servico = "SAC HAPVIDA"
        st.rerun()

# =====================================================
# DASHBOARD
# =====================================================
else:

    with st.sidebar:

        st.subheader(st.session_state.servico)

        supervisor = st.text_input("Supervisor")

        if st.button("Voltar"):
            st.session_state.servico = None
            st.rerun()

    if supervisor:

        df, erro = carregar_dados_aba(supervisor)

        if erro:
            st.error("Erro ao carregar dados")
            st.code(erro)
            st.stop()

        if "ultima_atualizacao" in st.session_state:
            st.caption(f"Atualizado em {st.session_state['ultima_atualizacao']}")

        tabs = st.tabs(["Individual","Ranking"])

        # =====================================================
        # INDIVIDUAL
        # =====================================================
        with tabs[0]:

            mat = st.text_input("Digite matrícula")

            if mat:

                res = df[df["Matricula"].astype(str).str.contains(mat)]

                if not res.empty:

                    r = res.iloc[0]

                    skeleton_cards()
                    time.sleep(0.4)

                    cols = st.columns(3)

                    for i,m in enumerate(["Aderencia","TMA Voz","Pesquisa"]):

                        with cols[i]:

                            exibir_card(
                                m,
                                r[m],
                                definir_cor_kpi(r[f"{m}_num"],m,METAS_BASE)
                            )

                    insights = gerar_insights(r,METAS_BASE)

                    if insights:
                        st.subheader("💡 Insights")
                        for i in insights:
                            st.info(i)

        # =====================================================
        # RANKING (CORRIGIDO)
        # =====================================================
        with tabs[1]:

            m_rank = st.selectbox("Ranking de",list(METAS_BASE.keys()))

            df_rank = df[
                (df[f"{m_rank}_num"].notna()) &
                (~df["Matricula"].astype(str).isin(MATRICULAS_BACKOFFICE))
            ].copy()

            if not df_rank.empty:

                is_menor = METAS_BASE[m_rank]['menor_melhor']

                if is_menor:
                    top = df_rank.sort_values(f"{m_rank}_num").head(5)
                else:
                    top = df_rank.sort_values(f"{m_rank}_num",ascending=False).head(5)

                cols = st.columns(5)

                for i,row in enumerate(top.itertuples()):

                    with cols[i]:

                        exibir_card(
                            f"{i+1}º - {row.Operador}",
                            getattr(row,m_rank),
                            definir_cor_kpi(
                                getattr(row,f"{m_rank}_num"),
                                m_rank,
                                METAS_BASE
                            )
                        )
