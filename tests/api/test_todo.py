from datetime import datetime, timedelta
from typing import AsyncGenerator

from fastapi.testclient import TestClient
from pytest import fixture
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

from fastapi_todos.app import create_app
from fastapi_todos.database import get_session

# tests with FastAPI + SQLModel
# https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/


# fixture: https://docs.pytest.org/en/stable/fixture.html
@fixture(name="session")
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    session_maker = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with session_maker() as session:
        yield session


def test_create(session: AsyncSession) -> None:
    app = create_app()

    # dependency injection in fastapi:
    # https://sqlmodel.tiangolo.com/tutorial/fastapi/tests/#create-the-engine-and-session-for-testing
    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    title = "test1"

    response = client.get("/todo/view")
    assert response.status_code == 200
    assert len(response.json()) == 0

    response = client.post("/todo/create", json={"title": title})
    assert response.status_code == 200

    response = client.get("/todo/view")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == title


def test_update(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    title = "test1"
    response = client.post("/todo/create", json={"title": title})
    assert response.status_code == 200
    todo_id = response.json()["id"]

    response = client.get(f"/todo/show/{todo_id}")
    assert response.status_code == 200
    assert not response.json()["finished"]

    response = client.patch(f"/todo/update/{todo_id}", json={"finished": True})
    assert response.status_code == 200

    response = client.get(f"/todo/show/{todo_id}")
    assert response.status_code == 200
    assert response.json()["finished"]


def test_update_when_record_is_not_found(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.patch("/todo/update/1", json={"title": "updated"})
    assert response.status_code == 404


def test_view(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    client.post("/todo/create", json={"title": "test1"})
    client.post("/todo/create", json={"title": "test2"})
    client.post("/todo/create", json={"title": "test3"})

    response = client.get("/todo/view")
    assert response.status_code == 200
    assert len(response.json()) == 3


def test_view_with_created_at(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    now = datetime.now() - timedelta(hours=9)
    client.post("/todo/create", json={"title": "test1"})
    client.post("/todo/create", json={"title": "test2"})
    response = client.post("/todo/create", json={"title": "test3"})
    todo_id = response.json()["id"]

    response = client.get("/todo/view")
    assert response.status_code == 200
    assert len(response.json()) == 3

    created_at = now - timedelta(days=1)
    created_at_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    client.patch(f"/todo/update/{todo_id}", json={"title": "updated", "created_at": created_at_str})

    response = client.get("/todo/view")
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get("/todo/view", headers={"Created-At": now.strftime("%Y-%m-%d %H:%M:%S")})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_show(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    title = "test1"

    response = client.post("/todo/create", json={"title": title})
    todo_id = response.json()["id"]

    response = client.get(f"/todo/show/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == title


def test_show_when_record_is_not_found(session: AsyncSession) -> None:
    app = create_app()

    app.dependency_overrides[get_session] = lambda: session
    client = TestClient(app)

    response = client.get("/todo/show/1")
    assert response.status_code == 404
