"""Trading position."""

from decimal import Decimal

from pydantic import BaseModel


class Position(BaseModel):
    # Parameters.
    symbol_name: str
    size: Decimal
    # State.
    pnl: Decimal

    @property
    def is_long(self) -> bool:
        return self.size > Decimal("0")

    @property
    def is_short(self) -> bool:
        return self.size < Decimal("0")
