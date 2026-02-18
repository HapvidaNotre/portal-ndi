import streamlit as st
import pandas as pd

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- CSS ----------
st.markdown("""
<style>

.stApp { background-color: #f8f9fa; }

/* BOTÕES HUB */
div.stButton > button {
    background-color: #0b2a6f;
    color: white;
    height: 70px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
    transition: 0.3s;
}

div.stButton > button:hover {
    background-color: #1341a3;
    transform: scale(1.03);
}

/* BOTÕES MENU */
.menu-btn button {
    height: 55px;
    font-weight: 700;
    border-radius: 10px;
}

/* CARDS */
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

# Aliases para nomes alternativos de colunas na planilha
ALIAS_COLUNAS = {
    'tma voz': ['tma voz', 'tma', 'tma_voz', 'tempo medio de atendimento', 'tempo médio de atendimento'],
    'pesquisa': ['pesquisa', 'nota pesquisa', 'nota_pesquisa', 'nps', 'nota de pesquisa'],
    'aderencia': ['aderencia', 'aderência', 'adh', 'adherencia'],
    'resolutividade': ['resolutividade', 'resolutividade%', 'resolut'],
    'silencio': ['silencio', 'silêncio', 'silencio%'],
    'pausa total': ['pausa total'],
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# ---------- FUNÇÕES ----------
def buscar_coluna(cols_dict, metrica):
    """Busca o nome real da coluna na planilha usando aliases."""
    aliases = ALIAS_COLUNAS.get(metrica.lower(), [metrica.lower()])
    for alias in aliases:
        if alias in cols_dict:
            return cols_dict[alias]
    return None

def limpar_valor_numerico(valor):
    if pd.isna(valor): return None
    try:
        return float(str(valor).replace('%','').replace(',','.').strip())
    except:
        return None

def converter_tma(valor):
    if pd.isna(valor): return None
    try:
        p = str(valor).strip().split(':')
        if len(p) == 3:
            return int(p[0]) * 60 + int(p[1]) + int(p[2]) / 60
        return float(str(valor).replace(',','.'))
    except:
        return None

def definir_cor_kpi(valor_num, metrica):
    if valor_num is None: return "#999"
    conf = METAS_BASE[metrica]
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']

    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m + tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m - tol else "#dc3545")

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

    col_op  = cols.get('operador',  'Operador')
    col_mat = cols.get('matricula', 'Matricula')

    for m in METAS_BASE.keys():
        # Usa buscar_coluna para encontrar o nome real da coluna com aliases
        origem = buscar_coluna(cols, m)

        if origem:
            if 'TMA' in m:
                df[f'{m}_num'] = df[origem].apply(converter_tma)
            else:
                df[f'{m}_num'] = df[origem].apply(limpar_valor_numerico)

            df[m] = df[origem].astype(str)
        else:
            # Coluna não encontrada: preenche com None para não quebrar o app
            df[f'{m}_num'] = None
            df[m] = '---'

    # ----- PAUSA TOTAL -----
    col_imp  = cols.get('pausa improdutiva')
    col_prod = cols.get('pausa produtiva')

    if col_imp and col_prod:
        df['Pausa Total_num'] = (
            df[col_imp].apply(limpar_valor_numerico).fillna(0)
            + df[col_prod].apply(limpar_valor_numerico).fillna(0)
        )
        df['Pausa Total'] = df['Pausa Total_num'].apply(lambda x: f"{x:.1f}%")

    return df, col_op, col_mat

# ---------- HUB ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    st.markdown("<h1 style='text-align:center;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    if c1.button("SAC NDI", use_container_width=True):
        st.session_state.servico = "SAC NDI"
        st.rerun()

    if c2.button("SAC PPO", use_container_width=True):
        st.session_state.servico = "SAC PPO"
        st.rerun()

    if c3.button("SAC HAPVIDA", use_container_width=True):
        st.session_state.servico = "SAC HAPVIDA"
        st.rerun()

# ---------- DASHBOARD ----------
else:

    with st.sidebar:

        st.markdown(f"### {st.session_state.servico}")

        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]

        elif st.session_state.servico == "SAC PPO":
            lista = ["Selecione...", "Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex"]

        else:
            lista = ["Selecione...", "Equipe Hapvida"]

        supervisor = st.selectbox("Supervisor:", lista)

        if st.button("Voltar"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":

        df, col_op, col_mat = carregar_dados_aba(supervisor)

        # Filtra linhas de totais/cabeçalhos e backoffice
        df_eq = df[
            (~df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA|SUPERVISOR', na=False)) &
            (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))
        ].copy()

        # ---------- MENU SUPERIOR ----------
        st.markdown("### 📊 Painel de Análise")

        if "aba_ativa" not in st.session_state:
            st.session_state.aba_ativa = "Individual"

        c1, c2, c3, c4 = st.columns(4)

        if c1.button("Individual", use_container_width=True):
            st.session_state.aba_ativa = "Individual"
            st.rerun()

        if c2.button("Equipe", use_container_width=True):
            st.session_state.aba_ativa = "Equipe"
            st.rerun()

        if c3.button("Ranking", use_container_width=True):
            st.session_state.aba_ativa = "Ranking"
            st.rerun()

        if c4.button("Saúde", use_container_width=True):
            st.session_state.aba_ativa = "Saúde"
            st.rerun()

        aba = st.session_state.aba_ativa

        st.divider()

        # ---------- INDIVIDUAL ----------
        if aba == "Individual":

            mat = st.text_input("Matrícula")

            if mat:
                res = df[df[col_mat].astype(str) == mat]

                if not res.empty:
                    r = res.iloc[0]

                    st.subheader(r[col_op])

                    c1, c2, c3 = st.columns(3)

                    with c1:
                        exibir_card("Aderência",      r['Aderencia'],   definir_cor_kpi(r['Aderencia_num'],   'Aderencia'))
                        exibir_card("Silêncio",        r['Silencio'],    definir_cor_kpi(r['Silencio_num'],    'Silencio'))

                    with c2:
                        exibir_card("Resolutividade",  r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade'))
                        exibir_card("Pausa Total",     r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total'))

                    with c3:
                        exibir_card("TMA Voz",         r['TMA Voz'],     definir_cor_kpi(r['TMA Voz_num'],    'TMA Voz'))
                        exibir_card("Pesquisa",        r['Pesquisa'],    definir_cor_kpi(r['Pesquisa_num'],   'Pesquisa'))

                else:
                    st.warning("Matrícula não encontrada.")

        # ---------- EQUIPE ----------
        if aba == "Equipe":

            cols_cards = st.columns(len(METAS_BASE))

            for i, (metrica, conf) in enumerate(METAS_BASE.items()):
                # Usa apenas linhas com valor numérico válido para calcular a média
                serie = df_eq[f'{metrica}_num'].dropna()
                media = serie.mean() if not serie.empty else None
                txt = f"{media:.1f}{conf['unidade']}" if media is not None else "---"
                cor = definir_cor_kpi(media, metrica)

                with cols_cards[i]:
                    exibir_card(metrica, txt, cor)

        # ---------- RANKING ----------
        if aba == "Ranking":

            metrica_sel = st.selectbox("Métrica", list(METAS_BASE.keys()))

            top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
                by=f'{metrica_sel}_num',
                ascending=METAS_BASE[metrica_sel]['menor_melhor']
            ).head(5)

            for i, (_, row) in enumerate(top.iterrows()):
                exibir_card(f"{i+1}º {row[col_op]}", row[metrica_sel], "#28a745")

        # ---------- SAÚDE ----------
        if aba == "Saúde":

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
                columns={col_mat: 'Matrícula', 'Valor': metrica_sel}
            )

            st.dataframe(tabela, use_container_width=True)
