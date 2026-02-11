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

        # --- CORREÇÃO DE CHAVES ---
        # Adicionei 'preco' e 'ULTIMO' para garantir que capture o valor da cota
        price = l(ativo.get("preco") or ativo.get("price") or ativo.get("PRECO") or ativo.get("ULTIMO") or 0.0)
        pvp = l(ativo.get("pvp") or ativo.get("P/VP") or 0.0)
        dy = l(ativo.get("dy") or ativo.get("DY") or 0.0)
        liq = l(ativo.get("liquidez") or ativo.get("LIQUIDEZ") or 0.0)
        quality = l(ativo.get("quality") or 7) # Default 7 se não houver nota
        
        magic_score = round(pvp * 100, 1)

        # --- STATUS FIIs (Baseado nos seus critérios de 2026) ---
        status = "AGUARDAR"
        if pvp > 0:
            # Forte compra: Quality >= 7, P/VP <= 0.95, e Magic <= 110
            if quality >= 7 and pvp <= 0.95 and magic_score <= 110: 
                status = "FORTE COMPRA"
            # Compra: P/VP <= 0.95 e DY >= 8%
            elif pvp <= 0.95 and dy >= 8: 
                status = "COMPRA"

        return {
            "Papel": str(ativo.get("Papel") or ativo.get("PAPEL") or ""),
            "preco": price,      # Alterado para 'preco' para casar com o 01_FIIs.py
            "dy": dy, 
            "pvp": pvp, 
            "status": status, 
            "magic": magic_score, 
            "quality": quality,
            "queridinha": "SIM" if liq >= 5000000 else "NÃO"
        }