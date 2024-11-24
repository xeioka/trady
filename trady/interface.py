"""This module contains the abstract exchange interface.

All exchange implementations must subclass `ExchangeInterface` and implement required
methods by utilizing the underlying `session` for making HTTP requests (API calls).

Third-party API connectors/libraries _must not_ be used
since they tend to restrict the available functionality.
"""

import abc
from datetime import datetime

from requests import Session

from .datatypes import Symbol


class ExchangeInterface(abc.ABC):
    """Abstract exchange interface.

    Attributes
    ----------
    session
        Requests session. Must be used for _all_ HTTP requests.
    """

    def __init__(self) -> None:
        self.session: Session = Session()

    def get_datetime(self) -> datetime:
        """Retrieves date and time."""
        raise NotImplementedError

    def get_symbols(self) -> list[Symbol]:
        """Retrieves available symbols."""
        raise NotImplementedError
