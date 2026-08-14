from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.entities.purchase import Purchase, PurchaseItem
from app.domain.enums import PaymentMethod
from app.domain.repositories.purchase_repository import PurchaseRepository
from app.infrastructure.db.models.purchase_model import PurchaseItemModel, PurchaseModel


def _to_domain(model: PurchaseModel) -> Purchase:
    return Purchase(
        id=model.id,
        partner_id=model.partner_id,
        payment_method=PaymentMethod(model.payment_method),
        subtotal=model.subtotal,
        total=model.total,
        date=model.date,
        items=[
            PurchaseItem(
                id=item.id,
                purchase_id=item.purchase_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_cost=item.unit_cost,
                subtotal=item.subtotal,
            )
            for item in model.items
        ],
    )


class SqlAlchemyPurchaseRepository(PurchaseRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, purchase: Purchase) -> Purchase:
        model = PurchaseModel(
            partner_id=purchase.partner_id,
            payment_method=purchase.payment_method.value,
            subtotal=purchase.subtotal,
            total=purchase.total,
            items=[
                PurchaseItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_cost=item.unit_cost,
                    subtotal=item.subtotal,
                )
                for item in purchase.items
            ],
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def get_by_id(self, purchase_id: int) -> Purchase | None:
        stmt = (
            select(PurchaseModel)
            .options(selectinload(PurchaseModel.items))
            .where(PurchaseModel.id == purchase_id)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None

    def list_all(self) -> list[Purchase]:
        stmt = (
            select(PurchaseModel)
            .options(selectinload(PurchaseModel.items))
            .order_by(PurchaseModel.date.desc(), PurchaseModel.id.desc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
