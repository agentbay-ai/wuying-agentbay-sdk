from dataclasses import dataclass
from enum import Enum
from typing import Optional


class BetaContextMountAccessMode(Enum):
    """Access mode for context mount (beta)"""

    READ_WRITE = "readWrite"
    READ_ONLY = "readOnly"


class BetaContextMountStrategy(Enum):
    """Mount strategy for context mount (beta)"""

    STANDARD = "standard"
    PERFORMANCE = "performance"


@dataclass
class BetaContextMount:
    """
    [Beta] Defines the context mount configuration for direct-mount persistence.

    Unlike ContextSync which requires explicit synchronization, BetaContextMount
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
    access_mode: BetaContextMountAccessMode = BetaContextMountAccessMode.READ_WRITE
    strategy: BetaContextMountStrategy = BetaContextMountStrategy.STANDARD

    @classmethod
    def new(
        cls,
        context_id: str,
        path: str,
        access_mode: Optional[BetaContextMountAccessMode] = None,
        strategy: Optional[BetaContextMountStrategy] = None,
    ):
        return cls(
            context_id=context_id,
            path=path,
            access_mode=access_mode or BetaContextMountAccessMode.READ_WRITE,
            strategy=strategy or BetaContextMountStrategy.STANDARD,
        )

    def with_access_mode(self, access_mode: BetaContextMountAccessMode):
        self.access_mode = access_mode
        return self

    def with_strategy(self, strategy: BetaContextMountStrategy):
        self.strategy = strategy
        return self

    def _to_mount_config_dict(self):
        return {
            "accessMode": self.access_mode.value,
            "storageMode": self.strategy.value,
        }
