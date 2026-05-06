import json
from pathlib import Path
from typing import Any


import aiofiles
from faker import Faker

from typing_extensions import Annotated

import typer

# from project.database.session import async_session_maker
from project.auth_lib import get_password_hash
from project.auth_schemas import SPermissionIn, UserIn, UserInDB, UserOut

# from project.database.session import async_session_maker
from project.database.dao_util import (
    create_update_superuser,
    init_db,
    load_permissions,
    create_users as async_load_users,
)
import asyncio

# logger = logger.getLogger(__name__)


USER_FILE = "scripts/users.json"

fake = Faker()

app = typer.Typer()


# users =


async def _add_permissions_to_user(username: str, permission: SPermissionIn):

    pass


async def _load_users(users_file: str | Path) -> list[UserOut]:
    # Opens the file without blocking the event loop
    # async with aiofiles.open('example.txt', mode='w') as f:
    #     await f.write('Hello, Async world!')

    async with aiofiles.open(users_file, mode="r") as f:
        users = await f.read()
    users_list: list[dict[str, Any]] = json.loads(users)
    return await async_load_users(
        (
            UserInDB(
                hashed_password=get_password_hash(user.get("password", "")), **user
            )
            for user in users_list
        )
    )


@app.command()
def load_users(
    users_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="path when save users",
        ),
    ] = Path(USER_FILE),
):
    """Load users from json file to db"""
    typer.echo("loading users...")
    asyncio.run(_load_users(users_file))
    typer.echo("users loaded")



async def async_init_db_load_permissions():
    """
    Drop and create db, load permissions
    """

    typer.echo("initializing db...")
    await init_db()
    typer.echo("db initialized")

    typer.echo("loading permissions...")
    await load_permissions()
    typer.echo("permissions loaded")


@app.command()
def init_db_load_permissions():
    """
    Drop and create db, load permissions
    """
    asyncio.run(async_init_db_load_permissions())


async def async_create_superuser(email: str, password: str) -> UserOut:
    """
    create superuser (update if exists), add all permissions, username always "superuser"
    """
    superuser = UserInDB(
        username="superuser",
        full_name="Super User",
        email=email,
        hashed_password=get_password_hash(password),
    )
    return await create_update_superuser(superuser)


@app.command()
# app.command(help="delete superuser, create new superuser, add add superuser permissions")
def create_superuser(
    email: Annotated[str, typer.Option(prompt="Email of the superuser")],
    password: Annotated[
        str,
        typer.Option(
            prompt=True,
            confirmation_prompt=True,
            hide_input=True,
            help="Password for the superuser",
        ),
    ],
):
    """
    create superuser (update if exists), add all permissions, username always "superuser"
    """
    # print(f"email: {email}")
    # print(f"password: {password}")
    su = asyncio.run(async_create_superuser(email, password))
    typer.echo(f"superuser created: {su}")


def _gen_users(ammount: int) -> list[UserIn]:

    users = [
        UserIn(
            username=p.get("username"),  # type: ignore
            full_name=p.get("name"),  # type: ignore
            email=p.get("mail"),  # type: ignore
            password=fake.password(length=7),
        )
        for p in (fake.profile() for _ in range(ammount))
    ]

    return users


@app.command(help="generate random users,load to json file")
def gen_users(
    amount: Annotated[int, typer.Option(help="amount of users to generate")] = 10,
    out_file: Annotated[
        Path,
        typer.Option(
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
            help="path to save users",
        ),
    ] = Path(USER_FILE),
) -> None:
    print(f"amount: {amount}")
    print(f"path: {out_file}")
    users: list[UserIn] = _gen_users(amount)
    users_json = json.dumps([user.model_dump() for user in users], indent=4)
    with out_file.open("w") as f:
        f.write(users_json)


if __name__ == "__main__":
    app()
