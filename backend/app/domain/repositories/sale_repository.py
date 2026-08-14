from abc import ABC, abstractmethod

from app.domain.entities.sale import Sale


class SaleRepository(ABC):
    @abstractmethod
    def add(self, sale: Sale) -> Sale: ...

    @abstractmethod
    def get_by_id(self, sale_id: int) -> Sale | None: ...

    @abstractmethod
    def list_all(self) -> list[Sale]: ...
