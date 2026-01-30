import streamlit as st
import pandas as pd
import plotly.express as px

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Portal de Performance NDI", layout="wide", page_icon="🚀")

# --- INICIALIZAÇÃO DO ESTADO DE NAVEGAÇÃO ---
if 'servico' not in st.session_state:
    st.session_state.servico = None

# 2. DICIONÁRIO CENTRALIZADO DE METAS
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

# 3. FUNÇÕES DE SUPORTE
def converter_para_numero(valor):
    if pd.isna(valor): return 0.0
    try: return float(str(valor).replace('%', '').replace(',', '.').strip())
    except: return 0.0

def converter_tma_minutos(tempo_str):
    try:
        partes = str(tempo_str).split(':')
        if len(partes) == 3: return int(partes[0]) * 60 + int(partes[1]) + int(partes[2]) / 60
        elif len(partes) == 2: return int(partes[0]) + int(partes[1]) / 60
        return 0.0
    except: return 0.0

def definir_cor_kpi(valor, metrica_key, metas_atuais):
    config = metas_atuais.get(metrica_key)
    if not config: return "#333"
    m, tol, menor_melhor = config['valor'], config['margem'], config['menor_melhor']
    if menor_melhor:
        if valor <= m: return "#28a745" # Verde
        if valor <= m + tol: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= m: return "#28a745"
        if valor >= m - tol: return "#ffc107"
        return "#dc3545"

def exibir_card(label, valor, cor="#333", icon=""):
    # Formatação para 2 casas decimais se for numérico (ex: Pesquisa/NPS)
    if isinstance(valor, (int, float)):
        valor_formatado = f"{valor:.2f}"
    else:
        valor_formatado = str(valor)
        
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 10px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 12px;">
            <p style="margin: 0; font-size: 11px; color: #666; font-weight: bold; text-transform: uppercase;">{label}</p>
            <h2 style="margin: 5px 0 0 0; color: {cor}; font-size: 20px;">{icon} {valor_formatado}</h2>
        </div>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def carregar_dados(nome_aba):
    try:
        SHEET_ID = "1uOREvgGXscOpmtWK7SQ3oCI67pDQOmZWcOaxg0E025E"
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nome_aba.replace(' ', '%20')}"
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        
        # Mapeamento para ignorar maiúsculas/minúsculas no nome das colunas da planilha
        col_map = {col.lower(): col for col in df.columns}
        target_op = col_map.get('operador', 'Operador')
        target_mat = col_map.get('matricula', 'Matricula')

        colunas_meta = list(METAS_BASE.keys()) + ['Pausa Total', 'Pausa Produtiva', 'Pausa Improdutiva']
        for col in colunas_meta:
            real_col = col_map.get(col.lower(), col)
            if real_col in df.columns:
                df[f'{col}_num'] = df[real_col].apply(converter_tma_minutos if 'TMA' in col or 'Pausa' in col else converter_para_numero)
            else:
                df[f'{col}_num'] = 0.0
        
        return df, target_op, target_mat
    except Exception as e:
        st.error(f"Erro ao carregar dados da aba {nome_aba}: {e}")
        return None, None, None

# --- LOBBY DE ENTRADA ---
if st.session_state.servico is None:
    st.markdown("<h1 style='text-align: center; color: #004a99;'>🚀 Portal de Performance NDI</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px;'>Selecione o serviço para continuar:</p>", unsafe_allow_html=True)
    st.write("---")
    
    col_l1, col_l2, col_l3 = st.columns(3)
    if col_l1.button("🏢 SAC NDI", use_container_width=True, type="primary"):
        st.session_state.servico = "SAC NDI"; st.rerun()
    if col_l2.button("🏦 SAC PPO", use_container_width=True):
        st.session_state.servico = "SAC PPO"; st.rerun()
    if col_l3.button("🏥 SAC HAPVIDA", use_container_width=True):
        st.session_state.servico = "SAC HAPVIDA"; st.rerun()

# --- INTERFACE PRINCIPAL ---
else:
    with st.sidebar:
        st.title(f"📍 {st.session_state.servico}")
        
        # Mapeamento de supervisores por serviço selecionado
        if st.session_state.servico == "SAC NDI":
            lista = ["Selecione...", "Equipe Erik", "Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Beatriz", "Equipe Aline", "Equipe Marcelo"]
        elif st.session_state.servico == "SAC PPO":
            lista = ["Selecione...", "Equipe Ellen", "Equipe Carla", "Equipe Magno", "Equipe Alex"]
        else:
            lista = ["Selecione...", "Em Breve"]
        
        supervisor = st.selectbox("Selecione o Supervisor:", lista)
        st.write("---")
        if st.button("⬅️ Voltar ao Lobby"):
            st.session_state.servico = None; st.rerun()

    if supervisor != "Selecione..." and "Em Breve" not in supervisor:
        df, col_op, col_mat = carregar_dados(supervisor)
        
        if df is not None:
            # Regras de Pausa Total por equipe
            equipes_16 = ["Equipe Davi", "Equipe Elaine", "Equipe Sayanne", "Equipe Aline", "Equipe Marcelo"]
            meta_p = 16.60 if supervisor in equipes_16 else 21.75
            metas_s = METAS_BASE.copy()
            metas_s['Pausa Total'] = {'valor': meta_p, 'margem': 3.0, 'menor_melhor': True}

            st.header(f"Performance: {supervisor}")
            tabs = st.tabs(["👤 Individual", "👥 Equipe", "🏆 Melhores", "📊 Saúde da Operação"])

            # 1. ABA INDIVIDUAL
            with tabs[0]:
                mat_in = st.text_input("Digite sua Matrícula:")
                if mat_in:
                    res = df[df[col_mat].astype(str).str.contains(mat_in.strip())]
                    if not res.empty:
                        r = res.iloc[0]
                        st.subheader(f"Olá, {r[col_op]}")
                        
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            exibir_card("Aderência", r.get('Aderencia', '0%'), definir_cor_kpi(r['Aderencia_num'], 'Aderencia', metas_s))
                            exibir_card("Pausa Produtiva", r.get('Pausa Produtiva', '00:00'), "#004a99", "⏱️")
                            val_pesquisa = converter_para_numero(r.get('Pesquisa', 0))
                            exibir_card("Pesquisa (NPS)", val_pesquisa, definir_cor_kpi(val_pesquisa, 'Pesquisa', metas_s), "⭐")
                        with c2:
                            exibir_card("Resolutividade", r.get('Resolutividade', '0%'), definir_cor_kpi(r['Resolutividade_num'], 'Resolutividade', metas_s))
                            exibir_card("Pausa Improdutiva", r.get('Pausa Improdutiva', '00:00'), "#004a99", "⏱️")
                            exibir_card("Transferência", r.get('Transf', '0%'), "#666")
                        with c3:
                            exibir_card("TMA Voz", r.get('TMA Voz', '00:00'), definir_cor_kpi(r['TMA Voz_num'], 'TMA Voz', metas_s), "⏱️")
                            exibir_card("Absenteísmo", r.get('Absenteismo', '0%'), definir_cor_kpi(r['Absenteismo_num'], 'Absenteismo', metas_s))
                            exibir_card("Pausa Total", r.get('Pausa Total', '00:00'), definir_cor_kpi(r['Pausa Total_num'], 'Pausa Total', metas_s), "⏱️")
                    else: st.warning("Matrícula não encontrada.")

            # 2. ABA EQUIPE
            with tabs[1]:
                eq = df[df[col_op].str.strip().str.upper() == 'EQUIPE']
                if not eq.empty:
                    e = eq.iloc[0]
                    cols = st.columns(3)
                    for i, (k, v) in enumerate(metas_s.items()):
                        val_num = e.get(f'{k}_num', 0)
                        val_label = e.get(k, '0') if k != 'Pesquisa' else val_num
                        with cols[i % 3]: 
                            exibir_card(f"{k} Equipe", val_label, definir_cor_kpi(val_num, k, metas_s))
                else: st.info("Linha 'EQUIPE' não encontrada na planilha.")

            # 3. ABA MELHORES (RANKINGS)
            with tabs[2]:
                df_ops = df[df[col_op].str.strip().str.upper() != 'EQUIPE'].copy()
                for k, v in metas_s.items():
                    st.markdown(f"#### Ranking: {k}")
                    top = df_ops.nsmallest(3, f'{k}_num') if v['menor_melhor'] else df_ops.nlargest(3, f'{k}_num')
                    mc = st.columns(3)
                    for i, (_, row) in enumerate(top.iterrows()):
                        val_top = row.get(k, '0') if k != 'Pesquisa' else row.get(f'{k}_num', 0)
                        with mc[i]: exibir_card(f"{i+1}º Lugar", row[col_op], definir_cor_kpi(row[f'{k}_num'], k, metas_s), ["🥇","🥈","🥉"][i])
                    st.divider()

            # 4. ABA SAÚDE DA OPERAÇÃO
            with tabs[3]:
                df_s = df[df[col_op].str.strip().str.upper() != 'EQUIPE'].copy()
                sel = st.selectbox("Selecione a métrica para análise:", list(metas_s.keys()))
                mv, inv = metas_s[sel]['valor'], metas_s[sel]['menor_melhor']
                df_s['Status'] = df_s[f'{sel}_num'].apply(lambda x: 'Dentro da Meta' if (x <= mv if inv else x >= mv) else 'Fora da Meta')
                
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    fig = px.pie(df_s, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro da Meta':'#28a745','Fora da Meta':'#dc3545'}, title=f"Visão Geral: {sel}")
                    st.plotly_chart(fig, use_container_width=True)
                with c_s2:
                    st.subheader("Lista Detalhada")
                    st.dataframe(df_s[[col_op, sel, 'Status']], use_container_width=True, hide_index=True)
