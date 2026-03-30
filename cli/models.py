"""Data models and validation logic for OpenSound.

This module contains the Pydantic models used to parse, validate,
and serialize application configurations and plugin installation recipes.
"""

from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class PackageType(str, Enum):
    """Enumeration of supported audio plugin formats."""

    vst3 = "vst3"
    vst = "vst"
    lv2 = "lv2"
    clap = "clap"
    samplepack = "samplepack"


class AppConfig(BaseModel):
    """Application configuration model.

    Attributes:
        install_paths: A mapping of PackageType formats to their default
            installation directories on the host system.
    """

    install_paths: dict[PackageType, str] = {
        PackageType.vst3: "~/.vst3",
        PackageType.lv2: "~/.lv2",
        PackageType.clap: "~/.clap",
        PackageType.vst: "~/.vst",
    }


class OsType(str, Enum):
    """Enumeration of supported operating systems."""

    linux = "linux"
    windows = "windows"
    macos = "macos"


class Targets(BaseModel):
    """Target paths for extracting items from an archive.

    Attributes:
        type: The plugin format (e.g., VST3, LV2).
        path: The relative path or pattern inside the downloaded archive.
        enabled: Whether this specific target should be installed.
    """

    type: PackageType
    path: str
    enabled: bool = True


class RecipeSchema(BaseModel):
    """Configuration recipe for an installable sound package or plugin.

    Attributes:
        name: Name of the package/plugin.
        version: Version string (e.g., '1.5.5').
        description: Optional brief description of the package.
        targets: A list of targets (folders/files) to extract from the payload.
            Must contain at least one item.
        os: Target operating system compatibility.
        url: The download URL for the package payload (usually a ZIP).
        sha256: Optional strict 64-character SHA-256 hash for payload verification.
    """

    name: str
    version: str
    description: str | None = None
    targets: list[Targets] = Field(min_length=1)
    os: OsType
    url: HttpUrl
    sha256: str | None = Field(min_length=64, max_length=64)
