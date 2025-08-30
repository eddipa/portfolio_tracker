from __future__ import annotations
from typing import Dict, List, Optional
import csv

from utils import Money, D
from assets import Trade

# ---------------------- CSV helpers ----------------------
def read_trades_csv(path: str) -> List[Trade]:
    trades: List[Trade] = []
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        # required = {"date", "ticker", "side", "qty", "price", "fee"}
        # missing = required - set(map(str.lower, r.fieldnames or []))
        # Accept case-insensitive headers by normalizing keys
        for row in r:
            # normalize keys to lower
            nrow = {k.lower(): v for k, v in row.items()}
            trades.append(Trade.from_row(nrow))
    trades.sort(key=lambda t: t.date)
    return trades


def read_prices_csv(path: Optional[str]) -> Dict[str, Money]:
    prices: Dict[str, Money] = {}
    if not path:
        return prices
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            ticker = row["ticker"].strip().upper()
            prices[ticker] = D(row["price"])  # no validation here
    return prices
