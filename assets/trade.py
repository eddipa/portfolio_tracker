from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict

from utils import Money, D

@dataclass
class Trade:
    """
    Trade class
    """
    date: datetime
    ticker: str
    side: str  # "BUY" or "SELL"
    qty: Decimal
    price: Money
    fee: Money = D(0)

    @staticmethod
    def from_row(row: Dict[str, str]) -> "Trade":
        """
        Expected keys: date,ticker,side,qty,price,fee
        Accepts ISO-like dates: YYYY-MM-DD or YYYY/MM/DD
        """
        date_str = row["date"].replace("/", "-")
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return Trade(
            date=dt,
            ticker=row["ticker"].strip().upper(),
            side=row["side"].strip().upper(),
            qty=D(row["qty"]),
            price=D(row["price"]),
            fee=D(row.get("fee", "0") or "0"),
        )
