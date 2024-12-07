"""Binance settings.

Resources
---------
API documentation:
  - https://binance-docs.github.io/apidocs/futures/en/#general-info
"""

from pydantic import HttpUrl, NonNegativeFloat, PositiveInt

from trady.settings import ExchangeSettings


class BinanceSettings(ExchangeSettings, env_prefix="trady__binance__"):
    """Binance settings."""

    api_url: HttpUrl = HttpUrl("https://fapi.binance.com/fapi/")
    api_key: str = ""
    api_secret: str = ""
    candlesticks_max_number: PositiveInt = 1500
    candlesticks_iterator_throttle: NonNegativeFloat = 0.1
