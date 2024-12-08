"""Abstract exchange interface.

Exchange interface defines a unified way of implementing various exchanges and exposing common functionality.

All exchanges must implement this interface by subclassing `ExchangeInterface`.
"""

import abc
import time
from datetime import datetime
from typing import Iterator

from requests import Session

from trady.datatypes import Candlestick, Symbol
from trady.settings import ExchangeSettings


class ExchangeInterface(abc.ABC):
    """Abstract exchange interface.

    Public interface methods must be implemented by overriding their protected
    counterpart and utilizing `self._session` for making HTTP requests (API calls).

    Third-party API connectors/libraries _must not_ be used
    since they tend to restrict the available functionality.

    Attributes
    ----------
    self._settings
        Exchange-specific settings. Must be specified by implementing `_get_settings()`
    self._session
        A session object for making HTTP requests, see
        https://requests.readthedocs.io/en/latest/user/advanced/#session-objects

    Examples
    --------
    See any exchange in `trady.exchanges`.
    """

    @classmethod
    @abc.abstractmethod
    def _get_settings(cls) -> ExchangeSettings:
        """Return exchange-specific settings.

        Note that every exchange must define its own settings (see `trady.settings`).
        """
        pass

    def __init__(self) -> None:
        """Initialize interface."""
        self._settings: ExchangeSettings = self._get_settings()
        assert self._settings.api_key, f"{self.__class__.__name__} API key is missing"
        assert self._settings.api_secret, f"{self.__class__.__name__} API secret is missing"
        self._session: Session = Session()

    def get_datetime(self) -> datetime:
        """Retrieve datetime."""
        return self._get_datetime()

    def get_symbols(self) -> list[Symbol]:
        """Retrieve available symbols."""
        return self._get_symbols()

    def get_candlesticks(
        self,
        symbol: Symbol,
        interval: int,
        number: int | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Retrieve candlesticks (single API request).

        This method will return the latest candlesticks unless `start_datetime` or `end_datetime` is specified.

        Note that the maximum `number` of candlesticks is limited by a single API request.
        To retrieve all candlesticks for a given datetime period, use `get_candlesticks_iterator()`.

        Parameters
        ----------
        symbol
            A symbol to retrieve the candlesticks for.
        interval
            Candlesticks interval (in seconds).
        number
            Required number of candlesticks.
            The default and maximum value is `self._settings.candlesticks_max_number`.
            If there's not enough candlesticks the method will simply return all of them.
        start_datetime
            An open datetime to start with.
        end_datetime
            Maximum open datetime.
        """
        number = self._settings.candlesticks_max_number if number is None else number
        assert 1 <= number <= self._settings.candlesticks_max_number, f"invalid number {number}"
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
        """Retrieve candlesticks (chained API requests).

        This method allows to retrieve all candlesticks for a given datetime period by safely chaining
        the underlying `get_candlesticks()` calls. It becomes available when the latter is implemented.

        Parameters
        ----------
        symbol
            A symbol to retrieve the candlesticks for.
        interval
            Candlesticks interval (in seconds).
        start_datetime
            An open datetime to start with.
        end_datetime
            An open datetime to end with.

        Notes
        -----
        Safe chaining depends on the value of `self._settings.candlesticks_iterator_throttle`
        which is used for throttling API requests in order to avoid violating rate limits.
        """
        while True:
            candlesticks = self.get_candlesticks(
                symbol,
                interval,
                number=self._settings.candlesticks_max_number,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
            for candlestick in candlesticks:
                yield candlestick
            if (
                len(candlesticks) < self._settings.candlesticks_max_number
                or candlesticks[-1].close_datetime >= end_datetime
            ):
                return
            start_datetime = candlesticks[-1].close_datetime
            time.sleep(self._settings.candlesticks_iterator_throttle)

    @abc.abstractmethod
    def _get_datetime(self) -> datetime:
        """Override this to implement `get_datetime()`."""
        pass

    @abc.abstractmethod
    def _get_symbols(self) -> list[Symbol]:
        """Override this to implement `get_symbols()`."""
        pass

    @abc.abstractmethod
    def _get_candlesticks(
        self,
        symbol: Symbol,
        interval: int,
        number: int | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """Override this to implement `get_candlesticks()` and `get_candlesticks_iterator()`."""
        pass
