from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.inventory_movement import InventoryMovement
from app.domain.enums import MovementReferenceType, MovementType
from app.domain.repositories.inventory_repository import InventoryRepository
from app.infrastructure.db.models.inventory_movement_model import InventoryMovementModel


def _to_domain(model: InventoryMovementModel) -> InventoryMovement:
    return InventoryMovement(
        id=model.id,
        product_id=model.product_id,
        movement_type=MovementType(model.movement_type),
        quantity=model.quantity,
        unit_cost=model.unit_cost,
        balance_after=model.balance_after,
        reference_type=MovementReferenceType(model.reference_type),
        reference_id=model.reference_id,
        notes=model.notes,
        created_at=model.created_at,
    )


class SqlAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: Session):
        self._session = session

    def add_movement(self, movement: InventoryMovement) -> InventoryMovement:
        model = InventoryMovementModel(
            product_id=movement.product_id,
            movement_type=movement.movement_type.value,
            quantity=movement.quantity,
            unit_cost=movement.unit_cost,
            balance_after=movement.balance_after,
            reference_type=movement.reference_type.value,
            reference_id=movement.reference_id,
            notes=movement.notes,
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def list_by_product(self, product_id: int) -> list[InventoryMovement]:
        stmt = (
            select(InventoryMovementModel)
            .where(InventoryMovementModel.product_id == product_id)
            .order_by(InventoryMovementModel.created_at, InventoryMovementModel.id)
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]

    def list_all(self, product_id: int | None = None) -> list[InventoryMovement]:
        stmt = select(InventoryMovementModel)
        if product_id is not None:
            stmt = stmt.where(InventoryMovementModel.product_id == product_id)
        stmt = stmt.order_by(
            InventoryMovementModel.created_at.desc(), InventoryMovementModel.id.desc()
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
