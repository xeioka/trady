"""This module contains the Binance exchange implementation.

Resources
---------
API documentation:
  - https://developers.binance.com/docs/derivatives/usds-margined-futures/general-info
"""

from datetime import datetime
from typing import Any

from .datatypes import Rules, Symbol
from .interface import ExchangeInterface


class Binance(ExchangeInterface):
    """Binance exchange implementation."""

    API_URL: str = "https://fapi.binance.com/fapi/v1/"

    def get_datetime(self) -> datetime:
        """See `super().get_datetime()`."""
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Check-Server-Time
        response = self.session.get(self.API_URL + "time")
        timestamp = response.json()["serverTime"] / 1000
        return datetime.fromtimestamp(timestamp)

    def get_symbols(self) -> list[Symbol]:
        """See `super().get_symbols()`."""
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information
        response = self.session.get(self.API_URL + "exchangeInfo")
        symbols_data = response.json()["symbols"]
        return [
            self._translate_symbol(symbol_data)
            for symbol_data in symbols_data
            if symbol_data["status"] == "TRADING" and symbol_data["contractType"] == "PERPETUAL"
        ]

    def _translate_symbol(self, symbol_data: dict[str, Any]) -> Symbol:
        """Translates API data to a symbol.

        Parameters
        ----------
        symbol_data
            Symbol data returned by the API.
        """
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
        rules_data = symbol_data["filters"]
        return Symbol(
            base_asset=symbol_data["baseAsset"],
            quote_asset=symbol_data["quoteAsset"],
            rules=self._translate_rules(rules_data),
        )

    def _translate_rules(self, rules_data: list[dict[str, Any]]) -> Rules:
        """Translates API data to symbol rules.

        Parameters
        ----------
        rules_data
            Rules data returned by the API.
        """
        # https://developers.binance.com/docs/derivatives/usds-margined-futures/market-data/rest-api/Exchange-Information#response-example
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
