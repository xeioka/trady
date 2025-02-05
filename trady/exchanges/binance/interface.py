"""Binance interface.

Resources
---------
API documentation:
    - https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
"""

import hmac
from datetime import datetime
from decimal import Decimal
from typing import Any, Literal, Optional
from urllib.parse import urlencode

from pydantic import PositiveInt

from trady.datatypes import Balance, Candlestick, Position, Rules, Symbol
from trady.exceptions import ExchangeException
from trady.interface import ExchangeInterface

from .settings import BinanceSettings


class Binance(ExchangeInterface):
    """Binance interface.

    Attributes
    ----------
    INTERVAL_MAP
        A mapping between intervals (in seconds) and the corresponding API values.
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
        return BinanceSettings()

    def __init__(self) -> None:
        super().__init__()
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#endpoint-security-type
        self._session.headers.update({"X-MBX-APIKEY": self._settings.api_key})  # type: ignore

    def _sign_payload(self, payload: dict[str, Any], /) -> dict[str, Any]:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
        payload["timestamp"] = int(datetime.now().timestamp() * 1000)
        payload["signature"] = hmac.new(
            self._settings.api_secret.encode(),  # type: ignore
            msg=urlencode(payload).encode(),
            digestmod="SHA256",
        ).hexdigest()
        return payload

    def _get_datetime(self) -> datetime:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Check-Server-Time
        response_data = self._dispatch_api_request("GET", "v1/time")
        assert type(response_data) is dict, f"type {type(response_data)} was not expected"
        return datetime.fromtimestamp(response_data["serverTime"] / 1000)

    def _get_symbols(self) -> list[Symbol]:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        response_data = self._dispatch_api_request("GET", "v1/exchangeInfo")
        assert type(response_data) is dict, f"type {type(response_data)} was not expected"
        return [
            self._parse_symbol(symbol_data)
            for symbol_data in response_data["symbols"]
            if symbol_data["status"] == "TRADING" and symbol_data["contractType"] == "PERPETUAL"
        ]

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
        if interval not in self.INTERVAL_MAP:
            raise ValueError(f"unknown interval {interval}")
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
        response_data = self._dispatch_api_request(
            "GET",
            "v1/klines",
            params={
                "symbol": symbol.name,
                "interval": self.INTERVAL_MAP[interval],
                "limit": number,
                "startTime": int(start_datetime.timestamp() * 1000) if start_datetime else None,
                "endTime": int(end_datetime.timestamp() * 1000) if end_datetime else None,
            },
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        return [
            self._parse_candlestick(symbol, candlestick_data) for candlestick_data in response_data
        ]

    def _get_balance(self, asset: str, /) -> Balance:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3
        response_data = self._dispatch_api_request(
            "GET",
            "v3/balance",
            params=self._sign_payload({}),
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        for balance_data in response_data:
            if balance_data["asset"] == asset:
                return self._parse_balance(asset, balance_data)
        raise ValueError(f"unknown asset {asset}")

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
        self._set_margin_type(symbol, "CROSSED")
        self._set_leverage(symbol, leverage)
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Place-Multiple-Orders
        open_side, close_side = ("BUY", "SELL") if size > Decimal("0") else ("SELL", "BUY")
        base_order = {
            "symbol": symbol.name,
            "positionSide": "BOTH",
            "newOrderRespType": "RESULT",
            "recvWindow": 1000,
        }
        self._dispatch_api_request(
            "POST",
            "v1/order",
            data=self._sign_payload(
                {
                    **base_order,
                    "side": open_side,
                    "quantity": str(abs(size)),
                    "type": "MARKET",
                }
            ),
        )
        if take_profit is not None:
            self._dispatch_api_request(
                "POST",
                "v1/order",
                data=self._sign_payload(
                    {
                        **base_order,
                        "side": close_side,
                        "stopPrice": str(take_profit),
                        "type": "TAKE_PROFIT_MARKET",
                        "closePosition": "TRUE",
                        "workingType": "CONTRACT_PRICE",
                        "priceProtect": "FALSE",
                        "timeInForce": "GTE_GTC",
                    }
                ),
            )
        if stop_loss is not None:
            self._dispatch_api_request(
                "POST",
                "v1/order",
                data=self._sign_payload(
                    {
                        **base_order,
                        "side": close_side,
                        "stopPrice": str(stop_loss),
                        "type": "STOP_MARKET",
                        "closePosition": "TRUE",
                        "workingType": "CONTRACT_PRICE",
                        "priceProtect": "FALSE",
                        "timeInForce": "GTE_GTC",
                    }
                ),
            )
        return Position(symbol=symbol, size=size, leverage=leverage, pnl=Decimal("0"))

    def _set_margin_type(
        self,
        symbol: Symbol,
        margin_type: Literal["CROSSED", "ISOLATED"],
        /,
    ) -> None:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Margin-Type
        try:
            self._dispatch_api_request(
                "POST",
                "v1/marginType",
                data=self._sign_payload(
                    {
                        "symbol": symbol.name,
                        "marginType": margin_type,
                    }
                ),
            )
        except ExchangeException as exception:
            # -4046 is returned when the same margin type is already set.
            if exception.response_data.get("code", None) != -4046:
                raise

    def _set_leverage(self, symbol: Symbol, leverage: PositiveInt, /) -> None:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Change-Initial-Leverage
        self._dispatch_api_request(
            "POST",
            "v1/leverage",
            data=self._sign_payload(
                {
                    "symbol": symbol.name,
                    "leverage": leverage,
                }
            ),
        )

    def _parse_symbol(self, symbol_data: dict[str, Any], /) -> Symbol:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
        rules = self._parse_rules(symbol_data["filters"])
        return Symbol(
            base_asset=symbol_data["baseAsset"],
            quote_asset=symbol_data["quoteAsset"],
            rules=rules,
        )

    def _parse_rules(self, rules_data: list[dict[str, Any]], /) -> Rules:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/common-definition#symbol-filters
        kwargs = {}
        for rule_data in rules_data:
            match rule_data["filterType"]:
                case "LOT_SIZE":
                    kwargs["size_min_value"] = rule_data["minQty"]
                    kwargs["size_max_value"] = rule_data["maxQty"]
                    kwargs["size_step"] = rule_data["stepSize"]
                case "MIN_NOTIONAL":
                    kwargs["size_min_notional"] = rule_data["notional"]
                case "PRICE_FILTER":
                    kwargs["price_min_value"] = rule_data["minPrice"]
                    kwargs["price_max_value"] = rule_data["maxPrice"]
                    kwargs["price_step"] = rule_data["tickSize"]
        return Rules(**kwargs)

    def _parse_candlestick(self, symbol: Symbol, candlestick_data: list[Any], /) -> Candlestick:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data#response-example
        volume = Decimal(candlestick_data[7])
        buy_volume = Decimal(candlestick_data[10])
        sell_volume = volume - buy_volume
        return Candlestick(
            symbol=symbol,
            open_datetime=datetime.fromtimestamp(candlestick_data[0] / 1000),
            close_datetime=datetime.fromtimestamp(candlestick_data[6] / 1000),
            open=candlestick_data[1],
            high=candlestick_data[2],
            low=candlestick_data[3],
            close=candlestick_data[4],
            buy_volume=buy_volume,
            sell_volume=sell_volume,
        )

    def _parse_balance(self, asset: str, balance_data: dict[str, Any], /) -> Balance:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3#response-example
        return Balance(
            asset=asset,
            realized=balance_data["crossWalletBalance"],
            unrealized=balance_data["crossUnPnl"],
        )
