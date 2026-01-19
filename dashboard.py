import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. CONFIGURAÇÃO DA PLANILHA MESTRE
SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
SUPERVISORES = [
    "Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", 
    "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"
]

# 3. FUNÇÕES DE SUPORTE
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
    """Lógica de Semáforo: Verde (Meta), Amarelo (Atenção), Vermelho (Fora)"""
    if menor_melhor:
        if valor <= meta: return "#28a745" # Verde
        if valor <= meta + margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= meta: return "#28a745" # Verde
        if valor >= meta - margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 12px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 22px;">{icon} {valor}</h2>
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

        # Mapeamento e criação automática de colunas numéricas
        metricas_alvo = [
            'Aderencia', 'Absenteismo', 'Transf', 'TMA Voz', 'Pesquisa', 
            'Resolutividade', 'Pausa Produtiva', 'Pausa Improdutiva', 'Pausa Total'
        ]
        
        for col in metricas_alvo:
            if col in df.columns:
                if any(x in col for x in ['TMA']):
                    df[f'{col}_num'] = df[col].apply(converter_tma_minutos)
                else:
                    df[f'{col}_num'] = df[col].apply(converter_para_numero)
            else:
                df[col] = "0"
                df[f'{col}_num'] = 0.0
        return df
    except: return None

# --- INTERFACE PRINCIPAL ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde da Operação"])

        # --- 1. ABA INDIVIDUAL ---
        with tabs[0]:
            mat = st.text_input("Digite sua Matrícula para ver seus resultados:")
            if mat:
                res = df[df['Matricula'] == mat.strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r['Operador']}")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'], 85, 5))
                        exibir_card("Pausa Produtiva", r['Pausa Produtiva'], "#1f77b4", "⏱️")
                    with c2:
                        exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 85, 5))
                        exibir_card("Pausa Improdutiva", r['Pausa Improdutiva'], "#6c757d", "⏱️")
                    with c3:
                        exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'], 8, 1, True), "⏱️")
                        exibir_card("Absenteísmo", r['Absenteismo'], definir_cor_kpi(r['Absenteismo_num'], 5, 2, True))
                    
                    c4, c5, c6 = st.columns(3)
                    with c4: exibir_card("NPS (Pesquisa)", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'], 4.5, 0.5))
                    with c5: exibir_card("Transferência", r['Transf'], "#6c757d")
                    with c6: exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'], 21.75, 2, True), "⏱️")
                else: st.warning("Matrícula não encontrada.")

        # --- 2. ABA EQUIPE (MÉDIA GERAL) ---
        with tabs[1]:
            st.subheader(f"Visão Consolidada: {supervisor}")
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                cols = st.columns(3)
                met_list = [
                    ('Aderência Equipe', 'Aderencia'), ('Absenteísmo Equipe', 'Absenteismo'), ('Transferência Equipe', 'Transf'),
                    ('TMA Médio', 'TMA Voz'), ('NPS Médio', 'Pesquisa'), ('Resolutividade Equipe', 'Resolutividade'),
                    ('Pausa Produtiva', 'Pausa Produtiva'), ('Pausa Improdutiva', 'Pausa Improdutiva'), ('Pausa Total', 'Pausa Total')
                ]
                for i, (lab, col) in enumerate(met_list):
                    with cols[i % 3]: exibir_card(lab, e[col], "#007bff")

        # --- 3. ABA MELHORES (RANKING TOP 3) ---
        with tabs[2]:
            st.subheader("🏆 Melhores Resultados")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            def podio(col_num, col_txt, titulo, meta, inverter=False):
                st.markdown(f"#### {titulo}")
                top = df_ops.nsmallest(3, col_num) if inverter else df_ops.nlargest(3, col_num)
                m1, m2, m3 = st.columns(3)
                medalhas = ["🥇","🥈","🥉"]
                for i, (idx, row) in enumerate(top.iterrows()):
                    cor = definir_cor_kpi(row[col_num], meta, 2, inverter)
                    with [m1, m2, m3][i]:
                        exibir_card(f"{i+1}º Lugar", row['Operador'], cor, medalhas[i])
                        st.caption(f"Valor: {row[col_txt]}")
                st.divider()

            podio('Aderencia_num', 'Aderencia', "Destaques em Aderência (Meta 85%)", 85)
            podio('Resolutividade_num', 'Resolutividade', "Destaques em Resolutividade (Meta 85%)", 85)
            podio('TMA Voz_num', 'TMA Voz', "Destaques TMA (Meta 08:00)", 8, True)
            podio('Pesquisa_num', 'Pesquisa', "Destaques NPS (Meta 4.5)", 4.5)
            podio('Absenteismo_num', 'Absenteismo', "Menores Absenteísmos", 5, True)
            
            # Ranking de Pausa Total atualizado para Meta 21.75%
            podio('Pausa Total_num', 'Pausa Total', "Menor Tempo de Pausa Total (Meta 21,75%)", 21.75, True)

        # --- 4. ABA SAÚDE DA OPERAÇÃO ---
        with tabs[3]:
            st.header("📊 Saúde da Operação")
            df_s = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            sel = st.selectbox("Selecione a métrica para diagnóstico:", 
                              ["Aderencia", "Resolutividade", "TMA Voz", "Pesquisa", "Absenteismo", "Pausa Total"])
            
            # Ajuste de metas para o diagnóstico
            metas = {"TMA Voz": 8.0, "Absenteismo": 5.0, "Pesquisa": 4.5, "Pausa Total": 21.75}
            mv = metas.get(sel, 85.0)
            inv = True if sel in ["TMA Voz", "Absenteismo", "Pausa Total"] else False
            
            df_s['Status'] = df_s[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
            
            c_s1, c_s2 = st.columns(2)
            with c_s1:
                fig = px.pie(df_s, names='Status', hole=0.5, color='Status', 
                             color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'},
                             title=f"Distribuição de {sel}")
                st.plotly_chart(fig, use_container_width=True)
            with c_s2:
                st.subheader("Lista Detalhada")
                st.dataframe(df_s[['Operador', sel, 'Status']], use_container_width=True, hide_index=True)
