"""Idempotent demo data seed: admin user, categories, products, partners,
chart of accounts, and a handful of demo purchases/sales so the dashboard
and accounting screens look populated right after `docker-compose up`.
"""

from decimal import Decimal

from app.application.use_cases.purchases.register_purchase import (
    PurchaseItemInput,
    RegisterPurchaseInput,
    RegisterPurchaseUseCase,
)
from app.application.use_cases.sales.register_sale import (
    RegisterSaleInput,
    RegisterSaleUseCase,
    SaleItemInput,
)
from app.domain.accounting_codes import SEED_ACCOUNTS
from app.domain.entities.account import Account
from app.domain.entities.category import Category
from app.domain.entities.partner import Partner
from app.domain.entities.product import Product
from app.domain.entities.user import User
from app.domain.enums import AccountType, PartnerType, PaymentMethod
from app.infrastructure.config import get_settings
from app.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork
from app.infrastructure.security.password_hasher import BcryptPasswordHasher

CATEGORIES = ["Granos", "Abarrotes", "Aseo", "Bebidas"]

PRODUCTS = [
    # sku, name, category, unit, cost, sale, stock, min_stock
    ("GRA-001", "Arroz Diana 500g", "Granos", "unidad", "1800", "2500", "120", "20"),
    ("GRA-002", "Frijol Rojo 500g", "Granos", "unidad", "2200", "3000", "80", "15"),
    ("GRA-003", "Lenteja 500g", "Granos", "unidad", "2000", "2800", "10", "15"),
    ("GRA-004", "Maiz Trillado 1kg", "Granos", "unidad", "1500", "2200", "60", "10"),
    ("ABA-001", "Aceite Girasol 1L", "Abarrotes", "unidad", "6500", "8500", "40", "10"),
    ("ABA-002", "Azucar Blanca 1kg", "Abarrotes", "unidad", "2800", "3800", "8", "10"),
    ("ABA-003", "Sal Refisal 500g", "Abarrotes", "unidad", "900", "1500", "70", "10"),
    ("ASE-001", "Jabon en Polvo 1kg", "Aseo", "unidad", "5500", "7500", "25", "8"),
    ("ASE-002", "Detergente Liquido 1L", "Aseo", "unidad", "7000", "9500", "5", "8"),
    ("BEB-001", "Gaseosa Cola 1.5L", "Bebidas", "unidad", "3200", "4500", "50", "12"),
]

PARTNERS = [
    (PartnerType.PROVEEDOR, "Distribuidora El Trigal", "900123456-1", "3001234567"),
    (PartnerType.CLIENTE, "Consumidor Final Frecuente", None, "3009876543"),
    (PartnerType.AMBOS, "Comercializadora La Cosecha", "900654321-2", "3005556677"),
]


def run() -> None:
    settings = get_settings()
    hasher = BcryptPasswordHasher()

    with SqlAlchemyUnitOfWork() as uow:
        if uow.users.get_by_email(settings.admin_email) is None:
            uow.users.add(
                User(
                    id=None,
                    email=settings.admin_email,
                    password_hash=hasher.hash(settings.admin_password),
                    full_name=settings.admin_full_name,
                )
            )
            print(f"Usuario admin creado: {settings.admin_email}")

        category_ids: dict[str, int] = {}
        for name in CATEGORIES:
            existing = uow.categories.get_by_name(name)
            if existing is None:
                existing = uow.categories.add(Category(id=None, name=name))
                print(f"Categoria creada: {name}")
            category_ids[name] = existing.id

        for sku, name, cat_name, unit, cost, sale, stock, min_stock in PRODUCTS:
            if uow.products.get_by_sku(sku) is None:
                uow.products.add(
                    Product(
                        id=None,
                        sku=sku,
                        name=name,
                        category_id=category_ids[cat_name],
                        unit_of_measure=unit,
                        cost_price=Decimal(cost),
                        sale_price=Decimal(sale),
                        current_stock=Decimal(stock),
                        min_stock=Decimal(min_stock),
                    )
                )
                print(f"Producto creado: {sku} - {name}")

        existing_partner_names = {p.name for p in uow.partners.list()}
        for ptype, name, document_id, phone in PARTNERS:
            if name not in existing_partner_names:
                uow.partners.add(
                    Partner(id=None, type=ptype, name=name, document_id=document_id, phone=phone)
                )
                print(f"Tercero creado: {name}")

        for code, name, account_type in SEED_ACCOUNTS:
            if uow.accounts.get_by_code(code) is None:
                uow.accounts.add(
                    Account(id=None, code=code, name=name, type=AccountType(account_type))
                )
                print(f"Cuenta contable creada: {code} - {name}")

        uow.commit()

    seed_demo_transactions()

    print("Seed completado.")


def seed_demo_transactions() -> None:
    """Registers a few demo purchases/sales through the real use cases (so
    inventory and accounting stay consistent), only on the very first run.
    """
    with SqlAlchemyUnitOfWork() as uow:
        if uow.purchases.list_all():
            return
        products = {p.sku: p.id for p in uow.products.list()}
        supplier = next(p for p in uow.partners.list() if p.name == "Distribuidora El Trigal")
        supplier_customer = next(
            p for p in uow.partners.list() if p.name == "Comercializadora La Cosecha"
        )
        frequent_customer = next(
            p for p in uow.partners.list() if p.name == "Consumidor Final Frecuente"
        )

    RegisterPurchaseUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterPurchaseInput(
            partner_id=supplier.id,
            payment_method=PaymentMethod.CREDITO,
            items=[
                PurchaseItemInput(products["GRA-001"], Decimal("30"), Decimal("1800")),
                PurchaseItemInput(products["ABA-001"], Decimal("15"), Decimal("6500")),
            ],
        )
    )
    print("Compra demo registrada: Distribuidora El Trigal")

    RegisterPurchaseUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterPurchaseInput(
            partner_id=supplier_customer.id,
            payment_method=PaymentMethod.CONTADO,
            items=[PurchaseItemInput(products["BEB-001"], Decimal("20"), Decimal("3200"))],
        )
    )
    print("Compra demo registrada: Comercializadora La Cosecha")

    RegisterSaleUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterSaleInput(
            partner_id=frequent_customer.id,
            payment_method=PaymentMethod.CONTADO,
            items=[
                SaleItemInput(products["GRA-001"], Decimal("10"), Decimal("2500")),
                SaleItemInput(products["ABA-003"], Decimal("5"), Decimal("1500")),
            ],
        )
    )
    print("Venta demo registrada: Consumidor Final Frecuente")

    RegisterSaleUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterSaleInput(
            payment_method=PaymentMethod.CONTADO,
            items=[SaleItemInput(products["GRA-002"], Decimal("8"), Decimal("3000"))],
        )
    )
    print("Venta demo registrada: consumidor final")

    RegisterSaleUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterSaleInput(
            partner_id=supplier_customer.id,
            payment_method=PaymentMethod.CREDITO,
            items=[
                SaleItemInput(products["ASE-001"], Decimal("6"), Decimal("7500")),
                SaleItemInput(products["GRA-004"], Decimal("10"), Decimal("2200")),
            ],
        )
    )
    print("Venta demo registrada: Comercializadora La Cosecha")

    RegisterSaleUseCase(SqlAlchemyUnitOfWork()).execute(
        RegisterSaleInput(
            payment_method=PaymentMethod.CONTADO,
            items=[SaleItemInput(products["BEB-001"], Decimal("12"), Decimal("4500"))],
        )
    )
    print("Venta demo registrada: consumidor final")


if __name__ == "__main__":
    run()
