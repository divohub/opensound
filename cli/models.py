from enum import Enum
from pydantic import BaseModel, HttpUrl


class PackageType(str, Enum):
    vst3 = "vst3"
    lv2 = "lv2"
    clap = "clap"
    samplepack = "samplepack"


class OsType(str, Enum):
    linux = "linux"
    windows = "windows"
    macos = "macos"


class Recipe(BaseModel):
    name: str
    version: str
    description: str | None = None
    type: PackageType
    os: OsType
    url: HttpUrl
    install_path: str
    sha256: str | None = None
