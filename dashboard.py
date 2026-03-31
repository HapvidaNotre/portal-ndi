import streamlit as st
import pandas as pd
import time
from supabase import create_client, Client

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
    'Transf':        {'valor': 10.0,  'margem': 2.0, 'menor_melhor': True,  'unidade': '%'},
    'ShortCall':     {'valor': 5.0,   'margem': 1.0, 'menor_melhor': True,  'unidade': '%'},
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
    # Pausas
    'pausa produtiva':     'pausa_produtiva',
    'pausas produtivas':   'pausa_produtiva',
    '% pausa produtiva':   'pausa_produtiva',
    'pausa improdutiva':   'pausa_improdutiva',
    'pausas improdutivas': 'pausa_improdutiva',
    '% pausa improdutiva': 'pausa_improdutiva',
    'pausa total':         'pausa_total',
}

# ---------- FUNÇÕES UTILITÁRIAS ----------
def definir_cor_kpi(valor_num, metrica):
    if valor_num is None or pd.isna(valor_num): return "#999"
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

def _limpar_num(val):
    try:
        return float(str(val).replace('%','').replace(',','.').strip())
    except:
        return None

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
                elif col_db in ('operador',):
                    rec[col_db] = str(val).strip() if not pd.isna(val) else None
                else:
                    rec[col_db] = _limpar_num(val)

        # Recalcula pausa total
        prod   = rec.get('pausa_produtiva')   or 0
        improd = rec.get('pausa_improdutiva') or 0
        rec['pausa_total'] = round((prod or 0) + (improd or 0), 2)

        rec['atualizado_em'] = pd.Timestamp.now(tz='UTC').isoformat()

        mat = rec.get('matricula')
        if mat and str(mat).strip() not in ('', 'nan', 'None'):
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

    supabase.table("performance_operadores").upsert(
        registros_limpos,
        on_conflict="matricula,supervisor,servico"
    ).execute()

    return True

# ---------- LEITURA DO SUPABASE ----------
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
    })

    # Garante colunas de display formatadas para cada métrica
    for metrica, conf in METAS_BASE.items():
        col_num = f'{metrica}_num'
        if col_num in df.columns:
            df[metrica] = df[col_num].apply(
                lambda x: f"{x}{conf['unidade']}" if pd.notna(x) else '---'
            )
        else:
            df[metrica] = '---'
            df[col_num] = None

    return df, 'Operador', 'Matricula'

# ---------- HELPER: painel de análise ----------
def exibir_painel(df, col_op, col_mat, chave_aba="aba_ativa"):
    # Para dados vindos do Supabase não há linha de resumo — df_resumo fica vazio
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
    if c2.button("Equipe",     use_container_width=True, key=f"btn_eq_{chave_aba}"):
        st.session_state[chave_aba] = "Equipe";     st.rerun()
    if c3.button("Ranking",    use_container_width=True, key=f"btn_rk_{chave_aba}"):
        st.session_state[chave_aba] = "Ranking";    st.rerun()
    if c4.button("Saúde",      use_container_width=True, key=f"btn_sa_{chave_aba}"):
        st.session_state[chave_aba] = "Saúde";      st.rerun()

    aba = st.session_state[chave_aba]
    st.divider()

    # ── INDIVIDUAL ──────────────────────────────────────
    if aba == "Individual":
        mat = st.text_input("Matrícula")
        if mat:
            res = df[df[col_mat].astype(str) == mat]
            if not res.empty:
                r = res.iloc[0]
                st.subheader(r[col_op])
                # Linha 1: métricas originais
                c1, c2, c3 = st.columns(3)
                with c1:
                    exibir_card("Aderência",     r['Aderencia'],     definir_cor_kpi(r['Aderencia_num'],     'Aderencia'))
                    exibir_card("Silêncio",       r['Silencio'],      definir_cor_kpi(r['Silencio_num'],      'Silencio'))
                with c2:
                    exibir_card("Resolutividade", r['Resolutividade'],definir_cor_kpi(r['Resolutividade_num'],'Resolutividade'))
                    exibir_card("Pausa Total",    r['Pausa Total'],   definir_cor_kpi(r['Pausa Total_num'],   'Pausa Total'))
                with c3:
                    exibir_card("TMA Voz",        r['TMA Voz'],       definir_cor_kpi(r['TMA Voz_num'],       'TMA Voz'))
                    exibir_card("Pesquisa",        r['Pesquisa'],      definir_cor_kpi(r['Pesquisa_num'],      'Pesquisa'))
                # Linha 2: novas métricas
                st.markdown("#### Métricas Adicionais")
                c4, c5, c6, c7 = st.columns(4)
                with c4:
                    exibir_card("Absenteísmo",  r['Absenteismo'],  definir_cor_kpi(r['Absenteismo_num'],  'Absenteismo'))
                with c5:
                    exibir_card("Produtividade",r['Produtividade'],definir_cor_kpi(r['Produtividade_num'],'Produtividade'))
                with c6:
                    exibir_card("Transf",       r['Transf'],       definir_cor_kpi(r['Transf_num'],       'Transf'))
                with c7:
                    exibir_card("ShortCall",    r['ShortCall'],    definir_cor_kpi(r['ShortCall_num'],    'ShortCall'))
            else:
                st.warning("Matrícula não encontrada.")

    # ── EQUIPE ──────────────────────────────────────────
    if aba == "Equipe":
        if not df_eq.empty:
            st.markdown("**Médias da equipe**")
            metricas_eq = list(METAS_BASE.keys())
            cols_eq = st.columns(len(metricas_eq))
            for i, metrica in enumerate(metricas_eq):
                col_num = f'{metrica}_num'
                media = df_eq[col_num].mean() if col_num in df_eq.columns else None
                conf  = METAS_BASE[metrica]
                display = f"{media:.2f}{conf['unidade']}" if media is not None and not pd.isna(media) else '---'
                with cols_eq[i]:
                    exibir_card(metrica, display, definir_cor_kpi(media, metrica))
        else:
            st.warning("Nenhum operador encontrado para calcular médias.")

    # ── RANKING ─────────────────────────────────────────
    if aba == "Ranking":
        metrica_sel = st.selectbox("Métrica", list(METAS_BASE.keys()))
        top = df_eq.dropna(subset=[f'{metrica_sel}_num']).sort_values(
            by=f'{metrica_sel}_num', ascending=METAS_BASE[metrica_sel]['menor_melhor']
        ).head(5)
        for i, (_, row) in enumerate(top.iterrows()):
            exibir_card(f"{i+1}º {row[col_op]}", row[metrica_sel], "#28a745")

    # ── SAÚDE ────────────────────────────────────────────
    if aba == "Saúde":
        metrica_sel = st.selectbox("Selecione a Métrica:", list(METAS_BASE.keys()))
        conf_s  = METAS_BASE[metrica_sel]
        df_saude = df_eq.copy()

        def verificar_status(valor):
            if pd.isna(valor): return "Sem dado"
            if conf_s['menor_melhor']:
                return "Meta OK" if valor <= conf_s['valor'] else "Fora da Meta"
            return "Meta OK" if valor >= conf_s['valor'] else "Fora da Meta"

        df_saude['Status'] = df_saude[f'{metrica_sel}_num'].apply(verificar_status)
        df_saude['Valor']  = df_saude.apply(
            lambda x: x[metrica_sel] if pd.notna(x[f'{metrica_sel}_num']) else "---", axis=1
        )
        tabela = df_saude[[col_mat, col_op, 'Valor', 'Status']].rename(
            columns={col_mat: 'Matrícula', col_op: 'Operador', 'Valor': metrica_sel}
        )
        st.dataframe(tabela, use_container_width=True)

# ---------- HUB ----------
if 'servico' not in st.session_state:
    st.session_state.servico = None

if st.session_state.servico is None:

    # CSS do HUB — estiliza as colunas diretamente pelo DOM
    st.markdown("""
    <style>

    /* Zera padding global da tela principal */
    .stApp { background-color: #f0f4fb !important; }
    section.main > div.block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Coluna ESQUERDA (1ª coluna) */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1) {
        background-color: #ffffff !important;
        padding: 60px 50px 60px 50px !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }

    /* Coluna DIREITA (2ª coluna) */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
        background: linear-gradient(160deg, #0b2a6f 0%, #1a6fc4 100%) !important;
        padding: 40px !important;
        min-height: 100vh !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Botões do HUB */
    div[data-testid="stButton"] > button {
        background-color: #ffffff !important;
        color: #0b2a6f !important;
        border: 2px solid #c5d5f0 !important;
        height: 62px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        width: 100% !important;
        margin-bottom: 4px !important;
        letter-spacing: 0.4px !important;
        box-shadow: 0 2px 8px rgba(11,42,111,0.08) !important;
        transition: all 0.22s ease !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: #0b2a6f !important;
        color: #ffffff !important;
        border-color: #0b2a6f !important;
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0 10px 28px rgba(11,42,111,0.25) !important;
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
            <p style="font-size:11px; font-weight:700; color:#1a6fc4;
                      letter-spacing:3px; text-transform:uppercase; margin:0 0 12px 0;">
                HAPVIDA NOTREDAME INTERMÉDICA
            </p>
            <p style="font-size:28px; font-weight:900; color:#0b2a6f;
                      margin:0 0 6px 0; line-height:1.2;">
                Portal de<br>Performance NDI
            </p>
            <p style="font-size:13px; color:#999; margin:0 0 40px 0;">
                Selecione o serviço para continuar
            </p>
        """, unsafe_allow_html=True)

        if st.button("SAC NDI", use_container_width=True):
            st.session_state.servico = "SAC NDI"; st.rerun()
        if st.button("SAC PPO", use_container_width=True):
            st.session_state.servico = "SAC PPO"; st.rerun()
        if st.button("SAC HAPVIDA", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"; st.rerun()
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("ÁREA DO GESTOR", use_container_width=True):
            st.session_state.servico = "Supervisor"; st.rerun()

    # ── LADO DIREITO: fundo azul + logo ───────────────────────
    with col_right:
        st.markdown("""
            <div style="display:flex; flex-direction:column; align-items:center;
                        justify-content:center; min-height:85vh; gap:24px;">
                <img src="https://raw.githubusercontent.com/HapvidaNotre/portal-ndi/main/logo-hapvida-escudo-2048.png"
                     style="width:210px; filter:drop-shadow(0 6px 24px rgba(0,0,0,0.35));" />
                <p style="color:rgba(255,255,255,0.65); font-size:12px;
                          letter-spacing:3px; text-transform:uppercase; margin:0;">
                    Portal de Performance
                </p>
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
            chave       = f"{nome_sup}_{servico_sup}"
            dados_salvos = st.session_state.supervisor_dados.get(chave)

            st.markdown(f"### 👤 {nome_sup} — {servico_sup}")

            arquivo = st.file_uploader(
                "📂 Enviar planilha do BI (.xlsx)  —  um novo upload substitui os dados atuais",
                type=["xlsx"],
                key=f"upload_{chave}"
            )

            if arquivo is not None:
                with st.spinner("Processando e enviando para o banco..."):
                    try:
                        df_bi_raw = pd.read_excel(arquivo, dtype=str)

                        # Upsert no Supabase
                        sucesso = upsert_supabase(df_bi_raw, nome_sup, servico_sup)

                        if sucesso:
                            # Invalida cache para forçar releitura imediata
                            carregar_dados_supervisor.clear()

                            df_bi, col_op_bi, col_mat_bi = carregar_dados_supervisor(nome_sup, servico_sup)

                            st.session_state.supervisor_dados[chave] = {
                                'df':      df_bi,
                                'col_op':  col_op_bi,
                                'col_mat': col_mat_bi,
                                'arquivo': arquivo.name,
                            }
                            st.success(f"✅ **{arquivo.name}** processado e salvo com sucesso!")
                            dados_salvos = st.session_state.supervisor_dados[chave]

                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo: {e}")

            if dados_salvos:
                st.caption(f"📌 Última atualização: **{dados_salvos['arquivo']}** — faça um novo upload para atualizar.")
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
    # SAC NDI / SAC PPO / SAC HAPVIDA  (Supabase)
    # ══════════════════════════════════════════════════
    else:
        with st.sidebar:
            st.markdown(f"### {st.session_state.servico}")
            if st.session_state.servico == "SAC NDI":
                lista_sup = ["Selecione...","Erik","Davi","Elaine","Sayanne","Beatriz","Aline","Marcelo"]
            elif st.session_state.servico == "SAC PPO":
                lista_sup = ["Selecione...","Ellen","Carla","Magno","Alex"]
            else:
                lista_sup = ["Selecione...","Hapvida"]

            supervisor = st.selectbox("Supervisor:", lista_sup)
            if st.button("Voltar"):
                st.session_state.servico = None
                st.rerun()

        if supervisor != "Selecione...":
            df, col_op, col_mat = carregar_dados_supervisor(supervisor, st.session_state.servico)
            if df.empty:
                st.warning("Nenhum dado encontrado para este supervisor. Aguarde o upload da planilha pelo supervisor.")
            else:
                exibir_painel(df, col_op, col_mat)
