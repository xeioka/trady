"""This module contains the exchange interface.

Exchange interface is an abstract interface that defines a unified way
of implementing various exchanges and exposing common functionality.
"""

import abc
import time
from datetime import datetime
from typing import Iterator

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
    CANDLESTICKS_MAX_NUMBER
        Maximum number of candlesticks that can be retrieved in a single API request.
        Implementations must configure this attribute according to the exchange API limitations.
    CANDLESTICKS_ITERATOR_THROTTLE
        A delay between the API requests in `get_candlesticks_iterator()` (to avoid violating rate limits).
        Implementations must configure this attribute according to the exchange API limitations.

    Attributes (self)
    -----------------
    session
        A session object for making HTTP requests, see
        https://requests.readthedocs.io/en/latest/user/advanced/#session-objects

    Examples
    --------
    See the Binance implementation (`trady.binance`).
    """

    CANDLESTICKS_MAX_NUMBER: int = 10
    CANDLESTICKS_ITERATOR_THROTTLE: float = 0.1

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
        number: int = CANDLESTICKS_MAX_NUMBER,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Retrieves candlesticks (single API request).

        This method will return the latest candlesticks unless `start_datetime` or `end_datetime` is specified.

        Note that the maximum `number` of candlesticks is limited by `CANDLESTICKS_MAX_NUMBER`.
        To retrieve all candlesticks for a given datetime period, use `get_candlesticks_iterator()`.

        Parameters
        ----------
        symbol
            A symbol to retrieve the candlesticks for.
        interval
            Candlesticks interval (in seconds).
        number
            Required number of candlesticks. The maximum value is `CANDLESTICKS_MAX_NUMBER`.
            If there's not enough candlesticks the method will simply return all of them.
        start_datetime
            Specifies a candlestick open datetime to start with.
        end_datetime
            Specifies the maximum candlestick open datetime.
        """
        assert 1 <= number <= self.CANDLESTICKS_MAX_NUMBER, f"invalid number {number}"
        return self._get_candlesticks(
            symbol,
            interval,
            number=number,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def get_candlesticks_iterator(
        self,
        symbol: Symbol,
        interval: int,
        start_datetime: datetime,
        end_datetime: datetime,
    ) -> Iterator[Candlestick]:
        """Retrieves candlesticks (chained API requests).

        This method allows to retrieve all candlesticks for a given datetime
        period by safely chaining the underlying `get_candlesticks()` calls.

        Note that "safely" depends on the value of `CANDLESTICKS_ITERATOR_THROTTLE`.

        Parameters
        ----------
        symbol
            A symbol to retrieve the candlesticks for.
        interval
            Candlesticks interval (in seconds).
        start_datetime
            Specifies a candlestick open datetime to start with.
        end_datetime
            Specifies a candlestick open datetime to end with.
        """
        while True:
            candlesticks = self.get_candlesticks(
                symbol,
                interval,
                number=self.CANDLESTICKS_MAX_NUMBER,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
            for candlestick in candlesticks:
                yield candlestick
            if (
                len(candlesticks) < self.CANDLESTICKS_MAX_NUMBER
                or candlesticks[-1].close_datetime >= end_datetime
            ):
                return
            start_datetime = candlesticks[-1].close_datetime
            time.sleep(self.CANDLESTICKS_ITERATOR_THROTTLE)

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
        number: int = CANDLESTICKS_MAX_NUMBER,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Override this to implement `get_candlesticks()` and `get_candlesticks_iterator()`."""
        raise NotImplementedError
