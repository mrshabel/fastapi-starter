import jwt
import random
import urllib.parse
import hashlib
import threading
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from src.core.config import AppConfig
from src.models.user import TokenPayload, GoogleOAuthTokenPayload, OAuthProvider
from fastapi.logger import logger

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# compare plain and hashed passwords
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify if the input plain password matches the saved hashed password
    """
    try:
        return pwd_context.verify(secret=plain_password, hash=hashed_password)
    except (ValueError, TypeError):
        return False


# create a hash of the given password
def create_password_hash(password: str) -> str:
    """
    Create a hash of the input password
    """
    return pwd_context.hash(password)


def create_access_token(data: TokenPayload) -> str:
    """
    Create an encoded access token
    """
    to_encode = data.model_dump()
    to_encode.update({"sub": str(data.sub)})

    # set expiry
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(AppConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        payload=to_encode, key=AppConfig.JWT_SECRET, algorithm=AppConfig.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: TokenPayload) -> tuple[str, datetime]:
    """
    Create an encoded refresh token
    """
    to_encode = data.model_dump()
    to_encode.update({"sub": str(data.sub)})

    # set expiry
    expire = datetime.now(timezone.utc) + timedelta(
        hours=int(AppConfig.REFRESH_TOKEN_EXPIRE_HOURS)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        payload=to_encode,
        key=AppConfig.JWT_SECRET,
        algorithm=AppConfig.JWT_ALGORITHM,
    )
    return encoded_jwt, expire


def decode_token(token: str) -> TokenPayload | None:
    """
    Decode the input access token
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=AppConfig.JWT_SECRET,
            algorithms=AppConfig.JWT_ALGORITHM,
            verify=True,
        )

        # check for token expiry
        expiry = payload.get("exp")
        if not expiry or datetime.fromtimestamp(expiry) < datetime.now():
            return None

        sub = payload.get("sub")
        if not sub:
            return None

        token_data = TokenPayload(**payload)
    except Exception as e:
        logger.warning("Fatal Error. Token verification failed: ", str(e))
        raise

    return token_data


def decode_refresh_token(token: str) -> TokenPayload | None:
    """
    Decode the input refresh token
    """
    try:
        payload = jwt.decode(
            jwt=token,
            key=AppConfig.JWT_SECRET,
            algorithms=AppConfig.JWT_ALGORITHM,
            verify=True,
        )

        # check for token expiry
        expiry = payload.get("exp")
        if not expiry or datetime.fromtimestamp(expiry) < datetime.now():
            return None

        sub = payload.get("sub")
        if not sub:
            return None

        token_data = TokenPayload(**payload)
    except Exception as e:
        logger.warning("Fatal Error. Token verification failed: ", str(e))
        return None

    return token_data


def generate_otp(length: int = 6) -> tuple[str, datetime]:
    """
    Generate a new otp token

    Args:
        length (int): the length of the token
    Returns:
        token (str): the otp
        expiry (datetime): date and time the token expires
    """
    expiry: datetime = datetime.now(timezone.utc) + timedelta(
        minutes=AppConfig.OTP_EXPIRE_MINUTES
    )

    domain = "0123456789"
    otp = [random.choice(domain) for _ in range(length)]

    return "".join(otp), expiry


# external oauth
# store all clients that have initiated the oauth flow with their ttl
connected_oath_clients: dict[str, datetime] = {}
lock = threading.Lock()

# async def cleanup_stale_client_states():
#     for state, ttl in connected_oath_clients.items():
#         if ttl < datetime.now(timezone.utc):
#             with lock:
#                 connected_oath_clients.pop(state)

# # run in background
# loop = asyncio.get_running_loop()
# loop.run_in_executor()


def update_client_state(client_origin: str):
    ttl = datetime.now(timezone.utc) + timedelta(minutes=5)
    state = hashlib.sha256(client_origin.encode()).hexdigest()
    # lock map with a mutex to ensure atomic writes
    with lock:
        connected_oath_clients[state] = ttl
    return state


def check_client_state(state: str) -> bool:
    """Check if an OAuth client has initiated a request"""
    # check if state exists or ttl has not expired
    ttl = connected_oath_clients.get(state)
    if not ttl:
        return False

    if ttl < datetime.now(timezone.utc):
        # invalidate cache
        connected_oath_clients.pop(state)
        return False

    return True


def get_external_oauth_url(
    redirect_uri: str, state: str, provider: OAuthProvider = OAuthProvider.GOOGLE
):
    # compose details based on provider
    url: str
    client_id: str
    scope: str

    match provider:
        case OAuthProvider.GOOGLE:
            url = AppConfig.GOOGLE_OAUTH_URL
            client_id = AppConfig.GOOGLE_CLIENT_ID
            scope = AppConfig.GOOGLE_OAUTH_SCOPES
        case _:
            return

    # define client options, redirect url and scopes
    params = {
        "client_id": client_id,
        "scope": scope,
        "state": state,
        "redirect_uri": redirect_uri,
        "prompt": "consent",
        "response_type": "code",
        "access_type": "offline",
    }
    # encode params into query string
    query = urllib.parse.urlencode(params)

    return f"{url}?{query}"


def decode_google_token(token: str):
    """Decode the token from google oauth"""
    try:
        payload = jwt.decode(
            token,
            algorithms=AppConfig.OAUTH_TOKEN_ALGORITHM,
            options={"verify_signature": False},
        )
        expiry = payload.get("exp")
        if not expiry or datetime.fromtimestamp(expiry) < datetime.now():
            return None

    except Exception as e:
        logger.warning("Fatal Error. Token verification failed: ", str(e))
        return None

    return GoogleOAuthTokenPayload(**payload)
