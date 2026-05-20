import os
import unittest
from unittest.mock import patch

from agentbay import Config, _default_config, _load_config
from agentbay._common.config import (
    _DEFAULT_REGION,
    _REGION_ENDPOINT_MAP,
    _resolve_endpoint,
)


class ResolveEndpointTest(unittest.TestCase):
    """Direct tests for _resolve_endpoint()."""

    def test_empty_region_falls_back_to_default(self):
        for empty in (None, ""):
            with self.subTest(value=empty):
                actual_region, endpoint = _resolve_endpoint(empty)
                self.assertEqual(actual_region, _DEFAULT_REGION)
                self.assertEqual(endpoint, _REGION_ENDPOINT_MAP[_DEFAULT_REGION])

    def test_each_supported_region_maps_correctly(self):
        expected = {
            "cn-hangzhou": "agentbay.cn-hangzhou.aliyuncs.com",
            "ap-southeast-1": "agentbay.ap-southeast-1.aliyuncs.com",
            "us-east-1": "agentbay.us-east-1.aliyuncs.com",
        }
        for region, want_endpoint in expected.items():
            with self.subTest(region=region):
                actual_region, endpoint = _resolve_endpoint(region)
                self.assertEqual(actual_region, region)
                self.assertEqual(endpoint, want_endpoint)

    def test_pre_prefix_strips_and_uses_pre_endpoint(self):
        actual_region, endpoint = _resolve_endpoint("pre-cn-hangzhou")
        self.assertEqual(actual_region, "cn-hangzhou")
        self.assertEqual(endpoint, "agentbay-pre.cn-hangzhou.aliyuncs.com")

        actual_region, endpoint = _resolve_endpoint("pre-ap-southeast-1")
        self.assertEqual(actual_region, "ap-southeast-1")
        self.assertEqual(endpoint, "agentbay-pre.ap-southeast-1.aliyuncs.com")

    def test_invalid_region_raises_with_supported_list(self):
        with self.assertRaises(ValueError) as ctx:
            _resolve_endpoint("us-west-1")
        msg = str(ctx.exception)
        self.assertIn("us-west-1", msg)
        for region in _REGION_ENDPOINT_MAP:
            self.assertIn(region, msg)
        self.assertIn("pre-", msg)

    def test_invalid_pre_region_raises(self):
        with self.assertRaises(ValueError) as ctx:
            _resolve_endpoint("pre-us-west-1")
        self.assertIn("pre-us-west-1", str(ctx.exception))


class DefaultConfigTest(unittest.TestCase):
    def test_default_uses_hangzhou_unit_endpoint(self):
        cfg = _default_config()
        self.assertEqual(cfg["region_id"], "cn-hangzhou")
        self.assertEqual(cfg["endpoint"], "agentbay.cn-hangzhou.aliyuncs.com")
        self.assertEqual(cfg["timeout_ms"], 60000)


class LoadConfigDerivesEndpointTest(unittest.TestCase):
    """End-to-end behavior of _load_config: endpoint always comes from region."""

    def setUp(self):
        # Isolate from ambient environment
        for var in ("AGENTBAY_REGION_ID", "AGENTBAY_ENDPOINT", "AGENTBAY_TIMEOUT_MS"):
            os.environ.pop(var, None)

    def test_explicit_region_drives_endpoint(self):
        result = _load_config(Config(region_id="ap-southeast-1"))
        self.assertEqual(result["region_id"], "ap-southeast-1")
        self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")

    def test_pre_prefix_normalizes_region_in_loaded_config(self):
        result = _load_config(Config(region_id="pre-cn-hangzhou"))
        self.assertEqual(result["region_id"], "cn-hangzhou")
        self.assertEqual(result["endpoint"], "agentbay-pre.cn-hangzhou.aliyuncs.com")

    def test_no_config_uses_default(self):
        with patch(
            "agentbay._common.config._load_dotenv_with_fallback", lambda *a, **kw: None
        ):
            result = _load_config(None)
        self.assertEqual(result["region_id"], "cn-hangzhou")
        self.assertEqual(result["endpoint"], "agentbay.cn-hangzhou.aliyuncs.com")

    def test_env_var_region_id_is_picked_up(self):
        os.environ["AGENTBAY_REGION_ID"] = "us-east-1"
        try:
            with patch(
                "agentbay._common.config._load_dotenv_with_fallback",
                lambda *a, **kw: None,
            ):
                result = _load_config(None)
            self.assertEqual(result["region_id"], "us-east-1")
            self.assertEqual(result["endpoint"], "agentbay.us-east-1.aliyuncs.com")
        finally:
            os.environ.pop("AGENTBAY_REGION_ID", None)

    def test_legacy_endpoint_env_var_is_ignored(self):
        """Regression: AGENTBAY_ENDPOINT used to override endpoint; now it must be ignored."""
        os.environ["AGENTBAY_ENDPOINT"] = "should-be-ignored.example.com"
        try:
            with patch(
                "agentbay._common.config._load_dotenv_with_fallback",
                lambda *a, **kw: None,
            ):
                result = _load_config(None)
            self.assertNotEqual(result["endpoint"], "should-be-ignored.example.com")
            self.assertEqual(result["endpoint"], "agentbay.cn-hangzhou.aliyuncs.com")
        finally:
            os.environ.pop("AGENTBAY_ENDPOINT", None)

    def test_invalid_region_id_raises_during_load(self):
        with self.assertRaises(ValueError):
            _load_config(Config(region_id="us-west-1"))

    def test_explicit_config_takes_priority_over_env(self):
        os.environ["AGENTBAY_REGION_ID"] = "us-east-1"
        try:
            result = _load_config(Config(region_id="ap-southeast-1"))
            self.assertEqual(result["region_id"], "ap-southeast-1")
            self.assertEqual(
                result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com"
            )
        finally:
            os.environ.pop("AGENTBAY_REGION_ID", None)


if __name__ == "__main__":
    unittest.main()
