from dataclasses import dataclass


@dataclass
class Category:
    id: int | None
    name: str
    description: str | None = None
