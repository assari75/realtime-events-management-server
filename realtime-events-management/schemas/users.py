from pydantic import BaseModel
from typing import Optional


class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    username: str
    password: str


class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None
