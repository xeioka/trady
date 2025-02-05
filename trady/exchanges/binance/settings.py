"""Binance settings.

Resources
---------
API documentation:
    - https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
"""

from pydantic import HttpUrl, NonNegativeFloat, PositiveInt

from trady.settings import ExchangeSettings


class BinanceSettings(ExchangeSettings, env_prefix="trady__binance__"):
    api_url: HttpUrl = HttpUrl("https://fapi.binance.com/fapi/")
    candlesticks_max_number: PositiveInt = 1500
    candlesticks_iterator_throttle: NonNegativeFloat = 0.2
    api_key: str = ""
    api_secret: str = ""
