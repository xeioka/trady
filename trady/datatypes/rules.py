"""Symbol rules."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, PositiveInt


class Rules(BaseModel):
    # Size.
    size_min_value: Optional[Decimal] = None
    size_max_value: Optional[Decimal] = None
    size_step: Optional[Decimal] = None
    # Notional.
    notional_min_value: Optional[Decimal] = None
    notional_max_value: Optional[Decimal] = None
    # Leverage.
    leverage_max_value: Optional[PositiveInt] = None
    # Price.
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
