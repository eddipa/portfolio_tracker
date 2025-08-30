# Features
# - FIFO/LIFO matching
# - Fees per trade
# - Optional short selling
# - Realized & unrealized PnL
# - CSV I/O (trades, optional prices)
# - Simple CLI: python portfolio_tracker.py trades.csv FIFO --prices prices.csv [--allow-short]
#
# CSV formats
# trades.csv: date,ticker,side,qty,price,fee
#   Example: 2024-01-10,AAPL,BUY,10,180,0.50
# prices.csv: ticker,price
#   Example: AAPL,195.34

from __future__ import annotations
from decimal import getcontext
from typing import List, Optional
import argparse
import sys

from utils import MatchMethod
from assets import Inventory

from reports import build_report, print_report

from inputs import read_prices_csv, read_trades_csv

# Use Decimal for monetary precision.
getcontext().prec = 28

# ---------------------- CLI ----------------------
def run_cli(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Portfolio tracker (FIFO/LIFO) in pure Python.")
    p.add_argument("trades", help="Path to trades.csv")
    p.add_argument("method", choices=[MatchMethod.FIFO, MatchMethod.LIFO], help="Matching method")
    p.add_argument("--prices", help="Optional prices.csv with latest prices", default=None)
    p.add_argument("--allow-short", help="Allow short selling when sells exceed long qty", 
                   action="store_true")

    args = p.parse_args(argv)

    trades = read_trades_csv(args.trades)
    prices = read_prices_csv(args.prices)

    inv = Inventory(method=args.method, allow_short=args.allow_short)

    for tr in trades:
        inv.apply_trade(tr)

    rep = build_report(inv, prices)
    print_report(rep)
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
