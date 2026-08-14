from abc import ABC, abstractmethod

from app.domain.entities.purchase import Purchase


class PurchaseRepository(ABC):
    @abstractmethod
    def add(self, purchase: Purchase) -> Purchase: ...

    @abstractmethod
    def get_by_id(self, purchase_id: int) -> Purchase | None: ...

    @abstractmethod
    def list_all(self) -> list[Purchase]: ...
