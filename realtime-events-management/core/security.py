import datetime
from typing import Optional

import jose
from jose import jwt

from core import settings

def create_access_token(
    data: dict,
    expires_delta: Optional[datetime.timedelta] = settings.ACCESS_TOKEN_EXPIRE_MINUTES
):
    to_encode = data.copy()
    expire = datetime.datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        return user_id
    except jose.JWTError:
        return None