from decimal import Decimal

import pytest

from app.application.use_cases.sales.register_sale import (
    RegisterSaleInput,
    RegisterSaleUseCase,
    SaleItemInput,
)
from app.domain.entities.product import Product
from app.domain.enums import MovementType, PaymentMethod
from app.domain.exceptions import InsufficientStockError
from tests.unit.application.fakes.in_memory_uow import InMemoryUnitOfWork, seed_chart_of_accounts


def _make_product(
    uow: InMemoryUnitOfWork, stock: Decimal, cost: Decimal = Decimal("100")
) -> Product:
    return uow.products.add(
        Product(
            id=None,
            sku="SKU-1",
            name="Producto de prueba",
            category_id=1,
            unit_of_measure="unidad",
            cost_price=cost,
            sale_price=Decimal("150"),
            current_stock=stock,
            min_stock=Decimal("5"),
        )
    )


def test_register_sale_decrements_stock_and_creates_movement():
    uow = InMemoryUnitOfWork()
    seed_chart_of_accounts(uow)
    product = _make_product(uow, stock=Decimal("10"), cost=Decimal("100"))
    use_case = RegisterSaleUseCase(uow)

    result = use_case.execute(
        RegisterSaleInput(
            payment_method=PaymentMethod.CONTADO,
            items=[
                SaleItemInput(
                    product_id=product.id, quantity=Decimal("3"), unit_price=Decimal("150")
                )
            ],
        )
    )

    assert result.subtotal == Decimal("450")
    assert result.total == Decimal("450")
    assert result.items[0].unit_cost == Decimal("100")

    updated_product = uow.products.get_by_id(product.id)
    assert updated_product.current_stock == Decimal("7")

    movements = uow.inventory_movements.list_by_product(product.id)
    assert len(movements) == 1
    assert movements[0].movement_type == MovementType.SALIDA_VENTA
    assert movements[0].quantity == Decimal("3")
    assert movements[0].balance_after == Decimal("7")
    assert uow.committed is True

    entries = uow.journal_entries.list_all()
    assert len(entries) == 1
    entry = entries[0]
    # subtotal (450) + COGS (3 * cost 100 = 300) on both sides
    assert entry.total_debit() == entry.total_credit() == Decimal("750")


def test_register_sale_with_insufficient_stock_raises_and_persists_nothing():
    uow = InMemoryUnitOfWork()
    product = _make_product(uow, stock=Decimal("2"))
    use_case = RegisterSaleUseCase(uow)

    with pytest.raises(InsufficientStockError) as exc_info:
        use_case.execute(
            RegisterSaleInput(
                payment_method=PaymentMethod.CONTADO,
                items=[
                    SaleItemInput(
                        product_id=product.id, quantity=Decimal("5"), unit_price=Decimal("150")
                    )
                ],
            )
        )

    # The message must name the product and use clean quantities, since it is
    # shown verbatim to the shop clerk in the UI.
    message = str(exc_info.value)
    assert "Producto de prueba" in message
    assert "solicitaste 5" in message
    assert "solo hay 2 disponibles" in message

    assert uow.products.get_by_id(product.id).current_stock == Decimal("2")
    assert uow.sales.list_all() == []
    assert uow.inventory_movements.list_all() == []
    assert uow.journal_entries.list_all() == []
    assert uow.committed is False
