"""
money.py
"""
from decimal import Decimal


Money = Decimal
def D(x: str | float | int) -> Money: # pylint: disable=C0103
    """
    turn the numbers to a decimal.Decimal format

    Args:
        x (str | float | int): any number or str

    Returns:
        Money: A decimal.Decimal type
    """
    return Decimal(str(x))
