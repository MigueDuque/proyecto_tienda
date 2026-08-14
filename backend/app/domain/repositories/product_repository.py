from abc import ABC, abstractmethod

from app.domain.entities.product import Product


class ProductRepository(ABC):
    @abstractmethod
    def add(self, product: Product) -> Product: ...

    @abstractmethod
    def update(self, product: Product) -> Product: ...

    @abstractmethod
    def delete(self, product_id: int) -> None: ...

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product | None: ...

    @abstractmethod
    def get_by_sku(self, sku: str) -> Product | None: ...

    @abstractmethod
    def list_low_stock(self) -> list[Product]: ...

    @abstractmethod
    def list(self, category_id: int | None = None, only_active: bool = False) -> list[Product]: ...
