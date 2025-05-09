"""Symbol position."""

from decimal import Decimal

from pydantic import BaseModel, PositiveInt


class Position(BaseModel):
    # Parameters.
    symbol_name: str
    size: Decimal
    leverage: PositiveInt
    # State.
    pnl: Decimal

    @property
    def is_long(self) -> bool:
        return self.size > 0

    @property
    def is_short(self) -> bool:
        return self.size < 0
