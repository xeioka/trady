"""This module contains the Binance exchange implementation.

Resources
---------
API documentation:
  - https://binance-docs.github.io/apidocs/futures/en/#general-info
"""

from datetime import datetime

from .interface import ExchangeInterface


class Binance(ExchangeInterface):
    """Binance exchange implementation.

    Attributes
    ----------
    API_URL: str
        Base API URL.
    """

    API_URL: str = "https://fapi.binance.com/fapi/v1/"

    def get_datetime(self) -> datetime:
        # https://binance-docs.github.io/apidocs/futures/en/#check-server-time
        response = self.session.get(self.API_URL + "time")
        timestamp = response.json()["serverTime"] / 1000
        return datetime.fromtimestamp(timestamp)
