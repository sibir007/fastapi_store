
import typer

from scripts.init import app as init_app
from scripts.users import app as users_app
from scripts.products import app as products_app

app = typer.Typer()
app.add_typer(init_app, name="init", rich_help_panel="Subcommand")
app.add_typer(users_app, name="users", rich_help_panel="Subcommand")
app.add_typer(products_app, name="products", rich_help_panel="Subcommand")


if __name__ == "__main__":
    app()
