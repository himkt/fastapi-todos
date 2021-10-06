from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func
from sqlmodel import Field, SQLModel


class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    finished: bool = False
    # https://github.com/tiangolo/sqlmodel/issues/21
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=(Column(DateTime(timezone=True), server_default=func.now())),
    )
