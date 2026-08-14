from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.partner import Partner
from app.domain.enums import PartnerType
from app.domain.exceptions import NotFoundError
from app.domain.repositories.partner_repository import PartnerRepository
from app.infrastructure.db.models.partner_model import PartnerModel


def _to_domain(model: PartnerModel) -> Partner:
    return Partner(
        id=model.id,
        type=PartnerType(model.type),
        name=model.name,
        document_id=model.document_id,
        phone=model.phone,
        email=model.email,
        address=model.address,
        is_active=model.is_active,
    )


class SqlAlchemyPartnerRepository(PartnerRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, partner: Partner) -> Partner:
        model = PartnerModel(
            type=partner.type.value,
            name=partner.name,
            document_id=partner.document_id,
            phone=partner.phone,
            email=partner.email,
            address=partner.address,
            is_active=partner.is_active,
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def update(self, partner: Partner) -> Partner:
        model = self._session.get(PartnerModel, partner.id)
        if model is None:
            raise NotFoundError("Tercero", partner.id)
        model.type = partner.type.value
        model.name = partner.name
        model.document_id = partner.document_id
        model.phone = partner.phone
        model.email = partner.email
        model.address = partner.address
        model.is_active = partner.is_active
        self._session.flush()
        return _to_domain(model)

    def delete(self, partner_id: int) -> None:
        model = self._session.get(PartnerModel, partner_id)
        if model is not None:
            self._session.delete(model)
            self._session.flush()

    def get_by_id(self, partner_id: int) -> Partner | None:
        model = self._session.get(PartnerModel, partner_id)
        return _to_domain(model) if model else None

    def list(self, type: PartnerType | None = None) -> list[Partner]:
        stmt = select(PartnerModel)
        if type is not None:
            stmt = stmt.where(PartnerModel.type == type.value)
        stmt = stmt.order_by(PartnerModel.name)
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(m) for m in models]
