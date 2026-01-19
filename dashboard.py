import streamlit as st
import pandas as pd
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
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        
        # Mapeamento de colunas para garantir que TMA e NPS sejam encontrados
        map_cols = {'TMA Voz': ['TMA', 'TMA Voz'], 'Pesquisa': ['NPS', 'Pesquisa']}
        for oficial, vars in map_cols.items():
            for v in vars:
                if v in df.columns and oficial not in df.columns: df[oficial] = df[v]
        
        # Conversão numérica para cores e gráficos
        for col in ['Aderencia', 'Resolutividade', 'Pesquisa']:
            if col in df.columns:
                df[f'{col}_num'] = pd.to_numeric(df[col].astype(str).str.replace('%', '').str.replace(',', '.'), errors='coerce').fillna(0)
        return df
    except: return None

def definir_cor(valor, meta, margem_amarela=5, menor_melhor=False):
    """Lógica de cores: Verde, Amarelo e Vermelho"""
    if menor_melhor:
        if valor <= meta: return "#28a745" # Verde
        if valor <= meta + margem_amarela: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= meta: return "#28a745" # Verde
        if valor >= meta - margem_amarela: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 20px; border-radius: 12px; border-left: 10px solid {cor}; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); margin-bottom: 15px;">
            <p style="margin: 0; font-size: 13px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 26px;">{icon} {valor}</h2>
        </div>
    """, unsafe_allow_html=True)

# --- INTERFACE PRINCIPAL ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Para começar, selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados_aba(supervisor)
    if df is not None:
        tab_ind, tab_eq, tab_melhores, tab_grafico = st.tabs(["👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Saúde"])

        with tab_ind:
            mat = st.text_input("Digite sua Matrícula:")
            if mat:
                res = df[df['Matricula'] == mat.strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r.get('Operador', 'Colaborador')}")
                    
                    # Linha 1: Métricas Principais
                    c1, c2, c3 = st.columns(3)
                    with c1: exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor(r.get('Aderencia_num', 0), 85))
                    with c2: exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor(r.get('Resolutividade_num', 0), 85))
                    with c3: exibir_card("Transferência", r.get('Transf', '0%'), "#6c757d")

                    # Linha 2: TMA e NPS em Blocos
                    c4, c5 = st.columns(2)
                    with c4: exibir_card("TMA Voz", r.get('TMA Voz', '00:00:00'), "#1f77b4", "⏱️")
                    with c5: exibir_card("NPS (Pesquisa)", r.get('Pesquisa', '0,0'), definir_cor(r.get('Pesquisa_num', 0), 4.5, margem_amarela=0.5))
                else: st.warning("Matrícula não encontrada.")

        with tab_eq:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                st.subheader(f"Média Geral: {supervisor}")
                col1, col2, col3 = st.columns(3)
                with col1: exibir_card("Aderência Equipe", e.get('Aderencia', '0%'), "#28a745")
                with col2: exibir_card("Resolutividade Equipe", e.get('Resolutividade', '0%'), "#007bff")
                with col3: exibir_card("TMA Médio", e.get('TMA Voz', '00:00:00'), "#1f77b4", "⏱️")

        with tab_melhores:
            st.subheader(f"🏆 Top 3 por Categoria - {supervisor}")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops.empty:
                def gerar_podio(col, titulo, icone, meta_ref):
                    st.markdown(f"#### {icone} {titulo}")
                    top = df_ops.nlargest(3, f"{col}_num")
                    m1, m2, m3 = st.columns(3)
                    for i, (idx, row) in enumerate(top.iterrows()):
                        cor = definir_cor(row[f"{col}_num"], meta_ref)
                        with [m1, m2, m3][i]:
                            exibir_card(f"{i+1}º LUGAR", row['Operador'], cor, ["🥇","🥈","🥉"][i])
                    st.markdown("---")
                gerar_podio('Aderencia', 'Destaques em Aderência', "🎯", 85)
                gerar_podio('Resolutividade', 'Destaques em Resolutividade', "✅", 85)

        with tab_grafico:
            st.header("📊 Saúde da Operação")
            df_ops_g = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            if not df_ops_g.empty:
                df_ops_g['Status'] = df_ops_g['Aderencia_num'].apply(lambda x: 'Dentro da Meta' if x >= 85 else 'Fora da Meta')
                fig = px.pie(df_ops_g, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)
