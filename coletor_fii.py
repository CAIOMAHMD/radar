import pandas as pd
import requests
from io import StringIO

def obter_dados_fii(): 
    # URL específica para Fundos Imobiliários
    url = "https://www.fundamentus.com.br/fii_resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # O Fundamentus de FIIs pode vir com mais de uma tabela, pegamos a primeira [0]
        df = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]
    except Exception as e:
        print(f"❌ Erro na conexão FII: {e}")
        return pd.DataFrame()

    df.columns = [col.strip() for col in df.columns]

    # Mapeamento específico para FIIs
    # Em FIIs, o Fundamentus chama o setor de 'Segmento'
    colunas_map = {
        'Cotação': 'price',
        'Dividend Yield': 'dy',
        'P/VP': 'pvp',
        'Liquidez': 'liquidez',
        'Segmento': 'segmento',
        'Vacância Média': 'vacancia'
    }

    # Limpeza de dados (removendo % e tratando números)
    for col in df.columns:
        if col not in ['Papel', 'Segmento']:
            if not pd.api.types.is_numeric_dtype(df[col]):
                val = df[col].astype(str).str.replace('%', '', regex=False)
                val = val.str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
                df[col] = pd.to_numeric(val, errors='coerce')

    df = df.rename(columns=colunas_map)
    
    # FIIs não têm LPA/VPA da mesma forma que ações no Fundamentus (usamos VP e Preço)
    # Criamos colunas vazias para não quebrar o ScoreEngine
    if 'lpa' not in df.columns: df['lpa'] = 0
    if 'vpa' not in df.columns: df['vpa'] = df['price'] / df['pvp']
    if 'roe' not in df.columns: df['roe'] = 0 # FII não usa ROE, usa Yield

    # Identificador de FII
    df['is_fii'] = True
    
    # Filtro de Liquidez (FIIs costumam ter liquidez menor que ações, baixei para 500k)
    return df[df['liquidez'] > 500000].copy()