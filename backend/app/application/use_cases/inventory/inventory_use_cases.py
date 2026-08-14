from dataclasses import dataclass
from decimal import Decimal

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.inventory_movement import InventoryMovement
from app.domain.enums import MovementReferenceType, MovementType
from app.domain.exceptions import InsufficientStockError, InvalidOperationError, NotFoundError


@dataclass
class AdjustStockInput:
    product_id: int
    quantity_delta: Decimal
    notes: str | None = None


class AdjustStockUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, data: AdjustStockInput) -> InventoryMovement:
        if data.quantity_delta == 0:
            raise InvalidOperationError("El ajuste debe tener una cantidad distinta de cero")

        with self._uow as uow:
            product = uow.products.get_by_id(data.product_id)
            if product is None:
                raise NotFoundError("Producto", data.product_id)

            new_stock = product.current_stock + data.quantity_delta
            if new_stock < 0:
                raise InsufficientStockError(product.id, abs(data.quantity_delta), product.current_stock)

            movement_type = (
                MovementType.AJUSTE_ENTRADA if data.quantity_delta > 0 else MovementType.AJUSTE_SALIDA
            )
            movement = uow.inventory_movements.add_movement(
                InventoryMovement(
                    id=None,
                    product_id=product.id,
                    movement_type=movement_type,
                    quantity=abs(data.quantity_delta),
                    unit_cost=product.cost_price,
                    balance_after=new_stock,
                    reference_type=MovementReferenceType.ADJUSTMENT,
                    reference_id=product.id,
                    notes=data.notes,
                )
            )
            product.current_stock = new_stock
            uow.products.update(product)
            uow.commit()
            return movement


class GetKardexUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, product_id: int) -> list[InventoryMovement]:
        with self._uow as uow:
            if uow.products.get_by_id(product_id) is None:
                raise NotFoundError("Producto", product_id)
            return uow.inventory_movements.list_by_product(product_id)


class ListInventoryMovementsUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, product_id: int | None = None) -> list[InventoryMovement]:
        with self._uow as uow:
            return uow.inventory_movements.list_all(product_id=product_id)
