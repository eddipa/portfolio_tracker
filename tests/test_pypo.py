from datetime import datetime
from decimal import Decimal as D
import pytest
from assets import Trade, Inventory
from utils import MatchMethod
from reports import build_report

def T(date, ticker, side, qty, price, fee=0):
    return Trade(
        date=datetime.strptime(date, "%Y-%m-%d"),
        ticker=ticker,
        side=side,
        qty=D(str(qty)),
        price=D(str(price)),
        fee=D(str(fee)),
    )

def test_fifo_basic_realized():
    inv = Inventory(method=MatchMethod.FIFO)
    inv.apply_trade(T("2024-01-10", "AAPL", "BUY", 10, 100, 0))
    inv.apply_trade(T("2024-02-01", "AAPL", "SELL", 4, 110, 0.5))
    # Realized: (110-100)*4 - 0.5 = 39.5
    assert inv.realized["AAPL"] == D("39.5")

def test_lifo_mixed_lots_realized():
    inv = Inventory(method=MatchMethod.LIFO)
    inv.apply_trade(T("2024-01-10", "AAPL", "BUY", 10, 100, 0))
    inv.apply_trade(T("2024-01-20", "AAPL", "BUY", 5, 120, 0))
    inv.apply_trade(T("2024-02-01", "AAPL", "SELL", 6, 110, 0))
    # LIFO: sell 5 from 120 (-10 each -> -50), plus 1 from 100 (+10) => total -40
    assert inv.realized["AAPL"] == D("-40")

def test_fee_in_cost_basis_on_buy():
    inv = Inventory(method=MatchMethod.FIFO)
    inv.apply_trade(T("2024-01-10", "MSFT", "BUY", 10, 100, 1.0))
    rep = build_report(inv, {"MSFT": D("100")})
    pos = next(p for p in rep.positions if p.ticker == "MSFT")
    # Avg cost per share should include fee: 100 + 1/10 = 100.1
    assert pos.avg_cost.quantize(D("0.0001")) == D("100.1000")

def test_unrealized_long():
    inv = Inventory(method=MatchMethod.FIFO)
    inv.apply_trade(T("2024-01-10", "AAPL", "BUY", 10, 100, 0))
    rep = build_report(inv, {"AAPL": D("105")})
    pos = next(p for p in rep.positions if p.ticker == "AAPL")
    # Unrealized = (105 - 100) * 10 = 50
    assert pos.unrealized_pnl == D("50")

def test_short_cover_and_unrealized_short():
    inv = Inventory(method=MatchMethod.FIFO, allow_short=True)
    # Open short 5 @ 50
    inv.apply_trade(T("2024-01-10", "TSLA", "SELL", 5, 50, 0))
    # Cover 3 @ 40 -> realized = (50 - 40) * 3 = 30
    inv.apply_trade(T("2024-01-15", "TSLA", "BUY", 3, 40, 0))
    assert inv.realized["TSLA"] == D("30")
    # Remaining short: 2 shares opened at 50. At price 45, unrealized = (50 - 45) * 2 = 10
    rep = build_report(inv, {"TSLA": D("45")})
    pos = next(p for p in rep.positions if p.ticker == "TSLA")
    assert pos.qty == D("-2")
    assert pos.unrealized_pnl == D("10")

def test_short_partial_cover_cost_carries_correctly():
    inv = Inventory(method=MatchMethod.FIFO, allow_short=True)
    inv.apply_trade(T("2024-01-10", "TSLA", "SELL", 5, 50, 0))     # cost = 250, qty = -5
    inv.apply_trade(T("2024-01-15", "TSLA", "BUY", 3, 40, 0))      # cover 3 -> cost should be 100, qty = -2
    # Peek into internal lots
    lots = inv._lots["TSLA"] # pylint: disable=W0212
    lot = lots[0]
    assert lot.qty == D("-2")
    assert lot.cost == D("100")
    rep = build_report(inv, {"TSLA": D("45")})
    pos = next(p for p in rep.positions if p.ticker == "TSLA")
    assert pos.unrealized_pnl == D("10")

def test_sell_exceeds_without_short_raises():
    inv = Inventory(method=MatchMethod.FIFO, allow_short=False)
    inv.apply_trade(T("2024-01-10", "AAPL", "BUY", 1, 100, 0))
    with pytest.raises(ValueError):
        inv.apply_trade(T("2024-01-11", "AAPL", "SELL", 2, 110, 0))
