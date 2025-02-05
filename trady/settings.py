"""Abstract exchange settings.

Every exchange implementation must define its own settings by subclassing `ExchangeSettings`.

Resources
---------
Pydantic settings:
    - https://docs.pydantic.dev/latest/concepts/pydantic_settings/
"""

from pydantic import HttpUrl, NonNegativeFloat, PositiveInt
from pydantic_settings import BaseSettings


class ExchangeSettings(BaseSettings, env_file=".env", env_prefix="trady__"):
    """Abstract exchange settings.

    Subclasses must provide a unique `env_prefix` value (e.g. `trady__binance__`).

    Attributes
    ----------
    api_url
        Base API URL.
    candlesticks_max_number
        Maximum number of candlesticks that can be retrieved in a single API request.
    candlesticks_iterator_throttle
        A delay between the API requests (in seconds) when retrieving more candlesticks
        than `candlesticks_max_number`. It helps to prevent violating rate limits.

    Examples
    --------
    See `trady.exchanges.binance`.
    """

    api_url: HttpUrl
    candlesticks_max_number: PositiveInt
    candlesticks_iterator_throttle: NonNegativeFloat
