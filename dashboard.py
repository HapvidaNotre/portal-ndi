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

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI - SP")
data_att = obter_data_atualizacao()
st.info(f"📅 **Última atualização:** {data_att}")

df = carregar_dados()

if df is not None:
    tab_ind, tab_equipe = st.tabs(["👤 Métricas Individuais", "👥 Métricas Equipe"])

    with tab_ind:
        matricula_busca = st.text_input("Olá! Digite sua Matrícula para começar:", placeholder="Ex: 1039456")
        
        if matricula_busca:
            colaborador = df[df['Matricula'] == str(matricula_busca).strip()]
            
            if not colaborador.empty:
                res = colaborador.iloc[0]
                nome = res.get('Operador', 'Colaborador')
                st.subheader(f"Bem-vindo(a), {nome}!")
                
                # Lógica de Cards
                cores = []
                c1, c2, c3 = st.columns(3)
                with c1: cores.append(exibir_metricas("Aderência", res.get('Aderencia', 0), 95))
                with c2: cores.append(exibir_metricas("Resolutividade", res.get('Resolutividade', 0), 85))
                with c3: cores.append(exibir_metricas("Transf", res.get('Transf', 0), 85))

                c4, c5, c6 = st.columns(3)
                with c4: cores.append(exibir_metricas("Absenteísmo", res.get('Absenteismo', 0), 5, menor_melhor=True))
                with c5: cores.append(exibir_metricas("Pausa Total", res.get('Pausa Total', 0), 10, menor_melhor=True))
                with c6: st.info(f"⏱️ **TMA Voz:** {res.get('TMA Voz', '00:00:00')}")

                # Mensagem Dinâmica Motivacional
                st.markdown("---")
                if all(c == "green" for c in cores):
                    st.balloons()
                    st.success(f"🌟 **Incrível, {nome}!** Você está batendo todas as metas. Continue com esse foco!")
                elif cores.count("green") >= 3:
                    st.info(f"👍 **Bom trabalho, {nome}!** Você está no caminho certo. Ajuste os detalhes para ficar 100% verde!")
                else:
                    st.warning(f"💪 **Vamo pra cima, {nome}!** Identifique onde está o desafio e peça ajuda se precisar. Você consegue!")
            else:
                st.warning("Matrícula não encontrada.")

    with tab_equipe:
        # --- RANKING TOP 3 ---
        st.subheader("🏆 Destaques da Equipe (Resolutividade)")
        ranking_df = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
        
        # Converte resolutividade para número para o ranking
        ranking_df['Res_Num'] = ranking_df['Resolutividade'].astype(str).str.replace('%', '').str.replace(',', '.').astype(float)
        top_3 = ranking_df.nlargest(3, 'Res_Num')

        r1, r2, r3 = st.columns(3)
        podio = ["🥇 1º Lugar", "🥈 2º Lugar", "🥉 3º Lugar"]
        cols = [r1, r2, r3]
        for i, (idx, row) in enumerate(top_3.iterrows()):
            with cols[i]:
                st.markdown(f"""
                    <div style="text-align: center; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 2px solid #e9ecef;">
                        <h4 style="margin:0; color: #1f77b4;">{podio[i]}</h4>
                        <p style="font-size: 16px; font-weight: bold; margin:5px 0;">{row['Operador']}</p>
                        <span style="background-color: #d4edda; color: #155724; padding: 2px 10px; border-radius: 15px; font-size: 14px;">{row['Resolutividade']}</span>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("---")
        
        # --- MÉTRICAS GERAIS ---
        dados_equipe = df[df['Operador'].str.strip() == 'EQUIPE']
        if not dados_equipe.empty:
            res_eq = dados_equipe.iloc[0]
            st.subheader("📊 Média Geral do Time")
            e1, e2, e3 = st.columns(3)
            with e1: exibir_metricas("Aderência Equipe", res_eq.get('Aderencia', 0), 95)
            with e2: exibir_metricas("Resolutividade Equipe", res_eq.get('Resolutividade', 0), 85)
            with e3: exibir_metricas("Transf Equipe", res_eq.get('Transf', 0), 85)
            
            st.markdown(f"**TMA Médio da Sala:** `{res_eq.get('TMA Voz', '00:00:00')}`")
        else:
            st.warning("Linha 'EQUIPE' não encontrada na planilha.")

st.markdown("---")
st.caption("Portal de Performance NDI | Transparência e Reconhecimento")
