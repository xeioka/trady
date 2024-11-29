"""This module contains the exchange interface.

Exchange interface is an abstract interface that defines a unified way
of implementing various exchanges and exposing common functionality.
"""

import abc
from datetime import datetime

from requests import Session

from .datatypes import Symbol


class ExchangeInterface(abc.ABC):
    """Exchange interface.

    Public interface methods must be implemented by overriding their protected
    counterpart and utilizing `self.session` for making HTTP requests (API calls).

    Third-party API connectors/libraries _must not_ be used
    since they tend to restrict the available functionality.

    Attributes
    ----------
    session
        A session object for making HTTP requests, see
        https://requests.readthedocs.io/en/latest/user/advanced/#session-objects

    Examples
    --------
    See the Binance implementation (`trady.binance`).
    """

    def __init__(self) -> None:
        self.session: Session = Session()

    def get_datetime(self) -> datetime:
        """Retrieves date and time."""
        return self._get_datetime()

    def get_symbols(self) -> list[Symbol]:
        """Retrieves available symbols."""
        return self._get_symbols()

    def _get_datetime(self) -> datetime:
        """Override this to implement `get_datetime()`."""
        raise NotImplementedError

    def _get_symbols(self) -> list[Symbol]:
        """Override this to implement `get_symbols()`."""
        raise NotImplementedError
