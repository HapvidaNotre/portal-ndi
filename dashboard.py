import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.express as px

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

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 25px; border-radius: 12px; border-left: 8px solid {cor}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 20px; display: flex; flex-direction: column; justify-content: center;">
            <p style="margin: 0; font-size: 14px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h1 style="margin: 10px 0 0 0; color: {cor}; font-size: 32px;">{icon} {valor if pd.notna(valor) else '0%'}</h1>
        </div>
    """, unsafe_allow_html=True)

def calcular_cor(valor, meta, menor_melhor=False):
    try:
        v = float(str(valor).replace('%', '').replace(',', '.'))
        if menor_melhor:
            return "#28a745" if v <= meta else "#dc3545"
        return "#28a745" if v >= meta else "#dc3545"
    except: return "#333"

def criar_podio(df_ranking, coluna_valor, titulo):
    st.markdown(f"### 🏆 Top 3: {titulo}")
    temp_df = df_ranking.copy()
    temp_df['v_num'] = temp_df[coluna_valor].astype(str).str.replace('%', '').str.replace(',', '.').replace('nan', '0')
    temp_df['v_num'] = pd.to_numeric(temp_df['v_num'], errors='coerce').fillna(0)
    top_3 = temp_df.nlargest(3, 'v_num')
    
    cols = st.columns(3)
    medalhas = ["🥇", "🥈", "🥉"]
    for i, (idx, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div style="text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #ddd;">
                    <p style="font-size: 25px; margin:0;">{medalhas[i]}</p>
                    <p style="font-size: 16px; font-weight: bold; margin:0; color: #1f77b4;">{row['Operador']}</p>
                    <p style="font-size: 22px; font-weight: bold; margin:0; color: #28a745;">{row[coluna_valor]}</p>
                </div>
            """, unsafe_allow_html=True)

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
st.info(f"📅 **Sincronizado em:** {obter_data_atualizacao()}")

df = carregar_dados()

if df is not None:
    tab_ind, tab_equipe, tab_melhores, tab_grafico = st.tabs([
        "👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Gráficos de Saúde"
    ])

    # --- ABA INDIVIDUAL ---
    with tab_ind:
        matricula_busca = st.text_input("Digite sua Matrícula:", key="busc_ind")
        if matricula_busca:
            res = df[df['Matricula'] == str(matricula_busca).strip()]
            if not res.empty:
                r = res.iloc[0]
                st.subheader(f"Resultados: {r['Operador']}")
                c1, c2, c3 = st.columns(3)
                with c1: exibir_card("Aderência", r['Aderencia'], calcular_cor(r['Aderencia'], 85))
                with c2: exibir_card("Resolutividade", r['Resolutividade'], calcular_cor(r['Resolutividade'], 85))
                with c3: exibir_card("Transferência", r['Transf'], calcular_cor(r['Transf'], 85))

                c4, c5, c6 = st.columns(3)
                with c4: exibir_card("Absenteísmo", r['Absenteismo'], calcular_cor(r['Absenteismo'], 5, True))
                with c5: exibir_card("Pausa Total", r['Pausa Total'], calcular_cor(r['Pausa Total'], 10, True))
                with c6: exibir_card("Pesquisa (NPS)", r['Pesquisa'], "#FFD700", "⭐")

                st.markdown(f"""<div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #ddd;">
                    <h2 style="margin:0; color: #333;">⏱️ Seu TMA Voz: {r['TMA Voz']}</h2>
                </div>""", unsafe_allow_html=True)
            else: st.warning("Matrícula não encontrada.")

    # --- ABA EQUIPE ---
    with tab_equipe:
        eq = df[df['Operador'].str.strip() == 'EQUIPE']
        if not eq.empty:
            e = eq.iloc[0]
            st.subheader("📊 Médias Gerais da Sala")
            col1, col2, col3 = st.columns(3)
            with col1: exibir_card("Aderência Equipe", e['Aderencia'], calcular_cor(e['Aderencia'], 85))
            with col2: exibir_card("Resolutividade Equipe", e['Resolutividade'], calcular_cor(e['Resolutividade'], 85))
            with col3: exibir_card("Transf Equipe", e['Transf'], calcular_cor(e['Transf'], 85))

            col4, col5, col6 = st.columns(3)
            with col4: exibir_card("Absenteísmo Equipe", e['Absenteismo'], calcular_cor(e['Absenteismo'], 5, True))
            with col5: exibir_card("Pausa Total Equipe", e['Pausa Total'], calcular_cor(e['Pausa Total'], 10, True))
            with col6: exibir_card("NPS Médio Equipe", e['Pesquisa'], "#FFD700", "⭐")
            
            st.markdown(f"""<div style="background-color: #333; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="margin:0; color: white;">⏱️ TMA Médio da Equipe: {e['TMA Voz']}</h2>
            </div>""", unsafe_allow_html=True)

    # --- ABA MELHORES ---
    with tab_melhores:
        ranking_df = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
        if not ranking_df.empty:
            criar_podio(ranking_df, 'Aderencia', "Aderência")
            st.markdown("---")
            criar_podio(ranking_df, 'Resolutividade', "Resolutividade")
            st.markdown("---")
            criar_podio(ranking_df, 'Transf', "Transferência")

    # --- ABA GRÁFICOS ---
    with tab_grafico:
        st.header("📈 Saúde da Operação")
        df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
        
        def preparar_grafico(df, coluna, meta, menor_melhor=False):
            df['v_num'] = df[coluna].astype(str).str.replace('%', '').str.replace(',', '.').replace('nan', '0')
            df['v_num'] = pd.to_numeric(df['v_num'], errors='coerce').fillna(0)
            if menor_melhor:
                df['Status'] = df['v_num'].apply(lambda x: 'Dentro da Meta' if x <= meta else 'Fora da Meta')
            else:
                df['Status'] = df['v_num'].apply(lambda x: 'Dentro da Meta' if x >= meta else 'Fora da Meta')
            contagem = df['Status'].value_counts().reset_index()
            contagem.columns = ['Status', 'Quantidade']
            fig = px.pie(contagem, values='Quantidade', names='Status', hole=0.5,
                         color='Status', color_discrete_map={'Dentro da Meta':'#28a745', 'Fora da Meta':'#dc3545'})
            fig.update_layout(title=f"Visão: {coluna} (Meta: {meta}%)")
            return fig

        g1, g2 = st.columns(2)
        with g1: st.plotly_chart(preparar_grafico(df_ops, 'Aderencia', 85), use_container_width=True)
        with g2: st.plotly_chart(preparar_grafico(df_ops, 'Resolutividade', 85), use_container_width=True)
        
        g3, g4 = st.columns(2)
        with g3: st.plotly_chart(preparar_grafico(df_ops, 'Transf', 85), use_container_width=True)
        with g4: st.plotly_chart(preparar_grafico(df_ops, 'Absenteismo', 5, True), use_container_width=True)

st.markdown("---")
st.caption("Portal NDI | Performance Atualizada")
