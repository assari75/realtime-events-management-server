from sqlalchemy import orm as sa_orm
from passlib import context as passlib_context

from core import database

__all__ = ["User"]

pwd_context = passlib_context.CryptContext(schemes=["sha256_crypt"])


class User(database.Base):
    __tablename__ = 'users'

    id: sa_orm.Mapped[int] = sa_orm.mapped_column(primary_key=True)
    username: sa_orm.Mapped[str]
    password: sa_orm.Mapped[str]
    name: sa_orm.Mapped[str]

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name})>"
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)
