"""Trading position."""

from decimal import Decimal

from pydantic import BaseModel, PositiveInt

from .symbol import Symbol


class Position(BaseModel):
    # Parameters.
    symbol: Symbol
    size: Decimal
    leverage: PositiveInt
    # State.
    pnl: Decimal

    @property
    def is_long(self) -> bool:
        return self.size > Decimal("0")

    @property
    def is_short(self) -> bool:
        return self.size < Decimal("0")
