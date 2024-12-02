"""Abstract exchange settings.

Exchange settings define what settings must be exposed and configured for every exchange.

All exchanges must define their own settings by subclassing `ExchangeSettings`.

Resources
---------
Pydantic Settings:
    - https://docs.pydantic.dev/latest/concepts/pydantic_settings/
"""

from pydantic import HttpUrl, NonNegativeFloat, PositiveInt
from pydantic_settings import BaseSettings


class ExchangeSettings(BaseSettings, env_file=".env"):
    """Abstract exchange settings.

    Subclasses must provide unique `env_prefix` value (use `trady__{exchange_name}__`), see
    https://docs.pydantic.dev/latest/concepts/pydantic_settings/#environment-variable-names.

    Attributes
    ----------
    self.api_url
        Base API URL.
    self.candlesticks_max_number
        Maximum number of candlesticks that can be retrieved in a single API request.
    self.candlesticks_iterator_throttle
        A delay between the API requests when retrieving more candlesticks than
        `self.candlesticks_max_number`. It helps to avoid violating rate limits.

    Examples
    --------
    See any exchange in `trady.exchanges`.
    """

    api_url: HttpUrl
    candlesticks_max_number: PositiveInt
    candlesticks_iterator_throttle: NonNegativeFloat
