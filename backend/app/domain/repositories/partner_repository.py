from abc import ABC, abstractmethod

from app.domain.entities.partner import Partner
from app.domain.enums import PartnerType


class PartnerRepository(ABC):
    @abstractmethod
    def add(self, partner: Partner) -> Partner: ...

    @abstractmethod
    def update(self, partner: Partner) -> Partner: ...

    @abstractmethod
    def delete(self, partner_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, partner_id: int) -> Partner | None: ...

    @abstractmethod
    def list(self, type: PartnerType | None = None) -> list[Partner]: ...
