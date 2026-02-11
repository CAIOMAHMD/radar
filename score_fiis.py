class ScoreFIIs:
    @staticmethod
    def evaluate(ativo):
        def l(val):
            if val is None or val == "": return 0.0
            if isinstance(val, (int, float)): return float(val)
            s = str(val).replace('R$', '').replace(' ', '').replace('%', '').strip()
            if '.' in s and ',' in s: s = s.replace('.', '').replace(',', '.')
            elif ',' in s: s = s.replace(',', '.')
            try: return float(s)
            except: return 0.0

        price = l(ativo.get("price") or ativo.get("PRECO") or 0.0001)
        pvp = l(ativo.get("pvp") or ativo.get("P/VP") or 0.0)
        dy = l(ativo.get("dy") or ativo.get("DY") or 0.0)
        liq = l(ativo.get("liquidez") or ativo.get("LIQUIDEZ") or 0.0)
        quality = l(ativo.get("quality") or 7)
        
        magic_score = round(pvp * 100, 1)

        # Status FIIs (Critérios: Quality >= 7, P/VP <= 0.95, Magic <= 110)
        status = "AGUARDAR"
        if pvp > 0:
            if quality >= 7 and pvp <= 0.95 and magic_score <= 110: status = "FORTE COMPRA"
            elif pvp <= 0.95 and dy >= 8: status = "COMPRA"

        return {
            "Papel": str(ativo.get("Papel") or ativo.get("PAPEL") or ""),
            "price": price, "dy": dy, "pvp": pvp, "status": status, 
            "magic": magic_score, "quality": quality,
            "queridinha": "SIM" if liq >= 5000000 else "NÃO"
        }