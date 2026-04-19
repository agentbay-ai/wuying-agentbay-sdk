# Context Sync API Reference

## 🔄 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn how context synchronization works and how to persist data across sessions

## Overview

Context Sync provides a mechanism to persist files and directories across sessions by synchronizing local paths to a named context. It supports policies for upload/download behavior and selective path inclusion.

## UploadStrategy

```typescript
enum UploadStrategy
```

Upload strategy for context synchronization.

| Value | Description |
|-------|-------------|
| `UploadBeforeResourceRelease` | Upload before the resource is released (default) |

## DownloadStrategy

```typescript
enum DownloadStrategy
```

Download strategy for context synchronization.

| Value | Description |
|-------|-------------|
| `DownloadAsync` | Download asynchronously (default) |

## UploadMode

```typescript
enum UploadMode
```

Upload mode for context synchronization.

| Value | Description |
|-------|-------------|
| `File` | Default mode — files uploaded as-is |
| `Archive` | Files compressed into an archive before upload |

## UploadPolicy

```typescript
interface UploadPolicy
```

Defines the upload policy for context synchronization.

### Properties

#### autoUpload

```typescript
autoUpload: boolean  // default: true
```

Enables automatic upload.

#### uploadStrategy

```typescript
uploadStrategy: UploadStrategy  // default: UploadBeforeResourceRelease
```

Defines the upload strategy.

#### uploadMode

```typescript
uploadMode: UploadMode  // default: File
```

Defines the upload mode (`UploadMode.File` or `UploadMode.Archive`).

#### archiveExcludePaths

```typescript
archiveExcludePaths?: string[]
```

Paths excluded from Archive packaging, stored as individual files (FILE mode). Only applicable when `uploadMode = UploadMode.Archive`. Each entry is a relative path prefix (no wildcards). Matching files support Presigned URL direct access.

### Factory Function

```typescript
function newUploadPolicy(options?: Partial<UploadPolicy>): UploadPolicy
```

Creates a new upload policy with default values. Accepts partial options to override defaults.

## DownloadPolicy

```typescript
interface DownloadPolicy
```

Defines the download policy for context synchronization.

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `autoDownload` | `boolean` | `true` | Enables automatic download |
| `downloadStrategy` | `DownloadStrategy` | `DownloadAsync` | Defines the download strategy |

### Factory Function

```typescript
function newDownloadPolicy(): DownloadPolicy
```

## SyncPolicy

```typescript
interface SyncPolicy
```

Defines the complete synchronization policy, combining upload, download, delete, extract, recycle, and BWList policies.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `uploadPolicy?` | `UploadPolicy` | Upload behavior configuration |
| `downloadPolicy?` | `DownloadPolicy` | Download behavior configuration |
| `deletePolicy?` | `DeletePolicy` | Deletion synchronization configuration |
| `extractPolicy?` | `ExtractPolicy` | Archive extraction configuration |
| `recyclePolicy?` | `RecyclePolicy` | Data lifecycle configuration |
| `bwList?` | `BWList` | Directory whitelist configuration |

### Factory Function

```typescript
function newSyncPolicy(): SyncPolicy
```

Creates a new sync policy with all sub-policies set to their defaults.

## ContextSync

```typescript
class ContextSync
```

Defines the context synchronization configuration linking a context to a session path.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `contextId` | `string` | The context identifier |
| `path` | `string` | The local path to synchronize |
| `policy?` | `SyncPolicy` | The synchronization policy |

### Factory Function

```typescript
function newContextSync(contextId: string, path: string, policy?: SyncPolicy): ContextSync
```

## ContextSyncResult

```typescript
interface ContextSyncResult extends ApiResponse
```

Result of a context sync operation.

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `success` | `boolean` | Whether the operation succeeded |
| `errorMessage?` | `string` | Optional error message if the operation failed |
| `requestId?` | `string` | Optional request identifier for tracking API calls |

## Related Resources

- [Context Manager API Reference](context-manager.md)
- [Session API Reference](session.md)

