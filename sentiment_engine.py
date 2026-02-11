import feedparser
import google.generativeai as genai
import streamlit as st

# Tenta carregar a chave
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyD09t4DepfU7ALRX61JFdco4VkgPUsgQwc"

genai.configure(api_key=api_key)

class SentimentEngine:
    @staticmethod
    def get_market_sentiment(ticker):
        try:
            # 1. Coleta de notícias
            url = f"https://news.google.com/rss/search?q={ticker}+investidor+B3&hl=pt-BR&gl=BR&ceid=BR:pt-150"
            feed = feedparser.parse(url)
            
            contexto = "Sem notícias recentes."
            if feed.entries:
                titulos = [e.title for e in feed.entries[:5]]
                contexto = "\n- ".join(titulos)

            # 2. IA Gemini (Usando o 2.5 que validamos no seu Mac)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"Analise o sentimento para {ticker}: {contexto}. Responda apenas: SCORE: [0-100], RESUMO: [máximo 10 palavras]"
            
            response = model.generate_content(prompt)
            texto = response.text

            # 3. Extração simples
            score = "50"
            resumo = "Neutro"
            for linha in texto.split('\n'):
                if "SCORE:" in linha.upper():
                    score = linha.upper().replace("SCORE:", "").strip()
                if "RESUMO:" in linha.upper():
                    resumo = linha.upper().replace("RESUMO:", "").strip()

            return score, resumo

        except Exception as e:
            return "50", f"Erro: {str(e)[:15]}"