import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

import httpx

from cli.installer import get_default_cache_dir, _sync_extract_package
from cli.models import Recipe, AppConfig

# A valid recipe for our tests
VALID_RECIPE_PAYLOAD = {
    "name": "vital",
    "version": "1.5.5",
    "targets": [{"type": "vst3", "path": "Vital.vst3"}],
    "os": "linux",
    "url": "https://example.com/vital.zip",
    "sha256": "f" * 64,
}

class TestInstaller:
    """Test suite for the installer logic."""

    @patch("os.getenv")
    def test_get_default_cache_dir(self, mock_getenv):
        """Positive test: Verifies that cache directory paths are resolved appropriately."""
        mock_getenv.return_value = "/tmp/fake_cache"
        
        cache_dir = get_default_cache_dir()
        
        # It should append 'opensound' to the XDG_CACHE_HOME
        assert cache_dir == Path("/tmp/fake_cache/opensound")
        
    @patch("zipfile.ZipFile")
    @patch("cli.installer.get_default_cache_dir")
    def test_sync_extract_package_missing_target(self, mock_get_cache, mock_zipfile):
        """Negative test: Ensure ValueError is raised if the target path is missing from the ZIP."""
        mock_get_cache.return_value = Path("/tmp/cache")
        
        # Create a fake zipfile context manager
        mock_zf = MagicMock()
        mock_zf.namelist.return_value = ["wrong_folder/", "readme.txt"]
        
        mock_zipfile.return_value.__enter__.return_value = mock_zf
        
        recipe = Recipe(**VALID_RECIPE_PAYLOAD)
        config = AppConfig()
        
        with pytest.raises(ValueError) as exc_info:
            _sync_extract_package(Path("/tmp/fake.zip"), recipe, config)
            
        # Target 'Vital.vst3' was requested but only 'wrong_folder/' was available in namelist
        assert "not found in Zip Archives" in str(exc_info.value)
