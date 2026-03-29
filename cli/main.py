"""Command-Line Interface for OpenSound.

Serves as the main entry point to install packages via recipes
using the Typer framework.
"""

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
    """Install a sound package from a local recipe.

    Args:
        local: An optional path pointing to a local .yaml recipe file.
            If provided, the system parses the YAML, validates it into a Recipe,
            and attempts an automated download and installation of targets.
    """
    if local:
        with open(local) as file:
            data = yaml.safe_load(file)
            recipe = Recipe(**data)
            console.print(f"Succesfully loaded: {recipe}")

        asyncio.run(install_recipe(recipe))


if __name__ == "__main__":
    app()
