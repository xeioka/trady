"""Abstract exchange interface."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Iterator, Literal, Optional

from pydantic import PositiveInt
from requests import Session, status_codes

from .datatypes import Balance, Candlestick, Position, Rules, Symbol
from .exceptions import ExchangeException
from .settings import ExchangeSettings


class ExchangeInterface:
    """Abstract exchange interface.

    Public interface methods should be implemented by overriding their protected
    counterpart and utilizing `_dispatch_api_request()` for making API requests.

    Examples
    --------
    See `trady.exchanges.binance`.
    """

    @classmethod
    def _get_settings(cls) -> ExchangeSettings:
        """Override this to implement exchange-specific settings."""
        raise NotImplementedError

    def __init__(self) -> None:
        self._settings: ExchangeSettings = self._get_settings()
        self._session: Session = Session()

    def get_datetime(self) -> datetime:
        """Retrieve current datetime."""
        return self._get_datetime()

    def get_symbols(self) -> list[Symbol]:
        """Retrieve active symbols."""
        return self._get_symbols()

    def get_candlesticks(
        self,
        symbol: Symbol,
        interval: PositiveInt,
        /,
        *,
        number: Optional[PositiveInt] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> list[Candlestick]:
        """Retrieve candlesticks.

        This method returns the latest candlesticks unless `start_datetime` or `end_datetime` is specified.

        Parameters
        ----------
        symbol
            Candlesticks symbol.
        interval
            Candlesticks interval (in seconds).
        number
            Required number of candlesticks. The default and the maximum value is `_settings.candlesticks_max_number`.
        start_datetime
            A datetime to start with.
        end_datetime
            A datetime to end with.
        """
        if number is None:
            number = self._settings.candlesticks_max_number
        elif number > self._settings.candlesticks_max_number:
            raise ValueError(f"number must be <= {self._settings.candlesticks_max_number}")
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
        interval: PositiveInt,
        start_datetime: datetime,
        end_datetime: datetime,
        /,
    ) -> Iterator[Candlestick]:
        """Retrieve all candlesticks for a given datetime period.

        This method chains the underlying `get_candlesticks()` calls.

        Parameters
        ----------
        symbol
            Candlesticks symbol.
        interval
            Candlesticks interval (in seconds).
        start_datetime
            A datetime to start with.
        end_datetime
            A datetime to end with.
        """
        while True:
            candlesticks = self.get_candlesticks(
                symbol,
                interval,
                number=self._settings.candlesticks_max_number,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
            )
            yield from candlesticks
            if (
                len(candlesticks) < self._settings.candlesticks_max_number
                or candlesticks[-1].close_datetime >= end_datetime
            ):
                return
            start_datetime = candlesticks[-1].close_datetime
            time.sleep(self._settings.candlesticks_iterator_throttle)

    def get_rules(self) -> dict[str, Rules]:
        """Retrieve trading rules.

        Returns
        -------
        A mapping between symbol names and rules.
        """
        return self._get_rules()

    def get_balance(self, asset: str, /) -> Balance:
        """Retrieve asset balance.

        Parameters
        ----------
        asset
            Asset name.
        """
        return self._get_balance(asset)

    def get_positions(self) -> dict[str, Position]:
        """Retrieve open positions.

        Returns
        -------
        A mapping between symbol names and positions.
        """
        return self._get_positions()

    def open_position(
        self,
        symbol: Symbol,
        size: Decimal,
        /,
        *,
        leverage: PositiveInt = 1,
        take_profit: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
    ) -> Position:
        """Open position.

        Parameters
        ----------
        symbol
            Position symbol.
        size
            Position size (positive values for long, negative for short).
        leverage
            A leverage to use.
        take_profit
            Take profit price.
        stop_loss
            Stop loss price.
        """
        return self._open_position(
            symbol,
            size,
            leverage=leverage,
            take_profit=take_profit,
            stop_loss=stop_loss,
        )

    def close_position(self, position: Position, /) -> None:
        """Close position.

        Parameters
        ----------
        position
            A position to close.
        """
        self._close_position(position)

    def close_positions(self, positions: list[Position], /) -> None:
        """Close positions.

        Parameters
        ----------
        positions
            Positions to close.
        """
        self._close_positions(positions)

    def close_all_positions(self) -> None:
        """Close all positions."""
        self._close_all_positions()

    def _dispatch_api_request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        /,
        *,
        query_str: Optional[str] = None,
        query_dict: Optional[dict] = None,
        payload: Optional[dict] = None,
    ) -> dict | list:
        url = str(self._settings.api_url) + path
        if query_str:
            url = url + "?" + query_str.lstrip("?")
        match method:
            case "GET":
                response = self._session.get(url, params=query_dict)
            case "POST":
                response = self._session.post(url, params=query_dict, data=payload)
        if response.status_code != status_codes.codes.OK:
            raise ExchangeException(
                f"API request returned {response.status_code}",
                status_code=response.status_code,
                response_data=response.json(),
            )
        return response.json()  # type: ignore[no-any-return]

    def _get_datetime(self) -> datetime:
        """Override this to implement `get_datetime()`."""
        raise NotImplementedError

    def _get_symbols(self) -> list[Symbol]:
        """Override this to implement `get_symbols()`."""
        raise NotImplementedError

    def _get_candlesticks(
        self,
        symbol: Symbol,
        interval: PositiveInt,
        /,
        *,
        number: Optional[PositiveInt] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> list[Candlestick]:
        """Override this to implement `get_candlesticks()` and `get_candlesticks_iterator()`."""
        raise NotImplementedError

    def _get_rules(self) -> dict[str, Rules]:
        """Override this to implement `get_rules()`."""
        raise NotImplementedError

    def _get_balance(self, asset: str, /) -> Balance:
        """Override this to implement `get_balance()`."""
        raise NotImplementedError

    def _get_positions(self) -> dict[str, Position]:
        """Override this to implement `get_positions()`."""
        raise NotImplementedError

    def _open_position(
        self,
        symbol: Symbol,
        size: Decimal,
        /,
        *,
        leverage: PositiveInt = 1,
        take_profit: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
    ) -> Position:
        """Override this to implement `open_position()`."""
        raise NotImplementedError

    def _close_position(self, position: Position, /) -> None:
        """Override this to implement `close_position()`."""
        raise NotImplementedError

    def _close_positions(self, positions: list[Position], /) -> None:
        """Override this to implement `close_positions()`."""
        raise NotImplementedError

    def _close_all_positions(self) -> None:
        """Override this to implement `close_all_positions()`."""
        raise NotImplementedError
