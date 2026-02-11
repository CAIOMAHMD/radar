import math

class ScoreAcoes:
    @staticmethod
    def evaluate(ativo):
        # --- FUNÇÃO DE LIMPEZA (Essencial para não zerar os dados) ---
        def l(val):
            if val is None or val == "": return 0.0
            if isinstance(val, (int, float)): return float(val)
            s = str(val).replace('R$', '').replace(' ', '').replace('%', '').strip()
            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            try: return float(s)
            except: return 0.0

        # Mapeamento flexível de chaves
        price = l(ativo.get("price") or ativo.get("PRECO") or 0.0001)
        pvp = l(ativo.get("pvp") or ativo.get("P/VP") or 0.0)
        dy = l(ativo.get("dy") or ativo.get("DY") or 0.0)
        lpa = l(ativo.get("lpa") or ativo.get("LPA") or 0.0)
        vpa = l(ativo.get("vpa") or ativo.get("VPA") or 0.0)
        liq = l(ativo.get("liquidez") or ativo.get("LIQUIDEZ") or 0.0)
        ticker = str(ativo.get("Papel") or ativo.get("PAPEL") or "")

        # --- 1. BENJAMIN GRAHAM ---
        p_graham = math.sqrt(22.5 * lpa * vpa) if lpa > 0 and vpa > 0 else 0
        m_g = ((p_graham / price) - 1) * 100 if p_graham > 0 else 0
        m_graham_txt = f"{'+' if m_g > 0 else ''}{m_g:.1f}%" if p_graham > 0 else "---"

        # --- 2. DÉCIO BAZIN ---
        div_anual = price * (dy / 100)
        p_bazin = div_anual / 0.10 if dy > 0 else 0
        m_b = ((p_bazin / price) - 1) * 100 if p_bazin > 0 else 0
        m_bazin_txt = f"{'+' if m_b > 0 else ''}{m_b:.1f}%" if p_bazin > 0 else "---"

        # --- 3. GORDON (3 CENÁRIOS) ---
        def calc_gordon(k_perc, g_perc):
            k, g = k_perc/100, g_perc/100
            if dy > 0 and k > g:
                teto = (div_anual * (1 + g)) / (k - g)
                margem = ((teto / price) - 1) * 100
                return f"R$ {teto:.2f}", f"{'+' if margem > 0 else ''}{margem:.1f}%"
            return "---", "0%"

        g_apertado, m_apertado = calc_gordon(15, 2)
        g_equil, m_equil = calc_gordon(12, 3)
        g_otimista, m_otimista = calc_gordon(10, 5)

        # --- 4. STATUS E MAGIC (Seus Critérios: P/VP <= 0.90, DY >= 9, Magic <= 110) ---
        magic_score = round(pvp * 100, 1)
        status = "AGUARDAR"
        if pvp > 0:
            if pvp <= 0.90 and dy >= 9 and magic_score <= 110: status = "FORTE COMPRA"
            elif pvp <= 0.95 and dy >= 8: status = "COMPRA"
            elif pvp < 1.10: status = "NEUTRO"

        return {
            "Papel": ticker, "price": price, "dy": dy, "pvp": pvp, "status": status,
            "graham": f"R$ {p_graham:.2f}" if p_graham > 0 else "---",
            "m_graham": m_graham_txt,
            "bazin": f"R$ {p_bazin:.2f}" if p_bazin > 0 else "---",
            "m_bazin": m_bazin_txt,
            "g_apertado": g_apertado, "m_apertado": m_apertado,
            "g_equil": g_equil, "m_equil": m_equil,
            "g_otimista": g_otimista, "m_otimista": m_otimista,
            "magic": magic_score,
            "queridinha": "SIM" if liq >= 50000000 else "NÃO"
        }