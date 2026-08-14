from dataclasses import dataclass

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities.partner import Partner
from app.domain.enums import PartnerType
from app.domain.exceptions import NotFoundError


@dataclass
class PartnerInput:
    type: PartnerType
    name: str
    document_id: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    is_active: bool = True


class CreatePartnerUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, data: PartnerInput) -> Partner:
        with self._uow as uow:
            partner = Partner(
                id=None,
                type=data.type,
                name=data.name,
                document_id=data.document_id,
                phone=data.phone,
                email=data.email,
                address=data.address,
                is_active=data.is_active,
            )
            created = uow.partners.add(partner)
            uow.commit()
            return created


class UpdatePartnerUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, partner_id: int, data: PartnerInput) -> Partner:
        with self._uow as uow:
            existing = uow.partners.get_by_id(partner_id)
            if existing is None:
                raise NotFoundError("Tercero", partner_id)
            existing.type = data.type
            existing.name = data.name
            existing.document_id = data.document_id
            existing.phone = data.phone
            existing.email = data.email
            existing.address = data.address
            existing.is_active = data.is_active
            updated = uow.partners.update(existing)
            uow.commit()
            return updated


class DeletePartnerUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, partner_id: int) -> None:
        with self._uow as uow:
            if uow.partners.get_by_id(partner_id) is None:
                raise NotFoundError("Tercero", partner_id)
            uow.partners.delete(partner_id)
            uow.commit()


class GetPartnerUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, partner_id: int) -> Partner:
        with self._uow as uow:
            partner = uow.partners.get_by_id(partner_id)
            if partner is None:
                raise NotFoundError("Tercero", partner_id)
            return partner


class ListPartnersUseCase:
    def __init__(self, uow: AbstractUnitOfWork):
        self._uow = uow

    def execute(self, type: PartnerType | None = None) -> list[Partner]:
        with self._uow as uow:
            return uow.partners.list(type=type)
