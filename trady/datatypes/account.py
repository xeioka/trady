"""Account datatypes."""

from decimal import Decimal

from pydantic import BaseModel, PositiveInt


class Balance(BaseModel):
    realized: Decimal
    unrealized: Decimal

    @property
    def total(self) -> Decimal:
        return self.realized + self.unrealized


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


# Maps symbol names to positions.
AccountPositions = dict[str, Position]
