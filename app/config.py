from functools import lru_cache

from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict
from snowflake.sqlalchemy import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    snowflake_account: str
    snowflake_user: str
    snowflake_password: str
    snowflake_database: str
    snowflake_schema: str = "PUBLIC"
    snowflake_warehouse: str
    snowflake_role: str = ""
    secret_key: str
    access_token_ttl_seconds: int = 90  # was 900
    refresh_token_ttl_seconds: int = 604800

    def sqlalchemy_url(self) -> str:
        kwargs: dict[str, str] = {
            "account": self.snowflake_account,
            "user": self.snowflake_user,
            "password": self.snowflake_password,
            "database": self.snowflake_database,
            "schema": self.snowflake_schema,
            "warehouse": self.snowflake_warehouse,
        }
        if self.snowflake_role:
            kwargs["role"] = self.snowflake_role
        return URL(**kwargs)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
