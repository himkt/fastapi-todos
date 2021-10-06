from datetime import datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    finished: bool = False
    # https://github.com/tiangolo/sqlmodel/issues/21
    created_at: datetime = Field(
        default=None,
        sa_column=(Column(DateTime(timezone=True), server_default=func.now())),
    )
