import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- CSS ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ═══════════════════════════════
   DESIGN TOKENS
═══════════════════════════════ */
:root {
    --navy:       #0b2a6f;
    --navy-mid:   #0f3891;
    --blue:       #1a6fc4;
    --blue-light: #3b8de0;
    --accent:     #00c2ff;
    --bg:         #f0f4fa;
    --bg-card:    #ffffff;
    --text-dark:  #0d1b3e;
    --text-mid:   #4a5c7a;
    --text-muted: #8a9bb5;
    --border:     #dce6f7;
    --shadow-sm:  0 2px 8px rgba(11,42,111,0.07);
    --shadow-md:  0 6px 24px rgba(11,42,111,0.12);
    --shadow-lg:  0 16px 48px rgba(11,42,111,0.18);
    --radius-sm:  10px;
    --radius-md:  16px;
    --radius-lg:  24px;
}

/* ═══════════════════════════════
   BASE
═══════════════════════════════ */
html, body, .stApp {
    background-color: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* Remove padding padrão do Streamlit no topo */
.block-container { padding-top: 1.5rem !important; }

/* ═══════════════════════════════
   HUB — HEADER
═══════════════════════════════ */
.hub-wrapper {
    max-width: 960px;
    margin: 0 auto;
    padding: 0 16px;
}

.hub-header {
    background: linear-gradient(135deg, var(--navy) 0%, #0f3891 55%, #1a6fc4 100%);
    border-radius: var(--radius-lg);
    padding: 44px 48px 40px 48px;
    margin-bottom: 36px;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-lg);
}

.hub-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 280px; height: 280px;
    background: radial-gradient(circle, rgba(0,194,255,0.18) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
}

.hub-header::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 30%;
    width: 360px; height: 200px;
    background: radial-gradient(ellipse, rgba(255,255,255,0.05) 0%, transparent 65%);
    pointer-events: none;
}

.hub-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 5px 12px;
    border-radius: 100px;
    margin-bottom: 18px;
}

.hub-badge-dot {
    width: 6px; height: 6px;
    background: var(--accent);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--accent);
    animation: pulse-dot 2s infinite;
}

@keyframes pulse-dot {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

.hub-title {
    color: #ffffff;
    font-size: 32px;
    font-weight: 700;
    line-height: 1.2;
    margin: 0 0 10px 0;
    letter-spacing: -0.5px;
}

.hub-title span {
    color: var(--accent);
}

.hub-subtitle {
    color: rgba(255,255,255,0.62);
    font-size: 14px;
    font-weight: 400;
    margin: 0;
    letter-spacing: 0.2px;
}

.hub-meta {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-top: 28px;
    padding-top: 24px;
    border-top: 1px solid rgba(255,255,255,0.12);
}

.hub-meta-item {
    display: flex;
    align-items: center;
    gap: 7px;
    color: rgba(255,255,255,0.55);
    font-size: 12px;
    font-weight: 500;
}

.hub-meta-item strong {
    color: rgba(255,255,255,0.88);
    font-weight: 600;
}

/* ═══════════════════════════════
   HUB — SECTION LABEL
═══════════════════════════════ */
.hub-section-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.6px;
    text-transform: uppercase;
    color: var(--text-muted);
    margin-bottom: 14px;
    padding-left: 2px;
}

/* ═══════════════════════════════
   HUB — SERVICE CARDS
═══════════════════════════════ */
.hub-card {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: var(--radius-md);
    padding: 24px 22px 22px 22px;
    cursor: pointer;
    transition: all 0.22s ease;
    position: relative;
    overflow: hidden;
    box-shadow: var(--shadow-sm);
}

.hub-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--navy), var(--blue));
    opacity: 0;
    transition: opacity 0.22s ease;
}

.hub-card:hover {
    border-color: var(--blue-light);
    box-shadow: var(--shadow-md);
    transform: translateY(-3px);
}

.hub-card:hover::before {
    opacity: 1;
}

.hub-card-icon {
    width: 44px; height: 44px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    margin-bottom: 16px;
}

.hub-card-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-dark);
    margin: 0 0 6px 0;
    letter-spacing: -0.2px;
}

.hub-card-desc {
    font-size: 12.5px;
    color: var(--text-muted);
    line-height: 1.5;
    margin: 0 0 18px 0;
}

.hub-card-cta {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-size: 12px;
    font-weight: 600;
    color: var(--blue);
    letter-spacing: 0.2px;
}

/* ═══════════════════════════════
   HUB — SUPERVISOR CARD (destaque)
═══════════════════════════════ */
.hub-card-supervisor {
    background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
    border-color: transparent;
    color: white;
}

.hub-card-supervisor::before {
    background: linear-gradient(90deg, var(--accent), var(--blue-light));
}

.hub-card-supervisor:hover {
    border-color: transparent;
    box-shadow: var(--shadow-lg);
}

.hub-card-supervisor .hub-card-title { color: #ffffff; }
.hub-card-supervisor .hub-card-desc  { color: rgba(255,255,255,0.58); }
.hub-card-supervisor .hub-card-cta   { color: var(--accent); }

.hub-card-supervisor .hub-card-icon {
    background: rgba(255,255,255,0.1);
}

/* ═══════════════════════════════
   HUB — FOOTER
═══════════════════════════════ */
.hub-footer {
    margin-top: 40px;
    text-align: center;
    color: var(--text-muted);
    font-size: 11.5px;
    font-weight: 400;
    letter-spacing: 0.2px;
    padding-bottom: 24px;
}

/* ═══════════════════════════════
   BOTÕES MENU INTERNO
═══════════════════════════════ */
div.stButton > button {
    background-color: var(--navy);
    color: white;
    height: 52px;
    font-size: 14px;
    font-weight: 600;
    border-radius: var(--radius-sm);
    border: none;
    transition: all 0.2s ease;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.2px;
}

div.stButton > button:hover {
    background-color: var(--navy-mid);
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
}

div.stButton > button:active {
    transform: translateY(0);
}

/* ═══════════════════════════════
   METRIC CARDS (painéis internos)
═══════════════════════════════ */
.metric-card {
    background-color: white;
    padding: 16px 18px;
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow-sm);
    border-left: 5px solid;
    margin-bottom: 10px;
    transition: box-shadow 0.2s;
}

.metric-card:hover {
    box-shadow: var(--shadow-md);
}

/* ═══════════════════════════════
   SIDEBAR
═══════════════════════════════ */
section[data-testid="stSidebar"] {
    background: var(--navy) !important;
}

section[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.85) !important;
}

section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stButton > button {
    color: white !important;
}

section[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.1) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.18) !important;
}

/* ═══════════════════════════════
   SPLASH
═══════════════════════════════ */
.splash-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 0 40px 0;
}

.splash-title {
    color: var(--navy);
    font-size: 26px;
    font-weight: 800;
    margin-top: 20px;
    letter-spacing: 1px;
}

.splash-sub {
    color: #888;
    font-size: 14px;
    margin-top: 6px;
}

/* ═══════════════════════════════
   MISC REFINEMENTS
═══════════════════════════════ */
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

    # ── HEADER ──────────────────────────────────────────────
    st.markdown("""
    <div class="hub-wrapper">
      <div class="hub-header">
        <div class="hub-badge">
          <span class="hub-badge-dot"></span>
          Sistema Ativo
        </div>
        <h1 class="hub-title">Portal de Performance <span>NDI</span></h1>
        <p class="hub-subtitle">
          Acompanhe KPIs, rankings e saúde operacional das equipes em tempo real.
        </p>
        <div class="hub-meta">
          <div class="hub-meta-item">🏥 <strong>Hapvida NotreDame Intermédica</strong></div>
          <div class="hub-meta-item">📋 <strong>3</strong> serviços monitorados</div>
          <div class="hub-meta-item">⚡ Atualização a cada 60s</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── CARDS SAC ────────────────────────────────────────────
    st.markdown('<p class="hub-section-label">Central de Atendimento ao Cliente</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        st.markdown("""
        <div class="hub-card">
          <div class="hub-card-icon" style="background:#e8f0fc;">💙</div>
          <p class="hub-card-title">SAC NDI</p>
          <p class="hub-card-desc">Indicadores e ranking da equipe de atendimento NDI. Consulta individual e visão de equipe.</p>
          <span class="hub-card-cta">Acessar → </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar no SAC NDI", key="btn_ndi", use_container_width=True):
            st.session_state.servico = "SAC NDI"
            st.rerun()

    with col2:
        st.markdown("""
        <div class="hub-card">
          <div class="hub-card-icon" style="background:#eaf4fe;">🩵</div>
          <p class="hub-card-title">SAC PPO</p>
          <p class="hub-card-desc">Performance e métricas do atendimento PPO. Aderência, TMA, pesquisa e mais.</p>
          <span class="hub-card-cta">Acessar → </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar no SAC PPO", key="btn_ppo", use_container_width=True):
            st.session_state.servico = "SAC PPO"
            st.rerun()

    with col3:
        st.markdown("""
        <div class="hub-card">
          <div class="hub-card-icon" style="background:#e6f7ff;">💎</div>
          <p class="hub-card-title">SAC Hapvida</p>
          <p class="hub-card-desc">Painel integrado com os dados do SAC Hapvida. Saúde da equipe e ranking por métrica.</p>
          <span class="hub-card-cta">Acessar → </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar no SAC Hapvida", key="btn_hap", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

    # ── CARD SUPERVISÃO ──────────────────────────────────────
    st.markdown('<p class="hub-section-label" style="margin-top:28px;">Gestão</p>', unsafe_allow_html=True)

    _, col_sup, _ = st.columns([0.5, 2, 0.5])
    with col_sup:
        st.markdown("""
        <div class="hub-card hub-card-supervisor">
          <div style="display:flex; align-items:center; gap:14px; margin-bottom:14px;">
            <div class="hub-card-icon">🎯</div>
            <div>
              <p class="hub-card-title">Área da Supervisão</p>
              <p class="hub-card-desc" style="margin:0;">
                Importe planilhas do BI e analise a performance completa da sua equipe — individual, ranking e saúde operacional.
              </p>
            </div>
          </div>
          <span class="hub-card-cta">Acessar painel gerencial → </span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Entrar na Área da Supervisão", key="btn_sup", use_container_width=True):
            st.session_state.servico = "Supervisor"
            st.rerun()

    # ── FOOTER ────────────────────────────────────────────────
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
