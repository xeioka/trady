"""Binance implementation.

Resources
---------
API documentation:
  - https://binance-docs.github.io/apidocs/futures/en/#general-info
"""

from .binance import Binance
from .settings import BinanceSettings


__all__ = ("Binance", "BinanceSettings")
