"""Representation of the balance."""

from decimal import Decimal

from pydantic import BaseModel


class Balance(BaseModel):
    """Balance representation."""

    realized: Decimal
    unrealized: Decimal
