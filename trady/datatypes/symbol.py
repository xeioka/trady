"""Trading symbol."""

from pydantic import BaseModel

from .rules import Rules


class Symbol(BaseModel):
    base_asset: str
    quote_asset: str
    rules: Rules

    @property
    def name(self) -> str:
        return self.base_asset + self.quote_asset
