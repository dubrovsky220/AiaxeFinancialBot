import os

from dotenv import load_dotenv, find_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database.model import Base

# Loading environment variables
load_dotenv(find_dotenv())

# Creating database url from values of environment variables
db_url = (
    f'{os.getenv("DB_TYPE")}+{os.getenv("DB_ENGINE")}://{os.getenv("DB_USER")}:{os.getenv("DB_PASSWORD")}\
@{os.getenv("DB_HOST")}:{os.getenv("DB_PORT")}/{os.getenv("DB_NAME")}'
)

# Creating database engine and session maker
engine = create_async_engine(db_url, echo=True)
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    """Creates all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Deletes all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
