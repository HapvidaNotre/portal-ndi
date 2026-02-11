import streamlit as st
import pandas as pd
import plotly.express as px
import copy

# CONFIG
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# CSS
st.markdown("""
<style>
.stApp { background-color: #f8f9fa; }

.main-title { 
    text-align: center; 
    color: #004a99; 
    margin-bottom: 20px; 
    padding-top: 20px;
}

.hub-container {
    display: flex;
    justify-content: center;
    gap: 60px;
    margin-top: 60px;
    flex-wrap: wrap;
}

.hub-card { width: 260px; }

.hub-card div.stButton > button {
    width: 100%;
    height: 220px !important;
    border-radius: 24px;
    background: white;
    padding: 30px 20px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    transition: all 0.3s ease-in-out;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 20px !important;
    font-weight: 700 !important;
}

.hub-card div.stButton > button:hover {
    transform: translateY(-8px);
    box-shadow: 0 14px 28px rgba(0,74,153,0.18);
    border: 2px solid #004a99;
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

if 'servico' not in st.session_state:
    st.session_state.servico = None

# METAS
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

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# FUNÇÕES
def limpar_valor_numerico(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "None", "---", "nan"]:
        return None
    try:
        return float(str(valor).replace('%','').replace(',','.'))
    except:
        return None

def converter_tma_segundos(valor):
    if pd.isna(valor) or str(valor).strip() in ["","0","00:00:00","None"]:
        return None
    try:
        p = str(valor).split(':')
        if len(p)==3:
            return int(p[0])*60 + int(p[1]) + int(p[2])/60
        return float(str(valor).replace(',','.'))
    except:
        return None

def definir_cor_kpi(valor_num, metrica, metas):
    if valor_num is None: return "#999"
    conf = metas.get(metrica)
    if not conf: return "#333"

    m,tol,menor = conf['valor'],conf['margem'],conf['menor_melhor']

    if menor:
        return "#28a745" if valor_num<=m else ("#ffc107" if valor_num<=m+tol else "#dc3545")
    return "#28a745" if valor_num>=m else ("#ffc107" if valor_num>=m-tol else "#dc3545")

def exibir_card(label, valor_display, cor="#333", icon=""):
    txt = "---" if valor_display in [None,"nan","None",""] else str(valor_display)

    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:bold;text-transform:uppercase;">
            {label}
        </p>
        <h2 style="margin:5px 0 0 0;color:#1f3a5f;font-size:24px;font-weight:800;">
            {icon} {txt}
        </h2>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        SHEET_ID="1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url=f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
        df=pd.read_csv(url)
        df.columns=df.columns.str.strip()

        cols_originais={c.lower():c for c in df.columns}
        target_op=cols_originais.get('operador','Operador')
        target_mat=cols_originais.get('matricula','Matricula')

        for m in list(METAS_BASE.keys())+['Pausa Total']:
            origem = cols_originais.get(m.lower())

            if origem:
                df[f'{m}_num']=df[origem].apply(
                    converter_tma_segundos if 'TMA' in m or 'Pausa' in m else limpar_valor_numerico
                )
                df[m]=df[origem].astype(str).replace(['nan','None'],'---')
            else:
                df[f'{m}_num']=None
                df[m]="---"

        return df,target_op,target_mat
    except:
        return None,None,None

# HUB
if st.session_state.servico is None:

    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p>Selecione sua operação</p></div>", unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)

    with col1:
        if st.button("🏢\n\nSAC NDI", use_container_width=True):
            st.session_state.servico="SAC NDI"
            st.rerun()

    with col2:
        if st.button("🏦\n\nSAC PPO", use_container_width=True):
            st.session_state.servico="SAC PPO"
            st.rerun()

    with col3:
        if st.button("🏥\n\nSAC HAPVIDA", use_container_width=True):
            st.session_state.servico="SAC HAPVIDA"
            st.rerun()

else:

    with st.sidebar:

        st.markdown(f"### 📍 {st.session_state.servico}")

        if st.session_state.servico=="SAC NDI":
            lista=["Selecione...","Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]
        else:
            lista=["Selecione...","Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex","Equipe Hapvida"]

        supervisor=st.selectbox("Escolha o Supervisor:",lista)

        if st.button("⬅️ Voltar ao Hub"):
            st.session_state.servico=None
            st.rerun()

    if supervisor!="Selecione...":

        df,col_op,col_mat=carregar_dados_aba(supervisor)

        if df is not None:

            metas_atuais=copy.deepcopy(METAS_BASE)

            metas_atuais['Pausa Total']={'valor':21.75,'margem':3.0,'menor_melhor':True}

            tabs = st.tabs(["👤 Individual","👥 Equipe","🏆 Ranking","📊 Saúde"])

            # INDIVIDUAL
            with tabs[0]:

                mat = st.text_input("Digite sua Matrícula:")

                if mat:
                    res=df[df[col_mat].astype(str)==mat.strip()]

                    if not res.empty:
                        r=res.iloc[0]

                        st.subheader(f"Olá, {r[col_op]}")

                        c1,c2,c3=st.columns(3)

                        with c1:
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'],'Aderencia',metas_atuais))
                            exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'],'Silencio',metas_atuais),"🔇")

                        with c2:
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'],'Resolutividade',metas_atuais))
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'],'Pausa Total',metas_atuais),"⏱️")

                        with c3:
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'],'TMA Voz',metas_atuais),"📞")
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'],'Pesquisa',metas_atuais),"⭐")

            # RANKING (CORRIGIDO)
            with tabs[2]:

                m_rank = st.selectbox("Ver Ranking de:", list(metas_atuais.keys()))

                df_rank = df[
                    (df[col_op].astype(str).str.upper() != 'EQUIPE') &
                    (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{m_rank}_num'].notna())
                ].copy()

                if not df_rank.empty:

                    is_menor = metas_atuais[m_rank]['menor_melhor']

                    if is_menor:
                        top = df_rank.sort_values(by=f'{m_rank}_num').head(5)
                    else:
                        top = df_rank.sort_values(by=f'{m_rank}_num', ascending=False).head(5)

                    for i, (_, row) in enumerate(top.iterrows()):

                        exibir_card(
                            f"{i+1}º Lugar - {row[col_op]}",
                            row[m_rank],
                            definir_cor_kpi(row[f'{m_rank}_num'], m_rank, metas_atuais)
                        )

            # SAÚDE
            with tabs[3]:

                m_saude=st.selectbox("Analisar Saúde de:", list(metas_atuais.keys()))

                df_saude=df[
                    (df[col_op].astype(str).str.upper()!='EQUIPE') &
                    (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{m_saude}_num'].notna())
                ].copy()

                if not df_saude.empty:

                    conf=metas_atuais[m_saude]

                    df_saude['Status']=df_saude[f'{m_saude}_num'].apply(
                        lambda x:'Meta OK' if (x<=conf['valor'] if conf['menor_melhor'] else x>=conf['valor']) else 'Fora da Meta'
                    )

                    st.plotly_chart(
                        px.pie(
                            df_saude,
                            names='Status',
                            hole=0.5,
                            color='Status',
                            color_discrete_map={'Meta OK':'#28a745','Fora da Meta':'#dc3545'}
                        )
                    )

                    st.dataframe(df_saude[[col_op,m_saude,'Status']], hide_index=True, use_container_width=True)

