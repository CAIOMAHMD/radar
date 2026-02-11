import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from coletor_fii import obter_dados_fii
from sentiment_engine import SentimentEngine
from score_fiis import ScoreFIIs 

# Configuração da página
st.set_page_config(page_title="Radar FIIs IA", layout="wide")

st.title("🏢 FIIs")

def gerar_html_fii(df):
    css = """
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #f1f5f9; }
        .container { background: #1e293b; border-radius: 12px; padding: 15px; }
        table.dataTable { background: #1e293b !important; color: #cbd5e1 !important; width: 100% !important; border: none !important; }
        
        /* Redução de Fontes */
        th { background: #0f172a !important; color: #38bdf8 !important; text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }
        td { border-bottom: 1px solid #334155 !important; font-size: 12px; text-align: center; padding: 8px !important; }
        
        /* Badges menores */
        .status-FORTE { background: #059669; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 10px; }
        .status-COMPRA { background: #2563eb; color: white; padding: 2px 8px; border-radius: 4px; font-size: 10px; }
        .star-icon { color: #fbbf24; margin-right: 3px; font-size: 10px; }
        .magic-highlight { color: #fbbf24; font-weight: bold; font-size: 11px; }
        .price-val { color: #f1f5f9; font-weight: bold; font-size: 12px; }
        
        /* IA Score */
        .ia-otimista { color: #4ade80; font-weight: bold; font-size: 11px; }
        .ia-neutro { color: #fbbf24; font-weight: bold; font-size: 11px; }
        .ia-pessimista { color: #f87171; font-weight: bold; font-size: 11px; }

        /* Ajuste do input de busca do DataTables */
        .dataTables_filter input { font-size: 12px; padding: 4px; }
    </style>
    """
    html = f"<html><head><link rel='stylesheet' type='text/css' href='https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css'>{css}</head><body>"
    html += """<div class='container'><table id='tabFii'><thead><tr>
                <th>Papel</th><th>Preço</th><th>P/VP</th><th>DY Anual</th><th>IA Score</th><th>Bola de Neve</th><th>Status</th>
            </tr></thead><tbody>"""
    
    for _, r in df.iterrows():
        st_val = str(r.get('status', 'AGUARDAR'))
        st_cl = "status-FORTE" if "FORTE" in st_val else ("status-COMPRA" if "COMPRA" in st_val else "")
        star = "<span class='star-icon'>⭐</span>" if r.get('queridinha') == "SIM" else ""
        
        # IA Score
        ia_val = r.get('ia_score', '-')
        ia_class = ""
        if ia_val != "-":
            try:
                v = float(ia_val)
                if v >= 70: ia_class = "ia-otimista"
                elif v >= 40: ia_class = "ia-neutro"
                else: ia_class = "ia-pessimista"
            except: pass

        # BOLA DE NEVE
        dy_val = r.get('dy', 0)
        dy_m = (dy_val / 12) / 100
        magic_n = int(1 / dy_m) if dy_m > 0 else 0
        
        # PREÇO
        v_preco = r.get('preco') or r.get('price') or 0.0

        html += f"""<tr>
            <td>{star}<b>{r.get('Papel', '???')}</b></td>
            <td class='price-val'>R$ {v_preco:.2f}</td>
            <td>{r.get('pvp', 0.0):.2f}</td>
            <td style='color:#4ade80'>{dy_val:.1f}%</td>
            <td class='{ia_class}'>{ia_val}</td>
            <td class='magic-highlight'>🎯 {magic_n} cotas</td>
            <td><span class='{st_cl}'>{st_val}</span></td>
        </tr>"""
    
    html += "</tbody></table></div><script src='https://code.jquery.com/jquery-3.7.0.js'></script><script src='https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js'></script>"
    html += "<script>$(document).ready(function(){$('#tabFii').DataTable({'pageLength': 50, 'order': [[2, 'asc']]});});</script></body></html>"
    return html

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏢 Controle FIIs")
    if st.button('🔄 ATUALIZAR B3'):
        dados = obter_dados_fii()
        if not dados.empty:
            analisados = [ScoreFIIs.evaluate(row.to_dict()) for _, row in dados.iterrows()]
            st.session_state['df_fii_master'] = pd.DataFrame(analisados)

    if 'df_fii_master' in st.session_state:
        st.divider()
        fii_ia = st.selectbox("Escolha para IA:", ["-"] + sorted(st.session_state['df_fii_master']['Papel'].tolist()))
        if fii_ia != "-" and st.button('🚀 RODAR IA'):
            score, resumo = SentimentEngine.get_market_sentiment(fii_ia)
            idx = st.session_state['df_fii_master'].index[st.session_state['df_fii_master']['Papel'] == fii_ia][0]
            st.session_state['df_fii_master'].at[idx, 'ia_score'] = score
            st.rerun()

# --- ÁREA PRINCIPAL ---
if 'df_fii_master' in st.session_state:
    st.markdown("""
    <div style="display: flex; gap: 15px; background: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px;color:#38bdf8">
        <div style="font-size: 12px;"><b>IA Score:</b> <span style="color: #4ade80;">● Otimista</span> | <span style="color: #fbbf24;">● Neutro</span> | <span style="color: #f87171;">● Risco</span></div>
    </div>
    """, unsafe_allow_html=True)

    df_f = st.session_state['df_fii_master'].copy()
    c1, c2 = st.columns(2)
    with c1: q = st.checkbox("⭐ Apenas Queridinhas")
    with c2: 
        status_options = sorted([s for s in df_f['status'].unique() if s])
        st_sel = st.multiselect("Status:", status_options, default=status_options)

    if q: df_f = df_f[df_f['queridinha'] == "SIM"]
    if st_sel: df_f = df_f[df_f['status'].isin(st_sel)]
    
    components.html(gerar_html_fii(df_f), height=1000, scrolling=True)