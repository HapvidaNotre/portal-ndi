import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import copy

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# --- CSS AJUSTADO (Removendo conflitos de clique) ---
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .main-title { text-align: center; color: #004a99; margin-bottom: 20px; padding-top: 20px; }
    
    /* Estilização dos Cards */
    .metric-card {
        background-color: white; padding: 20px; border-radius: 12px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05); margin-bottom: 15px;
        border-left: 8px solid; transition: transform 0.2s;
    }
    .metric-card:hover { transform: translateX(5px); }
</style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# --- METAS ---
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'ShortCall': {'valor': 5.0, 'margem': 2.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Silencio': {'valor': 15.0, 'margem': 5.0, 'menor_melhor': True}
}

MATRICULAS_BACKOFFICE = ['1211819','1210820','1210724','1211110','1211213','1214016','10115858','1212492','1028483']

# --- FUNÇÕES ---
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
    txt = "—" if valor_display in [None,"nan","None","","---"] else str(valor_display)
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:bold;text-transform:uppercase;">{label}</p>
        <h2 style="margin:5px 0 0 0;color:#1f3a5f;font-size:24px;font-weight:800;">{icon} {txt}</h2>
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
        for m in list(METAS_BASE.keys()) + ['Pausa Total']:
            origem = cols_originais.get(m.lower())
            if origem:
                df[f'{m}_num'] = df[origem].apply(converter_tma_segundos if 'TMA' in m or 'Pausa' in m else limpar_valor_numerico)
                df[m] = df[origem].astype(str).replace(['nan','None'],'---')
            else:
                df[f'{m}_num'] = None
                df[m] = "---"
        return df, target_op, target_mat
    except: return None, None, None

# --- LÓGICA DE NAVEGAÇÃO: LOBBY ---
if st.session_state.servico is None:
    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p>Selecione sua operação</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    # Atribuir Keys únicas evita erros de estado no Streamlit
    if c1.button("🏢 SAC NDI", use_container_width=True, key="btn_ndi"):
        st.session_state.servico = "SAC NDI"
        st.rerun()
    if c2.button("🏦 SAC PPO", use_container_width=True, key="btn_ppo"):
        st.session_state.servico = "SAC PPO"
        st.rerun()
    if c3.button("🏥 SAC HAPVIDA", use_container_width=True, key="btn_hap"):
        st.session_state.servico = "SAC HAPVIDA"
        st.rerun()

# --- LÓGICA DE NAVEGAÇÃO: DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 📍 {st.session_state.servico}")
        lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"] if st.session_state.servico == "SAC NDI" else ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex", "Equipe Hapvida"]
        supervisor = st.selectbox("Escolha o Supervisor:", lista)
        st.markdown("---")
        # Botão de Voltar Corrigido
        if st.button("⬅️ Voltar ao Hub", use_container_width=True):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)
        if df is not None:
            metas_atuais = copy.deepcopy(METAS_BASE)
            metas_atuais['Pausa Total'] = {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True}
            
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            # ABA INDIVIDUAL
            with tabs[0]:
                mat = st.text_input("Digite sua Matrícula:", placeholder="Ex: 1234567")
                if mat:
                    res = df[df[col_mat].astype(str) == mat.strip()]
                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"## 👋 Olá, {r[col_op]}!")
                        c1, c2, c3 = st.columns(3)
                        with c1: 
                            exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'],'Aderencia', metas_atuais), "📈")
                            exibir_card("Silêncio", r['Silencio'], definir_cor_kpi(r['Silencio_num'],'Silencio', metas_atuais), "🔇")
                        with c2: 
                            exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'],'Resolutividade', metas_atuais), "✅")
                            exibir_card("Pausa Total", r['Pausa Total'], definir_cor_kpi(r['Pausa Total_num'],'Pausa Total', metas_atuais), "⏱️")
                        with c3: 
                            exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'],'TMA Voz', metas_atuais), "📞")
                            exibir_card("Pesquisa", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'],'Pesquisa', metas_atuais), "⭐")

            # ABA EQUIPE - GRÁFICO REFORMULADO
            with tabs[1]:
                st.markdown(f"### Comparativo da Equipe - {supervisor}")
                metrica_sel = st.selectbox("Selecione o indicador para comparar:", list(metas_atuais.keys()))
                
                # Filtragem para o gráfico
                df_grafico = df[
                    (df[col_op].astype(str).str.upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & 
                    (df[f'{metrica_sel}_num'].notna())
                ].copy()

                if not df_grafico.empty:
                    conf = metas_atuais[metrica_sel]
                    # Lógica de cor individual por barra
                    df_grafico['Cor'] = df_grafico[f'{metrica_sel}_num'].apply(
                        lambda x: '#28a745' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else '#dc3545'
                    )
                    
                    # Ordenar para facilitar a leitura (do melhor para o pior)
                    df_grafico = df_grafico.sort_values(by=f'{metrica_sel}_num', ascending=not conf['menor_melhor'])

                    # Criar Gráfico de Barras Horizontal
                    fig = px.bar(
                        df_grafico,
                        x=f'{metrica_sel}_num',
                        y=col_op,
                        orientation='h',
                        text=metrica_sel,
                        color='Cor',
                        color_discrete_map="identity",
                        labels={f'{metrica_sel}_num': 'Resultado', col_op: 'Operador'}
                    )
                    
                    # Linha de Meta Vertical
                    fig.add_vline(x=conf['valor'], line_dash="dash", line_color="black", 
                                 annotation_text=f" META: {conf['valor']}", annotation_position="top right")

                    fig.update_layout(showlegend=False, height=max(400, len(df_grafico)*30), margin=dict(l=0, r=0, t=30, b=0))
                    st.plotly_chart(fig, use_container_width=True)
                    st.success(f"💡 Barras **verdes** estão dentro da meta ({conf['valor']}).")
                else:
                    st.warning("Dados insuficientes para gerar o gráfico desta métrica.")

            # ABA RANKING
            with tabs[2]:
                m_rank = st.selectbox("Ver Ranking de:", list(metas_atuais.keys()), key="rank_sel")
                df_rank = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_rank}_num'].notna())].copy()
                if not df_rank.empty:
                    top = df_rank.sort_values(by=f'{m_rank}_num', ascending=metas_atuais[m_rank]['menor_melhor']).head(5)
                    for i, (_, row) in enumerate(top.iterrows()):
                        exibir_card(f"{i+1}º Lugar - {row[col_op]}", row[m_rank], "#28a745", "🏆")

            # ABA SAÚDE
            with tabs[3]:
                m_saude = st.selectbox("Analisar Saúde de:", list(metas_atuais.keys()), key="saude_sel")
                df_s = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_saude}_num'].notna())].copy()
                if not df_s.empty:
                    conf = metas_atuais[m_saude]
                    df_s['Status'] = df_s[f'{m_saude}_num'].apply(lambda x: 'Meta OK' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                    fig_p = px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Meta OK': '#28a745', 'Fora da Meta': '#dc3545'})
                    st.plotly_chart(fig_p)
