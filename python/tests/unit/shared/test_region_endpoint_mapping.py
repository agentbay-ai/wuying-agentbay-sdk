import os
import unittest
from unittest.mock import patch

from agentbay import Config, _default_config, _load_config
from agentbay._common.config import (
    _DEFAULT_REGION,
    _resolve_endpoint,
)


class ResolveEndpointTest(unittest.TestCase):
    """Direct tests for _resolve_endpoint()."""

    def test_empty_region_falls_back_to_default(self):
        for empty in (None, ""):
            with self.subTest(value=empty):
                actual_region, endpoint = _resolve_endpoint(empty)
                self.assertEqual(actual_region, _DEFAULT_REGION)
                self.assertEqual(endpoint, "agentbay.cn-hangzhou.aliyuncs.com")

    def test_known_region_maps_silently(self):
        """Known production regions resolve via the pattern with no warning."""
        cases = {
            "cn-hangzhou": "agentbay.cn-hangzhou.aliyuncs.com",
            "ap-southeast-1": "agentbay.ap-southeast-1.aliyuncs.com",
            "us-east-1": "agentbay.us-east-1.aliyuncs.com",
        }
        for region, want_endpoint in cases.items():
            with self.subTest(region=region):
                with patch("agentbay._common.config._logger") as mock_logger:
                    actual_region, endpoint = _resolve_endpoint(region)
                mock_logger.warning.assert_not_called()
                self.assertEqual(actual_region, region)
                self.assertEqual(endpoint, want_endpoint)

    def test_unknown_region_warns_and_falls_back_to_pattern(self):
        """Unknown production regions log a warning and still use the pattern
        (no validation error — newly onboarded regions work without an SDK
        upgrade; the warning helps catch typos)."""
        cases = {
            "us-west-1": "agentbay.us-west-1.aliyuncs.com",
            "eu-central-1": "agentbay.eu-central-1.aliyuncs.com",
        }
        for region, want_endpoint in cases.items():
            with self.subTest(region=region):
                with patch("agentbay._common.config._logger") as mock_logger:
                    actual_region, endpoint = _resolve_endpoint(region)
                self.assertEqual(actual_region, region)
                self.assertEqual(endpoint, want_endpoint)
                mock_logger.warning.assert_called_once()
                # Format: warning(template, *args) — render with %.
                template, *args = mock_logger.warning.call_args.args
                rendered = template % tuple(args)
                self.assertIn(region, rendered)
                self.assertIn("cn-hangzhou", rendered)
                self.assertIn("ap-southeast-1", rendered)
                self.assertIn("us-east-1", rendered)

    def test_pre_prefix_strips_and_uses_pre_endpoint(self):
        cases = {
            "pre-cn-hangzhou": ("cn-hangzhou", "agentbay-pre.cn-hangzhou.aliyuncs.com"),
            "pre-ap-southeast-1": (
                "ap-southeast-1",
                "wuyingai-pre.ap-southeast-1.aliyuncs.com",
            ),
            # Pre- prefix on an unknown region also composes by pattern.
            "pre-us-west-1": ("us-west-1", "agentbay-pre.us-west-1.aliyuncs.com"),
        }
        for region, (want_region, want_endpoint) in cases.items():
            with self.subTest(region=region):
                actual_region, endpoint = _resolve_endpoint(region)
                self.assertEqual(actual_region, want_region)
                self.assertEqual(endpoint, want_endpoint)


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

    def test_legacy_endpoint_env_var_used_as_fallback_when_no_region(self):
        """AGENTBAY_ENDPOINT is a deprecated fallback: used as-is when
        AGENTBAY_REGION_ID is not set."""
        os.environ["AGENTBAY_ENDPOINT"] = "custom-endpoint.example.com"
        try:
            with patch(
                "agentbay._common.config._load_dotenv_with_fallback",
                lambda *a, **kw: None,
            ):
                result = _load_config(None)
            self.assertEqual(result["endpoint"], "custom-endpoint.example.com")
        finally:
            os.environ.pop("AGENTBAY_ENDPOINT", None)

    def test_legacy_endpoint_env_var_ignored_when_region_set(self):
        """AGENTBAY_ENDPOINT is ignored when AGENTBAY_REGION_ID is also set."""
        os.environ["AGENTBAY_ENDPOINT"] = "should-be-ignored.example.com"
        os.environ["AGENTBAY_REGION_ID"] = "ap-southeast-1"
        try:
            with patch(
                "agentbay._common.config._load_dotenv_with_fallback",
                lambda *a, **kw: None,
            ):
                result = _load_config(None)
            self.assertNotEqual(result["endpoint"], "should-be-ignored.example.com")
            self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")
        finally:
            os.environ.pop("AGENTBAY_ENDPOINT", None)
            os.environ.pop("AGENTBAY_REGION_ID", None)

    def test_unknown_region_id_is_accepted_with_warning(self):
        """Soft whitelist: unknown regions emit a warning but still compose the
        pattern-based endpoint (no validation error)."""
        with patch("agentbay._common.config._logger") as mock_logger:
            result = _load_config(Config(region_id="us-west-1"))
        self.assertEqual(result["region_id"], "us-west-1")
        self.assertEqual(result["endpoint"], "agentbay.us-west-1.aliyuncs.com")
        mock_logger.warning.assert_called_once()
        template, *args = mock_logger.warning.call_args.args
        self.assertIn("us-west-1", template % tuple(args))

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

    def test_config_endpoint_kwarg_emits_deprecation_and_region_wins(self):
        """Config(endpoint=...) emits DeprecationWarning. When both region_id
        and endpoint are set, region_id wins and endpoint is ignored."""
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            cfg = Config(
                endpoint="should-be-ignored.example.com",
                region_id="ap-southeast-1",
            )
        self.assertTrue(
            any(issubclass(w.category, DeprecationWarning) for w in caught),
            f"Expected DeprecationWarning, got: {[w.category.__name__ for w in caught]}",
        )
        # Endpoint is stored on cfg (deprecated but not dropped)
        self.assertEqual(cfg.endpoint, "should-be-ignored.example.com")
        # When loaded, region_id takes precedence
        result = _load_config(cfg)
        self.assertEqual(result["endpoint"], "agentbay.ap-southeast-1.aliyuncs.com")

    def test_config_endpoint_kwarg_used_as_fallback_without_region(self):
        """Config(endpoint=...) without region_id uses endpoint as-is."""
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            cfg = Config(endpoint="custom-endpoint.example.com")
        self.assertTrue(
            any(issubclass(w.category, DeprecationWarning) for w in caught),
        )
        result = _load_config(cfg)
        self.assertEqual(result["endpoint"], "custom-endpoint.example.com")

    def test_config_without_endpoint_kwarg_emits_no_warning(self):
        """Sanity: not passing endpoint must not emit any deprecation warning."""
        import warnings
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always", DeprecationWarning)
            Config(region_id="cn-hangzhou")
        deprecation_warnings = [
            w for w in caught if issubclass(w.category, DeprecationWarning)
        ]
        self.assertEqual(deprecation_warnings, [])


if __name__ == "__main__":
    unittest.main()
