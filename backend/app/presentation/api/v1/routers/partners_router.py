from fastapi import APIRouter, Depends

from app.application.use_cases.partners.partner_use_cases import (
    CreatePartnerUseCase,
    DeletePartnerUseCase,
    GetPartnerUseCase,
    ListPartnersUseCase,
    PartnerInput,
    UpdatePartnerUseCase,
)
from app.domain.enums import PartnerType
from app.presentation.api.v1.deps import (
    get_create_partner_use_case,
    get_current_user,
    get_delete_partner_use_case,
    get_get_partner_use_case,
    get_list_partners_use_case,
    get_update_partner_use_case,
)
from app.presentation.api.v1.schemas.partner_schemas import PartnerCreateRequest, PartnerResponse

router = APIRouter(prefix="/partners", tags=["partners"], dependencies=[Depends(get_current_user)])


def _to_input(payload: PartnerCreateRequest) -> PartnerInput:
    return PartnerInput(
        type=payload.type,
        name=payload.name,
        document_id=payload.document_id,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        is_active=payload.is_active,
    )


@router.get("", response_model=list[PartnerResponse])
def list_partners(
    type: PartnerType | None = None,
    use_case: ListPartnersUseCase = Depends(get_list_partners_use_case),
):
    return use_case.execute(type=type)


@router.post("", response_model=PartnerResponse, status_code=201)
def create_partner(
    payload: PartnerCreateRequest,
    use_case: CreatePartnerUseCase = Depends(get_create_partner_use_case),
):
    return use_case.execute(_to_input(payload))


@router.get("/{partner_id}", response_model=PartnerResponse)
def get_partner(partner_id: int, use_case: GetPartnerUseCase = Depends(get_get_partner_use_case)):
    return use_case.execute(partner_id)


@router.put("/{partner_id}", response_model=PartnerResponse)
def update_partner(
    partner_id: int,
    payload: PartnerCreateRequest,
    use_case: UpdatePartnerUseCase = Depends(get_update_partner_use_case),
):
    return use_case.execute(partner_id, _to_input(payload))


@router.delete("/{partner_id}", status_code=204)
def delete_partner(
    partner_id: int, use_case: DeletePartnerUseCase = Depends(get_delete_partner_use_case)
):
    use_case.execute(partner_id)
