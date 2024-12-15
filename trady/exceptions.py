"""Exchange interface exceptions."""

from typing import Any


class ExchangeInterfaceException(Exception):
    """Exchange interface exception.

    Attributes
    ----------
    message
        Exception message.
    """

    def __init__(self, message: str, /) -> None:
        """Initialize exception."""
        super().__init__(message)
        self.message: str = message

    def __str__(self) -> str:
        """Return string representation."""
        return self.message


class InterfaceException(ExchangeInterfaceException):
    """Interface-related exception."""


class ExchangeException(ExchangeInterfaceException):
    """Exchange-related exception."""


class ExchangeAPIError(ExchangeException):
    """Exchange API error.

    Attributes
    ----------
    details
        Details returned by the API.
    """

    def __init__(self, *args: Any, details: dict[str, Any] | None = None, **kwargs: Any) -> None:
        """Initialize exception."""
        super().__init__(*args, **kwargs)
        self.details: dict[str, Any] = details if details is not None else {}

    def __str__(self) -> str:
        """Return string representation."""
        return self.message.rstrip(".") + f" ({self.details})."
