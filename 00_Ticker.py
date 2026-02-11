import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import warnings
import time 
from coletor import obter_dados_b3
from score_acoes import ScoreAcoes
from sentiment_engine import SentimentEngine

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Radar Ticker IA", layout="wide")

st.title("📈 Ticker")

warnings.filterwarnings("ignore", category=FutureWarning)

def limpar_e_reconstruir(df):
    tradutor = {
        'LPA': 'lpa', 'VPA': 'vpa', 'P/VP': 'pvp', 'DY': 'dy', 
        'PRECO': 'price', 'PREÇO': 'price', 'ROE': 'roe', 
        'LIQUIDEZ': 'liquidez', 'PAPEL': 'Papel'
    }
    df.columns = [tradutor.get(c.upper(), c.lower()) for c in df.columns]
    
    cols_num = ['lpa', 'vpa', 'pvp', 'dy', 'price', 'roe', 'liquidez']
    for col in cols_num:
        if col not in df.columns: df[col] = 0
        df[col] = df[col].astype(str).str.replace('R$', '', regex=False).str.strip()
        df[col] = df[col].str.replace('%', '', regex=False).str.strip()
        
        def tratar_brasileiro(valor):
            if not valor or valor == 'nan': return "0"
            if ',' in valor:
                return valor.replace('.', '').replace(',', '.')
            return valor

        df[col] = df[col].apply(tratar_brasileiro)
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    for i, row in df.iterrows():
        if row['pvp'] > 500: df.at[i, 'pvp'] = row['pvp'] / 100 
        if row['dy'] > 100: df.at[i, 'dy'] = row['dy'] / 100
        if row['roe'] > 100: df.at[i, 'roe'] = row['roe'] / 100
        
        if row['lpa'] <= 0 and row['dy'] > 0:
            df.at[i, 'lpa'] = row['price'] * (row['dy'] / 100)
        if row['vpa'] <= 0 and row['pvp'] > 0:
            df.at[i, 'vpa'] = row['price'] / row['pvp']
            
    return df

def gerar_html_string(df):
    css = """
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f1f5f9; }
        .container { background: #1e293b; border-radius: 12px; padding: 15px; }
        table.dataTable { background: #1e293b !important; color: #cbd5e1 !important; border: none !important; width: 100% !important; }
        th { background: #0f172a !important; color: #38bdf8 !important; font-size: 10px; text-transform: uppercase; white-space: nowrap; }
        td { border-bottom: 1px solid #334155 !important; font-size: 11px; text-align: center; padding: 8px !important; }
        .status-FORTE { background: #e11d48; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; }
        .status-COMPRA { background: #2563eb; color: white; padding: 3px 8px; border-radius: 4px; }
        .bg-verde { background: rgba(74, 222, 128, 0.2) !important; color: #4ade80 !important; }
        .bg-vermelho { background: rgba(248, 113, 113, 0.2) !important; color: #f87171 !important; }
        .m-pos { color: #4ade80; font-weight: bold; }
        .m-neg { color: #f87171; }
        .g-highlight { background: rgba(56, 189, 248, 0.07) !important; border-left: 1px solid #334155 !important; border-right: 1px solid #334155 !important; }
        small { font-size: 9px; display: block; line-height: 1.1; }
        .fire-icon { color: #f59e0b; margin-right: 4px; }
    </style>
    """
    html = f"<html><head><meta charset='UTF-8'><link rel='stylesheet' type='text/css' href='https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css'>{css}</head><body>"
    
    # Cabeçalho atualizado com os labels de Gordon por extenso
    html += """<div class='container'><table><thead><tr>
                <th>Papel</th><th>Preço</th><th>DY %</th><th>Graham</th><th>Bazin</th>
                <th>Gordon (Apert.)</th><th class='g-highlight'>Gordon (Equil.)</th><th>Gordon (Otim.)</th>
                <th>IA Sentimento</th><th>Magic</th><th>Status</th>
            </tr></thead><tbody>"""
    
    for _, r in df.iterrows():
        st_val = str(r['status'])
        st_cl = "status-FORTE" if "FORTE" in st_val else ("status-COMPRA" if "COMPRA" in st_val else "")
        fire = '<span class="fire-icon">🔥</span>' if r.get('queridinha') == "SIM" else ""
        
        ia_raw = str(r.get('ia_score', '-'))
        ia_num = "".join(filter(str.isdigit, ia_raw.split(',')[0]))
        ia_class = ""
        if ia_num.isdigit():
            if int(ia_num) >= 75: ia_class = "bg-verde"
            elif int(ia_num) <= 50: ia_class = "bg-vermelho"
        
        resumo = str(r.get('ia_resumo', '')).upper().replace("RESUMO:", "").strip()

        html += f"""<tr>
            <td>{fire}<b>{r['Papel']}</b></td>
            <td>R$ {r['price']:.2f}</td>
            <td>{r['dy']:.1f}%</td>
            <td>{r['graham']}<br><small class="{'m-pos' if '+' in r['m_graham'] else 'm-neg'}">{r['m_graham']}</small></td>
            <td>{r['bazin']}<br><small class="{'m-pos' if '+' in r['m_bazin'] else 'm-neg'}">{r['m_bazin']}</small></td>
            <td>{r['g_apertado']}<br><small class="{'m-pos' if '+' in r['m_apertado'] else 'm-neg'}">{r['m_apertado']}</small></td>
            <td class='g-highlight'><b>{r['g_equil']}</b><br><small class="{'m-pos' if '+' in r['m_equil'] else 'm-neg'}">{r['m_equil']}</small></td>
            <td>{r['g_otimista']}<br><small class="{'m-pos' if '+' in r['m_otimista'] else 'm-neg'}">{r['m_otimista']}</small></td>
            <td class='{ia_class}'>{ia_num if ia_num else '-'}<br><small>{resumo[:35]}</small></td>
            <td><b>{r['magic']}</b></td>
            <td><span class="{st_cl}">{r['status']}</span></td>
        </tr>"""
    
    html += "</tbody></table></div><script src='https://code.jquery.com/jquery-3.7.0.js'></script><script src='https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js'></script>"
    html += "<script>$(document).ready(function(){$('table').DataTable({'pageLength': 25, 'scrollX': true, 'order': [[10, 'asc']]});});</script></body></html>"
    return html

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚙️ Controle Ticker")
    if st.button('🔄 1. ATUALIZAR B3'):
        dados = obter_dados_b3()
        if not dados.empty:
            df_limpo = limpar_e_reconstruir(dados)
            # Processamento do Score das Ações
            analisados = [ScoreAcoes.evaluate(row.to_dict()) for _, row in df_limpo.iterrows()]
            st.session_state['df_master'] = pd.DataFrame(analisados)

    if 'df_master' in st.session_state:
        st.divider()
        ticker_ia = st.selectbox("Analisar Sentimento:", ["-"] + sorted(st.session_state['df_master']['Papel'].tolist()))
        if ticker_ia != "-" and st.button('🚀 RODAR IA'):
            with st.spinner(f'Consultando {ticker_ia}...'):
                score, resumo = SentimentEngine.get_market_sentiment(ticker_ia)
                if "429" in str(score) or "EXCEED" in str(score).upper():
                    st.error("Limite atingido. Aguarde 2 min.")
                else:
                    idx = st.session_state['df_master'].index[st.session_state['df_master']['Papel'] == ticker_ia][0]
                    st.session_state['df_master'].at[idx, 'ia_score'] = score
                    st.session_state['df_master'].at[idx, 'ia_resumo'] = resumo
                    st.toast(f"{ticker_ia} atualizado!")
                    st.rerun()

# --- FILTROS E TABELA PRINCIPAL ---
if 'df_master' in st.session_state:
    st.markdown("""
    <div style="display: flex; gap: 15px; background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px; color:#38bdf8">
        <div style="font-size: 12px;">
            <b>IA Sentimento:</b> 
            <span style="color: #4ade80;">● 75–100 Positivo</span> | 
            <span style="color: #fbbf24;">● 51–74 Neutro</span> | 
            <span style="color: #f87171;">● 0–50 Risco</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
if 'df_master' in st.session_state:
    df_f = st.session_state['df_master'].copy()
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        so_queridinhas = st.checkbox("🔥 Apenas as Mais Queridas (Liq > 5M)")
    with col_f2:
        opcoes_status = sorted(df_f['status'].unique().tolist())
        status_sel = st.multiselect("Filtrar por Status:", opcoes_status, default=[s for s in ["FORTE COMPRA", "COMPRA"] if s in opcoes_status])

    # Filtros lógicos
    if so_queridinhas:
        df_f = df_f[df_f['queridinha'] == "SIM"]
    
    if status_sel:
        df_f = df_f[df_f['status'].isin(status_sel)]
    
    components.html(gerar_html_string(df_f), height=1000, scrolling=True)
else:
    st.info("👈 Clique em 'Atualizar B3' para começar.")

