from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ContextMountAccessMode(Enum):
    """Access mode for context mount"""

    READ_WRITE = "readWrite"
    READ_ONLY = "readOnly"


class ContextMountStrategy(Enum):
    """Mount strategy for context mount"""

    STANDARD = "standard"
    PERFORMANCE = "performance"


@dataclass
class ContextMount:
    """
    Defines the context mount configuration for direct-mount persistence.

    Unlike ContextSync which requires explicit synchronization, ContextMount
    provides write-through persistence where data is persisted immediately
    without manual sync calls.

    Attributes:
        context_id: ID of the context to mount
        path: Path where the context should be mounted in the session
        access_mode: Access permission for the mount (read_write or read_only)
        strategy: Mount strategy (standard or performance)
    """

    context_id: str
    path: str
    access_mode: ContextMountAccessMode = ContextMountAccessMode.READ_WRITE
    strategy: ContextMountStrategy = ContextMountStrategy.STANDARD

    @classmethod
    def new(
        cls,
        context_id: str,
        path: str,
        access_mode: Optional[ContextMountAccessMode] = None,
        strategy: Optional[ContextMountStrategy] = None,
    ):
        return cls(
            context_id=context_id,
            path=path,
            access_mode=access_mode or ContextMountAccessMode.READ_WRITE,
            strategy=strategy or ContextMountStrategy.STANDARD,
        )

    def with_access_mode(self, access_mode: ContextMountAccessMode):
        self.access_mode = access_mode
        return self

    def with_strategy(self, strategy: ContextMountStrategy):
        self.strategy = strategy
        return self

    def _to_mount_config_dict(self):
        return {
            "accessMode": self.access_mode.value,
            "storageMode": self.strategy.value,
        }
