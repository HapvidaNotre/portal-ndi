import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# 2. DEFINIÇÃO DE METAS (DICIONÁRIO CENTRALIZADO)
METAS = {
    'Aderencia': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'Absenteismo': {'valor': 0.0, 'margem': 5.0, 'menor_melhor': True},
    'Transf': {'valor': 85.0, 'margem': 5.0, 'menor_melhor': False},
    'TMA Voz': {'valor': 8.0, 'margem': 1.0, 'menor_melhor': True},
    'Pesquisa': {'valor': 4.5, 'margem': 0.5, 'menor_melhor': False},
    'Resolutividade': {'valor': 75.0, 'margem': 5.0, 'menor_melhor': False},
    'Pausa Total': {'valor': 21.75, 'margem': 3.0, 'menor_melhor': True}
}

# 3. FUNÇÕES DE SUPORTE ATUALIZADAS
def definir_cor_kpi(valor, metrica_key):
    """Lógica Semafórica: Verde (Dentro), Amarelo (Quase), Vermelho (Fora)"""
    config = METAS.get(metrica_key)
    if not config: return "#333"
    
    m = config['valor']
    tol = config['margem']
    
    if config['menor_melhor']:
        if valor <= m: return "#28a745" # Verde (Dentro)
        if valor <= m + tol: return "#ffc107" # Amarelo (Quase)
        return "#dc3545" # Vermelho (Fora)
    else:
        if valor >= m: return "#28a745" # Verde (Dentro)
        if valor >= m - tol: return "#ffc107" # Amarelo (Quase)
        return "#dc3545" # Vermelho (Fora)

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
        
        for col in METAS.keys():
            if col in df.columns:
                if 'TMA' in col:
                    df[f'{col}_num'] = df[col].apply(converter_tma_minutos)
                else:
                    df[f'{col}_num'] = df[col].apply(converter_para_numero)
        return df
    except: return None

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"])

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde"])

        with tabs[0]: # INDIVIDUAL
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
                else: st.warning("Matrícula não encontrada.")

        with tabs[1]: # EQUIPE
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                cols = st.columns(3)
                for i, (k, v) in enumerate(METAS.items()):
                    with cols[i % 3]: exibir_card(f"{k} Equipe", e[k], definir_cor_kpi(e[f'{k}_num'], k))

        with tabs[2]: # MELHORES
            df_ops = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            for k, v in METAS.items():
                st.markdown(f"#### Top 3: {k}")
                top = df_ops.nsmallest(3, f'{k}_num') if v['menor_melhor'] else df_ops.nlargest(3, f'{k}_num')
                mc = st.columns(3)
                for i, (_, row) in enumerate(top.iterrows()):
                    with mc[i]: exibir_card(f"{i+1}º Lugar", row['Operador'], definir_cor_kpi(row[f'{k}_num'], k), ["🥇","🥈","🥉"][i])
                st.divider()
