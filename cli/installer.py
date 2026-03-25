import os
import asyncio
from pathlib import Path
from typing import Optional
import tempfile

import aiofiles
import typer
from rich.console import Console
import httpx

from .models import Recipe

console = Console()


async def download_package(
    recipe: Recipe, custom_path: Optional[Path] = None, chunk_size: int = 8192
):
    # task_id ?

    if custom_path:
        base_path = custom_path
    else:
        base_path = Path(tempfile.gettempdir()) / "opensound"

    try:
        # maybe redundancy ? nah im fucking goat
        await asyncio.to_thread(os.makedirs, str(base_path), exist_ok=True)

        async with httpx.AsyncClient() as client:
            async with client.stream("GET", str(recipe.url)) as response:
                response.raise_for_status()

                # TODO: progress bar implement

                total_size = int(response.headers.get("Content-Length", 0))

                if total_size == 0:
                    console.log("Warning: Content-Length is 0")
                    # pass to Progress id and length = 0
                    pass
                else:
                    # pass to Progress id and length
                    pass

                # downloaded_bytes = 0

                temp_zip_path = base_path / f"{recipe.name}"

                async with aiofiles.open(temp_zip_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        await f.write(chunk)
                        # downloaded_bytes += len(chunk)
                        # progress.update(task_id, downloaded_bytes)

    except httpx.HTTPStatusError as e:
        console.log(
            f"[bold red]Error HTTP: {e.response.status_code} - {
                e.response.text
            }[/bold red]"
        )
    except httpx.RequestError as e:
        console.log(f"[bold red]RequestError : {e}[/bold red]")
    except Exception as e:
        console.log(f"[bold red]Unexpected error : {e}[/bold red]")
