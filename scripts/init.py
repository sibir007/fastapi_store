
import typer

import asyncio

from project.database.dao_util import init_db as async_init_db

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
