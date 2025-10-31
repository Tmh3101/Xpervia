from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app import config

class Base(DeclarativeBase):
    pass

engine = create_engine(config.DATABASE_URL_ASYNC, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)