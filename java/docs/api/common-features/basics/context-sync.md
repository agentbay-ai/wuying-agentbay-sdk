# 🔄 Context-sync API Reference

## Overview

Context Sync provides a mechanism to persist files and directories across sessions by synchronizing local paths to a named context. It supports policies for upload/download behavior and selective path inclusion.


## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn how context synchronization works and how to persist data across sessions

## ContextSync

Defines the context synchronization configuration.

<p>This class configures how a context should be synchronized with a session,
including the context ID, mount path, synchronization policy, and whether to
wait for initial download completion.</p>

### Constructor

```java
public ContextSync()
```

```java
public ContextSync(String contextId, String path, SyncPolicy policy)
```

### Methods

### create

```java
public static ContextSync create(String contextId, String path, SyncPolicy policy)
```

### withPolicy

```java
public ContextSync withPolicy(SyncPolicy policy)
```

### withBetaWaitForCompletion

```java
public ContextSync withBetaWaitForCompletion(Boolean wait)
```

### getPolicy

```java
public SyncPolicy getPolicy()
```

### setPolicy

```java
public void setPolicy(SyncPolicy policy)
```

### getBetaWaitForCompletion

```java
public Boolean getBetaWaitForCompletion()
```

### setBetaWaitForCompletion

```java
public void setBetaWaitForCompletion(Boolean betaWaitForCompletion)
```



## SyncPolicy

Defines the synchronization policy

Attributes:
    - uploadPolicy: Defines the upload policy
    - downloadPolicy: Defines the download policy
    - deletePolicy: Defines the delete policy
    - extractPolicy: Defines the extract policy
    - recyclePolicy: Defines the recycle policy
    - bwList: Defines the black and white list

### Constructor

```java
public SyncPolicy()
```

```java
public SyncPolicy(UploadPolicy uploadPolicy, DownloadPolicy downloadPolicy, DeletePolicy deletePolicy, ExtractPolicy extractPolicy, BWList bwList)
```

```java
public SyncPolicy(UploadPolicy uploadPolicy, DownloadPolicy downloadPolicy, DeletePolicy deletePolicy, ExtractPolicy extractPolicy, RecyclePolicy recyclePolicy, BWList bwList)
```

### Methods

### defaultPolicy

```java
public static SyncPolicy defaultPolicy()
```

### getUploadPolicy

```java
public UploadPolicy getUploadPolicy()
```

### setUploadPolicy

```java
public void setUploadPolicy(UploadPolicy uploadPolicy)
```

### getDownloadPolicy

```java
public DownloadPolicy getDownloadPolicy()
```

### setDownloadPolicy

```java
public void setDownloadPolicy(DownloadPolicy downloadPolicy)
```

### getDeletePolicy

```java
public DeletePolicy getDeletePolicy()
```

### setDeletePolicy

```java
public void setDeletePolicy(DeletePolicy deletePolicy)
```

### getExtractPolicy

```java
public ExtractPolicy getExtractPolicy()
```

### setExtractPolicy

```java
public void setExtractPolicy(ExtractPolicy extractPolicy)
```

### getRecyclePolicy

```java
public RecyclePolicy getRecyclePolicy()
```

### setRecyclePolicy

```java
public void setRecyclePolicy(RecyclePolicy recyclePolicy)
```

### getBwList

```java
public BWList getBwList()
```

### setBwList

```java
public void setBwList(BWList bwList)
```



## UploadPolicy

Defines the upload policy for context synchronization

Attributes:
    autoUpload: Enables automatic upload
    uploadStrategy: Defines the upload strategy
    uploadMode: Defines the upload mode (UploadMode.FILE or UploadMode.ARCHIVE)
    period: Upload period in seconds (default: 30)
    archiveExcludePaths: When uploadMode is ARCHIVE, paths to upload as individual files

### Constructor

```java
public UploadPolicy()
```

```java
public UploadPolicy(boolean autoUpload, UploadStrategy uploadStrategy, Integer period)
```

```java
public UploadPolicy(boolean autoUpload, UploadStrategy uploadStrategy, UploadMode uploadMode, Integer period)
```

### Methods

### defaultPolicy

```java
public static UploadPolicy defaultPolicy()
```

### isAutoUpload

```java
public boolean isAutoUpload()
```

### setAutoUpload

```java
public void setAutoUpload(boolean autoUpload)
```

### getUploadStrategy

```java
public UploadStrategy getUploadStrategy()
```

### setUploadStrategy

```java
public void setUploadStrategy(UploadStrategy uploadStrategy)
```

### getPeriod

```java
public Integer getPeriod()
```

### setPeriod

```java
public void setPeriod(Integer period)
```

### getUploadMode

```java
public UploadMode getUploadMode()
```

### setUploadMode

```java
public void setUploadMode(UploadMode uploadMode)
```

### getArchiveExcludePaths

```java
public List<String> getArchiveExcludePaths()
```

### setArchiveExcludePaths

```java
public void setArchiveExcludePaths(List<String> archiveExcludePaths)
```



## DownloadPolicy

Defines the download policy for context synchronization

Attributes:
    autoDownload: Enables automatic download
    downloadStrategy: Defines the download strategy

### Constructor

```java
public DownloadPolicy()
```

```java
public DownloadPolicy(boolean autoDownload, DownloadStrategy downloadStrategy)
```

### Methods

### defaultPolicy

```java
public static DownloadPolicy defaultPolicy()
```

### isAutoDownload

```java
public boolean isAutoDownload()
```

### setAutoDownload

```java
public void setAutoDownload(boolean autoDownload)
```

### getDownloadStrategy

```java
public DownloadStrategy getDownloadStrategy()
```

### setDownloadStrategy

```java
public void setDownloadStrategy(DownloadStrategy downloadStrategy)
```



## DeletePolicy

Defines the delete policy for context synchronization

Attributes:
    syncLocalFile: Enables synchronization of local file deletions

### Constructor

```java
public DeletePolicy()
```

```java
public DeletePolicy(boolean syncLocalFile)
```

### Methods

### defaultPolicy

```java
public static DeletePolicy defaultPolicy()
```

### isSyncLocalFile

```java
public boolean isSyncLocalFile()
```

### setSyncLocalFile

```java
public void setSyncLocalFile(boolean syncLocalFile)
```



## ExtractPolicy

Defines the extract policy for context synchronization

Attributes:
    extract: Enables file extraction
    deleteSrcFile: Enables deletion of source file after extraction
    extractCurrentFolder: Enables extraction to current folder

### Constructor

```java
public ExtractPolicy()
```

```java
public ExtractPolicy(boolean extract, boolean deleteSrcFile, boolean extractCurrentFolder)
```

### Methods

### defaultPolicy

```java
public static ExtractPolicy defaultPolicy()
```

### isExtract

```java
public boolean isExtract()
```

### setExtract

```java
public void setExtract(boolean extract)
```

### isDeleteSrcFile

```java
public boolean isDeleteSrcFile()
```

### setDeleteSrcFile

```java
public void setDeleteSrcFile(boolean deleteSrcFile)
```

### isExtractCurrentFolder

```java
public boolean isExtractCurrentFolder()
```

### setExtractCurrentFolder

```java
public void setExtractCurrentFolder(boolean extractCurrentFolder)
```



## RecyclePolicy

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

### Constructor

```java
public RecyclePolicy()
```

```java
public RecyclePolicy(Lifecycle lifecycle, List<String> paths)
```

### Methods

### defaultPolicy

```java
public static RecyclePolicy defaultPolicy()
```

Creates a new recycle policy with default values

**Returns:**
- `RecyclePolicy`: RecyclePolicy with default values

### getLifecycle

```java
public Lifecycle getLifecycle()
```

### setLifecycle

```java
public void setLifecycle(Lifecycle lifecycle)
```

### getPaths

```java
public List<String> getPaths()
```

### setPaths

```java
public void setPaths(List<String> paths)
```



## WhiteList

Defines the white list configuration

Attributes:
    path: Path to include in the white list
    excludePaths: Paths to exclude from the white list

### Constructor

```java
public WhiteList()
```

```java
public WhiteList(String path, List<String> excludePaths)
```

### Methods

### getExcludePaths

```java
public List<String> getExcludePaths()
```

### setExcludePaths

```java
public void setExcludePaths(List<String> excludePaths)
```



## BWList

Defines the black and white list configuration

Attributes:
    whiteLists: Defines the white lists

### Constructor

```java
public BWList()
```

```java
public BWList(List<WhiteList> whiteLists)
```

### Methods

### getWhiteLists

```java
public List<WhiteList> getWhiteLists()
```

### setWhiteLists

```java
public void setWhiteLists(List<WhiteList> whiteLists)
```



## 🔗 Related Resources

- [Context Manager API Reference](../../../api/common-features/basics/context-manager.md)
- [Session API Reference](../../../api/common-features/basics/session.md)

