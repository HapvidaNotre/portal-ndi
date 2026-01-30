import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# --- INICIALIZAÇÃO DO ESTADO DE NAVEGAÇÃO ---
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. DICIONÁRIO CENTRALIZADO DE METAS
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

# 3. FUNÇÕES DE SUPORTE
def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        if valor <= m: return "#28a745" # Verde
        if valor <= m + tol: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= m: return "#28a745" # Verde
        if valor >= m - tol: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

def converter_para_numero(valor):
    if pd.isna(valor): return 0.0
    try: return float(str(valor).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def converter_tma_minutos(tempo_str):
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {valor}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx:out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        colunas_meta = list(METAS_BASE.keys()) + ['Pausa Total']
        for col in colunas_meta:
            if col in df.columns:
                df[f'{col}_num'] = df[col].apply(converter_tma_minutos if 'TMA' in col else converter_para_numero)
            else:
                df[f'{col}_num'] = 0.0
        return df
    except: return None

# --- LOBBY DE ENTRADA ---
if st.session_state.servico is None:
    st.markdown("<h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Selecione o serviço para acessar os indicadores:</p>", unsafe_allow_html=True)
    st.write("---")
    
    col_l1, col_l2, col_l3 = st.columns(3)
    
    with col_l1:
        if st.button("🏢 SAC NDI", use_container_width=True, type="primary"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
            
    with col_l2:
        if st.button("🏦 SAC PPO", use_container_width=True):
            st.session_state.servico = "SAC PPO"
            st.rerun()
            
    with col_l3:
        if st.button("🏥 SAC HAPVIDA", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

# --- INTERFACE PRINCIPAL ---
else:
    # Barra Lateral
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3208/3208631.png", width=100)
        st.title(f"{st.session_state.servico}")
        
        # Mapeamento de supervisores por serviço
        if st.session_state.servico == "SAC NDI":
            lista_supervisores = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            lista_supervisores = ["Selecione...", "Aguardando Cadastro PPO"]
        else:
            lista_supervisores = ["Selecione...", "Aguardando Cadastro Hapvida"]

        supervisor = st.selectbox("Selecione o Supervisor:", lista_supervisores)
        
        st.write("---")
        if st.button("⬅️ Voltar ao Lobby"):
            st.session_state.servico = None
            st.rerun()

    # Conteúdo Principal
    if supervisor != "Selecione..." and "Aguardando" not in supervisor:
        # Metas de Pausa Total Customizadas para NDI
        especiais = ["Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Aline", "Equipe Marcelo"]
        meta_pausa = 16.60 if supervisor in especiais else 21.75
        
        METAS_SESSAO = METAS_BASE.copy()
        METAS_SESSAO['Pausa Total'] = {'valor': meta_pausa, 'margem': 3.0, 'menor_melhor': True}

        df = carregar_dados(supervisor)
        if df is not None:
            st.header(f"Performance: {supervisor}")
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde da Operação"])

            # 1. ABA INDIVIDUAL
            with tabs[0]:
                mat = st.text_input("Digite sua Matrícula para consultar:")
                if mat:
                    res = df[df['Matricula'].astype(str).str.contains(mat.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r['Operador']}")
                        c1, c2, c3, c4 = st.columns(4)
                        with c1:
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'], 'Aderencia', METAS_SESSAO))
                            exibir_card("Produtividade", r['Produtividade'], definir_cor_kpi(r['Produtividade_num'], 'Produtividade', METAS_SESSAO))
                        with c2:
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', METAS_SESSAO))
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', METAS_SESSAO), "⏱️")
                        with c3:
                            exibir_card("Absenteísmo", r['Absenteismo'], definir_cor_kpi(r['Absenteismo_num'], 'Absenteismo', METAS_SESSAO))
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', METAS_SESSAO), "⏱️")
                        with c4:
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'], 'Pesquisa', METAS_SESSAO), "⭐")
                            exibir_card("ShortCall", r['ShortCall'], definir_cor_kpi(r['ShortCall_num'], 'ShortCall', METAS_SESSAO))
                        
                        st.divider()
                        st.caption("Detalhamento Operacional")
                        ca, cb, cc = st.columns(3)
                        ca.metric("Pausa Produtiva", r['Pausa Produtiva'])
                        cb.metric("Pausa Improdutiva", r['Pausa Improdutiva'])
                        cc.metric("Transferência", r['Transf'])
                    else: st.warning("Matrícula não encontrada.")

            # 2. ABA EQUIPE
            with tabs[1]:
                eq = df[df['Operador'].str.strip() == 'EQUIPE']
                if not eq.empty:
                    e = eq.iloc[0]
                    cols = st.columns(3)
                    for i, (k, v) in enumerate(METAS_SESSAO.items()):
                        with cols[i % 3]: 
                            exibir_card(f"{k} Equipe", e[k], definir_cor_kpi(e[f'{k}_num'], k, METAS_SESSAO))

            # 3. ABA MELHORES (RANKINGS)
            with tabs[2]:
                df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
                for k, v in METAS_SESSAO.items():
                    st.markdown(f"#### Ranking: {k}")
                    top = df_ops.nsmallest(3, f'{k}_num') if v['menor_melhor'] else df_ops.nlargest(3, f'{k}_num')
                    mc = st.columns(3)
                    for i, (_, row) in enumerate(top.iterrows()):
                        with mc[i]: exibir_card(f"{i+1}º Lugar", row['Operador'], definir_cor_kpi(row[f'{k}_num'], k, METAS_SESSAO), ["🥇","🥈","🥉"][i])
                    st.divider()

            # 4. ABA SAÚDE DA OPERAÇÃO
            with tabs[3]:
                df_s = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
                sel = st.selectbox("Diagnóstico por Métrica:", list(METAS_SESSAO.keys()))
                mv, inv = METAS_SESSAO[sel]['valor'], METAS_SESSAO[sel]['menor_melhor']
                df_s['Status'] = df_s[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    fig = px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                    st.plotly_chart(fig, use_container_width=True)
                with c_s2:
                    st.dataframe(df_s[['Operador', sel, 'Status']], use_container_width=True, hide_index=True)
    else:
        st.info("👋 Bem-vindo! Selecione o seu supervisor na barra lateral para carregar os resultados da equipe.")
