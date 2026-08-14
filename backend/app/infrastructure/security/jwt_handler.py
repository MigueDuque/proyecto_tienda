from datetime import UTC, datetime, timedelta

import jwt

from app.domain.exceptions import InvalidCredentialsError
from app.infrastructure.config import Settings


class JwtTokenService:
    def __init__(self, settings: Settings):
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._expire_minutes = settings.jwt_expire_minutes

    def create_access_token(self, subject: str) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self._expire_minutes)
        payload = {"sub": subject, "exp": expire}
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode_subject(self, token: str) -> str:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            raise InvalidCredentialsError()
        subject = payload.get("sub")
        if subject is None:
            raise InvalidCredentialsError()
        return subject
