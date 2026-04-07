# Context Sync API Reference

## UploadStrategy

```python
class UploadStrategy(Enum)
```

Upload strategy for context synchronization

#### UPLOAD_BEFORE_RESOURCE_RELEASE

```python
UPLOAD_BEFORE_RESOURCE_RELEASE = "UploadBeforeResourceRelease"
```

## DownloadStrategy

```python
class DownloadStrategy(Enum)
```

Download strategy for context synchronization

#### DOWNLOAD_ASYNC

```python
DOWNLOAD_ASYNC = "DownloadAsync"
```

## UploadMode

```python
class UploadMode(Enum)
```

Upload mode for context synchronization

#### FILE

```python
FILE = "File"
```

#### ARCHIVE

```python
ARCHIVE = "Archive"
```

## Lifecycle

```python
class Lifecycle(Enum)
```

Lifecycle options for recycle policy

#### LIFECYCLE_1DAY

```python
LIFECYCLE_1DAY = "Lifecycle_1Day"
```

#### LIFECYCLE_3DAYS

```python
LIFECYCLE_3DAYS = "Lifecycle_3Days"
```

#### LIFECYCLE_5DAYS

```python
LIFECYCLE_5DAYS = "Lifecycle_5Days"
```

#### LIFECYCLE_10DAYS

```python
LIFECYCLE_10DAYS = "Lifecycle_10Days"
```

#### LIFECYCLE_15DAYS

```python
LIFECYCLE_15DAYS = "Lifecycle_15Days"
```

#### LIFECYCLE_30DAYS

```python
LIFECYCLE_30DAYS = "Lifecycle_30Days"
```

#### LIFECYCLE_90DAYS

```python
LIFECYCLE_90DAYS = "Lifecycle_90Days"
```

#### LIFECYCLE_180DAYS

```python
LIFECYCLE_180DAYS = "Lifecycle_180Days"
```

#### LIFECYCLE_360DAYS

```python
LIFECYCLE_360DAYS = "Lifecycle_360Days"
```

#### LIFECYCLE_FOREVER

```python
LIFECYCLE_FOREVER = "Lifecycle_Forever"
```

## UploadPolicy

```python
@dataclass
class UploadPolicy()
```

Defines the upload policy for context synchronization

**Attributes**:

    auto_upload: Enables automatic upload
    upload_strategy: Defines the upload strategy
    upload_mode: Defines the upload mode (UploadMode.FILE or UploadMode.ARCHIVE)
    archive_exclude_paths: Paths excluded from Archive packaging, stored as individual
  files (FILE mode). Only applicable when upload_mode=ARCHIVE. Each entry is a
  relative path prefix (no wildcards). Matching files support Presigned URL
  direct access.

#### auto_upload: `bool`

```python
auto_upload = True
```

#### upload_strategy: `UploadStrategy`

```python
upload_strategy = UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE
```

#### upload_mode: `UploadMode`

```python
upload_mode = UploadMode.FILE
```

#### archive_exclude_paths: `List[str]`

```python
archive_exclude_paths = field(default_factory=list)
```

### default

```python
@classmethod
def default(cls)
```

Creates a new upload policy with default values

## DownloadPolicy

```python
@dataclass
class DownloadPolicy()
```

Defines the download policy for context synchronization

**Attributes**:

    auto_download: Enables automatic download
    download_strategy: Defines the download strategy

#### auto_download: `bool`

```python
auto_download = True
```

#### download_strategy: `DownloadStrategy`

```python
download_strategy = DownloadStrategy.DOWNLOAD_ASYNC
```

### default

```python
@classmethod
def default(cls)
```

Creates a new download policy with default values

## DeletePolicy

```python
@dataclass
class DeletePolicy()
```

Defines the delete policy for context synchronization

**Attributes**:

    sync_local_file: Enables synchronization of local file deletions

#### sync_local_file: `bool`

```python
sync_local_file = True
```

### default

```python
@classmethod
def default(cls)
```

Creates a new delete policy with default values

## ExtractPolicy

```python
@dataclass
class ExtractPolicy()
```

Defines the extract policy for context synchronization

**Attributes**:

    extract: Enables file extraction
    delete_src_file: Enables deletion of source file after extraction
    extract_current_folder: Enables extraction to the current folder

#### extract: `bool`

```python
extract = True
```

#### delete_src_file: `bool`

```python
delete_src_file = True
```

#### extract_current_folder: `bool`

```python
extract_current_folder = False
```

### default

```python
@classmethod
def default(cls)
```

Creates a new extract policy with default values

## RecyclePolicy

```python
@dataclass
class RecyclePolicy()
```

Defines the recycle policy for context synchronization

**Attributes**:

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

#### lifecycle: `Lifecycle`

```python
lifecycle = Lifecycle.LIFECYCLE_FOREVER
```

#### paths: `List[str]`

```python
paths = field(default_factory=lambda: [""])
```

### default

```python
@classmethod
def default(cls)
```

Creates a new recycle policy with default values

## WhiteList

```python
@dataclass
class WhiteList()
```

Defines the white list configuration

**Attributes**:

    path: Path to include in the white list
    exclude_paths: Paths to exclude from the white list

#### path: `str`

```python
path = ""
```

#### exclude_paths: `List[str]`

```python
exclude_paths = field(default_factory=list)
```

## BWList

```python
@dataclass
class BWList()
```

Defines the black and white list configuration

**Attributes**:

    white_lists: Defines the white lists

#### white_lists: `List[WhiteList]`

```python
white_lists = field(default_factory=list)
```

## MappingPolicy

```python
@dataclass
class MappingPolicy()
```

Defines the mapping policy for cross-platform context synchronization

**Attributes**:

    path: The original path from a different OS that should be mapped to the current context path

#### path: `str`

```python
path = ""
```

### default

```python
@classmethod
def default(cls)
```

Creates a new mapping policy with default values

## SyncPolicy

```python
@dataclass
class SyncPolicy()
```

Defines the synchronization policy

**Attributes**:

    upload_policy: Defines the upload policy
    download_policy: Defines the download policy
    delete_policy: Defines the delete policy
    extract_policy: Defines the extract policy
    recycle_policy: Defines the recycle policy
    bw_list: Defines the black and white list
    mapping_policy: Defines the mapping policy for cross-platform context synchronization

#### upload_policy: `Optional[UploadPolicy]`

```python
upload_policy = None
```

#### download_policy: `Optional[DownloadPolicy]`

```python
download_policy = None
```

#### delete_policy: `Optional[DeletePolicy]`

```python
delete_policy = None
```

#### extract_policy: `Optional[ExtractPolicy]`

```python
extract_policy = None
```

#### recycle_policy: `Optional[RecyclePolicy]`

```python
recycle_policy = None
```

#### bw_list: `Optional[BWList]`

```python
bw_list = None
```

#### mapping_policy: `Optional[MappingPolicy]`

```python
mapping_policy = None
```

### default

```python
@classmethod
def default(cls)
```

Creates a new sync policy with default values

## ContextSync

```python
@dataclass
class ContextSync()
```

Defines the context synchronization configuration

**Attributes**:

    context_id: ID of the context to synchronize
    path: Path where the context should be mounted
    policy: Defines the synchronization policy
    beta_wait_for_completion: Beta feature flag to control whether session creation
  should wait for this context's initial download to finish. If set to False,
  the SDK will not block create_session on this context. Defaults to None
  (treated as True for backward compatibility).

#### context_id: `str`

```python
context_id = None
```

#### path: `str`

```python
path = None
```

#### policy: `Optional[SyncPolicy]`

```python
policy = None
```

#### beta_wait_for_completion: `Optional[bool]`

```python
beta_wait_for_completion = None
```

### new

```python
@classmethod
def new(cls,
        context_id: str,
        path: str,
        policy: Optional[SyncPolicy] = None,
        beta_wait_for_completion: Optional[bool] = None)
```

Creates a new context sync configuration

### with_policy

```python
def with_policy(policy: SyncPolicy)
```

Sets the policy

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
