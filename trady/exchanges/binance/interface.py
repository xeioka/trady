"""Binance interface.

Resources
---------
API documentation:
    - https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
"""

import hmac
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional
from urllib.parse import urlencode

from pydantic import PositiveInt

from trady.datatypes import Balance, Candlestick, Position, Rules, Symbol
from trady.exception import ExchangeException
from trady.interface import ExchangeInterface

from .settings import BinanceSettings


class Binance(ExchangeInterface):
    # A mapping between intervals (in seconds) and the corresponding API values.
    _INTERVAL_MAP: dict[int, str] = {
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
        self._session.headers.update({"X-MBX-APIKEY": self._settings.api_key})  # type: ignore[attr-defined]

    def _sign_request_data(self, data: dict, /) -> dict:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info#signed-trade-and-user_data-endpoint-security
        data["timestamp"] = int(datetime.now().timestamp() * 1000)
        data["signature"] = hmac.new(
            self._settings.api_secret.encode(),  # type: ignore[attr-defined]
            msg=urlencode(data).encode(),
            digestmod="SHA256",
        ).hexdigest()
        return data

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
        if interval not in self._INTERVAL_MAP:
            raise ValueError(f"unknown interval {interval}")
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data
        response_data = self._dispatch_api_request(
            "GET",
            "v1/klines",
            query_dict={
                "symbol": symbol.name,
                "interval": self._INTERVAL_MAP[interval],
                "limit": number,
                "startTime": int(start_datetime.timestamp() * 1000) if start_datetime else None,
                "endTime": int(end_datetime.timestamp() * 1000) if end_datetime else None,
            },
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        return [self._parse_candlestick(candlestick_data) for candlestick_data in response_data]

    def _get_rules_map(self) -> dict[str, Rules]:
        # A mapping between symbol names and rules data.
        rules_data_map: dict[str, dict] = defaultdict(dict)
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        response_data = self._dispatch_api_request("GET", "v1/exchangeInfo")
        assert type(response_data) is dict, f"type {type(response_data)} was not expected"
        for symbol_data in response_data["symbols"]:
            symbol_name = symbol_data["symbol"]
            rules_data_map[symbol_name] = {"filters": symbol_data["filters"]}
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Notional-and-Leverage-Brackets
        response_data = self._dispatch_api_request(
            "GET",
            "v1/leverageBracket",
            query_dict=self._sign_request_data({}),
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        for symbol_data in response_data:
            symbol_name = symbol_data["symbol"]
            if symbol_name not in rules_data_map:
                continue
            for bracket_data in symbol_data["brackets"]:
                if Decimal(bracket_data["notionalFloor"]) == Decimal("0"):
                    rules_data_map[symbol_name]["bracket"] = bracket_data
                    break
        return {
            symbol_name: self._parse_rules(rules_data)
            for symbol_name, rules_data in rules_data_map.items()
        }

    def _get_balance(self, asset: str, /) -> Balance:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3
        response_data = self._dispatch_api_request(
            "GET",
            "v3/balance",
            query_dict=self._sign_request_data({}),
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        for balance_data in response_data:
            if balance_data["asset"] == asset:
                return self._parse_balance(balance_data)
        raise ValueError(f"unknown asset {asset}")

    def _get_positions_map(self) -> dict[str, Position]:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Position-Information-V2
        response_data = self._dispatch_api_request(
            "GET",
            "v2/positionRisk",
            query_dict=self._sign_request_data({}),
        )
        assert type(response_data) is list, f"type {type(response_data)} was not expected"
        return {
            position_data["symbol"]: self._parse_position(position_data)
            for position_data in response_data
            if Decimal(position_data["positionAmt"]) != Decimal("0")
        }

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
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api
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
            payload=self._sign_request_data(
                {
                    **base_order,
                    "side": open_side,
                    "quantity": str(abs(size)),
                    "type": "MARKET",
                },
            ),
        )
        if take_profit is not None:
            self._dispatch_api_request(
                "POST",
                "v1/order",
                payload=self._sign_request_data(
                    {
                        **base_order,
                        "side": close_side,
                        "stopPrice": str(take_profit),
                        "type": "TAKE_PROFIT_MARKET",
                        "closePosition": "TRUE",
                        "workingType": "CONTRACT_PRICE",
                        "priceProtect": "FALSE",
                        "timeInForce": "GTE_GTC",
                    },
                ),
            )
        if stop_loss is not None:
            self._dispatch_api_request(
                "POST",
                "v1/order",
                payload=self._sign_request_data(
                    {
                        **base_order,
                        "side": close_side,
                        "stopPrice": str(stop_loss),
                        "type": "STOP_MARKET",
                        "closePosition": "TRUE",
                        "workingType": "CONTRACT_PRICE",
                        "priceProtect": "FALSE",
                        "timeInForce": "GTE_GTC",
                    },
                ),
            )
        return Position(
            symbol_name=symbol.name,
            size=size,
            leverage=leverage,
            unrealized_pnl=Decimal("0"),
        )

    def _close_position(self, position: Position, /) -> None:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api
        self._dispatch_api_request(
            "POST",
            "v1/order",
            payload=self._sign_request_data(
                {
                    "symbol": position.symbol_name,
                    "side": "SELL" if position.is_long else "BUY",
                    "quantity": str(abs(position.size)),
                    "type": "MARKET",
                    "reduceOnly": "TRUE",
                    "positionSide": "BOTH",
                    "newOrderRespType": "RESULT",
                    "recvWindow": 1000,
                },
            ),
        )

    def _close_positions(self, positions: list[Position], /) -> None:
        for position in positions:
            self._close_position(position)

    def _close_all_positions(self) -> None:
        positions_map = self.get_positions_map()
        positions = list(positions_map.values())
        self._close_positions(positions)

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
                payload=self._sign_request_data(
                    {
                        "symbol": symbol.name,
                        "marginType": margin_type,
                    },
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
            payload=self._sign_request_data(
                {
                    "symbol": symbol.name,
                    "leverage": leverage,
                },
            ),
        )

    def _parse_symbol(self, symbol_data: dict, /) -> Symbol:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
        return Symbol(
            base_asset=symbol_data["baseAsset"],
            quote_asset=symbol_data["quoteAsset"],
        )

    def _parse_candlestick(self, candlestick_data: list, /) -> Candlestick:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Kline-Candlestick-Data#response-example
        volume = Decimal(candlestick_data[7])
        buy_volume = Decimal(candlestick_data[10])
        sell_volume = volume - buy_volume
        return Candlestick(
            open_datetime=datetime.fromtimestamp(candlestick_data[0] / 1000),
            close_datetime=datetime.fromtimestamp(candlestick_data[6] / 1000),
            open=candlestick_data[1],
            high=candlestick_data[2],
            low=candlestick_data[3],
            close=candlestick_data[4],
            buy_volume=buy_volume,
            sell_volume=sell_volume,
        )

    def _parse_rules(self, rules_data: dict, /) -> Rules:
        rules_kwargs = {}
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/common-definition#symbol-filters
        for filter_data in rules_data["filters"]:
            match filter_data["filterType"]:
                case "LOT_SIZE":
                    rules_kwargs["size_min_value"] = filter_data["minQty"]
                    rules_kwargs["size_max_value"] = filter_data["maxQty"]
                    rules_kwargs["size_step"] = filter_data["stepSize"]
                case "MIN_NOTIONAL":
                    rules_kwargs["notional_min_value"] = filter_data["notional"]
                case "PRICE_FILTER":
                    rules_kwargs["price_min_value"] = filter_data["minPrice"]
                    rules_kwargs["price_max_value"] = filter_data["maxPrice"]
                    rules_kwargs["price_step"] = filter_data["tickSize"]
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Notional-and-Leverage-Brackets#response-example
        rules_kwargs["notional_max_value"] = rules_data["bracket"]["notionalCap"]
        rules_kwargs["leverage_max_value"] = rules_data["bracket"]["initialLeverage"]
        return Rules(**rules_kwargs)

    def _parse_balance(self, balance_data: dict, /) -> Balance:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/account/rest-api/Futures-Account-Balance-V3#response-example
        return Balance(
            realized=balance_data["crossWalletBalance"],
            unrealized=balance_data["crossUnPnl"],
        )

    def _parse_position(self, position_data: dict, /) -> Position:
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/trade/rest-api/Position-Information-V2#response-example
        return Position(
            symbol_name=position_data["symbol"],
            size=position_data["positionAmt"],
            leverage=position_data["leverage"],
            unrealized_pnl=position_data["unRealizedProfit"],
        )
