
import typer

from manage.init import app as init_app
from manage.users import app as users_app
from manage.products import app as products_app
from manage.cart import app as cart_app

app = typer.Typer()
app.add_typer(init_app, name="init", rich_help_panel="Subcommand")
app.add_typer(users_app, name="users", rich_help_panel="Subcommand")
app.add_typer(products_app, name="products", rich_help_panel="Subcommand")
app.add_typer(cart_app, name="cart", rich_help_panel="Subcommand")


if __name__ == "__main__":
    app()
