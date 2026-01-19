import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÕES INICIAIS
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SUPERVISORES = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]

# 2. METAS DEFINIDAS
METAS = {
    'Aderencia': {'valor': 85.0, 'menor_melhor': False},
    'Resolutividade': {'valor': 85.0, 'menor_melhor': False},
    'TMA_minutos': {'valor': 8.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'menor_melhor': False},
    'Absenteismo': {'valor': 5.0, 'menor_melhor': True},
    'Transf': {'valor': 15.0, 'menor_melhor': True} # Exemplo de meta
}

# 3. FUNÇÕES DE TRATAMENTO DE DADOS
def converter_para_numero(valor):
    try:
        return float(str(valor).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def converter_tma(tempo_str):
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Criar colunas numéricas para comparação
        df['Aderencia_num'] = df['Aderencia'].apply(converter_para_numero)
        df['Resolutividade_num'] = df['Resolutividade'].apply(converter_para_numero)
        df['Pesquisa_num'] = df['Pesquisa'].apply(converter_para_numero)
        df['Abs_num'] = df['Absenteismo'].apply(converter_para_numero)
        df['TMA_num'] = df['TMA Voz'].apply(converter_tma)
        
        return df
    except: return None

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Saúde da Operação"])

        # --- ABA SAÚDE DA OPERAÇÃO (EXPANDIDA) ---
        with tabs[3]:
            st.header("📊 Diagnóstico de Saúde da Operação")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            # Seletor de Métrica para análise detalhada
            metrica_foco = st.selectbox("Selecione a Métrica para ver quem está fora da meta:", 
                                       ["Aderencia", "Resolutividade", "TMA Voz", "Pesquisa (NPS)", "Absenteismo"])

            # Lógica de Status Baseada na Métrica Selecionada
            if metrica_foco == "Aderencia":
                df_ops['Status'] = df_ops['Aderencia_num'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
            elif metrica_foco == "Resolutividade":
                df_ops['Status'] = df_ops['Resolutividade_num'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
            elif metrica_foco == "TMA Voz":
                df_ops['Status'] = df_ops['TMA_num'].apply(lambda x: 'Dentro da Meta' if x <= 8.0 else 'Fora da Meta')
            elif metrica_foco == "Pesquisa (NPS)":
                df_ops['Status'] = df_ops['Pesquisa_num'].apply(lambda x: 'Dentro da Meta' if x >= 4.5 else 'Fora da Meta')
            elif metrica_foco == "Absenteismo":
                df_ops['Status'] = df_ops['Abs_num'].apply(lambda x: 'Dentro da Meta' if x <= 5.0 else 'Fora da Meta')

            # Layout de Gráfico e Lista
            col_graf, col_lista = st.columns([1, 1])

            with col_graf:
                fig = px.pie(df_ops, names='Status', hole=0.5, title=f"Visão Geral: {metrica_foco}",
                             color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)

            with col_lista:
                st.subheader("Lista por Status")
                status_ver = st.radio("Filtrar lista por:", ["Fora da Meta", "Dentro da Meta"], horizontal=True)
                lista_filtrada = df_ops[df_ops['Status'] == status_ver][['Operador', metrica_foco.replace(' (NPS)', '')]]
                st.dataframe(lista_filtrada, use_container_width=True, hide_index=True)

            st.divider()
            
            # Grid de Mini-Gráficos para todas as outras métricas
            st.subheader("Visão Multidimensional (Status Rápido)")
            c1, c2, c3 = st.columns(3)
            
            def mini_rosca(coluna_num, meta, inverter, titulo, container):
                if inverter: # Menor é melhor
                    df_ops['Temp_Status'] = df_ops[coluna_num].apply(lambda x: 'Dentro' if x <= meta else 'Fora')
                else:
                    df_ops['Temp_Status'] = df_ops[coluna_num].apply(lambda x: 'Dentro' if x >= meta else 'Fora')
                
                fig_mini = px.pie(df_ops, names='Temp_Status', hole=0.7, title=titulo,
                                  color='Temp_Status', color_discrete_map={'Dentro':'#28a745','Fora':'#dc3545'})
                fig_mini.update_layout(showlegend=False, height=250, margin=dict(t=30, b=0, l=0, r=0))
                container.plotly_chart(fig_mini, use_container_width=True)

            mini_rosca('Aderencia_num', 85, False, "🎯 Aderência", c1)
            mini_rosca('Resolutividade_num', 85, False, "✅ Resolutividade", c2)
            mini_rosca('TMA_num', 8, True, "⏱️ TMA (8 min)", c3)
            
            c4, c5, c6 = st.columns(3)
            mini_rosca('Pesquisa_num', 4.5, False, "⭐ NPS", c4)
            mini_rosca('Abs_num', 5, True, "📉 Absenteísmo", c5)
            
            # Visualização de Pausas (Barras)
            with c6:
                st.write("**Média de Pausas (Minutos)**")
                pausas_df = pd.DataFrame({
                    'Tipo': ['Produtiva', 'Improdutiva', 'Total'],
                    'Minutos': [df_ops['Pausa Produtiva'].apply(converter_tma).mean(), 
                                df_ops['Pausa Improdutiva'].apply(converter_tma).mean(),
                                df_ops['Pausa Total'].apply(converter_tma).mean()]
                })
                fig_pausas = px.bar(pausas_df, x='Tipo', y='Minutos', color='Tipo')
                fig_pausas.update_layout(height=200, showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
                st.plotly_chart(fig_pausas, use_container_width=True)
