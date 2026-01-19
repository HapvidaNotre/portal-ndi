import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÕES INICIAIS
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SUPERVISORES = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]

# 2. FUNÇÕES DE TRATAMENTO
def converter_para_numero(valor):
    if pd.isna(valor): return 0.0
    try:
        return float(str(valor).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def converter_tma_minutos(tempo_str):
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

def definir_cor_kpi(valor, meta, margem, menor_melhor=False):
    if menor_melhor:
        if valor <= meta: return "#28a745"
        if valor <= meta + margem: return "#ffc107"
        return "#dc3545"
    else:
        if valor >= meta: return "#28a745"
        if valor >= meta - margem: return "#ffc107"
        return "#dc3545"

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 12px; border-radius: 10px; border-left: 6px solid {cor}; 
             box-shadow: 2px 2px 6px rgba(0,0,0,0.1); margin-bottom: 8px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h4 style="margin: 2px 0 0 0; color: {cor}; font-size: 18px;">{icon} {valor}</h4>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        if 'Matricula' in df.columns:
            df['Matricula'] = df['Matricula'].astype(str).str.split('.').str[0].str.strip()
        
        # Processamento de todas as métricas solicitadas
        colunas_percent = ['Aderencia', 'Absenteismo', 'Transf', 'Resolutividade']
        for col in colunas_percent:
            if col in df.columns: df[f'{col}_num'] = df[col].apply(converter_para_numero)
        
        if 'Pesquisa' in df.columns: df['Pesquisa_num'] = df['Pesquisa'].apply(converter_para_numero)
        
        colunas_tempo = ['TMA Voz', 'Pausa Produtiva', 'Pausa Improdutiva', 'Pausa Total']
        for col in colunas_tempo:
            if col in df.columns: df[f'{col}_num'] = df[col].apply(converter_tma_minutos)
            
        return df
    except: return None

# --- INTERFACE PRINCIPAL ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        # Abas solicitadas
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Saúde da Operação"])

        # 1. ABA INDIVIDUAL
        with tabs[0]:
            mat = st.text_input("Digite sua Matrícula:")
            if mat:
                res = df[df['Matricula'] == mat.strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r.get('Operador', 'Colaborador')}")
                    c1, c2, c3 = st.columns(3)
                    with c1: 
                        exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r.get('Aderencia_num', 0), 85, 5))
                        exibir_card("Absenteísmo", r.get('Absenteismo', '0%'), definir_cor_kpi(r.get('Abs_num', 0), 5, 2, True))
                        exibir_card("Pausa Produtiva", r.get('Pausa Produtiva', '00:00'), "#1f77b4", "⏱️")
                    with c2:
                        exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r.get('Resolutividade_num', 0), 85, 5))
                        exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r.get('TMA_num', 0), 8.0, 1.0, True), "⏱️")
                        exibir_card("Pausa Improdutiva", r.get('Pausa Improdutiva', '00:00'), "#333", "⏱️")
                    with c3:
                        exibir_card("NPS (Pesquisa)", r.get('Pesquisa', '0'), definir_cor_kpi(r.get('Pesquisa_num', 0), 4.5, 0.5))
                        exibir_card("Transferência", r.get('Transf', '0%'), "#6c757d")
                        exibir_card("Pausa Total", r.get('Pausa Total', '00:00'), "#333", "⏱️")

        # 2. ABA EQUIPE (TODAS AS MÉTRICAS)
        with tabs[1]:
            st.subheader(f"Visão Consolidada: {supervisor}")
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                cols = st.columns(3)
                metricas_eq = [
                    ("Aderência Equipe", 'Aderencia'), ("Resolutividade Equipe", 'Resolutividade'), ("TMA Médio", 'TMA Voz'),
                    ("NPS Médio", 'Pesquisa'), ("Absenteísmo", 'Absenteismo'), ("Transferência", 'Transf'),
                    ("Pausa Produtiva", 'Pausa Produtiva'), ("Pausa Improdutiva", 'Pausa Improdutiva'), ("Pausa Total", 'Pausa Total')
                ]
                for i, (label, col_nome) in enumerate(metricas_eq):
                    with cols[i % 3]: exibir_card(label, e.get(col_nome, 'N/A'), "#007bff")
            else: st.info("Linha 'EQUIPE' não localizada na planilha.")

        # 3. ABA MELHORES (RANKING TOP 3 - TODAS AS MÉTRICAS)
        with tabs[2]:
            st.subheader("🏆 Ranking Top 3 por Categoria")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            def gerar_podio(col_num, col_texto, titulo, icone, meta, menor_melhor=False):
                st.markdown(f"#### {icone} {titulo}")
                # Ajuste de lógica: Para TMA e Absenteísmo, os menores valores são os melhores
                top = df_ops.nsmallest(3, col_num) if menor_melhor else df_ops.nlargest(3, col_num)
                m1, m2, m3 = st.columns(3)
                for i, (idx, row) in enumerate(top.iterrows()):
                    cor = definir_cor_kpi(row[col_num], meta, 5, menor_melhor)
                    with [m1, m2, m3][i]:
                        exibir_card(f"{i+1}º LUGAR", row['Operador'], cor, ["🥇","🥈","🥉"][i])
                        st.caption(f"Resultado: {row[col_texto]}")
                st.divider()

            gerar_podio('Aderencia_num', 'Aderencia', "Destaques Aderência", "🎯", 85)
            gerar_podio('Resolutividade_num', 'Resolutividade', "Destaques Resolutividade", "✅", 85)
            gerar_podio('TMA_num', 'TMA Voz', "Destaques TMA (Meta 08:00)", "⏱️", 8, True)
            gerar_podio('Pesquisa_num', 'Pesquisa', "Destaques NPS", "⭐", 4.5)
            gerar_podio('Abs_num', 'Absenteismo', "Menor Absenteísmo", "📉", 5, True)

        # 4. ABA SAÚDE DA OPERAÇÃO (DIAGNÓSTICO COMPLETO)
        with tabs[3]:
            st.header("📊 Saúde da Operação")
            df_ops_g = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            metrica_analise = st.selectbox("Escolha a métrica para diagnóstico:", 
                ["Aderencia", "Resolutividade", "TMA Voz", "Pesquisa", "Absenteismo"])
            
            # Lógica de Meta para o Gráfico de Rosca
            meta_map = {"Aderencia": 85, "Resolutividade": 85, "TMA Voz": 8, "Pesquisa": 4.5, "Absenteismo": 5}
            inv_map = {"Aderencia": False, "Resolutividade": False, "TMA Voz": True, "Pesquisa": False, "Absenteismo": True}
            
            meta_val = meta_map[metrica_analise]
            is_inv = inv_map[metrica_analise]
            col_ref = f"{metrica_analise.split()[0]}_num" if "TMA" not in metrica_analise else "TMA_num"
            
            if is_inv: df_ops_g['Status'] = df_ops_g[col_ref].apply(lambda x: 'Dentro da Meta' if x <= meta_val else 'Fora da Meta')
            else: df_ops_g['Status'] = df_ops_g[col_ref].apply(lambda x: 'Dentro da Meta' if x >= meta_val else 'Fora da Meta')
            
            c_g1, c_g2 = st.columns([1, 1])
            with c_g1:
                fig = px.pie(df_ops_g, names='Status', hole=0.5, color='Status', 
                             color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'},
                             title=f"Visão: {metrica_analise}")
                st.plotly_chart(fig, use_container_width=True)
            with c_g2:
                st.subheader("Lista de Operadores")
                st.dataframe(df_ops_g[['Operador', metrica_analise, 'Status']], use_container_width=True, hide_index=True)
