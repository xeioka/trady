"""Asset balance."""

from decimal import Decimal

from pydantic import BaseModel


class Balance(BaseModel):
    asset: str
    realized: Decimal
    unrealized: Decimal

    @property
    def total(self) -> Decimal:
        return self.realized + self.unrealized
