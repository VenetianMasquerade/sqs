from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from sqlalchemy import Column, String, Integer, Boolean, DateTime, LargeBinary, ForeignKey
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./test.db"
Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

# Cached Minecraft Login from Crafty.gg
class MinecraftLogin(Base):
    __tablename__ = "minecraft_logins"

    id = Column(String, primary_key=True)  # crafty's id
    uuid = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False, index=True)
    type = Column(String)
    version = Column(Integer)
    deleted = Column(Boolean)
    upvotes_lifetime = Column(Integer)
    views_lifetime = Column(Integer)
    user_id = Column(String)
    location_id = Column(String)
    claimed_at = Column(DateTime)
    created_at = Column(DateTime)
    skins_count = Column(Integer)
    capes_count = Column(Integer)
    bio = Column(String)
    color = Column(String)
    upvotes_monthly = Column(Integer)
    views_monthly = Column(Integer)
    # We store skins as JSON string if needed; for simplicity we store the first skin image separately.
    skin = relationship("Skin", back_populates="minecraft_login", uselist=False)

# Cached Skin image
class Skin(Base):
    __tablename__ = "skins"

    id = Column(String, primary_key=True)
    username = Column(String, ForeignKey("minecraft_logins.username"), unique=True)
    image_data = Column(LargeBinary)  # store raw PNG binary
    cached_at = Column(DateTime, default=datetime.utcnow)

    minecraft_login = relationship("MinecraftLogin", back_populates="skin")

engine = create_async_engine(DATABASE_URL)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get async session

    :return: Async session handle
    """
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

