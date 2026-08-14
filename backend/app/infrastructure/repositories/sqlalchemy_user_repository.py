from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository
from app.infrastructure.db.models.user_model import UserModel


def _to_domain(model: UserModel) -> User:
    return User(
        id=model.id,
        email=model.email,
        password_hash=model.password_hash,
        full_name=model.full_name,
        is_active=model.is_active,
    )


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def add(self, user: User) -> User:
        model = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            full_name=user.full_name,
            is_active=user.is_active,
        )
        self._session.add(model)
        self._session.flush()
        return _to_domain(model)

    def get_by_id(self, user_id: int) -> User | None:
        model = self._session.get(UserModel, user_id)
        return _to_domain(model) if model else None

    def get_by_email(self, email: str) -> User | None:
        stmt = select(UserModel).where(UserModel.email == email)
        model = self._session.execute(stmt).scalar_one_or_none()
        return _to_domain(model) if model else None
