from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List

from utils import Money, D

from assets import Inventory

@dataclass
class PositionSummary:
    ticker: str
    qty: Decimal
    avg_cost: Money
    mkt_price: Money
    market_value: Money
    cost_basis: Money
    unrealized_pnl: Money


@dataclass
class Report:
    method: str
    realized_pnl: Dict[str, Money]
    positions: List[PositionSummary]
    total_realized: Money
    total_unrealized: Money
    total_equity: Money

def build_report(inv: Inventory, prices: Dict[str, Money]) -> Report:
    positions: List[PositionSummary] = []

    total_unrealized = D(0)
    total_equity = D(0)

    for ticker, lots in inv.positions().items():
        qty = sum((lot.qty for lot in lots), D(0))
        if qty == 0:
            continue
        mkt = prices.get(ticker, D(0))
        # Aggregate cost basis and market value
        cost_basis = sum((lot.cost for lot in lots), D(0))
        market_value = qty * mkt
        unreal = market_value - cost_basis
        avg_cost_per_share = (cost_basis / qty).quantize(D("0.0000001")) if qty != 0 else D(0)
        positions.append(PositionSummary(
            ticker=ticker,
            qty=qty,
            avg_cost=avg_cost_per_share,
            mkt_price=mkt,
            market_value=market_value,
            cost_basis=cost_basis,
            unrealized_pnl=unreal,
        ))
        total_unrealized += unreal
        total_equity += market_value

    total_realized = sum(inv.realized.values(), D(0))

    return Report(
        method=inv.method,
        realized_pnl=dict(inv.realized),
        positions=sorted(positions, key=lambda p: p.ticker),
        total_realized=total_realized,
        total_unrealized=total_unrealized,
        total_equity=total_equity,
    )

# ---------------------- Reporting (console) ----------------------

def fmt_money(x: Money) -> str:
    return f"{x.quantize(D('0.01'), rounding=ROUND_HALF_UP)}"


def print_report(rep: Report):
    print(f"\n=== Portfolio Report ({rep.method}) ===")
    print("-- Realized PnL by ticker --")
    if rep.realized_pnl:
        for t, v in sorted(rep.realized_pnl.items()):
            print(f"  {t:8s} {fmt_money(v):>12s}")
    else:
        print("  (none)")

    print("\n-- Open Positions --")
    if not rep.positions:
        print("  (none)")
    else:
        header = f"{'Ticker':<8}{'Qty':>12}{'AvgCost':>14}{'Price':>12}\
            {'MktValue':>14}{'CostBasis':>14}{'UnrlPnL':>14}"
        print(header)
        print("-" * len(header))
        for p in rep.positions:
            print(
                f"{p.ticker:<8}{str(p.qty):>12}{fmt_money(p.avg_cost):>14}\
                    {fmt_money(p.mkt_price):>12}"
                f"{fmt_money(p.market_value):>14}{fmt_money(p.cost_basis):>14}\
                    {fmt_money(p.unrealized_pnl):>14}"
            )

    print("\n-- Totals --")
    print(f"  Realized:   {fmt_money(rep.total_realized)}")
    print(f"  Unrealized: {fmt_money(rep.total_unrealized)}")
    print(f"  Equity:     {fmt_money(rep.total_equity)}\n")
