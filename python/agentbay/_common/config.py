import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import dotenv

from .logger import get_logger

# Initialize _logger for this module
_logger = get_logger("config")


# Endpoint is no longer user-configurable; it is derived from region_id by
# direct pattern substitution for production regions, and by a hardcoded
# lookup table for pre-release regions (since pre-release hostnames don't
# follow a single pattern: e.g. cn-hangzhou uses "agentbay-pre.*" while
# ap-southeast-1 uses "wuyingai-pre.*").
_DEFAULT_REGION = "cn-hangzhou"
_PRE_PREFIX = "pre-"

# Known production regions. Unknown entries are NOT rejected — they fall
# through to the default "agentbay.{region}.aliyuncs.com" pattern with a
# warning logged, since newly onboarded regions should work without an SDK
# upgrade. The warning helps catch typos before the request actually fires.
_KNOWN_REGIONS: Tuple[str, ...] = ("cn-hangzhou", "ap-southeast-1", "us-east-1")

# Hardcoded mapping for pre-release regions (after stripping the "pre-" prefix).
# Unknown entries fall back to "agentbay-pre.{actual}.aliyuncs.com" with a
# warning logged, since we genuinely don't know which pre-release naming
# convention a new region will adopt.
_PRE_REGION_ENDPOINT_MAP: Dict[str, str] = {
    "cn-hangzhou": "agentbay-pre.cn-hangzhou.aliyuncs.com",
    "ap-southeast-1": "wuyingai-pre.ap-southeast-1.aliyuncs.com",
}


def _resolve_endpoint(region_id: Optional[str]) -> Tuple[str, str]:
    """Resolve (actual_region, endpoint) from a user-supplied region_id.

    Empty/None region falls back to the default. A "pre-" prefix selects the
    pre-release endpoint and is stripped from the returned region:
    - Known pre regions use the hardcoded entry in `_PRE_REGION_ENDPOINT_MAP`.
    - Unknown pre regions log a warning and fall back to the default
      "agentbay-pre.{actual}.aliyuncs.com" pattern.

    Non-pre regions are composed by direct pattern substitution:
    - Known production regions in `_KNOWN_REGIONS` resolve silently.
    - Unknown regions log a warning and still use the pattern (no validation
      error — newly onboarded regions should work without an SDK upgrade).
    """
    if not region_id:
        region_id = _DEFAULT_REGION

    if region_id.startswith(_PRE_PREFIX):
        actual = region_id[len(_PRE_PREFIX):]
        if actual in _PRE_REGION_ENDPOINT_MAP:
            return actual, _PRE_REGION_ENDPOINT_MAP[actual]
        _logger.warning(
            f"Unknown pre-release region 'pre-{actual}'. Falling back to "
            f"'agentbay-pre.{actual}.aliyuncs.com'; the request may fail at "
            f"DNS resolution if the host does not exist. Known pre regions: "
            f"{list(_PRE_REGION_ENDPOINT_MAP.keys())}."
        )
        return actual, f"agentbay-pre.{actual}.aliyuncs.com"

    if region_id not in _KNOWN_REGIONS:
        _logger.warning(
            f"Unknown region '{region_id}'. Falling back to "
            f"'agentbay.{region_id}.aliyuncs.com'; the request may fail at "
            f"DNS resolution if the host does not exist. Known regions: "
            f"{list(_KNOWN_REGIONS)}."
        )
    return region_id, f"agentbay.{region_id}.aliyuncs.com"


class Config:
    """
    Configuration object for AgentBay client.

    The preferred input is ``region_id``; the SDK derives the endpoint from it
    via direct pattern substitution. ``endpoint`` is retained as a deprecated
    fallback: when ``region_id`` is not set the value of ``endpoint`` is used
    as-is. When both are set, ``region_id`` wins and ``endpoint`` is ignored.
    Either form emits a ``DeprecationWarning``.

    .. deprecated:: 0.21.0
        ``endpoint`` parameter. Use ``region_id`` instead.
    """

    def __init__(
        self,
        timeout_ms: Optional[int] = None,
        region_id: Optional[str] = None,
        endpoint: Optional[str] = None,
    ):
        self.timeout_ms = timeout_ms
        self.region_id = region_id
        self.endpoint: Optional[str] = endpoint if endpoint else None
        if endpoint:
            import warnings
            warnings.warn(
                f"Config(endpoint={endpoint!r}) is deprecated; pass region_id "
                "instead. The value is used only as a fallback when region_id "
                "is not set, and will be removed in a future major version.",
                DeprecationWarning,
                stacklevel=2,
            )


def _default_config() -> Dict[str, Any]:
    """Return the default configuration"""
    _, default_endpoint = _resolve_endpoint(_DEFAULT_REGION)
    return {
        "endpoint": default_endpoint,
        "timeout_ms": 60000,
        "region_id": _DEFAULT_REGION,
    }


# Browser data path constant
_BROWSER_DATA_PATH = "/tmp/agentbay_browser"
# Browser fingerprint persistent path constant
_BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint"
# Browser recording path constant
BROWSER_RECORD_PATH = "/home/wuying/record"

# Mobile info path constant for internal create context
_MOBILE_INFO_DEFAULT_PATH = "/data/agentbay_mobile_info"
# Mobile dev info sub path constant when append to user's context path
_MOBILE_INFO_SUB_PATH = "/agentbay_mobile_info/"
# Mobile dev info file name constant
_MOBILE_INFO_FILE_NAME = "dev_info.json"


def _find_dotenv_file(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find .env file by searching upward from start_path.

    Search order:
    1. Current working directory
    2. Parent directories (up to root)
    3. Git repository root (if found)

    Args:
        start_path: Starting directory for search (defaults to current working directory)

    Returns:
        Path to .env file if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current_path = Path(start_path).resolve()

    # Search upward until we reach root directory
    while current_path != current_path.parent:
        env_file = current_path / ".env"
        if env_file.exists():
            _logger.debug(f"Found .env file at: {env_file}")
            return env_file

        # Check if this is a git repository root
        git_dir = current_path / ".git"
        if git_dir.exists():
            _logger.debug(f"Found git repository root at: {current_path}")

        current_path = current_path.parent

    # Check root directory as well
    root_env = current_path / ".env"
    if root_env.exists():
        _logger.debug(f"Found .env file at root: {root_env}")
        return root_env

    return None


def _load_dotenv_with_fallback(custom_env_path: Optional[str] = None) -> None:
    """
    Load .env file with improved search strategy.

    Args:
        custom_env_path: Custom path to .env file (optional)
    """
    if custom_env_path:
        # Use custom path if provided
        env_path = Path(custom_env_path)
        if env_path.exists():
            dotenv.load_dotenv(env_path)
            _logger.info(f"Loaded custom .env file from: {env_path}")
            return
        else:
            _logger.warning(f"Custom .env file not found: {env_path}")

    # Find .env file using upward search
    env_file = _find_dotenv_file()
    if env_file:
        try:
            dotenv.load_dotenv(env_file)
            _logger.info(f"Loaded .env file from: {env_file}")
        except Exception as e:
            _logger.warning(f"Failed to load .env file {env_file}: {e}")
    else:
        _logger.debug("No .env file found in current directory or parent directories")


"""
Precedence (highest to lowest), evaluated independently for region_id and the
deprecated endpoint fallback:

1. Explicit cfg.region_id in code.
2. Explicit cfg.endpoint in code (deprecated fallback).
3. AGENTBAY_REGION_ID environment variable.
4. AGENTBAY_ENDPOINT environment variable (deprecated fallback).
5. Default region (cn-hangzhou).

When region_id is resolved at any level, the endpoint is derived from it via
the pattern. The endpoint fallback only kicks in when no region_id is found
at any level, and it bypasses the pattern (the value is used as-is).
"""


def _load_config(cfg, custom_env_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration with improved .env file search.

    Args:
        cfg: Configuration object (if provided, skips env loading)
        custom_env_path: Custom path to .env file (optional)

    Returns:
        Configuration dictionary with endpoint either derived from region_id
        (preferred) or taken from the deprecated endpoint fallback.
    """
    config = _default_config()
    explicit_region: Optional[str] = None
    explicit_endpoint: Optional[str] = None

    if cfg is not None:
        # When explicit config is provided, do NOT load env/.env.
        if getattr(cfg, "timeout_ms", None):
            if isinstance(cfg.timeout_ms, int) and cfg.timeout_ms > 0:
                config["timeout_ms"] = cfg.timeout_ms
        if getattr(cfg, "region_id", None):
            explicit_region = cfg.region_id
        if getattr(cfg, "endpoint", None):
            explicit_endpoint = cfg.endpoint
        # If both are set in code, region_id wins; warn that endpoint is ignored.
        if explicit_region and explicit_endpoint:
            import warnings
            warnings.warn(
                f"Config(region_id={explicit_region!r}, "
                f"endpoint={explicit_endpoint!r}): both set; endpoint is "
                "ignored because region_id takes precedence.",
                DeprecationWarning,
                stacklevel=2,
            )
            explicit_endpoint = None
    else:
        # Load .env file with improved search
        try:
            _load_dotenv_with_fallback(custom_env_path)
        except Exception as e:
            _logger.warning(f"Failed to load .env file: {e}")

        if timeout_ms := os.getenv("AGENTBAY_TIMEOUT_MS"):
            try:
                config["timeout_ms"] = int(timeout_ms)
            except ValueError:
                _logger.warning(
                    f"Invalid AGENTBAY_TIMEOUT_MS value: {timeout_ms}, using default"
                )
        if region_id := os.getenv("AGENTBAY_REGION_ID"):
            explicit_region = region_id
        if env_endpoint := os.getenv("AGENTBAY_ENDPOINT"):
            if explicit_region:
                _logger.warning(
                    f"AGENTBAY_ENDPOINT={env_endpoint!r} is deprecated and "
                    "ignored because AGENTBAY_REGION_ID is also set. Unset "
                    "AGENTBAY_ENDPOINT to silence this warning."
                )
            else:
                _logger.warning(
                    f"AGENTBAY_ENDPOINT={env_endpoint!r} is deprecated; set "
                    "AGENTBAY_REGION_ID instead. The value is used as a "
                    "fallback and will be removed in a future major version."
                )
                explicit_endpoint = env_endpoint

    if explicit_region:
        actual_region, endpoint = _resolve_endpoint(explicit_region)
        config["region_id"] = actual_region
        config["endpoint"] = endpoint
    elif explicit_endpoint:
        # Deprecated fallback: use the user-supplied endpoint verbatim.
        # region_id is left at its default so downstream code that reads it
        # (e.g. for telemetry) still has a non-empty value.
        config["endpoint"] = explicit_endpoint
    else:
        actual_region, endpoint = _resolve_endpoint(config["region_id"])
        config["region_id"] = actual_region
        config["endpoint"] = endpoint
    return config
