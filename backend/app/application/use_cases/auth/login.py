from dataclasses import dataclass

from app.application.interfaces import PasswordHasher, TokenService
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.exceptions import InvalidCredentialsError


@dataclass
class LoginResult:
    access_token: str
    token_type: str = "bearer"


class LoginUseCase:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        password_hasher: PasswordHasher,
        token_service: TokenService,
    ):
        self._uow = uow
        self._password_hasher = password_hasher
        self._token_service = token_service

    def execute(self, email: str, password: str) -> LoginResult:
        with self._uow as uow:
            user = uow.users.get_by_email(email)
            if user is None or not user.is_active:
                raise InvalidCredentialsError()
            if not self._password_hasher.verify(password, user.password_hash):
                raise InvalidCredentialsError()

        token = self._token_service.create_access_token(subject=str(user.id))
        return LoginResult(access_token=token)
