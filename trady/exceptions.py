"""Exchange exceptions."""

from typing import Optional


class ExchangeException(Exception):
    def __init__(
        self,
        message: str,
        /,
        *,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
    ) -> None:
        super().__init__(message)
        self.message: str = message
        self.status_code: Optional[int] = status_code
        self.response_data: dict = response_data or {}
