import json
from pathlib import Path

from typing import Any


import aiofiles
from faker import Faker
from faker_ecommerce import EcommerceProvider  # type: ignore

from typing_extensions import Annotated

import typer
from project.lib_auth import get_password_hash
from project.schemas_auth import SUserIn, SUserInDB, SUserOut
from project.database.dao_users_util import (
    create_update_superuser,
    clear_users_table,
    create_users,
)
import asyncio

from manage.utils import save_list_to_json_file

# logger = logger.getLogger(__name__)


USER_FILE = "manage/users.json"

fake = Faker()

app = typer.Typer()


async def save_users_to_db(users_file: str | Path) -> list[SUserOut]:
    # Opens the file without blocking the event loop
    # async with aiofiles.open('example.txt', mode='w') as f:
    #     await f.write('Hello, Async world!')
    typer.echo("Clearing users table...")
    await clear_users_table()
    typer.echo("users table cleread")
    typer.echo(f"loading users from {users_file} ...")
    async with aiofiles.open(users_file, mode="r") as f:
        users = await f.read()
    users_list: list[dict[str, Any]] = json.loads(users)
    typer.echo("users loaded")
    typer.echo("saving users to db...")
    return await create_users(
        (
            SUserInDB(
                hashed_password=get_password_hash(user.get("password", "")), **user
            )
            for user in users_list
        )
    )


@app.command()
def save(
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
    """Clear User table, load users from json file, save loaded users to db"""

    asyncio.run(save_users_to_db(users_file))
    typer.echo("users saved")


async def async_create_superuser(email: str, password: str) -> SUserOut:
    """
    create superuser (update if exists), add all permissions, username always "superuser"
    """
    superuser = SUserInDB(
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


def gentrate_users(ammount: int) -> list[SUserIn]:

    users = [
        SUserIn(
            username=p.get("username"),  # type: ignore
            full_name=p.get("name"),  # type: ignore
            email=p.get("mail"),  # type: ignore
            password=fake.password(length=7),
        )
        for p in (fake.profile() for _ in range(ammount))
    ]

    return users


@app.command(help="generate random users,save to json file")
def generate(
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
    users: list[SUserIn] = gentrate_users(amount)
    save_list_to_json_file(out_file, users, SUserIn)


