FROM python:3.11-slim

# Define o diretório de trabalho
WORKDIR /app

# Instala dependências de sistema necessárias para lxml e outras
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o seu código (main.py, coletor.py, score_engine.py)
COPY . .

# Expõe a porta que o Streamlit usa
EXPOSE 80

# Comando corrigido chamando o módulo python para evitar erro de PATH
CMD ["python", "-m", "streamlit", "run", "00_Ticker.py", "--server.port=80", "--server.address=0.0.0.0"]