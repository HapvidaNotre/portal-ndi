import streamlit as st
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- SESSION ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

# ---------- CSS ----------
st.markdown("""
<style>

.stApp { background-color: #f8f9fa; }

/* HEADER CENTRALIZADO */
.header-container {
    display:flex;
    justify-content:center;
    align-items:center;
    gap:15px;
    padding:30px 0;
}

/* BOTÕES HUB */
div.stButton > button {
    background: linear-gradient(135deg,#0f172a,#1e3a8a);
    color:white;
    font-weight:700;
    font-size:18px;
    height:65px;
    border-radius:12px;
    border:none;
    transition:all .25s ease;
    box-shadow:0 4px 12px rgba(0,0,0,.15);
}

div.stButton > button:hover {
    transform:translateY(-3px);
    background:linear-gradient(135deg,#1e3a8a,#2563eb);
    box-shadow:0 8px 18px rgba(0,0,0,.25);
}

/* CARDS */
.metric-card {
    background:white;
    padding:15px;
    border-radius:10px;
    box-shadow:2px 2px 8px rgba(0,0,0,.05);
    border-left:6px solid;
    margin-bottom:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------- METAS ----------
METAS_BASE = {
    'Aderencia': {'valor':85,'margem':5,'menor_melhor':False,'unidade':'%'},
    'Resolutividade': {'valor':75,'margem':5,'menor_melhor':False,'unidade':'%'},
    'TMA Voz': {'valor':8,'margem':1,'menor_melhor':True,'unidade':' min'},
    'Pesquisa': {'valor':4.5,'margem':0.5,'menor_melhor':False,'unidade':''},
    'Silencio': {'valor':15,'margem':5,'menor_melhor':True,'unidade':'%'},
    'Pausa Total': {'valor':21.75,'margem':3,'menor_melhor':True,'unidade':'%'}
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# ---------- EQUIPES ----------
EQUIPES = {
    "SAC NDI":["Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"],
    "SAC PPO":["Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex"],
    "SAC HAPVIDA":["Equipe Hapvida"]
}

# ---------- FUNÇÕES ----------
def limpar_valor(valor):
    if pd.isna(valor): return None
    try:
        return float(str(valor).replace('%','').replace(',','.'))
    except:
        return None

def converter_tma(valor):
    if pd.isna(valor): return None
    try:
        p=str(valor).split(':')
        if len(p)==3:
            return int(p[0])*60+int(p[1])+int(p[2])/60
        return float(str(valor).replace(',','.'))
    except:
        return None

def cor_kpi(v,metrica):
    if v is None or pd.isna(v): return "#999"
    c=METAS_BASE[metrica]
    if c['menor_melhor']:
        return "#28a745" if v<=c['valor'] else "#dc3545"
    return "#28a745" if v>=c['valor'] else "#dc3545"

def card(label,valor,cor):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="font-size:11px;color:#666;font-weight:bold;">{label}</p>
        <h4 style="color:#1f3a5f;">{valor}</h4>
    </div>
    """, unsafe_allow_html=True)

# ---------- CARREGAMENTO ----------
@st.cache_data(ttl=60)
def carregar_dados(aba):

    SHEET_ID="1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
    url=f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ','%20')}"
    df=pd.read_csv(url)

    df.columns=df.columns.str.strip()
    cols={c.lower():c for c in df.columns}

    col_op=cols.get('operador','Operador')
    col_mat=cols.get('matricula','Matricula')

    for m in METAS_BASE:
        origem=cols.get(m.lower())
        if origem:
            if 'TMA' in m:
                df[m+"_num"]=df[origem].apply(converter_tma)
            else:
                df[m+"_num"]=df[origem].apply(limpar_valor)
            df[m]=df[origem].astype(str)

    # ----- PAUSA TOTAL -----
    imp=cols.get('pausa improdutiva')
    prod=cols.get('pausa produtiva')

    if imp and prod:
        df['Pausa Total_num']=df[imp].apply(limpar_valor).fillna(0)+df[prod].apply(limpar_valor).fillna(0)
        df['Pausa Total']=df['Pausa Total_num'].apply(lambda x:f"{x:.1f}%")

    return df,col_op,col_mat

# ---------- HUB ----------
if st.session_state.servico is None:

    st.markdown("""
    <div class="header-container">
        <div style="font-size:50px;">🚀</div>
        <h1>Portal de Performance NDI</h1>
    </div>
    """, unsafe_allow_html=True)

    c1,c2,c3=st.columns(3)

    if c1.button("SAC NDI",use_container_width=True):
        st.session_state.servico="SAC NDI"
        st.rerun()

    if c2.button("SAC PPO",use_container_width=True):
        st.session_state.servico="SAC PPO"
        st.rerun()

    if c3.button("SAC HAPVIDA",use_container_width=True):
        st.session_state.servico="SAC HAPVIDA"
        st.rerun()

# ---------- DASHBOARD ----------
else:

    with st.sidebar:

        st.markdown(f"### {st.session_state.servico}")
        supervisor=st.selectbox("Supervisor:",["Selecione..."]+EQUIPES[st.session_state.servico])

        if st.button("Voltar"):
            st.session_state.servico=None
            st.rerun()

    if supervisor!="Selecione...":

        with st.spinner("Carregando dados..."):
            time.sleep(.8)
            df,col_op,col_mat=carregar_dados(supervisor)

        df_eq=df[(df[col_op].str.upper()!="EQUIPE") & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))]

        t1,t2,t3,t4=st.tabs(["Individual","Equipe","Ranking","Saúde"])

        # ---------- INDIVIDUAL ----------
        with t1:

            mat=st.text_input("Matrícula")

            if mat:
                r=df[df[col_mat].astype(str)==mat]

                if not r.empty:
                    r=r.iloc[0]
                    st.subheader(r[col_op])

                    c1,c2,c3=st.columns(3)

                    with c1:
                        card("Aderência",r['Aderencia'],cor_kpi(r['Aderencia_num'],'Aderencia'))
                        card("Silêncio",r['Silencio'],cor_kpi(r['Silencio_num'],'Silencio'))

                    with c2:
                        card("Resolutividade",r['Resolutividade'],cor_kpi(r['Resolutividade_num'],'Resolutividade'))
                        card("Pausa Total",r['Pausa Total'],cor_kpi(r['Pausa Total_num'],'Pausa Total'))

                    with c3:
                        card("TMA Voz",r['TMA Voz'],cor_kpi(r['TMA Voz_num'],'TMA Voz'))
                        card("Pesquisa",r['Pesquisa'],cor_kpi(r['Pesquisa_num'],'Pesquisa'))

        # ---------- EQUIPE ----------
        with t2:

            cols_cards=st.columns(len(METAS_BASE))

            for i,(m,c) in enumerate(METAS_BASE.items()):
                media=df_eq[m+"_num"].mean()
                txt=f"{media:.1f}{c['unidade']}" if pd.notna(media) else "---"
                with cols_cards[i]:
                    card(m,txt,cor_kpi(media,m))

        # ---------- RANKING ----------
        with t3:

            m_sel=st.selectbox("Métrica",list(METAS_BASE.keys()))

            top=df_eq.sort_values(m_sel+"_num",ascending=METAS_BASE[m_sel]['menor_melhor']).head(5)

            for i,(_,row) in enumerate(top.iterrows()):
                card(f"{i+1}º {row[col_op]}",row[m_sel],"#28a745")

        # ---------- SAÚDE ----------
        with t4:

            m_sel=st.selectbox("Selecione a Métrica:",list(METAS_BASE.keys()))
            conf=METAS_BASE[m_sel]

            df_s=df_eq.copy()

            def status(v):
                if pd.isna(v): return "Sem dado"
                if conf['menor_melhor']:
                    return "Meta OK" if v<=conf['valor'] else "Fora da Meta"
                return "Meta OK" if v>=conf['valor'] else "Fora da Meta"

            df_s['Status']=df_s[m_sel+"_num"].apply(status)

            tabela=df_s[[col_mat,m_sel,'Status']].rename(columns={col_mat:'Matrícula'})
            st.dataframe(tabela,use_container_width=True)

        st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
