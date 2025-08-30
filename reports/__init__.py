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
    """
    Build a report with correct unrealized PnL handling for both longs and shorts.
    - Long lots (qty > 0): unreal = (mkt - cost_per_share) * qty
    - Short lots (qty < 0): unreal = (cost_per_share - mkt) * (-qty)
    Equity uses market value = qty * mkt (negative for shorts).
    """
    positions: List[PositionSummary] = []

    total_unrealized = D(0)
    total_equity = D(0)

    for ticker, lots in inv.positions().items():
        if not lots:
            continue
        mkt = prices.get(ticker, D(0))

        agg_qty = D(0)
        agg_cost_basis = D(0)
        unreal = D(0)
        market_value = D(0)

        for lot in lots:
            cp = lot.cost_per_share
            if lot.qty > 0:
                # Long: gain if market > cost
                unreal += (mkt - cp) * lot.qty
            elif lot.qty < 0:
                # Short: gain if market < cost
                unreal += (cp - mkt) * (-lot.qty)
            agg_qty += lot.qty
            agg_cost_basis += lot.cost
            market_value += lot.qty * mkt

        if agg_qty == 0:
            continue

        # Average cost per share (positive number for both long & short)
        avg_cost_per_share = (
            (agg_cost_basis / abs(agg_qty)).quantize(D("0.0000001"))
            if agg_qty != 0 else D(0)
        )

        positions.append(PositionSummary(
            ticker=ticker,
            qty=agg_qty,
            avg_cost=avg_cost_per_share,
            mkt_price=mkt,
            market_value=market_value,
            cost_basis=agg_cost_basis,
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
