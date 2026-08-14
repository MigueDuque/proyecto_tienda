from dataclasses import dataclass

from app.domain.enums import PartnerType


@dataclass
class Partner:
    id: int | None
    type: PartnerType
    name: str
    document_id: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool = True
