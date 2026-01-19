import sys
from logging.config import fileConfig
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from backend.cfg.cfg import settings
from backend.src.app.domain.models.db import Base

project_root = Path(__file__).resolve().parents[1]
sys.path.append(str(project_root))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
# noinspection PyTypeChecker
def _build_sync_url(async_url: str) -> str:
    """
    Build a sync SQLAlchemy URL for Alembic migrations.

    :param async_url: async SQLAlchemy URL

    :return: sync SQLAlchemy URL
    """
    parsed = urlparse(async_url)
    scheme = parsed.scheme.replace("+aiomysql", "+pymysql")
    return urlunparse(parsed._replace(scheme=scheme))


config.set_main_option("sqlalchemy.url", _build_sync_url(async_url=settings.database.url))


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    This configures the context with just a URL and not an Engine, though
    an Engine is acceptable here as well. By skipping the Engine creation,
    no DBAPI needs to be available.

    Calls to ``context.execute()`` here emit the given string to the
    script output.

    :return: None
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    In this scenario the code creates an Engine and associates a
    connection with the context.

    :return: None
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
