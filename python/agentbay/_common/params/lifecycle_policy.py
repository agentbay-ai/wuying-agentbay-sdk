from typing import Optional


class LifecyclePolicy:
    """
    Lifecycle policy for session management.

    Controls how and when a session is automatically released.
    When used, SDK takes full control of lifecycle — console defaults are overridden.

    All time values are in MINUTES.

    Attributes:
        idle_release_timeout: Minutes of inactivity before auto-release (default: 5).
        max_runtime: Maximum total runtime in minutes from creation (default: 30).
        manual_release: If True, disables all auto-release; session only ends via delete().
    """

    def __init__(
        self,
        idle_release_timeout: Optional[int] = None,
        max_runtime: Optional[int] = None,
        manual_release: bool = False,
    ):
        if manual_release:
            if idle_release_timeout is not None:
                raise ValueError(
                    "idle_release_timeout cannot be set when manual_release=True. "
                    "In manual release mode, the session is only released via delete()."
                )
            if max_runtime is not None:
                raise ValueError(
                    "max_runtime cannot be set when manual_release=True. "
                    "In manual release mode, the session is only released via delete()."
                )
            self.idle_release_timeout = 0
            self.max_runtime = 0
            self.manual_release = True
            return

        resolved_idle = idle_release_timeout if idle_release_timeout is not None else 5
        resolved_max = max_runtime if max_runtime is not None else 30

        if not isinstance(resolved_idle, int) or isinstance(resolved_idle, bool):
            raise ValueError("idle_release_timeout must be a positive integer (minutes)")
        if resolved_idle <= 0:
            raise ValueError("idle_release_timeout must be a positive integer (minutes)")

        if not isinstance(resolved_max, int) or isinstance(resolved_max, bool):
            raise ValueError("max_runtime must be a positive integer (minutes)")
        if resolved_max <= 0:
            raise ValueError("max_runtime must be a positive integer (minutes)")

        self.idle_release_timeout = resolved_idle
        self.max_runtime = resolved_max
        self.manual_release = False
