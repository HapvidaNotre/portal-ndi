import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="📊")

# 2. Link da sua planilha Google (Exportação CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/export?format=csv"

# 3. Função para Carregar Dados com Cache
@st.cache_data(ttl=300)
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        # Ajusta a matrícula para texto e remove decimais
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base: {e}")
        return None

# 4. Função de exibição dos Cards coloridos
def exibir_metricas(label, valor, meta, menor_melhor=False):
    try:
        # Converte o valor para número para lógica de cores
        valor_str = str(valor).replace('%', '').replace(',', '.')
        valor_num = float(valor_str)
        
        if menor_melhor:
            # Para Absenteísmo e Pausas: Menor que a meta = Verde
            cor = "green" if valor_num <= meta else "red"
        else:
            # Para Aderência, Resolutividade e Transf: Maior ou igual a meta = Verde
            cor = "green" if valor_num >= meta else "red"
    except:
        cor = "#333"

    # Garante que o % apareça apenas uma vez
    exibicao = str(valor) if '%' in str(valor) else f"{valor}%"

    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid {cor}; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">{label}</p>
            <h2 style="margin: 0; color: {cor};">{exibicao if pd.notna(valor) else '0%'}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("📊 Portal de Performance NDI - SP")
st.info("📅 Última atualização: Métricas do dia **16/01**")
st.markdown("---")

df = carregar_dados()

if df is not None:
    matricula_busca = st.text_input("Olá! Digite sua Matrícula para conferir seus resultados:", placeholder="Ex: 1039456")

    if matricula_busca:
        colaborador = df[df['Matricula'] == str(matricula_busca).strip()]

        if not colaborador.empty:
            res = colaborador.iloc[0]
            st.success(f"Resultados localizados para: **{res.get('Operador', 'Colaborador')}**")
            
            # Linha 1: Indicadores de Performance
            c1, c2, c3 = st.columns(3)
            with c1: exibir_metricas("Aderência", res.get('Aderencia', 0), 95)
            with c2: exibir_metricas("Resolutividade", res.get('Resolutividade', 0), 85)
            # Transf: Acima de 85% fica Verde
            with c3: exibir_metricas("Transf", res.get('Transf', 0), 85) 

            # Linha 2: Indicadores de Comportamento
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
            
            # TMA Voz formatado
            st.markdown(f"### ⏱️ TMA Voz: `{res.get('TMA Voz', '00:00:00')}`")
        else:
            st.warning("Matrícula não encontrada. Verifique os dados na planilha.")

st.markdown("---")
st.caption("NDI Hapvida NotreDame Intermédica | Gestão de Performance")
