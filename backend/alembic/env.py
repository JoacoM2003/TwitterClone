from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app.db.base import Base
from app.models import user, tweet, follow  # Importar todos los modelos
from app.core.config import settings

# Configurar target_metadata
target_metadata = Base.metadata

def run_migrations_online():
    configuration = context.config
    configuration.set_main_option("sqlalchemy.url", settings.database_url)
    
    connectable = engine_from_config(
        configuration.get_section(configuration.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()