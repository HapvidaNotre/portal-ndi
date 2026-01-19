import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. Configurações da Planilha
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

# 3. Funções de Suporte
def obter_data_atualizacao():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/pubhtml"
        response = requests.get(url, timeout=5)
        data_header = response.headers.get('Date')
        if data_header:
            dt = datetime.strptime(data_header, '%a, %d %b %Y %H:%M:%S %Z')
            return dt.strftime('%d/%m/%Y às %H:%M')
    except: return "Recentemente"
    return "Recentemente"

@st.cache_data(ttl=60)
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base: {e}")
        return None

def exibir_metricas(label, valor, meta, menor_melhor=False):
    try:
        valor_str = str(valor).replace('%', '').replace(',', '.')
        valor_num = float(valor_str)
        if menor_melhor: cor = "green" if valor_num <= meta else "red"
        else: cor = "green" if valor_num >= meta else "red"
    except: cor = "#333"
    exibicao = str(valor) if '%' in str(valor) else f"{valor}%"
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid {cor}; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">{label}</p>
            <h2 style="margin: 0; color: {cor};">{exibicao if pd.notna(valor) else '0%'}</h2>
        </div>
    """, unsafe_allow_html=True)
    return cor

def criar_podio(df_ranking, coluna_nome, coluna_valor, titulo):
    st.subheader(f"🏆 Top 3: {titulo}")
    # Converte para número para ordenar corretamente
    temp_df = df_ranking.copy()
    temp_df['valor_num'] = temp_df[coluna_valor].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
    top_3 = temp_df.nlargest(3, 'valor_num')
    
    cols = st.columns(3)
    medalhas = ["🥇 1º", "🥈 2º", "🥉 3º"]
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div style="text-align: center; background-color: #f8f9fa; padding: 10px; border-radius: 10px; border: 1px solid #ddd;">
                    <p style="font-size: 14px; font-weight: bold; margin:0; color: #555;">{medalhas[i]}</p>
                    <p style="font-size: 16px; font-weight: bold; margin:0; color: #1f77b4;">{row[coluna_nome]}</p>
                    <p style="font-size: 20px; font-weight: bold; margin:0; color: #28a745;">{row[coluna_valor]}</p>
                </div>
            """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
data_att = obter_data_atualizacao()
st.info(f"📅 **Sincronizado com Google Sheets em:** {data_att}")

df = carregar_dados()

if df is not None:
    tab_ind, tab_equipe, tab_melhores = st.tabs(["👤 Métricas Individuais", "👥 Métricas Equipe", "⭐ Melhores"])

    # --- ABA INDIVIDUAL ---
    with tab_ind:
        matricula_busca = st.text_input("Olá! Digite sua Matrícula:", placeholder="Ex: 1039456")
        if matricula_busca:
            colaborador = df[df['Matricula'] == str(matricula_busca).strip()]
            if not colaborador.empty:
                res = colaborador.iloc[0]
                st.subheader(f"Bem-vindo(a), {res.get('Operador', 'Colaborador')}!")
                c1, c2, c3 = st.columns(3)
                exibir_metricas("Aderência", res.get('Aderencia', 0), 95)
                exibir_metricas("Resolutividade", res.get('Resolutividade', 0), 85)
                exibir_metricas("Transf", res.get('Transf', 0), 85)
                st.markdown(f"**TMA Voz:** `{res.get('TMA Voz', '00:00:00')}` | **NPS:** `{res.get('Pesquisa', 'N/A')}`")
            else:
                st.warning("Matrícula não encontrada.")

    # --- ABA EQUIPE ---
    with tab_equipe:
        st.subheader("📊 Resultados Consolidados do Time")
        dados_equipe = df[df['Operador'].str.strip() == 'EQUIPE']
        if not dados_equipe.empty:
            res_eq = dados_equipe.iloc[0]
            e1, e2, e3 = st.columns(3)
            with e1: exibir_metricas("Aderência Equipe", res_eq.get('Aderencia', 0), 95)
            with e2: exibir_metricas("Resolutividade Equipe", res_eq.get('Resolutividade', 0), 85)
            with e3: exibir_metricas("Transf Equipe", res_eq.get('Transf', 0), 85)
            
            e4, e5, e6 = st.columns(3)
            with e4: exibir_metricas("Absenteísmo Médio", res_eq.get('Absenteismo', 0), 5, menor_melhor=True)
            with e5: exibir_metricas("Pausa Total Média", res_eq.get('Pausa Total', 0), 10, menor_melhor=True)
            with e6: 
                st.markdown(f"""
                    <div style="background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 6px solid #FFD700; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">NPS Equipe</p>
                        <h2 style="margin: 0; color: #444;">⭐ {res_eq.get('Pesquisa', 'N/A')}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown(f"**TMA Médio Geral:** `{res_eq.get('TMA Voz', '00:00:00')}`")
        else:
            st.warning("Linha 'EQUIPE' não localizada.")

    # --- ABA MELHORES ---
    with tab_melhores:
        st.header("🌟 Destaques do Período")
        st.write("Estes são os 3 operadores com melhor desempenho em cada pilar.")
        
        # Filtra para não incluir a linha 'EQUIPE' no ranking
        ranking_df = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
        
        if not ranking_df.empty:
            criar_podio(ranking_df, 'Operador', 'Aderencia', "Aderência")
            st.markdown("---")
            criar_podio(ranking_df, 'Operador', 'Resolutividade', "Resolutividade")
            st.markdown("---")
            criar_podio(ranking_df, 'Operador', 'Transf', "Transferência")
        else:
            st.write("Dados insuficientes para gerar o ranking.")

st.markdown("---")
st.caption("Portal NDI | Performance e Reconhecimento")
