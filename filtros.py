import pandas as pd

def aplicar_filtros_acoes(df):
    """
    Aplica as regras de negócio para Ações baseadas nos critérios do usuário.
    Retorna dois DataFrames: (forte_compra, compra)
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()

    # Criamos uma cópia para evitar avisos de SettingWithCopy
    df_result = df.copy()

    # --- REGRA: FORTE COMPRA ---
    # Critérios: P/VP <= 0.90, DY >= 9%, e Magic Number <= 110
    condicao_forte = (
        (df_result['P_VP'] <= 0.90) & 
        (df_result['DY'] >= 9) & 
        (df_result['magic_number'] <= 110)
    )
    
    # --- REGRA: COMPRA ---
    # Critérios: P/VP <= 0.95 e DY >= 8%
    condicao_compra = (
        (df_result['P_VP'] <= 0.95) & 
        (df_result['DY'] >= 8)
    )

    df_forte = df_result[condicao_forte].copy()
    df_compra = df_result[condicao_compra].copy()

    # Ordenar ambos pelo Magic Number (melhores oportunidades primeiro)
    df_forte = df_forte.sort_values('magic_number')
    df_compra = df_compra.sort_values('magic_number')

    return df_forte, df_compra

def aplicar_filtros_fiis(df):
    """
    Regra para FIIs: Quality >= 7, P/VP <= 0.95, e Magic <= 110
    """
    if 'Quality' not in df.columns:
        return pd.DataFrame()

    condicao_fii = (
        (df['Quality'] >= 7) & 
        (df['P_VP'] <= 0.95) & 
        (df['magic_number'] <= 110)
    )
    return df[condicao_fii].copy()