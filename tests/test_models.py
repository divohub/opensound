import pytest
from pydantic import ValidationError
from cli.models import AppConfig, OsType, PackageType, Recipe, Targets

# A valid recipe payload we can reuse and mutate in tests
VALID_RECIPE_PAYLOAD = {
    "name": "vital",
    "version": "1.5.5",
    "description": "Spectral warping synth",
    "targets": [{"type": "vst3", "path": "Vital.vst3"}],
    "os": "linux",
    "url": "https://example.com/vital.zip",
    "sha256": "a" * 64,  # Exact 64 chars required
}


class TestModels:
    """Test suite for data models and their validations."""

    def test_recipe_creation_success(self):
        """Positive test: Ensure valid data creates a Recipe object without throwing exceptions."""
        recipe = Recipe(**VALID_RECIPE_PAYLOAD)
        
        assert recipe.name == "vital"
        assert recipe.version == "1.5.5"
        assert recipe.os == OsType.linux
        assert str(recipe.url) == "https://example.com/vital.zip"
        assert len(recipe.targets) == 1
        assert recipe.targets[0].type == PackageType.vst3

    def test_recipe_invalid_sha256_length(self):
        """Negative test: Ensure sha256 must be exactly 64 characters long."""
        invalid_payload = VALID_RECIPE_PAYLOAD.copy()
        
        # Test too short
        invalid_payload["sha256"] = "a" * 63
        with pytest.raises(ValidationError) as exc_info:
            Recipe(**invalid_payload)
        assert "sha256" in str(exc_info.value)
        
        # Test too long
        invalid_payload["sha256"] = "a" * 65
        with pytest.raises(ValidationError) as exc_info:
            Recipe(**invalid_payload)
        assert "sha256" in str(exc_info.value)

    def test_recipe_empty_targets(self):
        """Negative test: Ensure targets list cannot be empty."""
        invalid_payload = VALID_RECIPE_PAYLOAD.copy()
        invalid_payload["targets"] = []
        
        with pytest.raises(ValidationError) as exc_info:
            Recipe(**invalid_payload)
        
        # Checking that the error is explicitly about the 'targets' field constraints
        assert "targets" in str(exc_info.value)

    @pytest.mark.parametrize("os_val", ["linux", "windows", "macos"])
    def test_valid_os_types(self, os_val):
        """Positive test: Check that valid OS values are accepted."""
        payload = VALID_RECIPE_PAYLOAD.copy()
        payload["os"] = os_val
        recipe = Recipe(**payload)
        assert recipe.os == OsType(os_val)

    def test_invalid_os_type(self):
        """Negative test: Ensure unsupported OS values are rejected."""
        payload = VALID_RECIPE_PAYLOAD.copy()
        payload["os"] = "templeos"  # Unsupported
        
        with pytest.raises(ValidationError):
            Recipe(**payload)

    def test_app_config_defaults(self):
        """Positive test: Ensure AppConfig has sensible fallback defaults if not provided."""
        config = AppConfig()
        
        # Assert default paths are populated correctly
        assert PackageType.vst3 in config.install_paths
        assert config.install_paths[PackageType.vst3] == "~/.vst3"
        assert config.install_paths[PackageType.lv2] == "~/.lv2"

    def test_app_config_custom_paths(self):
        """Positive test: Ensure AppConfig accepts custom path overrides."""
        custom_paths = {PackageType.vst3: "/opt/custom/vst3"}
        config = AppConfig(install_paths=custom_paths)
        
        assert config.install_paths[PackageType.vst3] == "/opt/custom/vst3"
