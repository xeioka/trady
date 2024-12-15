"""A single interface for various exchanges."""

from trady.exceptions import ExchangeException, InterfaceException
from trady.exchanges import Binance
from trady.interface import ExchangeInterface


__all__ = ("ExchangeException", "InterfaceException", "Binance", "ExchangeInterface")
