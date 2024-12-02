"""Representation of a symbol and its rules."""

from decimal import Decimal

from pydantic import BaseModel


class Rules(BaseModel):
    """Rules representation."""

    # Order size rules.
    min_notional: Decimal | None = None
    min_size: Decimal | None = None
    max_size: Decimal | None = None
    size_step: Decimal | None = None

    # Order price rules.
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    price_step: Decimal | None = None


class Symbol(BaseModel):
    """Symbol representation."""

    base_asset: str
    quote_asset: str
    rules: Rules

    @property
    def name(self) -> str:
        """Symbol name."""
        return self.base_asset + self.quote_asset
