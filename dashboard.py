import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. TOOLKIT DE CSS AVANÇADO
# Este bloco força a largura dos botões, cria a animação de hover e ajusta a sidebar
st.markdown("""
    <style>
    /* Expande a área de conteúdo para as bordas */
    .block-container {
        max-width: 96% !important;
        padding-top: 2rem !important;
    }

    /* BOTÕES DO LOBBY: Esticados e Retangulares */
    /* Segmentamos apenas os botões dentro das colunas (Lobby) */
    div[data-testid="column"] div.stButton > button {
        width: 100% !important;
        height: 7em !important;
        font-size: 22px !important;
        font-weight: bold !important;
        border-radius: 15px !important;
        background-color: #f8f9fa !important;
        border: 1px solid #dee2e6 !important;
        color: #495057 !important;
        transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05) !important;
    }

    /* Animação de elevação e brilho no Hover */
    div[data-testid="column"] div.stButton > button:hover {
        transform: translateY(-8px) !important;
        box-shadow: 0 12px 20px rgba(0,0,0,0.1) !important;
        border-color: #004a99 !important;
        color: #004a99 !important;
        background-color: #ffffff !important;
    }

    /* BOTÃO VOLTAR (SIDEBAR): Pequeno e Discreto */
    section[data-testid="stSidebar"] div.stButton > button {
        height: 35px !important;
        width: 120px !important;
        font-size: 14px !important;
        font-weight: normal !important;
        border-radius: 8px !important;
        margin-top: 20px !important;
    }

    /* Ajuste de Tabs para ocupar mais espaço */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. REGRAS DE NEGÓCIO E METAS
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'ShortCall': {'valor': 5.0, 'margem': 2.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False}
}

MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 5. FUNÇÕES COMPLEXAS DE TRATAMENTO
def limpar_e_converter(valor):
    """Trata strings sujas, porcentagens e valores nulos de forma robusta."""
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    # Remove qualquer caractere que não seja número, vírgula ou ponto
    s = re.sub(r'[^\d,.-]', '', s)
    if s in ['', '0', '00', 'nan', 'none']: return None
    try:
        return float(s.replace(',', '.'))
    except: return None

def tempo_para_minutos(valor):
    """Converte formatos HH:MM:SS ou MM:SS para float (minutos)."""
    if pd.isna(valor): return None
    s = str(valor).strip()
    if s.lower() in ['none', '', 'nan', '00:00:00', '0']: return None
    try:
        partes = s.split(':')
        if len(partes) == 3: # HH:MM:SS
            return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: # MM:SS
            return int(partes[0]) + int(partes[1]) / 60
        return float(s.replace(',', '.'))
    except: return None

def definir_cor_kpi(valor, metrica, metas_dict):
    if valor is None: return "#6c757d"
    meta = metas_dict.get(metrica)
    v, m, tol = valor, meta['valor'], meta['margem']
    if meta['menor_melhor']:
        return "#28a745" if v <= m else ("#ffc107" if v <= m + tol else "#dc3545")
    return "#28a745" if v >= m else ("#ffc107" if v >= m - tol else "#dc3545")

def card_metric(label, valor, cor="#333", icon=""):
    fmt = f"{valor:.2f}" if isinstance(valor, (int, float)) else "N/A"
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 8px solid {cor}; 
             box-shadow: 2px 2px 10px rgba(0,0,0,0.08); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 11px; color: #888; font-weight: bold;">{label.upper()}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 22px;">{icon} {fmt}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        sid = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Identificação de colunas críticas
        c_op = next((c for c in df.columns if 'operador' in c.lower()), df.columns[0])
        c_mat = next((c for c in df.columns if 'matricula' in c.lower()), df.columns[1])

        # Criação de colunas numéricas tratadas
        for m in list(METAS_BASE.keys()) + ['Pausa Total']:
            col_origem = next((c for c in df.columns if m.lower() in c.lower()), None)
            if col_origem:
                func = tempo_para_minutos if ('TMA' in m or 'Pausa' in m) else limpar_e_converter
                df[f'{m}_num'] = df[col_origem].apply(func)
            else:
                df[f'{m}_num'] = None
        return df, c_op, c_mat
    except Exception as e:
        st.error(f"Erro na Planilha: {e}")
        return None, None, None

# --- NAVEGAÇÃO LOBBY ---
if st.session_state.servico is None:
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Criamos colunas para esticar os botões horizontalmente
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🏢 SAC NDI"): st.session_state.servico = "SAC NDI"; st.rerun()
    with c2:
        if st.button("🏦 SAC PPO"): st.session_state.servico = "SAC PPO"; st.rerun()
    with c3:
        if st.button("🏥 SAC HAPVIDA"): st.session_state.servico = "SAC HAPVIDA"; st.rerun()
else:
    # --- INTERFACE INTERNA ---
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        opcoes = {
            "SAC NDI": ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"],
            "SAC PPO": ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"],
            "SAC HAPVIDA": ["Selecione...", "Equipe Hapvida"]
        }
        supervisor = st.selectbox("Supervisor:", opcoes[st.session_state.servico])
        if st.button("⬅️ Voltar"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        if df is not None:
            # Cálculo de metas de pausa específicas
            metas_s = METAS_BASE.copy()
            pausas = {"Carla": 17.27, "Ellen": 19.06, "Alex": 17.17, "Magno": 19.18}
            meta_p = next((v for k, v in pausas.items() if k in supervisor), 21.75)
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tab_ind, tab_rank, tab_saude = st.tabs(["👤 INDIVIDUAL", "🏆 RANKING", "📊 SAÚDE"])

            with tab_ind:
                mat = st.text_input("Digite sua Matrícula:")
                if mat:
                    r = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not r.empty:
                        item = r.iloc[0]
                        st.subheader(f"Dashboard: {item[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            card_metric("Aderência", item['Aderencia_num'], definir_cor_kpi(item['Aderencia_num'], 'Aderencia', metas_s))
                            card_metric("Pesquisa", item['Pesquisa_num'], definir_cor_kpi(item['Pesquisa_num'], 'Pesquisa', metas_s), "⭐")
                        with c2:
                            card_metric("Resolutividade", item['Resolutividade_num'], definir_cor_kpi(item['Resolutividade_num'], 'Resolutividade', metas_s))
                        with c3:
                            card_metric("TMA Voz", item['TMA Voz_num'], definir_cor_kpi(item['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                    else: st.warning("Matrícula não encontrada.")

            with tab_rank:
                for m, v in metas_s.items():
                    # Filtragem para o Ranking: Remove Equipe, Backoffice e Nulos
                    df_r = df[(df[col_op].str.strip().upper() != 'EQUIPE') & 
                              (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                              (df[f'{m}_num'].notna())].copy()
                    if not df_r.empty:
                        st.markdown(f"#### Melhores em {m}")
                        res = df_r.nsmallest(3, f'{m}_num') if v['menor_melhor'] else df_r.nlargest(3, f'{m}_num')
                        cols = st.columns(3)
                        for i, (_, row) in enumerate(res.iterrows()):
                            with cols[i]: card_metric(f"{i+1}º Lugar", row[col_op], definir_cor_kpi(row[f'{m}_num'], m, metas_s), ["🥇","🥈","🥉"][i])
                    st.divider()

            with tab_saude:
                sel = st.selectbox("Escolha a Métrica:", list(metas_s.keys()))
                # Filtro que remove "Nones" e evita o erro da Ludmilla
                df_s = df[(df[col_op].str.strip().upper() != 'EQUIPE') & 
                          (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                          (df[f'{sel}_num'].notna())].copy()
                
                if not df_s.empty:
                    mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                    df_s['Status'] = df_s[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                    
                    c1, c2 = st.columns([1, 1])
                    with c1:
                        fig = px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    with c2:
                        st.dataframe(df_s[[col_op, f'{sel}_num', 'Status']], hide_index=True, use_container_width=True)
                else: st.info("Sem dados para esta métrica.")
