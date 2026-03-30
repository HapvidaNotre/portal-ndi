import streamlit as st
import pandas as pd
import time

st.set_page_config(
    page_title="Portal de Performance NDI",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════════════════════════
# CSS GLOBAL — Design System completo
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>

/* ── Reset & Base ─────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.stApp {
    background: #f0f4fb;
    background-image:
        radial-gradient(circle at 15% 20%, rgba(11,42,111,0.06) 0%, transparent 50%),
        radial-gradient(circle at 85% 80%, rgba(26,111,196,0.06) 0%, transparent 50%);
    min-height: 100vh;
}

/* Oculta elementos desnecessários do Streamlit */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── Botões Streamlit padrão (abas do painel) ─────────────── */
div.stButton > button {
    background-color: #0b2a6f;
    color: white;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 600;
    font-size: 14px;
    border-radius: 10px;
    border: none;
    padding: 10px 20px;
    transition: all 0.2s ease;
    letter-spacing: 0.3px;
}
div.stButton > button:hover {
    background-color: #1341a3;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(11,42,111,0.3);
}
div.stButton > button:active {
    transform: translateY(0px);
}

/* ── Cards KPI ────────────────────────────────────────────── */
.metric-card {
    background: white;
    padding: 16px 18px;
    border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
    border-left: 5px solid;
    margin-bottom: 12px;
    transition: box-shadow 0.2s;
}
.metric-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.10);
}

</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# CSS DO HUB — isolado para não vazar nas outras telas
# ══════════════════════════════════════════════════════════════
HUB_CSS = """
<style>

/* ── Wrapper geral do hub ─────────────────────────────────── */
.hub-wrapper {
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 20px 60px 20px;
}

/* ── Header ───────────────────────────────────────────────── */
.hub-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 32px 0 36px 0;
    border-bottom: 1px solid rgba(11,42,111,0.10);
    margin-bottom: 44px;
    flex-wrap: wrap;
    gap: 16px;
}

.hub-header-left { display: flex; align-items: center; gap: 18px; }

.hub-logo-badge {
    width: 56px; height: 56px;
    background: linear-gradient(135deg, #0b2a6f, #1a6fc4);
    border-radius: 16px;
    display: flex; align-items: center; justify-content: center;
    font-size: 26px;
    box-shadow: 0 4px 16px rgba(11,42,111,0.30);
    flex-shrink: 0;
}

.hub-title {
    font-size: 26px;
    font-weight: 800;
    color: #0b2a6f;
    letter-spacing: -0.5px;
    line-height: 1.1;
    margin: 0;
}

.hub-subtitle {
    font-size: 13px;
    color: #7a8fb5;
    font-weight: 500;
    margin: 4px 0 0 0;
    letter-spacing: 0.2px;
}

.hub-badge-env {
    background: rgba(11,42,111,0.07);
    color: #0b2a6f;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}

/* ── Section label ────────────────────────────────────────── */
.hub-section-label {
    font-size: 11px;
    font-weight: 700;
    color: #a0b0cc;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 0 0 16px 0;
}

/* ── Grid de cards ────────────────────────────────────────── */
.hub-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
    margin-bottom: 40px;
}

.hub-grid-2 {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 18px;
    max-width: 680px;
}

/* ── Card base ────────────────────────────────────────────── */
.hub-card {
    background: white;
    border-radius: 18px;
    padding: 26px 24px 22px 24px;
    border: 1.5px solid rgba(11,42,111,0.07);
    cursor: pointer;
    transition: all 0.22s cubic-bezier(0.22, 1, 0.36, 1);
    position: relative;
    overflow: hidden;
    text-decoration: none !important;
}

.hub-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0b2a6f, #1a6fc4);
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.25s ease;
    border-radius: 18px 18px 0 0;
}

.hub-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(11,42,111,0.14);
    border-color: rgba(11,42,111,0.18);
}

.hub-card:hover::before {
    transform: scaleX(1);
}

/* ── Card com destaque (Supervisão) ───────────────────────── */
.hub-card-featured {
    background: linear-gradient(135deg, #0b2a6f 0%, #1341a3 60%, #1a6fc4 100%);
    border-color: transparent;
    color: white;
}

.hub-card-featured::before {
    background: rgba(255,255,255,0.3);
}

.hub-card-featured:hover {
    box-shadow: 0 16px 48px rgba(11,42,111,0.35);
}

/* ── Elementos internos do card ───────────────────────────── */
.card-icon-wrap {
    width: 46px; height: 46px;
    border-radius: 13px;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px;
    margin-bottom: 16px;
    background: rgba(11,42,111,0.07);
    transition: transform 0.2s;
}

.hub-card:hover .card-icon-wrap {
    transform: scale(1.08);
}

.hub-card-featured .card-icon-wrap {
    background: rgba(255,255,255,0.18);
}

.card-title {
    font-size: 15px;
    font-weight: 700;
    color: #0b2a6f;
    margin: 0 0 6px 0;
    letter-spacing: -0.2px;
}

.hub-card-featured .card-title { color: white; }

.card-desc {
    font-size: 12.5px;
    color: #7a8fb5;
    margin: 0 0 18px 0;
    line-height: 1.5;
    font-weight: 400;
}

.hub-card-featured .card-desc { color: rgba(255,255,255,0.72); }

.card-cta {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    font-weight: 700;
    color: #1a6fc4;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}

.hub-card-featured .card-cta { color: rgba(255,255,255,0.85); }

.card-cta-arrow { transition: transform 0.2s; }
.hub-card:hover .card-cta-arrow { transform: translateX(4px); }

/* ── Tag de status no card ────────────────────────────────── */
.card-tag {
    position: absolute;
    top: 16px; right: 16px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
}

.tag-live {
    background: rgba(40,167,69,0.12);
    color: #1a7a3c;
}

.tag-restricted {
    background: rgba(255,153,0,0.13);
    color: #b36a00;
}

/* ── Rodapé do hub ────────────────────────────────────────── */
.hub-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 24px;
    border-top: 1px solid rgba(11,42,111,0.08);
    flex-wrap: wrap;
    gap: 10px;
}

.hub-footer-text {
    font-size: 12px;
    color: #a0b0cc;
    font-weight: 500;
}

.hub-footer-dot {
    width: 7px; height: 7px;
    background: #28a745;
    border-radius: 50%;
    display: inline-block;
    margin-right: 6px;
    box-shadow: 0 0 0 2px rgba(40,167,69,0.2);
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { box-shadow: 0 0 0 2px rgba(40,167,69,0.2); }
    50%       { box-shadow: 0 0 0 5px rgba(40,167,69,0.08); }
}

/* ── Responsividade ───────────────────────────────────────── */
@media (max-width: 900px) {
    .hub-grid { grid-template-columns: repeat(2, 1fr); }
    .hub-grid-2 { grid-template-columns: 1fr; max-width: 100%; }
}
@media (max-width: 600px) {
    .hub-grid { grid-template-columns: 1fr; }
    .hub-title { font-size: 20px; }
}

</style>
"""


# ══════════════════════════════════════════════════════════════
# SPLASH SCREEN
# ══════════════════════════════════════════════════════════════
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(150deg, #061a4f 0%, #0b2a6f 50%, #0d3490 100%) !important; }
    </style>
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                min-height:80vh; text-align:center; padding:40px 20px;">

        <div style="width:80px;height:80px;background:rgba(255,255,255,0.12);border-radius:24px;
                    display:flex;align-items:center;justify-content:center;font-size:40px;
                    margin-bottom:24px;backdrop-filter:blur(10px);
                    box-shadow:0 8px 32px rgba(0,0,0,0.25);">
            📊
        </div>

        <p style="color:rgba(255,255,255,0.5);font-size:11px;letter-spacing:3px;
                  text-transform:uppercase;font-weight:600;margin:0 0 12px 0;">
            HAPVIDA NOTREDAME INTERMÉDICA
        </p>

        <p style="color:white;font-size:32px;font-weight:800;letter-spacing:-0.5px;margin:0 0 8px 0;
                  font-family:'Plus Jakarta Sans',sans-serif;">
            Portal de Performance
        </p>
        <p style="color:rgba(255,255,255,0.4);font-size:14px;font-weight:500;margin:0 0 48px 0;">
            NDI · WFM Operacional
        </p>

    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        barra = st.progress(0)
        for i in range(1, 101):
            time.sleep(0.015)
            barra.progress(i)

    st.session_state.splash_done = True
    st.rerun()


# ══════════════════════════════════════════════════════════════
# METAS & CONFIGURAÇÕES
# ══════════════════════════════════════════════════════════════
METAS_BASE = {
    'Aderencia':      {'valor': 85.0,  'margem': 5.0,  'menor_melhor': False, 'unidade': '%'},
    'Resolutividade': {'valor': 75.0,  'margem': 5.0,  'menor_melhor': False, 'unidade': '%'},
    'TMA Voz':        {'valor': 8.0,   'margem': 1.0,  'menor_melhor': True,  'unidade': ' min'},
    'Pesquisa':       {'valor': 4.5,   'margem': 0.5,  'menor_melhor': False, 'unidade': ''},
    'Silencio':       {'valor': 15.0,  'margem': 5.0,  'menor_melhor': True,  'unidade': '%'},
    'Pausa Total':    {'valor': 21.75, 'margem': 3.0,  'menor_melhor': True,  'unidade': '%'},
}

ALIAS_COLUNAS = {
    'tma voz':        ['tma voz','tma','tma_voz','tempo medio de atendimento','tempo médio de atendimento','tma volumetria voz'],
    'pesquisa':       ['pesquisa','nota pesquisa','nota_pesquisa','nps','nota de pesquisa','nota pesquisa voz'],
    'aderencia':      ['aderencia','aderência','adh','adherencia','aderencia (%)'],
    'resolutividade': ['resolutividade','resolutividade%','resolut'],
    'silencio':       ['silencio','silêncio','silencio%'],
    'pausa total':    ['pausa total','% pausa improdutiva','pausa improdutiva'],
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']


# ══════════════════════════════════════════════════════════════
# FUNÇÕES UTILITÁRIAS
# ══════════════════════════════════════════════════════════════
def buscar_coluna(cols_dict, metrica):
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
            return int(p[0])*60 + int(p[1]) + int(p[2])/60
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
        <p style="margin:0;font-size:10px;color:#7a8fb5;font-weight:700;text-transform:uppercase;
                  letter-spacing:0.8px;">{label}</p>
        <h4 style="margin:6px 0 0 0;color:#0b2a6f;font-weight:800;font-size:20px;">{valor_display}</h4>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════════════════
def _processar_df(df):
    df.columns = df.columns.str.strip()
    cols = {c.lower(): c for c in df.columns}
    col_op  = cols.get('operador',  'Operador')
    col_mat = cols.get('matricula', 'Matricula')

    for m in METAS_BASE.keys():
        origem = buscar_coluna(cols, m)
        if origem:
            if 'TMA' in m:
                df[f'{m}_num'] = df[origem].apply(converter_tma)
            else:
                df[f'{m}_num'] = df[origem].apply(limpar_valor_numerico)
            df[m] = df[origem].astype(str)
        else:
            df[f'{m}_num'] = None
            df[m] = '---'

    col_imp  = cols.get('pausa improdutiva') or cols.get('% pausa improdutiva')
    col_prod = cols.get('pausa produtiva')

    if col_imp and col_prod:
        df['Pausa Total_num'] = (
            df[col_imp].apply(limpar_valor_numerico).fillna(0)
            + df[col_prod].apply(limpar_valor_numerico).fillna(0)
        )
        df['Pausa Total'] = df['Pausa Total_num'].apply(lambda x: f"{x:.1f}%")
    elif col_imp:
        pass  # já processado no loop acima

    return df, col_op, col_mat


def processar_excel_bi(arquivo):
    xl = pd.ExcelFile(arquivo)
    frames = []
    for aba in xl.sheet_names:
        try:
            df_aba = xl.parse(aba, header=0)
            df_aba.columns = df_aba.columns.str.strip()
            cols_lower = {c.lower(): c for c in df_aba.columns}
            if 'operador' in cols_lower or 'matricula' in cols_lower:
                df_aba['_aba'] = aba
                frames.append(df_aba)
        except Exception:
            pass
    if not frames:
        raise ValueError("Nenhuma aba com colunas 'Operador' ou 'Matricula' encontrada.")
    df = pd.concat(frames, ignore_index=True)
    return _processar_df(df)


@st.cache_data(ttl=600)
def carregar_dados_aba(supervisor):
    SHEETS = {
        "Equipe Erik":    "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=0",
        "Equipe Davi":    "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=1",
        "Equipe Elaine":  "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=2",
        "Equipe Sayanne": "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=3",
        "Equipe Beatriz": "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=4",
        "Equipe Aline":   "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=5",
        "Equipe Marcelo": "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=6",
        "Equipe Ellen":   "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=7",
        "Equipe Carla":   "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=8",
        "Equipe Magno":   "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=9",
        "Equipe Alex":    "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=10",
        "Equipe Hapvida": "https://docs.google.com/spreadsheets/d/XXXXXXXXXX/export?format=csv&gid=11",
    }
    url = SHEETS.get(supervisor, "")
    df = pd.read_csv(url)
    return _processar_df(df)


# ══════════════════════════════════════════════════════════════
# PAINEL DE DESEMPENHO (sub-telas)
# ══════════════════════════════════════════════════════════════
def exibir_painel(df, col_op, col_mat, chave_aba="aba_padrao"):
    df_eq = df[~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)].copy()

    cols_low = {c.lower(): c for c in df.columns}
    col_tipo = cols_low.get('tipo') or cols_low.get('tipo de atendimento')

    df_resumo = pd.DataFrame()
    if col_tipo:
        resumo_rows = df[df[col_tipo].astype(str).str.lower().isin(['equipe','media','média','resumo','total'])]
        if not resumo_rows.empty:
            df_resumo = resumo_rows.copy()

    if chave_aba not in st.session_state:
        st.session_state[chave_aba] = "Individual"

    # ── Barra de navegação das abas ──
    st.markdown("""
    <div style="margin-bottom: 6px;">
        <p style="font-size:11px;color:#a0b0cc;font-weight:700;
                  text-transform:uppercase;letter-spacing:1.5px;margin-bottom:12px;">
            Visualização
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("👤 Individual",  use_container_width=True, key=f"btn_ind_{chave_aba}"):
        st.session_state[chave_aba] = "Individual"; st.rerun()
    if c2.button("👥 Equipe",      use_container_width=True, key=f"btn_eq_{chave_aba}"):
        st.session_state[chave_aba] = "Equipe";     st.rerun()
    if c3.button("🏆 Ranking",     use_container_width=True, key=f"btn_rk_{chave_aba}"):
        st.session_state[chave_aba] = "Ranking";    st.rerun()
    if c4.button("🩺 Saúde",       use_container_width=True, key=f"btn_sa_{chave_aba}"):
        st.session_state[chave_aba] = "Saúde";      st.rerun()

    aba = st.session_state[chave_aba]
    st.divider()

    if aba == "Individual":
        mat = st.text_input("🔍 Digite a Matrícula", placeholder="Ex: 1210820")
        if mat:
            res = df[df[col_mat].astype(str) == mat]
            if not res.empty:
                r = res.iloc[0]
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,#0b2a6f,#1a6fc4);
                            border-radius:14px;padding:20px 24px;margin-bottom:20px;color:white;">
                    <p style="margin:0;font-size:11px;opacity:0.65;text-transform:uppercase;
                              letter-spacing:1px;font-weight:600;">Operador</p>
                    <p style="margin:4px 0 0 0;font-size:22px;font-weight:800;">{r[col_op]}</p>
                    <p style="margin:2px 0 0 0;font-size:12px;opacity:0.6;">Matrícula {mat}</p>
                </div>
                """, unsafe_allow_html=True)
                c1, c2, c3 = st.columns(3)
                with c1:
                    exibir_card("Aderência",     r['Aderencia'],      definir_cor_kpi(r['Aderencia_num'],      'Aderencia'))
                    exibir_card("Silêncio",       r['Silencio'],       definir_cor_kpi(r['Silencio_num'],       'Silencio'))
                with c2:
                    exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade'))
                    exibir_card("Pausa Total",    r['Pausa Total'],    definir_cor_kpi(r['Pausa Total_num'],    'Pausa Total'))
                with c3:
                    exibir_card("TMA Voz",        r['TMA Voz'],        definir_cor_kpi(r['TMA Voz_num'],        'TMA Voz'))
                    exibir_card("Pesquisa",       r['Pesquisa'],       definir_cor_kpi(r['Pesquisa_num'],       'Pesquisa'))
            else:
                st.warning("⚠️ Matrícula não encontrada na planilha.")

    if aba == "Equipe":
        cols_cards = st.columns(len(METAS_BASE))
        if not df_resumo.empty:
            linha_oficial = df_resumo.iloc[0]
            for i, (metrica, _) in enumerate(METAS_BASE.items()):
                with cols_cards[i]:
                    exibir_card(metrica, linha_oficial[metrica],
                                definir_cor_kpi(linha_oficial[f'{metrica}_num'], metrica))
        else:
            st.warning("Não foi possível localizar a linha de média/equipe na planilha.")

    if aba == "Ranking":
        metrica_sel = st.selectbox("📊 Métrica", list(METAS_BASE.keys()))
        top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
            by=f'{metrica_sel}_num',
            ascending=METAS_BASE[metrica_sel]['menor_melhor']
        ).head(5)
        medals = ["🥇","🥈","🥉","4º","5º"]
        for i, (_, row) in enumerate(top.iterrows()):
            exibir_card(f"{medals[i]}  {row[col_op]}", row[metrica_sel], "#28a745")

    if aba == "Saúde":
        metrica_sel = st.selectbox("🩺 Selecione a Métrica:", list(METAS_BASE.keys()))
        conf_s = METAS_BASE[metrica_sel]
        df_saude = df_eq.copy()

        def verificar_status(valor):
            if pd.isna(valor): return "Sem dado"
            if conf_s['menor_melhor']:
                return "✅ Meta OK" if valor <= conf_s['valor'] else "❌ Fora da Meta"
            return "✅ Meta OK" if valor >= conf_s['valor'] else "❌ Fora da Meta"

        df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)
        df_saude['Valor']  = df_saude.apply(
            lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---", axis=1
        )
        tabela = df_saude[[col_mat, 'Valor', 'Status']].rename(
            columns={col_mat: 'Matrícula', 'Valor': metrica_sel}
        )
        st.dataframe(tabela, use_container_width=True)


# ══════════════════════════════════════════════════════════════
# HUB — tela inicial
# ══════════════════════════════════════════════════════════════
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    # Injeta CSS do hub
    st.markdown(HUB_CSS, unsafe_allow_html=True)

    # Wrapper
    st.markdown('<div class="hub-wrapper">', unsafe_allow_html=True)

    # ── Header ──────────────────────────────────────────────
    from datetime import datetime
    now = datetime.now().strftime("%d/%m/%Y  %H:%M")

    st.markdown(f"""
    <div class="hub-header">
        <div class="hub-header-left">
            <div class="hub-logo-badge">📊</div>
            <div>
                <p class="hub-title">Portal de Performance NDI</p>
                <p class="hub-subtitle">WFM · Acompanhamento Operacional · Optimus 2026</p>
            </div>
        </div>
        <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
            <span style="font-size:12px;color:#a0b0cc;font-weight:500;">{now}</span>
            <span class="hub-badge-env">Produção</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Seção: Serviços de Atendimento ───────────────────────
    st.markdown('<p class="hub-section-label">Serviços de atendimento</p>', unsafe_allow_html=True)

    # Cards SAC (3 colunas) usando st.columns + HTML clicável via botão hidden
    col1, col2, col3 = st.columns(3)

    CARDS_SAC = [
        {
            "col": col1,
            "key": "SAC NDI",
            "icon": "🏥",
            "title": "SAC NDI",
            "desc": "Serviço de Atendimento ao Cliente — NotreDame Intermédica. Consultas, acompanhamento e suporte.",
            "tag": "live",
            "tag_label": "Ao vivo",
        },
        {
            "col": col2,
            "key": "SAC PPO",
            "icon": "💼",
            "title": "SAC PPO",
            "desc": "Atendimento especializado PPO. Monitoramento de indicadores e desempenho de equipe.",
            "tag": "live",
            "tag_label": "Ao vivo",
        },
        {
            "col": col3,
            "key": "SAC HAPVIDA",
            "icon": "❤️",
            "title": "SAC Hapvida",
            "desc": "Central de atendimento Hapvida. KPIs, aderência e qualidade consolidados.",
            "tag": "live",
            "tag_label": "Ao vivo",
        },
    ]

    for card in CARDS_SAC:
        with card["col"]:
            st.markdown(f"""
            <div class="hub-card">
                <span class="card-tag tag-{card['tag']}">{card['tag_label']}</span>
                <div class="card-icon-wrap">{card['icon']}</div>
                <p class="card-title">{card['title']}</p>
                <p class="card-desc">{card['desc']}</p>
                <span class="card-cta">Acessar <span class="card-cta-arrow">→</span></span>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Acessar {card['key']}", key=f"hub_{card['key']}", use_container_width=True):
                st.session_state.servico = card['key']
                st.rerun()

    # ── Separador ────────────────────────────────────────────
    st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

    # ── Seção: Área restrita ─────────────────────────────────
    st.markdown('<p class="hub-section-label">Área restrita</p>', unsafe_allow_html=True)

    _, col_sup, _ = st.columns([1, 2, 1])

    with col_sup:
        st.markdown("""
        <div class="hub-card hub-card-featured">
            <span class="card-tag tag-restricted" style="background:rgba(255,255,255,0.15);color:rgba(255,255,255,0.8);">
                Restrito
            </span>
            <div class="card-icon-wrap">🛡️</div>
            <p class="card-title">Área da Supervisão</p>
            <p class="card-desc">
                Painel exclusivo para supervisores. Upload de planilhas BI, análise de equipe,
                ranking e saúde de indicadores.
            </p>
            <span class="card-cta">Entrar <span class="card-cta-arrow">→</span></span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar na Área da Supervisão", key="hub_sup", use_container_width=True):
            st.session_state.servico = "Supervisor"
            st.rerun()

    # ── Rodapé ───────────────────────────────────────────────
    st.markdown(f"""
    <div class="hub-footer">
        <span class="hub-footer-text">
            <span class="hub-footer-dot"></span>
            Sistema operacional
        </span>
        <span class="hub-footer-text">
            Hapvida NotreDame Intermédica &nbsp;·&nbsp; WFM Optimus 2026
        </span>
        <span class="hub-footer-text">v2.0</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
# DASHBOARDS  (sub-telas)
# ══════════════════════════════════════════════════════════════
else:

    # ── Botão Voltar elegante ────────────────────────────────
    col_back, col_title = st.columns([1, 8])
    with col_back:
        if st.button("← Voltar", key="voltar_topo"):
            st.session_state.servico = None
            st.rerun()
    with col_title:
        st.markdown(f"""
        <div style="padding:6px 0;">
            <p style="font-size:10px;color:#a0b0cc;text-transform:uppercase;
                      letter-spacing:1.5px;font-weight:700;margin:0;">Portal de Performance NDI</p>
            <p style="font-size:20px;font-weight:800;color:#0b2a6f;margin:2px 0 0 0;">
                {st.session_state.servico}
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ════════════════════════════════════════════════════════
    # ÁREA DA SUPERVISÃO
    # ════════════════════════════════════════════════════════
    if st.session_state.servico == "Supervisor":

        SUPERVISORES = {
            "SAC NDI":     ["Erik","Davi","Elaine","Sayanne","Beatriz","Aline","Marcelo"],
            "SAC PPO":     ["Ellen","Carla","Magno","Alex"],
            "SAC HAPVIDA": ["Hapvida"],
        }

        if 'supervisor_dados' not in st.session_state:
            st.session_state.supervisor_dados = {}

        with st.sidebar:
            st.markdown("### 📋 Área da Supervisão")
            servico_sup = st.selectbox("Serviço:", ["Selecione..."] + list(SUPERVISORES.keys()))
            nomes_disp  = SUPERVISORES.get(servico_sup, []) if servico_sup != "Selecione..." else []
            nome_sup    = st.selectbox("Seu nome:", ["Selecione..."] + nomes_disp)
            if st.button("Voltar ao Hub"):
                st.session_state.servico = None
                st.rerun()

        if servico_sup == "Selecione..." or nome_sup == "Selecione...":
            st.markdown("""
            <div style="text-align:center;padding:80px 0;color:#a0b0cc;">
                <p style="font-size:48px;margin:0;">👈</p>
                <p style="font-size:16px;font-weight:600;color:#0b2a6f;margin:12px 0 6px 0;">
                    Selecione seu serviço e nome
                </p>
                <p style="font-size:13px;">Use a barra lateral para identificar-se e continuar.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            chave = f"{nome_sup}_{servico_sup}"
            dados_salvos = st.session_state.supervisor_dados.get(chave)

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0b2a6f,#1a6fc4);
                        border-radius:14px;padding:20px 24px;margin-bottom:20px;color:white;
                        display:flex;align-items:center;gap:16px;">
                <div style="font-size:32px;">👤</div>
                <div>
                    <p style="margin:0;font-size:11px;opacity:0.65;text-transform:uppercase;
                              letter-spacing:1px;font-weight:600;">Supervisor</p>
                    <p style="margin:2px 0 0 0;font-size:20px;font-weight:800;">{nome_sup}</p>
                    <p style="margin:2px 0 0 0;font-size:12px;opacity:0.6;">{servico_sup}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            arquivo = st.file_uploader(
                "📂 Enviar planilha do BI (.xlsx)",
                type=["xlsx"],
                key=f"upload_{chave}",
                help="Um novo upload substitui os dados congelados."
            )

            if arquivo is not None:
                with st.spinner("Processando planilha..."):
                    try:
                        df_bi, col_op_bi, col_mat_bi = processar_excel_bi(arquivo)
                        st.session_state.supervisor_dados[chave] = {
                            'df': df_bi,
                            'col_op': col_op_bi,
                            'col_mat': col_mat_bi,
                            'arquivo': arquivo.name,
                        }
                        st.success(f"✅ Planilha **{arquivo.name}** carregada com sucesso!")
                        dados_salvos = st.session_state.supervisor_dados[chave]
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")

            if dados_salvos:
                st.caption(f"📌 Dados do arquivo: **{dados_salvos['arquivo']}** — envie novo arquivo para atualizar.")
                st.divider()
                exibir_painel(dados_salvos['df'], dados_salvos['col_op'], dados_salvos['col_mat'], chave_aba=f"aba_{chave}")
            elif arquivo is None:
                st.markdown("""
                <div style="text-align:center;padding:60px 0;color:#a0b0cc;">
                    <p style="font-size:48px;margin:0;">📊</p>
                    <p style="font-size:16px;font-weight:600;color:#0b2a6f;margin:12px 0 6px 0;">
                        Nenhuma planilha carregada
                    </p>
                    <p style="font-size:13px;">Envie o arquivo .xlsx exportado pelo BI para visualizar os dados da sua equipe.</p>
                </div>
                """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════
    # SAC NDI / SAC PPO / SAC HAPVIDA
    # ════════════════════════════════════════════════════════
    else:
        with st.sidebar:
            st.markdown(f"### {st.session_state.servico}")
            if st.session_state.servico == "SAC NDI":
                lista = ["Selecione...","Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]
            elif st.session_state.servico == "SAC PPO":
                lista = ["Selecione...","Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex"]
            else:
                lista = ["Selecione...","Equipe Hapvida"]

            supervisor = st.selectbox("Supervisor:", lista)
            if st.button("Voltar ao Hub"):
                st.session_state.servico = None
                st.rerun()

        if supervisor != "Selecione...":
            df, col_op, col_mat = carregar_dados_aba(supervisor)
            exibir_painel(df, col_op, col_mat)
        else:
            st.markdown("""
            <div style="text-align:center;padding:80px 0;color:#a0b0cc;">
                <p style="font-size:48px;margin:0;">👈</p>
                <p style="font-size:16px;font-weight:600;color:#0b2a6f;margin:12px 0 6px 0;">
                    Selecione o supervisor
                </p>
                <p style="font-size:13px;">Use a barra lateral para escolher a equipe desejada.</p>
            </div>
            """, unsafe_allow_html=True)
