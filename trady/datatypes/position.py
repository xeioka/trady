"""Representation of a position."""

from decimal import Decimal

from pydantic import BaseModel, PositiveInt

from .symbol import Symbol


class Position(BaseModel):
    """Position representation."""

    # Parameters.
    symbol: Symbol
    size: Decimal
    leverage: PositiveInt
    # PnL.
    pnl: Decimal

    @property
    def is_short(self) -> bool:
        """Whether it's short."""
        return self.size < Decimal("0")

    @property
    def is_long(self) -> bool:
        """Whether it's long."""
        return self.size > Decimal("0")
