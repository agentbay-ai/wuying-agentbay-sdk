# Class: ContextSync

## 🔄 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn how context synchronization works and how to persist data across sessions

## Overview

Context Sync provides a mechanism to persist files and directories across sessions by synchronizing local paths to a named context. It supports policies for upload/download behavior and selective path inclusion.

## Table of contents


### Properties

- [betaWaitForCompletion](#betawaitforcompletion)
- [policy](#policy)

### Methods

- [withBetaWaitForCompletion](#withbetawaitforcompletion)
- [withPolicy](#withpolicy)

## Properties

```typescript
contextId: `string`
path: `string`
```


### betaWaitForCompletion

• `Optional` **betaWaitForCompletion**: `boolean`

Beta feature flag to control whether session creation should wait for this context's
initial download to finish. If set to false, the SDK will not block create() on this context.
Defaults to undefined (treated as true for backward compatibility).

___

### policy

• `Optional` **policy**: ``SyncPolicy``

## Methods

### withBetaWaitForCompletion

▸ **withBetaWaitForCompletion**(`wait`): [`ContextSync`](context-sync.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `wait` | `boolean` |

#### Returns

[`ContextSync`](context-sync.md)

___

### withPolicy

▸ **withPolicy**(`policy`): [`ContextSync`](context-sync.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `policy` | ``SyncPolicy`` |

#### Returns

[`ContextSync`](context-sync.md)


`wuying-agentbay-sdk` / SyncPolicyImpl

# Class: SyncPolicyImpl

## Implements

- ``SyncPolicy``

## Table of contents

### Constructors

- `constructor`

### Properties

- `bwList`
- `deletePolicy`
- `downloadPolicy`
- `extractPolicy`
- `recyclePolicy`
- `uploadPolicy`

### Methods

- `toJSON`

## Constructors

### constructor

• **new SyncPolicyImpl**(`policy?`): ``SyncPolicyImpl``

#### Parameters

| Name | Type |
| :------ | :------ |
| `policy?` | `Partial`\<``SyncPolicy``\> |

#### Returns

``SyncPolicyImpl``

## Properties

### bwList

• `Optional` **bwList**: ``BWList``

#### Implementation of

`SyncPolicy`.`bwList`

___

### deletePolicy

• `Optional` **deletePolicy**: ``DeletePolicy``

#### Implementation of

`SyncPolicy`.`deletePolicy`

___

### downloadPolicy

• `Optional` **downloadPolicy**: ``DownloadPolicy``

#### Implementation of

`SyncPolicy`.`downloadPolicy`

___

### extractPolicy

• `Optional` **extractPolicy**: ``ExtractPolicy``

#### Implementation of

`SyncPolicy`.`extractPolicy`

___

### recyclePolicy

• `Optional` **recyclePolicy**: ``RecyclePolicy``

#### Implementation of

`SyncPolicy`.`recyclePolicy`

___

### uploadPolicy

• `Optional` **uploadPolicy**: ``UploadPolicy``

#### Implementation of

`SyncPolicy`.`uploadPolicy`

## Methods

### toJSON

▸ **toJSON**(): ``SyncPolicy``

#### Returns

``SyncPolicy``


`wuying-agentbay-sdk` / SyncPolicy

# Interface: SyncPolicy

## Implemented by

- ``SyncPolicyImpl``

## Table of contents

### Properties

- `bwList`
- `deletePolicy`
- `downloadPolicy`
- `extractPolicy`
- `mappingPolicy`
- `recyclePolicy`
- `uploadPolicy`

## Properties

### bwList

• `Optional` **bwList**: ``BWList``

___

### deletePolicy

• `Optional` **deletePolicy**: ``DeletePolicy``

___

### downloadPolicy

• `Optional` **downloadPolicy**: ``DownloadPolicy``

___

### extractPolicy

• `Optional` **extractPolicy**: ``ExtractPolicy``

___

### mappingPolicy

• `Optional` **mappingPolicy**: ``MappingPolicy``

___

### recyclePolicy

• `Optional` **recyclePolicy**: ``RecyclePolicy``

___

### uploadPolicy

• `Optional` **uploadPolicy**: ``UploadPolicy``


`wuying-agentbay-sdk` / UploadPolicy

# Interface: UploadPolicy

## Table of contents

### Properties

- `archiveExcludePaths`
- `autoUpload`
- `uploadMode`
- `uploadStrategy`

## Properties

### archiveExcludePaths

• `Optional` **archiveExcludePaths**: `string`[]

___

### autoUpload

• **autoUpload**: `boolean`

___

### uploadMode

• **uploadMode**: ``UploadMode``

___

### uploadStrategy

• **uploadStrategy**: ``UploadBeforeResourceRelease``


`wuying-agentbay-sdk` / DownloadPolicy

# Interface: DownloadPolicy

## Table of contents

### Properties

- `autoDownload`
- `downloadStrategy`

## Properties

### autoDownload

• **autoDownload**: `boolean`

___

### downloadStrategy

• **downloadStrategy**: ``DownloadAsync``


`wuying-agentbay-sdk` / DeletePolicy

# Interface: DeletePolicy

## Table of contents

### Properties

- `syncLocalFile`

## Properties

### syncLocalFile

• **syncLocalFile**: `boolean`


`wuying-agentbay-sdk` / ExtractPolicy

# Interface: ExtractPolicy

## Implemented by

- ``ExtractPolicyClass``

## Table of contents

### Properties

- `deleteSrcFile`
- `extract`
- `extractToCurrentFolder`

## Properties

### deleteSrcFile

• **deleteSrcFile**: `boolean`

___

### extract

• **extract**: `boolean`

___

### extractToCurrentFolder

• **extractToCurrentFolder**: `boolean`


`wuying-agentbay-sdk` / RecyclePolicy

# Interface: RecyclePolicy

## Table of contents

### Properties

- `lifecycle`
- `paths`

## Properties

### lifecycle

• **lifecycle**: ``Lifecycle``

___

### paths

• **paths**: `string`[]


`wuying-agentbay-sdk` / MappingPolicy

# Interface: MappingPolicy

## Table of contents

### Properties

- `path`

## Properties

### path

• **path**: `string`


`wuying-agentbay-sdk` / UploadMode

# Enumeration: UploadMode

## Table of contents

### Enumeration Members

- `Archive`
- `File`

## Enumeration Members

### Archive

• **Archive** = ``"Archive"``

___

### File

• **File** = ``"File"``


`wuying-agentbay-sdk` / UploadStrategy

# Enumeration: UploadStrategy

## Table of contents

### Enumeration Members

- `UploadBeforeResourceRelease`

## Enumeration Members

### UploadBeforeResourceRelease

• **UploadBeforeResourceRelease** = ``"UploadBeforeResourceRelease"``


`wuying-agentbay-sdk` / DownloadStrategy

# Enumeration: DownloadStrategy

## Table of contents

### Enumeration Members

- `DownloadAsync`

## Enumeration Members

### DownloadAsync

• **DownloadAsync** = ``"DownloadAsync"``


`wuying-agentbay-sdk` / ContextSyncResult

# Interface: ContextSyncResult

Base interface for API responses

## Hierarchy

- ``ApiResponse``

  ↳ **`ContextSyncResult`**

## Table of contents

### Properties

- `errorMessage`
- `requestId`
- `success`

## Properties

### errorMessage

• `Optional` **errorMessage**: `string`

Optional error message if the operation failed

#### Overrides

`ApiResponse`.`errorMessage`

___

### requestId

• `Optional` **requestId**: `string`

Optional request identifier for tracking API calls

#### Inherited from

`ApiResponse`.`requestId`

___

### success

• **success**: `boolean`

Optional status code if the operation failed

#### Overrides

`ApiResponse`.`success`

## Related Resources

- [Context Manager API Reference](context-manager.md)
- [Session API Reference](session.md)

