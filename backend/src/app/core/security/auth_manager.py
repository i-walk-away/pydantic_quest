from datetime import datetime, timedelta, UTC
from uuid import uuid4

from jwt import encode
from passlib.context import CryptContext

from src.cfg.cfg import settings


class AuthManager:
    """
    Manages security operations related to authentication.
    """

    def __init__(self, context: CryptContext) -> None:
        self.context = context

    def hash_password(self, password: str) -> str:
        """
        Hashes a password.

        :param password: input password to hash
        :return: hash value
        """
        return self.context.hash(secret=password)

    def verify_password_against_hash(
            self,
            plain_password: str,
            hashed_password: str,
    ) -> bool:
        """
        Validates a given plaintext password against a hashed one. the plain_password gets
        hashed and the result is compared to the given hashed_password.

        :param plain_password: Password to validate
        :param hashed_password: Hashed password to validate against

        :return: True if hashing plain_password results in a hash that exactly matches
          hashed_password. Otherwise False.
        """
        return self.context.verify(secret=plain_password, hash=hashed_password)

    @staticmethod
    def generate_jwt(
            input_data: dict,
            expires_in: int = settings.auth.jwt_lifespan,
    ) -> str:
        """
        Generates a JSON Web Token (JWT).

        :param input_data: Data to encode in the token payload
        :param expires_in: Amount ot minutes until the token expires.

        :return: JSON Web Token.
        """
        jwt_payload = input_data.copy()
        jwt_payload.update(
            {
                'iat': datetime.now(UTC),
                'exp': datetime.now(UTC) + timedelta(expires_in),
                'jti': str(uuid4()),
            },
        )
        return encode(
            payload=jwt_payload,
            key=settings.auth.jwt_secret_key,
            algorithm=settings.auth.jwt_algorithm,
        )
