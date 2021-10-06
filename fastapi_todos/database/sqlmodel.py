from typing import Iterable

from sqlmodel import Session, SQLModel, create_engine

from fastapi_todos.config import ServerConfiguration


# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/#last-review
def init_database() -> None:
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)


def get_session() -> Iterable[Session]:
    with Session(engine) as session:
        yield session


settings = ServerConfiguration()
engine = create_engine(f"mysql://docker:docker@{settings.MYSQL_HOST}:3306/fastapi_todos")  # noqa


# https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
if __name__ == "__main__":
    init_database()
