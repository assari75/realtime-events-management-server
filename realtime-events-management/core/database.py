import sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from . import settings

engine = sqlalchemy.create_engine(settings.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
