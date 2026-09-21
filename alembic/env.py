from logging.config import fileConfig

from alembic.ddl.impl import DefaultImpl
from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context
from app.config import get_settings
from app.models import Base


class SnowflakeImpl(DefaultImpl):
    """Alembic has no built-in Snowflake DDL dialect; this registers one."""

    __dialect__ = "snowflake"
    transactional_ddl = False

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

get_settings.cache_clear()
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = get_settings().sqlalchemy_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(
        get_settings().sqlalchemy_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
