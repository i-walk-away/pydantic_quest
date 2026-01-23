import hmac
from base64 import urlsafe_b64encode
from hashlib import sha256
from secrets import token_urlsafe


def create_oauth_state(secret: str) -> tuple[str, str, str]:
    """
    Create signed OAuth state and PKCE verifier payload.

    :param secret: signing secret

    :return: tuple of state, code_verifier, cookie_value
    """
    state = token_urlsafe(32)
    code_verifier = token_urlsafe(64)
    signature = _sign(secret=secret, state=state, code_verifier=code_verifier)
    cookie_value = f"{state}.{code_verifier}.{signature}"

    return state, code_verifier, cookie_value


def parse_oauth_state(
        secret: str,
        cookie_value: str,
        state: str,
) -> str | None:
    """
    Validate OAuth state cookie and return code_verifier.

    :param secret: signing secret
    :param cookie_value: cookie payload
    :param state: state from the query string

    :return: code_verifier
    """
    parts = cookie_value.split(".")
    if len(parts) != 3:
        return None

    stored_state, code_verifier, signature = parts
    expected_signature = _sign(
        secret=secret,
        state=stored_state,
        code_verifier=code_verifier,
    )

    if not hmac.compare_digest(signature, expected_signature):
        return None

    if stored_state != state:
        return None

    return code_verifier


def build_code_challenge(code_verifier: str) -> str:
    """
    Build PKCE code challenge for the given verifier.

    :param code_verifier: PKCE verifier

    :return: PKCE challenge string
    """
    digest = sha256(code_verifier.encode()).digest()
    return urlsafe_b64encode(digest).rstrip(b"=").decode()


def _sign(secret: str, state: str, code_verifier: str) -> str:
    message = f"{state}.{code_verifier}".encode()
    return hmac.new(secret.encode(), message, sha256).hexdigest()
