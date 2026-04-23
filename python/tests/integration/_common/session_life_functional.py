"""
Session lifecycle functional helpers.

Provides two classes for managing session lifecycles:
  - AsyncSessionLifecycle  (for AsyncAgentBay)
  - SyncSessionLifecycle   (for AgentBay / sync)

Both classes support:
  - Creating a session (default or with ContextSync)
  - Deleting the session
  - Querying session status via get_status()

Errors during create / delete raise SessionLifecycleError so that test code
can catch them explicitly.
"""

from __future__ import annotations

import os
from typing import Optional

from agentbay import AsyncAgentBay, AgentBay, CreateSessionParams, BrowserContext
from agentbay._common.exceptions import SessionError
from agentbay._common.params.context_sync import ContextSync


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------


class SessionLifecycleError(Exception):
    """Raised when a session lifecycle operation (create / delete) fails."""

    def __init__(self, message: str, cause: Optional[Exception] = None):
        super().__init__(message)
        self.cause = cause

    def __str__(self) -> str:
        base = super().__str__()
        if self.cause is not None:
            return f"{base} | caused by: {self.cause!r}"
        return base


# ---------------------------------------------------------------------------
# Async variant
# ---------------------------------------------------------------------------


class AsyncSessionLifecycle:
    """
    Manages a single AsyncAgentBay session lifecycle.

    Usage example (pytest)::

        @pytest.fixture(scope="module")
        async def lifecycle():
            mgr = AsyncSessionLifecycle()
            yield mgr
            await mgr.delete()

        @pytest.mark.asyncio
        async def test_something(lifecycle):
            result = await lifecycle.default_create("linux_latest")
            assert result.success
            status = await lifecycle.get_status()
            assert status.success
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Args:
            api_key: AgentBay API key. Falls back to ``AGENTBAY_API_KEY`` env var.
        """
        resolved_key = api_key or os.environ.get("AGENTBAY_API_KEY") or ""
        if not resolved_key:
            raise SessionLifecycleError(
                "API key is required. Set AGENTBAY_API_KEY or pass api_key."
            )
        self._agent_bay = AsyncAgentBay(api_key=resolved_key)
        # Stores the SessionResult from the last create call
        self._result = None
        # Whether to sync context data when deleting the session.
        # True for context_name / browser_name sessions, False for default sessions.
        self._sync_context = False
        # Tracks all contexts created via create_context(); deleted by delete_all_contexts()
        self._owned_contexts: list = []

    @property
    def agent_bay(self) -> AsyncAgentBay:
        """Public accessor for the underlying AsyncAgentBay client.

        Useful when a test needs to call AgentBay-level APIs (e.g. list, get,
        delete, context.*) alongside the session managed by this lifecycle.
        """
        return self._agent_bay

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    async def create_context(self, name: str) -> object:
        """Get or create a named context and track it for cleanup.

        Calls ``agent_bay.context.get(name, create=True)`` to resolve the
        context, caches it in ``_owned_contexts``, and returns the context
        object so callers can use its ``id`` directly.

        Args:
            name: Context name to look up or create.

        Returns:
            The context object (with ``.id`` and ``.name`` attributes).

        Raises:
            SessionLifecycleError: If the API call fails.
        """
        try:
            result = await self._agent_bay.context.get(name, create=True)
        except Exception as exc:
            raise SessionLifecycleError(
                f"context.get({name!r}) raised an exception",
                cause=exc,
            ) from exc

        if not result.success or result.context is None:
            raise SessionLifecycleError(
                f"Failed to get/create context {name!r}: {result.error_message}"
            )

        self._owned_contexts.append(result.context)
        print(f"Context created/resolved: {result.context.name} (ID: {result.context.id})")
        return result.context

    async def delete_all_contexts(self) -> None:
        """Delete all contexts previously created via :meth:`create_context`.

        Errors are printed as warnings and do not raise, so teardown always
        completes even when individual deletes fail.
        """
        for context in self._owned_contexts:
            try:
                await self._agent_bay.context.delete(context)
                print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context {context.id}: {e}")
        self._owned_contexts.clear()

    async def default_create(
        self,
        image_id: Optional[str] = None,
        params: Optional[CreateSessionParams] = None,
    ) -> object:
        """
        Create a session and cache the result.

        Args:
            image_id: Convenience shorthand – creates a ``CreateSessionParams``
                      with only ``image_id`` set.  Ignored when *params* is given.
            params: Full :class:`CreateSessionParams` to use.  When provided,
                    *image_id* is ignored.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        if params is None:
            params = CreateSessionParams(image_id=image_id)
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session: {result.error_message}"
            )
        self._result = result
        self._sync_context = False
        return result

    async def create_with_context_name(
        self,
        image_id: str,
        context_name: str,
        path: str,
        policy: object,
    ) -> object:
        """
        Create a session with a ContextSync built from a context name.

        Internally calls ``agent_bay.context.get(context_name, create=True)`` to
        resolve the context ID, then assembles a :class:`ContextSync` and creates the
        session.  Everything uses the same ``self._agent_bay`` instance so the resulting
        session belongs to the same account / connection as any other session created
        by this lifecycle object.

        Args:
            image_id: The image ID to create the session with.
            context_name: Name of the context to look up or create.
            path: The local path for the ContextSync.
            policy: Required :class:`SyncPolicy` to attach to the ContextSync.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If context lookup or session creation fails.
        """
        if policy is None:
            raise SessionLifecycleError(
                "policy is required for create_with_context_name(). "
                "Please provide a SyncPolicy instance."
            )
        ctx = await self.create_context(context_name)
        context_sync = ContextSync(
            ctx.id,
            path=path,
            policy=policy,
        )
        params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
        )
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create (with context_name) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session with context_name: {result.error_message}"
            )
        self._result = result
        self._sync_context = True
        return result

    async def create_with_browser_name(
        self,
        image_id: str,
        context_name: str,
        **kwargs,
    ) -> object:
        """
        Create a browser session with a BrowserContext built from a context name.

        Internally calls ``agent_bay.context.get(context_name, create=True)`` to
        resolve the context ID, then assembles a :class:`BrowserContext` using the
        resolved ID and any extra keyword arguments, and delegates to the standard
        session-create path.  Everything uses the same ``self._agent_bay`` instance.

        Args:
            image_id: The image ID to create the session with (e.g. ``"browser_latest"``).
            context_name: Name of the browser context to look up or create.
            **kwargs: Extra keyword arguments forwarded to :class:`BrowserContext`
                      (e.g. ``auto_upload=True``, ``sync_mode=...``,
                      ``extension_option=...``, ``fingerprint_context=...``).

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If context lookup or session creation fails.
        """
        ctx = await self.create_context(context_name)
        browser_context = BrowserContext(ctx.id, **kwargs)
        params = CreateSessionParams(image_id=image_id)
        params.browser_context = browser_context
        try:
            result = await self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.create (with browser_name) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create browser session: {result.error_message}"
            )

        self._result = result
        self._sync_context = True
        return result

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    async def get_status(self) -> str:
        """
        Call ``session.get_status()`` on the currently cached session.

        Returns:
            str: The session status string (e.g. ``"Running"``） when the call succeeds.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call returns success=False, or if an
                                   unexpected exception occurs.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create(), create_with_context_name(), or create_with_browser_name() first."
            )
        try:
            status_result = await self._result.session.get_status()
            print(f"Session status: {status_result.status}")
        except SessionError:
            raise
        except Exception as exc:
            raise SessionLifecycleError(
                "get_status() raised an unexpected exception",
                cause=exc,
            ) from exc

        if not status_result.success:
            raise SessionLifecycleError(
                f"get_status() failed: {status_result.error_message}"
            )
        return status_result.status

    # ------------------------------------------------------------------
    # Session deletion
    # ------------------------------------------------------------------

    async def delete(self) -> object:
        """
        Delete the currently cached session.

        Uses ``sync_context=True`` automatically when the session was created
        via :meth:`create_with_context_name` or :meth:`create_with_browser_name`,
        and ``sync_context=False`` for sessions created via :meth:`default_create`.

        Returns:
            DeleteResult.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call raises, or if deletion returns
                                   success=False.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create(), create_with_context_name(), or create_with_browser_name() first."
            )
        session = self._result.session
        try:
            result = await self._agent_bay.delete(session, sync_context=self._sync_context)
        except Exception as exc:
            raise SessionLifecycleError(
                "AsyncAgentBay.delete raised an exception",
                cause=exc,
            ) from exc

        if not result.success:
            raise SessionLifecycleError(
                f"Failed to delete session: {result.error_message}"
            )

        self._result = None
        self._sync_context = False
        return result


# ---------------------------------------------------------------------------
# Sync variant
# ---------------------------------------------------------------------------


class SyncSessionLifecycle:
    """
    Manages a single AgentBay (sync) session lifecycle.

    Usage example (pytest)::

        @pytest.fixture(scope="module")
        def lifecycle():
            mgr = SyncSessionLifecycle()
            yield mgr
            mgr.delete()

        @pytest.mark.asyncio
        def test_something(lifecycle):
            result = lifecycle.default_create("linux_latest")
            assert result.success
            status = lifecycle.get_status()
            assert status.success
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        """
        Args:
            api_key: AgentBay API key. Falls back to ``AGENTBAY_API_KEY`` env var.
        """
        resolved_key = api_key or os.environ.get("AGENTBAY_API_KEY") or ""
        if not resolved_key:
            raise SessionLifecycleError(
                "API key is required. Set AGENTBAY_API_KEY or pass api_key."
            )
        self._agent_bay = AgentBay(api_key=resolved_key)
        # Stores the SessionResult from the last create call
        self._result = None
        # Whether to sync context data when deleting the session.
        # True for context_name / browser_name sessions, False for default sessions.
        self._sync_context = False
        # Tracks all contexts created via create_context(); deleted by delete_all_contexts()
        self._owned_contexts: list = []

    @property
    def agent_bay(self) -> AgentBay:
        """Public accessor for the underlying AgentBay client.

        Useful when a test needs to call AgentBay-level APIs (e.g. list, get,
        delete, context.*) alongside the session managed by this lifecycle.
        """
        return self._agent_bay

    # ------------------------------------------------------------------
    # Context helpers
    # ------------------------------------------------------------------

    def create_context(self, name: str) -> object:
        """Get or create a named context and track it for cleanup.

        Calls ``agent_bay.context.get(name, create=True)`` to resolve the
        context, caches it in ``_owned_contexts``, and returns the context
        object so callers can use its ``id`` directly.

        Args:
            name: Context name to look up or create.

        Returns:
            The context object (with ``.id`` and ``.name`` attributes).

        Raises:
            SessionLifecycleError: If the API call fails.
        """
        try:
            result = self._agent_bay.context.get(name, create=True)
        except Exception as exc:
            raise SessionLifecycleError(
                f"context.get({name!r}) raised an exception",
                cause=exc,
            ) from exc

        if not result.success or result.context is None:
            raise SessionLifecycleError(
                f"Failed to get/create context {name!r}: {result.error_message}"
            )

        self._owned_contexts.append(result.context)
        print(f"Context created/resolved: {result.context.name} (ID: {result.context.id})")
        return result.context

    def delete_all_contexts(self) -> None:
        """Delete all contexts previously created via :meth:`create_context`.

        Errors are printed as warnings and do not raise, so teardown always
        completes even when individual deletes fail.
        """
        for context in self._owned_contexts:
            try:
                self._agent_bay.context.delete(context)
                print(f"Context deleted: {context.id}")
            except Exception as e:
                print(f"Warning: Failed to delete context {context.id}: {e}")
        self._owned_contexts.clear()

    def default_create(
        self,
        image_id: Optional[str] = None,
        params: Optional[CreateSessionParams] = None,
    ) -> object:
        """
        Create a session and cache the result.

        Args:
            image_id: Convenience shorthand – creates a ``CreateSessionParams``
                      with only ``image_id`` set.  Ignored when *params* is given.
            params: Full :class:`CreateSessionParams` to use.  When provided,
                    *image_id* is ignored.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If the API call fails or returns success=False.
        """
        if params is None:
            params = CreateSessionParams(image_id=image_id)
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session: {result.error_message}"
            )
        self._result = result
        self._sync_context = False
        return result

    def create_with_context_name(
        self,
        image_id: str,
        context_name: str,
        path: str,
        policy: object,
    ) -> object:
        """
        Create a session with a ContextSync built from a context name.

        Internally calls ``agent_bay.context.get(context_name, create=True)`` to
        resolve the context ID, then assembles a :class:`ContextSync` and creates the
        session.  Everything uses the same ``self._agent_bay`` instance so the resulting
        session belongs to the same account / connection as any other session created
        by this lifecycle object.

        Args:
            image_id: The image ID to create the session with.
            context_name: Name of the context to look up or create.
            path: The local path for the ContextSync.
            policy: Required :class:`SyncPolicy` to attach to the ContextSync.

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If context lookup or session creation fails.
        """
        if policy is None:
            raise SessionLifecycleError(
                "policy is required for create_with_context_name(). "
                "Please provide a SyncPolicy instance."
            )
        ctx = self.create_context(context_name)
        context_sync = ContextSync(
            ctx.id,
            path=path,
            policy=policy,
        )
        params = CreateSessionParams(
            image_id=image_id,
            context_syncs=[context_sync],
        )
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create (with context_name) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create session with context_name: {result.error_message}"
            )
        self._result = result
        self._sync_context = True
        return result

    def create_with_browser_name(
        self,
        image_id: str,
        context_name: str,
        **kwargs,
    ) -> object:
        """
        Create a browser session with a BrowserContext built from a context name.

        Internally calls ``agent_bay.context.get(context_name, create=True)`` to
        resolve the context ID, then assembles a :class:`BrowserContext` using the
        resolved ID and any extra keyword arguments, and delegates to the standard
        session-create path.  Everything uses the same ``self._agent_bay`` instance.

        Args:
            image_id: The image ID to create the session with (e.g. ``"browser_latest"``).
            context_name: Name of the browser context to look up or create.
            **kwargs: Extra keyword arguments forwarded to :class:`BrowserContext`
                      (e.g. ``auto_upload=True``, ``sync_mode=...``,
                      ``extension_option=...``, ``fingerprint_context=...``).

        Returns:
            SessionResult: The full result object from AgentBay.create().

        Raises:
            SessionLifecycleError: If context lookup or session creation fails.
        """
        ctx = self.create_context(context_name)
        browser_context = BrowserContext(ctx.id, **kwargs)
        params = CreateSessionParams(image_id=image_id)
        params.browser_context = browser_context
        try:
            result = self._agent_bay.create(params)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.create (with browser_name) raised an exception",
                cause=exc,
            ) from exc

        if not result.success and result.error_message and "no authorized app" in result.error_message:
            raise SessionLifecycleError(
                f"The user has no authorized app instance: {result.error_message}"
            )
        if not result.success or result.session is None:
            raise SessionLifecycleError(
                f"Failed to create browser session: {result.error_message}"
            )

        self._result = result
        self._sync_context = True
        return result

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def get_status(self) -> str:
        """
        Call ``session.get_status()`` on the currently cached session.

        Returns:
            str: The session status string (e.g. ``"Running"``） when the call succeeds.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call returns success=False, or if an
                                   unexpected exception occurs.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create(), create_with_context_name(), or create_with_browser_name() first."
            )
        try:
            status_result = self._result.session.get_status()
            print(f"Session status: {status_result.status}")
        except SessionError:
            raise
        except Exception as exc:
            raise SessionLifecycleError(
                "get_status() raised an unexpected exception",
                cause=exc,
            ) from exc

        if not status_result.success:
            raise SessionLifecycleError(
                f"get_status() failed: {status_result.error_message}"
            )
        return status_result.status

    # ------------------------------------------------------------------
    # Session deletion
    # ------------------------------------------------------------------

    def delete(self) -> object:
        """
        Delete the currently cached session.

        Uses ``sync_context=True`` automatically when the session was created
        via :meth:`create_with_context_name` or :meth:`create_with_browser_name`,
        and ``sync_context=False`` for sessions created via :meth:`default_create`.

        Returns:
            DeleteResult.

        Raises:
            SessionLifecycleError: If no session has been created yet, if the
                                   API call raises, or if deletion returns
                                   success=False.
        """
        if self._result is None or self._result.session is None:
            raise SessionLifecycleError(
                "No active session. Call default_create(), create_with_context_name(), or create_with_browser_name() first."
            )
        session = self._result.session
        try:
            result = self._agent_bay.delete(session, sync_context=self._sync_context)
        except Exception as exc:
            raise SessionLifecycleError(
                "AgentBay.delete raised an exception",
                cause=exc,
            ) from exc

        if not result.success:
            raise SessionLifecycleError(
                f"Failed to delete session: {result.error_message}"
            )

        self._result = None
        self._sync_context = False
        return result


