from decimal import Decimal

import pytest

from app.application.services.accounting_service import AccountingService
from app.domain.entities.journal_entry import JournalEntry, JournalEntryLine
from app.domain.entities.sale import Sale, SaleItem
from app.domain.enums import JournalEntryReferenceType, PaymentMethod
from app.domain.exceptions import UnbalancedEntryError

ACCOUNT_IDS = {"1105": 1, "1305": 2, "4135": 3, "6135": 4, "1435": 5, "2205": 6}


def test_assert_balanced_accepts_equal_debit_and_credit():
    entry = JournalEntry(
        id=None,
        description="Asiento de prueba",
        reference_type=JournalEntryReferenceType.MANUAL,
        lines=[
            JournalEntryLine(id=None, account_id=1, debit=Decimal("100"), credit=Decimal("0")),
            JournalEntryLine(id=None, account_id=2, debit=Decimal("0"), credit=Decimal("100")),
        ],
    )
    AccountingService().assert_balanced(entry)  # no exception


def test_assert_balanced_rejects_unequal_debit_and_credit():
    entry = JournalEntry(
        id=None,
        description="Asiento descuadrado",
        reference_type=JournalEntryReferenceType.MANUAL,
        lines=[
            JournalEntryLine(id=None, account_id=1, debit=Decimal("100"), credit=Decimal("0")),
            JournalEntryLine(id=None, account_id=2, debit=Decimal("0"), credit=Decimal("90")),
        ],
    )
    with pytest.raises(UnbalancedEntryError):
        AccountingService().assert_balanced(entry)


def test_build_sale_entry_is_balanced_for_cash_sale():
    sale = Sale(
        id=1,
        payment_method=PaymentMethod.CONTADO,
        subtotal=Decimal("450"),
        total=Decimal("450"),
        items=[
            SaleItem(
                id=1,
                product_id=1,
                quantity=Decimal("3"),
                unit_price=Decimal("150"),
                unit_cost=Decimal("100"),
                subtotal=Decimal("450"),
            )
        ],
    )
    entry = AccountingService().build_sale_entry(ACCOUNT_IDS, sale, total_cost=Decimal("300"))

    assert entry.total_debit() == entry.total_credit() == Decimal("750")
    assert len(entry.lines) == 4


def test_build_sale_entry_uses_receivable_account_for_credit_sale():
    sale = Sale(
        id=1,
        payment_method=PaymentMethod.CREDITO,
        subtotal=Decimal("450"),
        total=Decimal("450"),
        items=[],
    )
    entry = AccountingService().build_sale_entry(ACCOUNT_IDS, sale, total_cost=Decimal("300"))

    receivable_line = next(line for line in entry.lines if line.account_id == ACCOUNT_IDS["1305"])
    assert receivable_line.debit == Decimal("450")
