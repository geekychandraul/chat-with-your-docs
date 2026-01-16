from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import settings
from app.core.db.database import Base
from app.models import *  # noqa

# from app.orm.models import mapper_registry

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option("sqlalchemy.url", settings.ALEMBIC_DATABASE_URI)
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_name(name, type_, parent_names):
    """Determine whether an object name should be included in autogenerate.

    Args:
        name (str): the object name (table, schema, etc.).
        type_ (str): the type of object (e.g. "schema").
        parent_names (Sequence[str]): parent names for the object.

    Returns:
        bool: True if the object should be included for migrations.
    """
    if type_ == "schema":
        return name == settings.POSTGRES_DB_SCHEMA
    return True


def run_migrations_offline() -> None:
    """Run Alembic migrations in 'offline' mode.

    This configures the migration context with only the URL and emits
    SQL statements to stdout without creating a DBAPI connection.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        include_schemas=True,
        include_name=include_name,
        version_table_schema=settings.POSTGRES_DB_SCHEMA,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # this callback is used to prevent an auto-migration from being generated
    # when there are no changes to the schema
    # reference: http://alembic.zzzcomputing.com/en/latest/cookbook.html
    def process_revision_directives(context, revision, directives):
        """Drop generated revision directives if there are no schema changes.

        When autogenerate is requested and there are no upgrade operations,
        this prevents creation of an empty migration file by clearing the
        directives list.
        """
        if getattr(config.cmd_opts, "autogenerate", False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # process_revision_directives=process_revision_directives,
            include_schemas=True,
            include_name=include_name,
            version_table_schema=settings.POSTGRES_DB_SCHEMA,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
