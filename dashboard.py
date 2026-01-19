import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="📊")

# 2. Configurações da Planilha (ID extraído do seu link)
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 3. Função para obter a data da última modificação automática
def obter_data_atualizacao():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/pubhtml"
        response = requests.get(url, timeout=5)
        data_header = response.headers.get('Date')
        if data_header:
            dt = datetime.strptime(data_header, '%a, %d %b %Y %H:%M:%S %Z')
            return dt.strftime('%d/%m/%Y às %H:%M')
    except:
        return "Recentemente"
    return "Recentemente"

# 4. Função para Carregar Dados
@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        # Tratamento da coluna Matricula (sem acento conforme sua planilha)
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base: {e}")
        return None

# 5. Função de Estilização dos Cards
def exibir_metricas(label, valor, meta, menor_melhor=False):
    try:
        valor_str = str(valor).replace('%', '').replace(',', '.')
        valor_num = float(valor_str)
        if menor_melhor:
            cor = "green" if valor_num <= meta else "red"
        else:
            cor = "green" if valor_num >= meta else "red"
    except:
        cor = "#333"

    exibicao = str(valor) if '%' in str(valor) else f"{valor}%"

    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid {cor}; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">{label}</p>
            <h2 style="margin: 0; color: {cor};">{exibicao if pd.notna(valor) else '0%'}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("📊 Portal de Performance NDI - SP")

# Exibe a data da última atualização automática
data_att = obter_data_atualizacao()
st.info(f"📅 **Última atualização dos dados na planilha:** {data_att}")

df = carregar_dados()

if df is not None:
    # Criação das Abas: Individual e Equipe
    tab_ind, tab_equipe = st.tabs(["👤 Métricas Individuais", "👥 Métricas Equipe"])

    # --- ABA INDIVIDUAL ---
    with tab_ind:
        matricula_busca = st.text_input("Olá Operador! Digite sua Matrícula:", placeholder="Ex: 1039456")
        
        if matricula_busca:
            colaborador = df[df['Matricula'] == str(matricula_busca).strip()]
            
            if not colaborador.empty:
                res = colaborador.iloc[0]
                st.success(f"Resultados de: **{res.get('Operador', 'Colaborador')}**")
                
                c1, c2, c3 = st.columns(3)
                with c1: exibir_metricas("Aderência", res.get('Aderencia', 0), 95)
                with c2: exibir_metricas("Resolutividade", res.get('Resolutividade', 0), 85)
                with c3: exibir_metricas("Transf", res.get('Transf', 0), 85)

                c4, c5, c6 = st.columns(3)
                with c4: exibir_metricas("Absenteísmo", res.get('Absenteismo', 0), 5, menor_melhor=True)
                with c5: exibir_metricas("Pausa Total", res.get('Pausa Total', 0), 10, menor_melhor=True)
                with c6:
                    st.markdown(f"""
                        <div style="background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 6px solid #FFD700; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">Pesquisa (NPS)</p>
                            <h2 style="margin: 0; color: #444;">⭐ {res.get('Pesquisa', 'N/A')}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"### ⏱️ TMA Voz: `{res.get('TMA Voz', '00:00:00')}`")
            else:
                st.warning("Matrícula não encontrada na base.")

    # --- ABA EQUIPE ---
    with tab_equipe:
        st.subheader("📊 Performance Geral do Time")
        
        # Procura a linha onde o nome do operador seja exatamente 'EQUIPE'
        dados_equipe = df[df['Operador'].str.strip() == 'EQUIPE']

        if not dados_equipe.empty:
            res_eq = dados_equipe.iloc[0]
            st.markdown("Veja abaixo como está o desempenho coletivo do nosso time em relação às metas:")
            
            e1, e2, e3 = st.columns(3)
            with e1: exibir_metricas("Aderência Equipe", res_eq.get('Aderencia', 0), 95)
            with e2: exibir_metricas("Resolutividade Equipe", res_eq.get('Resolutividade', 0), 85)
            with e3: exibir_metricas("Transf Equipe", res_eq.get('Transf', 0), 85)

            e4, e5, e6 = st.columns(3)
            with e4: exibir_metricas("Absenteísmo Equipe", res_eq.get('Absenteismo', 0), 5, menor_melhor=True)
            with e5: exibir_metricas("Pausa Total Equipe", res_eq.get('Pausa Total', 0), 10, menor_melhor=True)
            with e6:
                 st.markdown(f"""
                    <div style="background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 6px solid #FFD700; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">NPS Médio da Equipe</p>
                        <h2 style="margin: 0; color: #444;">⭐ {res_eq.get('Pesquisa', 'N/A')}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"### ⏱️ TMA Médio da Equipe: `{res_eq.get('TMA Voz', '00:00:00')}`")
        else:
            st.warning("⚠️ Dados da equipe não localizados. Certifique-se de que existe uma linha na planilha onde a coluna 'Operador' esteja preenchida como: EQUIPE")

st.markdown("---")
st.caption("NDI Hapvida NotreDame Intermédica | Criado para facilitar seu acompanhamento")
