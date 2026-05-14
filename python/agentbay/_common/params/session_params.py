from typing import TYPE_CHECKING, Dict, List, Optional
from enum import Enum

from agentbay.api.models._create_mcp_session_request import ExtraConfigs

from ..config import _BROWSER_FINGERPRINT_PERSIST_PATH
from ..logger import get_logger
from .lifecycle_policy import LifecyclePolicy
from .context_mount import ContextMount, ContextMountAccessMode, ContextMountStrategy
from .context_sync import (
    BWList,
    ContextSync,
    DeletePolicy,
    ExtractPolicy,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)

# Initialize _logger for this module
_logger = get_logger("session_params")

if TYPE_CHECKING:
    from ..extension import ExtensionOption
    from .browser import BrowserFingerprintContext


class BrowserSyncMode(Enum):
    """
    Browser data synchronization mode.

    Attributes:
        MINIMAL: Synchronize only essential files (Cookies, Local State).
                 Smallest footprint. Sufficient for basic cookie-based auth.
        STANDARD: Synchronize login state and anti-risk-control data.
                  Includes Cookies, localStorage, IndexedDB, saved passwords,
                  preferences, HSTS, GPU cache, etc. Recommended for most scenarios.
    """
    MINIMAL = "minimal"    # Only Cookies + Local State
    STANDARD = "standard"  # Login state + anti-risk-control (recommended)


class BrowserContext:
    """
    Browser context configuration for session.

    This class provides browser context configuration for cloud sessions, supports browser fingerprint
    context persistence, supports automatic extension synchronization when ExtensionOption is provided.

    Key Features:
    - Browser context binding for sessions
    - Automatic browser data upload on session end
    - Optional browser fingerprint integration with automatic context sync generation
    - Optional extension integration with automatic context sync generation
    - Clean API with ExtensionOption encapsulation

    Attributes:
        context_id (str): ID of the browser context to bind to the session
        auto_upload (bool): Whether to automatically upload browser data when session ends
        sync_mode (BrowserSyncMode): Browser data synchronization mode
            - MINIMAL: Only sync essential files (Cookies, Local State) - fastest
            - STANDARD: Sync login state + anti-risk-control data - recommended
        fingerprint_context (Optional[BrowserFingerprintContext]):
            Browser fingerprint context configuration object containing fingerprint_context_id.
        extension_option (Optional[ExtensionOption]): Extension configuration object containing
                                                     context_id and extension_ids.
        extension_context_id (Optional[str]): ID of the extension context for browser extensions.
                                             Set automatically from extension_option.
        extension_ids (Optional[List[str]]): List of extension IDs to synchronize.
                                           Set automatically from extension_option.
        extension_context_syncs (Optional[List[ContextSync]]): Auto-generated context syncs for extensions.
                                                              None if no extension configuration provided,
                                                              or List[ContextSync] if extensions are configured.

    Extension Configuration:
    - **ExtensionOption**: Pass an ExtensionOption object with context_id and extension_ids
    - **No Extensions**: Don't provide extension_option parameter (extension_context_syncs will be None)

    Usage Examples:
        ```python
        # With extensions using ExtensionOption
        from agentbay.extension import ExtensionOption

        ext_option = ExtensionOption(
            context_id="my_extensions",
            extension_ids=["ext1", "ext2"]
        )

        browser_context = BrowserContext(
            context_id="browser_session",
            auto_upload=True,
            extension_option=ext_option
        )

        # Without extensions (minimal configuration)
        browser_context = BrowserContext(
            context_id="browser_session",
            auto_upload=True
        )
        # extension_context_syncs will be None
        ```
    """

    def __init__(
        self,
        context_id: str,
        auto_upload: bool = True,
        sync_mode: "BrowserSyncMode" = None,
        extension_option: Optional["ExtensionOption"] = None,
        fingerprint_context: Optional["BrowserFingerprintContext"] = None,
    ):
        """
        Initialize BrowserContext with optional extension support.

        Args:
            context_id (str): ID of the browser context to bind to the session.
                             This identifies the browser instance for the session.

            auto_upload (bool, optional): Whether to automatically upload browser data
                                        when the session ends. Defaults to True.

            sync_mode (BrowserSyncMode, optional): Browser data synchronization mode.
                                                  - MINIMAL: Only sync essential files (Cookies, Local State) - fastest
                                                  - STANDARD: Sync login state + anti-risk-control data (Cookies, localStorage,
                                                    IndexedDB, passwords, preferences, HSTS, GPUCache, etc.) - recommended
                                                  Defaults to MINIMAL.

            fingerprint_context (Optional[BrowserFingerprintContext], optional):
                        Browser fingerprint context configuration object containing fingerprint_context_id.
                        Defaults to None.

            extension_option (Optional[ExtensionOption], optional): Extension configuration object containing
                                                                   context_id and extension_ids. This encapsulates
                                                                   all extension-related configuration.
                                                                   Defaults to None.
        Fingerprint Configuration:
            - **BrowserFingerprintContext**: Use fingerprint_context parameter with a BrowserFingerprintContext object
            - **No Fingerprint**: Don't provide fingerprint_context parameter (fingerprint_context_sync will be None)

        Fingerprint Auto-generation:
            - fingerprint_context_sync is automatically generated when fingerprint_context is provided
            - fingerprint_context_sync will be None if no fingerprint_context is provided
            - fingerprint_context_sync will be a ContextSync if fingerprint_context is valid

        Extension Configuration:
            - **ExtensionOption**: Use extension_option parameter with an ExtensionOption object
            - **No Extensions**: Don't provide extension_option parameter

        Auto-generation:
            - extension_context_syncs is automatically generated when extension_option is provided
            - extension_context_syncs will be None if no extension_option is provided
            - extension_context_syncs will be a List[ContextSync] if extension_option is valid

        Examples:
            ```python
            # With extensions using ExtensionOption
            from agentbay.extension import ExtensionOption

            ext_option = ExtensionOption(
                context_id="my_extensions",
                extension_ids=["ext1", "ext2"]
            )

            browser_context = BrowserContext(
                context_id="browser_session",
                auto_upload=True,
                extension_option=ext_option
            )

            # Without extensions (minimal configuration)
            browser_context = BrowserContext(
                context_id="browser_session",
                auto_upload=True
            )
            # extension_context_syncs will be None
            ```
        """
        self.context_id = context_id
        self.auto_upload = auto_upload
        self.sync_mode = sync_mode if sync_mode is not None else BrowserSyncMode.STANDARD
        self.extension_option = extension_option
        self.fingerprint_context = fingerprint_context

        # Handle extension configuration from ExtensionOption
        if extension_option:
            # Extract extension information from ExtensionOption
            self.extension_context_id = extension_option.context_id
            self.extension_ids = extension_option.extension_ids
            # Auto-generate extension context syncs
            self.extension_context_syncs = self._create_extension_context_syncs()
        else:
            # No extension configuration provided
            self.extension_context_id = None
            self.extension_ids = []
            self.extension_context_syncs = None

        # Handle browser fingerprint configuration from BrowserFingerprintContext
        if fingerprint_context:
            self.fingerprint_context_id = fingerprint_context.fingerprint_context_id
            # Auto-generate fingerprint context sync
            self.fingerprint_context_sync = self._create_fingerprint_context_sync()
        else:
            self.fingerprint_context_id = None
            self.fingerprint_context_sync = None

    def _create_extension_context_syncs(self) -> List[ContextSync]:
        """
        Create ContextSync configurations for browser extensions.

        This method is called only when extension_option is provided and contains
        valid extension configuration (context_id and extension_ids).

        Returns:
            List[ContextSync]: List of context sync configurations for extensions.
                              Returns empty list if extension configuration is invalid.
        """
        if not self.extension_ids or not self.extension_context_id:
            return []

        # Create whitelist for each extension ID
        white_lists = [
            WhiteList(path=f"{ext_id}", exclude_paths=[])
            for ext_id in self.extension_ids
        ]

        # Create sync policy for extensions
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=False),
            delete_policy=DeletePolicy(sync_local_file=False),
            extract_policy=ExtractPolicy(extract=True, delete_src_file=True),
            recycle_policy=RecyclePolicy.default(),
            bw_list=BWList(white_lists=white_lists),
        )

        # Create context sync for extensions
        extension_sync = ContextSync(
            context_id=self.extension_context_id,
            path="/tmp/extensions/",
            policy=sync_policy,
        )

        return [extension_sync]

    def _create_fingerprint_context_sync(self) -> ContextSync:
        """
        Create ContextSync configurations for browser fingerprint.

        This method is called only when fingerprint_context is provided and contains
        valid fingerprint configuration (fingerprint_context_id).

        Returns:
            ContextSync: Context sync configurations for fingerprint.
                         Returns None if fingerprint configuration is invalid.
        """
        if not self.fingerprint_context_id or not self.fingerprint_context_id.strip():
            return None

        # Create whitelist for fingerprint context
        white_lists = []

        # Create sync policy for fingerprint
        sync_policy = SyncPolicy(
            upload_policy=UploadPolicy(auto_upload=False),
            extract_policy=ExtractPolicy(extract=True, delete_src_file=True),
            bw_list=BWList(white_lists=white_lists),
        )

        # Create context sync for fingerprint
        fingerprint_sync = ContextSync(
            context_id=self.fingerprint_context_id,
            path=_BROWSER_FINGERPRINT_PERSIST_PATH,
            policy=sync_policy,
        )

        return fingerprint_sync

    def get_extension_context_syncs(self) -> List[ContextSync]:
        """
        Get context syncs for extensions.

        Returns:
            List[ContextSync]: Context sync configurations for extensions.
                               Returns empty list if no extensions configured.
        """
        return self.extension_context_syncs or []

    def get_fingerprint_context_sync(self) -> ContextSync:
        """
        Get context sync for fingerprint.

        Returns:
            ContextSync: Context sync configurations for fingerprint.
                         Returns None if fingerprint configuration is invalid.
        """
        return self.fingerprint_context_sync


class CreateSessionParams:
    """
    Parameters for creating a new session in the AgentBay cloud environment.

    Attributes:
        labels (Optional[Dict[str, str]]): Custom labels for the Session. These can be
            used for organizing and filtering sessions.
        idle_release_timeout (Optional[int]): SDK-side idle release timeout in seconds.
            Deprecated for lifecycle control: use ``lifecycle_policy`` instead.
            Mutually exclusive with ``lifecycle_policy``.
            This parameter takes effect together with console-side MCP/user interaction
            idle timeouts. The cloud environment is automatically released only when
            all idle timeouts are reached (or when the single-run maximum duration is reached).
        lifecycle_policy (Optional[LifecyclePolicy]): Full lifecycle control (minutes).
            Mutually exclusive with ``idle_release_timeout``. When set, SDK takes full
            control of session lifecycle (console defaults are overridden).
        context_syncs (Optional[List[ContextSync]]): List of context synchronization
            configurations that define how contexts should be synchronized and mounted.
        browser_context (Optional[BrowserContext]): Optional configuration for browser data synchronization.
        policy_id (Optional[str]): Policy id to apply when creating the session.
        enable_browser_replay (Optional[bool]): Whether to enable browser recording for the session. When not set (None), the server-side default behavior applies. Set to True to enable, False to disable
        extra_configs (Optional[ExtraConfigs]): Advanced configuration parameters for mobile environments.
        framework (Optional[str]): Framework name for tracking (e.g., "langchain"). Defaults to empty string (direct call).
        beta_network_id (Optional[str]): Beta network ID to bind this session to.
        load_skills (Optional[bool]): Whether to load skills into the sandbox.
        skill_names (Optional[List[str]]): Skill names to load. Loads all visible skills when load_skills=True and this is not specified.
    """

    def __init__(
        self,
        labels: Optional[Dict[str, str]] = None,
        image_id: Optional[str] = None,
        idle_release_timeout: Optional[int] = None,
        lifecycle_policy: Optional[LifecyclePolicy] = None,
        context_syncs: Optional[List[ContextSync]] = None,
        context_mounts: Optional[List[ContextMount]] = None,
        browser_context: Optional[BrowserContext] = None,
        policy_id: Optional[str] = None,
        beta_network_id: Optional[str] = None,
        enable_browser_replay: Optional[bool] = None,
        extra_configs: Optional[ExtraConfigs] = None,
        framework: Optional[str] = None,
        load_skills: Optional[bool] = None,
        skill_names: Optional[List[str]] = None,
    ):
        """
        Initialize CreateSessionParams.

        Args:
            labels (Optional[Dict[str, str]], optional): Custom labels for the Session.
                Defaults to None.
            image_id (Optional[str], optional): ID of the image to use for the session.
                Defaults to None.
            idle_release_timeout (Optional[int], optional): SDK-side idle release timeout in seconds.
                Mutually exclusive with lifecycle_policy.
            lifecycle_policy (Optional[LifecyclePolicy], optional): Lifecycle policy (minutes).
                Mutually exclusive with idle_release_timeout.
            context_syncs (Optional[List[ContextSync]], optional): List of context
                synchronization configurations. Defaults to None.
            browser_context (Optional[BrowserContext], optional): Browser context configuration.
                If extension_ids are provided in BrowserContext, extension syncs will be
                automatically added. Defaults to None.
            policy_id (Optional[str], optional): Policy id to apply when creating the session.
                Defaults to None.
            beta_network_id (Optional[str], optional): Beta network ID to bind this session to.
                Defaults to None.
            enable_browser_replay (Optional[bool], optional): Whether to enable browser recording for the session.
                When not set, server-side default behavior applies. Set to True to enable, False to disable.
            extra_configs (Optional[ExtraConfigs], optional): Advanced configuration parameters for mobile environments.
                Defaults to None.
            framework (Optional[str], optional): Framework name for tracking (e.g., "langchain").
                Defaults to None (empty string in tracking, indicating direct call).
        """
        self.labels = labels or {}
        self.image_id = image_id
        if lifecycle_policy is not None and idle_release_timeout is not None:
            raise ValueError(
                "idle_release_timeout is deprecated, use lifecycle_policy.idle_release_timeout instead. Cannot set both."
            )
        if idle_release_timeout is not None:
            if not isinstance(idle_release_timeout, int):
                raise ValueError(
                    "idle_release_timeout must be an int (seconds)")
            if idle_release_timeout <= 0:
                raise ValueError("idle_release_timeout must be > 0 (seconds)")
        self.idle_release_timeout = idle_release_timeout
        self.lifecycle_policy = lifecycle_policy

        # Start with provided context_syncs
        all_context_syncs = list(context_syncs or [])

        # Add extension context syncs from browser_context if available
        if browser_context and browser_context.extension_context_syncs:
            all_context_syncs.extend(browser_context.extension_context_syncs)
            _logger.info(
                f"Added {len(browser_context.extension_context_syncs)} extension context sync(s) from BrowserContext"
            )

        # Add fingerprint context sync from browser_context if available
        if browser_context and browser_context.fingerprint_context_sync:
            all_context_syncs.append(browser_context.fingerprint_context_sync)
            _logger.info(f"Added fingerprint context sync from BrowserContext")

        self.context_syncs = all_context_syncs
        self.context_mounts = list(context_mounts or [])
        self.browser_context = browser_context
        self.policy_id = policy_id
        self.beta_network_id = beta_network_id
        # Keep None if not provided - server-side default behavior applies
        self.enable_browser_replay = enable_browser_replay
        self.extra_configs = extra_configs
        self.framework = framework or ""
        self.load_skills = load_skills
        self.skill_names = skill_names


class ListSessionParams:
    """
    Parameters for listing sessions with pagination support.

    Attributes:
        max_results (int): Number of results per page.
        next_token (str): Token for the next page.
        labels (Dict[str, str]): Labels to filter by.
    """

    def __init__(
        self,
        max_results: int = 10,
        next_token: str = "",
        labels: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize ListSessionParams with default values.

        Args:
            max_results (int, optional): Number of results per page. Defaults to 10.
            next_token (str, optional): Token for the next page. Defaults to "".
            labels (Optional[Dict[str, str]], optional): Labels to filter by.
                Defaults to None.
        """
        self.max_results = max_results
        self.next_token = next_token
        self.labels = labels if labels is not None else {}
