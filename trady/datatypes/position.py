"""Symbol position."""

from decimal import Decimal

from pydantic import BaseModel, PositiveInt


class Position(BaseModel):
    # Parameters.
    symbol_name: str
    size: Decimal
    leverage: PositiveInt
    # State.
    unrealized_pnl: Decimal

    @property
    def is_long(self) -> bool:
        return self.size > Decimal("0")

    @property
    def is_short(self) -> bool:
        return self.size < Decimal("0")
