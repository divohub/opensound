"""Installer module for fetching and extracting sound packages.

This module handles downloading package artifacts via HTTP, extracting ZIP archives,
and correctly placing the extracted components in standard OS-specific directories
defined by the configuration.
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
import tempfile
import zipfile
import shutil

import aiofiles
from rich.console import Console
import httpx
from .models import Recipe, Targets, PackageType
from .config import AppConfig, load_config

console = Console()


def get_default_cache_dir() -> Path:
    """Retrieve the platform-specific default cache directory.

    Resolves to `$XDG_CACHE_HOME/opensound` or `~/.cache/opensound`.

    Returns:
        Path: A path object pointing to the writable cache directory.
    """
    xdg_cache = os.getenv("XDG_CACHE_HOME", "~/.cache/")
    base = Path(xdg_cache).expanduser() / "opensound"

    base.mkdir(parents=True, exist_ok=True)
    return base


async def download_package(
    recipe: Recipe, custom_path: Optional[Path] = None, chunk_size: int = 8192
) -> Path | None:
    """Download a package asynchronously over HTTP.

    Streams a package from `recipe.url` into a temporary zip file.

    Args:
        recipe: The `Recipe` object describing the file to download.
        custom_path: An optional directory to download the file into.
        chunk_size: Size in bytes of each download chunk (default 8192).

    Returns:
        Path | None: The absolute path to the downloaded .zip file on disk,
            or `None` if an HTTP/Request error occurs.
    """
    # task_id ?

    if custom_path:
        base_path = custom_path
    else:
        base_path = get_default_cache_dir()

    try:
        # We use asyncio.to_thread to prevent blocking the event loop on IO calls
        await asyncio.to_thread(os.makedirs, str(base_path), exist_ok=True)

        async with httpx.AsyncClient(follow_redirects=True) as client:
            async with client.stream("GET", str(recipe.url)) as response:
                if response.is_error:
                    await response.aread()
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

                temp_zip_path = base_path / f"{recipe.name}.zip"

                async with aiofiles.open(temp_zip_path, "wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size=chunk_size):
                        await f.write(chunk)
                        # downloaded_bytes += len(chunk)
                        # progress.update(task_id, downloaded_bytes)
            return temp_zip_path

    except httpx.HTTPStatusError as e:
        error_body = e.response.text if e.response.is_closed else "Content not read"
        console.log(
            f"[bold red]Error HTTP: {
                e.response.status_code} - {error_body}[/bold red]"
        )
    except httpx.RequestError as e:
        console.log(f"[bold red]RequestError : {e}[/bold red]")
    except Exception as e:
        console.log(f"[bold red]Unexpected error : {e}[/bold red]")
    return None


async def install_recipe(recipe: Recipe):
    """Orchestrate the installation process for a specific recipe.

    Downloads the artifact, loads current app config, and dispatches the
    extraction process to a separate thread.

    Args:
        recipe: The `Recipe` to install.
    """
    # main entry point for installation

    zip_path = await download_package(recipe)

    if zip_path:
        config = load_config()
        console.log(
            f"Starting extraction for [bold cyan] {recipe.name}[/bold cyan] ..."
        )

        try:
            await asyncio.to_thread(_sync_extract_package, zip_path, recipe, config)
            console.log(
                f"[bold green]Sussecfully installed {recipe.name} [/bold green]"
            )
        except Exception as e:
            console.log(f"[bold red]Installation is failed: {e} [/bold red]")


def _sync_extract_package(zip_path: Path, recipe: Recipe, config: AppConfig):
    """Synchronously extract and place files from a downloaded ZIP archive.

    This function is CPU/IO bound and should be executed in a thread pool.
    It verifies that requested targets exist in the zip file, extracts it to
    a temporary path, and systematically moves files into their final system
    destinations.

    Args:
        zip_path: Path to the downloaded ZIP artifact.
        recipe: Configuration metadata defining what components to extract.
        config: Application configuration, mapping package types to install paths.

    Raises:
        ValueError: If a target path defined in the recipe is completely missing
            from the ZIP archive list.
        FileNotFoundError: If a target path is found in namelist, but fails
            to manifest during the physical extraction process.
    """
    cache_dir = get_default_cache_dir()

    with zipfile.ZipFile(zip_path, "r") as zf:
        namelist = zf.namelist()

        for target in recipe.targets:
            if not any(target.path in name for name in namelist):
                raise ValueError(
                    f"Target path '{target.path}' not found in Zip Archives"
                )

        with tempfile.TemporaryDirectory(dir=cache_dir) as tmp_dir:
            tmp_path = Path(tmp_dir)
            console.log(f"Extracting to TemporaryDirectory: {cache_dir}...")
            zf.extractall(tmp_path)

            for target in recipe.targets:
                install_base = Path(
                    os.path.expanduser(config.install_paths[target.type])
                )

                final_destination = install_base / Path(target.path).name

                found_items = list(tmp_path.glob(f"**/{target.path}"))

                if not found_items:
                    raise FileNotFoundError(
                        f"Could not locate {target.path} after extraction"
                    )

                source_path = found_items[0]

                # We can do this more elegantly in the future,
                # but currently we replace the target if it already exists.
                if final_destination.exists():
                    console.log(f"Replacing existing version at {
                                final_destination}")

                    if final_destination.is_dir():
                        shutil.rmtree(final_destination)
                    else:
                        final_destination.unlink()

                final_destination.parent.mkdir(parents=True, exist_ok=True)

                shutil.move(str(source_path), str(final_destination))
                console.log(f"Moved {target.path} successfully to {
                            final_destination}")
