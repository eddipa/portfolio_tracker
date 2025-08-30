from __future__ import annotations
from typing import Dict, List, Optional
from collections import deque

from utils import Money, D, MatchMethod
from assets import Trade, Lot

class Inventory:
    """Inventory of positions per ticker, supporting FIFO/LIFO matching.
    For shorts (allow_short=True), we allow negative aggregate qty, 
    represented as lots with negative qty.
    """

    def __init__(self, method: str = MatchMethod.FIFO, allow_short: bool = False):
        self.method = method
        self.allow_short = allow_short
        # Per-ticker lots (deque for FIFO efficiency). Each element is Lot.
        self._lots: Dict[str, deque[Lot]] = {}
        # Realized PnL per ticker
        self.realized: Dict[str, Money] = {}

    def _ensure(self, ticker: str) -> deque[Lot]:
        if ticker not in self._lots:
            self._lots[ticker] = deque()
            self.realized[ticker] = D(0)
        return self._lots[ticker]

    def apply_trade(self, tr: Trade):
        """apply trade

        Args:
            tr (Trade)

        Raises:
            ValueError: the side (Buy or Sell) is not defined
        """
        lots = self._ensure(tr.ticker)

        if tr.side == "BUY":
            self._buy(lots, tr)
        elif tr.side == "SELL":
            self._sell(lots, tr)
        else:
            raise ValueError(f"Unknown side {tr.side}")

    def _buy(self, lots: deque, tr: Trade):
        # Buying closes short lots first if present, then adds a long lot.
        qty = tr.qty
        price = tr.price
        fee = tr.fee
        #spend = (qty * price + fee)

        # If top of book is short (negative qty), buying will cover it.
        qty_remaining = qty

        def pop_left() -> 'Lot':
            return lots.popleft() if self.method == MatchMethod.FIFO else lots.pop()

        def push(l: Lot):
            if self.method == MatchMethod.FIFO:
                lots.append(l)
            else:
                lots.append(l)  # same append; pop direction changes match order

        # Cover shorts first
        while qty_remaining > 0 and lots and (lots[0].qty < 0 if self.method == MatchMethod.FIFO else lots[-1].qty < 0):
            lot = lots[0] if self.method == MatchMethod.FIFO else lots[-1]
            cover_qty = min(qty_remaining, -lot.qty)
            # Realized PnL = (lot cost per share * (-1) - buy price) * cover_qty? Wait: short opened with negative qty and cost is proceeds.
            # Convention: For a short lot, cost is the cash received (positive), qty is negative. Realized when covering: proceeds - cost basis per share -> actually PnL = (lot.cost_per_share - buy_price) * cover_qty
            pnl = (lot.cost_per_share - tr.price) * cover_qty
            self.realized[tr.ticker] += pnl
            lot.qty += cover_qty  # less negative
            lot.cost -= lot.cost_per_share * cover_qty  # reduce proportional cost/proceeds
            qty_remaining -= cover_qty
            if lot.qty == 0:
                pop_left()
        
        if qty_remaining > 0:
            # Add remaining as a long lot; include fee fully in this lot's cost basis.
            push(Lot(qty=qty_remaining, cost=qty_remaining * price + fee, date=tr.date))

    def _sell(self, lots: deque, tr: Trade):
        qty = tr.qty
        price = tr.price
        fee = tr.fee

        qty_remaining = qty

        def pop_left() -> 'Lot':
            return lots.popleft() if self.method == MatchMethod.FIFO else lots.pop()

        def peek() -> Optional[Lot]:
            return lots[0] if self.method == MatchMethod.FIFO else lots[-1]

        def push(l: Lot):
            lots.append(l)

        # Close long lots first
        while qty_remaining > 0 and lots and (peek().qty > 0):
            lot = peek()
            close_qty = min(qty_remaining, lot.qty)
            pnl = (price - lot.cost_per_share) * close_qty \
            - (fee if close_qty == qty_remaining else D(0))
            # Fee: allocate fully to the final matched piece of the sell. Simpler than prorating.
            self.realized[tr.ticker] += pnl
            lot.qty -= close_qty
            lot.cost -= lot.cost_per_share * close_qty
            qty_remaining -= close_qty
            if lot.qty == 0:
                pop_left()

        if qty_remaining > 0:
            if not self.allow_short:
                raise ValueError("Sell exceeds long position and shorting is disabled." \
                " Use --allow-short.")
            # Open a short lot for the remaining quantity.
            # For shorts, we store qty negative and cost as proceeds (net of fee).
            proceeds = qty_remaining * price - fee
            push(Lot(qty=-qty_remaining, cost=proceeds, date=tr.date))

    def positions(self) -> Dict[str, List[Lot]]:
        """get positions

        Returns:
            Dict[str, List[Lot]]: a dictionary of positions
        """
        return {t: list(lots) for t, lots in self._lots.items() if lots}
