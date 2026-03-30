import os
from unittest.mock import patch, mock_open
import pytest
import yaml
from pathlib import Path

from cli.config import load_config
from cli.models import AppConfig, PackageType


class TestConfig:
    """Test suite for configuration loading module."""

    @patch("cli.config.CONFIG_PATH")
    def test_load_config_missing_file(self, mock_exists):
        """Positive test: When config file is missing, the default AppConfig should be returned."""
        mock_exists.return_value = False

        config = load_config()

        # Verify default paths
        assert config.install_paths[PackageType.vst3] == "~/.vst3"
        assert config.install_paths[PackageType.lv2] == "~/.lv2"

    @patch("cli.config.CONFIG_PATH")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
install_paths:
  vst3: "/custom/vst3/path"
  lv2: "/custom/lv2/path"
""",
    )
    def test_load_config_with_valid_yaml(self, mock_file, mock_exists):
        """Positive test: Valid YAML correctly populates AppConfig."""
        mock_exists.return_value = True

        config = load_config()

        assert config.install_paths[PackageType.vst3] == "/custom/vst3/path"
        assert config.install_paths[PackageType.lv2] == "/custom/lv2/path"
        # Since not defined in yaml, and Pydantic dictates replacing the dict if one is passed vs merging
        # Note: If AppConfig was defined using Pydantic strictly without deep merging, it replaces `install_paths` dict entirely.

    @patch("cli.config.CONFIG_PATH")
    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
# Empty YAML or invalid structure
""",
    )
    def test_load_config_empty_yaml(self, mock_file, mock_exists):
        """Negative test: Ensure empty YAML safely falls back to default AppConfig values."""
        mock_exists.return_value = True

        config = load_config()

        assert config.install_paths[PackageType.vst3] == "~/.vst3"
