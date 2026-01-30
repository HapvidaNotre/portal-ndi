import streamlit as st
import pandas as pd
import plotly.express as px
import re

# 1. CONFIGURAÇÃO DA PÁGINA (Layout Wide para usar a tela toda)
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CSS AVANÇADO - FORÇA BRUTA PARA DIMENSIONAMENTO
st.markdown("""
    <style>
    /* 1. Ajusta o container principal para dar o máximo de largura possível */
    .block-container {
        max-width: 98% !important;
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }

    /* 2. ESTILO DOS BOTÕES DO LOBBY (As caixas gigantes) */
    /* Seleciona APENAS os botões que estão dentro das colunas principais */
    div[data-testid="column"] button {
        width: 100% !important;        /* Ocupa 100% da largura da coluna vermelha */
        height: 300px !important;      /* Altura fixa bem grande */
        font-size: 32px !important;    /* Texto grande */
        font-weight: 800 !important;
        text-transform: uppercase;
        border-radius: 20px !important;
        
        /* Visual Clean e Profissional */
        background: white !important;
        border: 2px solid #e0e0e0 !important;
        color: #1f3a5f !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05) !important;
        
        /* Centralização */
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }

    /* Efeito ao passar o mouse (Hover) */
    div[data-testid="column"] button:hover {
        border-color: #004a99 !important;
        color: #004a99 !important;
        transform: translateY(-5px) !important;
        box-shadow: 0 10px 25px rgba(0,74,153,0.15) !important;
        background-color: #f8f9fa !important;
    }

    /* 3. ESTILO DO BOTÃO VOLTAR (SIDEBAR) - Proteção para não ficar gigante */
    section[data-testid="stSidebar"] button {
        height: 45px !important;       /* Altura normal */
        width: 100% !important;        /* Largura da sidebar */
        font-size: 16px !important;    /* Fonte pequena */
        background-color: #e9ecef !important;
        border: 1px solid #ced4da !important;
        box-shadow: none !important;
        margin-top: 10px !important;
    }
    
    section[data-testid="stSidebar"] button:hover {
        background-color: #dee2e6 !important;
        color: #000 !important;
    }

    /* Ajuste visual das Abas */
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-size: 18px !important; font-weight: bold; }
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

# 5. FUNÇÕES DE TRATAMENTO DE DADOS (CORREÇÃO DE "NONE")
def limpar_valor(valor, is_time=False):
    """
    Função robusta que converte 'None', 'nan', '0', vazios em None real (Python).
    Isso impede que eles entrem nos gráficos.
    """
    if pd.isna(valor): return None
    s = str(valor).strip().lower()
    
    # Lista de valores considerados inválidos/nulos
    if s in ['none', '', 'nan', 'null', '#n/a', '-', '0', '0.0', '0%']:
        return None

    # Tratamento de Tempo (TMA/Pausa)
    if is_time and ':' in s:
        try:
            partes = s.split(':')
            if len(partes) == 3:
                return int(partes[0]) * 60 + int(partes[1]) + float(partes[2]) / 60
            elif len(partes) == 2:
                return int(partes[0]) + float(partes[1]) / 60
        except:
            return None
    
    # Tratamento de Números
    try:
        limpo = re.sub(r'[^\d,.-]', '', s).replace(',', '.')
        val = float(limpo)
        return val if val != 0 else None
    except:
        return None

@st.cache_data(ttl=60)
def carregar_dados(aba):
    try:
        # ID da planilha e URL
        sid = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{sid}/gviz/tq?tqx=out:csv&sheet={aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Identificar colunas chaves
        col_op = next((c for c in df.columns if 'operador' in c.lower()), df.columns[0])
        col_mat = next((c for c in df.columns if 'matricula' in c.lower()), df.columns[1])

        # Converter colunas de métricas
        for metrica in list(METAS_BASE.keys()) + ['Pausa Total']:
            col_origem = next((c for c in df.columns if metrica.lower() in c.lower()), None)
            if col_origem:
                is_time = 'TMA' in metrica or 'Pausa' in metrica
                df[f'{metrica}_num'] = df[col_origem].apply(lambda x: limpar_valor(x, is_time))
            else:
                df[f'{metrica}_num'] = None
        
        return df, col_op, col_mat
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None

def definir_cor(valor, metrica, metas):
    if valor is None: return "#6c757d" # Cinza
    m = metas.get(metrica)
    if not m: return "#333"
    
    v, marg, menor = m['valor'], m['margem'], m['menor_melhor']
    if menor:
        return "#28a745" if valor <= v else ("#ffc107" if valor <= v + marg else "#dc3545")
    else:
        return "#28a745" if valor >= v else ("#ffc107" if valor >= v - marg else "#dc3545")

def kpi_card(titulo, valor, cor, icon=""):
    v_str = f"{valor:.2f}" if isinstance(valor, (float, int)) else "N/A"
    st.markdown(f"""
    <div style="background: white; padding: 20px; border-radius: 12px; border-left: 8px solid {cor}; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 10px;">
        <span style="font-size: 12px; color: #888; font-weight: bold; text-transform: uppercase;">{titulo}</span>
        <h3 style="margin: 5px 0 0 0; color: {cor}; font-size: 24px;">{icon} {v_str}</h3>
    </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NAVEGAÇÃO ---

if st.session_state.servico is None:
    # --- TELA LOBBY (BOTÕES GIGANTES) ---
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Use gap="medium" para criar espaçamento entre os botões
    c1, c2, c3 = st.columns(3, gap="medium")
    
    # Devido ao CSS injetado, estes botões terão 300px de altura e 100% de largura
    with c1:
        if st.button("🏢 SAC NDI"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with c2:
        if st.button("🏦 SAC PPO"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with c3:
        if st.button("🏥 SAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    # --- TELA INTERNA (DASHBOARD) ---
    with st.sidebar:
        st.header(f"📍 {st.session_state.servico}")
        
        if st.session_state.servico == "SAC NDI":
            opts = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            opts = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            opts = ["Selecione...", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Supervisor:", opts)
        
        st.write("")
        st.write("")
        # Botão Voltar (Estilo Pequeno pelo CSS section[data-testid="stSidebar"])
        if st.button("⬅️ Voltar ao Lobby"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        
        if df is not None:
            # Metas específicas
            metas_locais = METAS_BASE.copy()
            pausas = {"Carla": 17.27, "Ellen": 19.06, "Alex": 17.17, "Magno": 19.18}
            meta_p = next((v for k, v in pausas.items() if k in supervisor), 21.75)
            metas_locais['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            tab1, tab2, tab3 = st.tabs(["👤 Individual", "🏆 Ranking", "📊 Saúde da Equipe"])

            # 1. ABA INDIVIDUAL
            with tab1:
                mat_input = st.text_input("Digite a Matrícula:", placeholder="Ex: 123456")
                if mat_input:
                    res = df[df[col_mat].astype(str).str.contains(mat_input.strip())]
                    if not res.empty:
                        dado = res.iloc[0]
                        st.subheader(f"Operador: {dado[col_op]}")
                        g1, g2, g3 = st.columns(3)
                        with g1: kpi_card("Aderência", dado['Aderencia_num'], defining_cor(dado['Aderencia_num'], 'Aderencia', metas_locais))
                        with g2: kpi_card("Resolutividade", dado['Resolutividade_num'], defining_cor(dado['Resolutividade_num'], 'Resolutividade', metas_locais))
                        with g3: kpi_card("TMA Voz", dado['TMA Voz_num'], defining_cor(dado['TMA Voz_num'], 'TMA Voz', metas_locais), "⏱️")
                    else:
                        st.warning("Matrícula não encontrada.")

            # 2. ABA RANKING
            with tab2:
                sel_rank = st.selectbox("Métrica:", list(metas_locais.keys()))
                df_r = df[
                    (df[col_op].str.strip().upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{sel_rank}_num'].notna())
                ].copy()
                
                if not df_r.empty:
                    menor_m = metas_locais[sel_rank]['menor_melhor']
                    top = df_r.nsmallest(3, f'{sel_rank}_num') if menor_m else df_r.nlargest(3, f'{sel_rank}_num')
                    
                    cc1, cc2, cc3 = st.columns(3)
                    for i, (idx, row) in enumerate(top.iterrows()):
                        with [cc1, cc2, cc3][i]:
                            kpi_card(f"{i+1}º Lugar", row[col_op], definir_cor(row[f'{sel_rank}_num'], sel_rank, metas_locais), ["🥇","🥈","🥉"][i])
                    st.divider()
                    st.dataframe(df_r[[col_op, f'{sel_rank}_num']].sort_values(by=f'{sel_rank}_num', ascending=menor_m), use_container_width=True, hide_index=True)

            # 3. ABA SAÚDE (CORREÇÃO DE DADOS VAZIOS/NONE)
            with tab3:
                sel_saude = st.selectbox("Análise Geral:", list(metas_locais.keys()))
                
                # --- FILTRO CRÍTICO ---
                # Remove quem tem valor Nulo (None) ou vazio.
                # Isso resolve o problema da Ludmila aparecendo com 'None'
                df_s = df[
                    (df[col_op].str.strip().upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{sel_saude}_num'].notna()) 
                ].copy()

                if not df_s.empty:
                    mv, mi = metas_locais[sel_saude]['valor'], metas_locais[sel_saude]['menor_melhor']
                    
                    df_s['Status'] = df_s[f'{sel_saude}_num'].apply(
                        lambda x: 'Dentro da Meta' if (x <= mv if mi else x >= mv) else 'Fora da Meta'
                    )
                    
                    c_pizza, c_tabela = st.columns([1, 1.5])
                    with c_pizza:
                        fig = px.pie(df_s, names='Status', hole=0.5, color='Status',
                                     color_discrete_map={'Dentro da Meta':'#28a745', 'Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with c_tabela:
                        # Mostra apenas operadores válidos
                        st.dataframe(
                            df_s[[col_op, f'{sel_saude}_num', 'Status']].style.applymap(
                                lambda v: f"color: {'#28a745' if v=='Dentro da Meta' else '#dc3545'}", subset=['Status']
                            ),
                            use_container_width=True, hide_index=True
                        )
                else:
                    st.info("Todos os dados desta métrica estão vazios ou nulos.")
