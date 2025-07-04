"""Abstract exchange interface."""

import time
from datetime import datetime
from decimal import Decimal
from typing import Iterator, Literal, Optional

from pydantic import PositiveInt
from requests import Session, status_codes
from requests.exceptions import JSONDecodeError

from .datatypes import (
    AccountPositions,
    Balance,
    Candlestick,
    MarketRules,
    MarketStats,
    Position,
    Symbol,
)
from .exceptions import ExchangeException
from .settings import ExchangeSettings


class ExchangeInterface:
    """Abstract exchange interface.

    Public interface methods should be implemented by overriding their protected
    counterpart and utilizing `_dispatch_api_request()` for making API requests.

    Examples
    --------
    See `trady.exchanges.binance.interface`.
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
        symbol_name: str,
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
        symbol_name
            Candlesticks symbol.
        interval
            Candlesticks interval.
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
            symbol_name,
            interval,
            number=number,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )

    def get_candlesticks_iterator(
        self,
        symbol_name: str,
        interval: PositiveInt,
        start_datetime: datetime,
        end_datetime: datetime,
        /,
    ) -> Iterator[Candlestick]:
        """Retrieve all candlesticks for a given datetime period.

        This method chains the underlying `get_candlesticks()` calls.

        Parameters
        ----------
        symbol_name
            Candlesticks symbol.
        interval
            Candlesticks interval.
        start_datetime
            A datetime to start with.
        end_datetime
            A datetime to end with.
        """
        while True:
            candlesticks = self.get_candlesticks(
                symbol_name,
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

    def get_market_stats_24h(self) -> MarketStats:
        """Retrieve market stats (24h)."""
        return self._get_market_stats_24h()

    def get_market_rules(self) -> MarketRules:
        """Retrieve market rules."""
        return self._get_market_rules()

    def get_balance(self, asset: str, /) -> Balance:
        """Retrieve asset balance.

        Parameters
        ----------
        asset
            Asset name.
        """
        return self._get_balance(asset)

    def get_account_positions(self) -> AccountPositions:
        """Retrieve account positions."""
        return self._get_account_positions()

    def open_position(
        self,
        symbol_name: str,
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
        symbol_name
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
            symbol_name,
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
            url += "?" + query_str.lstrip("?")
        match method:
            case "GET":
                response = self._session.get(url, params=query_dict)
            case "POST":
                response = self._session.post(url, params=query_dict, data=payload)
        if response.status_code != status_codes.codes.OK:
            try:
                response_data = response.json()
            except JSONDecodeError:
                response_data = None
            raise ExchangeException(
                f"API request returned {response.status_code}",
                status_code=response.status_code,
                response_data=response_data,
            )
        return response.json()  # type: ignore[no-any-return]

    def _get_datetime(self) -> datetime:
        raise NotImplementedError

    def _get_symbols(self) -> list[Symbol]:
        raise NotImplementedError

    def _get_candlesticks(
        self,
        symbol_name: str,
        interval: PositiveInt,
        /,
        *,
        number: Optional[PositiveInt] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> list[Candlestick]:
        raise NotImplementedError

    def _get_market_stats_24h(self) -> MarketStats:
        raise NotImplementedError

    def _get_market_rules(self) -> MarketRules:
        raise NotImplementedError

    def _get_balance(self, asset: str, /) -> Balance:
        raise NotImplementedError

    def _get_account_positions(self) -> AccountPositions:
        raise NotImplementedError

    def _open_position(
        self,
        symbol_name: str,
        size: Decimal,
        /,
        *,
        leverage: PositiveInt = 1,
        take_profit: Optional[Decimal] = None,
        stop_loss: Optional[Decimal] = None,
    ) -> Position:
        raise NotImplementedError

    def _close_position(self, position: Position, /) -> None:
        raise NotImplementedError

    def _close_positions(self, positions: list[Position], /) -> None:
        raise NotImplementedError

    def _close_all_positions(self) -> None:
        raise NotImplementedError
