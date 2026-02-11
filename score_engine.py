import math

class ScoreEngine:
    @staticmethod
    def evaluate(ativo):
        # --- LIMPEZA DE DADOS PESADA ---
        def limpar_fin(val):
            if val is None or val == "": return 0.0
            if isinstance(val, (int, float)): return float(val)
            s = str(val).replace('R$', '').replace(' ', '').replace('%', '').strip()
            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            try: return float(s)
            except: return 0.0

        # Tenta pegar os dados independente se a chave é 'pvp', 'P/VP', 'PVP', etc.
        price = limpar_fin(ativo.get("price") or ativo.get("PRECO") or ativo.get("PREÇO") or 0.0001)
        pvp = limpar_fin(ativo.get("pvp") or ativo.get("P/VP") or ativo.get("PVP") or ativo.get("P/VPA") or 0.0)
        dy = limpar_fin(ativo.get("dy") or ativo.get("DY") or 0.0)
        lpa = limpar_fin(ativo.get("lpa") or ativo.get("LPA") or 0.0)
        vpa = limpar_fin(ativo.get("vpa") or ativo.get("VPA") or 0.0)
        liquidez = limpar_fin(ativo.get("liquidez") or ativo.get("LIQUIDEZ") or 0.0)
        
        ticker = str(ativo.get("Papel") or ativo.get("PAPEL") or ativo.get("TICKER") or "")
        is_fii = ativo.get("is_fii", False) or ticker.endswith('11')
        
        # --- CÁLCULOS BASE ---
        div_anual = price * (dy / 100)
        p_graham = math.sqrt(22.5 * lpa * vpa) if not is_fii and lpa > 0 and vpa > 0 else 0

        # --- GORDON ---
        def calc_gordon(k_p, g_p):
            k, g = k_p/100, g_p/100
            g_f = min(g, 0.01) if is_fii else g 
            if dy > 0 and k > g_f:
                teto = (div_anual * (1 + g_f)) / (k - g_f)
                return f"R$ {teto:.2f}", f"{((teto/price)-1)*100:+.1f}%"
            return "---", "0%"

        ga, ma = calc_gordon(15, 2)
        ge, me = calc_gordon(12, 3)
        go, mo = calc_gordon(10, 5)

        # --- STATUS E MÁGICA ---
        magic = round(pvp * 100, 1)
        status = "AGUARDAR"
        
        # SÓ VALIDA STATUS SE O PVP FOR MAIOR QUE ZERO (Evita erro de dado vazio)
        if pvp > 0:
            if is_fii:
                if pvp <= 0.95 and dy >= 9 and magic <= 110: status = "FORTE COMPRA"
                elif pvp <= 0.95 and dy >= 8: status = "COMPRA"
            else:
                if pvp <= 0.90 and dy >= 9 and magic <= 110: status = "FORTE COMPRA"
                elif pvp <= 0.95 and dy >= 8: status = "COMPRA"
                elif pvp < 1.10: status = "NEUTRO"

        limiar = 5000000 if is_fii else 10000000

        return {
            "Papel": ticker, "price": price, "dy": dy, "pvp": pvp, "status": status,
            "graham": f"R$ {p_graham:.2f}" if p_graham > 0 else "---",
            "m_graham": f"{((p_graham/price)-1)*100:+.1f}%" if p_graham > 0 else "---",
            "g_equil": ge, "m_equil": me,
            "magic": magic,
            "queridinha": "SIM" if liquidez >= limiar else "NÃO"
        }