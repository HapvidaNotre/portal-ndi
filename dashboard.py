import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CONFIGURAÇÃO DA PLANILHA MESTRE
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SUPERVISORES = [
    "Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", 
    "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"
]

# 3. FUNÇÕES DE SUPORTE E CONVERSÃO
def converter_para_numero(valor):
    """Converte strings de porcentagem e decimais da planilha para float"""
    if pd.isna(valor): return 0.0
    try:
        s = str(valor).replace('%', '').replace(',', '.').strip()
        return float(s)
    except: return 0.0

def converter_tma_para_minutos(tempo_str):
    """Converte HH:MM:SS para minutos totais para cálculo de cores"""
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: # HH:MM:SS
            return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: # MM:SS
            return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

def definir_cor_kpi(valor, meta, margem, menor_melhor=False):
    """Lógica Verde (Meta), Amarelo (Quase), Vermelho (Fora)"""
    if menor_melhor:
        if valor <= meta: return "#28a745" # Verde
        if valor <= meta + margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= meta: return "#28a745" # Verde
        if valor >= meta - margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

def exibir_card(label, valor, cor="#333", icon=""):
    """Cria os blocos visuais das métricas"""
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 8px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px; height: 110px;">
            <p style="margin: 0; font-size: 12px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 22px;">{icon} {valor}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Limpeza de Matrícula
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        
        # Criação de colunas numéricas para cálculos
        metricas = ['Aderencia', 'Resolutividade', 'Pesquisa', 'Absenteismo', 'Transf']
        for m in metricas:
            if m in df.columns: df[f'{m}_num'] = df[m].apply(converter_para_numero)
        
        if 'TMA Voz' in df.columns:
            df['TMA_num'] = df['TMA Voz'].apply(converter_tma_para_minutos)
            
        return df
    except: return None

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Saúde"])

        # --- ABA INDIVIDUAL ---
        with tabs[0]:
            mat = st.text_input("Digite sua Matrícula:")
            if mat:
                res = df[df['Matricula'] == mat.strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r.get('Operador', 'Colaborador')}")
                    
                    # Linha 1: KPIs Principais
                    c1, c2, c3, c4 = st.columns(4)
                    with c1: exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r.get('Aderencia_num', 0), 85, 5))
                    with c2: exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r.get('Resolutividade_num', 0), 85, 5))
                    with c3: exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r.get('TMA_num', 0), 8.0, 1.0, True), "⏱️")
                    with c4: exibir_card("NPS", r.get('Pesquisa', '0'), definir_cor_kpi(r.get('Pesquisa_num', 0), 4.5, 0.5))

                    # Linha 2: Presença e Transferência
                    c5, c6, c7, c8 = st.columns(4)
                    with c5: exibir_card("Absenteísmo", r.get('Absenteismo', '0%'), definir_cor_kpi(r.get('Absenteismo_num', 0), 5.0, 5.0, True))
                    with c6: exibir_card("Transferência", r.get('Transf', '0%'), "#6c757d")
                    with c7: exibir_card("Pausa Produtiva", r.get('Pausa Produtiva', '00:00'), "#1f77b4")
                    with c8: exibir_card("Pausa Total", r.get('Pausa Total', '00:00'), "#333")

                else: st.warning("Matrícula não encontrada.")

        # --- ABA EQUIPE ---
        with tabs[1]:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                st.subheader(f"Média Geral: {supervisor}")
                col1, col2, col3, col4 = st.columns(4)
                with col1: exibir_card("Aderência Equipe", e.get('Aderencia', '0%'), "#28a745")
                with col2: exibir_card("Resolutividade Equipe", e.get('Resolutividade', '0%'), "#007bff")
                with col3: exibir_card("TMA Médio", e.get('TMA Voz', '00:00'), "#1f77b4", "⏱️")
                with col4: exibir_card("Média NPS", e.get('Pesquisa', '0'), "#28a745")
            else: st.info("Linha 'EQUIPE' não encontrada.")

        # --- ABA MELHORES (PODIOS) ---
        with tabs[2]:
            st.subheader(f"🏆 Top 3 por Categoria - {supervisor}")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops.empty:
                def gerar_ranking(col_num, col_texto, titulo, icone, meta, margem, menor_melhor=False):
                    st.markdown(f"#### {icone} {titulo}")
                    top = df_ops.nsmallest(3, col_num) if menor_melhor else df_ops.nlargest(3, col_num)
                    m1, m2, m3 = st.columns(3)
                    for i, (idx, row) in enumerate(top.iterrows()):
                        cor = definir_cor_kpi(row[col_num], meta, margem, menor_melhor)
                        with [m1, m2, m3][i]:
                            exibir_card(f"{i+1}º LUGAR", row['Operador'], cor, ["🥇","🥈","🥉"][i])
                            st.caption(f"Resultado: {row[col_texto]}")
                    st.markdown("---")

                gerar_ranking('Aderencia_num', 'Aderencia', "Melhores em Aderência", "🎯", 85, 5)
                gerar_ranking('Resolutividade_num', 'Resolutividade', "Melhores em Resolutividade", "✅", 85, 5)
                gerar_ranking('TMA_num', 'TMA Voz', "Destaques Velocidade (Menor TMA)", "⏱️", 8.0, 1.0, True)

        # --- ABA GRÁFICOS ---
        with tabs[3]:
            st.header("📊 Saúde da Operação")
            df_ops_g = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops_g.empty:
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    df_ops_g['Status'] = df_ops_g['Aderencia_num'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
                    fig = px.pie(df_ops_g, names='Status', hole=0.5, title="Visão: Aderência (Meta 85%)",
                                 color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                    st.plotly_chart(fig, use_container_width=True)
                with col_g2:
                    fig2 = px.histogram(df_ops_g, x="Resolutividade_num", nbins=10, title="Distribuição de Resolutividade",
                                        labels={'Resolutividade_num': 'Resolutividade %'}, color_discrete_sequence=['#007bff'])
                    st.plotly_chart(fig2, use_container_width=True)
