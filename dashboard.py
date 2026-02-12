import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import copy

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# --- 2. ESTILIZAÇÃO CSS CUSTOMIZADA ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-title { text-align: center; color: #004a99; margin-bottom: 20px; padding-top: 20px; }
    
    /* Cards de Métricas Individuais */
    .metric-card {
        background-color: white; padding: 15px; border-radius: 10px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.05); border-left: 6px solid;
        margin-bottom: 10px;
    }
    
    /* Dashboard de Médias da Equipe */
    .team-summary-container {
        background-color: #ffffff; padding: 25px; border-radius: 15px;
        border: 1px solid #e0e0e0; margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    
    /* Botões do Hub */
    div.stButton > button {
        width: 100%; height: 120px !important; border-radius: 12px;
        font-size: 18px !important; font-weight: bold !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURAÇÕES DE METAS E NEGÓCIO ---
if 'servico' not in st.session_state:
    st.session_state.servico = None

METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False, 'unidade': '%'},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True, 'unidade': ' min'},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False, 'unidade': ''},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True, 'unidade': '%'},
    'Pausa Total': {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True, 'unidade': ' min'}
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# --- 4. FUNÇÕES DE SUPORTE (DATA ENGINE) ---
def limpar_valor_numerico(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "None", "—", "nan", "---"]: return None
    try: return float(str(valor).replace('%','').replace(',','.'))
    except: return None

def converter_tma_segundos(valor):
    if pd.isna(valor) or str(valor).strip() in ["","0","00:00:00","None"]: return None
    try:
        p = str(valor).split(':')
        if len(p)==3: return int(p[0])*60 + int(p[1]) + int(p[2])/60
        return float(str(valor).replace(',','.'))
    except: return None

def definir_cor_kpi(valor_num, metrica, metas):
    if valor_num is None: return "#999"
    conf = metas.get(metrica)
    if not conf: return "#333"
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']
    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m + tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m - tol else "#dc3545")

def exibir_card(label, valor_display, cor="#333", icon=""):
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:bold;text-transform:uppercase;">{label}</p>
        <h4 style="margin:5px 0 0 0;color:#1f3a5f;font-weight:800;">{icon} {valor_display}</h4>
    </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados_aba(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ','%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        cols_originais = {c.lower(): c for c in df.columns}
        target_op = cols_originais.get('operador', 'Operador')
        target_mat = cols_originais.get('matricula', 'Matricula')
        for m in list(METAS_BASE.keys()):
            origem = cols_originais.get(m.lower())
            if origem:
                df[f'{m}_num'] = df[origem].apply(converter_tma_segundos if 'TMA' in m or 'Pausa' in m else limpar_valor_numerico)
                df[m] = df[origem].astype(str).replace(['nan','None'],'---')
        return df, target_op, target_mat
    except: return None, None, None

# --- 5. LÓGICA DE NAVEGAÇÃO: HUB (LOBBY) ---
if st.session_state.servico is None:
    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p>Selecione sua operação para continuar</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("🏢 SAC NDI", key="btn_ndi"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with c2:
        if st.button("🏦 SAC PPO", key="btn_ppo"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with c3:
        if st.button("🏥 SAC HAPVIDA", key="btn_hap"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

# --- 6. LÓGICA DE NAVEGAÇÃO: DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 📍 {st.session_state.servico}")
        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        else:
            lista = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
            
        supervisor = st.selectbox("Escolha o Supervisor:", lista)
        st.divider()
        if st.button("⬅️ Voltar ao Hub", use_container_width=True):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)
        
        if df is not None:
            t1, t2, t3, t4 = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            # --- ABA 1: INDIVIDUAL ---
            with t1:
                mat = st.text_input("Digite sua Matrícula:", placeholder="Ex: 1234567")
                if mat:
                    res = df[df[col_mat].astype(str) == mat.strip()]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"## 👋 Olá, {r[col_op]}!")
                        c1, c2, c3 = st.columns(3)
                        with c1: 
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'],'Aderencia', METAS_BASE), "📈")
                            exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'],'Silencio', METAS_BASE), "🔇")
                        with c2: 
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'],'Resolutividade', METAS_BASE), "✅")
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'],'Pausa Total', METAS_BASE), "⏱️")
                        with c3: 
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'],'TMA Voz', METAS_BASE), "📞")
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'],'Pesquisa', METAS_BASE), "⭐")
                    else: st.warning("Matrícula não encontrada nesta equipe.")

            # --- ABA 2: EQUIPE (MÉDIAS + GRÁFICO) ---
            with t2:
                st.markdown(f"### 📊 Dashboard da Equipe - {supervisor}")
                
                # Filtragem de dados (Remove linha totalizadora e backoffice)
                df_eq = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                           (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE))].copy()

                # SEÇÃO: RESUMO DE MÉDIAS
                st.markdown('<div class="team-summary-container">', unsafe_allow_html=True)
                cols = st.columns(len(METAS_BASE))
                for i, (metrica, conf) in enumerate(METAS_BASE.items()):
                    media_valor = df_eq[f'{metrica}_num'].mean()
                    cor = definir_cor_kpi(media_valor, metrica, METAS_BASE)
                    txt_media = f"{media_valor:.1f}{conf['unidade']}" if not pd.isna(media_valor) else "---"
                    with cols[i]:
                        exibir_card(metrica, txt_media, cor)
                st.markdown('</div>', unsafe_allow_html=True)

                # SEÇÃO: GRÁFICO COMPARATIVO
                st.divider()
                metrica_sel = st.selectbox("Escolha a métrica para detalhar o time:", list(METAS_BASE.keys()))
                conf_sel = METAS_BASE[metrica_sel]
                
                df_grafico = df_eq[df_eq[f'{metrica_sel}_num'].notna()].sort_values(by=f'{metrica_sel}_num', ascending=not conf_sel['menor_melhor'])
                
                # Cores dinâmicas para as barras
                df_grafico['Cor'] = df_grafico[f'{metrica_sel}_num'].apply(
                    lambda x: '#28a745' if (x <= conf_sel['valor'] if conf_sel['menor_melhor'] else x >= conf_sel['valor']) else '#dc3545'
                )

                fig = px.bar(df_grafico, x=f'{metrica_sel}_num', y=col_op, orientation='h',
                             text=metrica_sel, color='Cor', color_discrete_map="identity",
                             title=f"Desempenho por Colaborador: {metrica_sel}")
                
                fig.add_vline(x=conf_sel['valor'], line_dash="dash", line_color="black", annotation_text=f"Meta: {conf_sel['valor']}")
                fig.update_layout(height=max(400, len(df_grafico)*25), showlegend=False, margin=dict(l=0, r=10, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)

            # --- ABA 3: RANKING ---
            with t3:
                m_rank = st.selectbox("Ranking de:", list(METAS_BASE.keys()), key="rank_sel")
                top = df_eq[df_eq[f'{m_rank}_num'].notna()].sort_values(by=f'{m_rank}_num', ascending=METAS_BASE[m_rank]['menor_melhor']).head(5)
                for i, (_, row) in enumerate(top.iterrows()):
                    exibir_card(f"{i+1}º Lugar - {row[col_op]}", row[m_rank], "#28a745", "🏆")

            # --- ABA 4: SAÚDE (DISTRIBUIÇÃO) ---
            with t4:
                m_saude = st.selectbox("Status da Equipe:", list(METAS_BASE.keys()), key="saude_sel")
                conf = METAS_BASE[m_saude]
                df_eq['Status'] = df_eq[f'{m_saude}_num'].apply(lambda x: 'Meta OK' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                fig_p = px.pie(df_eq, names='Status', hole=0.5, color='Status', color_discrete_map={'Meta OK': '#28a745', 'Fora da Meta': '#dc3545'})
                st.plotly_chart(fig_p)
