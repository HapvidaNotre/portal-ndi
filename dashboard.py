# --- ABA MELHORES (Pódio por Métrica) ---
        with tab_melhores:
            st.subheader(f"🏆 Destaques da Equipe")
            
            # Remove a linha 'EQUIPE' para o ranking
            df_ranking = df[df['Operador'].str.strip() != 'EQUIPE'].copy()
            
            if not df_ranking.empty:
                # Função interna para criar cada pódio
                def criar_podio_metrica(coluna_nome, titulo_exibicao, icone):
                    st.markdown(f"#### {icone} Top 3: {titulo_exibicao}")
                    # Ordena pela métrica numérica criada no carregamento
                    top_3 = df_ranking.nlargest(3, f"{coluna_nome}_num")
                    
                    m1, m2, m3 = st.columns(3)
                    medalhas = ["🥇", "🥈", "🥉"]
                    
                    for i, (idx, row) in enumerate(top_3.iterrows()):
                        col_atual = [m1, m2, m3][i]
                        with col_atual:
                            exibir_card(
                                f"{i+1}º Lugar", 
                                row['Operador'], 
                                "#FFD700" if i==0 else "#C0C0C0" if i==1 else "#CD7F32",
                                medalhas[i]
                            )
                            st.caption(f"Resultado: {row[coluna_nome]}")
                    st.markdown("---")

                # Exibe os pódios individuais conforme sua preferência
                criar_podio_metrica('Aderencia', 'Aderência', "🎯")
                criar_podio_metrica('Resolutividade', 'Resolutividade', "✅")
                
                # Se houver a coluna Transf na planilha, ativa este pódio
                if 'Transf' in df_ranking.columns:
                    # Para transferência, geralmente o MENOR é melhor. 
                    # Se quiser os maiores, use nlargest. Para menores, nsmallest.
                    criar_podio_metrica('Transf', 'Transferência', "📞")
                
            else:
                st.info("Aguardando dados para gerar os pódios.")
