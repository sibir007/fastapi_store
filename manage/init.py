
import typer

import asyncio

from project.database.dao_users_util import clear_and_resave_permissions
from project.database.dao_util import init_db as async_init_db
from manage.users import app

app = typer.Typer()


async def async_init_db_load_permissions():
    """
    Drop and create db
    """

    typer.echo("initializing db...")
    await async_init_db()
    typer.echo("db initialized")

    # typer.echo("loading permissions...")
    # await load_permissions()
    # typer.echo("permissions loaded")


@app.command()
def init_db():
    """
    Drop and create db
    """
    asyncio.run(async_init_db_load_permissions())


@app.command()
def save_permissions():
    """clear and resave permissions to db"""

    asyncio.run(clear_and_resave_permissions())
