"""A single interface for various exchanges."""

from .exchanges import Binance
from .interface import ExchangeInterface


__all__ = (
    "Binance",
    "ExchangeInterface",
)
