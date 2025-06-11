"""Market datatypes."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, PositiveInt


class Symbol(BaseModel):
    base_asset: str
    quote_asset: str

    @property
    def name(self) -> str:
        return self.base_asset + self.quote_asset

    def __eq__(self, other: object) -> bool:
        match other:
            case Symbol():
                return self.name == other.name
            case _:
                return self.name == other

    def __hash__(self) -> int:
        return hash(self.name)


class SymbolStats(BaseModel):
    volume: Decimal


class SymbolRules(BaseModel):
    # Position size (absolute value).
    size_min_value: Optional[Decimal] = None
    size_max_value: Optional[Decimal] = None
    size_step: Optional[Decimal] = None
    # Position notional (absolute value).
    notional_min_value: Optional[Decimal] = None
    notional_max_value: Optional[Decimal] = None
    # Position leverage.
    leverage_max_value: Optional[PositiveInt] = None
    # Position TP/SL price.
    price_min_value: Optional[Decimal] = None
    price_max_value: Optional[Decimal] = None
    price_step: Optional[Decimal] = None

    def validate_size(self, size: Decimal, /) -> Decimal:
        abs_size = abs(size)
        if self.size_min_value is not None and abs_size < self.size_min_value:
            raise ValueError(f"absolute size must be >= {self.size_min_value}")
        if self.size_max_value is not None and abs_size > self.size_max_value:
            raise ValueError(f"absolute size must be <= {self.size_max_value}")
        if self.size_step is not None:
            return (size // self.size_step) * self.size_step
        return size

    def validate_notional(self, notional: Decimal, /) -> Decimal:
        abs_notional = abs(notional)
        if self.notional_min_value is not None and abs_notional < self.notional_min_value:
            raise ValueError(f"absolute notional must be >= {self.notional_min_value}")
        if self.notional_max_value is not None and abs_notional > self.notional_max_value:
            raise ValueError(f"absolute notional must be <= {self.notional_max_value}")
        return notional

    def validate_leverage(self, leverage: PositiveInt, /) -> PositiveInt:
        if self.leverage_max_value is not None and leverage > self.leverage_max_value:
            raise ValueError(f"leverage must be <= {self.leverage_max_value}")
        return leverage

    def validate_price(self, price: Decimal, /) -> Decimal:
        if self.price_min_value is not None and price < self.price_min_value:
            raise ValueError(f"price must be >= {self.price_min_value}")
        if self.price_max_value is not None and price > self.price_max_value:
            raise ValueError(f"price must be <= {self.price_max_value}")
        if self.price_step is not None:
            return (price // self.price_step) * self.price_step
        return price


class Candlestick(BaseModel):
    # Open/close datetime.
    open_datetime: datetime
    close_datetime: datetime
    # Open/high/low/close price.
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    # Volume.
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


# Maps symbol names to stats.
MarketStats = dict[str, SymbolStats]
# Maps symbol names to rules.
MarketRules = dict[str, SymbolRules]
