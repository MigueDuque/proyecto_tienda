from abc import ABC, abstractmethod

from app.domain.entities.inventory_movement import InventoryMovement


class InventoryRepository(ABC):
    @abstractmethod
    def add_movement(self, movement: InventoryMovement) -> InventoryMovement: ...

    @abstractmethod
    def list_by_product(self, product_id: int) -> list[InventoryMovement]: ...

    @abstractmethod
    def list_all(self, product_id: int | None = None) -> list[InventoryMovement]: ...
