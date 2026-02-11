import streamlit as st

# Configuração da página (DEVE ser a primeira instrução)
st.set_page_config(page_title="Metodologia dos Scores", layout="wide")

st.title("📊 Metodologia dos Scores")

st.write("Esta página resume todos os cálculos utilizados pelos motores de avaliação de Ações e FIIs:")

st.markdown("---")

# -----------------------------
# SEÇÃO 1 — SCORE AÇÕES
# -----------------------------
st.header("📈 Score para Ações (ScoreAcoes)")

st.subheader("1. Limpeza e Padronização dos Dados")
st.markdown("""
Todos os valores passam por uma função de limpeza que:
- Remove símbolos como `R$`, `%`, espaços e vírgulas.
- Converte números no formato brasileiro para float.
- Garante que valores vazios virem `0.0`.
- **Ajuste de Escala:** Corrige distorções onde P/VP > 500 ou DY > 100 (ajustando decimais).
""")

st.subheader("2. Benjamin Graham – Preço Justo")
st.latex(r"P_{Graham} = \sqrt{22.5 \cdot LPA \cdot VPA}")
st.markdown("""
A margem de segurança exibida abaixo do preço é calculada como:
""")
st.latex(r"Margem = \left(\frac{P_{Graham}}{Preço} - 1\right) \cdot 100")

st.subheader("3. Décio Bazin – Preço Justo")
st.markdown("O método Bazin assume um retorno mínimo de **6% ao ano**.")
st.latex(r"P_{Bazin} = \frac{Dividendos\ Anuais}{0.06}")

st.subheader("4. Modelo de Gordon – Cenários de Crescimento")
st.markdown("""
O modelo projeta o preço justo com base na taxa de desconto ($k$) e crescimento perpétuo ($g$):
""")
st.latex(r"P = \frac{Dividendos \cdot (1+g)}{k - g}")

st.markdown("""
| Coluna na Tabela | Cenário | Taxa Desconto ($k$) | Crescimento ($g$) |
|:---:|:---:|:---:|:---:|
| **Gordon (Apert.)** | Conservador | 15% | 2% |
| **Gordon (Equil.)** | Equilibrado | 12% | 3% |
| **Gordon (Otim.)** | Otimista | 10% | 5% |
""")

st.subheader("5. IA Sentimento (Gemini AI)")
st.markdown("""
O motor de IA realiza uma busca em tempo real no Google News (RSS) para os últimos 5 a 8 fatos relevantes do ativo.
- **Score (0-100):** Avalia se as notícias são otimistas ou pessimistas.
- **Resumo:** Uma síntese de até 10 palavras sobre o momento atual do mercado.
""")

st.subheader("6. Critérios de Classificação (Status)")
st.markdown("""
Conforme sua estratégia personalizada:
- **FORTE COMPRA** ➔ $P/VP \le 0.90$, $DY \ge 9\%$ e $Magic \le 110$.
- **COMPRA** ➔ $P/VP \le 0.95$ e $DY \ge 8\%$.
- **NEUTRO** ➔ $P/VP < 1.10$.
- **AGUARDAR** ➔ Ativos que não se enquadram nos filtros acima.
""")

st.markdown("---")

# -----------------------------
# SEÇÃO 2 — SCORE FIIs
# -----------------------------
st.header("🏢 Score para FIIs (ScoreFIIs)")

st.subheader("1. Critérios de Seleção")
st.markdown("""
- **FORTE COMPRA** ➔ Quality $\ge 7$, $P/VP \le 0.95$ e $Magic \le 110$.
- **COMPRA** ➔ $P/VP \le 0.95$ e $DY \ge 8\%$.
- **Queridinha (FIIs):** Liquidez diária $\ge$ R$ 5 Milhões.
""")

st.subheader("2. Bola de Neve (Cálculo de Cotas)")
st.markdown("""
Calcula quantas cotas são necessárias para que o dividendo pague uma nova cota:
""")
st.latex(r"N_{cotas} = \text{int}\left( \frac{1}{\text{DY Mensal}} \right)")

st.markdown("---")
st.info("💡 **Dica:** O Magic Score é calculado como $P/VP \cdot 100$.")