import fastapi
from fastapi import security as fastapi_security
from fastapi import status as fastapi_status
from sqlalchemy import orm as sa_orm

from core import database
from core import security
from models import users

oauth2_scheme = fastapi_security.OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(
    token: str = fastapi.Depends(oauth2_scheme),
    db: sa_orm.Session = fastapi.Depends(database.get_db)
) -> users.User:
    credentials_exception = fastapi.HTTPException(
        status_code=fastapi_status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    user_id = security.verify_token(token)
    if user_id is None:
        raise credentials_exception
        
    user = db.query(users.User).filter(users.User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    return user
