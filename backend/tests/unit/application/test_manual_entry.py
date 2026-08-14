from decimal import Decimal

import pytest

from app.application.use_cases.accounting.accounting_use_cases import (
    ManualEntryLineInput,
    RegisterManualEntryInput,
    RegisterManualEntryUseCase,
)
from app.domain.exceptions import InvalidOperationError, UnbalancedEntryError
from tests.unit.application.fakes.in_memory_uow import InMemoryUnitOfWork, seed_chart_of_accounts


def test_register_manual_entry_persists_balanced_entry():
    uow = InMemoryUnitOfWork()
    seed_chart_of_accounts(uow)
    caja = uow.accounts.get_by_code("1105")
    gastos = uow.accounts.get_by_code("5195")
    use_case = RegisterManualEntryUseCase(uow)

    entry = use_case.execute(
        RegisterManualEntryInput(
            description="Pago de arriendo",
            lines=[
                ManualEntryLineInput(
                    account_id=gastos.id, debit=Decimal("50000"), credit=Decimal("0")
                ),
                ManualEntryLineInput(
                    account_id=caja.id, debit=Decimal("0"), credit=Decimal("50000")
                ),
            ],
        )
    )

    assert entry.total_debit() == entry.total_credit() == Decimal("50000")
    assert len(uow.journal_entries.list_all()) == 1
    assert uow.committed is True


def test_register_manual_entry_rejects_unbalanced_lines():
    uow = InMemoryUnitOfWork()
    seed_chart_of_accounts(uow)
    caja = uow.accounts.get_by_code("1105")
    gastos = uow.accounts.get_by_code("5195")
    use_case = RegisterManualEntryUseCase(uow)

    with pytest.raises(UnbalancedEntryError):
        use_case.execute(
            RegisterManualEntryInput(
                description="Asiento descuadrado",
                lines=[
                    ManualEntryLineInput(
                        account_id=gastos.id, debit=Decimal("100"), credit=Decimal("0")
                    ),
                    ManualEntryLineInput(
                        account_id=caja.id, debit=Decimal("0"), credit=Decimal("90")
                    ),
                ],
            )
        )
    assert uow.journal_entries.list_all() == []


def test_register_manual_entry_requires_at_least_two_lines():
    uow = InMemoryUnitOfWork()
    seed_chart_of_accounts(uow)
    caja = uow.accounts.get_by_code("1105")
    use_case = RegisterManualEntryUseCase(uow)

    with pytest.raises(InvalidOperationError):
        use_case.execute(
            RegisterManualEntryInput(
                description="Asiento invalido",
                lines=[
                    ManualEntryLineInput(
                        account_id=caja.id, debit=Decimal("100"), credit=Decimal("0")
                    )
                ],
            )
        )
