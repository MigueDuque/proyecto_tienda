from decimal import Decimal

import pytest

from app.application.use_cases.inventory.inventory_use_cases import (
    AdjustStockInput,
    AdjustStockUseCase,
)
from app.domain.entities.product import Product
from app.domain.enums import MovementType
from app.domain.exceptions import InsufficientStockError
from tests.unit.application.fakes.in_memory_uow import InMemoryUnitOfWork


def _make_product(uow: InMemoryUnitOfWork, stock: Decimal) -> Product:
    return uow.products.add(
        Product(
            id=None,
            sku="SKU-1",
            name="Producto de prueba",
            category_id=1,
            unit_of_measure="unidad",
            cost_price=Decimal("100"),
            sale_price=Decimal("150"),
            current_stock=stock,
            min_stock=Decimal("5"),
        )
    )


def test_positive_adjustment_increments_stock():
    uow = InMemoryUnitOfWork()
    product = _make_product(uow, stock=Decimal("10"))
    use_case = AdjustStockUseCase(uow)

    movement = use_case.execute(AdjustStockInput(product_id=product.id, quantity_delta=Decimal("4")))

    assert movement.movement_type == MovementType.AJUSTE_ENTRADA
    assert uow.products.get_by_id(product.id).current_stock == Decimal("14")


def test_negative_adjustment_below_zero_raises():
    uow = InMemoryUnitOfWork()
    product = _make_product(uow, stock=Decimal("3"))
    use_case = AdjustStockUseCase(uow)

    with pytest.raises(InsufficientStockError):
        use_case.execute(AdjustStockInput(product_id=product.id, quantity_delta=Decimal("-5")))

    assert uow.products.get_by_id(product.id).current_stock == Decimal("3")
