from decimal import Decimal
from typing import TYPE_CHECKING

from app.domain import accounting_codes as codes
from app.domain.entities.journal_entry import JournalEntry, JournalEntryLine
from app.domain.entities.purchase import Purchase
from app.domain.entities.sale import Sale
from app.domain.enums import JournalEntryReferenceType, PaymentMethod
from app.domain.exceptions import NotFoundError, UnbalancedEntryError

if TYPE_CHECKING:
    from app.application.unit_of_work import AbstractUnitOfWork


def resolve_account_ids(uow: "AbstractUnitOfWork", codes_needed: list[str]) -> dict[str, int]:
    """Looks up chart-of-accounts ids by code, used to build journal entries."""
    ids: dict[str, int] = {}
    for code in codes_needed:
        account = uow.accounts.get_by_code(code)
        if account is None:
            raise NotFoundError("CuentaContable", code)
        ids[code] = account.id
    return ids


class AccountingService:
    """Builds balanced journal entries for sales and purchases.

    Callers pass a {account_code: account_id} lookup (fetched once from the
    chart of accounts) so this service stays free of any repository/DB
    dependency and is trivially unit-testable.
    """

    def assert_balanced(self, entry: JournalEntry) -> None:
        total_debit = entry.total_debit()
        total_credit = entry.total_credit()
        if total_debit != total_credit:
            raise UnbalancedEntryError(total_debit, total_credit)

    def build_sale_entry(
        self, accounts: dict[str, int], sale: Sale, total_cost: Decimal
    ) -> JournalEntry:
        cash_or_receivable = (
            codes.CAJA if sale.payment_method == PaymentMethod.CONTADO else codes.CUENTAS_POR_COBRAR
        )

        entry = JournalEntry(
            id=None,
            description=f"Venta #{sale.id}",
            reference_type=JournalEntryReferenceType.SALE,
            reference_id=sale.id,
            lines=[
                JournalEntryLine(
                    id=None, account_id=accounts[cash_or_receivable], debit=sale.total, credit=Decimal("0")
                ),
                JournalEntryLine(
                    id=None, account_id=accounts[codes.VENTAS], debit=Decimal("0"), credit=sale.subtotal
                ),
                JournalEntryLine(
                    id=None,
                    account_id=accounts[codes.COSTO_DE_VENTAS],
                    debit=total_cost,
                    credit=Decimal("0"),
                ),
                JournalEntryLine(
                    id=None, account_id=accounts[codes.INVENTARIO], debit=Decimal("0"), credit=total_cost
                ),
            ],
        )
        self.assert_balanced(entry)
        return entry

    def build_purchase_entry(self, accounts: dict[str, int], purchase: Purchase) -> JournalEntry:
        cash_or_payable = (
            codes.CAJA if purchase.payment_method == PaymentMethod.CONTADO else codes.CUENTAS_POR_PAGAR
        )

        entry = JournalEntry(
            id=None,
            description=f"Compra #{purchase.id}",
            reference_type=JournalEntryReferenceType.PURCHASE,
            reference_id=purchase.id,
            lines=[
                JournalEntryLine(
                    id=None, account_id=accounts[codes.INVENTARIO], debit=purchase.total, credit=Decimal("0")
                ),
                JournalEntryLine(
                    id=None,
                    account_id=accounts[cash_or_payable],
                    debit=Decimal("0"),
                    credit=purchase.total,
                ),
            ],
        )
        self.assert_balanced(entry)
        return entry
