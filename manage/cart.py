from pathlib import Path
import random

# import aiofiles

from typing_extensions import Annotated

import typer

import asyncio

from project.database.dao_cart_util import add_update_delete_cart_item, clear_cart_items_table, get_all_cards
from project.database.dao_users_util import get_users_names
from project.schemas_cart import SCartItemDbOut, SCartItemIn
from project.schemas_products import (
    SProductSummaryOutByer,
)
from manage.utils import save_list_to_json_file
from project.service_store import get_products_summary_for_byer

CART_ITEMS_FILE = "manage/cart_items.json"


app = typer.Typer()


async def generate_cart_items(average_item_amount: int) -> list[SCartItemDbOut]:
    await clear_cart_items_table()
    users_names: list[str] = await get_users_names()
    nomenclatures: list[SProductSummaryOutByer] = await get_products_summary_for_byer()
    items_overal_amount: int = average_item_amount * len(users_names)

    cart_items_gen = (
        SCartItemIn(
            nom_id=n.id,
            quantity=int(n.total_remainder / average_item_amount),
            username=random.choice(users_names),
        )
        for n in (random.choice(nomenclatures) for _ in range(items_overal_amount))
    )

    for item in cart_items_gen:
        await add_update_delete_cart_item(item)
    
    return await get_all_cards()


@app.command()
def generate(
    amount: Annotated[
        int, typer.Option(help="average amount of cart items on one user")
    ] = 3,
    out_file: Annotated[
        Path,
        typer.Option(
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
            help="path to cart items file",
        ),
    ] = Path(CART_ITEMS_FILE),
) -> None:
    """
    1. clear CartItems table
    2. select users and symmary of nomenclature
    3. select random user and random nomenclature and insert cart item whit quantity=nomenclature.quantit/--amount
    4. select CartItems table and save data to --out-file
    """
    typer.echo(f"generating card items...")
    items = asyncio.run(generate_cart_items(amount))
    typer.echo("cart items generated")
    typer.echo(f"saving card items to file {out_file}...")
    save_list_to_json_file(out_file, items, SCartItemDbOut)
    typer.echo(f"items saved to file")
