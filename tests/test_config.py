"""Tests for configuration module."""
import os
import pytest
from unittest.mock import patch

from app.config import get_settings, Settings


class TestGetSettings:
    """Tests for get_settings function."""

    def test_missing_ado_org_raises_error(self):
        """Missing ADO_ORG should raise ValueError."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="ADO_ORG"):
                get_settings()

    def test_missing_ado_project_raises_error(self):
        """Missing ADO_PROJECT should raise ValueError."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="ADO_PROJECT"):
                get_settings()

    def test_missing_ado_pat_raises_error(self):
        """ Missing ADO_PAT should raise ValueError."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
            "ADO_PROJECT": "TestProject",
        }
        with patch.dict(os.environ, env, clear=True):
            with pytest.raises(ValueError, match="ADO_PAT"):
                get_settings()

    def test_valid_settings_returns_settings(self):
        """Valid env vars should return Settings object."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "test-pat-token",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_settings()

        assert isinstance(settings, Settings)
        assert settings.ado_org == "https://dev.azure.com/testorg"
        assert settings.ado_project == "TestProject"
        assert settings.ado_pat == "test-pat-token"
        assert settings.ado_api_version == "7.1-preview.3"
        assert settings.port == 8080
        assert settings.log_level == "INFO"

    def test_custom_api_version(self):
        """Custom API version should be used."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "test-pat-token",
            "ADO_API_VERSION": "7.2-preview.1",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_settings()

        assert settings.ado_api_version == "7.2-preview.1"

    def test_custom_port(self):
        """Custom port should be used."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "test-pat-token",
            "PORT": "9000",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_settings()

        assert settings.port == 9000

    def test_custom_log_level(self):
        """Custom log level should be used."""
        env = {
            "ADO_ORG": "https://dev.azure.com/testorg",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "test-pat-token",
            "LOG_LEVEL": "DEBUG",
        }
        with patch.dict(os.environ, env, clear=True):
            settings = get_settings()

        assert settings.log_level == "DEBUG"
