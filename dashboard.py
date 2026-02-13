import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- CSS ----------
st.markdown("""
<style>
.stApp { background-color: #f8f9fa; }

.metric-card {
    background-color: white;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.05);
    border-left: 6px solid;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- METAS ----------
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True, 'unidade': ' min'},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False, 'unidade': ''},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True, 'unidade': '%'},
    'Pausa Total': {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True, 'unidade': '%'}
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# ---------- FUNÇÕES ----------
def limpar_valor_numerico(valor):
    if pd.isna(valor): return None
    try:
        return float(str(valor).replace('%','').replace(',','.'))
    except:
        return None

def converter_tma(valor):
    if pd.isna(valor): return None
    try:
        p = str(valor).split(':')
        if len(p)==3:
            return int(p[0])*60 + int(p[1]) + int(p[2])/60
        return float(str(valor).replace(',','.'))
    except:
        return None

def definir_cor_kpi(valor_num, metrica):
    if valor_num is None: return "#999"
    conf = METAS_BASE[metrica]
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']

    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m+tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m-tol else "#dc3545")

def exibir_card(label, valor_display, cor):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:bold;text-transform:uppercase;">{label}</p>
        <h4 style="margin:5px 0 0 0;color:#1f3a5f;font-weight:800;">{valor_display}</h4>
    </div>
    """, unsafe_allow_html=True)

# ---------- CARREGAMENTO ----------
@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):

    SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()
    cols = {c.lower(): c for c in df.columns}

    col_op = cols.get('operador', 'Operador')
    col_mat = cols.get('matricula', 'Matricula')

    for m in METAS_BASE.keys():
        origem = cols.get(m.lower())
        if origem:
            if 'TMA' in m:
                df[f'{m}_num'] = df[origem].apply(converter_tma)
            else:
                df[f'{m}_num'] = df[origem].apply(limpar_valor_numerico)

            df[m] = df[origem].astype(str)

    # ----- PAUSA TOTAL = IMPRODUTIVA + PRODUTIVA -----
    col_imp = cols.get('pausa improdutiva')
    col_prod = cols.get('pausa produtiva')

    if col_imp and col_prod:
        df['Pausa Improdutiva_num'] = df[col_imp].apply(limpar_valor_numerico)
        df['Pausa Produtiva_num'] = df[col_prod].apply(limpar_valor_numerico)

        df['Pausa Total_num'] = (
            df['Pausa Improdutiva_num'].fillna(0)
            + df['Pausa Produtiva_num'].fillna(0)
        )

        df['Pausa Total'] = df['Pausa Total_num'].apply(lambda x: f"{x:.1f}%")

    return df, col_op, col_mat

# ---------- HUB ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    st.title("🚀 Portal de Performance NDI")

    c1,c2,c3 = st.columns(3)

    with c1:
        if st.button("SAC NDI", use_container_width=True):
            st.session_state.servico = "SAC NDI"
            st.rerun()

    with c2:
        if st.button("SAC PPO", use_container_width=True):
            st.session_state.servico = "SAC PPO"
            st.rerun()

    with c3:
        if st.button("SAC HAPVIDA", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

# ---------- DASHBOARD ----------
else:

    with st.sidebar:

        st.markdown(f"### {st.session_state.servico}")

        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]
        else:
            lista = ["Selecione...", "Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex","Equipe Hapvida"]

        supervisor = st.selectbox("Supervisor:", lista)

        if st.button("Voltar"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":

        df, col_op, col_mat = carregar_dados_aba(supervisor)

        df_eq = df[(df[col_op].astype(str).str.upper()!='EQUIPE') &
                   (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))].copy()

        t1,t2,t3,t4 = st.tabs(["Individual","Equipe","Ranking","Saúde"])

        # ---------- INDIVIDUAL ----------
        with t1:

            mat = st.text_input("Matrícula")

            if mat:
                res = df[df[col_mat].astype(str)==mat]

                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(r[col_op])

                    c1,c2,c3 = st.columns(3)

                    with c1:
                        exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'],'Aderencia'))
                        exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'],'Silencio'))

                    with c2:
                        exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'],'Resolutividade'))
                        exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'],'Pausa Total'))

                    with c3:
                        exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'],'TMA Voz'))
                        exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'],'Pesquisa'))

        # ---------- EQUIPE ----------
        with t2:

            cols_cards = st.columns(len(METAS_BASE))

            for i,(metrica,conf) in enumerate(METAS_BASE.items()):
                media = df_eq[f'{metrica}_num'].mean()
                txt = f"{media:.1f}{conf['unidade']}" if pd.notna(media) else "---"
                cor = definir_cor_kpi(media,metrica)

                with cols_cards[i]:
                    exibir_card(metrica,txt,cor)

        # ---------- RANKING ----------
        with t3:

            metrica_sel = st.selectbox("Métrica", list(METAS_BASE.keys()))

            top = df_eq.sort_values(
                by=f'{metrica_sel}_num',
                ascending=METAS_BASE[metrica_sel]['menor_melhor']
            ).head(5)

            for i,(_,row) in enumerate(top.iterrows()):
                exibir_card(f"{i+1}º {row[col_op]}", row[metrica_sel], "#28a745")

        # ---------- SAÚDE (COM MATRÍCULA) ----------
        with t4:

            st.subheader("Saúde da Operação")

            metrica_sel = st.selectbox("Selecione a Métrica:", list(METAS_BASE.keys()))

            conf = METAS_BASE[metrica_sel]

            df_saude = df_eq.copy()

            def verificar_status(valor):
                if pd.isna(valor):
                    return "Sem dado"

                if conf['menor_melhor']:
                    return "Meta OK" if valor <= conf['valor'] else "Fora da Meta"
                else:
                    return "Meta OK" if valor >= conf['valor'] else "Fora da Meta"

            df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)

            df_saude['Valor'] = df_saude.apply(
                lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---",
                axis=1
            )

            tabela = df_saude[[col_mat, 'Valor', 'Status']].rename(
                columns={
                    col_mat: 'Matrícula',
                    'Valor': metrica_sel
                }
            )

            st.dataframe(tabela, use_container_width=True)

