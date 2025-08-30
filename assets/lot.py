from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from utils import Money, D

@dataclass
class Lot:
    """Lot class
    """
    qty: Decimal
    cost: Money  # total cost basis for this lot (incl. proportional fees)
    date: datetime

    @property
    def cost_per_share(self) -> Money:
        """calculate cost of each share

        Returns:
            Money: return the Money (decimal.Decimal) value
        """
        if self.qty == 0:
            return D(0)
        # IMPORTANT: use absolute qty so per-share cost is positive for both long and short lots
        return (self.cost / abs(self.qty)).quantize(D("0.0000001"))
