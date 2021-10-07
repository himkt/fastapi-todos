from datetime import datetime
from typing import List, Optional, Union

import fastapi
from fastapi.params import Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from fastapi_todos.database import get_session
from fastapi_todos.model.todo import Todo

router = fastapi.APIRouter()


@router.post("/todo/create")
async def create(
    todo: Todo,
    # https://github.com/tiangolo/fastapi/issues/1522
    # https://github.com/tiangolo/fastapi/issues/219
    session: AsyncSession = Depends(get_session),  # type: ignore  # noqa: B008
) -> JSONResponse:

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return JSONResponse(
        status_code=200,
        content={
            "id": todo.id,
            "message": f"{todo.title} is successfully added",
        },
    )


@router.get("/todo/show/{id}")
async def show(
    id: int,
    session: AsyncSession = Depends(get_session),  # type: ignore  # noqa: B008
) -> Union[JSONResponse, Todo]:

    # https://sqlmodel.tiangolo.com/tutorial/select/
    statement = select(Todo).where(Todo.id == id)
    response = await session.execute(statement)

    # https://sqlmodel.tiangolo.com/tutorial/one/
    record = response.first()
    if record is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"Todo #{id} is not found."},
        )

    return record


class UpdateTodo(BaseModel):
    title: Optional[str]
    finished: Optional[bool]
    created_at: Optional[datetime]


@router.patch("/todo/update/{id}")
async def update(
    id: int,
    update_param: UpdateTodo,
    session: AsyncSession = Depends(get_session),  # type: ignore  # noqa: B008
) -> Todo:

    statement = select(Todo).where(Todo.id == id)
    response = await session.execute(statement)

    todo = response.fetchone()
    if todo is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"Todo #{id} is not found."},
        )

    if update_param.title is not None:
        todo.title = update_param.title

    if update_param.finished is not None:
        todo.finished = update_param.finished

    if update_param.created_at is not None:
        todo.created_at = update_param.created_at

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return todo


@router.get("/todo/view", response_model=List[Todo])
async def view(
    session: AsyncSession = Depends(get_session),  # type: ignore  # noqa: B008
    # https://fastapi.tiangolo.com/tutorial/header-params/
    created_at: str = Header(None),  # type: ignore  # noqa: B008
) -> List[Todo]:

    statement = select(Todo)
    if created_at is not None:
        _created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
        statement = statement.where(Todo.created_at >= _created_at)

    response = await session.execute(statement)
    records = response.fetchall()
    return records
