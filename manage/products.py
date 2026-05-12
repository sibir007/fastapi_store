from decimal import Decimal
from pathlib import Path
from random import choice, randint, triangular
from typing import Generator, Iterable

# import aiofiles
from faker import Faker
from faker_ecommerce import EcommerceProvider  # type: ignore

from typing_extensions import Annotated

import typer

import asyncio

from project.schemas_products import (
    SNomenclatureOut,
)
from project.database.dao_products_util import (
    add_nomenclatures,
    add_products,
    clear_nomenclature_table,
    get_nomenclatures,
)
from project.schemas_products import SNomenclatureIn, SProductIn, SProsuctDbOutFull
from manage.utils import save_list_to_json_file

PRODUCTS_FILE = "scripts/products.json"
NOMENCLATURE_FILE = "scripts/nomenclature.json"

# for generane prices
AVERAGE_PRICE_MIN = 100
AVERAGE_PRICE_MAX = 20_000
AVERAGE_PRICE_MODE = 1_000

# for generating product
PRODUCT_AMMOUNT_MIN = 1
PRODUCT_AMMOUNT_MAX = 20
AVERAGE_PRICE_DEVIATION = 0.15


app = typer.Typer()


fake = Faker()
fake.add_provider(EcommerceProvider)


# async def _load_products(products_file: str | Path) -> list[SProductOut]:
#     # Opens the file without blocking the event loop
#     # async with aiofiles.open('example.txt', mode='w') as f:
#     #     await f.write('Hello, Async world!')

#     async with aiofiles.open(products_file, mode="r") as f:
#         proudcts = await f.read()
#     products_list: list[dict[str, Any]] = json.loads(proudcts)
#     return await create_products(
#         (
#             SProductIn(
#                  **product
#             )
#             for product in products_list
#         )
#     )


# @app.command()
# def load_products(
#     products_file: Annotated[
#         Path,
#         typer.Option(
#             exists=True,
#             file_okay=True,
#             dir_okay=False,
#             writable=False,
#             readable=True,
#             resolve_path=True,
#             help="path where seved products",
#         ),
#     ] = Path(PRODUCTS_FILE),
# ):
#     """Load products from json file to db"""
#     typer.echo("loading products...")
#     asyncio.run(_load_products(products_file))
#     typer.echo("products loaded")


class SNomenclatureOutAv(SNomenclatureOut):
    average_price: float


def _generate_nomenclature(ammount: int) -> Generator[SNomenclatureIn, None, None]:

    nomenclature: Generator[SNomenclatureIn, None, None] = (
        SNomenclatureIn(
            name=fake.product_name(include_brand=True),
            description=fake.product_description(),
        )
        for _ in range(ammount)
    )

    return nomenclature


def _generate_products(
    nomenclature: list[SNomenclatureOut], number_deliveries: int
) -> Generator[SProductIn, None, None]:
    nom_av_list: list[SNomenclatureOutAv] = add_average_price(nomenclature)
    deliver_overal = range(len(nomenclature) * number_deliveries)
    random_nom = (choice(nom_av_list) for _ in deliver_overal)
    products: Generator[SProductIn, None, None] = (
        SProductIn(
            cost_price=_get_random_cost_price(n), quantity=randint(PRODUCT_AMMOUNT_MIN, PRODUCT_AMMOUNT_MAX), nom_id=n.id
        )
        for n in random_nom
    )

    return products


def _get_random_cost_price(nomenclature: SNomenclatureOutAv):
    cost_price = Decimal(
        triangular(
            float(nomenclature.average_price * (1 - AVERAGE_PRICE_DEVIATION)),
            float(nomenclature.average_price * (1 + AVERAGE_PRICE_DEVIATION)),
            float(nomenclature.average_price),
        )
    ).quantize(Decimal("1.00"))

    return cost_price


async def generate_products(
    nomenclature_amount: int,
    number_deliveries: int,
) -> tuple[list[SProsuctDbOutFull], list[SNomenclatureOut]]:
    typer.echo("clearing Products and Nomenclatur tables")
    await clear_nomenclature_table()
    # await clear_product_table()
    typer.echo(f"generating nomenclature...")
    nom_in: Generator[SNomenclatureIn, None, None] = _generate_nomenclature(
        nomenclature_amount
    )
    typer.echo(f"nomenclature generated")
    typer.echo("saving nomenclature to db...")
    nom_out: list[SNomenclatureOut] = await add_nomenclatures(nom_in)
    typer.echo("nomenclature saved")
    typer.echo("generating products...")
    prod_in: Generator[SProductIn, None, None] = _generate_products(
        nom_out, number_deliveries
    )
    typer.echo("products generaded")
    typer.echo("saving products to db...")
    prod_out: list[SProsuctDbOutFull] = await add_products(prod_in)
    typer.echo("product saved")
    typer.echo("select nomenclature from db...")
    nom_out = await get_nomenclatures()
    typer.echo(f"nomenclsture selected")
    return prod_out, nom_out


@app.command()
def generate(
    nomenclature_amount: Annotated[
        int, typer.Option(help="amount of nomenclature items to generate")
    ] = 10,
    number_deliveries: Annotated[
        int, typer.Option(help="average quantity of deliveries of each nomenclature")
    ] = 5,
    nomenclature_out_file: Annotated[
        Path,
        typer.Option(
            exists=True,
            file_okay=True,
            dir_okay=False,
            writable=False,
            readable=True,
            resolve_path=True,
            help="path to nomenclature file",
        ),
    ] = Path(NOMENCLATURE_FILE),
    products_out_file: Annotated[
        Path,
        typer.Option(
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
            help="path to save products",
        ),
    ] = Path(PRODUCTS_FILE),
) -> None:
    """
    0. clear Proucts and Nomenclature tables
    1. generate random products nomenclature --nomenclature-amount, save it to db,
    on returned items additionally sets an average price, which is used to generate
    individual deliveries of products.
    2. calculates the total number of product deliveries as:
    number of nomenclature items * average quantity of deliveries of each nomenclature
    (--number-deliveries),
    3. generates products by random read nomenclature item  with
    random cost price based on the average price of the nomenclature item
    and save it to db
    4. save products to json file --products-out-file
    5. read nomenclature from db and save it to json file --nomenclature-out-file
    """

    products_out_db, nom_out_db = asyncio.run(
        generate_products(nomenclature_amount, number_deliveries)
    )
    typer.echo(f"saving products to file {products_out_file}...")
    save_list_to_json_file(products_out_file, products_out_db, SProsuctDbOutFull)
    typer.echo(f"products saved to file")
    typer.echo(f"saving nomenclature to file {nomenclature_out_file}...")
    save_list_to_json_file(nomenclature_out_file, nom_out_db, SNomenclatureOut)
    typer.echo(f"nomenclature saved to file")


async def async_save_nomenclature_to_db(
    nomenclature: Iterable[SNomenclatureIn],
) -> list[SNomenclatureOut]:
    typer.echo(f"clearing nomenclature table...")
    await clear_nomenclature_table()
    typer.echo(f"nomenclature table cleared")
    typer.echo(f"saving nomenclature to db...")
    return await add_nomenclatures(nomenclature)


# @app.command()
def generate_nomenclature(
    amount: Annotated[
        int, typer.Option(help="amount of nomenclature items to generate")
    ] = 10,
    out_file: Annotated[
        Path,
        typer.Option(
            exists=False,
            file_okay=True,
            dir_okay=False,
            writable=True,
            readable=True,
            resolve_path=True,
            help="path to save nomenclature",
        ),
    ] = Path(NOMENCLATURE_FILE),
) -> None:
    """Generate random products nomenclature, save it to db and json file
    additionally sets an average price, which is used to generate
    individual deliveries of products
    """
    typer.echo(f"generating nomenclature...")
    nomenclature: Generator[SNomenclatureIn, None, None] = _generate_nomenclature(
        amount
    )
    typer.echo(f"generating nomenclature complite")
    typer.echo(f"saving nomenclature to db...")
    nomenclature_out_db: list[SNomenclatureOut] = asyncio.run(
        async_save_nomenclature_to_db(nomenclature)
    )
    typer.echo(f"nomenclature saved to db")

    nomenclature_out_db_av = add_average_price(nomenclature_out_db)
    save_list_to_json_file(out_file, nomenclature_out_db_av, SNomenclatureOutAv)
    typer.echo(f"nomenclature stored")


def add_average_price(nomenclature_out_db: Iterable[SNomenclatureOut]):
    nomenclature_out_db_av: list[SNomenclatureOutAv] = [
        SNomenclatureOutAv(
            **n.model_dump(),
            average_price=round(
                triangular(AVERAGE_PRICE_MIN, AVERAGE_PRICE_MAX, AVERAGE_PRICE_MODE), 2
            ),
        )
        for n in nomenclature_out_db
    ]

    return nomenclature_out_db_av
