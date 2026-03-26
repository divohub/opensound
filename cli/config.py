import yaml
from pathlib import Path
from .models import AppConfig

CONFIG_PATH = Path("~/.config/opensound/config.yaml").expanduser()


def load_config() -> AppConfig:
    if not CONFIG_PATH.exists():
        return AppConfig()

    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f) or {}
        return AppConfig(**data)
