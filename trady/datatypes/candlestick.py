"""Symbol candlestick."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Candlestick(BaseModel):
    # Interval.
    open_datetime: datetime
    close_datetime: datetime
    # OHLC.
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    # Volume (in quote asset).
    buy_volume: Decimal
    sell_volume: Decimal

    @property
    def change(self) -> Decimal:
        return self.close - self.open

    @property
    def change_percent(self) -> Decimal:
        return (self.change / self.open) * 100

    @property
    def range(self) -> Decimal:
        return self.high - self.low

    @property
    def range_percent(self) -> Decimal:
        return (self.range / self.open) * 100

    @property
    def high_shadow(self) -> Decimal:
        return self.high - max(self.open, self.close)

    @property
    def high_shadow_percent(self) -> Decimal:
        return (self.high_shadow / self.open) * 100

    @property
    def low_shadow(self) -> Decimal:
        return min(self.open, self.close) - self.low

    @property
    def low_shadow_percent(self) -> Decimal:
        return (self.low_shadow / self.open) * 100

    @property
    def volume(self) -> Decimal:
        return self.buy_volume + self.sell_volume
