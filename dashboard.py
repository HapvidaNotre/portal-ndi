import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import copy

# CONFIG
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# CSS
st.markdown("""
<style>
.stApp { background-color: #f8f9fa; }

.main-title { 
    text-align: center; 
    color: #004a99; 
    margin-bottom: 20px; 
    padding-top: 20px;
}

.hub-container {
    display: flex;
    justify-content: center;
    gap: 60px;
    margin-top: 60px;
    flex-wrap: wrap;
}

.stButton > button {
    min-height: 220px;
    transition: all 0.3s ease-in-out;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,74,153,0.15);
}

.metric-card {
    background-color: white; 
    padding: 20px; 
    border-radius: 12px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.05); 
    margin-bottom: 15px; 
    border-left: 8px solid;
    transition: transform 0.2s;
}

.metric-card:hover {
    transform: translateX(5px);
}

.info-box {
    background-color: #e7f3ff;
    border-left: 4px solid #004a99;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}

.warning-box {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# METAS
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

# FUNCOES
def limpar_valor_numerico(valor):
    if pd.isna(valor) or str(valor).strip() in ["", "None", "—", "nan"]:
        return None
    try:
        return float(str(valor).replace('%','').replace(',','.'))
    except:
        return None

def converter_tma_segundos(valor):
    if pd.isna(valor) or str(valor).strip() in ["","0","00:00:00","None"]:
        return None
    try:
        p = str(valor).split(':')
        if len(p)==3:
            return int(p[0])*60 + int(p[1]) + int(p[2])/60
        return float(str(valor).replace(',','.'))
    except:
        return None

def definir_cor_kpi(valor_num, metrica, metas):
    if valor_num is None: return "#999"
    conf = metas.get(metrica)
    if not conf: return "#333"
    
    m, tol, menor = conf['valor'], conf['margem'], conf['menor_melhor']

    if menor:
        return "#28a745" if valor_num <= m else ("#ffc107" if valor_num <= m + tol else "#dc3545")
    return "#28a745" if valor_num >= m else ("#ffc107" if valor_num >= m - tol else "#dc3545")

def exibir_card(label, valor_display, cor="#333", icon=""):
    txt = "—" if valor_display in [None,"nan","None",""] else str(valor_display)
    st.markdown(f"""
    <div class="metric-card" style="border-left-color:{cor};">
        <p style="margin:0;font-size:11px;color:#666;font-weight:bold;text-transform:uppercase;">
            {label}
        </p>
        <h2 style="margin:5px 0 0 0;color:#1f3a5f;font-size:24px;font-weight:800;">
            {icon} {txt}
        </h2>
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
                df[f'{m}_num'] = df[origem].apply(
                    converter_tma_segundos if 'TMA' in m or 'Pausa' in m else limpar_valor_numerico
                )
                df[m] = df[origem].astype(str).replace(['nan','None'],'---')
            else:
                df[f'{m}_num'] = None
                df[m] = "---"

        return df, target_op, target_mat
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        return None, None, None

def calcular_estatisticas_equipe(df, metrica, col_op, col_mat, metas):
    df_filtrado = df[
        (df[col_op].astype(str).str.upper() != 'EQUIPE') &
        (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) &
        (df[f'{metrica}_num'].notna())
    ].copy()

    if df_filtrado.empty:
        return None

    valores = df_filtrado[f'{metrica}_num']
    conf = metas.get(metrica, {})

    stats = {
        'media': valores.mean(),
        'mediana': valores.median(),
        'minimo': valores.min(),
        'maximo': valores.max(),
        'total_operadores': len(valores),
        'meta': conf.get('valor'),
        'menor_melhor': conf.get('menor_melhor', False)
    }

    if conf:
        if conf['menor_melhor']:
            na_meta = (valores <= conf['valor']).sum()
        else:
            na_meta = (valores >= conf['valor']).sum()
        stats['perc_meta'] = (na_meta / len(valores)) * 100

    return stats

# HUB
if st.session_state.servico is None:
    st.markdown("<div class='main-title'><h1>🚀 Portal de Performance NDI</h1><p>Selecione sua operação</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🏢 SAC NDI", use_container_width=True):
            st.session_state.servico = "SAC NDI"
            st.rerun()

    with col2:
        if st.button("🏦 SAC PPO", use_container_width=True):
            st.session_state.servico = "SAC PPO"
            st.rerun()

    with col3:
        if st.button("🏥 SAC HAPVIDA", use_container_width=True):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    with st.sidebar:
        st.markdown(f"### 📍 {st.session_state.servico}")

        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...","Equipe Erik","Equipe Davi","Equipe Elaine","Equipe Sayanne","Equipe Beatriz","Equipe Aline","Equipe Marcelo"]
        else:
            lista = ["Selecione...","Equipe Ellen","Equipe Carla","Equipe Magno","Equipe Alex","Equipe Hapvida"]

        supervisor = st.selectbox("Escolha o Supervisor:", lista)
        st.markdown("---")
        st.markdown("### ℹ️ Legenda de Cores")
        st.markdown("🟢 **Verde**: Na meta")
        st.markdown("🟡 **Amarelo**: Atenção")
        st.markdown("🔴 **Vermelho**: Fora da meta")

        if st.button("⬅️ Voltar ao Hub", use_container_width=True):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados_aba(supervisor)

        if df is not None and not df.empty:
            metas_atuais = copy.deepcopy(METAS_BASE)
            metas_atuais['Pausa Total'] = {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True}

            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Ranking", "📊 Saúde"])

            with tabs[0]:
                st.markdown(f"### Consulta Individual - {supervisor}")
                mat = st.text_input("Digite sua Matrícula:", placeholder="Ex: 1234567")

                if mat:
                    mat_clean = mat.strip()
                    res = df[df[col_mat].astype(str) == mat_clean]

                    if not res.empty:
                        r = res.iloc[0]
                        st.markdown(f"## 👋 Olá, {r[col_op]}!")
                        st.markdown('<div class="info-box">📊 Seus indicadores de performance</div>', unsafe_allow_html=True)

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
                        
                        if r['Produtividade'] != "---" or r['Transf'] != "---" or r['ShortCall'] != "---":
                            st.markdown("### 📊 Outras Métricas")
                            c4, c5, c6 = st.columns(3)
                            with c4:
                                if r['Produtividade'] != "---":
                                    exibir_card("Produtividade", r['Produtividade'], definir_cor_kpi(r['Produtividade_num'],'Produtividade', metas_atuais), "💪")
                            with c5:
                                if r['Transf'] != "---":
                                    exibir_card("Transferência", r['Transf'], definir_cor_kpi(r['Transf_num'],'Transf', metas_atuais), "📲")
                            with c6:
                                if r['ShortCall'] != "---":
                                    exibir_card("Short Call", r['ShortCall'], definir_cor_kpi(r['ShortCall_num'],'ShortCall', metas_atuais), "⚡")
                    else:
                        st.warning(f"❌ Matrícula **{mat_clean}** não encontrada.")
                else:
                    st.info("💡 Digite sua matrícula acima")

            with tabs[1]:
                st.markdown(f"### Visão Geral da Equipe - {supervisor}")
                metrica_equipe = st.selectbox("Selecione o indicador:", list(metas_atuais.keys()), key="metrica_equipe")
                stats = calcular_estatisticas_equipe(df, metrica_equipe, col_op, col_mat, metas_atuais)
                
                if stats:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.metric("Média da Equipe", f"{stats['media']:.2f}")
                    with col2: st.metric("Mediana", f"{stats['mediana']:.2f}")
                    with col3: 
                        if stats['meta']: st.metric("Meta", f"{stats['meta']:.2f}")
                    with col4:
                        if 'perc_meta' in stats: st.metric("% na Meta", f"{stats['perc_meta']:.1f}%")
                    
                    df_equipe = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{metrica_equipe}_num'].notna())].copy()
                    fig = px.histogram(df_equipe, x=f'{metrica_equipe}_num', nbins=20, title=f'Distribuição de {metrica_equipe}', color_discrete_sequence=['#004a99'])
                    if stats['meta']:
                        fig.add_vline(x=stats['meta'], line_dash="dash", line_color="red", annotation_text=f"Meta: {stats['meta']:.2f}")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Dados indisponíveis.")

            with tabs[2]:
                st.markdown(f"### 🏆 Ranking - {supervisor}")
                m_rank = st.selectbox("Ver Ranking de:", list(metas_atuais.keys()), key="metrica_rank")
                df_rank = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_rank}_num'].notna())].copy()
                if not df_rank.empty:
                    is_menor = metas_atuais[m_rank]['menor_melhor']
                    top = df_rank.sort_values(by=f'{m_rank}_num', ascending=is_menor).head(5)
                    medalhas = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
                    for i, (_, row) in enumerate(top.iterrows()):
                        exibir_card(f"{medalhas[i]} {i+1}º Lugar - {row[col_op]}", row[m_rank], definir_cor_kpi(row[f'{m_rank}_num'], m_rank, metas_atuais))
                else:
                    st.warning("⚠️ Ranking indisponível.")

            with tabs[3]:
                st.markdown(f"### 📊 Saúde da Operação - {supervisor}")
                m_saude = st.selectbox("Analisar Saúde de:", list(metas_atuais.keys()), key="metrica_saude")
                df_saude = df[(df[col_op].astype(str).str.upper() != 'EQUIPE') & (~df[col_mat].astype(str).isin(MATRICULAS_BACKOFFICE)) & (df[f'{m_saude}_num'].notna())].copy()
                if not df_saude.empty:
                    conf = metas_atuais[m_saude]
                    df_saude['Status'] = df_saude[f'{m_saude}_num'].apply(lambda x: 'Meta OK' if (x <= conf['valor'] if conf['menor_melhor'] else x >= conf['valor']) else 'Fora da Meta')
                    col1, col2, col3 = st.columns(3)
                    total = len(df_saude)
                    na_meta = (df_saude['Status'] == 'Meta OK').sum()
                    with col1: st.metric("Total", total)
                    with col2: st.metric("Na Meta", f"{na_meta} ({na_meta/total*100:.1f}%)")
                    with col3: st.metric("Fora", f"{total-na_meta} ({(total-na_meta)/total*100:.1f}%)")
                    fig = px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Meta OK': '#28a745', 'Fora da Meta': '#dc3545'})
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("⚠️ Dados indisponíveis.")
        elif df is None:
            st.error("❌ Erro ao carregar dados.")
    else:
        st.info("👆 Selecione um supervisor na barra lateral")
