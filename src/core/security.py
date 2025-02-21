import jwt
import random
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from src.core.config import AppConfig
from src.models.user import TokenPayload
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
