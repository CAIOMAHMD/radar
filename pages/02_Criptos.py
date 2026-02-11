import streamlit as st
import pandas as pd
import yfinance as yf
import streamlit as st

st.title("💰 Criptos")


st.set_page_config(page_title="Radar Cripto", layout="wide")

st.markdown("Monitoramento em tempo real das principais moedas do mercado.")

# Lista das "Queridinhas" do mercado cripto
criptos_alvo = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'ADA-USD', 'DOT-USD']

def buscar_dados_cripto():
    lista_dados = []
    for ticker in criptos_alvo:
        try:
            c = yf.Ticker(ticker)
            hist = c.history(period="2d")
            if len(hist) >= 2:
                preco_atual = hist['Close'].iloc[-1]
                preco_ontem = hist['Close'].iloc[-2]
                variacao = ((preco_atual - preco_ontem) / preco_ontem) * 100
                
                lista_dados.append({
                    'Moeda': ticker.replace('-USD', ''),
                    'Preço (USD)': preco_atual,
                    'Variação 24h (%)': round(variacao, 2), # Arredondado para 2 casas
                    'Volume (24h)': c.info.get('volume24Hr', 0)
                })
        except Exception as e:
            continue
    return pd.DataFrame(lista_dados)

if st.sidebar.button('🔄 ATUALIZAR PREÇOS'):
    with st.spinner('Conectando com a Exchange...'):
        df_cripto = buscar_dados_cripto()
        if not df_cripto.empty:
            st.session_state['df_cripto'] = df_cripto

if 'df_cripto' in st.session_state:
    df = st.session_state['df_cripto']
    
    # Exibição de Métricas no Topo (Cards)
    st.subheader("📊 Resumo do Mercado")
    cols = st.columns(len(df))
    for i, row in df.iterrows():
        # Formata a string de variação para o card
        delta_str = f"{row['Variação 24h (%)']}%"
        cols[i].metric(row['Moeda'], f"$ {row['Preço (USD)']:,.2f}", delta_str)

    st.divider()
    
    # Tabela formatada para melhor leitura
    st.subheader("🔍 Detalhes")
    
    # Criamos uma cópia para formatar a exibição sem estragar os números do dataframe
    df_formatado = df.copy()
    df_formatado['Preço (USD)'] = df_formatado['Preço (USD)'].map('$ {:,.2f}'.format)
    df_formatado['Variação 24h (%)'] = df_formatado['Variação 24h (%)'].map('{:,.2f}%'.format)
    df_formatado['Volume (24h)'] = df_formatado['Volume (24h)'].map('$ {:,.0f}'.format)
    
    st.dataframe(df_formatado, use_container_width=True, hide_index=True)
else:
    st.info("👈 Clique em 'ATUALIZAR PREÇOS' na barra lateral.")