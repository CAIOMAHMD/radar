import pandas as pd
import requests
from io import StringIO

def obter_dados_b3():  # <--- O nome TEM que ser este
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        df = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return pd.DataFrame()

    df.columns = [col.strip() for col in df.columns]

    # Mapeamento para garantir que 'Setor' vire 'segmento'
    colunas_map = {
        'Cotação': 'price',
        'Div.Yield': 'dy',
        'P/VP': 'pvp',
        'LPA': 'lpa',
        'VPA': 'vpa',
        'ROE': 'roe',
        'Liq.2meses': 'liquidez',
        'Setor': 'segmento'
    }

    # Limpeza de strings para números
    for col in df.columns:
        if col not in ['Papel', 'Setor']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].astype(str).str.replace('%', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.rename(columns=colunas_map)
    
    # Blindagem para a coluna segmento
    if 'segmento' not in df.columns:
        df['segmento'] = "N/A"

    # Correção de escala
    if df['pvp'].mean() < 0.1: df['pvp'] *= 100
    if df['dy'].mean() < 0.5: df['dy'] *= 100
    
    df['is_fii'] = False
    return df[df['liquidez'] > 1000000].copy()