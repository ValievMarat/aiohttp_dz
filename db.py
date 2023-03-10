import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# PG_DSN = 'postgresql+asyncpg://app:app@127.0.0.1:5432/advertisement'
PG_DSN = 'postgresql+asyncpg://app:app@db:5432/advertisement'
engine = create_async_engine(PG_DSN)
Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()


class User(Base):

    __tablename__ = 'app_users'

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    username = sq.Column(sq.String, nullable=False, unique=True, index=True)
    password = sq.Column(sq.String, nullable=False)
    mail = sq.Column(sq.String, nullable=False)
    created_at = sq.Column(sq.DateTime, server_default=sq.func.now())


class Advert(Base):

    __tablename__ = 'app_adverts'
    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    caption = sq.Column(sq.String(length=100), nullable=False)
    description = sq.Column(sq.Text, nullable=False)
    created_at = sq.Column(sq.DateTime, server_default=sq.func.now())
    owner_id = sq.Column(sq.Integer, sq.ForeignKey("app_users.id"), nullable=False)
