from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.sale import Sale, SaleItem
from app.domain.enums import PaymentMethod
from app.domain.repositories.sale_repository import SaleRepository
from app.infrastructure.db.models.sale_model import SaleItemModel, SaleModel


def _to_domain(model: SaleModel) -> Sale:
    return Sale(
        id=model.id,
        partner_id=model.partner_id,
        payment_method=PaymentMethod(model.payment_method),
        subtotal=model.subtotal,
        total=model.total,
        date=model.date,
        items=[
            SaleItem(
                id=item.id,
                sale_id=item.sale_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                unit_cost=item.unit_cost,
                subtotal=item.subtotal,
            )
            for item in model.items
        ],
    )


class SqlAlchemySaleRepository(SaleRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, sale: Sale) -> Sale:
        model = SaleModel(
            partner_id=sale.partner_id,
            payment_method=sale.payment_method.value,
            subtotal=sale.subtotal,
            total=sale.total,
            items=[
                SaleItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    unit_cost=item.unit_cost,
                    subtotal=item.subtotal,
                )
                for item in sale.items
            ],
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def get_by_id(self, sale_id: int) -> Sale | None:
        stmt = (
            select(SaleModel).options(selectinload(SaleModel.items)).where(SaleModel.id == sale_id)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None

    def list_all(self) -> list[Sale]:
        stmt = (
            select(SaleModel)
            .options(selectinload(SaleModel.items))
            .order_by(SaleModel.date.desc(), SaleModel.id.desc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
