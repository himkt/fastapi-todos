from functools import lru_cache

import pydantic


# https://pydantic-docs.helpmanual.io/usage/settings/
class ServerConfiguration(pydantic.BaseSettings):
    MYSQL_HOST: str = "127.0.0.1"


# https://fastapi.tiangolo.com/advanced/settings/#settings-in-a-dependency
@lru_cache
def get_settings() -> ServerConfiguration:
    return ServerConfiguration()
