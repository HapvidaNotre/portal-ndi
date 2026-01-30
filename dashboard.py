import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA (Deve ser a primeira linha)
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CSS AVANÇADO (CORREÇÃO DE TAMANHO E LEIAUTE)
st.markdown("""
    <style>
    /* Aumenta a largura útil da página para caber os botões gigantes */
    .block-container {
        max-width: 98% !important;
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    /* --- ESTILO DOS BOTÕES DO LOBBY (MENU PRINCIPAL) --- */
    /* Alvo: Botões que estão na área principal (não na sidebar) */
    div[data-testid="stAppViewContainer"] div[data-testid="column"] button {
        width: 100% !important;
        height: 320px !important;  /* FORÇA UMA ALTURA GIGANTE */
        font-size: 36px !important; /* AUMENTA A FONTE */
        font-weight: 800 !important;
        text-transform: uppercase;
        border-radius: 30px !important;
        /* Gradiente sutil para dar volume */
        background: linear-gradient(135deg, #ffffff 0%, #f0f2f6 100%) !important;
        border: 2px solid #e0e0e0 !important;
        color: #0f2c4c !important; /* Azul escuro */
        box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important;
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        
        /* Centraliza o texto e ícone */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    /* Efeito ao passar o mouse (Hover) nos botões gigantes */
    div[data-testid="stAppViewContainer"] div[data-testid="column"] button:hover {
        transform: translateY(-10px) scale(1.01) !important;
        border-color: #004a99 !important;
        color: #004a99 !important;
        box-shadow: 0 20px 40px rgba(0, 74, 153, 0.2) !important;
        background: #ffffff !important;
    }

    /* --- ESTILO DO BOTÃO VOLTAR (SIDEBAR) --- */
    /* Força o botão da sidebar a ser pequeno, ignorando o estilo acima */
    section[data-testid="stSidebar"] button {
        height: 45px !important;
        width: 100% !important;
        font-size: 16px !important;
        border-radius: 8px !important;
        background-color: #e9ecef !important;
        color: #333 !important;
        box-shadow: none !important;
        margin-top: 20px !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #dee2e6 !important;
        border-color: #adb5bd !important;
        transform: none !important;
    }

    /* Ajuste visual das abas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# 3. ESTADO DA SESSÃO
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 4. DEFINIÇÃO DE METAS
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

# 5. FUNÇÕES ROBUSTAS DE TRATAMENTO DE DADOS
def limpar_valor(valor, is_time=False):
    """
    Converte valores sujos, porcentagens e strings 'None' para números ou None real.
    """
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    
    # LISTA NEGRA: Se for qualquer um destes, retorna None imediatamente
    if s in ['none', '', 'nan', 'null', '#n/a', '-', '0', '0.0', '0%']:
        return None

    # Tratamento de Tempo (TMA/Pausa)
    if is_time and ':' in s:
        try:
            partes = s.split(':')
            # HH:MM:SS ou MM:SS
            if len(partes) == 3:
                return int(partes[0]) * 60 + int(partes[1]) + float(partes[2]) / 60
            elif len(partes) == 2:
                return int(partes[0]) + float(partes[1]) / 60
        except:
            return None
    
    # Tratamento de Números Comuns
    try:
        # Remove R$, %, espaços e letras
        limpo = re.sub(r'[^\d,.-]', '', s)
        # Troca vírgula por ponto
        limpo = limpo.replace(',', '.')
        val = float(limpo)
        return val if val != 0 else None
    except:
        return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        sheet_id = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Localiza colunas principais
        col_op = next((c for c in df.columns if 'operador' in c.lower()), df.columns[0])
        col_mat = next((c for c in df.columns if 'matricula' in c.lower()), df.columns[1])

        # Cria colunas numéricas limpas
        for metrica in list(METAS_BASE.keys()) + ['Pausa Total']:
            col_origem = next((c for c in df.columns if metrica.lower() in c.lower()), None)
            if col_origem:
                is_time = 'TMA' in metrica or 'Pausa' in metrica
                df[f'{metrica}_num'] = df[col_origem].apply(lambda x: limpar_valor(x, is_time))
            else:
                df[f'{metrica}_num'] = None
        
        return df, col_op, col_mat
    except Exception as e:
        st.error(f"Erro ao conectar com a planilha: {e}")
        return None, None, None

def definir_cor(valor, metrica, metas):
    if valor is None: return "#6c757d"
    m = metas.get(metrica)
    if not m: return "#333"
    
    v_meta, margem, menor_melhor = m['valor'], m['margem'], m['menor_melhor']
    
    if menor_melhor:
        if valor <= v_meta: return "#28a745" # Verde
        if valor <= v_meta + margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= v_meta: return "#28a745"
        if valor >= v_meta - margem: return "#ffc107"
        return "#dc3545"

def exibir_kpi(label, valor, cor, icon=""):
    v_str = f"{valor:.2f}" if isinstance(valor, (float, int)) else "N/A"
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border-left: 8px solid {cor}; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px;">
        <span style="font-size: 12px; color: #888; font-weight: 700; text-transform: uppercase;">{label}</span>
        <h3 style="margin: 5px 0 0 0; color: {cor}; font-size: 24px;">{icon} {v_str}</h3>
    </div>
    """, unsafe_allow_html=True)

# --- NAVEGAÇÃO ---

if st.session_state.servico is None:
    # --- TELA: LOBBY (BOTÕES GIGANTES) ---
    st.markdown("<br><h1 style='text-align: center; color: #0f2c4c; font-size: 42px;'>🚀 PORTAL DE PERFORMANCE NDI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666; margin-bottom: 40px;'>Selecione o serviço para acessar os indicadores</p>", unsafe_allow_html=True)
    
    # Grid de 3 colunas para os botões
    c1, c2, c3 = st.columns(3)
    
    # Botões agora respondem ao CSS "height: 320px !important" definido acima
    with c1:
        if st.button("🏢\nSAC NDI"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with c2:
        if st.button("🏦\nSAC PPO"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with c3:
        if st.button("🏥\nSAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    # --- TELA: DASHBOARD (SIDEBAR E CONTEÚDO) ---
    with st.sidebar:
        st.markdown(f"## 📍 {st.session_state.servico}")
        
        # Menu dinâmico de supervisores
        if st.session_state.servico == "SAC NDI":
            opts = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            opts = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            opts = ["Selecione...", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Selecione o Supervisor:", opts)
        
        st.write("---")
        # Botão Voltar (Estilizado pequeno pelo CSS)
        if st.button("⬅️ Voltar ao Lobby"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        
        if df is not None:
            # Definição das metas de pausa por supervisor
            metas_locais = METAS_BASE.copy()
            p_map = {"Carla": 17.27, "Ellen": 19.06, "Alex": 17.17, "Magno": 19.18}
            meta_pausa = next((v for k, v in p_map.items() if k in supervisor), 21.75)
            metas_locais['Pausa Total'] = {'valor': meta_pausa, 'margem': 3.0, 'menor_melhor': True}

            t1, t2, t3 = st.tabs(["👤 INDIVIDUAL", "🏆 RANKING", "📊 SAÚDE DA EQUIPE"])

            # --- ABA INDIVIDUAL ---
            with t1:
                mat = st.text_input("🔍 Digite a Matrícula do Operador:", placeholder="Ex: 123456")
                if mat:
                    res = df[df[col_mat].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        dado = res.iloc[0]
                        st.subheader(f"Analítico: {dado[col_op]}")
                        g1, g2, g3 = st.columns(3)
                        with g1:
                            exibir_kpi("Aderência", dado['Aderencia_num'], definir_cor(dado['Aderencia_num'], 'Aderencia', metas_locais))
                        with g2:
                            exibir_kpi("Resolutividade", dado['Resolutividade_num'], definir_cor(dado['Resolutividade_num'], 'Resolutividade', metas_locais))
                        with g3:
                            exibir_kpi("TMA Voz", dado['TMA Voz_num'], definir_cor(dado['TMA Voz_num'], 'TMA Voz', metas_locais), "⏱️")
                    else:
                        st.warning("⚠️ Matrícula não encontrada na base desta equipe.")

            # --- ABA RANKING ---
            with t2:
                metrica_rank = st.selectbox("Ordenar por:", list(metas_locais.keys()), key="rank_sel")
                # Filtra Backoffice e Equipe
                df_r = df[
                    (df[col_op].str.strip().upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{metrica_rank}_num'].notna())
                ].copy()
                
                if not df_r.empty:
                    eh_menor = metas_locais[metrica_rank]['menor_melhor']
                    top3 = df_r.nsmallest(3, f'{metrica_rank}_num') if eh_menor else df_r.nlargest(3, f'{metrica_rank}_num')
                    
                    st.markdown(f"### 🏆 Top 3 - {metrica_rank}")
                    cols = st.columns(3)
                    for i, (idx, row) in enumerate(top3.iterrows()):
                        with cols[i]:
                            cor = definir_cor(row[f'{metrica_rank}_num'], metrica_rank, metas_locais)
                            medalhas = ["🥇", "🥈", "🥉"]
                            exibir_kpi(f"{i+1}º Lugar", row[col_op], cor, medalhas[i])
                    st.divider()
                    st.dataframe(df_r[[col_op, col_mat, f'{metrica_rank}_num']].sort_values(by=f'{metrica_rank}_num', ascending=eh_menor), hide_index=True, use_container_width=True)

            # --- ABA SAÚDE (CORREÇÃO DO BUG 'NONE') ---
            with t3:
                sel_saude = st.selectbox("Análise Geral:", list(metas_locais.keys()), key="saude_sel")
                
                # --- FILTRO CRÍTICO ---
                # Remove Equipe, Backoffice e, PRINCIPALMENTE, quem tem valor Nulo (None)
                df_s = df[
                    (df[col_op].str.strip().upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{sel_saude}_num'].notna()) # <--- ISSO REMOVE LUDMILA SE ELA TIVER 'NONE'
                ].copy()

                if not df_s.empty:
                    meta_val = metas_locais[sel_saude]['valor']
                    meta_inv = metas_locais[sel_saude]['menor_melhor']
                    
                    # Lógica de Classificação
                    df_s['Status'] = df_s[f'{sel_saude}_num'].apply(
                        lambda x: 'Dentro da Meta' if (x <= meta_val if meta_inv else x >= meta_val) else 'Fora da Meta'
                    )
                    
                    c_pie, c_tab = st.columns([1, 1.5])
                    with c_pie:
                        fig = px.pie(df_s, names='Status', hole=0.6, color='Status',
                                     color_discrete_map={'Dentro da Meta':'#28a745', 'Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with c_tab:
                        # Mostra coluna original para conferência visual, mas a cor vem do cálculo numérico
                        col_display = next((c for c in df.columns if sel_saude.lower() in c.lower()), sel_saude)
                        st.dataframe(
                            df_s[[col_op, col_display, 'Status']].style.applymap(
                                lambda v: f"color: {'#28a745' if v=='Dentro da Meta' else '#dc3545'}", subset=['Status']
                            ), 
                            use_container_width=True, 
                            hide_index=True
                        )
                else:
                    st.info("ℹ️ Não há dados válidos para calcular a saúde desta métrica (todos os operadores estão com valor zerado ou nulo).")
