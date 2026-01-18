import streamlit as st
import pandas as pd

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="📊")

# 2. Link da sua planilha Google (Exportação automática para CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E/export?format=csv"

# 3. Função para Carregar Dados
@st.cache_data(ttl=300) # Atualiza o cache a cada 5 minutos
def carregar_dados():
    try:
        df = pd.read_csv(SHEET_URL)
        # Limpa espaços extras nos nomes das colunas para evitar erros
        df.columns = df.columns.str.strip()
        
        # Tratamento da coluna Matricula (conforme sua planilha: sem acento)
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro ao conectar com a base de dados: {e}")
        return None

# 4. Função de Estilização dos Cards
def exibir_metricas(label, valor, meta, menor_melhor=False):
    try:
        # Converte o valor para número para definir a cor do indicador
        limpo = str(valor).replace('%', '').replace(',', '.')
        valor_num = float(limpo)
        
        if menor_melhor:
            cor = "green" if valor_num <= meta else "red"
        else:
            cor = "green" if valor_num >= meta else "red"
    except:
        cor = "#333" # Cor neutra caso o valor não seja numérico

    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 10px; border-left: 6px solid {cor}; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">{label}</p>
            <h2 style="margin: 0; color: {cor};">{valor if pd.notna(valor) else '0%'}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
st.title("📊 Portal de Performance NDI - SP")
st.markdown("---")

df = carregar_dados()

if df is not None:
    # Campo de Busca para o Operador
    matricula_busca = st.text_input("Olá! Digite sua Matrícula para conferir seus resultados:", placeholder="Ex: 1027083")

    if matricula_busca:
        # Busca na coluna 'Matricula' (exatamente como no seu Google Sheets)
        colaborador = df[df['Matricula'] == str(matricula_busca).strip()]

        if not colaborador.empty:
            res = colaborador.iloc[0]
            # Usa 'Operador' em vez de 'Nome', pois é como está na sua coluna A
            st.success(f"Resultados localizados para: **{res.get('Operador', 'Colaborador')}**")
            
            # Linha 1 de Indicadores
            c1, c2, c3 = st.columns(3)
            with c1: exibir_metricas("Aderência", f"{res.get('Aderencia', 0)}%", 95)
            with c2: exibir_metricas("Resolutividade", f"{res.get('Resolutividade', 0)}%", 85)
            with c3: exibir_metricas("Absenteísmo", f"{res.get('Absenteismo', 0)}%", 5, menor_melhor=True)

            # Linha 2 de Indicadores
            c4, c5, c6 = st.columns(3)
            with c4: exibir_metricas("Pausa Total", f"{res.get('Pausa Total', 0)}%", 10, menor_melhor=True)
            with c5: exibir_metricas("Transf", f"{res.get('Transf', 0)}%", 10, menor_melhor=True)
            with c6:
                # Card de Pesquisa (NPS)
                st.markdown(f"""
                    <div style="background-color: #fcfcfc; padding: 20px; border-radius: 10px; border-left: 6px solid #FFD700; box-shadow: 2px 2px 8px rgba(0,0,0,0.1);">
                        <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold;">Pesquisa (NPS)</p>
                        <h2 style="margin: 0; color: #444;">⭐ {res.get('Pesquisa', 'N/A')}</h2>
                    </div>
                """, unsafe_allow_html=True)
            
            # Exibição do TMA Voz (Coluna F da sua planilha)
            st.markdown(f"### ⏱️ TMA Voz: `{res.get('TMA Voz', '00:00:00')}`")
        else:
            st.warning("Matrícula não encontrada. Verifique se o número está correto na sua Planilha Google.")
    else:
        st.info("Aguardando digitação da matrícula...")
else:
    st.error("Não foi possível carregar a base de dados. Verifique as permissões de compartilhamento da sua planilha.")

st.markdown("---")
st.caption("Dados integrados via Google Sheets | NDI Hapvida NotreDame Intermédica")
