import streamlit as st
import pandas as pd

# Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI-SP", layout="wide")

# --- SENHA DO GESTOR ---
# Defina aqui a sua senha de acesso
SENHA_MESTRA = "12345" 

st.title("📊 Portal de Performance NDI - SP")

# --- SISTEMA DE ABAS (Separação de Áreas) ---
aba_operador, aba_gestor = st.tabs(["👤 Área do Operador", "🔐 Área do Gestor"])

# --- ÁREA DO GESTOR ---
with aba_gestor:
    st.header("Acesso Administrativo")
    senha = st.text_input("Digite a senha do gestor:", type="password")
    
    if senha == SENHA_MESTRA:
        st.success("Acesso liberado!")
        upload = st.file_uploader("Suba a planilha do BI atualizada", type=["xlsx"], key="gestor_upload")
        
        if upload:
            # Salva o arquivo em cache para o operador conseguir ler
            df_geral = pd.read_excel(upload)
            df_geral.columns = df_geral.columns.str.strip()
            st.session_state['dados_bi'] = df_geral
            st.info("✅ Dados carregados com sucesso! Agora os operadores podem consultar.")
    elif senha != "":
        st.error("Senha incorreta.")

# --- ÁREA DO OPERADOR ---
with aba_operador:
    if 'dados_bi' not in st.session_state:
        st.warning("⚠️ O portal ainda não foi atualizado pelo gestor hoje.")
    else:
        st.header("Consulta Individual de Performance")
        df = st.session_state['dados_bi']
        
        # Tratamento de Dados (Métricas)
        cols_pct = ['Aderencia', 'Absenteismo', 'Transf', 'Resolutividade', 
                    'Pausa Produtiva', 'Pausa Improdutiva', 'Pausa Total']
        
        for col in df.columns:
            if col in cols_pct:
                if df[col].dtype == 'object':
                    df[col] = df[col].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
                if df[col].max() > 1.0:
                    df[col] = df[col] / 100
            if 'Pesquisa' in col and df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(',', '.').astype(float)

        # Lógica de Emojis
        def formatar_com_emoji(val, meta, tipo='min'):
            if pd.isna(val): return "-"
            if tipo == 'min':
                if val >= meta: emoji = "🟢"
                elif val >= (meta * 0.9): emoji = "🟡"
                else: emoji = "🔴"
            else:
                if val <= meta: emoji = "🟢"
                elif val <= (meta * 1.1): emoji = "🟡"
                else: emoji = "🔴"
            return f"{emoji} {val:.2%}"

        matricula_busca = st.text_input("Digite sua Matrícula para ver seus resultados:")

        if matricula_busca:
            df['Matricula_Str'] = df['Matricula'].astype(str)
            resultado = df[df['Matricula_Str'] == matricula_busca.strip()].copy()

            if not resultado.empty:
                res = resultado.iloc[0]
                st.success(f"Olá, {res['Operador']}! Veja seus indicadores:")
                
                # Exibição em Colunas (Melhor visual para o Operador)
                c1, c2, c3 = st.columns(3)
                c1.metric("Aderência", formatar_com_emoji(res['Aderencia'], 0.80))
                c1.metric("Absenteísmo", formatar_com_emoji(res['Absenteismo'], 0.05, 'max'))
                
                c2.metric("Resolutividade", formatar_com_emoji(res['Resolutividade'], 0.80))
                c2.metric("Pausa Total", formatar_com_emoji(res['Pausa Total'], 0.2175, 'max'))
                
                c3.metric("Transf", formatar_com_emoji(res['Transf'], 0.85))
                c3.metric("Pesquisa", f"⭐ {res['Pesquisa']:.2f}" if pd.notna(res['Pesquisa']) else "-")
                
                st.info(f"⏱️ **Seu TMA Voz:** {res['TMA Voz']}")
            else:
                st.error("Matrícula não encontrada.")
