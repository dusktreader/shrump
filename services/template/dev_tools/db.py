import json
import subprocess

import docker_gadgets
import typer
from loguru import logger

from alembic.command import revision as sqla_migrate
from alembic.command import upgrade as sqla_upgrade
from alembic.command import downgrade as sqla_downgrade
from alembic.config import Config

from api.config import settings
from api.storage import build_db_url

app = typer.Typer()


@app.command()
def login(test: bool = typer.Option(False, help="Log into the test database.")):
    """Log into a local database."""
    url = build_db_url(force_test=test, asynchronous=False)
    logger.debug(f"Logging into database: {url}")
    subprocess.run(["pgcli", url])


@app.command()
def migrate(
    message: str = typer.Option("Unlabeled migration", help="The message to attach to the migration."),
    blank: bool = typer.Option(False, help="Produce a blank migration"),
):
    """Create alembic migrations for a local database."""
    logger.debug(f"Creating migration with message: {message}")
    config = Config(file_="alembic/alembic.ini")
    sqla_migrate(config, message=message, autogenerate=not blank)


@app.command()
def upgrade(target: str = typer.Option("head", help="The migration to which the db should be upgraded.")):
    """Apply alembic migrations to a local database."""
    logger.debug("Upgrading database...")

    config = Config(file_="alembic/alembic.ini")
    sqla_upgrade(config, target)


@app.command()
def downgrade(target: str = typer.Option("-1", help="The migration to which the db should be downgraded.")):
    """Revert alembic migrations to a local database."""
    logger.debug("Downgrading database...")

    config = Config(file_="alembic/alembic.ini")
    sqla_downgrade(config, target)


@app.command()
def start(test: bool = typer.Option(False, help="Start a test database.")):
    """Start a local postgres database for local development."""
    name = "dev-shrump-pin-writer-postgres"
    kwargs = dict(
        image="postgres:17-alpine",
        env=dict(
            POSTGRES_PASSWORD=settings.DATABASE_PSWD,
            POSTGRES_DB=settings.DATABASE_NAME,
            POSTGRES_USER=settings.DATABASE_USER,
        ),
        ports={"5432/tcp": settings.DATABASE_PORT},
    )
    if test:
        kwargs.update(
            env=dict(
                POSTGRES_PASSWORD=settings.TEST_DATABASE_PSWD,
                POSTGRES_DB=settings.TEST_DATABASE_NAME,
                POSTGRES_USER=settings.TEST_DATABASE_USER,
            ),
            ports={"5432/tcp": settings.TEST_DATABASE_PORT},
            tmpfs={"/var/lib/postgresql/data": "rw"},
        )
        name = "test-shrump-pin-writer-postgres"

    logger.debug(f"Starting {name} with:\n {json.dumps(kwargs, indent=2)}")

    docker_gadgets.start_service(name, **kwargs)


@app.command()
def start_all():
    """Start all local databases."""
    start()
    start(test=True)


@app.command()
def stop(test: bool = typer.Option(False, help="Stop a test database.")):
    """Stop a local postgres database."""
    name = "dev-shrump-pin-writer-postgres"
    if test:
        name = "test-shrump-pin-writer-postgres"

    logger.debug(f"Stopping {name}")

    docker_gadgets.stop_service(name)
