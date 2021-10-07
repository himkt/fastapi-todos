from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi_todos.config import ServerConfiguration


# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#last-review
# https://testdriven.io/blog/fastapi-sqlmodel/
async def init_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


settings = ServerConfiguration()
engine = create_async_engine(
    f"mysql+aiomysql://docker:docker@{settings.MYSQL_HOST}:3306"
    "/fastapi_todos",
    future=True
)
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
if __name__ == "__main__":
    init_database()
