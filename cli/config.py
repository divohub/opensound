"""Configuration management for the OpenSound application.

Responsible for safely loading user-defined settings from YAML files.
"""

import yaml
from pathlib import Path
from .models import AppConfig

CONFIG_PATH = Path("~/.config/opensound/config.yaml").expanduser()


def load_config() -> AppConfig:
    """Load configuration variables from the designated config file.

    Checks if a YAML file exists at `~/.config/opensound/config.yaml`.
    If it exists, it safely parses it into an `AppConfig` Pydantic model.
    Otherwise, returns default settings.

    Returns:
        AppConfig: An initialized application configuration model.
    """
    if not CONFIG_PATH.exists():
        return AppConfig()

    with open(CONFIG_PATH, "r") as f:
        data = yaml.safe_load(f) or {}
        return AppConfig(**data)
