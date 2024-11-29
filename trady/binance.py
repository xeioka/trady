"""This module contains the Binance implementation.

Resources
---------
API documentation:
  - https://binance-docs.github.io/apidocs/futures/en/#general-info
"""

from datetime import datetime
from typing import Any

from .datatypes import Rules, Symbol
from .interface import ExchangeInterface


class Binance(ExchangeInterface):
    """Binance implementation."""

    API_URL: str = "https://fapi.binance.com/fapi/v1/"

    def _get_datetime(self) -> datetime:
        """See `super()._get_datetime()`.

        API endpoint:
            - https://binance-docs.github.io/apidocs/futures/en/#check-server-time
        """
        response = self.session.get(self.API_URL + "time")
        timestamp = response.json()["serverTime"] / 1000
        return datetime.fromtimestamp(timestamp)

    def _get_symbols(self) -> list[Symbol]:
        """See `super()._get_symbols()`.

        API endpoint:
            - https://binance-docs.github.io/apidocs/futures/en/#exchange-information
        """
        response = self.session.get(self.API_URL + "exchangeInfo")
        symbols_data = response.json()["symbols"]
        return [
            self._parse_symbol(symbol_data)
            for symbol_data in symbols_data
            if symbol_data["status"] == "TRADING" and symbol_data["contractType"] == "PERPETUAL"
        ]

    def _parse_symbol(self, symbol_data: dict[str, Any]) -> Symbol:
        """Parses symbol data.

        Parameters
        ----------
        symbol_data
            Symbol data as returned by the API, see `symbols` here
            https://binance-docs.github.io/apidocs/futures/en/#exchange-information
        """
        rules_data = symbol_data["filters"]
        return Symbol(
            base_asset=symbol_data["baseAsset"],
            quote_asset=symbol_data["quoteAsset"],
            rules=self._parse_rules(rules_data),
        )

    def _parse_rules(self, rules_data: list[dict[str, Any]]) -> Rules:
        """Parses rules data.

        Parameters
        ----------
        rules_data
            Rules data as returned by the API, see `filters` here
            https://binance-docs.github.io/apidocs/futures/en/#exchange-information
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
