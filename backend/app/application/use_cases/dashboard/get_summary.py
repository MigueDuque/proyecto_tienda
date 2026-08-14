from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain import accounting_codes as codes
from app.domain.entities.product import Product
from app.domain.entities.purchase import Purchase
from app.domain.entities.sale import Sale


@dataclass
class DashboardSummary:
    sales_today_total: Decimal
    sales_month_total: Decimal
    cash_balance: Decimal
    low_stock_products: list[Product] = field(default_factory=list)
    recent_sales: list[Sale] = field(default_factory=list)
    recent_purchases: list[Purchase] = field(default_factory=list)


class GetDashboardSummaryUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self) -> DashboardSummary:
        with self._uow as uow:
            now = datetime.now(UTC)
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            month_start = today_start.replace(day=1)

            all_sales = uow.sales.list_all()
            sales_today_total = sum(
                (s.total for s in all_sales if s.date and s.date >= today_start), Decimal("0")
            )
            sales_month_total = sum(
                (s.total for s in all_sales if s.date and s.date >= month_start), Decimal("0")
            )

            cash_balance = Decimal("0")
            for code in (codes.CAJA, codes.BANCOS):
                account = uow.accounts.get_by_code(code)
                if account is not None:
                    cash_balance += uow.accounts.get_balance(account.id)

            return DashboardSummary(
                sales_today_total=sales_today_total,
                sales_month_total=sales_month_total,
                cash_balance=cash_balance,
                low_stock_products=uow.products.list_low_stock(),
                recent_sales=all_sales[:5],
                recent_purchases=uow.purchases.list_all()[:5],
            )
