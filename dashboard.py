import streamlit as st
import pandas as pd
import time
from datetime import datetime

st.set_page_config(
    page_title="Portal de Performance NDI",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed",
)

# ---------- CSS HAPVIDA BI LAYOUT ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

* { font-family: 'Nunito', sans-serif !important; box-sizing: border-box; }

/* Remove padding padrão do Streamlit */
.stApp { background-color: #f0f2f5; }
.block-container { padding: 0 !important; max-width: 100% !important; }
header[data-testid="stHeader"] { background: transparent; }
section[data-testid="stSidebar"] { background-color: #0b2a6f; }
section[data-testid="stSidebar"] * { color: white !important; }
section[data-testid="stSidebar"] .stSelectbox label { color: white !important; }

/* ── WRAPPER GERAL ── */
.hapvida-wrapper {
    display: flex;
    min-height: 100vh;
    background: #f0f2f5;
}

/* ── PAINEL ESQUERDO (conteúdo) ── */
.hapvida-left {
    flex: 1 1 auto;
    padding: 36px 40px 36px 40px;
    display: flex;
    flex-direction: column;
}

/* ── PAINEL DIREITO (banner azul) ── */
.hapvida-right {
    width: 340px;
    min-width: 260px;
    background: #1352CC;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 30px;
    gap: 30px;
}

.hapvida-right .slogan {
    color: white;
    font-size: 28px;
    font-weight: 800;
    line-height: 1.25;
    text-align: left;
    align-self: flex-start;
}

/* ── LOGO SVG Hapvida ── */
.hapvida-logo-area {
    display: flex;
    align-items: center;
    gap: 12px;
    align-self: flex-start;
}

/* ── CABEÇALHO ESQUERDO ── */
.hapvida-header {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 28px;
}

.hapvida-header-icon {
    font-size: 38px;
    line-height: 1;
}

.hapvida-title {
    font-size: 26px;
    font-weight: 900;
    color: #0b2a6f;
    line-height: 1.15;
    margin: 0;
}

/* ── GRID DE BOTÕES ── */
.btn-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
    margin-bottom: 24px;
}

.nav-btn {
    background-color: #1352CC;
    color: white !important;
    font-size: 13px;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 14px 8px;
    text-align: center;
    cursor: pointer;
    transition: background 0.2s, transform 0.15s;
    line-height: 1.3;
    min-height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.nav-btn:hover {
    background-color: #0e3fa8;
    transform: scale(1.03);
}

.nav-btn.active {
    background-color: #E8521A !important;
}

/* ── RODAPÉ ── */
.hapvida-footer {
    margin-top: auto;
    font-size: 11px;
    color: #888;
    padding-top: 12px;
}

/* ── STREAMLIT BUTTONS OVERRIDE para a grade ── */
div.stButton > button {
    background-color: #1352CC !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    border-radius: 8px !important;
    border: none !important;
    height: 58px !important;
    width: 100% !important;
    transition: background 0.2s, transform 0.15s !important;
    font-family: 'Nunito', sans-serif !important;
}

div.stButton > button:hover {
    background-color: #0e3fa8 !important;
    transform: scale(1.02) !important;
    border: none !important;
}

div.stButton > button:focus {
    box-shadow: none !important;
    border: none !important;
}

/* Botão HOME (ativo / laranja) */
.btn-home > div.stButton > button {
    background-color: #E8521A !important;
}
.btn-home > div.stButton > button:hover {
    background-color: #c94415 !important;
}

/* Botão VOLTAR (sidebar) */
.btn-voltar > div.stButton > button {
    background-color: rgba(255,255,255,0.15) !important;
    color: white !important;
    height: 40px !important;
    font-size: 13px !important;
    border-radius: 6px !important;
}

/* ── METRIC CARDS ── */
.metric-card {
    background: white;
    padding: 14px 16px;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    border-left: 6px solid;
    margin-bottom: 10px;
}

/* ── PAINEL ANÁLISE ── */
.painel-title {
    font-size: 20px;
    font-weight: 800;
    color: #0b2a6f;
    margin-bottom: 16px;
}

/* ── DIVIDER ── */
.hapvida-divider {
    border: none;
    border-top: 2px solid #e0e4ed;
    margin: 18px 0;
}

/* ── PROGRESS BAR ── */
div[data-testid="stProgress"] > div > div {
    background-color: #1352CC !important;
}

/* ── UPLOAD ── */
div[data-testid="stFileUploader"] label { font-weight: 700; color: #0b2a6f; }

/* ── INFO / WARNING ── */
div[data-testid="stAlert"] { border-radius: 8px; }

/* ── TABS ── */
button[data-baseweb="tab"] {
    font-weight: 700 !important;
    font-family: 'Nunito', sans-serif !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #1352CC !important;
    border-bottom-color: #1352CC !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# SPLASH SCREEN
# ══════════════════════════════════════════════════
if 'splash_done' not in st.session_state:
    st.session_state.splash_done = False

if not st.session_state.splash_done:
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                min-height:80vh;text-align:center;background:#1352CC;
                position:fixed;top:0;left:0;right:0;bottom:0;z-index:9999;">
        <svg width="180" viewBox="0 0 300 180" xmlns="http://www.w3.org/2000/svg" style="margin-bottom:24px;">
          <!-- Flower icon simplified -->
          <ellipse cx="90" cy="70" rx="28" ry="45" fill="#E8521A" transform="rotate(-30,90,70)"/>
          <ellipse cx="90" cy="70" rx="28" ry="45" fill="#F47B20" transform="rotate(30,90,70)"/>
          <ellipse cx="90" cy="70" rx="28" ry="45" fill="#F5A623" transform="rotate(90,90,70)"/>
          <ellipse cx="90" cy="70" rx="28" ry="45" fill="#E8521A" transform="rotate(150,90,70)"/>
          <ellipse cx="90" cy="70" rx="28" ry="45" fill="#D94010" transform="rotate(-90,90,70)"/>
          <circle cx="90" cy="70" r="18" fill="#FFC107"/>
          <!-- hapvida text -->
          <text x="130" y="85" font-family="Nunito,sans-serif" font-weight="900"
                font-size="48" fill="white">hapvida</text>
        </svg>
        <p style="color:rgba(255,255,255,0.7);font-size:15px;margin:0;font-family:Nunito,sans-serif;">
            Portal de Performance NDI — Carregando...
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 2, 1])
    with col_center:
        barra = st.progress(0)
        for i in range(1, 101):
            time.sleep(0.018)
            barra.progress(i)

    st.session_state.splash_done = True
    st.rerun()

# ══════════════════════════════════════════════════
# METAS E CONFIGURAÇÕES
# ══════════════════════════════════════════════════
METAS_BASE = {
    'Aderencia':      {'valor': 85.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Resolutividade': {'valor': 75.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'TMA Voz':        {'valor': 8.0,   'margem': 1.0, 'menor_melhor': True,  'unidade': ' min'},
    'Pesquisa':       {'valor': 4.5,   'margem': 0.5, 'menor_melhor': False, 'unidade': ''},
    'Silencio':       {'valor': 15.0,  'margem': 5.0, 'menor_melhor': True,  'unidade': '%'},
    'Pausa Total':    {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True,  'unidade': '%'},
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

# ══════════════════════════════════════════════════
# FUNÇÕES UTILITÁRIAS
# ══════════════════════════════════════════════════
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
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m+tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m-tol else "#dc3545")

def exibir_card(label, valor_display, cor):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:700;text-transform:uppercase;
                  letter-spacing:.5px;">{label}</p>
        <h4 style="margin:5px 0 0 0;color:#1f3a5f;font-weight:800;font-size:20px;">{valor_display}</h4>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# PROCESSAMENTO DE DADOS
# ══════════════════════════════════════════════════
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
            df[col_imp].apply(limpar_valor_numerico).fillna(0) +
            df[col_prod].apply(limpar_valor_numerico).fillna(0)
        )
        df['Pausa Total'] = df['Pausa Total_num'].apply(lambda x: f"{x:.1f}%")
    elif col_imp:
        df['Pausa Total_num'] = df[col_imp].apply(limpar_valor_numerico)
        df['Pausa Total'] = df['Pausa Total_num'].apply(
            lambda x: f"{x:.1f}%" if x is not None else "---"
        )

    return df, col_op, col_mat

@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
    df = pd.read_csv(url)
    return _processar_df(df)

_COLUNAS_FRACAO = {'aderencia (%)', '% pausa improdutiva', 'absenteismo'}

def processar_excel_bi(arquivo):
    df = pd.read_excel(arquivo, dtype=str)
    df.columns = df.columns.str.strip()
    df_num = pd.read_excel(arquivo)
    df_num.columns = df_num.columns.str.strip()
    for col in df_num.columns:
        if col.lower() in _COLUNAS_FRACAO:
            df[col] = (df_num[col] * 100).round(2).astype(str)
    cols_lower = {c.lower() for c in df.columns}
    if 'pausa produtiva' not in cols_lower and '% pausa improdutiva' in cols_lower:
        df['Pausa Produtiva'] = '0'
    return _processar_df(df)

# ══════════════════════════════════════════════════
# PAINEL DE ANÁLISE
# ══════════════════════════════════════════════════
def exibir_painel(df, col_op, col_mat, chave_aba="aba_ativa"):
    df_resumo = df[df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA', na=False)].copy()
    df_eq = df[
        (~df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA|SUPERVISOR', na=False)) &
        (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))
    ].copy()

    st.markdown('<p class="painel-title">📊 Painel de Análise</p>', unsafe_allow_html=True)

    if chave_aba not in st.session_state:
        st.session_state[chave_aba] = "Individual"

    # Sub-navegação estilo BI
    c1, c2, c3, c4 = st.columns(4)
    abas = ["Individual", "Equipe", "Ranking", "Saúde"]
    cols_abas = [c1, c2, c3, c4]
    for col_aba, nome_aba in zip(cols_abas, abas):
        is_active = st.session_state[chave_aba] == nome_aba
        css_class = "btn-home" if is_active else ""
        with col_aba:
            with st.container():
                if css_class:
                    st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
                if st.button(nome_aba, use_container_width=True, key=f"btn_{nome_aba}_{chave_aba}"):
                    st.session_state[chave_aba] = nome_aba
                    st.rerun()
                if css_class:
                    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<hr class="hapvida-divider">', unsafe_allow_html=True)

    aba = st.session_state[chave_aba]

    if aba == "Individual":
        mat = st.text_input("🔍 Matrícula", placeholder="Digite a matrícula...")
        if mat:
            res = df[df[col_mat].astype(str) == mat]
            if not res.empty:
                r = res.iloc[0]
                st.markdown(f"<h3 style='color:#0b2a6f;font-weight:800;'>👤 {r[col_op]}</h3>", unsafe_allow_html=True)
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
                st.warning("⚠️ Matrícula não encontrada.")

    elif aba == "Equipe":
        cols_cards = st.columns(len(METAS_BASE))
        if not df_resumo.empty:
            linha_oficial = df_resumo.iloc[0]
            for i, (metrica, _) in enumerate(METAS_BASE.items()):
                with cols_cards[i]:
                    exibir_card(metrica, linha_oficial[metrica], definir_cor_kpi(linha_oficial[f'{metrica}_num'], metrica))
        else:
            st.warning("⚠️ Não foi possível localizar a linha de média/equipe na planilha.")

    elif aba == "Ranking":
        metrica_sel = st.selectbox("Métrica", list(METAS_BASE.keys()))
        top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
            by=f'{metrica_sel}_num', ascending=METAS_BASE[metrica_sel]['menor_melhor']
        ).head(5)
        for i, (_, row) in enumerate(top.iterrows()):
            exibir_card(f"🏅 {i+1}º — {row[col_op]}", row[metrica_sel], "#28a745")

    elif aba == "Saúde":
        metrica_sel = st.selectbox("Selecione a Métrica:", list(METAS_BASE.keys()))
        conf_s = METAS_BASE[metrica_sel]
        df_saude = df_eq.copy()

        def verificar_status(valor):
            if pd.isna(valor): return "Sem dado"
            if conf_s['menor_melhor']:
                return "✅ Meta OK" if valor <= conf_s['valor'] else "❌ Fora da Meta"
            return "✅ Meta OK" if valor >= conf_s['valor'] else "❌ Fora da Meta"

        df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)
        df_saude['Valor'] = df_saude.apply(
            lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---", axis=1
        )
        tabela = df_saude[[col_mat, 'Valor', 'Status']].rename(
            columns={col_mat: 'Matrícula', 'Valor': metrica_sel}
        )
        st.dataframe(tabela, use_container_width=True)

# ══════════════════════════════════════════════════
# COMPONENTES DO LAYOUT HAPVIDA
# ══════════════════════════════════════════════════
HAPVIDA_LOGO_SVG = """
<svg width="160" viewBox="0 0 360 80" xmlns="http://www.w3.org/2000/svg">
  <!-- Flower petals -->
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#E8521A" transform="rotate(-35,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#F47B20" transform="rotate(25,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#E8521A" transform="rotate(85,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#D94010" transform="rotate(145,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#F5A623" transform="rotate(-95,38,36)"/>
  <circle cx="38" cy="36" r="10" fill="#FFC107"/>
  <!-- Text -->
  <text x="62" y="50" font-family="Nunito,sans-serif" font-weight="900"
        font-size="34" fill="white">hapvida</text>
</svg>
"""

HAPVIDA_LOGO_SVG_BLUE = """
<svg width="160" viewBox="0 0 360 80" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#E8521A" transform="rotate(-35,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#F47B20" transform="rotate(25,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#E8521A" transform="rotate(85,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#D94010" transform="rotate(145,38,36)"/>
  <ellipse cx="38" cy="36" rx="13" ry="22" fill="#F5A623" transform="rotate(-95,38,36)"/>
  <circle cx="38" cy="36" r="10" fill="#FFC107"/>
  <text x="62" y="50" font-family="Nunito,sans-serif" font-weight="900"
        font-size="34" fill="#0b2a6f">hapvida</text>
</svg>
"""

# ══════════════════════════════════════════════════
# RENDER: CABEÇALHO BI
# ══════════════════════════════════════════════════
def render_header(titulo, subtitulo=""):
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:flex-start;
                background:white; padding:28px 36px 20px 36px;
                border-bottom:3px solid #1352CC; margin-bottom:0;">
        <div>
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="32" rx="6" fill="#1352CC"/>
                  <rect x="6" y="8" width="4" height="16" rx="2" fill="white"/>
                  <rect x="14" y="14" width="4" height="10" rx="2" fill="white"/>
                  <rect x="22" y="10" width="4" height="14" rx="2" fill="white"/>
                  <path d="M8 16 L16 12 L24 8" stroke="#FFC107" stroke-width="2" fill="none" stroke-linecap="round"/>
                </svg>
                <span style="font-size:22px;font-weight:900;color:#0b2a6f;">{titulo}</span>
            </div>
            {f'<p style="color:#555;font-size:14px;margin:0;font-weight:600;">{subtitulo}</p>' if subtitulo else ''}
        </div>
        <div style="text-align:right;">
            {HAPVIDA_LOGO_SVG_BLUE}
            <p style="font-size:10px;color:#aaa;margin:2px 0 0 0;">Última Atualização: {agora}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# HUB PRINCIPAL
# ══════════════════════════════════════════════════
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    # Layout de duas colunas: esquerda (conteúdo) + direita (banner azul)
    col_main, col_banner = st.columns([3, 1])

    with col_main:
        # Cabeçalho
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.markdown(f"""
        <div style="padding:36px 36px 0 36px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
                <svg width="36" height="36" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                  <rect width="32" height="32" rx="6" fill="#1352CC"/>
                  <rect x="6" y="8" width="4" height="16" rx="2" fill="white"/>
                  <rect x="14" y="14" width="4" height="10" rx="2" fill="white"/>
                  <rect x="22" y="10" width="4" height="14" rx="2" fill="white"/>
                  <path d="M8 16 L16 12 L24 8" stroke="#FFC107" stroke-width="2" fill="none" stroke-linecap="round"/>
                </svg>
                <div>
                    <p style="margin:0;font-size:24px;font-weight:900;color:#0b2a6f;line-height:1.1;">
                        Análise e Planejamento
                    </p>
                    <p style="margin:0;font-size:22px;font-weight:900;color:#0b2a6f;line-height:1.1;">
                        Acompanhamento Operacional
                    </p>
                    <p style="margin:0;font-size:20px;font-weight:900;color:#0b2a6f;line-height:1.2;">
                        Portal de Performance NDI
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<div style="padding:20px 36px 12px 36px;">', unsafe_allow_html=True)

        # Grade de botões — linha 1
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown('<div class="btn-home">', unsafe_allow_html=True)
            if st.button("🏠  Home", use_container_width=True, key="hub_home"):
                pass
            st.markdown('</div>', unsafe_allow_html=True)
        with c2:
            if st.button("SAC NDI", use_container_width=True, key="hub_sac_ndi"):
                st.session_state.servico = "SAC NDI"; st.rerun()
        with c3:
            if st.button("SAC PPO", use_container_width=True, key="hub_sac_ppo"):
                st.session_state.servico = "SAC PPO"; st.rerun()
        with c4:
            if st.button("SAC HAPVIDA", use_container_width=True, key="hub_sac_hap"):
                st.session_state.servico = "SAC HAPVIDA"; st.rerun()
        with c5:
            if st.button("Área da Supervisão", use_container_width=True, key="hub_sup"):
                st.session_state.servico = "Supervisor"; st.rerun()

        st.markdown('<hr class="hapvida-divider" style="margin:16px 0;">', unsafe_allow_html=True)

        # Mensagem de boas-vindas centralizada
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;">
            <p style="font-size:48px;margin:0;">📊</p>
            <p style="font-size:18px;font-weight:700;color:#0b2a6f;margin:12px 0 6px 0;">
                Bem-vindo ao Portal de Performance NDI
            </p>
            <p style="font-size:14px;color:#888;margin:0;">
                Selecione um serviço acima para acessar o painel de análise da sua equipe.
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <p style="font-size:11px;color:#aaa;padding:0 36px 20px 36px;margin:0;">
            Última Atualização: {agora}
        </p>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_banner:
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        st.markdown(f"""
        <div style="background:#1352CC;min-height:100vh;padding:60px 30px;
                    display:flex;flex-direction:column;justify-content:center;gap:32px;">
            <p style="color:white;font-size:30px;font-weight:800;line-height:1.2;margin:0;">
                Sua vida<br>pede um plano<br>que cresce junto<br>com você.
            </p>
            {HAPVIDA_LOGO_SVG}
            <p style="color:rgba(255,255,255,0.5);font-size:11px;margin:0;">
                Última Atualização: {agora}
            </p>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# DASHBOARDS
# ══════════════════════════════════════════════════
else:

    # ── ÁREA DA SUPERVISÃO ──────────────────────────
    if st.session_state.servico == "Supervisor":

        SUPERVISORES = {
            "SAC NDI":     ["Erik","Davi","Elaine","Sayanne","Beatriz","Aline","Marcelo"],
            "SAC PPO":     ["Ellen","Carla","Magno","Alex"],
            "SAC HAPVIDA": ["Hapvida"],
        }

        if 'supervisor_dados' not in st.session_state:
            st.session_state.supervisor_dados = {}

        with st.sidebar:
            st.markdown("""
            <div style="padding:20px 0 10px 0;">
                <p style="font-size:16px;font-weight:800;color:white;margin:0;">📋 Área da Supervisão</p>
            </div>
            """, unsafe_allow_html=True)

            servico_sup = st.selectbox("Serviço:", ["Selecione..."] + list(SUPERVISORES.keys()))
            nomes_disp  = SUPERVISORES.get(servico_sup, []) if servico_sup != "Selecione..." else []
            nome_sup    = st.selectbox("Seu nome:", ["Selecione..."] + nomes_disp)

            st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
            if st.button("← Voltar ao Hub", use_container_width=True):
                st.session_state.servico = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        render_header("Análise e Planejamento — Supervisão", "Acompanhamento Operacional · Portal NDI")

        if servico_sup == "Selecione..." or nome_sup == "Selecione...":
            st.markdown("""
            <div style="text-align:center;padding:60px 0;color:#888;">
                <p style="font-size:40px;">👈</p>
                <p style="font-size:15px;">Selecione seu serviço e nome na barra lateral para continuar.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            chave = f"{nome_sup}_{servico_sup}"
            dados_salvos = st.session_state.supervisor_dados.get(chave)

            st.markdown(f"""
            <div style="padding:20px 36px 0 36px;">
                <p style="font-size:18px;font-weight:800;color:#0b2a6f;margin:0;">
                    👤 {nome_sup} — {servico_sup}
                </p>
            </div>
            """, unsafe_allow_html=True)

            with st.container():
                st.markdown('<div style="padding:16px 36px;">', unsafe_allow_html=True)
                arquivo = st.file_uploader(
                    "📂 Enviar planilha do BI (.xlsx) — um novo upload substitui os dados atuais",
                    type=["xlsx"],
                    key=f"upload_{chave}"
                )
                st.markdown('</div>', unsafe_allow_html=True)

            if arquivo is not None:
                with st.spinner("Processando planilha..."):
                    try:
                        df_bi, col_op_bi, col_mat_bi = processar_excel_bi(arquivo)
                        st.session_state.supervisor_dados[chave] = {
                            'df': df_bi, 'col_op': col_op_bi,
                            'col_mat': col_mat_bi, 'arquivo': arquivo.name,
                        }
                        st.success(f"✅ Planilha **{arquivo.name}** carregada com sucesso!")
                        dados_salvos = st.session_state.supervisor_dados[chave]
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")

            if dados_salvos:
                st.caption(f"📌 Dados congelados: **{dados_salvos['arquivo']}** — faça novo upload para atualizar.")
                st.markdown('<hr class="hapvida-divider">', unsafe_allow_html=True)
                with st.container():
                    st.markdown('<div style="padding:0 36px;">', unsafe_allow_html=True)
                    exibir_painel(dados_salvos['df'], dados_salvos['col_op'], dados_salvos['col_mat'], chave_aba=f"aba_{chave}")
                    st.markdown('</div>', unsafe_allow_html=True)
            elif arquivo is None:
                st.markdown("""
                <div style="text-align:center;padding:60px 0;color:#888;">
                    <p style="font-size:48px;">📊</p>
                    <p style="font-size:15px;">Nenhuma planilha carregada ainda.<br>
                    Envie o arquivo <b>.xlsx</b> exportado pelo BI para visualizar os dados da sua equipe.</p>
                </div>
                """, unsafe_allow_html=True)

    # ── SAC NDI / PPO / HAPVIDA ──────────────────────
    else:
        with st.sidebar:
            st.markdown(f"""
            <div style="padding:20px 0 10px 0;">
                <p style="font-size:16px;font-weight:800;color:white;margin:0;">
                    📊 {st.session_state.servico}
                </p>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.servico == "SAC NDI":
                lista = ["Selecione...","Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]
            elif st.session_state.servico == "SAC PPO":
                lista = ["Selecione...","Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex"]
            else:
                lista = ["Selecione...","Equipe Hapvida"]

            supervisor = st.selectbox("Supervisor:", lista)

            st.markdown('<div class="btn-voltar">', unsafe_allow_html=True)
            if st.button("← Voltar ao Hub", use_container_width=True):
                st.session_state.servico = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        render_header(f"Análise e Planejamento — {st.session_state.servico}", "Acompanhamento Operacional · Portal NDI")

        if supervisor != "Selecione...":
            with st.container():
                st.markdown('<div style="padding:0 36px;">', unsafe_allow_html=True)
                df, col_op, col_mat = carregar_dados_aba(supervisor)
                exibir_painel(df, col_op, col_mat)
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 0;color:#888;">
                <p style="font-size:40px;">👈</p>
                <p style="font-size:15px;">Selecione um supervisor na barra lateral para visualizar os dados.</p>
            </div>
            """, unsafe_allow_html=True)
