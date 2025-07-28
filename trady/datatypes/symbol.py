from pydantic import BaseModel


class Symbol(BaseModel):
    base_asset: str
    quote_asset: str

    @property
    def name(self) -> str:
        return self.base_asset + self.quote_asset

    def __eq__(self, other: object) -> bool:
        match other:
            case Symbol():
                return self.name == other.name
            case _:
                return self.name == other

    def __hash__(self) -> int:
        return hash(self.name)
