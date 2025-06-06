"""Symbol stats."""

from decimal import Decimal

from pydantic import BaseModel


class Stats(BaseModel):
    volume: Decimal
