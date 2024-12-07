"""Binance implementation.

Resources
---------
API documentation:
  - https://binance-docs.github.io/apidocs/futures/en/#general-info
"""

import hmac
from datetime import datetime
from decimal import Decimal
from typing import Any
from urllib.parse import urlencode

from trady.datatypes import Candlestick, Rules, Symbol
from trady.interface import ExchangeInterface

from .settings import BinanceSettings


class Binance(ExchangeInterface):
    """Binance implementation.

    Attributes
    ----------
    cls.INTERVAL_MAP
        A mapping between intervals in seconds and the corresponding API values.
    """

    INTERVAL_MAP: dict[int, str] = {
        60: "1m",
        60 * 3: "3m",
        60 * 5: "5m",
        60 * 15: "15m",
        60 * 30: "30m",
        60 * 60: "1h",
        60 * 60 * 2: "2h",
        60 * 60 * 4: "4h",
        60 * 60 * 6: "6h",
        60 * 60 * 8: "8h",
        60 * 60 * 12: "12h",
        60 * 60 * 24: "1d",
    }

    @classmethod
    def _get_settings(cls) -> BinanceSettings:
        """See `ExchangeInterface._get_settings()`."""
        return BinanceSettings()

    def __init__(self) -> None:
        """Initialize interface."""
        super().__init__()
        # https://binance-docs.github.io/apidocs/futures/en/#endpoint-security-type
        self._session.headers.update({"X-MBX-APIKEY": self._settings.api_key})

    def _sign_payload(self, payload: dict[str, str | int]) -> dict[str, str | int]:
        """Sign request payload.

        For more information on signing payloads, see
        https://binance-docs.github.io/apidocs/futures/en/#endpoint-security-type.

        Parameters
        ----------
        payload
            A payload to sign.
        """
        payload["timestamp"] = int(datetime.now().timestamp() * 1000)
        payload["signature"] = hmac.new(
            self._settings.api_secret.encode(),
            msg=urlencode(payload).encode(),
            digestmod="SHA256",
        ).hexdigest()
        return payload

    def _get_datetime(self) -> datetime:
        """See `ExchangeInterface._get_datetime()`.

        API endpoint:
            - https://binance-docs.github.io/apidocs/futures/en/#check-server-time
        """
        response = self._session.get(str(self._settings.api_url) + "v1/time")
        timestamp = response.json()["serverTime"] / 1000
        return datetime.fromtimestamp(timestamp)

    def _get_symbols(self) -> list[Symbol]:
        """See `ExchangeInterface._get_symbols()`.

        API endpoint:
            - https://binance-docs.github.io/apidocs/futures/en/#exchange-information
        """
        response = self._session.get(str(self._settings.api_url) + "v1/exchangeInfo")
        symbols_data = response.json()["symbols"]
        return [
            self._parse_symbol(symbol_data)
            for symbol_data in symbols_data
            if symbol_data["status"] == "TRADING" and symbol_data["contractType"] == "PERPETUAL"
        ]

    def _get_candlesticks(
        self,
        symbol: Symbol,
        interval: int,
        number: int | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> list[Candlestick]:
        """See `ExchangeInterface._get_candlesticks()`.

        API endpoint:
            - https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data
        """
        if interval not in self.INTERVAL_MAP:
            raise NotImplementedError(f"unsupported interval ({interval})")
        payload = {
            "symbol": symbol.name,
            "interval": self.INTERVAL_MAP[interval],
            "limit": str(number),
            "startTime": int(start_datetime.timestamp() * 1000) if start_datetime else None,
            "endTime": int(end_datetime.timestamp() * 1000) if end_datetime else None,
        }
        response = self._session.get(str(self._settings.api_url) + "v1/klines", params=payload)
        candlesticks_data = response.json()
        return [self._parse_candlestick(candlestick_data) for candlestick_data in candlesticks_data]

    def _parse_symbol(self, symbol_data: dict[str, Any]) -> Symbol:
        """Parse symbol data.

        Parameters
        ----------
        symbol_data
            Symbol data as returned by the API, see `symbols` in
            https://binance-docs.github.io/apidocs/futures/en/#exchange-information.
        """
        rules_data = symbol_data["filters"]
        return Symbol(
            base_asset=symbol_data["baseAsset"],
            quote_asset=symbol_data["quoteAsset"],
            rules=self._parse_rules(rules_data),
        )

    def _parse_rules(self, rules_data: list[dict[str, Any]]) -> Rules:
        """Parse rules data.

        Parameters
        ----------
        rules_data
            Rules data as returned by the API, see `filters` in
            https://binance-docs.github.io/apidocs/futures/en/#exchange-information.
        """
        rules_kwargs = {}
        for rule_data in rules_data:
            if rule_data["filterType"] == "MIN_NOTIONAL":
                rules_kwargs["min_notional"] = rule_data["notional"]
            elif rule_data["filterType"] == "LOT_SIZE":
                rules_kwargs["min_size"] = rule_data["minQty"]
                rules_kwargs["max_size"] = rule_data["maxQty"]
                rules_kwargs["size_step"] = rule_data["stepSize"]
            elif rule_data["filterType"] == "PRICE_FILTER":
                rules_kwargs["min_price"] = rule_data["minPrice"]
                rules_kwargs["max_price"] = rule_data["maxPrice"]
                rules_kwargs["price_step"] = rule_data["tickSize"]
        return Rules(**rules_kwargs)

    def _parse_candlestick(self, candlestick_data: list[Any]) -> Candlestick:
        """Parse candlestick data.

        Parameters
        ----------
        candlestick_data
            Candlestick data as returned by the API, see
            https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data.
        """
        total_volume = Decimal(candlestick_data[7])
        buy_volume = Decimal(candlestick_data[10])
        sell_volume = total_volume - buy_volume
        return Candlestick(
            open_datetime=datetime.fromtimestamp(candlestick_data[0] / 1000),
            close_datetime=datetime.fromtimestamp(candlestick_data[6] / 1000),
            open_price=candlestick_data[1],
            low_price=candlestick_data[3],
            high_price=candlestick_data[2],
            close_price=candlestick_data[4],
            sell_volume=sell_volume,
            buy_volume=buy_volume,
        )
