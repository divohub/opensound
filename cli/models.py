from enum import Enum
from pydantic import BaseModel, HttpUrl, Field


class PackageType(str, Enum):
    vst3 = "vst3"
    vst = "vst"
    lv2 = "lv2"
    clap = "clap"
    samplepack = "samplepack"


class AppConfig(BaseModel):
    install_paths: dict[PackageType, str] = {
        PackageType.vst3: "~/.vst3",
        PackageType.lv2: "~/.lv2",
        PackageType.clap: "~/.clap",
        PackageType.vst: "~/.vst",
    }


class OsType(str, Enum):
    linux = "linux"
    windows = "windows"
    macos = "macos"


class Targets(BaseModel):
    type: PackageType
    path: str
    enabled: bool = true


class Recipe(BaseModel):
    name: str
    version: str
    description: str | None = None
    targets: list[Targets] = Field(min_length=1)
    os: OsType
    url: HttpUrl
    install_path: str
    sha256: str | None = Field(min_length=64, max_length=64)
