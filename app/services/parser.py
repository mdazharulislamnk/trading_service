import re
from app.models import OrderSide

class ParsingError(Exception):
    pass

class SignalParser:
    @staticmethod
    def parse(signal_text: str) -> dict:
        """
        Parses the raw signal text into a dictionary of values.
        Expected format:
        BUY EURUSD [@1.0860]
        SL 1.0850
        TP 1.0890
        """
        lines = signal_text.strip().splitlines()
        if not lines:
            raise ParsingError("Empty signal")

        # Line 1: ACTION SYMBOL [@PRICE]
        first_line = lines[0].upper()
        match = re.match(r"(BUY|SELL)\s+([A-Z0-9]+)(?:\s+@([\d\.]+))?", first_line)
        
        if not match:
            raise ParsingError("Invalid first line format. Expected: ACTION SYMBOL [@PRICE]")
        
        action, symbol, price = match.groups()
        data = {
            "side": OrderSide(action),
            "symbol": symbol,
            "price": float(price) if price else None,
            "sl": None,
            "tp": None
        }

        # Parse subsequent lines for SL and TP
        for line in lines[1:]:
            line = line.strip().upper()
            if line.startswith("SL"):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        data["sl"] = float(parts[1])
                    except ValueError:
                        raise ParsingError(f"Invalid SL value: {parts[1]}")
            elif line.startswith("TP"):
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        data["tp"] = float(parts[1])
                    except ValueError:
                        raise ParsingError(f"Invalid TP value: {parts[1]}")

        # Validation Logic
        if data["sl"] and data["tp"] and data["price"]:
            entry = data["price"]
            if data["side"] == OrderSide.BUY:
                if not (data["sl"] < entry < data["tp"]):
                    # Note: Sometimes TP might be open, but strict rule says SL < TP
                    if data["sl"] >= data["tp"]:
                        raise ParsingError("For BUY, SL must be lower than TP")
            elif data["side"] == OrderSide.SELL:
                if not (data["sl"] > entry > data["tp"]):
                    if data["sl"] <= data["tp"]:
                        raise ParsingError("For SELL, SL must be higher than TP")

        return data
