from __future__ import with_statement

import logging
from logging.config import fileConfig
import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from dotenv import load_dotenv

# ✅ Load environment variables from .env
load_dotenv()

# ✅ Get the DATABASE_URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("❌ ERROR: DATABASE_URL is not set in the environment!")

# ✅ Alembic Config object (Provides access to .ini file values)
config = context.config

# ✅ Set the database URL dynamically in Alembic config
config.set_main_option("sqlalchemy.url", database_url)

# ✅ Setup logging
fileConfig(config.config_file_name)
logger = logging.getLogger("alembic.env")

# ✅ Import models and metadata for migrations
from models import db
target_metadata = db.metadata  # ✅ Correct way to get metadata

# ------------------------------
# ✅ Run Migrations in OFFLINE Mode
# ------------------------------
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


# ------------------------------
# ✅ Run Migrations in ONLINE Mode
# ------------------------------
def run_migrations_online():
    """Run migrations in 'online' mode."""

    # ✅ Create an engine manually instead of relying on Flask
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


# ✅ Determine migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
