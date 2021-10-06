from fastapi import FastAPI

from fastapi_todos.api.todo import router as todo_router
from fastapi_todos.database import init_database


def create_app() -> FastAPI:
    app = FastAPI()
    app.include_router(todo_router)

    # https://sqlmodel.tiangolo.com/tutorial/fastapi/simple-hero-api/#create-database-and-tables-on-startup
    @app.on_event("startup")
    async def startup() -> None:
        init_database()

    return app
