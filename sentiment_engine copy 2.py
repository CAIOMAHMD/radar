import feedparser
import google.generativeai as genai
import streamlit as st

# Tenta carregar a chave
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = "AIzaSyD09t4DepfU7ALRX61JFdco4VkgPUsgQwc"

genai.configure(api_key=api_key)

# sentiment_engine.py

class SentimentEngine:
    @staticmethod
    # Removi o cache fixo para permitir atualizações manuais sob demanda
    def get_market_sentiment(ticker):
        try:
            # 1. Coleta de notícias
            url = f"https://news.google.com/rss/search?q={ticker}+investidor+B3&hl=pt-BR&gl=BR&ceid=BR:pt-150"
            feed = feedparser.parse(url)
            
            contexto = "Sem notícias recentes relevantes."
            if feed.entries:
                titulos = [e.title for e in feed.entries[:8]] # Pegando um pouco mais de contexto
                contexto = "\n- ".join(titulos)

            # 2. IA Gemini (Sugestão: use 1.5-flash para maior compatibilidade atual)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = (
                f"Analise o sentimento de mercado para o ativo {ticker} baseado nestas notícias: {contexto}. "
                "Responda estritamente neste formato: SCORE: [0-100], RESUMO: [máximo 10 palavras]"
            )
            
            response = model.generate_content(prompt)
            texto = response.text

            # 3. Extração robusta
            score = "50"
            resumo = "Neutro"
            for linha in texto.split('\n'):
                if "SCORE:" in linha.upper():
                    # Extrai apenas os dígitos do score
                    import re
                    match = re.search(r'\d+', linha)
                    if match: score = match.group()
                if "RESUMO:" in linha.upper():
                    resumo = linha.upper().replace("RESUMO:", "").strip()

            return score, resumo

        except Exception as e:
            return "50", f"Erro: {str(e)[:15]}"