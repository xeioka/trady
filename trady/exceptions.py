"""Exchange exceptions."""

from typing import Optional

from pydantic import PositiveInt


class ExchangeException(Exception):
    """Base exchange exception.

    Attributes
    ----------
    message
        Exception message.
    status_code
        HTTP status code.
    response_data
        Response data.
    """

    def __init__(
        self,
        message: str,
        /,
        *,
        status_code: Optional[PositiveInt] = None,
        response_data: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.status_code: PositiveInt | None = status_code
        self.response_data: dict = response_data or {}
