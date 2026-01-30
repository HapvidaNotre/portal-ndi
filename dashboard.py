import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# CSS para botões GIGANTES no Lobby e design limpo
st.markdown("""
    <style>
    /* Estilo dos botões do Lobby inicial */
    div.stButton > button {
        height: 8em !important;
        font-size: 25px !important;
        font-weight: bold !important;
        width: 100% !important;
        border-radius: 20px !important;
        background-color: #f8f9fa !important;
        border: 2px solid #dee2e6 !important;
        color: #333 !important;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        border-color: #004a99 !important;
        color: #004a99 !important;
        background-color: #e9ecef !important;
        transform: scale(1.02);
    }
    /* Ajuste para o botão de 'Voltar' no sidebar não ficar gigante */
    section[data-testid="stSidebar"] div.stButton > button {
        height: 3em !important;
        font-size: 16px !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. METAS E CONFIGURAÇÕES
METAS_BASE = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Produtividade': {'valor': 90.0, 'margem': 10.0, 'menor_melhor': False},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'ShortCall': {'valor': 5.0, 'margem': 2.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False}
}

# Matrículas do Backoffice que não devem ir para o Ranking
MATRICULAS_BACKOFFICE = ['1211819', '1210820', '1210724', '1211110', '1211213', '1214016', '10115858', '1212492', '1028483']

# 3. FUNÇÕES DE TRATAMENTO
def converter_para_numero(valor):
    if pd.isna(valor) or str(valor).strip().lower() in ['none', '', 'nan', '0']: return None
    try:
        num = float(str(valor).replace('%', '').replace(',', '.').strip())
        return num if num > 0 else None
    except: return None

def converter_tma_minutos(tempo_str):
    if pd.isna(tempo_str) or str(tempo_str).strip().lower() in ['none', '', 'nan', '00:00:00', '0']: return None
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        return int(partes[0]) + int(partes[1]) / 60
    except: return None

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    if valor is None: return "#6c757d"
    config = metas_atuais.get(metrica_key)
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        if valor <= m: return "#28a745"
        return "#ffc107" if valor <= m + tol else "#dc3545"
    else:
        if valor >= m: return "#28a745"
        return "#ffc107" if valor >= m - tol else "#dc3545"

def exibir_card(label, valor, cor="#333", icon=""):
    if isinstance(valor, (int, float)):
        val_fmt = f"{valor:.2f}"
    else:
        val_fmt = str(valor) if str(valor).lower() != 'none' else "N/A"
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {val_fmt}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Mapeamento insensível a maiúsculas/minúsculas para evitar KeyError
        col_map = {col.lower(): col for col in df.columns}
        target_op = col_map.get('operador', df.columns[0]) # Fallback para primeira coluna se não achar
        target_mat = col_map.get('matricula', df.columns[1])

        for col in list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']:
            real_col = col_map.get(col.lower())
            if real_col:
                df[f'{col}_num'] = df[real_col].apply(converter_tma_minutos if 'TMA' in col or 'Pausa' in col else converter_para_numero)
            else:
                df[f'{col}_num'] = None
        return df, target_op, target_mat
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None, None, None

# --- LOBBY INICIAL ---
if st.session_state.servico is None:
    st.markdown("<br><h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #666;'>Selecione o serviço para iniciar</p>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏢 SAC NDI"):
            st.session_state.servico = "SAC NDI"
            st.rerun()
    with col2:
        if st.button("🏦 SAC PPO"):
            st.session_state.servico = "SAC PPO"
            st.rerun()
    with col3:
        if st.button("🏥 SAC HAPVIDA"):
            st.session_state.servico = "SAC HAPVIDA"
            st.rerun()

else:
    # --- ÁREA INTERNA ---
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            lista = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            lista = ["Selecione...", "Equipe Hapvida"]
        
        supervisor = st.selectbox("Selecione o Supervisor:", lista)
        st.write("---")
        if st.button("⬅️ Voltar ao Lobby"):
            st.session_state.servico = None
            st.rerun()

    if supervisor != "Selecione...":
        df, col_op, col_mat = carregar_dados(supervisor)
        
        if df is not None:
            # Metas Customizadas
            metas_s = METAS_BASE.copy()
            if "Carla" in supervisor: meta_p = 17.27
            elif "Ellen" in supervisor: meta_p = 19.06
            elif "Alex" in supervisor: meta_p = 17.17
            elif "Magno" in supervisor: meta_p = 19.18
            else: meta_p = 21.75
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            st.header(f"Performance: {supervisor}")
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde"])

            with tabs[0]:
                mat_in = st.text_input("Digite sua Matrícula para consultar:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r.get('Aderencia', 'N/A'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                            exibir_card("Pesquisa", r['Pesquisa_num'] if r['Pesquisa_num'] else "0.00", definir_cor_kpi(r['Pesquisa_num'], 'Pesquisa', metas_s), "⭐")
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', 'N/A'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', 'N/A'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                    else: st.warning("Matrícula não encontrada.")

            with tabs[1]: # EQUIPE
                try:
                    # Busca ignorando case
                    eq_row = df[df[col_op].str.strip().str.upper() == 'EQUIPE']
                    if not eq_row.empty:
                        e = eq_row.iloc[0]
                        cols = st.columns(3)
                        for i, k in enumerate(metas_s.keys()):
                            val_num = e.get(f'{k}_num')
                            val_label = e.get(k, '0') if k != 'Pesquisa' else (f"{val_num:.2f}" if val_num else "0.00")
                            with cols[i % 3]: exibir_card(f"{k} Equipe", val_label, definir_cor_kpi(val_num, k, metas_s))
                except: st.error("Linha 'EQUIPE' não identificada na planilha.")

            with tabs[2]: # RANKING (FILTRADO)
                for k, v in metas_s.items():
                    df_rank = df[
                        (df[col_op].str.strip().str.upper() != 'EQUIPE') & 
                        (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                        (df[f'{k}_num'].notna())
                    ].copy()
                    if not df_rank.empty:
                        st.markdown(f"#### Ranking: {k}")
                        top = df_rank.nsmallest(3, f'{k}_num') if v['menor_melhor'] else df_rank.nlargest(3, f'{k}_num')
                        mc = st.columns(3)
                        for i, (_, row) in enumerate(top.iterrows()):
                            val_top = row.get(k) if k != 'Pesquisa' else f"{row[f'{k}_num']:.2f}"
                            with mc[i]: exibir_card(f"{i+1}º Lugar", row[col_op], definir_cor_kpi(row[f'{k}_num'], k, metas_s), ["🥇","🥈","🥉"][i])
                    st.divider()

            with tabs[3]: # SAÚDE (FILTRADA)
                sel = st.selectbox("Escolha a Métrica:", list(metas_s.keys()))
                df_saude = df[
                    (df[col_op].str.strip().str.upper() != 'EQUIPE') & 
                    (~df[col_mat].astype(str).str.strip().isin(MATRICULAS_BACKOFFICE)) &
                    (df[f'{sel}_num'].notna())
                ].copy()
                if not df_saude.empty:
                    mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                    df_saude['Status'] = df_saude[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                    c_s1, c_s2 = st.columns(2)
                    with c_s1:
                        fig = px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'})
                        st.plotly_chart(fig, use_container_width=True)
                    with c_s2: st.dataframe(df_saude[[col_op, sel, 'Status']], hide_index=True)
