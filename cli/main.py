import asyncio
import typer
from rich.console import Console
import yaml
from .models import Recipe
from .installer import install_recipe

console = Console()

app = typer.Typer()


@app.command()
def install(local: str = typer.Option(None, "--local", "-l")):
    if local:
        with open(local) as file:
            data = yaml.safe_load(file)
            recipe = Recipe(**data)
            console.print(f"Succesfully loaded: {recipe}")

        asyncio.run(install_recipe(recipe))


if __name__ == "__main__":
    app()
