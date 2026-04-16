import streamlit as st
import pandas as pd
import time
import hashlib
from supabase import create_client, Client

st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# ---------- CSS ----------
st.markdown("""
<style>

/* FUNDO GERAL */
.stApp { background-color: #f8f9fa; }

/* INPUTS GLOBAIS — estrutura neutra (sem forçar cores escuras fora da área do gestor) */
div[data-testid="stTextInput"] {
    margin-bottom: 6px !important;
}
div[data-testid="stTextInput"] > div {
    border-radius: 14px !important;
    transition: all 0.25s ease !important;
    overflow: hidden !important;
}
div[data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    font-size: 15px !important;
    font-weight: 500 !important;
    height: 52px !important;
    line-height: 52px !important;
    padding: 0 18px !important;
    vertical-align: middle !important;
    letter-spacing: 0.3px !important;
    outline: none !important;
}
div[data-testid="stTextInput"] label,
div[data-testid="stTextInput"] label p {
    font-size: 10px !important;
    font-weight: 800 !important;
    letter-spacing: 2.5px !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}
/* Remove tooltip "Press Enter to apply" — global */
div[data-testid="InputInstructions"] {
    display: none !important;
}



/* Oculta barra preta padrão do Streamlit */
[data-testid="stToolbar"],
header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
    min-height: 0 !important;
}

/* Oculta a sidebar e o botão de recolher/expandir — navegação feita no conteúdo principal */
[data-testid="stSidebar"],
[data-testid="collapsedControl"] {
    display: none !important;
}

/* Remove espaço reservado pelo header mesmo quando oculto */
.stApp > header { display: none !important; height: 0 !important; }
[data-testid="stAppViewContainer"] { padding-top: 0 !important; margin-top: 0 !important; }
[data-testid="stMain"] { padding-top: 0 !important; margin-top: 0 !important; }
.stMainBlockContainer { padding-top: 0 !important; margin-top: 0 !important; }
.block-container { padding-top: 0rem !important; }

/* Oculta menu hamburguer e botão de deploy */
#MainMenu { visibility: hidden !important; }
.stDeployButton { display: none !important; }
footer { visibility: hidden !important; }

/* Oculta ícones do canto inferior direito (watermark Streamlit) */
[data-testid="stStatusWidget"] { display: none !important; }
.__web-inspector-hide-shortcut__,
[data-testid="manage-app-button"],
.viewerBadge_container__r5tak,
.viewerBadge_link__qRIco,
span.css-1lsmgbg,
#stDecoration { display: none !important; }
div[class*="viewerBadge"] { display: none !important; }
div[class*="watermark"] { display: none !important; }

/* Badge "Hosted with Streamlit" */
div[data-testid="stAppViewBlockContainer"] ~ div { display: none !important; }
a[href*="streamlit.io"] { display: none !important; }
[class*="badge"] { display: none !important; }
[class*="Badge"] { display: none !important; }
[class*="hostBadge"] { display: none !important; }
[class*="HostBadge"] { display: none !important; }

/* Remove espaço vazio no topo */
.stApp > div:first-child { margin-top: 0 !important; }
section.main > div.block-container {
    padding-top: 0 !important;
    margin-top: 0 !important;
}

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

/* ALERTAS — garante texto legivel independente do tema */
[data-testid="stAlert"] p,
[data-testid="stAlert"] div,
[data-testid="stAlert"] span,
.stAlert p, .stAlert div {
    color: #1a1a1a !important;
}

/* SPLASH */
.splash-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 0 40px 0;
}

.splash-title {
    color: #0b2a6f;
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

# ---------- SUPABASE ----------
@st.cache_resource
def conectar_supabase() -> Client:
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

# ---------- METAS ----------
METAS_BASE = {
    'Aderencia':     {'valor': 85.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Resolutividade':{'valor': 75.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'TMA Voz':       {'valor': 8.0,   'margem': 1.0, 'menor_melhor': True,  'unidade': ' min'},
    'Pesquisa':      {'valor': 4.5,   'margem': 0.5, 'menor_melhor': False, 'unidade': ''},
    'Silencio':      {'valor': 15.0,  'margem': 5.0, 'menor_melhor': True,  'unidade': '%'},
    'Pausa Total':   {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True,  'unidade': '%'},
    'Absenteismo':   {'valor': 5.0,   'margem': 1.0, 'menor_melhor': True,  'unidade': '%'},
    'Produtividade': {'valor': 80.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Transf':        {'valor': 85.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'ShortCall':     {'valor': 5.0,   'margem': 1.0, 'menor_melhor': True,  'unidade': '%'},
    'FCR':           {'valor': 80.0,  'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Direcionado':   {'valor': 20.0,  'margem': 5.0, 'menor_melhor': True,  'unidade': '%'},
    'Rechamada':     {'valor': 15.0,  'margem': 3.0, 'menor_melhor': True,  'unidade': '%'},
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# Mapeamento coluna Excel (lowercase) → coluna no Supabase
_MAP_COLUNAS_BI = {
    'operador':            'operador',
    'matricula':           'matricula',
    # Aderência
    'aderencia':           'aderencia',
    'aderencia (%)':       'aderencia',
    '(%) aderencia':       'aderencia',
    # Absenteísmo
    'absenteismo':         'absenteismo',
    '(%) absenteismo':     'absenteismo',
    # Produtividade
    'produtividade':       'produtividade',
    '(%) produtividade':   'produtividade',
    # Transf
    'transf':              'transf',
    '(%) transf':          'transf',
    # TMA Voz
    'tma voz':             'tma_voz',
    # ShortCall
    'shortcall':           'shortcall',
    '(%) shortcall':       'shortcall',
    # Silêncio
    'silencio':            'silencio',
    'silêncio':            'silencio',
    'silencio (%)':        'silencio',
    'silêncio (%)':        'silencio',
    # Pesquisa
    'pesquisa':            'pesquisa',
    # Resolutividade
    'resolutividade':      'resolutividade',
    '(%) resolutividade':  'resolutividade',
    # FCR
    'fcr':                 'fcr',
    '% fcr (1° contato)':  'fcr',
    '% fcr (1 contato)':   'fcr',
    '% fcr':               'fcr',
    # Direcionado
    'direcionado':         'direcionado',
    '% direcionado':       'direcionado',
    '% direcionadas':      'direcionado',
    'direcionadas':        'direcionado',
    # Pausas — colunas de % têm prioridade sobre colunas de tempo (HH:MM:SS)
    '% pausa produtiva':   'pausa_produtiva',
    'pausa produtiva':     'pausa_produtiva',
    'pausas produtivas':   'pausa_produtiva',
    '% pausa improdutiva': 'pausa_improdutiva',
    'pausa improdutiva':   'pausa_improdutiva',
    'pausas improdutivas': 'pausa_improdutiva',
    'pausa total':         'pausa_total',
}

# ---------- METAS — Supabase CRUD ----------
@st.cache_data(ttl=300)
def carregar_metas_gestor(supervisor: str, servico: str) -> dict:
    """Carrega metas customizadas do gestor. Retorna METAS_BASE se não houver nenhuma salva."""
    try:
        supabase = conectar_supabase()
        res = (
            supabase.table("gestores_metas")
            .select("metas_json")
            .eq("supervisor", supervisor)
            .eq("servico", servico)
            .limit(1)
            .execute()
        )
        if res.data and res.data[0].get("metas_json"):
            metas_salvas = res.data[0]["metas_json"]
            # Mescla com METAS_BASE para garantir que menor_melhor e unidade sempre existam
            metas = {}
            for k, v_base in METAS_BASE.items():
                if k in metas_salvas:
                    metas[k] = {**v_base, **metas_salvas[k]}
                else:
                    metas[k] = v_base.copy()
            return metas
    except Exception:
        pass
    return {k: v.copy() for k, v in METAS_BASE.items()}

def salvar_metas_gestor(supervisor: str, servico: str, metas_dict: dict) -> bool:
    """Salva (upsert) metas customizadas do gestor no Supabase."""
    try:
        supabase = conectar_supabase()
        # Serializa apenas valor e margem (menor_melhor e unidade vêm do METAS_BASE)
        metas_json = {k: {"valor": v["valor"], "margem": v["margem"]} for k, v in metas_dict.items()}
        supabase.table("gestores_metas").upsert(
            {"supervisor": supervisor, "servico": servico, "metas_json": metas_json},
            on_conflict="supervisor,servico"
        ).execute()
        carregar_metas_gestor.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar metas: {e}")
        return False

# ---------- FUNÇÕES UTILITÁRIAS ----------
def definir_cor_kpi(valor_num, metrica, metas=None):
    if valor_num is None or pd.isna(valor_num): return "#999"
    conf = (metas or METAS_BASE).get(metrica, METAS_BASE.get(metrica, {}))
    if not conf: return "#999"
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']
    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m + tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m - tol else "#dc3545")

def exibir_card(label, valor_display, cor, tendencia=None):
    cor_bg = {
        "#28a745": "rgba(40,167,69,0.08)",
        "#ffc107": "rgba(255,193,7,0.10)",
        "#dc3545": "rgba(220,53,69,0.08)",
        "#999":    "rgba(150,150,150,0.07)",
    }.get(cor, "rgba(150,150,150,0.07)")

    if tendencia == 'good':
        tend_html = '<span style="font-size:11px; color:#28a745; font-weight:700;">▲ subindo</span>'
    elif tendencia == 'bad':
        tend_html = '<span style="font-size:11px; color:#dc3545; font-weight:700;">▼ caindo</span>'
    elif tendencia == 'stable':
        tend_html = '<span style="font-size:11px; color:#aaa; font-weight:600;">● estável</span>'
    else:
        tend_html = ''

    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 14px;
        padding: 16px 14px 14px 14px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        border-top: 4px solid {cor};
        text-align: center;
        min-height: 90px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
    ">
        <p style="margin:0; font-size:10px; color:#888; font-weight:700;
                  text-transform:uppercase; letter-spacing:0.8px; line-height:1.3;">{label}</p>
        <p style="margin:0; font-size:22px; font-weight:900; color:#0b2a6f; line-height:1.1;">{valor_display}</p>
        {tend_html}
    </div>
    """, unsafe_allow_html=True)

def exibir_card_ranking(pos, nome, valor, cor):
    icone = ["🥇","🥈","🥉","4º","5º"][pos] if pos < 3 else f"{pos+1}º"
    st.markdown(f"""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
        border-left: 5px solid {cor};
        display: flex;
        align-items: center;
        gap: 14px;
    ">
        <span style="font-size:22px; min-width:30px;">{icone}</span>
        <div style="flex:1;">
            <p style="margin:0; font-size:13px; font-weight:700; color:#1f3a5f;">{nome}</p>
        </div>
        <p style="margin:0; font-size:18px; font-weight:900; color:{cor};">{valor}</p>
    </div>
    """, unsafe_allow_html=True)

def _limpar_num(val):
    try:
        return float(str(val).replace('%','').replace(',','.').strip())
    except:
        return None

def _limpar_matricula(val):
    s = str(val).strip()
    # float-like string → remove .0
    if '.' in s:
        partes = s.split('.')
        if partes[1].strip('0') == '':
            s = partes[0]
    return s if s not in ('', 'nan', 'None', 'nan.0') else None

def _converter_tma(val):
    try:
        partes = str(val).strip().split(':')
        if len(partes) == 3:
            return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        return _limpar_num(val)
    except:
        return None

# ---------- UPSERT SUPABASE ----------
# Colunas do BI que vêm como frações decimais (0.0–1.0) e precisam virar %
_COLUNAS_FRACAO = {
    'aderencia (%)', '(%) aderencia',
    '% pausa improdutiva', '(%) pausa improdutiva', 'pausas improdutivas',
    '% pausa produtiva', '(%) pausa produtiva', 'pausas produtivas',
    'absenteismo', '(%) absenteismo',
    'produtividade', '(%) produtividade',
    'transf', '(%) transf',
    'shortcall', '(%) shortcall',
    'silencio', 'silêncio', 'silencio (%)', 'silêncio (%)',
    'resolutividade', '(%) resolutividade',
    'fcr', '% fcr (1° contato)', '% fcr (1 contato)', '% fcr',
    'direcionado', '% direcionado', '% direcionadas', 'direcionadas',
}

def upsert_supabase(df_raw: pd.DataFrame, supervisor: str, servico: str) -> bool:
    """Processa o Excel bruto e faz upsert no Supabase por matrícula+supervisor+serviço."""
    supabase = conectar_supabase()

    df_raw = df_raw.copy()
    df_raw.columns = df_raw.columns.str.strip()

    # Converte colunas de fração decimal → porcentagem
    df_num = df_raw.copy()
    for col in df_num.columns:
        if col.lower() in _COLUNAS_FRACAO:
            try:
                df_raw[col] = (pd.to_numeric(df_num[col], errors='coerce') * 100).round(2).astype(str)
            except:
                pass

    cols_lower = {c.lower(): c for c in df_raw.columns}
    registros = []

    for _, row in df_raw.iterrows():
        rec = {'supervisor': supervisor, 'servico': servico}

        for col_excel, col_db in _MAP_COLUNAS_BI.items():
            col_real = cols_lower.get(col_excel)
            if col_real and col_db not in rec:
                val = row[col_real]
                if col_db == 'tma_voz':
                    rec[col_db] = _converter_tma(val)
                elif col_db == 'matricula':
                    rec[col_db] = _limpar_matricula(val)
                elif col_db in ('operador',):
                    rec[col_db] = str(val).strip() if not pd.isna(val) else None
                else:
                    rec[col_db] = _limpar_num(val)

        # Recalcula pausa total
        prod   = rec.get('pausa_produtiva')   or 0
        improd = rec.get('pausa_improdutiva') or 0
        rec['pausa_total'] = round((prod or 0) + (improd or 0), 2)

        rec['atualizado_em'] = pd.Timestamp.now(tz='UTC').isoformat()

        mat      = rec.get('matricula')
        operador = rec.get('operador') or ''
        is_total = any(t in operador.upper() for t in ('TOTAL','EQUIPE','MÉDIA','MEDIA'))

        if is_total:
            # Guarda a linha de totais com matrícula especial para uso na aba Equipe
            rec['matricula'] = '__TOTAL__'
            registros.append(rec)
        elif mat and str(mat).strip() not in ('', 'nan', 'None'):
            registros.append(rec)

    if not registros:
        st.warning("Nenhum registro válido encontrado no arquivo.")
        return False

    # Sanitiza NaN/inf → None para evitar erro JSON do Supabase
    import math
    def _sanitize(v):
        if v is None:
            return None
        try:
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return None
        except Exception:
            pass
        return v

    registros_limpos = [
        {k: _sanitize(v) for k, v in rec.items()}
        for rec in registros
    ]

    # Deduplica pelo conflict key — evita erro 'ON CONFLICT DO UPDATE command cannot affect row a second time'
    seen = {}
    for rec in registros_limpos:
        key = (rec.get('matricula'), rec.get('supervisor'), rec.get('servico'))
        seen[key] = rec
    registros_limpos = list(seen.values())

    supabase.table("performance_operadores").upsert(
        registros_limpos,
        on_conflict="matricula,supervisor,servico"
    ).execute()

    # ── Histórico: limpa meses anteriores e insere snapshot atual ──
    try:
        from datetime import datetime, timezone
        mes_atual = datetime.now(timezone.utc).strftime('%Y-%m-01')

        # Remove registros de meses anteriores para este supervisor/serviço
        supabase.table("performance_historico") \
            .delete() \
            .eq("supervisor", supervisor) \
            .eq("servico", servico) \
            .lt("upload_date", mes_atual) \
            .execute()

        # Monta registros só com colunas numéricas para o histórico
        _COLS_HIST = ['supervisor','servico','matricula','operador',
                      'aderencia','resolutividade','tma_voz','pesquisa','silencio',
                      'absenteismo','produtividade','transf','shortcall',
                      'pausa_produtiva','pausa_improdutiva','pausa_total',
                      'fcr','direcionado']
        upload_ts  = pd.Timestamp.now(tz='UTC').isoformat()
        hist_recs  = []
        for rec in registros_limpos:
            if rec.get('matricula') == '__TOTAL__':
                continue
            h = {k: rec.get(k) for k in _COLS_HIST}
            h['upload_date'] = upload_ts
            hist_recs.append(h)

        if hist_recs:
            supabase.table("performance_historico").insert(hist_recs).execute()
    except Exception:
        pass  # Histórico não bloqueia o upload principal

    return True

# ---------- UPSERT FCR/DIRECIONADO ----------
def upsert_supabase_fcr(df_raw: pd.DataFrame, supervisor: str, servico: str) -> bool:
    """Lê arquivo de FCR e atualiza colunas fcr e direcionado no Supabase.
    
    O cruzamento é feito pelo NOME do operador, pois o 'Login Operador' do FCR
    é um identificador diferente da Matrícula do BI.
    """
    supabase = conectar_supabase()

    df_raw = df_raw.copy()
    df_raw.columns = [str(c).strip() for c in df_raw.columns]

    # Detecta linhas de metadados antes do cabeçalho real
    # (ex.: planilhas que têm "DATA - Ano  2026  2026..." na primeira linha)
    real_header_idx = None
    for i in range(min(5, len(df_raw))):
        row_vals = [str(v).lower().strip() for v in df_raw.iloc[i].values]
        if any('nome' in v or 'login' in v or 'matric' in v for v in row_vals):
            real_header_idx = i
            break

    if real_header_idx is not None:
        df_raw.columns = [str(v).strip() for v in df_raw.iloc[real_header_idx].values]
        df_raw = df_raw.iloc[real_header_idx + 1:].reset_index(drop=True)

    # Detecção flexível de colunas
    nome_col = fcr_col = dir_col = None
    for col in df_raw.columns:
        cl = str(col).lower().strip()
        if 'nome' in cl and 'operador' in cl:
            nome_col = col
        if cl.startswith('% fcr') or '% fcr' in cl:
            fcr_col = col
        if '% direcionad' in cl:
            dir_col = col

    if not nome_col or not fcr_col:
        st.error(
            "Colunas obrigatórias não encontradas no arquivo FCR. "
            "Verifique se contém 'Nome Operador' e '% FCR (1° Contato)'."
        )
        return False

    # Busca os registros já salvos no Supabase para montar mapa Nome → Matrícula
    # (A planilha do BI deve ser enviada antes do FCR)
    res = (
        supabase.table("performance_operadores")
        .select("matricula,operador")
        .eq("supervisor", supervisor)
        .eq("servico", servico)
        .execute()
    )

    def _norm_nome(s):
        return str(s).upper().strip()

    nome_to_mat = {}
    if res.data:
        for r in res.data:
            if r.get('operador') and r.get('matricula'):
                nome_to_mat[_norm_nome(r['operador'])] = r['matricula']

    if not nome_to_mat:
        st.error(
            "⚠️ Nenhum dado do BI encontrado para esta equipe. "
            "Envie a planilha de **Métricas Gerais** antes de enviar o FCR."
        )
        return False

    registros = []
    nao_encontrados = []
    import math as _math

    for _, row in df_raw.iterrows():
        nome = _norm_nome(row.get(nome_col, ''))
        if not nome or nome in ('', 'NAN', 'NONE', 'TOTAL'):
            continue

        mat = nome_to_mat.get(nome)
        if not mat:
            nao_encontrados.append(nome)
            continue

        fcr_val = _limpar_num(row.get(fcr_col))
        if fcr_val is not None:
            if not (_math.isnan(fcr_val) or _math.isinf(fcr_val)):
                if fcr_val <= 1.0:
                    fcr_val = round(fcr_val * 100, 2)
            else:
                fcr_val = None

        rec = {
            'matricula':     mat,
            'supervisor':    supervisor,
            'servico':       servico,
            'fcr':           fcr_val,
            'atualizado_em': pd.Timestamp.now(tz='UTC').isoformat(),
        }

        if dir_col:
            dir_val = _limpar_num(row.get(dir_col))
            if dir_val is not None:
                if not (_math.isnan(dir_val) or _math.isinf(dir_val)):
                    if dir_val <= 1.0:
                        dir_val = round(dir_val * 100, 2)
                else:
                    dir_val = None
            rec['direcionado'] = dir_val

        registros.append(rec)

    if nao_encontrados:
        st.warning(
            f"⚠️ {len(nao_encontrados)} operador(es) do FCR não encontrado(s) na planilha do BI: "
            f"{', '.join(nao_encontrados[:5])}{'...' if len(nao_encontrados) > 5 else ''}"
        )

    if not registros:
        st.warning("Nenhum registro FCR pôde ser vinculado. Verifique se a planilha do BI foi enviada primeiro.")
        return False

    # Deduplica
    seen = {}
    for rec in registros:
        key = (rec.get('matricula'), rec.get('supervisor'), rec.get('servico'))
        seen[key] = rec
    registros = list(seen.values())

    supabase.table("performance_operadores").upsert(
        registros,
        on_conflict="matricula,supervisor,servico"
    ).execute()

    carregar_dados_supervisor.clear()
    return True


# ---------- UPSERT RECHAMADA ----------
def upsert_supabase_rechamada(df_raw: pd.DataFrame, supervisor: str, servico: str) -> bool:
    """Lê arquivo de Rechamada e atualiza coluna rechamada no Supabase.
    O cruzamento é feito pelo NOME do agente (coluna 'Agente'), pois não há matrícula.
    """
    supabase = conectar_supabase()

    df_raw = df_raw.copy()
    df_raw.columns = [str(c).strip() for c in df_raw.columns]

    # Detecta linha de metadados antes do cabeçalho real.
    # IMPORTANTE: a verificação é RESTRITA — só reprocessa se a linha for exclusivamente
    # composta por palavras-chave de cabeçalho, evitando falso positivo com linhas de
    # filtros exportados (ex.: "Chamadas Atendidas Agente não está em branco...")
    real_header_idx = None
    _HEADER_KEYWORDS = ('agente', 'nome operador', 'operador', 'nome', 'matricula')
    for i in range(min(5, len(df_raw))):
        row_vals = [str(v).lower().strip() for v in df_raw.iloc[i].values if str(v).strip() not in ('', 'nan', 'None')]
        # Só reprocessa se pelo menos uma célula for EXATAMENTE uma palavra-chave de cabeçalho
        # (e não um texto longo contendo essas palavras)
        if any(v in _HEADER_KEYWORDS for v in row_vals):
            real_header_idx = i
            break

    if real_header_idx is not None:
        df_raw.columns = [str(v).strip() for v in df_raw.iloc[real_header_idx].values]
        df_raw = df_raw.iloc[real_header_idx + 1:].reset_index(drop=True)

    # ── Detecção de colunas com PRIORIDADE POR NOME EXATO ──────────────────────
    # Nomes exatos conhecidos para a coluna de agente
    _AGENTE_EXATOS = {'agente', 'nome operador', 'operador', 'nome'}
    # Nomes exatos conhecidos para a coluna de rechamada (%)
    _RECHAMADA_EXATOS = {'(%) rechamada', '% rechamada', 'rechamada (%)', '% de rechamada'}

    agente_col = rechamada_col = None

    # 1ª passagem: busca match EXATO (mais confiável)
    for col in df_raw.columns:
        cl = str(col).lower().strip()
        if agente_col is None and cl in _AGENTE_EXATOS:
            agente_col = col
        if rechamada_col is None and cl in _RECHAMADA_EXATOS:
            rechamada_col = col

    # 2ª passagem: fallback — padrão com exclusão de colunas que NÃO são rechamada pura
    # Exclui explicitamente: shortcall, tma, chamadas (contagem), transferência
    _RECHAMADA_EXCLUIR = ('shortcall', 'tma', 'chamadas rechamadas', 'transf')
    if rechamada_col is None:
        for col in df_raw.columns:
            cl = str(col).lower().strip()
            if ('rechamada' in cl and '%' in cl
                    and not any(ex in cl for ex in _RECHAMADA_EXCLUIR)):
                rechamada_col = col
                break

    # 3ª passagem: fallback final — qualquer coluna com "rechamada" exceto as excluídas
    if rechamada_col is None:
        for col in df_raw.columns:
            cl = str(col).lower().strip()
            if ('rechamada' in cl
                    and not any(ex in cl for ex in _RECHAMADA_EXCLUIR)):
                rechamada_col = col
                break

    if not agente_col or not rechamada_col:
        st.error(
            f"Colunas obrigatórias não encontradas no arquivo de Rechamada. "
            f"Colunas detectadas: {list(df_raw.columns)}. "
            f"Verifique se contém 'Agente' e '(%) Rechamada'."
        )
        return False

    st.info(f"📋 Colunas detectadas → Agente: **{agente_col}** | Rechamada: **{rechamada_col}**")

    # Busca mapa Nome → Matrícula já salvo no Supabase
    res = (
        supabase.table("performance_operadores")
        .select("matricula,operador")
        .eq("supervisor", supervisor)
        .eq("servico", servico)
        .execute()
    )

    def _norm_nome(s):
        return str(s).upper().strip()

    nome_to_mat = {}
    if res.data:
        for r in res.data:
            if r.get('operador') and r.get('matricula'):
                nome_to_mat[_norm_nome(r['operador'])] = r['matricula']

    if not nome_to_mat:
        st.error(
            "⚠️ Nenhum dado do BI encontrado para esta equipe. "
            "Envie a planilha de **Métricas Gerais** antes de enviar a Rechamada."
        )
        return False

    registros = []
    nao_encontrados = []
    import math as _math

    for _, row in df_raw.iterrows():
        nome = _norm_nome(row.get(agente_col, ''))
        if not nome or nome in ('', 'NAN', 'NONE', 'TOTAL'):
            continue
        # Ignora linhas de rodapé/metadados do BI (ex: texto de filtros exportado)
        if len(nome) > 80 or nome.startswith('FILTRO') or nome.startswith('PARÂMETRO'):
            continue

        mat = nome_to_mat.get(nome)
        if not mat:
            nao_encontrados.append(nome)
            continue

        rec_val = _limpar_num(row.get(rechamada_col))
        if rec_val is not None:
            if not (_math.isnan(rec_val) or _math.isinf(rec_val)):
                if rec_val <= 1.0:
                    rec_val = round(rec_val * 100, 2)
            else:
                rec_val = None

        registros.append({
            'matricula':     mat,
            'supervisor':    supervisor,
            'servico':       servico,
            'rechamada':     rec_val,
            'atualizado_em': pd.Timestamp.now(tz='UTC').isoformat(),
        })

    if nao_encontrados:
        st.warning(
            f"⚠️ {len(nao_encontrados)} agente(s) da Rechamada não encontrado(s) na planilha do BI: "
            f"{', '.join(nao_encontrados[:5])}{'...' if len(nao_encontrados) > 5 else ''}"
        )

    if not registros:
        st.warning("Nenhum registro de Rechamada pôde ser vinculado. Verifique se a planilha do BI foi enviada primeiro.")
        return False

    # Deduplica
    seen = {}
    for rec in registros:
        key = (rec.get('matricula'), rec.get('supervisor'), rec.get('servico'))
        seen[key] = rec
    registros = list(seen.values())

    supabase.table("performance_operadores").upsert(
        registros,
        on_conflict="matricula,supervisor,servico"
    ).execute()

    carregar_dados_supervisor.clear()
    return True

@st.cache_data(ttl=60)
def carregar_dados_supervisor(supervisor: str, servico: str):
    """Lê dados do Supabase para o supervisor/serviço e retorna df no padrão do sistema."""
    supabase = conectar_supabase()

    res = (
        supabase.table("performance_operadores")
        .select("*")
        .eq("supervisor", supervisor)
        .eq("servico", servico)
        .execute()
    )

    if not res.data:
        return pd.DataFrame(), 'Operador', 'Matricula'

    df = pd.DataFrame(res.data)

    # Renomeia colunas do banco → padrão do sistema
    df = df.rename(columns={
        'operador':          'Operador',
        'matricula':         'Matricula',
        'aderencia':         'Aderencia_num',
        'absenteismo':       'Absenteismo_num',
        'produtividade':     'Produtividade_num',
        'transf':            'Transf_num',
        'tma_voz':           'TMA Voz_num',
        'shortcall':         'ShortCall_num',
        'silencio':          'Silencio_num',
        'pesquisa':          'Pesquisa_num',
        'resolutividade':    'Resolutividade_num',
        'pausa_produtiva':   'Pausa Produtiva_num',
        'pausa_improdutiva': 'Pausa Improdutiva_num',
        'pausa_total':       'Pausa Total_num',
        'fcr':               'FCR_num',
        'direcionado':       'Direcionado_num',
        'rechamada':         'Rechamada_num',
    })

    # Coerce todas as colunas _num para float (Supabase pode retornar como object/string)
    for metrica in METAS_BASE:
        col_num = f'{metrica}_num'
        if col_num in df.columns:
            df[col_num] = pd.to_numeric(df[col_num], errors='coerce')

    # Garante colunas de display formatadas para cada métrica
    for metrica, conf in METAS_BASE.items():
        col_num = f'{metrica}_num'
        unidade = conf['unidade']  # captura local para evitar bug de closure no lambda
        if col_num in df.columns:
            if metrica == 'TMA Voz':
                def _fmt_tma(x):
                    if pd.isna(x): return '---'
                    total_sec = round(float(x) * 60)
                    h = total_sec // 3600
                    m = (total_sec % 3600) // 60
                    s = total_sec % 60
                    return f"{h:02d}:{m:02d}:{s:02d}"
                df[metrica] = df[col_num].apply(_fmt_tma)
            else:
                df[metrica] = df[col_num].apply(
                    lambda x, u=unidade: f"{x:.2f}{u}" if pd.notna(x) else '---'
                )
        else:
            df[metrica] = '---'
            df[col_num] = None

    return df, 'Operador', 'Matricula'

@st.cache_data(ttl=60)
def buscar_tendencias(matricula: str, supervisor: str, servico: str) -> dict:
    """Compara os dois últimos uploads do operador e retorna tendência por métrica."""
    try:
        supabase = conectar_supabase()
        mat_clean = _limpar_matricula(matricula) or matricula.strip()

        res = (
            supabase.table("performance_historico")
            .select("upload_date,aderencia,resolutividade,tma_voz,pesquisa,silencio,"
                    "absenteismo,produtividade,transf,shortcall,pausa_total")
            .eq("matricula", mat_clean)
            .eq("supervisor", supervisor)
            .eq("servico", servico)
            .order("upload_date", desc=True)
            .limit(20)
            .execute()
        )

        if not res.data or len(res.data) < 2:
            return {}

        df_h = pd.DataFrame(res.data)
        df_h['upload_date'] = pd.to_datetime(df_h['upload_date'])

        datas = sorted(df_h['upload_date'].unique(), reverse=True)
        if len(datas) < 2:
            return {}

        atual   = df_h[df_h['upload_date'] == datas[0]].iloc[0]
        anterior = df_h[df_h['upload_date'] == datas[1]].iloc[0]

        _MAP_TEND = {
            'Aderencia':      'aderencia',
            'Resolutividade': 'resolutividade',
            'TMA Voz':        'tma_voz',
            'Pesquisa':       'pesquisa',
            'Silencio':       'silencio',
            'Absenteismo':    'absenteismo',
            'Produtividade':  'produtividade',
            'Transf':         'transf',
            'ShortCall':      'shortcall',
            'Pausa Total':    'pausa_total',
            'FCR':            'fcr',
            'Direcionado':    'direcionado',
            'Rechamada':      'rechamada',
        }

        tendencias = {}
        for metrica, col in _MAP_TEND.items():
            v_atual = atual.get(col)
            v_ant   = anterior.get(col)
            if v_atual is None or v_ant is None:
                continue
            try:
                v_atual = float(v_atual)
                v_ant   = float(v_ant)
                diff    = v_atual - v_ant
                if abs(diff) < 0.01:
                    tendencias[metrica] = 'stable'
                else:
                    menor_melhor = METAS_BASE[metrica]['menor_melhor']
                    subiu = diff > 0
                    tendencias[metrica] = 'good' if (subiu != menor_melhor) else 'bad'
            except Exception:
                pass

        return tendencias
    except Exception:
        return {}

@st.cache_data(ttl=60)
def buscar_supervisor_por_matricula(matricula: str):
    """Dado uma matrícula, retorna (supervisor, servico) registrado no Supabase."""
    supabase = conectar_supabase()
    mat_clean = _limpar_matricula(matricula) or matricula.strip()
    res = (
        supabase.table("performance_operadores")
        .select("supervisor,servico,operador")
        .eq("matricula", mat_clean)
        .limit(1)
        .execute()
    )
    if res.data:
        d = res.data[0]
        return d.get('supervisor'), d.get('servico'), d.get('operador')
    return None, None, None

# ---------- AUTH GESTORES ----------
def _hash_senha(matricula: str, senha: str) -> str:
    raw = f"{matricula}:{senha}:ndi_portal_2025"
    return hashlib.sha256(raw.encode()).hexdigest()

def gestor_buscar(matricula: str):
    supabase = conectar_supabase()
    try:
        res = supabase.table("gestores_auth").select("*").eq("matricula", matricula.strip()).limit(1).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None

def gestor_cadastrar(matricula: str, nome: str, servico: str, senha: str, email: str = '') -> bool:
    supabase = conectar_supabase()
    try:
        supabase.table("gestores_auth").insert({
            "matricula":  matricula.strip(),
            "nome":       nome,
            "servico":    servico,
            "senha_hash": _hash_senha(matricula, senha),
            "email":      email.strip().lower(),
        }).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao cadastrar: {e}")
        return False

def gestor_alterar_senha(matricula: str, senha_nova: str) -> bool:
    supabase = conectar_supabase()
    try:
        supabase.table("gestores_auth").update(
            {"senha_hash": _hash_senha(matricula, senha_nova)}
        ).eq("matricula", matricula.strip()).execute()
        return True
    except Exception as e:
        st.error(f"Erro ao alterar senha: {e}")
        return False

import smtplib, random, string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def _gerar_codigo(n=6) -> str:
    return ''.join(random.choices(string.digits, k=n))

def enviar_email_reset(destinatario: str, nome: str, codigo: str) -> bool:
    try:
        cfg = st.secrets["email"]
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🔑 Portal NDI — Código de redefinição de senha"
        msg["From"]    = cfg["usuario"]
        msg["To"]      = destinatario

        html = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;
                    background:#f4f7fb;border-radius:16px;padding:40px 36px;">
            <div style="text-align:center;margin-bottom:28px;">
                <p style="font-size:32px;margin:0;">🔑</p>
                <p style="font-size:11px;font-weight:800;color:#1a6fc4;
                          letter-spacing:3px;text-transform:uppercase;margin:8px 0 4px;">
                    Portal NDI
                </p>
                <p style="font-size:20px;font-weight:900;color:#0b2a6f;margin:0;">
                    Redefinição de senha
                </p>
            </div>
            <p style="color:#444;font-size:14px;margin:0 0 20px;">
                Olá, <b>{nome}</b>! Use o código abaixo para redefinir sua senha.<br>
                Ele é válido por <b>10 minutos</b>.
            </p>
            <div style="background:#0b2a6f;border-radius:12px;padding:24px;
                        text-align:center;margin:0 0 24px;">
                <p style="color:rgba(255,255,255,0.6);font-size:11px;
                          letter-spacing:2px;text-transform:uppercase;margin:0 0 8px;">
                    Seu código
                </p>
                <p style="color:#ffffff;font-size:36px;font-weight:900;
                          letter-spacing:10px;margin:0;">
                    {codigo}
                </p>
            </div>
            <p style="color:#999;font-size:12px;text-align:center;margin:0;">
                Se não foi você quem solicitou, ignore este e-mail.
            </p>
        </div>
        """
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(cfg["smtp_host"], int(cfg["smtp_port"])) as s:
            s.ehlo()
            s.starttls()
            s.login(cfg["usuario"], cfg["senha"])
            s.sendmail(cfg["usuario"], destinatario, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Erro ao enviar e-mail: {e}")
        return False

# ---------- HELPER: painel de análise ----------
def exibir_painel(df, col_op, col_mat, chave_aba="aba_ativa", mat_operador=None, metas=None):
    metas = metas or METAS_BASE
    df_eq = df[
        (~df[col_op].astype(str).str.upper().str.contains('EQUIPE|TOTAL|MÉDIA|MEDIA|SUPERVISOR', na=False)) &
        (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))
    ].copy()

    # ── CSS das abas ───────────────────────────────────
    st.markdown("""
    <style>
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: white !important;
        color: #0b2a6f !important;
        border: 2px solid #dce6f7 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        transition: all 0.2s !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: #0b2a6f !important;
        color: white !important;
        border-color: #0b2a6f !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if chave_aba not in st.session_state:
        st.session_state[chave_aba] = "Individual"

    aba = st.session_state[chave_aba]

    # Cabeçalho com abas
    st.markdown(f"""
    <div style="display:flex; align-items:center; justify-content:space-between;
                margin-bottom: 4px;">
        <p style="margin:0; font-size:18px; font-weight:800; color:#0b2a6f;">📊 Painel de Análise</p>
        <p style="margin:0; font-size:12px; color:#aaa;">{len(df_eq)} operadores carregados</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    if c1.button("👤 Individual", use_container_width=True, key=f"btn_ind_{chave_aba}"):
        st.session_state[chave_aba] = "Individual"; st.rerun()
    if c2.button("👥 Equipe",     use_container_width=True, key=f"btn_eq_{chave_aba}"):
        st.session_state[chave_aba] = "Equipe";     st.rerun()
    if c3.button("🏆 Ranking",    use_container_width=True, key=f"btn_rk_{chave_aba}"):
        st.session_state[chave_aba] = "Ranking";    st.rerun()
    if c4.button("🩺 Saúde",      use_container_width=True, key=f"btn_sa_{chave_aba}"):
        st.session_state[chave_aba] = "Saúde";      st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── INDIVIDUAL ──────────────────────────────────────
    if aba == "Individual":
        # Se a matrícula já foi identificada externamente, usa direto sem mostrar o campo de busca
        if mat_operador:
            mat = mat_operador
        else:
            mat = st.text_input("🔍 Digite a Matrícula do Operador", placeholder="Ex: 1035323")

        def _renderizar_operador(mat_busca):
            res = df[df[col_mat].astype(str) == mat_busca.strip()]
            if not res.empty:
                r = res.iloc[0]
                # Só exibe o banner se não vier da área do operador (onde já aparece acima)
                if not mat_operador:
                    st.markdown(f"""
                    <div style="background:linear-gradient(135deg,#0b2a6f,#1a6fc4);
                                border-radius:14px; padding:18px 22px; margin:10px 0 18px 0;
                                display:flex; align-items:center; gap:14px;">
                        <span style="font-size:32px;">👤</span>
                        <div>
                            <p style="margin:0; color:rgba(255,255,255,0.65); font-size:11px;
                                      letter-spacing:2px; text-transform:uppercase;">Operador</p>
                            <p style="margin:0; color:white; font-size:20px; font-weight:900;">{r[col_op]}</p>
                            <p style="margin:0; color:rgba(255,255,255,0.5); font-size:12px;">Matrícula {r[col_mat]}</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Busca tendências do histórico
                sup_tend = st.session_state.get('op_supervisor') or df['supervisor'].iloc[0] if 'supervisor' in df.columns else ''
                svc_tend = st.session_state.get('op_servico')    or df['servico'].iloc[0]    if 'servico'    in df.columns else ''
                tend = buscar_tendencias(str(r[col_mat]), sup_tend, svc_tend)

                # Linha 1 — 5 métricas principais
                metricas_l1 = [
                    ("Aderência",      'Aderencia'),
                    ("Resolutividade", 'Resolutividade'),
                    ("TMA Voz",        'TMA Voz'),
                    ("Pesquisa",       'Pesquisa'),
                    ("Silêncio",       'Silencio'),
                ]
                cols = st.columns(5)
                for idx, (label, key) in enumerate(metricas_l1):
                    with cols[idx]:
                        exibir_card(label, r[key], definir_cor_kpi(r[f'{key}_num'], key.replace(' ','') if key != 'TMA Voz' else 'TMA Voz', metas), tend.get(key))

                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                # Linha 2 — 5 métricas adicionais
                metricas_l2 = [
                    ("Absenteísmo",   'Absenteismo'),
                    ("Produtividade", 'Produtividade'),
                    ("Transf",        'Transf'),
                    ("ShortCall",     'ShortCall'),
                    ("Pausa Total",   'Pausa Total'),
                ]
                cols2 = st.columns(5)
                for idx, (label, key) in enumerate(metricas_l2):
                    with cols2[idx]:
                        exibir_card(label, r[key], definir_cor_kpi(r.get(f'{key}_num'), key, metas), tend.get(key))

                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

                # Linha 3 — FCR, Direcionado e Rechamada
                metricas_l3 = [
                    ("FCR (1° Contato)", 'FCR'),
                    ("Direcionado",      'Direcionado'),
                    ("Rechamada",        'Rechamada'),
                ]
                cols3 = st.columns(5)
                for idx, (label, key) in enumerate(metricas_l3):
                    with cols3[idx]:
                        exibir_card(label, r[key], definir_cor_kpi(r.get(f'{key}_num'), key, metas), tend.get(key))
            else:
                st.warning("⚠️ Matrícula não encontrada.")

        if mat:
            _renderizar_operador(mat)
        elif not mat_operador:
            st.markdown("""
            <div style='text-align:center; padding:50px 0; color:#bbb;'>
                <p style='font-size:40px; margin:0;'>🔍</p>
                <p style='font-size:15px; margin-top:10px;'>Digite a matrícula para ver os KPIs do operador</p>
            </div>
            """, unsafe_allow_html=True)

    # ── EQUIPE ──────────────────────────────────────────
    if aba == "Equipe":
        if not df_eq.empty:
            # Usa a linha __TOTAL__ (apurado real do BI) quando disponível
            df_total = df[df[col_mat].astype(str) == '__TOTAL__']
            usar_total = not df_total.empty
            fonte_label = "valores apurados pelo BI" if usar_total else f"médias de {len(df_eq)} operadores"
            st.markdown(f"<p style='color:#888; font-size:13px; margin:0 0 12px 0;'>📋 Exibindo {fonte_label}</p>", unsafe_allow_html=True)

            def _get_valor_equipe(metrica):
                col_num = f'{metrica}_num'
                if usar_total:
                    val = df_total.iloc[0].get(col_num)
                    return val if pd.notna(val) else None
                else:
                    return df_eq[col_num].mean() if col_num in df_eq.columns else None

            metricas_todos = list(metas.keys())
            row1 = metricas_todos[:5]
            row2 = metricas_todos[5:10]
            row3 = metricas_todos[10:]

            def _fmt_equipe(metrica, val):
                if val is None or pd.isna(val):
                    return '---'
                if metrica == 'TMA Voz':
                    total_sec = round(float(val) * 60)
                    h = total_sec // 3600
                    m = (total_sec % 3600) // 60
                    s = total_sec % 60
                    return f"{h:02d}:{m:02d}:{s:02d}"
                conf = metas[metrica]
                return f"{val:.2f}{conf['unidade']}"

            cols1 = st.columns(5)
            for i, metrica in enumerate(row1):
                val   = _get_valor_equipe(metrica)
                display = _fmt_equipe(metrica, val)
                with cols1[i]:
                    exibir_card(metrica, display, definir_cor_kpi(val, metrica, metas))

            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

            cols2 = st.columns(5)
            for i, metrica in enumerate(row2):
                val   = _get_valor_equipe(metrica)
                display = _fmt_equipe(metrica, val)
                with cols2[i]:
                    exibir_card(metrica, display, definir_cor_kpi(val, metrica, metas))

            if row3:
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                cols3 = st.columns(5)
                for i, metrica in enumerate(row3):
                    val   = _get_valor_equipe(metrica)
                    display = _fmt_equipe(metrica, val)
                    with cols3[i]:
                        exibir_card(metrica, display, definir_cor_kpi(val, metrica, metas))

            st.markdown("""
            <div style="display:flex; gap:18px; margin-top:14px; justify-content:center;">
                <span style="font-size:12px; color:#28a745; font-weight:700;">● Dentro da meta</span>
                <span style="font-size:12px; color:#ffc107; font-weight:700;">● Atenção</span>
                <span style="font-size:12px; color:#dc3545; font-weight:700;">● Fora da meta</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum operador encontrado.")

    # ── RANKING ─────────────────────────────────────────
    if aba == "Ranking":
        col_sel, col_vazio = st.columns([2, 3])
        with col_sel:
            metrica_sel = st.selectbox("Selecionar métrica:", list(metas.keys()))

        top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
            by=f'{metrica_sel}_num', ascending=metas[metrica_sel]['menor_melhor']
        ).head(3)

        if top.empty:
            st.info("Sem dados suficientes para este ranking.")
        else:
            top_list = list(top.iterrows())
            medalhas = [
                {"emoji": "🥇", "label": "1º lugar", "cor": "#FFD700", "bg": "#fffbe6", "altura": "160px", "tamanho": "28px"},
                {"emoji": "🥈", "label": "2º lugar", "cor": "#C0C0C0", "bg": "#f7f7f7", "altura": "130px", "tamanho": "22px"},
                {"emoji": "🥉", "label": "3º lugar", "cor": "#CD7F32", "bg": "#fff5ee", "altura": "110px", "tamanho": "20px"},
            ]
            ordem_exibicao = [1, 0, 2] if len(top_list) >= 3 else list(range(len(top_list)))

            st.markdown(f"<p style='color:#888; font-size:13px; margin:8px 0 20px 0; text-align:center;'>🏆 Top 3 — <b>{metrica_sel}</b></p>", unsafe_allow_html=True)

            cols_podio = st.columns(3)
            for col_idx, rank_idx in enumerate(ordem_exibicao):
                if rank_idx >= len(top_list):
                    continue
                _, row = top_list[rank_idx]
                m = medalhas[rank_idx]
                cor_kpi = definir_cor_kpi(row[f'{metrica_sel}_num'], metrica_sel, metas)
                nome = row[col_op] if col_op in row else f"Matrícula {row[col_mat]}"
                nome_curto = f"Mat. {row[col_mat]}"

                with cols_podio[col_idx]:
                    st.markdown(f"""
                    <div style="background:{m['bg']}; border-radius:18px;
                                border: 2px solid {m['cor']}; padding:20px 12px;
                                text-align:center; min-height:{m['altura']};
                                display:flex; flex-direction:column;
                                align-items:center; justify-content:center; gap:6px;
                                box-shadow: 0 4px 16px rgba(0,0,0,0.08);">
                        <p style="margin:0; font-size:36px; line-height:1;">{m['emoji']}</p>
                        <p style="margin:0; font-size:10px; color:#999; font-weight:700;
                                  text-transform:uppercase; letter-spacing:1.5px;">{m['label']}</p>
                        <p style="margin:0; font-size:13px; font-weight:800; color:#1f3a5f;
                                  line-height:1.3;">{nome_curto}</p>
                        <p style="margin:0; font-size:{m['tamanho']}; font-weight:900;
                                  color:{cor_kpi};">{row[metrica_sel]}</p>
                    </div>
                    """, unsafe_allow_html=True)

    # ── SAÚDE ────────────────────────────────────────────
    if aba == "Saúde":
        col_sel2, _ = st.columns([2, 3])
        with col_sel2:
            metrica_sel = st.selectbox("Selecione a Métrica:", list(metas.keys()))

        conf_s   = metas[metrica_sel]
        df_saude = df_eq.copy()

        def verificar_status(valor):
            if pd.isna(valor): return "Sem dado"
            if conf_s['menor_melhor']:
                return "✅ Meta OK" if valor <= conf_s['valor'] else ("⚠️ Atenção" if valor <= conf_s['valor'] + conf_s['margem'] else "❌ Fora da Meta")
            return "✅ Meta OK" if valor >= conf_s['valor'] else ("⚠️ Atenção" if valor >= conf_s['valor'] - conf_s['margem'] else "❌ Fora da Meta")

        df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)
        df_saude['Valor']  = df_saude.apply(
            lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---", axis=1
        )

        # Resumo rápido
        total = len(df_saude)
        ok    = (df_saude['Status'] == "✅ Meta OK").sum()
        at    = (df_saude['Status'] == "⚠️ Atenção").sum()
        out   = (df_saude['Status'] == "❌ Fora da Meta").sum()
        c1s, c2s, c3s = st.columns(3)
        with c1s: exibir_card("✅ Na Meta",     f"{ok}/{total}",  "#28a745")
        with c2s: exibir_card("⚠️ Atenção",    f"{at}/{total}",  "#ffc107")
        with c3s: exibir_card("❌ Fora da Meta",f"{out}/{total}", "#dc3545")

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Exibe apenas matrícula (sem nome do operador para preservar privacidade)
        tabela = df_saude[[col_mat, 'Valor', 'Status']].rename(
            columns={col_mat: 'Matrícula', 'Valor': metrica_sel}
        ).reset_index(drop=True)
        st.dataframe(tabela, use_container_width=True, hide_index=True)

# ---------- HUB ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:
    # Força scroll ao topo no elemento correto do Streamlit
    st.components.v1.html("""
    <script>
        (function() {
            var tries = 0;
            function scrollTop() {
                var el = window.parent.document.querySelector('[data-testid="stMain"]');
                if (el) { el.scrollTop = 0; }
                else if (tries++ < 10) { setTimeout(scrollTop, 100); }
            }
            scrollTop();
        })();
    </script>
    """, height=0)

    # CSS do HUB — estiliza as colunas diretamente pelo DOM
    st.markdown("""
    <style>

    /* Zera padding global da tela principal */
    .stApp { background: linear-gradient(160deg, #0b2a6f 0%, #1a6fc4 100%) !important; }
    section.main > div.block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Impede scroll na tela do HUB */
    html, body, .stApp {
        height: 100vh !important;
        overflow: hidden !important;
    }

    /* Container horizontal ocupa exatamente a viewport */
    [data-testid="stHorizontalBlock"] {
        height: 100vh !important;
        margin: 0 !important;
        gap: 0 !important;
    }

    /* Coluna ESQUERDA — glassmorphism branco */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
        background: rgba(255, 255, 255, 0.97) !important;
        backdrop-filter: blur(28px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
        border-right: 1px solid rgba(200, 215, 235, 0.8) !important;
        box-shadow: 4px 0 40px rgba(0, 0, 0, 0.12) !important;
        padding: 60px 50px 60px 50px !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    /* Texto da coluna esquerda — legível no fundo branco */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) p,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) span,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) label {
        color: #4a6080 !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) h1,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) h2,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) h3 {
        color: #0b2a6f !important;
    }

    /* Coluna DIREITA (2ª coluna) */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
        background: linear-gradient(160deg, #0b2a6f 0%, #1a6fc4 100%) !important;
        padding: 40px !important;
        height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Botões do HUB — branco claro com borda azul */
    div[data-testid="stButton"] > button {
        background: rgba(255, 255, 255, 0.75) !important;
        color: #0b2a6f !important;
        border: 1.5px solid rgba(11, 42, 111, 0.2) !important;
        height: 62px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        width: 100% !important;
        margin-bottom: 4px !important;
        letter-spacing: 0.8px !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 18px rgba(11, 42, 111, 0.1) !important;
        transition: all 0.22s ease !important;
    }
    div[data-testid="stButton"] > button *,
    div[data-testid="stButton"] > button p,
    div[data-testid="stButton"] > button span,
    div[data-testid="stButton"] > button div,
    div[data-testid="stButton"] > button label {
        color: #0b2a6f !important;
        -webkit-text-fill-color: #0b2a6f !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: rgba(255, 255, 255, 0.95) !important;
        border-color: rgba(11, 42, 111, 0.45) !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 30px rgba(11, 42, 111, 0.15) !important;
    }
    div[data-testid="stButton"] > button:hover * {
        color: #0b2a6f !important;
        -webkit-text-fill-color: #0b2a6f !important;
    }

    div[data-testid="stButton"] > button:active {
        transform: scale(0.97) !important;
        box-shadow: none !important;
    }

    </style>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="small")

    # ── LADO ESQUERDO: título + botões ────────────────────────
    with col_left:
        st.markdown("""
            <p style="font-size:10px; font-weight:800; color:#1a6fc4;
                      letter-spacing:4px; text-transform:uppercase; margin:0 0 18px 0;
                      border-left: 3px solid #1a6fc4; padding-left: 10px;">
                Hapvida Notredame Intermédica
            </p>
            <p style="font-size:32px; font-weight:900; color:#0b2a6f;
                      margin:0 0 10px 0; line-height:1.15; letter-spacing:-0.5px;">
                Portal de<br>Performance <span style="color:#1a6fc4;">NDI</span>
            </p>
            <p style="font-size:13px; color:#6b82a0; margin:0 0 40px 0;
                      font-weight:500; letter-spacing:0.3px;">
                Selecione como deseja acessar
            </p>
        """, unsafe_allow_html=True)

        if st.button("👤  OPERADOR", use_container_width=True):
            st.session_state.servico = "Operador"; st.rerun()
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🗂️  ÁREA DO GESTOR", use_container_width=True):
            st.session_state.servico = "Supervisor"; st.rerun()

    # ── LADO DIREITO: fundo azul + logo ───────────────────────
    with col_right:
        st.markdown("""
            <style>
            @keyframes heartbeat {
                0%   { transform: scale(1);    }
                14%  { transform: scale(1.08); }
                28%  { transform: scale(1);    }
                42%  { transform: scale(1.05); }
                70%  { transform: scale(1);    }
                100% { transform: scale(1);    }
            }
            .logo-pulse {
                animation: heartbeat 2.2s ease-in-out infinite;
                transform-origin: center center;
            }
            </style>
            <div style="display:flex; flex-direction:column; align-items:center;
                        justify-content:center; min-height:85vh; gap:24px;">
                <img src="https://raw.githubusercontent.com/HapvidaNotre/portal-ndi/main/logo-hapvida-escudo-2048.png"
                     class="logo-pulse"
                     style="width:210px; filter:drop-shadow(0 6px 24px rgba(0,0,0,0.35));" />
                <p style="color:rgba(255,255,255,0.65); font-size:12px;
                          letter-spacing:3px; text-transform:uppercase; margin:0;">
                    Portal de Performance
                </p>
                <div style="text-align:center; margin-top:-10px;">
                    <p style="color:rgba(255,255,255,0.35); font-size:10px;
                              letter-spacing:2px; text-transform:uppercase; margin:0 0 4px 0;">
                        Desenvolvido por
                    </p>
                    <p style="color:rgba(255,255,255,0.75); font-size:13px;
                              font-weight:700; letter-spacing:1px; margin:0;">
                        Sup. Erik Coelho
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)

# ---------- DASHBOARD ----------
else:

    # ══════════════════════════════════════════════════
    # ÁREA DA SUPERVISÃO — com autenticação
    # ══════════════════════════════════════════════════
    if st.session_state.servico == "Supervisor":

        SUPERVISORES = {
            "SAC NDI":     ["Erik","Davi","Elaine","Sayanne","Beatriz","Aline","Marcelo,","Richarlysson"],
            "SAC PPO":     ["Ellen","Carla","Magno","Alex"],
            "SAC HAPVIDA": ["Hapvida"],
        }

        # Inicializa estados de autenticação
        for _k, _v in [('gestor_logado', False), ('gestor_matricula', ''),
                        ('gestor_nome', ''), ('gestor_servico', ''),
                        ('gestor_tela', 'login')]:
            if _k not in st.session_state:
                st.session_state[_k] = _v

        # ── Barra de navegação do Gestor (substituiu a sidebar) ───────────
        if st.session_state.gestor_logado:
            _col_info, _col_sair, _col_voltar = st.columns([4, 1, 1])
            with _col_info:
                st.markdown(
                    f"<p style='margin:0; font-size:13px; color:#0b2a6f; font-weight:700;'>"
                    f"🗂️ {st.session_state.gestor_nome} &nbsp;·&nbsp; "
                    f"<span style='color:#666; font-weight:400;'>{st.session_state.gestor_servico}</span></p>",
                    unsafe_allow_html=True
                )
            with _col_sair:
                if st.button("🔒 Sair", use_container_width=True):
                    for _k in ('gestor_logado','gestor_matricula','gestor_nome','gestor_servico'):
                        st.session_state[_k] = '' if _k != 'gestor_logado' else False
                    st.session_state.gestor_tela = 'login'
                    st.rerun()
            with _col_voltar:
                if st.button("← Início", use_container_width=True):
                    for _k in ('gestor_logado','gestor_matricula','gestor_nome','gestor_servico'):
                        st.session_state[_k] = '' if _k != 'gestor_logado' else False
                    st.session_state.gestor_tela = 'login'
                    st.session_state.servico = None
                    st.rerun()
        else:
            _col_v, _ = st.columns([1, 5])
            with _col_v:
                if st.button("← Início"):
                    st.session_state.servico = None
                    st.rerun()

        # ══════════════════════════════════════════════════
        # NÃO LOGADO — telas de login / cadastro
        # ══════════════════════════════════════════════════
        if not st.session_state.gestor_logado:

            # CSS completo da tela de login
            st.markdown("""
            <style>

            /* Fundo azul gradiente na tela de login */
            .stApp {
                background: linear-gradient(160deg, #0b2a6f 0%, #1a6fc4 100%) !important;
            }

            /* Bloco central fica sobre o gradiente */
            section.main > div.block-container {
                padding-top: 0 !important;
            }

            /* Card de login — glassmorphism */
            .login-glass-card {
                background: rgba(255, 255, 255, 0.10);
                backdrop-filter: blur(24px) saturate(180%);
                -webkit-backdrop-filter: blur(24px) saturate(180%);
                border: 1px solid rgba(255, 255, 255, 0.22);
                border-radius: 24px;
                padding: 48px 44px 40px 44px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
                max-width: 420px;
                margin: 0 auto;
            }

            /* Inputs — fundo semitransparente escuro + texto branco */
            div[data-testid="stTextInput"] > div {
                background: rgba(255, 255, 255, 0.10) !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
                border: 1.5px solid rgba(255, 255, 255, 0.30) !important;
                box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15) !important;
            }
            div[data-testid="stTextInput"] > div:hover {
                background: rgba(255, 255, 255, 0.16) !important;
                border-color: rgba(255, 255, 255, 0.50) !important;
                box-shadow: 0 6px 20px rgba(0, 0, 0, 0.20) !important;
            }
            div[data-testid="stTextInput"] > div:focus-within {
                background: rgba(255, 255, 255, 0.18) !important;
                border-color: #64b9ff !important;
                box-shadow:
                    0 0 0 3px rgba(90, 185, 255, 0.35),
                    0 6px 20px rgba(0, 0, 0, 0.18) !important;
            }

            /* Texto branco no input — legível sobre fundo escuro */
            div[data-testid="stTextInput"] input {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
                caret-color: #ffffff !important;
            }
            div[data-testid="stTextInput"] input::placeholder {
                color: rgba(255, 255, 255, 0.50) !important;
                font-style: italic !important;
                font-size: 13px !important;
                -webkit-text-fill-color: rgba(255, 255, 255, 0.50) !important;
            }
            /* Labels ficam brancas pois estão sobre o fundo azul gradient */
            div[data-testid="stTextInput"] label,
            div[data-testid="stTextInput"] label p {
                color: rgba(255, 255, 255, 0.90) !important;
            }
            /* Ícone olho da senha */
            div[data-testid="stTextInput"] button {
                background: transparent !important;
                border: none !important;
                color: rgba(255, 255, 255, 0.65) !important;
                transition: color 0.2s ease !important;
                margin-right: 6px !important;
            }
            div[data-testid="stTextInput"] button:hover {
                color: rgba(255, 255, 255, 0.95) !important;
                background: transparent !important;
            }

            /* Botões dentro do card — glass claro */
            div[data-testid="stButton"] > button {
                background: rgba(255, 255, 255, 0.18) !important;
                color: #ffffff !important;
                border: 1.5px solid rgba(255, 255, 255, 0.35) !important;
                border-radius: 12px !important;
                height: 52px !important;
                font-size: 14px !important;
                font-weight: 700 !important;
                letter-spacing: 0.5px !important;
                backdrop-filter: blur(8px) !important;
                -webkit-backdrop-filter: blur(8px) !important;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1) !important;
                transition: all 0.22s ease !important;
            }
            div[data-testid="stButton"] > button *,
            div[data-testid="stButton"] > button p,
            div[data-testid="stButton"] > button span,
            div[data-testid="stButton"] > button div {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }
            div[data-testid="stButton"] > button:hover {
                background: rgba(255, 255, 255, 0.30) !important;
                border-color: rgba(255, 255, 255, 0.6) !important;
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 24px rgba(0,0,0,0.18) !important;
            }
            div[data-testid="stButton"] > button:hover * {
                color: #ffffff !important;
                -webkit-text-fill-color: #ffffff !important;
            }

            /* Alertas legíveis no fundo escuro */
            [data-testid="stAlert"] p,
            [data-testid="stAlert"] div,
            [data-testid="stAlert"] span {
                color: #1a1a1a !important;
            }

            </style>
            """, unsafe_allow_html=True)

            _, col_center, _ = st.columns([1, 2, 1])
            with col_center:

                # ── TELA DE LOGIN ─────────────────────────────
                if st.session_state.gestor_tela == 'login':
                    st.markdown("""
                    <div class="login-glass-card">
                        <div style="text-align:center; margin-bottom:32px;">
                            <p style="font-size:40px; margin:0 0 12px 0;">🗂️</p>
                            <p style="font-size:10px; font-weight:800; color:rgba(255,255,255,0.55);
                                      letter-spacing:3px; text-transform:uppercase; margin:0 0 6px 0;">
                                Portal NDI
                            </p>
                            <p style="font-size:24px; font-weight:900; color:#ffffff; margin:0 0 4px 0;">
                                Área do Gestor
                            </p>
                            <p style="font-size:13px; color:rgba(255,255,255,0.5); margin:0;">
                                Acesse com sua matrícula e senha
                            </p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                    mat_login  = st.text_input("👤  Matrícula", placeholder="Ex: 1035323", key="login_mat")
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    sen_login  = st.text_input("🔒  Senha", type="password", placeholder="Sua senha", key="login_sen")
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

                    col_a, col_b = st.columns(2)
                    entrar   = col_a.button("✅ Entrar",           use_container_width=True)
                    cadastro = col_b.button("📝 Primeiro acesso", use_container_width=True)

                    esqueci = st.button("🔑 Esqueci minha senha", use_container_width=True)

                    if entrar:
                        if not mat_login or not sen_login:
                            st.warning("Preencha matrícula e senha.")
                        else:
                            gestor = gestor_buscar(mat_login)
                            if gestor is None:
                                st.error("Matrícula não cadastrada. Clique em **Primeiro acesso** para criar sua conta.")
                            elif gestor['senha_hash'] != _hash_senha(mat_login, sen_login):
                                st.error("Senha incorreta.")
                            else:
                                st.session_state.gestor_logado   = True
                                st.session_state.gestor_matricula = mat_login
                                st.session_state.gestor_nome     = gestor['nome']
                                st.session_state.gestor_servico  = gestor['servico']
                                st.rerun()

                    if esqueci:
                        st.session_state.gestor_tela = 'esqueci_senha'
                        st.rerun()

                    if cadastro:
                        st.session_state.gestor_tela = 'cadastro'
                        st.rerun()

                # ── TELA DE CADASTRO (primeiro acesso) ────────
                elif st.session_state.gestor_tela == 'cadastro':
                    st.markdown("""
                    <div style="text-align:center; margin-bottom:24px;">
                        <p style="font-size:32px; margin:0;">📝</p>
                        <p style="font-size:20px; font-weight:900; color:#ffffff; margin:4px 0 4px 0;">Criar conta</p>
                        <p style="font-size:13px; color:rgba(255,255,255,0.65); margin:0;">Preencha seus dados para o primeiro acesso</p>
                    </div>
                    """, unsafe_allow_html=True)

                    mat_cad  = st.text_input("👤  Sua Matrícula",  placeholder="Ex: 1035323",  key="cad_mat")
                    svc_cad  = st.selectbox("📋  Serviço",         list(SUPERVISORES.keys()),   key="cad_svc")
                    nomes_c  = SUPERVISORES.get(svc_cad, [])
                    nom_cad  = st.selectbox("🙋  Seu nome",        nomes_c,                     key="cad_nom")

                    col_email, col_dom = st.columns([3, 2])
                    with col_email:
                        prefixo_email = st.text_input("📧  Seu e-mail corporativo", placeholder="nome.sobrenome", key="cad_email_prefix")
                    with col_dom:
                        st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
                        st.markdown("<p style='color:rgba(255,255,255,0.6); font-size:14px; padding-top:14px; margin:0;'>@hapvida.com.br</p>", unsafe_allow_html=True)
                    email_cad = f"{prefixo_email.strip().lower()}@hapvida.com.br" if prefixo_email.strip() else ""

                    sen_cad  = st.text_input("🔒  Criar senha",    type="password", placeholder="Mínimo 6 caracteres", key="cad_sen")
                    sen_cad2 = st.text_input("✅  Confirmar senha",type="password", placeholder="Repita a senha",      key="cad_sen2")

                    col_c, col_d = st.columns(2)
                    salvar  = col_c.button("✅ Criar conta",  use_container_width=True)
                    voltar  = col_d.button("← Voltar",        use_container_width=True)

                    if voltar:
                        st.session_state.gestor_tela = 'login'
                        st.rerun()

                    if salvar:
                        if not mat_cad or not sen_cad or not prefixo_email.strip():
                            st.warning("Preencha todos os campos, incluindo o e-mail.")
                        elif len(sen_cad) < 6:
                            st.warning("A senha deve ter no mínimo 6 caracteres.")
                        elif sen_cad != sen_cad2:
                            st.error("As senhas não coincidem.")
                        elif gestor_buscar(mat_cad) is not None:
                            st.error("Esta matrícula já possui cadastro. Volte e faça login.")
                        else:
                            ok = gestor_cadastrar(mat_cad, nom_cad, svc_cad, sen_cad, email_cad)
                            if ok:
                                st.success("✅ Conta criada! Fazendo login...")
                                time.sleep(1)
                                st.session_state.gestor_logado    = True
                                st.session_state.gestor_matricula = mat_cad
                                st.session_state.gestor_nome      = nom_cad
                                st.session_state.gestor_servico   = svc_cad
                                st.session_state.gestor_tela      = 'login'
                                st.rerun()

                # ── TELA: ESQUECI MINHA SENHA ──────────────────
                elif st.session_state.gestor_tela == 'esqueci_senha':
                    st.markdown("""
                    <div style="text-align:center; margin-bottom:24px;">
                        <p style="font-size:32px; margin:0;">📧</p>
                        <p style="font-size:20px; font-weight:900; color:#ffffff; margin:4px 0;">Esqueci minha senha</p>
                        <p style="font-size:13px; color:rgba(255,255,255,0.55); margin:0;">
                            Digite sua matrícula para receber o código no e-mail cadastrado.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    mat_esq = st.text_input("👤  Matrícula", placeholder="Ex: 1035323", key="esq_mat")

                    col_env, col_vol = st.columns(2)
                    enviar_cod = col_env.button("📨 Enviar código", use_container_width=True)
                    vol_esq    = col_vol.button("← Voltar",         use_container_width=True)

                    if vol_esq:
                        st.session_state.gestor_tela = 'login'
                        st.rerun()

                    if enviar_cod:
                        if not mat_esq:
                            st.warning("Digite sua matrícula.")
                        else:
                            gestor = gestor_buscar(mat_esq.strip())
                            if gestor is None:
                                st.error("Matrícula não encontrada.")
                            elif not gestor.get('email'):
                                st.error("Nenhum e-mail cadastrado para esta matrícula. Entre em contato com o administrador.")
                            else:
                                codigo = _gerar_codigo()
                                st.session_state.reset_codigo    = codigo
                                st.session_state.reset_matricula = mat_esq.strip()
                                st.session_state.reset_expiry    = time.time() + 600  # 10 min
                                enviado = enviar_email_reset(gestor['email'], gestor['nome'], codigo)
                                if enviado:
                                    email_mask = gestor['email']
                                    partes = email_mask.split('@')
                                    email_mask = partes[0][:3] + '***@hapvida.com.br'
                                    st.success(f"✅ Código enviado para **{email_mask}**. Verifique sua caixa de entrada.")
                                    time.sleep(1.5)
                                    st.session_state.gestor_tela = 'verificar_codigo'
                                    st.rerun()

                # ── TELA: VERIFICAR CÓDIGO ─────────────────────
                elif st.session_state.gestor_tela == 'verificar_codigo':
                    st.markdown("""
                    <div style="text-align:center; margin-bottom:24px;">
                        <p style="font-size:32px; margin:0;">🔢</p>
                        <p style="font-size:20px; font-weight:900; color:#ffffff; margin:4px 0;">Digite o código</p>
                        <p style="font-size:13px; color:rgba(255,255,255,0.55); margin:0;">
                            Insira o código de 6 dígitos enviado ao seu e-mail.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    cod_digitado = st.text_input("🔢  Código de verificação", placeholder="Ex: 483921", key="cod_ver")

                    col_ok, col_rv = st.columns(2)
                    verificar  = col_ok.button("✅ Verificar", use_container_width=True)
                    reenviar   = col_rv.button("🔄 Reenviar",  use_container_width=True)

                    if reenviar:
                        st.session_state.gestor_tela = 'esqueci_senha'
                        st.rerun()

                    if verificar:
                        expiry = st.session_state.get('reset_expiry', 0)
                        if time.time() > expiry:
                            st.error("⏱️ Código expirado. Solicite um novo.")
                        elif cod_digitado.strip() != st.session_state.get('reset_codigo', ''):
                            st.error("❌ Código incorreto. Tente novamente.")
                        else:
                            st.session_state.gestor_tela = 'nova_senha_reset'
                            st.rerun()

                # ── TELA: NOVA SENHA APÓS RESET ────────────────
                elif st.session_state.gestor_tela == 'nova_senha_reset':
                    st.markdown("""
                    <div style="text-align:center; margin-bottom:24px;">
                        <p style="font-size:32px; margin:0;">🔒</p>
                        <p style="font-size:20px; font-weight:900; color:#ffffff; margin:4px 0;">Nova senha</p>
                        <p style="font-size:13px; color:rgba(255,255,255,0.55); margin:0;">
                            Escolha uma senha forte para sua conta.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    nova_sen  = st.text_input("🔒  Nova senha",     type="password", placeholder="Mínimo 6 caracteres", key="rst_nova")
                    nova_sen2 = st.text_input("✅  Confirmar senha", type="password", key="rst_nova2")

                    salvar_rst = st.button("💾 Salvar nova senha", use_container_width=True)

                    if salvar_rst:
                        if len(nova_sen) < 6:
                            st.warning("A senha deve ter no mínimo 6 caracteres.")
                        elif nova_sen != nova_sen2:
                            st.error("As senhas não coincidem.")
                        else:
                            mat_rst = st.session_state.get('reset_matricula', '')
                            if gestor_alterar_senha(mat_rst, nova_sen):
                                for k in ('reset_codigo', 'reset_matricula', 'reset_expiry'):
                                    st.session_state.pop(k, None)
                                st.success("✅ Senha redefinida com sucesso! Faça login.")
                                time.sleep(1.5)
                                st.session_state.gestor_tela = 'login'
                                st.rerun()

                # ── TELA DE ALTERAR SENHA ─────────────────────
                elif st.session_state.gestor_tela == 'alterar_senha':
                    st.markdown("""
                    <div style="text-align:center; margin-bottom:24px;">
                        <p style="font-size:32px; margin:0;">🔑</p>
                        <p style="font-size:20px; font-weight:900; color:#0b2a6f; margin:4px 0;">Alterar senha</p>
                    </div>
                    """, unsafe_allow_html=True)

                    sen_at   = st.text_input("🔑  Senha atual",    type="password", key="alt_at")
                    sen_nova = st.text_input("🔒  Nova senha",     type="password", placeholder="Mínimo 6 caracteres", key="alt_nova")
                    sen_nov2 = st.text_input("✅  Confirmar nova", type="password", key="alt_nov2")

                    col_e, col_f = st.columns(2)
                    confirmar = col_e.button("✅ Confirmar", use_container_width=True)
                    can_alt   = col_f.button("← Cancelar",  use_container_width=True)

                    if can_alt:
                        st.session_state.gestor_tela = 'logado'
                        st.rerun()
                    if confirmar:
                        gestor = gestor_buscar(st.session_state.gestor_matricula)
                        if gestor and gestor['senha_hash'] != _hash_senha(st.session_state.gestor_matricula, sen_at):
                            st.error("Senha atual incorreta.")
                        elif len(sen_nova) < 6:
                            st.warning("A nova senha deve ter no mínimo 6 caracteres.")
                        elif sen_nova != sen_nov2:
                            st.error("As senhas não coincidem.")
                        else:
                            if gestor_alterar_senha(st.session_state.gestor_matricula, sen_nova):
                                st.success("✅ Senha alterada com sucesso!")
                                time.sleep(1)
                                st.session_state.gestor_tela = 'logado'
                                st.rerun()

                # ── TELA DE CONFIGURAR METAS ──────────────────
                elif st.session_state.gestor_tela == 'configurar_metas':
                    _nome_g    = st.session_state.gestor_nome
                    _servico_g = st.session_state.gestor_servico

                    st.markdown("""
                    <div style="text-align:center; margin-bottom:8px;">
                        <p style="font-size:32px; margin:0;">🎯</p>
                        <p style="font-size:20px; font-weight:900; color:#0b2a6f; margin:4px 0;">Configurar Metas</p>
                        <p style="font-size:12px; color:#888; margin:0;">
                            Defina o valor-alvo e a margem de tolerância de cada indicador.<br>
                            As cores dos operadores serão atualizadas automaticamente.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Legenda visual
                    st.markdown("""
                    <div style="display:flex; gap:20px; justify-content:center;
                                background:#f8f9fa; border-radius:10px; padding:10px 16px;
                                margin:12px 0 20px 0;">
                        <span style="font-size:12px; color:#28a745; font-weight:700;">🟢 ≥ Meta</span>
                        <span style="font-size:12px; color:#ffc107; font-weight:700;">🟡 Dentro da margem</span>
                        <span style="font-size:12px; color:#dc3545; font-weight:700;">🔴 Fora da meta</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # Carrega metas atuais (do banco ou defaults)
                    metas_atuais = carregar_metas_gestor(_nome_g, _servico_g)

                    # Configs de exibição por métrica
                    _META_LABELS = {
                        'Aderencia':      ('📅 Aderência',      False, '%'),
                        'Resolutividade': ('✅ Resolutividade',  False, '%'),
                        'TMA Voz':        ('🎙️ TMA Voz',         True,  'min'),
                        'Pesquisa':       ('⭐ Pesquisa',        False, ''),
                        'Silencio':       ('🔇 Silêncio',        True,  '%'),
                        'Pausa Total':    ('⏸️ Pausa Total',     True,  '%'),
                        'Absenteismo':    ('🚫 Absenteísmo',     True,  '%'),
                        'Produtividade':  ('⚡ Produtividade',   False, '%'),
                        'Transf':         ('🔁 Transferência',   False, '%'),
                        'ShortCall':      ('📵 ShortCall',       True,  '%'),
                    }

                    novos_valores = {}
                    for metrica, (label, menor_melhor, unidade) in _META_LABELS.items():
                        conf_atual = metas_atuais.get(metrica, METAS_BASE[metrica])
                        direcao = "🔻 menor = melhor" if menor_melhor else "🔺 maior = melhor"

                        st.markdown(f"""
                        <div style="background:white; border-radius:12px; padding:14px 18px 10px 18px;
                                    margin-bottom:10px; box-shadow:0 2px 8px rgba(0,0,0,0.06);
                                    border-left: 5px solid #1a6fc4;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                                <p style="margin:0; font-size:14px; font-weight:800; color:#0b2a6f;">{label}</p>
                                <span style="font-size:10px; color:#aaa; font-weight:600;">{direcao}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        col_v, col_m = st.columns(2)
                        with col_v:
                            novo_val = st.number_input(
                                f"Meta ({unidade if unidade else 'valor'})",
                                min_value=0.0, max_value=999.0,
                                value=float(conf_atual['valor']),
                                step=0.5,
                                format="%.2f",
                                key=f"meta_val_{metrica}"
                            )
                        with col_m:
                            novo_mar = st.number_input(
                                "Margem de tolerância",
                                min_value=0.0, max_value=100.0,
                                value=float(conf_atual['margem']),
                                step=0.5,
                                format="%.2f",
                                key=f"meta_mar_{metrica}"
                            )

                        # Preview das faixas em tempo real
                        if menor_melhor:
                            ok_str  = f"≤ {novo_val:.2f}{unidade}"
                            atc_str = f"{novo_val:.2f} – {novo_val + novo_mar:.2f}{unidade}"
                            out_str = f"> {novo_val + novo_mar:.2f}{unidade}"
                        else:
                            ok_str  = f"≥ {novo_val:.2f}{unidade}"
                            atc_str = f"{novo_val - novo_mar:.2f} – {novo_val:.2f}{unidade}"
                            out_str = f"< {novo_val - novo_mar:.2f}{unidade}"

                        st.markdown(f"""
                        <div style="display:flex; gap:10px; margin:-4px 0 6px 0; flex-wrap:wrap;">
                            <span style="font-size:11px; background:rgba(40,167,69,0.12); color:#28a745;
                                          border-radius:6px; padding:3px 10px; font-weight:700;">🟢 {ok_str}</span>
                            <span style="font-size:11px; background:rgba(255,193,7,0.15); color:#b88a00;
                                          border-radius:6px; padding:3px 10px; font-weight:700;">🟡 {atc_str}</span>
                            <span style="font-size:11px; background:rgba(220,53,69,0.10); color:#dc3545;
                                          border-radius:6px; padding:3px 10px; font-weight:700;">🔴 {out_str}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        novos_valores[metrica] = {
                            **METAS_BASE[metrica],
                            'valor':  novo_val,
                            'margem': novo_mar,
                        }

                    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                    col_salv, col_rest, col_can = st.columns(3)

                    if col_salv.button("💾 Salvar metas", use_container_width=True):
                        if salvar_metas_gestor(_nome_g, _servico_g, novos_valores):
                            st.success("✅ Metas salvas! Os operadores já verão as novas cores.")
                            time.sleep(1.2)
                            st.session_state.gestor_tela = 'logado'
                            st.rerun()

                    if col_rest.button("↺ Restaurar padrão", use_container_width=True):
                        if salvar_metas_gestor(_nome_g, _servico_g, {k: v.copy() for k, v in METAS_BASE.items()}):
                            st.success("✅ Metas restauradas para o padrão!")
                            time.sleep(1.2)
                            st.session_state.gestor_tela = 'logado'
                            st.rerun()

                    if col_can.button("← Cancelar", use_container_width=True):
                        st.session_state.gestor_tela = 'logado'
                        st.rerun()

        # ══════════════════════════════════════════════════
        # LOGADO — área de upload
        # ══════════════════════════════════════════════════
        else:
            nome_sup    = st.session_state.gestor_nome
            servico_sup = st.session_state.gestor_servico

            # Banner do gestor logado
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0b2a6f,#1a6fc4);
                        border-radius:14px; padding:18px 24px; margin-bottom:24px;
                        display:flex; align-items:center; justify-content:space-between;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <span style="font-size:28px;">🗂️</span>
                    <div>
                        <p style="margin:0; color:rgba(255,255,255,0.6); font-size:11px;
                                  letter-spacing:2px; text-transform:uppercase;">Gestor logado</p>
                        <p style="margin:0; color:white; font-size:18px; font-weight:900;">{nome_sup}</p>
                        <p style="margin:0; color:rgba(255,255,255,0.65); font-size:12px;">{servico_sup}</p>
                    </div>
                </div>
                <p style="margin:0; color:rgba(255,255,255,0.45); font-size:11px;">Mat. {st.session_state.gestor_matricula}</p>
            </div>
            """, unsafe_allow_html=True)

            # Botões alterar senha + configurar metas
            col_alt, col_metas_btn, _ = st.columns([1, 1, 3])
            if col_alt.button("🔑 Alterar senha"):
                st.session_state.gestor_tela = 'alterar_senha'
                st.session_state.gestor_logado = False
                st.rerun()
            if col_metas_btn.button("🎯 Configurar Metas"):
                st.session_state.gestor_tela = 'configurar_metas'
                st.session_state.gestor_logado = False
                st.rerun()

            st.divider()

            # ── Três uploaders rotulados ────────────────────────────
            col_up1, col_up2, col_up3 = st.columns(3)

            with col_up1:
                st.markdown("""
                <div style="background:#f0f4ff; border-radius:12px; padding:12px 16px 6px 16px;
                            border-left:4px solid #1a6fc4; margin-bottom:10px; min-height:80px;">
                    <p style="margin:0; font-size:12px; font-weight:800; color:#0b2a6f;
                              letter-spacing:1.5px; text-transform:uppercase;">
                        📊 Métricas em Geral
                    </p>
                    <p style="margin:4px 0 0 0; font-size:12px; color:#666;">
                        Planilha do BI com Aderência, TMA, Pausas, etc.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                arquivo_bi = st.file_uploader(
                    "Enviar planilha de Métricas Gerais (.xlsx)",
                    type=["xlsx"],
                    key=f"upload_bi_{nome_sup}_{servico_sup}",
                    label_visibility="collapsed"
                )

            with col_up2:
                st.markdown("""
                <div style="background:#f0fff4; border-radius:12px; padding:12px 16px 6px 16px;
                            border-left:4px solid #28a745; margin-bottom:10px; min-height:80px;">
                    <p style="margin:0; font-size:12px; font-weight:800; color:#0b2a6f;
                              letter-spacing:1.5px; text-transform:uppercase;">
                        🎯 FCR e Direcionadas
                    </p>
                    <p style="margin:4px 0 0 0; font-size:12px; color:#666;">
                        Planilha com % FCR (1° Contato) e % Direcionado.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                arquivo_fcr = st.file_uploader(
                    "Enviar planilha de FCR (.xlsx)",
                    type=["xlsx"],
                    key=f"upload_fcr_{nome_sup}_{servico_sup}",
                    label_visibility="collapsed"
                )

            with col_up3:
                st.markdown("""
                <div style="background:#fff8f0; border-radius:12px; padding:12px 16px 6px 16px;
                            border-left:4px solid #fd7e14; margin-bottom:10px; min-height:80px;">
                    <p style="margin:0; font-size:12px; font-weight:800; color:#0b2a6f;
                              letter-spacing:1.5px; text-transform:uppercase;">
                        🔁 Rechamada
                    </p>
                    <p style="margin:4px 0 0 0; font-size:12px; color:#666;">
                        Planilha com % Rechamada por agente.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                arquivo_rechamada = st.file_uploader(
                    "Enviar planilha de Rechamada (.xlsx)",
                    type=["xlsx"],
                    key=f"upload_rechamada_{nome_sup}_{servico_sup}",
                    label_visibility="collapsed"
                )

            # ── Processar arquivo de Métricas Gerais ──────────────
            if arquivo_bi is not None:
                with st.spinner("Processando métricas gerais..."):
                    try:
                        df_bi_raw = pd.read_excel(arquivo_bi, dtype=str)
                        sucesso = upsert_supabase(df_bi_raw, nome_sup, servico_sup)
                        if sucesso:
                            carregar_dados_supervisor.clear()
                            st.success(f"✅ **{arquivo_bi.name}** — Métricas gerais enviadas com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo de métricas: {e}")

            # ── Processar arquivo de FCR ───────────────────────────
            if arquivo_fcr is not None:
                with st.spinner("Processando FCR e Direcionadas..."):
                    try:
                        df_fcr_raw = pd.read_excel(arquivo_fcr, dtype=str)
                        sucesso_fcr = upsert_supabase_fcr(df_fcr_raw, nome_sup, servico_sup)
                        if sucesso_fcr:
                            st.success(f"✅ **{arquivo_fcr.name}** — FCR e Direcionadas enviados com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo FCR: {e}")

            # ── Processar arquivo de Rechamada ─────────────────────
            if arquivo_rechamada is not None:
                with st.spinner("Processando Rechamada..."):
                    try:
                        df_rec_raw = pd.read_excel(arquivo_rechamada, dtype=str)
                        sucesso_rec = upsert_supabase_rechamada(df_rec_raw, nome_sup, servico_sup)
                        if sucesso_rec:
                            st.success(f"✅ **{arquivo_rechamada.name}** — Rechamada enviada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo de Rechamada: {e}")

            if arquivo_bi is None and arquivo_fcr is None and arquivo_rechamada is None:
                st.markdown("""
                <div style='text-align:center; padding: 50px 0; color:#aaa;'>
                    <p style='font-size:44px;'>📤</p>
                    <p style='font-size:15px;'>Envie o arquivo <b>.xlsx</b> exportado pelo BI<br>para atualizar os dados da equipe.</p>
                </div>
                """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    # ÁREA DO OPERADOR  (busca automática por matrícula)
    # ══════════════════════════════════════════════════
    elif st.session_state.servico == "Operador":

        _col_v2, _ = st.columns([1, 5])
        with _col_v2:
            if st.button("← Voltar", use_container_width=True):
                st.session_state.servico = None
                st.session_state.pop('op_supervisor', None)
                st.session_state.pop('op_servico', None)
                st.session_state.pop('op_nome', None)
                st.rerun()

        if not st.session_state.get('op_supervisor'):
            _, _col_login, _ = st.columns([1, 2, 1])
            with _col_login:
                st.markdown("""
                <div style="text-align:center; padding:30px 0 20px 0;">
                    <p style="font-size:11px; font-weight:700; color:#1a6fc4;
                              letter-spacing:3px; text-transform:uppercase; margin:0 0 8px 0;">
                        ACESSO DO OPERADOR
                    </p>
                    <p style="font-size:24px; font-weight:900; color:#0b2a6f; margin:0 0 24px 0;">
                        Digite sua matrícula
                    </p>
                </div>
                """, unsafe_allow_html=True)
                mat_input = st.text_input("Matrícula", placeholder="Ex: 1035323", label_visibility="collapsed")
                buscar = st.button("🔍 Buscar", use_container_width=True)

            if buscar and mat_input:
                sup, svc, nome_op = buscar_supervisor_por_matricula(mat_input.strip())
                if sup:
                    st.session_state.op_supervisor  = sup
                    st.session_state.op_servico     = svc
                    st.session_state.op_nome        = nome_op or mat_input.strip()
                    st.session_state.op_matricula   = mat_input.strip()
                    st.rerun()
                else:
                    st.session_state.pop('op_supervisor', None)
                    st.warning("⚠️ Matrícula não encontrada. Verifique o número ou aguarde o gestor enviar a planilha.")

        if st.session_state.get('op_supervisor'):
            sup = st.session_state.op_supervisor
            svc = st.session_state.op_servico
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0b2a6f,#1a6fc4);
                        border-radius:14px; padding:16px 22px; margin:14px 0 20px 0;
                        display:flex; align-items:center; gap:16px;">
                <span style="font-size:28px;">👤</span>
                <div>
                    <p style="margin:0; color:rgba(255,255,255,0.6); font-size:11px;
                              letter-spacing:2px; text-transform:uppercase;">Operador identificado</p>
                    <p style="margin:2px 0; color:white; font-size:17px; font-weight:900;">{st.session_state.op_nome}</p>
                    <p style="margin:0; color:rgba(255,255,255,0.65); font-size:12px;">
                        Equipe: <b>{sup}</b> &nbsp;|&nbsp; Serviço: <b>{svc}</b>
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_trocar, _ = st.columns([1, 5])
            if col_trocar.button("🔄 Trocar operador", use_container_width=True):
                st.session_state.pop('op_supervisor', None)
                st.session_state.pop('op_servico', None)
                st.session_state.pop('op_nome', None)
                st.session_state.pop('op_matricula', None)
                st.rerun()

            mat_input = st.session_state.get('op_matricula', sup)
            df, col_op, col_mat = carregar_dados_supervisor(sup, svc)
            if df.empty:
                st.warning("Nenhum dado disponível ainda. Aguarde o gestor enviar a planilha.")
            else:
                # Carrega metas customizadas do gestor desta equipe
                metas_op = carregar_metas_gestor(sup, svc)

                # Exibe data da última atualização feita pelo gestor
                if 'atualizado_em' in df.columns:
                    try:
                        ultima_atualizacao = pd.to_datetime(df['atualizado_em']).max()
                        ultima_atualizacao = ultima_atualizacao.tz_convert('America/Fortaleza')
                        data_fmt = ultima_atualizacao.strftime('%d/%m/%Y às %H:%M')
                        st.markdown(f"""
                        <div style="display:flex; align-items:center; gap:8px;
                                    background:#f0f4ff; border-radius:10px;
                                    padding:10px 16px; margin-bottom:14px;
                                    border-left:4px solid #1a6fc4;">
                            <span style="font-size:18px;">🗓️</span>
                            <p style="margin:0; font-size:13px; color:#444;">
                                Métricas atualizadas pelo gestor em
                                <b style="color:#0b2a6f;">{data_fmt}</b>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                    except:
                        pass
                exibir_painel(df, col_op, col_mat, chave_aba=f"aba_op_{mat_input}", mat_operador=mat_input, metas=metas_op)
