import pandas as pd
import requests
from io import StringIO
import numpy as np

def obter_dados_b3():
    url = "https://www.fundamentus.com.br/resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        df = pd.read_html(StringIO(response.text), decimal=',', thousands='.')[0]
    except Exception as e:
        print(f"❌ Erro na conexão: {e}")
        return pd.DataFrame()

    # 1. Limpeza radical dos nomes das colunas (remove \n, \t e espaços)
    df.columns = [str(col).strip().replace('\n', '').replace('\r', '') for col in df.columns]

    # 2. Mapeamento Robusto
    colunas_map = {
        'Cotação': 'price',
        'P/L': 'pl',
        'P/VP': 'pvp',
        'Div.Yield': 'dy',
        'LPA': 'lpa',
        'VPA': 'vpa',
        'Liq.2meses': 'liquidez'
    }
    df = df.rename(columns=colunas_map)

    # 3. Blindagem: Garante que as colunas existam para os cálculos
    cols_finais = ['price', 'pl', 'pvp', 'dy', 'lpa', 'vpa', 'liquidez']
    for col in cols_finais:
        if col not in df.columns:
            df[col] = 0.0

    # 4. Conversão Numérica
    for col in cols_finais:
        if not pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].astype(str).str.replace('%', '', regex=False)
            df[col] = df[col].str.replace('.', '', regex=False)
            df[col] = df[col].str.replace(',', '.', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # 5. Cálculos de Valor Justo (Alinhados com sua tabela de ITSA4)
    # Ajuste de escala do DY (Ex: 11.6 vira 0.116)
    df['dy_dec'] = df['dy'] / 100
    df['dpa'] = df['price'] * df['dy_dec']
    
    # Modelos de Bazin
    df['bazin_6'] = df['dpa'] / 0.06
    df['bazin_9'] = df['dpa'] / 0.09
    df['bazin_10'] = df['dpa'] / 0.10  # O seu valor de R$ 16,90
    
    # Modelo de Graham (Calculado como sqrt(22.5 * LPA * VPA))
    df['graham'] = np.sqrt(np.maximum(0, 22.5 * df['lpa'] * df['vpa']))

    # 6. Status com seus critérios (P/VP e DY)
    def classificar(row):
        # Forte Compra: P/VP <= 0.90 e DY >= 9%
        if row['pvp'] <= 0.90 and row['dy'] >= 9:
            return "🔥 FORTE COMPRA"
        # Compra: P/VP <= 0.95 e DY >= 8%
        elif row['pvp'] <= 0.95 and row['dy'] >= 8:
            return "✅ COMPRA"
        else:
            return "⏳ AGUARDAR"

    df['status_estrategia'] = df.apply(classificar, axis=1)
    
    # Filtro de Liquidez para evitar ativos sem giro
    return df[df['liquidez'] > 1000000].copy()