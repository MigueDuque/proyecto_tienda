from dataclasses import dataclass


@dataclass
class User:
    id: int | None
    email: str
    password_hash: str
    full_name: str
    is_active: bool = True
