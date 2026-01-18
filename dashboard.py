import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="📊")

# Link da sua planilha Google exportada como CSV
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/export?format=csv"

# Função para carregar dados
@st.cache_data(ttl=600) # Atualiza o cache a cada 10 minutos
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()
        if 'Matrícula' in df.columns:
            df['Matrícula'] = df['Matrícula'].astype(str).str.replace('.0', '', regex=False)
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a Planilha Google: {e}")
        return None

# Estilização de Cards
def card_indicador(label, valor, meta, inverso=False):
    # Lógica de cores: verde se bater a meta, vermelho se não.
    # 'inverso=True' para indicadores onde menos é melhor (ex: Absenteísmo)
    try:
        num_valor = float(str(valor).replace('%', '').replace(',', '.'))
        if inverso:
            cor = "green" if num_valor <= meta else "red"
        else:
            cor = "green" if num_valor >= meta else "red"
    except:
        cor = "black"
    
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid {cor}; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
            <p style="margin: 0; font-size: 14px; color: #666;">{label}</p>
            <h2 style="margin: 0; color: {cor};">{valor}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE ---
st.markdown("# 📊 Portal de Performance NDI - SP")
st.markdown("---")

df = carregar_dados()

if df is not None:
    tab1, tab2 = st.tabs(["👤 Área do Operador", "🔐 Área do Gestor"])

    with tab1:
        st.subheader("Consulta Individual de Performance")
        matricula_busca = st.text_input("Digite sua Matrícula para ver seus resultados:")

        if matricula_busca:
            colaborador = df[df['Matrícula'] == matricula_busca]

            if not colaborador.empty:
                row = colaborador.iloc[0]
                st.success(f"Olá, {row['Nome']}! Veja seus indicadores:")

                # Primeira Linha de Cards
                c1, c2, c3 = st.columns(3)
                with c1: card_indicador("Aderência", f"{row['Aderência']}%", 95)
                with c2: card_indicador("Resolutividade", f"{row['Resolutividade']}%", 85)
                with c3: card_indicador("Transf", f"{row['Transf']}%", 10, inverso=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Segunda Linha de Cards
                c4, c5, c6 = st.columns(3)
                with c4: card_indicador("Absenteísmo", f"{row['Absenteísmo']}%", 5, inverso=True)
                with c5: card_indicador("Pausa Total", f"{row['Pausa Total']}%", 10, inverso=True)
                with c6: 
                    st.markdown(f"""
                        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 5px solid gold; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);">
                            <p style="margin: 0; font-size: 14px; color: #666;">Pesquisa (NPS)</p>
                            <h2 style="margin: 0; color: #444;">⭐ {row['Pesquisa']}</h2>
                        </div>
                    """, unsafe_allow_html=True)

                st.info(f"⏱️ **Seu TMA Voz:** {row['TMA']}")
            else:
                st.error("Matrícula não localizada na base atual.")

    with tab2:
        st.subheader("Configurações do Gestor")
        st.write("✅ **Status:** O portal está conectado diretamente à sua Planilha Google.")
        st.write("Para atualizar os dados, basta editar sua planilha oficial no Google Drive. O site refletirá as mudanças em instantes.")
        if st.button("Forçar Atualização de Dados"):
            st.cache_data.clear()
            st.rerun()

else:
    st.warning("Aguardando carregamento da base de dados...")

st.markdown("---")
st.caption("Desenvolvido para NDI - Hapvida NotreDame Intermédica")
