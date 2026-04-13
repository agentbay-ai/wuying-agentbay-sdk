import re
import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class UploadStrategy(Enum):
    """Upload strategy for context synchronization"""

    UPLOAD_BEFORE_RESOURCE_RELEASE = "UploadBeforeResourceRelease"


class DownloadStrategy(Enum):
    """Download strategy for context synchronization"""

    DOWNLOAD_ASYNC = "DownloadAsync"


class UploadMode(Enum):
    """Upload mode for context synchronization"""

    FILE = "File"
    ARCHIVE = "Archive"


class Lifecycle(Enum):
    """Lifecycle options for recycle policy"""

    LIFECYCLE_1DAY = "Lifecycle_1Day"
    LIFECYCLE_3DAYS = "Lifecycle_3Days"
    LIFECYCLE_5DAYS = "Lifecycle_5Days"
    LIFECYCLE_10DAYS = "Lifecycle_10Days"
    LIFECYCLE_15DAYS = "Lifecycle_15Days"
    LIFECYCLE_30DAYS = "Lifecycle_30Days"
    LIFECYCLE_90DAYS = "Lifecycle_90Days"
    LIFECYCLE_180DAYS = "Lifecycle_180Days"
    LIFECYCLE_360DAYS = "Lifecycle_360Days"
    LIFECYCLE_FOREVER = "Lifecycle_Forever"


@dataclass
class UploadPolicy:
    """
    Defines the upload policy for context synchronization

    Attributes:
        auto_upload: Enables automatic upload
        upload_strategy: Defines the upload strategy
        upload_mode: Defines the upload mode (UploadMode.FILE or UploadMode.ARCHIVE)
    """

    auto_upload: bool = True
    upload_strategy: UploadStrategy = UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
    upload_mode: UploadMode = UploadMode.FILE

    def __post_init__(self):
        """Validate upload_mode value"""
        if not isinstance(self.upload_mode, UploadMode):
            valid_values = [e.value for e in UploadMode]
            raise ValueError(
                f"Invalid upload_mode value: {self.upload_mode}. "
                f"Valid values are: {', '.join(valid_values)}"
            )

    @classmethod
    def default(cls):
        """Creates a new upload policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            auto_upload=self.auto_upload,
            upload_strategy=self.upload_strategy,
            upload_mode=self.upload_mode,
        )

    def __dict__(self):
        return {
            "autoUpload": self.auto_upload,
            "uploadStrategy": (
                self.upload_strategy.value if self.upload_strategy else None
            ),
            "uploadMode": self.upload_mode.value if self.upload_mode else None,
        }


@dataclass
class DownloadPolicy:
    """
    Defines the download policy for context synchronization

    Attributes:
        auto_download: Enables automatic download
        download_strategy: Defines the download strategy
    """

    auto_download: bool = True
    download_strategy: DownloadStrategy = DownloadStrategy.DOWNLOAD_ASYNC

    @classmethod
    def default(cls):
        """Creates a new download policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            auto_download=self.auto_download,
            download_strategy=self.download_strategy,
        )

    def __dict__(self):
        return {
            "autoDownload": self.auto_download,
            "downloadStrategy": (
                self.download_strategy.value if self.download_strategy else None
            ),
        }


@dataclass
class DeletePolicy:
    """
    Defines the delete policy for context synchronization

    Attributes:
        sync_local_file: Enables synchronization of local file deletions
    """

    sync_local_file: bool = True

    @classmethod
    def default(cls):
        """Creates a new delete policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(sync_local_file=self.sync_local_file)

    def __dict__(self):
        return {"syncLocalFile": self.sync_local_file}


@dataclass
class ExtractPolicy:
    """
    Defines the extract policy for context synchronization

    Attributes:
        extract: Enables file extraction
        delete_src_file: Enables deletion of source file after extraction
        extract_current_folder: Enables extraction to the current folder
    """

    extract: bool = True
    delete_src_file: bool = True
    extract_current_folder: bool = False

    @classmethod
    def default(cls):
        """Creates a new extract policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            extract=self.extract,
            delete_src_file=self.delete_src_file,
            extract_current_folder=self.extract_current_folder,
        )

    def __dict__(self):
        return {
            "extract": self.extract,
            "deleteSrcFile": self.delete_src_file,
            "extractToCurrentFolder": self.extract_current_folder,
        }


@dataclass
class RecyclePolicy:
    """
    Defines the recycle policy for context synchronization

    Attributes:
        lifecycle: Defines how long the context data should be retained
            Available options:
            - LIFECYCLE_1DAY: Keep data for 1 day
            - LIFECYCLE_3DAYS: Keep data for 3 days
            - LIFECYCLE_5DAYS: Keep data for 5 days
            - LIFECYCLE_10DAYS: Keep data for 10 days
            - LIFECYCLE_15DAYS: Keep data for 15 days
            - LIFECYCLE_30DAYS: Keep data for 30 days
            - LIFECYCLE_90DAYS: Keep data for 90 days
            - LIFECYCLE_180DAYS: Keep data for 180 days
            - LIFECYCLE_360DAYS: Keep data for 360 days
            - LIFECYCLE_FOREVER: Keep data permanently (default)
        paths: Specifies which directories or files should be subject to the recycle policy
            Rules:
            - Must use exact directory/file paths
            - Wildcard patterns (* ? [ ]) are NOT supported
            - Empty string "" means apply to all paths in the context
            - Multiple paths can be specified as a list
            Default: [""] (applies to all paths)
    """

    lifecycle: Lifecycle = Lifecycle.LIFECYCLE_FOREVER
    paths: List[str] = field(default_factory=lambda: [""])

    def __post_init__(self):
        """Validate lifecycle and paths configuration"""
        # Validate lifecycle value
        if not isinstance(self.lifecycle, Lifecycle):
            valid_values = [e.value for e in Lifecycle]
            raise ValueError(
                f"Invalid lifecycle value: {self.lifecycle}. "
                f"Valid values are: {', '.join(valid_values)}"
            )

        # Validate that paths don't contain wildcard patterns
        for path in self.paths:
            if path and path.strip() != "" and self._contains_wildcard(path):
                raise ValueError(
                    f"Wildcard patterns are not supported in recycle policy paths. Got: {path}. "
                    "Please use exact directory paths instead."
                )

    @staticmethod
    def _contains_wildcard(path: str) -> bool:
        """Check if path contains wildcard characters"""
        return bool(re.search(r"[*?\[\]]", path))

    @classmethod
    def default(cls):
        """Creates a new recycle policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            lifecycle=self.lifecycle,
            paths=copy.deepcopy(self.paths, memo),
        )

    def __dict__(self):
        return {
            "lifecycle": self.lifecycle.value if self.lifecycle else None,
            "paths": self.paths,
        }


@dataclass
class WhiteList:
    """
    Defines the white list configuration

    Attributes:
        path: Path to include in the white list.
            When is_path_regex is False (default), this must be an exact absolute directory path
            and wildcard characters are not allowed.
            When is_path_regex is True, this is treated as a regex pattern (e.g. "/home/wuying/.*").
        exclude_paths: Paths to exclude from the white list.
            When is_exclude_regex is False (default), these must be exact absolute directory paths
            and wildcard characters are not allowed.
            When is_exclude_regex is True, these are treated as regex patterns.
        is_path_regex: If True, path is interpreted as a regex pattern.
            If False (default), path is an absolute directory path.
        is_exclude_regex: If True, exclude_paths entries are interpreted as regex patterns.
            If False (default), exclude_paths entries are absolute directory paths.
    """

    path: str = ""
    exclude_paths: List[str] = field(default_factory=list)
    is_path_regex: bool = False
    is_exclude_regex: bool = False

    def __post_init__(self):
        """Validate that non-regex paths don't contain wildcard patterns"""
        if not self.is_path_regex and self._contains_wildcard(self.path):
            raise ValueError(
                f"Wildcard patterns are not supported in path when is_path_regex=False. Got: {self.path}. "
                "Please use exact directory paths or set is_path_regex=True for regex matching."
            )
        if not self.is_exclude_regex:
            for exclude_path in self.exclude_paths:
                if self._contains_wildcard(exclude_path):
                    raise ValueError(
                        f"Wildcard patterns are not supported in exclude_paths when is_exclude_regex=False. "
                        f"Got: {exclude_path}. "
                        "Please use exact directory paths or set is_exclude_regex=True for regex matching."
                    )

    @staticmethod
    def _contains_wildcard(path: str) -> bool:
        """Check if path contains wildcard characters"""
        return bool(re.search(r"[*?\[\]]", path))

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            path=self.path,
            exclude_paths=copy.deepcopy(self.exclude_paths, memo),
            is_path_regex=self.is_path_regex,
            is_exclude_regex=self.is_exclude_regex,
        )

    def __dict__(self):
        result = {
            "path": self.path,
            "excludePaths": self.exclude_paths,
            "isPathRegex": self.is_path_regex,
            "isExcludeRegex": self.is_exclude_regex,
        }
        return result


@dataclass
class BWList:
    """
    Defines the black and white list configuration

    Attributes:
        white_lists: Defines the white lists
    """

    white_lists: List[WhiteList] = field(default_factory=list)

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            white_lists=copy.deepcopy(self.white_lists, memo),
        )

    def __dict__(self):
        return {
            "whiteLists": (
                [wl.__dict__() for wl in self.white_lists] if self.white_lists else []
            )
        }


@dataclass
class MappingPolicy:
    """
    Defines the mapping policy for cross-platform context synchronization

    Attributes:
        path: The original path from a different OS that should be mapped to the current context path
    """

    path: str = ""

    @classmethod
    def default(cls):
        """Creates a new mapping policy with default values"""
        return cls()

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(path=self.path)

    def __dict__(self):
        return {"path": self.path}


@dataclass
class SyncPolicy:
    """
    Defines the synchronization policy

    Attributes:
        upload_policy: Defines the upload policy
        download_policy: Defines the download policy
        delete_policy: Defines the delete policy
        extract_policy: Defines the extract policy
        recycle_policy: Defines the recycle policy
        bw_list: Defines the black and white list
        mapping_policy: Defines the mapping policy for cross-platform context synchronization
    """

    upload_policy: Optional[UploadPolicy] = None
    download_policy: Optional[DownloadPolicy] = None
    delete_policy: Optional[DeletePolicy] = None
    extract_policy: Optional[ExtractPolicy] = None
    recycle_policy: Optional[RecyclePolicy] = None
    bw_list: Optional[BWList] = None
    mapping_policy: Optional[MappingPolicy] = None

    def __post_init__(self):
        """Post-initialization to ensure all policies have default values if not provided"""
        if self.upload_policy is None:
            self.upload_policy = UploadPolicy.default()
        if self.download_policy is None:
            self.download_policy = DownloadPolicy.default()
        if self.delete_policy is None:
            self.delete_policy = DeletePolicy.default()
        if self.extract_policy is None:
            self.extract_policy = ExtractPolicy.default()
        if self.recycle_policy is None:
            self.recycle_policy = RecyclePolicy.default()
        if self.bw_list is None:
            self.bw_list = BWList(white_lists=[WhiteList(path="", exclude_paths=[])])

    @classmethod
    def default(cls):
        """Creates a new sync policy with default values"""
        return cls(
            upload_policy=UploadPolicy.default(),
            download_policy=DownloadPolicy.default(),
            delete_policy=DeletePolicy.default(),
            extract_policy=ExtractPolicy.default(),
            recycle_policy=RecyclePolicy.default(),
            bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
        )

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            upload_policy=copy.deepcopy(self.upload_policy, memo) if self.upload_policy else None,
            download_policy=copy.deepcopy(self.download_policy, memo) if self.download_policy else None,
            delete_policy=copy.deepcopy(self.delete_policy, memo) if self.delete_policy else None,
            extract_policy=copy.deepcopy(self.extract_policy, memo) if self.extract_policy else None,
            recycle_policy=copy.deepcopy(self.recycle_policy, memo) if self.recycle_policy else None,
            bw_list=copy.deepcopy(self.bw_list, memo) if self.bw_list else None,
            mapping_policy=copy.deepcopy(self.mapping_policy, memo) if self.mapping_policy else None,
        )

    def __dict__(self):
        result = {}
        if self.upload_policy:
            result["uploadPolicy"] = self.upload_policy.__dict__()
        if self.download_policy:
            result["downloadPolicy"] = self.download_policy.__dict__()
        if self.delete_policy:
            result["deletePolicy"] = self.delete_policy.__dict__()
        if self.extract_policy:
            result["extractPolicy"] = self.extract_policy.__dict__()
        if self.recycle_policy:
            result["recyclePolicy"] = self.recycle_policy.__dict__()
        if self.bw_list:
            result["bwList"] = self.bw_list.__dict__()
        if self.mapping_policy:
            result["mappingPolicy"] = self.mapping_policy.__dict__()
        return result


@dataclass
class ContextSync:
    """
    Defines the context synchronization configuration

    Attributes:
        context_id: ID of the context to synchronize
        path: Path where the context should be mounted
        policy: Defines the synchronization policy
        beta_wait_for_completion: Beta feature flag to control whether session creation
            should wait for this context's initial download to finish. If set to False,
            the SDK will not block create_session on this context. Defaults to None
            (treated as True for backward compatibility).
    """

    context_id: str
    path: str
    policy: Optional[SyncPolicy] = None
    beta_wait_for_completion: Optional[bool] = None

    @classmethod
    def new(
        cls,
        context_id: str,
        path: str,
        policy: Optional[SyncPolicy] = None,
        beta_wait_for_completion: Optional[bool] = None,
    ):
        """Creates a new context sync configuration"""
        return cls(
            context_id=context_id,
            path=path,
            policy=policy,
            beta_wait_for_completion=beta_wait_for_completion,
        )

    def __deepcopy__(self, memo):
        """Support deepcopy for dataclass with __dict__() method"""
        return self.__class__(
            context_id=self.context_id,
            path=self.path,
            policy=copy.deepcopy(self.policy, memo) if self.policy else None,
            beta_wait_for_completion=self.beta_wait_for_completion,
        )

    def with_policy(self, policy: SyncPolicy):
        """Sets the policy"""
        self.policy = policy
        return self
