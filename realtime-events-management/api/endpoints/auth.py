import datetime

import fastapi
from fastapi import security as fastapi_security
from fastapi import status as fastapi_status
from sqlalchemy import orm as sa_orm

from core import database, settings, security
from models import users as users_model
from schemas import users as users_schema

router = fastapi.APIRouter()

@router.post("/register", response_model=users_schema.User)
def register_user(user: users_schema.UserCreate, db: sa_orm.Session = fastapi.Depends(database.get_db)):
    db_user = db.query(users_model.User).filter(users_model.User.username == user.username).first()
    if db_user:
        raise fastapi.HTTPException(
            status_code=400,
            detail="Email or username already registered"
        )

    hashed_password = users_model.User.get_password_hash(user.password)
    db_user = users_model.User(
        username=user.username,
        password=hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/token", response_model=users_schema.Token)
def login_for_access_token(
    form_data: fastapi_security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: sa_orm.Session = fastapi.Depends(database.get_db)
):
    user = db.query(users_model.User).filter(users_model.User.username == form_data.username).first()
    if not user or not users_model.User.verify_password(form_data.password, user.password):
        raise fastapi.HTTPException(
            status_code=fastapi_status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}