"""Trading rules."""

from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class Rules(BaseModel):
    # Size.
    size_min_value: Optional[Decimal] = None
    size_min_notional: Optional[Decimal] = None
    size_max_value: Optional[Decimal] = None
    size_max_notional: Optional[Decimal] = None
    size_step: Optional[Decimal] = None
    # Price.
    price_min_value: Optional[Decimal] = None
    price_max_value: Optional[Decimal] = None
    price_step: Optional[Decimal] = None

    def validate_size(
        self,
        size: Decimal,
        /,
        *,
        current_price: Optional[Decimal] = None,
    ) -> Decimal:
        abs_size = abs(size)
        if self.size_min_value is not None and abs_size < self.size_min_value:
            raise ValueError(f"size must be >= {self.size_min_value}")
        if (
            self.size_min_notional is not None
            and current_price is not None
            and (abs_size * current_price) < self.size_min_notional
        ):
            raise ValueError(f"notional must be >= {self.size_min_notional}")
        if self.size_max_value is not None and abs_size > self.size_max_value:
            raise ValueError(f"size must be <= {self.size_max_value}")
        if (
            self.size_max_notional is not None
            and current_price is not None
            and (abs_size * current_price) > self.size_max_notional
        ):
            raise ValueError(f"notional must be <= {self.size_max_notional}")
        if self.size_step:
            return (size // self.size_step) * self.size_step
        return size

    def validate_price(self, price: Decimal, /) -> Decimal:
        if self.price_min_value is not None and price < self.price_min_value:
            raise ValueError(f"price must be >= {self.price_min_value}")
        if self.price_max_value is not None and price > self.price_max_value:
            raise ValueError(f"price must be <= {self.price_max_value}")
        if self.price_step:
            return (price // self.price_step) * self.price_step
        return price
