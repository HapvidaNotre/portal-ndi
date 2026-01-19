import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CONFIGURAÇÃO DA PLANILHA MESTRE
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"

# Lista de supervisores conforme suas abas
SUPERVISORES = [
    "Selecione...",
    "Equipe Erik", 
    "Equipe Davi", 
    "Equipe Elaine", 
    "Equipe Sayanne", 
    "Equipe Beatriz", 
    "Equipe Aline", 
    "Equipe Marcelo"
]

# 3. Funções de Suporte
@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        nome_aba_url = nome_aba.replace(" ", "%20")
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba_url}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        return df
    except Exception as e:
        return None

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 12px; border-left: 8px solid {cor}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h1 style="margin: 10px 0 0 0; color: {cor}; font-size: 30px;">{icon} {valor if pd.notna(valor) else '0%'}</h1>
        </div>
    """, unsafe_allow_html=True)

def calcular_cor(valor, meta, menor_melhor=False):
    try:
        v = float(str(valor).replace('%', '').replace(',', '.'))
        if menor_melhor: return "#28a745" if v <= meta else "#dc3545"
        return "#28a745" if v >= meta else "#dc3545"
    except: return "#333"

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")

# Filtro de Supervisor (HUB)
supervisor_selecionado = st.selectbox("Para começar, selecione o seu Supervisor:", SUPERVISORES)

if supervisor_selecionado != "Selecione...":
    df = carregar_dados_aba(supervisor_selecionado)

    if df is not None:
        # Abas solicitadas
        tab_ind, tab_equipe, tab_melhores, tab_grafico = st.tabs([
            "👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Gráficos de Saúde"
        ])

        with tab_ind:
            matricula = st.text_input("Digite sua Matrícula:", key="input_mat")
            if matricula:
                res = df[df['Matricula'] == str(matricula).strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r.get('Operador', 'Colaborador')}")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1: exibir_card("Aderência", r.get('Aderencia', 0), calcular_cor(r.get('Aderencia', 0), 85))
                    with c2: exibir_card("Resolutividade", r.get('Resolutividade', 0), calcular_cor(r.get('Resolutividade', 0), 85))
                    with c3: exibir_card("Transferência", r.get('Transf', 0), calcular_cor(r.get('Transf', 0), 85))
                    
                    # Formato TMA e NPS
                    st.markdown(f"**TMA Voz:** `{r.get('TMA Voz', '00:00:00')}` | **NPS:** `{r.get('Pesquisa', 'N/A')}`")
                else:
                    st.warning("Matrícula não encontrada nesta equipe.")

        with tab_equipe:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                col1, col2, col3 = st.columns(3)
                with col1: exibir_card("Aderência Equipe", e.get('Aderencia', 0), calcular_cor(e.get('Aderencia', 0), 85))
                with col2: exibir_card("Resolutividade Equipe", e.get('Resolutividade', 0), calcular_cor(e.get('Resolutividade', 0), 85))
                with col3: exibir_card("TMA Médio", e.get('TMA Voz', '00:00:00'), "#1f77b4", "⏱️")
            else:
                st.info("Linha 'EQUIPE' não encontrada nesta aba.")

        with tab_grafico:
            st.header("📈 Saúde da Operação")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops.empty:
                # Conversão para gráfico
                df_ops['v'] = pd.to_numeric(df_ops['Aderencia'].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce').fillna(0)
                df_ops['Status'] = df_ops['v'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
                fig = px.pie(df_ops, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)

    else:
        st.error("Não foi possível carregar os dados. Verifique se a aba tem o nome exato.")

else:
    st.info("Selecione um supervisor acima para visualizar os dados da sua equipe.")

st.markdown("---")
st.caption("Portal NDI | Performance e Resultados")
