"""This module contains the exchange interface.

Exchange interface is an abstract interface that defines a unified way
of implementing various exchanges and exposing common functionality.
"""

import abc
from datetime import datetime

from requests import Session

from .datatypes import Candlestick, Symbol


class ExchangeInterface(abc.ABC):
    """Exchange interface.

    Public interface methods must be implemented by overriding their protected
    counterpart and utilizing `self.session` for making HTTP requests (API calls).

    Third-party API connectors/libraries _must not_ be used
    since they tend to restrict the available functionality.

    Attributes (cls)
    ----------------
    CANDLESTICKS_MAX_LIMIT
        Maximum number of candlesticks that can be retrieved in a single API request.
        Implementations must specify this value according to the exchange API limit.

    Attributes (self)
    -----------------
    session
        A session object for making HTTP requests, see
        https://requests.readthedocs.io/en/latest/user/advanced/#session-objects

    Examples
    --------
    See the Binance implementation (`trady.binance`).
    """

    CANDLESTICKS_MAX_LIMIT: int = 10

    def __init__(self) -> None:
        self.session: Session = Session()

    def get_datetime(self) -> datetime:
        """Retrieves datetime."""
        return self._get_datetime()

    def get_symbols(self) -> list[Symbol]:
        """Retrieves available symbols."""
        return self._get_symbols()

    def get_candlesticks(
        self,
        symbol: Symbol,
        interval: int,
        limit: int = CANDLESTICKS_MAX_LIMIT,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Retrieves candlesticks for a symbol (in a single API request).

        This method will return the latest candlesticks unless `start_datetime`/`end_datetime` is specified.

        Parameters
        ----------
        symbol
            A symbol to retrieve the candlesticks for.
        interval
            Candlesticks interval (in seconds).
        limit
            Maximum number of candlesticks. Must belong to [1, `CANDLESTICKS_MAX_LIMIT`].
            Note that this methods will always try to return the maximum number.
        start_datetime
            Specifies the earliest open datetime and a starting point.
        end_datetime
            Specifies the latest open datetime.
        """
        assert 1 <= limit <= self.CANDLESTICKS_MAX_LIMIT, f"invalid limit {limit}"
        return self._get_candlesticks(
            symbol,
            interval,
            limit=limit,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def _get_datetime(self) -> datetime:
        """Override this to implement `get_datetime()`."""
        raise NotImplementedError

    def _get_symbols(self) -> list[Symbol]:
        """Override this to implement `get_symbols()`."""
        raise NotImplementedError

    def _get_candlesticks(
        self,
        symbol: Symbol,
        interval: int,
        limit: int = CANDLESTICKS_MAX_LIMIT,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Override this to implement `get_candlesticks()`."""
        raise NotImplementedError
