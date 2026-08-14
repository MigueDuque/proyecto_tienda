from fastapi import APIRouter, Depends

from app.application.use_cases.accounting.accounting_use_cases import (
    GetAccountBalanceUseCase,
    ListAccountsUseCase,
    ListJournalEntriesUseCase,
    ManualEntryLineInput,
    RegisterManualEntryInput,
    RegisterManualEntryUseCase,
)
from app.presentation.api.v1.deps import (
    get_current_user,
    get_get_account_balance_use_case,
    get_list_accounts_use_case,
    get_list_journal_entries_use_case,
    get_register_manual_entry_use_case,
)
from app.presentation.api.v1.schemas.accounting_schemas import (
    AccountBalanceResponse,
    AccountResponse,
    JournalEntryResponse,
    ManualEntryCreateRequest,
)

router = APIRouter(
    prefix="/accounting", tags=["accounting"], dependencies=[Depends(get_current_user)]
)


@router.get("/accounts", response_model=list[AccountResponse])
def list_accounts(use_case: ListAccountsUseCase = Depends(get_list_accounts_use_case)):
    return use_case.execute()


@router.get("/accounts/{account_id}/balance", response_model=AccountBalanceResponse)
def get_account_balance(
    account_id: int, use_case: GetAccountBalanceUseCase = Depends(get_get_account_balance_use_case)
):
    balance = use_case.execute(account_id)
    return AccountBalanceResponse(account_id=account_id, balance=balance)


@router.get("/journal-entries", response_model=list[JournalEntryResponse])
def list_journal_entries(
    use_case: ListJournalEntriesUseCase = Depends(get_list_journal_entries_use_case),
):
    return use_case.execute()


@router.post("/journal-entries", response_model=JournalEntryResponse, status_code=201)
def create_manual_entry(
    payload: ManualEntryCreateRequest,
    use_case: RegisterManualEntryUseCase = Depends(get_register_manual_entry_use_case),
):
    data = RegisterManualEntryInput(
        description=payload.description,
        lines=[
            ManualEntryLineInput(
                account_id=line.account_id,
                debit=line.debit,
                credit=line.credit,
                description=line.description,
            )
            for line in payload.lines
        ],
    )
    return use_case.execute(data)
