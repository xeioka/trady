"""This module contains the representation of a candlestick."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Candlestick(BaseModel):
    """Candlestick representation."""

    # Open/close datetime.
    open_datetime: datetime
    close_datetime: datetime

    # Open/low/high/close price.
    open_price: Decimal
    low_price: Decimal
    high_price: Decimal
    close_price: Decimal

    # Sell/buy volume (in quote asset).
    sell_volume: Decimal
    buy_volume: Decimal

    @property
    def change_value(self) -> Decimal:
        """Price change (value)."""
        return self.close_price - self.open_price

    @property
    def change(self) -> Decimal:
        """Price change (percent)."""
        return (self.change_value / self.open_price) * 100

    @property
    def range_value(self) -> Decimal:
        """Price range (value)."""
        return self.high_price - self.low_price

    @property
    def range(self) -> Decimal:
        """Price range (percent)."""
        return (self.range_value / self.open_price) * 100

    @property
    def low_shadow_value(self) -> Decimal:
        """Low shadow (value)."""
        return min(self.open_price, self.close_price) - self.low_price

    @property
    def low_shadow(self) -> Decimal:
        """Low shadow (percent)."""
        return (self.low_shadow_value / self.open_price) * 100

    @property
    def high_shadow_value(self) -> Decimal:
        """High shadow (value)."""
        return self.high_price - max(self.open_price, self.close_price)

    @property
    def high_shadow(self) -> Decimal:
        """High shadow (percent)."""
        return (self.high_shadow_value / self.open_price) * 100

    @property
    def total_volume(self) -> Decimal:
        """Total volume (in quote asset)."""
        return self.sell_volume + self.buy_volume

    @property
    def pressure(self) -> Decimal:
        """Sell/buy pressure (percent).

        Interpretation:
            - 0 means total sell pressure (sell volume = total volume);
            - 100 means total buy pressure (buy volume = total volume);
        """
        if self.total_volume == Decimal("0"):
            return Decimal("50")
        return (self.buy_volume / self.total_volume) * 100
