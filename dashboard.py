import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CONFIGURAÇÃO DA PLANILHA MESTRE
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"

SUPERVISORES = [
    "Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", 
    "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"
]

# 3. Funções de Suporte
@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        # Limpeza de Matrícula
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        # Converter métricas para numérico para o ranking
        for col in ['Aderencia', 'Resolutividade']:
            if col in df.columns:
                df[f'{col}_num'] = pd.to_numeric(df[col].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except:
        return None

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 8px solid {cor}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 26px;">{icon} {valor}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
st.title("🚀 Portal de Performance NDI")
supervisor_selecionado = st.selectbox("Para começar, selecione o seu Supervisor:", SUPERVISORES)

if supervisor_selecionado != "Selecione...":
    df = carregar_dados_aba(supervisor_selecionado)

    if df is not None:
        tab_ind, tab_equipe, tab_melhores, tab_grafico = st.tabs([
            "👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Gráficos de Saúde"
        ])

        # --- ABA INDIVIDUAL ---
        with tab_ind:
            mat = st.text_input("Digite sua Matrícula:", key="input_mat")
            if mat:
                res = df[df['Matricula'] == str(mat).strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r.get('Operador', 'Colaborador')}")
                    c1, c2, c3 = st.columns(3)
                    with c1: exibir_card("Aderência", r.get('Aderencia', '0%'), "#28a745")
                    with c2: exibir_card("Resolutividade", r.get('Resolutividade', '0%'), "#007bff")
                    with c3: exibir_card("Transferência", r.get('Transf', '0%'), "#6c757d")
                    st.markdown(f"**TMA Voz:** `{r.get('TMA Voz', '00:00:00')}` | **NPS:** `{r.get('Pesquisa', '0,0')}`")
                else: st.warning("Matrícula não encontrada.")

        # --- ABA EQUIPE ---
        with tab_equipe:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                col1, col2, col3 = st.columns(3)
                with col1: exibir_card("Aderência Equipe", e.get('Aderencia', '0%'), "#28a745")
                with col2: exibir_card("Resolutividade Equipe", e.get('Resolutividade', '0%'), "#007bff")
                with col3: exibir_card("TMA Médio", e.get('TMA Voz', '00:00:00'), "#1f77b4", "⏱️")

        # --- ABA MELHORES (RANKING ATUALIZADO) ---
        with tab_melhores:
            st.subheader(f"🏆 Destaques - {supervisor_selecionado}")
            # Filtra apenas operadores (remove a linha 'EQUIPE')
            df_ranking = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            if not df_ranking.empty:
                # Criar uma nota média para o ranking
                df_ranking['Nota_Final'] = (df_ranking['Aderencia_num'] + df_ranking['Resolutividade_num']) / 2
                df_ranking = df_ranking.sort_values(by='Nota_Final', ascending=False).head(5)
                
                # Exibição do Top 3 em colunas (Pódio)
                m1, m2, m3 = st.columns(3)
                top = df_ranking.iloc
                if len(df_ranking) >= 1:
                    with m1: exibir_card("1º Lugar", top[0]['Operador'], "#FFD700", "🥇")
                if len(df_ranking) >= 2:
                    with m2: exibir_card("2º Lugar", top[1]['Operador'], "#C0C0C0", "🥈")
                if len(df_ranking) >= 3:
                    with m3: exibir_card("3º Lugar", top[2]['Operador'], "#CD7F32", "🥉")
                
                st.markdown("---")
                st.dataframe(df_ranking[['Operador', 'Aderencia', 'Resolutividade', 'TMA Voz']], use_container_width=True)
            else:
                st.info("Dados insuficientes para gerar o ranking.")

        # --- ABA GRÁFICOS ---
        with tab_grafico:
            st.header("📊 Saúde da Operação")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops.empty:
                df_ops['Status'] = df_ops['Aderencia_num'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
                fig = px.pie(df_ops, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Selecione um supervisor para carregar o portal.")
