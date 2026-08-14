from dataclasses import dataclass

from app.domain.enums import AccountType


@dataclass
class Account:
    id: int | None
    code: str
    name: str
    type: AccountType
    parent_id: int | None = None
    is_active: bool = True
