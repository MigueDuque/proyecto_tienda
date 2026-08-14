from decimal import Decimal

import pytest

from app.application.use_cases.purchases.register_purchase import (
    PurchaseItemInput,
    RegisterPurchaseInput,
    RegisterPurchaseUseCase,
)
from app.domain.entities.partner import Partner
from app.domain.entities.product import Product
from app.domain.enums import MovementType, PartnerType, PaymentMethod
from app.domain.exceptions import InvalidOperationError, NotFoundError
from tests.unit.application.fakes.in_memory_uow import InMemoryUnitOfWork


def _make_product(uow: InMemoryUnitOfWork, stock: Decimal = Decimal("10")) -> Product:
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


def _make_supplier(uow: InMemoryUnitOfWork, type: PartnerType = PartnerType.PROVEEDOR) -> Partner:
    return uow.partners.add(Partner(id=None, type=type, name="Proveedor de prueba"))


def test_register_purchase_increments_stock_and_updates_cost():
    uow = InMemoryUnitOfWork()
    product = _make_product(uow, stock=Decimal("10"))
    supplier = _make_supplier(uow)
    use_case = RegisterPurchaseUseCase(uow)

    result = use_case.execute(
        RegisterPurchaseInput(
            partner_id=supplier.id,
            payment_method=PaymentMethod.CREDITO,
            items=[
                PurchaseItemInput(product_id=product.id, quantity=Decimal("5"), unit_cost=Decimal("120"))
            ],
        )
    )

    assert result.total == Decimal("600")

    updated_product = uow.products.get_by_id(product.id)
    assert updated_product.current_stock == Decimal("15")
    assert updated_product.cost_price == Decimal("120")

    movements = uow.inventory_movements.list_by_product(product.id)
    assert len(movements) == 1
    assert movements[0].movement_type == MovementType.ENTRADA_COMPRA
    assert movements[0].balance_after == Decimal("15")
    assert uow.committed is True


def test_register_purchase_rejects_non_supplier_partner():
    uow = InMemoryUnitOfWork()
    product = _make_product(uow)
    customer = _make_supplier(uow, type=PartnerType.CLIENTE)
    use_case = RegisterPurchaseUseCase(uow)

    with pytest.raises(InvalidOperationError):
        use_case.execute(
            RegisterPurchaseInput(
                partner_id=customer.id,
                payment_method=PaymentMethod.CONTADO,
                items=[
                    PurchaseItemInput(
                        product_id=product.id, quantity=Decimal("1"), unit_cost=Decimal("10")
                    )
                ],
            )
        )
    assert uow.purchases.list_all() == []


def test_register_purchase_with_unknown_product_raises_not_found():
    uow = InMemoryUnitOfWork()
    supplier = _make_supplier(uow)
    use_case = RegisterPurchaseUseCase(uow)

    with pytest.raises(NotFoundError):
        use_case.execute(
            RegisterPurchaseInput(
                partner_id=supplier.id,
                payment_method=PaymentMethod.CONTADO,
                items=[
                    PurchaseItemInput(product_id=999, quantity=Decimal("1"), unit_cost=Decimal("10"))
                ],
            )
        )
