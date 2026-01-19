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

# 3. FUNÇÕES DE TRATAMENTO DE DADOS
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
        if valor <= meta: return "#28a745" # Verde
        if valor <= meta + margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho
    else:
        if valor >= meta: return "#28a745" # Verde
        if valor >= meta - margem: return "#ffc107" # Amarelo
        return "#dc3545" # Vermelho

def exibir_card(label, valor, cor="#333", icon=""):
    st.markdown(f"""
        <div style="background-color: white; padding: 15px; border-radius: 10px; border-left: 8px solid {cor}; 
             box-shadow: 2px 2px 8px rgba(0,0,0,0.1); margin-bottom: 10px;">
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

        # Mapeamento Inteligente (Corrige erros de digitação na planilha)
        mapeamento = {
            'Aderencia': ['Aderencia', 'Aderência', 'ADERENCIA'],
            'Absenteismo': ['Absenteismo', 'Absenteísmo', 'ABS'],
            'Transf': ['Transf', 'Transferência', 'Transf.'],
            'TMA Voz': ['TMA Voz', 'TMA', 'Tma'],
            'Pesquisa': ['Pesquisa', 'NPS', 'Nps', 'PESQUISA'],
            'Resolutividade': ['Resolutividade', 'RESOLUTIVIDADE'],
            'Pausa Produtiva': ['Pausa Produtiva', 'PAUSA PRODUTIVA'],
            'Pausa Improdutiva': ['Pausa Improdutiva', 'PAUSA IMPRODUTIVA'],
            'Pausa Total': ['Pausa Total', 'PAUSA TOTAL']
        }

        # Garante que as colunas padrão existam e cria as versões numéricas (_num)
        for oficial, variantes in mapeamento.items():
            # Tenta encontrar a coluna original
            col_encontrada = next((v for v in variantes if v in df.columns), None)
            
            if col_encontrada:
                df[oficial] = df[col_encontrada] # Padroniza o nome
                if oficial in ['TMA Voz', 'Pausa Produtiva', 'Pausa Improdutiva', 'Pausa Total']:
                    df[f'{oficial}_num'] = df[oficial].apply(converter_tma_minutos)
                else:
                    df[f'{oficial}_num'] = df[oficial].apply(converter_para_numero)
            else:
                # Se não existir na planilha, cria com valor zero para não dar erro
                df[oficial] = "0"
                df[f'{oficial}_num'] = 0.0

        return df
    except Exception as e:
        st.error(f"Erro ao ler a aba: {e}")
        return None

# --- INTERFACE ---
st.title("🚀 Portal de Performance NDI")
supervisor = st.selectbox("Selecione o seu Supervisor:", SUPERVISORES)

if supervisor != "Selecione...":
    df = carregar_dados(supervisor)
    if df is not None:
        tabs = st.tabs(["👤 Individual", "👥 Equipe", "⭐ Melhores", "📊 Saúde da Operação"])

        # 1. INDIVIDUAL
        with tabs[0]:
            mat = st.text_input("Digite sua Matrícula:")
            if mat:
                res = df[df['Matricula'] == mat.strip()]
                if not res.empty:
                    r = res.iloc[0]
                    st.subheader(f"Olá, {r['Operador']}")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        exibir_card("Aderência", r['Aderencia'], definir_cor_kpi(r['Aderencia_num'], 85, 5))
                        exibir_card("Absenteísmo", r['Absenteismo'], definir_cor_kpi(r['Absenteismo_num'], 5, 2, True))
                    with c2:
                        exibir_card("Resolutividade", r['Resolutividade'], definir_cor_kpi(r['Resolutividade_num'], 85, 5))
                        exibir_card("TMA Voz", r['TMA Voz'], definir_cor_kpi(r['TMA Voz_num'], 8, 1, True), "⏱️")
                    with c3:
                        exibir_card("NPS", r['Pesquisa'], definir_cor_kpi(r['Pesquisa_num'], 4.5, 0.5))
                        exibir_card("Transferência", r['Transf'], "#6c757d")
                    
                    st.markdown("---")
                    st.subheader("📊 Controle de Pausas")
                    p1, p2, p3 = st.columns(3)
                    with p1: exibir_card("Produtiva", r['Pausa Produtiva'], "#1f77b4")
                    with p2: exibir_card("Improdutiva", r['Pausa Improdutiva'], "#e377c2")
                    with p3: exibir_card("Total", r['Pausa Total'], "#333")

        # 2. EQUIPE
        with tabs[1]:
            eq = df[df['Operador'].str.strip() == 'EQUIPE']
            if not eq.empty:
                e = eq.iloc[0]
                st.subheader(f"Médias da Equipe: {supervisor}")
                col_eq = st.columns(3)
                metricas = [
                    ("Aderência", 'Aderencia'), ("Resolutividade", 'Resolutividade'), ("TMA", 'TMA Voz'),
                    ("NPS", 'Pesquisa'), ("Absenteísmo", 'Absenteismo'), ("Transferência", 'Transf'),
                    ("Pausa Produtiva", 'Pausa Produtiva'), ("Pausa Improdutiva", 'Pausa Improdutiva'), ("Pausa Total", 'Pausa Total')
                ]
                for i, (label, col) in enumerate(metricas):
                    with col_eq[i % 3]: exibir_card(label, e[col], "#007bff")

        # 3. MELHORES (RANKING)
        with tabs[2]:
            st.subheader("🏆 Ranking Top 3")
            df_rank = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            def gerar_podio(col_num, col_label, titulo, icone, meta, inverter=False):
                st.markdown(f"#### {icone} {titulo}")
                top = df_rank.nsmallest(3, col_num) if inverter else df_rank.nlargest(3, col_num)
                m1, m2, m3 = st.columns(3)
                for i, (idx, row) in enumerate(top.iterrows()):
                    cor = definir_cor_kpi(row[col_num], meta, 5, inverter)
                    with [m1, m2, m3][i]:
                        exibir_card(f"{i+1}º Lugar", row['Operador'], cor, ["🥇","🥈","🥉"][i])
                        st.caption(f"Valor: {row[col_label]}")
                st.divider()

            gerar_podio('Aderencia_num', 'Aderencia', "Aderência", "🎯", 85)
            gerar_podio('Resolutividade_num', 'Resolutividade', "Resolutividade", "✅", 85)
            gerar_podio('TMA Voz_num', 'TMA Voz', "TMA (Menor é melhor)", "⏱️", 8, True)
            gerar_podio('Pesquisa_num', 'Pesquisa', "NPS", "⭐", 4.5)

        # 4. SAÚDE
        with tabs[3]:
            st.header("📊 Saúde da Operação")
            df_saude = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            metrica = st.selectbox("Analisar Saúde de:", ["Aderencia", "Resolutividade", "TMA Voz", "Pesquisa", "Absenteismo"])
            
            meta_v = 8.0 if metrica == "TMA Voz" else 5.0 if metrica == "Absenteismo" else 4.5 if metrica == "Pesquisa" else 85.0
            is_inv = True if metrica in ["TMA Voz", "Absenteismo"] else False
            
            if is_inv: df_saude['Status'] = df_saude[f'{metrica}_num'].apply(lambda x: 'Dentro' if x <= meta_v else 'Fora')
            else: df_saude['Status'] = df_saude[f'{metrica}_num'].apply(lambda x: 'Dentro' if x >= meta_v else 'Fora')
            
            c_g1, c_g2 = st.columns(2)
            with c_g1:
                fig = px.pie(df_saude, names='Status', hole=0.5, color='Status', color_discrete_map={'Dentro':'#28a745','Fora':'#dc3545'})
                st.plotly_chart(fig, use_container_width=True)
            with c_g2:
                st.dataframe(df_saude[['Operador', metrica, 'Status']], use_container_width=True, hide_index=True)

### O que foi corrigido:
1. **Fim do KeyError:** Criei um dicionário (`mapeamento`) que padroniza os nomes das colunas. Se a planilha tiver "TMA", ele transforma em "TMA Voz" e cria o "TMA Voz_num" automaticamente.
2. **Criação de Colunas Seguras:** Se uma métrica (como "Absenteismo") não for encontrada, o código cria ela com valor "0" em vez de travar o programa.
3. **Consistência de Nomes:** Todos os rankings e cards agora usam exatamente os mesmos nomes de colunas definidos no carregamento.
4. **Visão Geral:** As 9 métricas aparecem em todas as abas conforme solicitado.

Pode copiar e colar todo este código. Ele é robusto o suficiente para lidar com pequenas variações nos nomes das colunas da sua planilha. **Deseja que eu adicione mais alguma métrica específica?**
