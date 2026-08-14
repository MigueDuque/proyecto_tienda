from dataclasses import dataclass, field
from decimal import Decimal

from app.application.services.accounting_service import AccountingService, resolve_account_ids
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain import accounting_codes as codes
from app.domain.entities.inventory_movement import InventoryMovement
from app.domain.entities.purchase import Purchase, PurchaseItem
from app.domain.enums import MovementReferenceType, MovementType, PartnerType, PaymentMethod
from app.domain.exceptions import InvalidOperationError, NotFoundError


@dataclass
class PurchaseItemInput:
    product_id: int
    quantity: Decimal
    unit_cost: Decimal


@dataclass
class RegisterPurchaseInput:
    partner_id: int
    payment_method: PaymentMethod
    items: list[PurchaseItemInput] = field(default_factory=list)


class RegisterPurchaseUseCase:
    def __init__(self, uow: AbstractUnitOfWork, accounting: AccountingService | None = None):
        self._uow = uow
        self._accounting = accounting or AccountingService()

    def execute(self, data: RegisterPurchaseInput) -> Purchase:
        if not data.items:
            raise InvalidOperationError("La compra debe tener al menos un item")

        with self._uow as uow:
            partner = uow.partners.get_by_id(data.partner_id)
            if partner is None:
                raise NotFoundError("Tercero", data.partner_id)
            if partner.type not in (PartnerType.PROVEEDOR, PartnerType.AMBOS):
                raise InvalidOperationError(
                    f"El tercero {partner.name} no esta habilitado como proveedor"
                )

            purchase_items: list[PurchaseItem] = []
            subtotal = Decimal("0")
            for item in data.items:
                product = uow.products.get_by_id(item.product_id)
                if product is None:
                    raise NotFoundError("Producto", item.product_id)
                item_subtotal = item.quantity * item.unit_cost
                subtotal += item_subtotal
                purchase_items.append(
                    PurchaseItem(
                        id=None,
                        product_id=item.product_id,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        subtotal=item_subtotal,
                    )
                )

            purchase = uow.purchases.add(
                Purchase(
                    id=None,
                    partner_id=data.partner_id,
                    payment_method=data.payment_method,
                    subtotal=subtotal,
                    total=subtotal,
                    items=purchase_items,
                )
            )

            for item in purchase.items:
                product = uow.products.get_by_id(item.product_id)
                new_stock = product.current_stock + item.quantity
                uow.inventory_movements.add_movement(
                    InventoryMovement(
                        id=None,
                        product_id=item.product_id,
                        movement_type=MovementType.ENTRADA_COMPRA,
                        quantity=item.quantity,
                        unit_cost=item.unit_cost,
                        balance_after=new_stock,
                        reference_type=MovementReferenceType.PURCHASE,
                        reference_id=purchase.id,
                    )
                )
                product.current_stock = new_stock
                product.cost_price = item.unit_cost
                uow.products.update(product)

            cash_or_payable = (
                codes.CAJA
                if data.payment_method == PaymentMethod.CONTADO
                else codes.CUENTAS_POR_PAGAR
            )
            account_ids = resolve_account_ids(uow, [codes.INVENTARIO, cash_or_payable])
            entry = self._accounting.build_purchase_entry(account_ids, purchase)
            uow.journal_entries.add(entry)

            uow.commit()
            return purchase


class ListPurchasesUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> list[Purchase]:
        with self._uow as uow:
            return uow.purchases.list_all()


class GetPurchaseUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, purchase_id: int) -> Purchase:
        with self._uow as uow:
            purchase = uow.purchases.get_by_id(purchase_id)
            if purchase is None:
                raise NotFoundError("Compra", purchase_id)
            return purchase
