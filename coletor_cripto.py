import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Radar Cripto", layout="wide")

st.title("🚀 Radar de Criptomoedas")
st.markdown("Monitoramento em tempo real das principais moedas do mercado.")

# Lista das "Queridinhas" do mercado cripto
criptos_alvo = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'ADA-USD', 'DOT-USD']

def buscar_dados_cripto():
    lista_dados = []
    for ticker in criptos_alvo:
        c = yf.Ticker(ticker)
        hist = c.history(period="2d")
        if len(hist) >= 2:
            preco_atual = hist['Close'].iloc[-1]
            preco_ontem = hist['Close'].iloc[-2]
            variacao = ((preco_atual - preco_ontem) / preco_ontem) * 100
            
            lista_dados.append({
                'Moeda': ticker.replace('-USD', ''),
                'Preço (USD)': f"$ {preco_atual:,.2f}",
                'Variação 24h': variacao,
                'Volume': f"$ {c.info.get('volume24Hr', 0):,.0f}"
            })
    return pd.DataFrame(lista_dados)

if st.sidebar.button('🔄 ATUALIZAR PREÇOS'):
    with st.spinner('Conectando com a Blockchain...'):
        df_cripto = buscar_dados_cripto()
        st.session_state['df_cripto'] = df_cripto

if 'df_cripto' in st.session_state:
    df = st.session_state['df_cripto']
    
    # Exibição em Cards (Estilo Dashboard)
    cols = st.columns(len(df))
    for i, row in df.iterrows():
        cor = "green" if row['Variação 24h'] > 0 else "red"
        cols[i].metric(row['Moeda'], row['Preço (USD)'], f"{row['Variação 24h']:.2f}%")

    st.divider()
    st.dataframe(df, use_container_width=True)
else:
    st.info("👈 Clique em 'ATUALIZAR PREÇOS' para ver o mercado.")