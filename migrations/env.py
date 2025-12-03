from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import AsyncEngine
from alembic import context
import asyncio

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# IMPORTANT: Import your Base object and all model files here.
# This ensures that Alembic's autogenerate feature can see all your tables.
from app.core.database import Base, engine
from app.models.user import User, Address
from app.models.product import Category, Subcategory, Product
from app.models.offers import Offer
from app.models.order import Order, OrderItem

target_metadata = Base.metadata

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine

    if isinstance(connectable, AsyncEngine):
        # We need to run the migration inside an async context.
        # This is the correct way to do it.
        asyncio.run(do_run_migrations_async(connectable))
    else:
        # Fallback for synchronous engines
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()

async def do_run_migrations_async(connectable):
    """Asynchronous function to configure and run migrations."""
    # This is a key step: We get a connection from the engine first.
    async with connectable.connect() as connection:
        # Now we can run the synchronous migration logic on the connection.
        # The extra `connection` argument has been removed here.
        await connection.run_sync(do_run_migrations)

def do_run_migrations(connection):
    """Synchronous function that configures and runs migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Main entry point to start the migration process
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
