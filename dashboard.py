import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;0,9..40,800&display=swap');

/* ═══════════════════════════════════════
   DESIGN TOKENS
═══════════════════════════════════════ */
:root {
    --navy:        #0a2558;
    --navy-mid:    #0d3080;
    --blue:        #1662b8;
    --blue-lt:     #2f80ed;
    --accent:      #00b8e6;
    --bg:          #eef2f9;
    --bg-2:        #e6ecf8;
    --white:       #ffffff;
    --text-1:      #0c1a38;
    --text-2:      #3d5070;
    --text-3:      #8096b8;
    --border:      #d4dff2;
    --border-hover:#2f80ed;
    --sh-xs: 0 1px 4px rgba(10,37,88,0.06);
    --sh-sm: 0 3px 12px rgba(10,37,88,0.09);
    --sh-md: 0 8px 28px rgba(10,37,88,0.14);
    --sh-lg: 0 20px 56px rgba(10,37,88,0.22);
    --r-sm: 10px;
    --r-md: 16px;
    --r-lg: 22px;
}

/* ═══════════════════════════════════════
   BASE
═══════════════════════════════════════ */
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', system-ui, sans-serif !important;
}
.block-container {
    padding-top: 1.25rem !important;
    max-width: 1080px !important;
}

/* ═══════════════════════════════════════
   HUB — HERO HEADER
═══════════════════════════════════════ */
.hub-hero {
    background: linear-gradient(130deg, #081e4a 0%, #0d2f7c 45%, #1662b8 100%);
    border-radius: var(--r-lg);
    padding: 40px 44px 36px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--sh-lg);
}
.hub-hero::before {
    content: '';
    position: absolute;
    top: -80px; right: -80px;
    width: 320px; height: 320px;
    background: radial-gradient(circle, rgba(0,184,230,0.16) 0%, transparent 68%);
    pointer-events: none;
}
.hub-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: 25%;
    width: 400px; height: 180px;
    background: radial-gradient(ellipse, rgba(255,255,255,0.04) 0%, transparent 60%);
    pointer-events: none;
}
.hero-chip {
    display: inline-flex; align-items: center; gap: 7px;
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    color: rgba(255,255,255,0.78);
    font-size: 10.5px; font-weight: 700;
    letter-spacing: 1.8px; text-transform: uppercase;
    padding: 5px 13px; border-radius: 100px;
    margin-bottom: 20px;
}
.hero-dot {
    width: 7px; height: 7px;
    background: var(--accent); border-radius: 50%;
    box-shadow: 0 0 8px var(--accent);
    animation: blink 2.2s ease-in-out infinite;
}
@keyframes blink { 0%,100%{opacity:1} 55%{opacity:0.3} }

.hero-title {
    color: #fff; font-size: 30px; font-weight: 800;
    line-height: 1.18; margin: 0 0 9px;
    letter-spacing: -0.6px;
}
.hero-title em { font-style:normal; color: var(--accent); }
.hero-sub {
    color: rgba(255,255,255,0.55); font-size: 13.5px;
    font-weight: 400; margin: 0; line-height: 1.5;
}
.hero-stats {
    display: flex; align-items: center; gap: 28px;
    margin-top: 28px; padding-top: 22px;
    border-top: 1px solid rgba(255,255,255,0.10);
}
.hero-stat {
    color: rgba(255,255,255,0.45); font-size: 11.5px; font-weight: 500;
}
.hero-stat strong { color: rgba(255,255,255,0.86); font-weight: 700; }

/* ═══════════════════════════════════════
   HUB — SECTION LABEL
═══════════════════════════════════════ */
.hub-label {
    font-size: 10.5px; font-weight: 800;
    letter-spacing: 2px; text-transform: uppercase;
    color: var(--text-3); margin-bottom: 12px;
    padding-left: 1px;
}

/* ═══════════════════════════════════════
   HUB — CARD TOP (HTML parte de cima)
   O botão st.button é a parte de baixo
═══════════════════════════════════════ */
.ct {
    background: var(--white);
    border: 1.5px solid var(--border);
    border-bottom: none;
    border-radius: var(--r-md) var(--r-md) 0 0;
    padding: 22px 20px 18px;
    transition: border-color 0.18s, background 0.18s;
    position: relative;
}
/* Linha colorida de acento no topo do card — aparece no hover */
.ct::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    border-radius: var(--r-md) var(--r-md) 0 0;
    background: linear-gradient(90deg, var(--navy), var(--blue-lt));
    opacity: 0;
    transition: opacity 0.2s;
}
.ct:hover { border-color: var(--border-hover); }
.ct:hover::before { opacity: 1; }

/* Ícone dentro do card */
.ct-icon {
    width: 42px; height: 42px; border-radius: 11px;
    display: flex; align-items: center; justify-content: center;
    font-size: 19px; margin-bottom: 14px;
    flex-shrink: 0;
}
.ct-title {
    font-size: 14.5px; font-weight: 800; color: var(--text-1);
    margin: 0 0 5px; letter-spacing: -0.2px;
}
.ct-desc {
    font-size: 12px; color: var(--text-3);
    line-height: 1.55; margin: 0;
}
/* Variante escura para Supervisão */
.ct-dark {
    background: linear-gradient(135deg, #081e4a 0%, #0d2f7c 55%, #1662b8 100%);
    border-color: transparent;
}
.ct-dark::before {
    background: linear-gradient(90deg, var(--accent), var(--blue-lt));
}
.ct-dark:hover { border-color: transparent; }
.ct-dark .ct-title { color: #fff; }
.ct-dark .ct-desc  { color: rgba(255,255,255,0.52); }

/* ═══════════════════════════════════════
   BOTÃO COMO PARTE INFERIOR DO CARD
   CSS :has() elimina o gap e conecta
═══════════════════════════════════════ */

/* Zera margem do element-container do card-top */
[data-testid="column"] .element-container:has(.ct) {
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}
/* Puxa o próximo elemento (o botão) para colar */
[data-testid="column"] .element-container:has(.ct) + .element-container {
    margin-top: -2px !important;
}

/* Estiliza o botão como base do card — variante clara (SAC) */
[data-testid="column"] .element-container:has(.ct:not(.ct-dark)) + .element-container .stButton > button {
    background: #f4f8fe !important;
    color: var(--blue) !important;
    border: 1.5px solid var(--border) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-md) var(--r-md) !important;
    height: 46px !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 8px 22px rgba(10,37,88,0.09) !important;
    transition: all 0.18s ease !important;
}
[data-testid="column"] .element-container:has(.ct:not(.ct-dark)) + .element-container .stButton > button:hover {
    background: #e8f0fb !important;
    color: var(--navy) !important;
    border-color: var(--border-hover) !important;
    box-shadow: 0 10px 30px rgba(10,37,88,0.15) !important;
    transform: none !important;
}

/* Estiliza o botão da variante escura (Supervisão) */
[data-testid="column"] .element-container:has(.ct-dark) + .element-container .stButton > button {
    background: rgba(0, 184, 230, 0.12) !important;
    color: var(--accent) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    border-top: none !important;
    border-radius: 0 0 var(--r-md) var(--r-md) !important;
    height: 46px !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3px !important;
    box-shadow: 0 12px 32px rgba(10,37,88,0.26) !important;
    transition: all 0.18s ease !important;
}
[data-testid="column"] .element-container:has(.ct-dark) + .element-container .stButton > button:hover {
    background: rgba(0,184,230,0.2) !important;
    box-shadow: 0 16px 42px rgba(10,37,88,0.34) !important;
    transform: none !important;
}

/* ═══════════════════════════════════════
   BOTÕES INTERNOS (painéis de dados)
═══════════════════════════════════════ */
div.stButton > button {
    background-color: var(--navy);
    color: white;
    height: 50px;
    font-size: 13.5px;
    font-weight: 600;
    border-radius: var(--r-sm);
    border: none;
    transition: all 0.18s ease;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.2px;
}
div.stButton > button:hover {
    background-color: var(--navy-mid);
    box-shadow: var(--sh-md);
    transform: translateY(-1px);
}
div.stButton > button:active { transform: translateY(0); }

/* ═══════════════════════════════════════
   METRIC CARDS (painéis internos)
═══════════════════════════════════════ */
.metric-card {
    background: var(--white);
    padding: 15px 17px;
    border-radius: var(--r-sm);
    box-shadow: var(--sh-xs);
    border-left: 5px solid;
    margin-bottom: 10px;
    transition: box-shadow 0.18s;
}
.metric-card:hover { box-shadow: var(--sh-sm); }

/* ═══════════════════════════════════════
   SIDEBAR
═══════════════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--navy) !important;
}
section[data-testid="stSidebar"] * { color: rgba(255,255,255,0.82) !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.09) !important;
    border: 1px solid rgba(255,255,255,0.16) !important;
    color: white !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.16) !important;
}

/* ═══════════════════════════════════════
   FOOTER HUB
═══════════════════════════════════════ */
.hub-footer {
    margin-top: 44px; padding-bottom: 24px;
    text-align: center;
    color: var(--text-3); font-size: 11px;
    letter-spacing: 0.3px;
}

/* ═══════════════════════════════════════
   SPLASH
═══════════════════════════════════════ */
.splash-container {
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    padding: 80px 0 40px;
}
.splash-title { color: var(--navy); font-size: 26px; font-weight: 800; margin-top: 20px; }
.splash-sub   { color: #888; font-size: 14px; margin-top: 6px; }

/* ═══════════════════════════════════════
   MISC
═══════════════════════════════════════ */
h3 { font-family: 'DM Sans', sans-serif !important; }
.stProgress > div > div { background-color: var(--blue) !important; }

</style>
""", unsafe_allow_html=True)

# ---------- SPLASH SCREEN ----------
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    st.markdown("""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;
                padding: 80px 0 20px 0; text-align:center;">
        <img src="https://raw.githubusercontent.com/HapvidaNotre/portal-ndi/main/logo-hapvida-escudo-2048.png"
             width="160" style="margin-bottom:20px;" />
        <p style="background: linear-gradient(135deg, #0b2a6f, #1a6fc4);
                  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                  font-size:28px; font-weight:900; letter-spacing:1px; margin:0;">
            Portal de Performance NDI
        </p>
        <p style="color:#888; font-size:14px; margin-top:8px;">Carregando...</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        barra = st.progress(0)
        for i in range(1, 101):
            time.sleep(0.02)
            barra.progress(i)

    st.session_state.splash_done = True
    st.rerun()

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
    'tma voz': ['tma voz', 'tma', 'tma_voz', 'tempo medio de atendimento',
                'tempo médio de atendimento', 'tma volumetria voz'],
    'pesquisa': ['pesquisa', 'nota pesquisa', 'nota_pesquisa', 'nps',
                 'nota de pesquisa', 'nota pesquisa voz'],
    'aderencia': ['aderencia', 'aderência', 'adh', 'adherencia', 'aderencia (%)'],
    'resolutividade': ['resolutividade', 'resolutividade%', 'resolut'],
    'silencio': ['silencio', 'silêncio', 'silencio%'],
    'pausa total': ['pausa total', '% pausa improdutiva', 'pausa improdutiva'],
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

# ---------- PROCESSAMENTO COMUM ----------
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
        # BI exporta apenas improdutiva — usa direto como Pausa Total
        df['Pausa Total_num'] = df[col_imp].apply(limpar_valor_numerico)
        df['Pausa Total'] = df['Pausa Total_num'].apply(
            lambda x: f"{x:.1f}%" if x is not None else "---"
        )

    return df, col_op, col_mat

# ---------- CARREGAMENTO (Google Sheets) ----------
@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
    df = pd.read_csv(url)
    return _processar_df(df)

# ---------- CARREGAMENTO (Upload Excel BI) ----------
# Colunas do BI que vêm como frações decimais (0.0–1.0) e precisam virar %
_COLUNAS_FRACAO = {'aderencia (%)', '% pausa improdutiva', 'absenteismo'}

def processar_excel_bi(arquivo):
    df = pd.read_excel(arquivo, dtype=str)
    df.columns = df.columns.str.strip()

    # Converte colunas de fração decimal → porcentagem
    df_num = pd.read_excel(arquivo)
    df_num.columns = df_num.columns.str.strip()
    for col in df_num.columns:
        if col.lower() in _COLUNAS_FRACAO:
            df[col] = (df_num[col] * 100).round(2).astype(str)

    # Se não há "Pausa Produtiva" separada, cria coluna auxiliar zerada
    # para que _processar_df possa somar improdutiva + 0 = total
    cols_lower = {c.lower() for c in df.columns}
    if 'pausa produtiva' not in cols_lower and '% pausa improdutiva' in cols_lower:
        df['Pausa Produtiva'] = '0'

    return _processar_df(df)

# ---------- HELPER: painel de análise ----------
def exibir_painel(df, col_op, col_mat, chave_aba="aba_ativa"):
    df_resumo = df[df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA', na=False)].copy()
    df_eq = df[
        (~df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA|SUPERVISOR', na=False)) &
        (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))
    ].copy()

    st.markdown("### 📊 Painel de Análise")
    if chave_aba not in st.session_state:
        st.session_state[chave_aba] = "Individual"

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("Individual", use_container_width=True, key=f"btn_ind_{chave_aba}"):
        st.session_state[chave_aba] = "Individual"; st.rerun()
    if c2.button("Equipe", use_container_width=True, key=f"btn_eq_{chave_aba}"):
        st.session_state[chave_aba] = "Equipe"; st.rerun()
    if c3.button("Ranking", use_container_width=True, key=f"btn_rk_{chave_aba}"):
        st.session_state[chave_aba] = "Ranking"; st.rerun()
    if c4.button("Saúde", use_container_width=True, key=f"btn_sa_{chave_aba}"):
        st.session_state[chave_aba] = "Saúde"; st.rerun()

    aba = st.session_state[chave_aba]
    st.divider()

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
                    exibir_card("TMA Voz",         r['TMA Voz'],    definir_cor_kpi(r['TMA Voz_num'],     'TMA Voz'))
                    exibir_card("Pesquisa",        r['Pesquisa'],   definir_cor_kpi(r['Pesquisa_num'],    'Pesquisa'))
            else:
                st.warning("Matrícula não encontrada.")

    if aba == "Equipe":
        cols_cards = st.columns(len(METAS_BASE))
        if not df_resumo.empty:
            linha_oficial = df_resumo.iloc[0]
            for i, (metrica, _) in enumerate(METAS_BASE.items()):
                with cols_cards[i]:
                    exibir_card(metrica, linha_oficial[metrica], definir_cor_kpi(linha_oficial[f'{metrica}_num'], metrica))
        else:
            st.warning("Não foi possível localizar a linha de média/equipe na planilha.")

    if aba == "Ranking":
        metrica_sel = st.selectbox("Métrica", list(METAS_BASE.keys()))
        top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
            by=f'{metrica_sel}_num', ascending=METAS_BASE[metrica_sel]['menor_melhor']
        ).head(5)
        for i, (_, row) in enumerate(top.iterrows()):
            exibir_card(f"{i+1}º {row[col_op]}", row[metrica_sel], "#28a745")

    if aba == "Saúde":
        metrica_sel = st.selectbox("Selecione a Métrica:", list(METAS_BASE.keys()))
        conf_s = METAS_BASE[metrica_sel]
        df_saude = df_eq.copy()

        def verificar_status(valor):
            if pd.isna(valor): return "Sem dado"
            if conf_s['menor_melhor']:
                return "Meta OK" if valor <= conf_s['valor'] else "Fora da Meta"
            return "Meta OK" if valor >= conf_s['valor'] else "Fora da Meta"

        df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)
        df_saude['Valor'] = df_saude.apply(
            lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---", axis=1
        )
        tabela = df_saude[[col_mat, 'Valor', 'Status']].rename(
            columns={col_mat: 'Matrícula', 'Valor': metrica_sel}
        )
        st.dataframe(tabela, use_container_width=True)

# ---------- HUB ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    # ── HERO ────────────────────────────────────────────────────
    st.markdown("""
    <div class="hub-hero">
      <div class="hero-chip">
        <span class="hero-dot"></span>
        Hapvida NotreDame Intermédica
      </div>
      <h1 class="hero-title">Portal de Performance <em>NDI</em></h1>
      <p class="hero-sub">
        Monitoramento de KPIs, rankings e saúde operacional das equipes de atendimento.
      </p>
      <div class="hero-stats">
        <span class="hero-stat">📋 <strong>3</strong> serviços ativos</span>
        <span class="hero-stat">🔄 Atualização <strong>a cada 60s</strong></span>
        <span class="hero-stat">📊 <strong>6</strong> métricas monitoradas</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION: SAC ────────────────────────────────────────────
    st.markdown('<p class="hub-label">Central de Atendimento ao Cliente</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3, gap="medium")

    with c1:
        st.markdown("""
        <div class="ct">
          <div class="ct-icon" style="background:#dbeafe;">💙</div>
          <p class="ct-title">SAC NDI</p>
          <p class="ct-desc">
            Consulta individual por matrícula, visão de equipe, ranking e saúde operacional por métrica.
          </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar SAC NDI →", key="btn_ndi", use_container_width=True):
            st.session_state.servico = "SAC NDI"; st.rerun()

    with c2:
        st.markdown("""
        <div class="ct">
          <div class="ct-icon" style="background:#d1fae5;">🩵</div>
          <p class="ct-title">SAC PPO</p>
          <p class="ct-desc">
            Performance e métricas do atendimento PPO. Aderência, TMA, pesquisa, silêncio e pausas.
          </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar SAC PPO →", key="btn_ppo", use_container_width=True):
            st.session_state.servico = "SAC PPO"; st.rerun()

    with c3:
        st.markdown("""
        <div class="ct">
          <div class="ct-icon" style="background:#ede9fe;">💎</div>
          <p class="ct-title">SAC Hapvida</p>
          <p class="ct-desc">
            Painel integrado do SAC Hapvida. Ranking por métrica e mapa de saúde da equipe.
          </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Acessar SAC Hapvida →", key="btn_hap", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"; st.rerun()

    # ── SECTION: SUPERVISÃO ─────────────────────────────────────
    st.markdown('<p class="hub-label" style="margin-top:30px;">Gestão</p>', unsafe_allow_html=True)

    _, c_sup, _ = st.columns([0.3, 2.4, 0.3])
    with c_sup:
        st.markdown("""
        <div class="ct ct-dark">
          <div style="display:flex; align-items:center; gap:18px;">
            <div class="ct-icon" style="background:rgba(255,255,255,0.10);">🎯</div>
            <div>
              <p class="ct-title">Área da Supervisão</p>
              <p class="ct-desc">
                Importe planilhas exportadas pelo BI e analise a performance completa da equipe —
                consulta individual, ranking e saúde operacional.
              </p>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar na Área da Supervisão →", key="btn_sup", use_container_width=True):
            st.session_state.servico = "Supervisor"; st.rerun()

    # ── FOOTER ──────────────────────────────────────────────────
    st.markdown("""
    <div class="hub-footer">
        Portal de Performance NDI &nbsp;·&nbsp; Hapvida NotreDame Intermédica &nbsp;·&nbsp; Uso interno
    </div>
    """, unsafe_allow_html=True)

# ---------- DASHBOARD ----------
else:

    # ══════════════════════════════════════════════════
    # ÁREA DA SUPERVISÃO
    # ══════════════════════════════════════════════════
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

            if st.button("Voltar"):
                st.session_state.servico = None
                st.rerun()

        if servico_sup == "Selecione..." or nome_sup == "Selecione...":
            st.info("👈 Selecione seu serviço e nome na barra lateral para continuar.")
        else:
            chave = f"{nome_sup}_{servico_sup}"
            dados_salvos = st.session_state.supervisor_dados.get(chave)

            st.markdown(f"### 👤 {nome_sup} — {servico_sup}")

            # Upload sempre visível; novo arquivo substitui os dados congelados
            arquivo = st.file_uploader(
                "📂 Enviar planilha do BI (.xlsx)  —  um novo upload substitui os dados atuais",
                type=["xlsx"],
                key=f"upload_{chave}"
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
                st.caption(f"📌 Dados congelados do arquivo: **{dados_salvos['arquivo']}** — faça um novo upload para atualizar.")
                st.divider()
                exibir_painel(dados_salvos['df'], dados_salvos['col_op'], dados_salvos['col_mat'], chave_aba=f"aba_{chave}")
            elif arquivo is None:
                st.markdown("""
                <div style='text-align:center; padding: 60px 0; color:#888;'>
                    <p style='font-size:48px;'>📊</p>
                    <p style='font-size:16px;'>Nenhuma planilha carregada ainda.<br>
                    Envie o arquivo <b>.xlsx</b> exportado pelo BI para visualizar os dados da sua equipe.</p>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    # SAC NDI / SAC PPO / SAC HAPVIDA  (Google Sheets)
    # ══════════════════════════════════════════════════
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
            exibir_painel(df, col_op, col_mat)
