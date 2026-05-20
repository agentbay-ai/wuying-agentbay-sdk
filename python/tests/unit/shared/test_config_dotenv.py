"""
Test cases for enhanced .env file loading functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agentbay import (
    _find_dotenv_file,
    _load_config,
    _load_dotenv_with_fallback,
)

def _writable_temp_root() -> Path:
    root = Path(__file__).resolve().parent / ".pytest-tmp"
    root.mkdir(parents=True, exist_ok=True)
    return root


class TestDotEnvLoading:
    """Test enhanced .env file loading functionality."""

    def test__find_dotenv_file_current_directory(self):
        """Test finding .env file in current directory."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_file = tmpdir_path / ".env"

            def _exists(self: Path) -> bool:
                return self == env_file

            # Find .env file from current directory
            with patch("pathlib.Path.exists", _exists):
                found_file = _find_dotenv_file(tmpdir_path)
                assert found_file.resolve() == env_file.resolve()
                assert found_file.exists()

    def test__find_dotenv_file_parent_directory(self):
        """Test finding .env file in parent directory."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create .env in parent directory
            parent_env = tmpdir_path / ".env"

            def _exists(self: Path) -> bool:
                return self == parent_env

            # Create subdirectory
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Find .env file from subdirectory (should find parent's .env)
            with patch("pathlib.Path.exists", _exists):
                found_file = _find_dotenv_file(subdir)
                assert found_file.resolve() == parent_env.resolve()
                assert found_file.exists()

    def test__find_dotenv_file_git_repo_root(self):
        """Test finding .env file in git repository root."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create .git directory (simulate git repo)
            git_dir = tmpdir_path / ".git"
            # Create .env in git root
            git_env = tmpdir_path / ".env"

            def _exists(self: Path) -> bool:
                return self == git_dir or self == git_env

            # Create nested subdirectory
            subdir = tmpdir_path / "src" / "deep"
            subdir.mkdir(parents=True)

            # Find .env file from deep subdirectory
            with patch("pathlib.Path.exists", _exists):
                found_file = _find_dotenv_file(subdir)
                assert found_file.resolve() == git_env.resolve()

    def test__find_dotenv_file_not_found(self):
        """Test when .env file is not found anywhere."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Force "not found" even if the test runs inside a real repo that has a .env in parents.
            def _exists(_: Path) -> bool:
                return False

            with patch("pathlib.Path.exists", _exists):
                found_file = _find_dotenv_file(subdir)
                assert found_file is None

    def test_load_dotenv_with_custom_path(self):
        """Test loading .env file from custom path."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            custom_env = tmpdir_path / "custom.env"
            custom_env.write_text("CUSTOM_VAR=custom_value")

            # Clear any existing env var
            if "CUSTOM_VAR" in os.environ:
                del os.environ["CUSTOM_VAR"]

            # Load custom .env file
            _load_dotenv_with_fallback(str(custom_env))

            # Check if variable was loaded
            assert os.environ.get("CUSTOM_VAR") == "custom_value"

            # Cleanup
            if "CUSTOM_VAR" in os.environ:
                del os.environ["CUSTOM_VAR"]

    def test__load_dotenv_with_fallback_search(self):
        """Test loading .env file using fallback search."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create .env in parent
            parent_env = tmpdir_path / ".env"

            # Create subdirectory
            subdir = tmpdir_path / "subdir"
            subdir.mkdir()

            # Clear any existing env var
            if "FALLBACK_VAR" in os.environ:
                del os.environ["FALLBACK_VAR"]

            def _fake_load_dotenv(_path) -> bool:
                os.environ.setdefault("FALLBACK_VAR", "fallback_value")
                return True

            # Change to subdirectory and load .env
            with patch("pathlib.Path.cwd", return_value=subdir):
                with patch("agentbay._common.config._find_dotenv_file", return_value=parent_env):
                    with patch("agentbay._common.config.dotenv.load_dotenv", side_effect=_fake_load_dotenv):
                        _load_dotenv_with_fallback()

            # Check if variable was loaded from parent
            assert os.environ.get("FALLBACK_VAR") == "fallback_value"

            # Cleanup
            if "FALLBACK_VAR" in os.environ:
                del os.environ["FALLBACK_VAR"]

    def test_environment_variable_precedence(self):
        """Test that environment variables take precedence over .env file."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_file = tmpdir_path / ".env"

            # Set environment variable (higher precedence)
            os.environ["PRECEDENCE_VAR"] = "from_environment"

            try:
                def _fake_load_dotenv(_path) -> bool:
                    os.environ.setdefault("PRECEDENCE_VAR", "from_env_file")
                    return True

                # Load config with .env file
                with patch("agentbay._common.config.dotenv.load_dotenv", side_effect=_fake_load_dotenv):
                    config = _load_config(None, str(env_file))

                # Environment variable should take precedence
                assert os.environ.get("PRECEDENCE_VAR") == "from_environment"

            finally:
                # Cleanup
                if "PRECEDENCE_VAR" in os.environ:
                    del os.environ["PRECEDENCE_VAR"]

    def test__load_config_with_custom_env_file(self):
        """Test _load_config with custom .env file path."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            custom_env = tmpdir_path / "test.env"
            custom_env.write_text(
                """
AGENTBAY_REGION_ID=ap-southeast-1
AGENTBAY_TIMEOUT_MS=30000
""".strip()
            )

            # Clear existing env vars
            for var in ["AGENTBAY_REGION_ID", "AGENTBAY_TIMEOUT_MS"]:
                if var in os.environ:
                    del os.environ[var]

            try:
                # Load config with custom .env file
                config = _load_config(None, str(custom_env))

                # Region drives endpoint via the mapping
                assert config["region_id"] == "ap-southeast-1"
                assert config["endpoint"] == "agentbay.ap-southeast-1.aliyuncs.com"
                assert config["timeout_ms"] == 30000

            finally:
                # Cleanup
                for var in ["AGENTBAY_REGION_ID", "AGENTBAY_TIMEOUT_MS"]:
                    if var in os.environ:
                        del os.environ[var]

    def test__load_config_upward_search(self):
        """Test _load_config with upward .env file search."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create .env in parent
            parent_env = tmpdir_path / ".env"

            # Create subdirectory
            subdir = tmpdir_path / "project" / "src"
            subdir.mkdir(parents=True)

            # Clear existing env vars
            if "AGENTBAY_REGION_ID" in os.environ:
                del os.environ["AGENTBAY_REGION_ID"]

            try:
                def _fake_load_dotenv(_path) -> bool:
                    os.environ.setdefault("AGENTBAY_REGION_ID", "us-east-1")
                    return True

                # Simulate running from subdirectory
                with patch("os.getcwd", return_value=str(subdir)):
                    with patch("agentbay._common.config._find_dotenv_file", return_value=parent_env):
                        with patch("agentbay._common.config.dotenv.load_dotenv", side_effect=_fake_load_dotenv):
                            config = _load_config(None)

                # Region picked up from .env, endpoint derived from mapping
                assert config["region_id"] == "us-east-1"
                assert config["endpoint"] == "agentbay.us-east-1.aliyuncs.com"

            finally:
                # Cleanup
                if "AGENTBAY_REGION_ID" in os.environ:
                    del os.environ["AGENTBAY_REGION_ID"]

    def test_invalid_timeout_handling(self):
        """Test handling of invalid AGENTBAY_TIMEOUT_MS values."""
        with tempfile.TemporaryDirectory(dir=str(_writable_temp_root())) as tmpdir:
            tmpdir_path = Path(tmpdir)
            env_file = tmpdir_path / ".env"

            # Clear existing env vars
            if "AGENTBAY_TIMEOUT_MS" in os.environ:
                del os.environ["AGENTBAY_TIMEOUT_MS"]

            try:
                def _fake_load_dotenv(_path) -> bool:
                    os.environ.setdefault("AGENTBAY_TIMEOUT_MS", "invalid_number")
                    return True

                # Load config with invalid timeout
                with patch("agentbay._common.config.dotenv.load_dotenv", side_effect=_fake_load_dotenv):
                    config = _load_config(None, str(env_file))

                # Should use default timeout value
                assert config["timeout_ms"] == 60000  # Default value

            finally:
                # Cleanup
                if "AGENTBAY_TIMEOUT_MS" in os.environ:
                    del os.environ["AGENTBAY_TIMEOUT_MS"]


if __name__ == "__main__":
    pytest.main([__file__])
