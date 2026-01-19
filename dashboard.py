import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. DICIONÁRIO CENTRALIZADO DE METAS (Utilizado para Cores, Rankings e Saúde)
# Margem define o limite para a cor Amarela (Quase na Meta)
METAS = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Pausa Total': {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True}
}

# 3. FUNÇÕES DE TRATAMENTO E LÓGICA
def definir_cor_kpi(valor, metrica_key):
    """Lógica Semafórica: Verde (Dentro), Amarelo (Quase), Vermelho (Fora)"""
    config = METAS.get(metrica_key)
    if not config: return "#333"
    
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    
    if menor_melhor:
        if valor <= m: return "#28a745" # Verde
        if valor <= m + tol: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= m: return "#28a745" # Verde
        if valor >= m - tol: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

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

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {valor}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Garante que colunas extras de Pausas Prod/Improd existam para a visão geral
        for col in ['Pausa Produtiva', 'Pausa Improdutiva']:
            if col not in df.columns: df[col] = "00:00"

        # Processamento numérico baseado no dicionário de METAS
        for col in METAS.keys():
            if col in df.columns:
                df[f'{col}_num'] = df[col].apply(converter_tma_minutos if 'TMA' in col else converter_para_numero)
        return df
    except: return None

# --- UI PRINCIPAL ---
st.title("🚀 Portal de Performance NDI")
supervisores_lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
supervisor = st.selectbox("Selecione o seu Supervisor:", supervisores_lista)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde da Operação"])

        # 1. ABA INDIVIDUAL
        with tabs[0]:
            mat = st.text_input("Sua Matrícula:")
            if mat:
                res = df[df['Matricula'].astype(str).str.contains(mat.strip())]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r['Operador']}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'], 'Aderencia'))
                        exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'], 'Pesquisa'), "⭐")
                    with c2:
                        exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade'))
                        exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz'), "⏱️")
                    with c3:
                        exibir_card("Absenteísmo", r['Absenteismo'], definir_cor_kpi(r['Absenteismo_num'], 'Absenteismo'))
                        exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total'), "⏱️")
                    
                    st.divider()
                    st.caption("Métricas adicionais")
                    ca, cb = st.columns(2)
                    ca.info(f"Transferência: {r['Transf']}")
                    cb.info(f"Pausa Produtiva: {r['Pausa Produtiva']} | Improdutiva: {r['Pausa Improdutiva']}")
                else: st.warning("Matrícula não encontrada.")

        # 2. ABA EQUIPE (MÉDIA GERAL)
        with tabs[1]:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                st.subheader(f"Médias da Equipe: {supervisor}")
                cols = st.columns(3)
                for i, (k, v) in enumerate(METAS.items()):
                    with cols[i % 3]: 
                        exibir_card(f"{k} Equipe", e[k], definir_cor_kpi(e[f'{k}_num'], k))
            else: st.info("Linha 'EQUIPE' não encontrada.")

        # 3. ABA MELHORES (RANKINGS TOP 3)
        with tabs[2]:
            st.subheader("🏆 Melhores Resultados (Top 3)")
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            for k, v in METAS.items():
                st.markdown(f"#### Ranking: {k}")
                # Lógica: Menor é melhor para Abs, TMA e Pausa Total
                top = df_ops.nsmallest(3, f'{k}_num') if v['menor_melhor'] else df_ops.nlargest(3, f'{k}_num')
                mc = st.columns(3)
                medalhas = ["🥇","🥈","🥉"]
                for i, (_, row) in enumerate(top.iterrows()):
                    if i < 3:
                        with mc[i]: 
                            exibir_card(f"{i+1}º Lugar", row['Operador'], definir_cor_kpi(row[f'{k}_num'], k), medalhas[i])
                            st.caption(f"Valor: {row[k]}")
                st.divider()

        # 4. ABA SAÚDE DA OPERAÇÃO
        with tabs[3]:
            st.header("📊 Saúde da Operação")
            df_s = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            sel_saude = st.selectbox("Selecione a métrica para diagnóstico visual:", list(METAS.keys()))
            
            conf = METAS[sel_saude]
            mv, inv = conf['valor'], conf['menor_melhor']
            
            # Classificação para o gráfico de rosca
            df_s['Status'] = df_s[f'{sel_saude}_num'].apply(
                lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta'
            )
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                fig = px.pie(df_s, names='Status', hole=0.5, color='Status', 
                             color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'},
                             title=f"Distribuição de {sel_saude} (Meta: {mv})")
                st.plotly_chart(fig, use_container_width=True)
            with c_g2:
                st.subheader("Lista Detalhada")
                st.dataframe(df_s[['Operador', sel_saude, 'Status']], use_container_width=True, hide_index=True)

else:
    st.info("Aguardando seleção de supervisor.")
