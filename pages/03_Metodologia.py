import streamlit as st

st.title("📊 Metodologia dos Scores")

st.set_page_config(page_title="Metodologia dos Scores", layout="wide")

st.write("Esta página resume todos os cálculos utilizados pelos motores de avaliação:")

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

Isso evita erros e mantém consistência.
""")

st.subheader("2. Benjamin Graham – Preço Justo")
st.latex(r"P_{Graham} = \sqrt{22.5 \cdot LPA \cdot VPA}")
st.markdown("""
- Se **LPA > 0** e **VPA > 0**, calcula-se o preço justo.
- A margem é dada por:

""")
st.latex(r"Margem = \left(\frac{P_{Graham}}{Preço} - 1\right) \cdot 100")

st.subheader("3. Décio Bazin – Preço Justo pelo Dividend Yield")
st.markdown("""
O método Bazin assume retorno mínimo de **6% ao ano**.

""")
st.latex(r"P_{Bazin} = \frac{Dividendos\ Anuais}{0.06}")

st.markdown("""
A margem é calculada como:

""")
st.latex(r"Margem = \left(\frac{P_{Bazin}}{Preço} - 1\right) \cdot 100")

st.subheader("4. Modelo de Gordon – 3 Cenários")
st.markdown("""
O modelo de Gordon é aplicado em três cenários:

| Cenário | k (desconto) | g (crescimento) |
|--------|--------------|-----------------|
| Apertado | 15% | 2% |
| Equilíbrio | 12% | 3% |
| Otimista | 10% | 5% |

Fórmula:
""")

st.latex(r"P = \frac{D_1}{k - g} \quad \text{onde} \quad D_1 = Dividendos \cdot (1+g)")

st.subheader("5. Magic Score")
st.markdown("""
O Magic Score é simplificado como:

""")
st.latex(r"Magic = P/VP \cdot 100")

st.subheader("6. Status da Ação")
st.markdown("""
Critérios usados:

- **FORTE COMPRA** → P/VP ≤ 0.90, DY ≥ 9%, Magic ≤ 110  
- **COMPRA** → P/VP ≤ 0.95 e DY ≥ 8%  
- **NEUTRO** → P/VP < 1.10  
- Caso contrário → **AGUARDAR**
""")

st.subheader("7. Queridinha da Bolsa")
st.markdown("""
Uma ação é marcada como **SIM** se a liquidez diária for ≥ **R$ 50 milhões**.
""")

st.markdown("---")

# -----------------------------
# SEÇÃO 2 — SCORE FIIs
# -----------------------------
st.header("🏢 Score para FIIs (ScoreFIIs)")

st.subheader("1. Indicadores Utilizados")
st.markdown("""
- **P/VP**
- **Dividend Yield**
- **Liquidez**
- **Quality Score** (nota de 0 a 10)
""")

st.subheader("2. Magic Score para FIIs")
st.latex(r"Magic = P/VP \cdot 100")

st.subheader("3. Status do FII")
st.markdown("""
Critérios:

- **FORTE COMPRA** → Quality ≥ 7, P/VP ≤ 0.95, Magic ≤ 110  
- **COMPRA** → P/VP ≤ 0.95 e DY ≥ 8%  
- Caso contrário → **AGUARDAR**
""")

st.subheader("4. Queridinha dos FIIs")
st.markdown("""
Um FII é marcado como **SIM** se a liquidez diária for ≥ **R$ 5 milhões**.
""")

st.markdown("---")

st.info("Esta página é atualizada automaticamente conforme a lógica dos motores ScoreAcoes e ScoreFIIs evolui.")
