from dataclasses import dataclass, field
from decimal import Decimal

from app.application.services.accounting_service import AccountingService, resolve_account_ids
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain import accounting_codes as codes
from app.domain.entities.inventory_movement import InventoryMovement
from app.domain.entities.sale import Sale, SaleItem
from app.domain.enums import MovementReferenceType, MovementType, PaymentMethod
from app.domain.exceptions import InsufficientStockError, InvalidOperationError, NotFoundError


@dataclass
class SaleItemInput:
    product_id: int
    quantity: Decimal
    unit_price: Decimal


@dataclass
class RegisterSaleInput:
    payment_method: PaymentMethod
    partner_id: int | None = None
    items: list[SaleItemInput] = field(default_factory=list)


class RegisterSaleUseCase:
    def __init__(self, uow: AbstractUnitOfWork, accounting: AccountingService | None = None):
        self._uow = uow
        self._accounting = accounting or AccountingService()

    def execute(self, data: RegisterSaleInput) -> Sale:
        if not data.items:
            raise InvalidOperationError("La venta debe tener al menos un item")

        with self._uow as uow:
            if data.partner_id is not None and uow.partners.get_by_id(data.partner_id) is None:
                raise NotFoundError("Tercero", data.partner_id)

            sale_items: list[SaleItem] = []
            subtotal = Decimal("0")
            products_by_id = {}
            for item in data.items:
                product = uow.products.get_by_id(item.product_id)
                if product is None:
                    raise NotFoundError("Producto", item.product_id)
                if product.current_stock < item.quantity:
                    raise InsufficientStockError(product.name, item.quantity, product.current_stock)
                products_by_id[item.product_id] = product
                item_subtotal = item.quantity * item.unit_price
                subtotal += item_subtotal
                sale_items.append(
                    SaleItem(
                        id=None,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_price=item.unit_price,
                        unit_cost=product.cost_price,
                        subtotal=item_subtotal,
                    )
                )

            sale = uow.sales.add(
                Sale(
                    id=None,
                    partner_id=data.partner_id,
                    payment_method=data.payment_method,
                    subtotal=subtotal,
                    total=subtotal,
                    items=sale_items,
                )
            )

            for item in sale.items:
                product = products_by_id[item.product_id]
                new_stock = product.current_stock - item.quantity
                uow.inventory_movements.add_movement(
                    InventoryMovement(
                        id=None,
                        product_id=item.product_id,
                        movement_type=MovementType.SALIDA_VENTA,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        balance_after=new_stock,
                        reference_type=MovementReferenceType.SALE,
                        reference_id=sale.id,
                    )
                )
                product.current_stock = new_stock
                uow.products.update(product)

            total_cost = sum((item.quantity * item.unit_cost for item in sale.items), Decimal("0"))
            cash_or_receivable = (
                codes.CAJA
                if data.payment_method == PaymentMethod.CONTADO
                else codes.CUENTAS_POR_COBRAR
            )
            needed_codes = [
                cash_or_receivable,
                codes.VENTAS,
                codes.COSTO_DE_VENTAS,
                codes.INVENTARIO,
            ]
            account_ids = resolve_account_ids(uow, needed_codes)
            entry = self._accounting.build_sale_entry(account_ids, sale, total_cost)
            uow.journal_entries.add(entry)

            uow.commit()
            return sale


class ListSalesUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[Sale]:
        with self._uow as uow:
            return uow.sales.list_all()


class GetSaleUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, sale_id: int) -> Sale:
        with self._uow as uow:
            sale = uow.sales.get_by_id(sale_id)
            if sale is None:
                raise NotFoundError("Venta", sale_id)
            return sale
