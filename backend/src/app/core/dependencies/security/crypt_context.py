from passlib.context import CryptContext


def get_crypt_context() -> CryptContext:
    """
    Constructs an instance of passlib.CryptContext, which handles
    hash operations (hashing a password, verifying a hash etc).

    :return: CryptContext object.
    """
    return CryptContext(schemes=["bcrypt"], deprecated="auto")
