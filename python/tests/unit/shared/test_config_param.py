import os
import tempfile
import unittest
from pathlib import Path
from unittest import TestCase
from unittest.mock import mock_open, patch

from agentbay import Config
from agentbay import _default_config, _load_config


def _writable_temp_root() -> Path:
    root = Path(__file__).resolve().parent / ".pytest-tmp"
    root.mkdir(parents=True, exist_ok=True)
    return root


class LoadConfigTestCase(unittest.TestCase):
    def setUp(self):
        # Create temporary .env file directory
        self.test_dir = tempfile.TemporaryDirectory(dir=str(_writable_temp_root()))
        self.env_file = Path(self.test_dir.name) / ".env"
        # Isolate from ambient environment for region/timeout
        for var in ("AGENTBAY_REGION_ID", "AGENTBAY_TIMEOUT_MS"):
            os.environ.pop(var, None)

    def tearDown(self):
        for var in ("AGENTBAY_REGION_ID", "AGENTBAY_TIMEOUT_MS"):
            os.environ.pop(var, None)
        self.test_dir.cleanup()

    def test_load_from_passed_config(self):
        """Explicit Config drives region_id (and derived endpoint)."""
        os.chdir(self.test_dir.name)
        custom_cfg = Config(
            timeout_ms=5000,
            region_id="ap-southeast-1",
        )
        result = _load_config(custom_cfg)

        self.assertEqual(result["region_id"], "ap-southeast-1")
        self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 5000)

    def test_partial_config_fields_are_filled_with_defaults(self):
        """
        Config should allow passing only a subset of fields.

        Expected behavior:
        - Missing fields are filled with SDK defaults.
        - Explicitly provided region_id drives endpoint via the mapping.
        """
        os.chdir(self.test_dir.name)
        cfg = Config(region_id="ap-southeast-1")
        result = _load_config(cfg)

        default = _default_config()
        self.assertEqual(result["region_id"], "ap-southeast-1")
        self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], default["timeout_ms"])

    def test_load_from_env_file(self):
        """Region picked up from .env file when no explicit config is passed."""
        os.chdir(self.test_dir.name)

        def _fake_load_dotenv(_path) -> bool:
            os.environ.setdefault("AGENTBAY_REGION_ID", "us-east-1")
            os.environ.setdefault("AGENTBAY_TIMEOUT_MS", "10000")
            return True

        with patch(
            "agentbay._common.config._find_dotenv_file", return_value=self.env_file
        ):
            with patch(
                "agentbay._common.config.dotenv.load_dotenv",
                side_effect=_fake_load_dotenv,
            ):
                result = _load_config(None)

        self.assertEqual(result["region_id"], "us-east-1")
        self.assertEqual(result["endpoint"], "agentbay.us-east-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 10000)

    @patch("pathlib.Path.is_file", return_value=False)
    def test_load_from_system_env_vars(self, mock_is_file):
        """Region picked up from process environment when no explicit config."""
        os.chdir(self.test_dir.name)
        os.environ["AGENTBAY_REGION_ID"] = "us-east-1"
        os.environ["AGENTBAY_TIMEOUT_MS"] = "15000"

        result = _load_config(None)

        self.assertEqual(result["region_id"], "us-east-1")
        self.assertEqual(result["endpoint"], "agentbay.us-east-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 15000)

    @patch("pathlib.Path.is_file", return_value=False)
    def test_use__default_config_when_no_source_provided(self, mock_is_file):
        """No explicit config, no env vars → SDK defaults (cn-hangzhou unit)."""
        os.chdir(self.test_dir.name)

        with patch(
            "agentbay._common.config._load_dotenv_with_fallback",
            lambda *a, **kw: None,
        ):
            result = _load_config(None)

        default = _default_config()
        self.assertEqual(result["region_id"], default["region_id"])
        self.assertEqual(result["endpoint"], default["endpoint"])
        self.assertEqual(result["timeout_ms"], default["timeout_ms"])

    def test_config_precedence_order(self):
        """Explicit > env var > .env file > default, exercised on region_id."""
        def _fake_load_dotenv(_path) -> bool:
            os.environ.setdefault("AGENTBAY_REGION_ID", "us-east-1")
            os.environ.setdefault("AGENTBAY_TIMEOUT_MS", "10000")
            return True

        os.chdir(self.test_dir.name)

        # 1. Explicit config beats everything (env vars and .env)
        os.environ["AGENTBAY_REGION_ID"] = "ap-southeast-1"
        os.environ["AGENTBAY_TIMEOUT_MS"] = "15000"

        custom_cfg = Config(
            timeout_ms=2000,
            region_id="cn-hangzhou",
        )
        result = _load_config(custom_cfg)
        self.assertEqual(result["region_id"], "cn-hangzhou")
        self.assertEqual(result["endpoint"], "agentbay.cn-hangzhou.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 2000)

        # 2. No explicit config → process env vars take effect
        with patch(
            "agentbay._common.config._find_dotenv_file", return_value=self.env_file
        ):
            with patch(
                "agentbay._common.config.dotenv.load_dotenv",
                side_effect=_fake_load_dotenv,
            ):
                result = _load_config(None)
        self.assertEqual(result["region_id"], "ap-southeast-1")
        self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 15000)

        # 3. Clear process env vars → values fall back to .env file (us-east-1)
        os.environ.pop("AGENTBAY_REGION_ID")
        os.environ.pop("AGENTBAY_TIMEOUT_MS")
        with patch(
            "agentbay._common.config._find_dotenv_file", return_value=self.env_file
        ):
            with patch(
                "agentbay._common.config.dotenv.load_dotenv",
                side_effect=_fake_load_dotenv,
            ):
                result = _load_config(None)
        self.assertEqual(result["region_id"], "us-east-1")
        self.assertEqual(result["endpoint"], "agentbay.us-east-1.aliyuncs.com")
        self.assertEqual(result["timeout_ms"], 10000)


if __name__ == "__main__":
    unittest.main()
