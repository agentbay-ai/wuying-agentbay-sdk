# Class: BetaContextMount

## 📂 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn how Context Mount provides direct-mount write-through persistence

## Overview

[Beta] BetaContextMount provides direct-mount write-through persistence where data is persisted immediately without manual sync calls. Unlike ContextSync, mounted paths act as live persistent storage. Requires imageId=aio-ubuntu-2404 on the session.

[Beta] Represents a context mount configuration for direct-mount persistence.

IMPORTANT: BetaContextMount requires `imageId: "aio-ubuntu-2404"` on the session.
Other images do not provide a real OSS-backed mount — writes are not persisted to
the shared context store and are invisible to other sessions even with the same
contextId and mount path.

Use `withSourcePath()` to mount only a subdirectory of the context. The
subdirectory's contents are projected to the mount root.

## Table of contents


### Properties


### Methods

- `toMountConfigJSON`
- `withAccessMode`
- `withSourcePath`
- `withStrategy`

## Properties

```typescript
accessMode: ``BetaContextMountAccessMode``
contextId: `string`
path: `string`
sourcePath: `string`
strategy: ``BetaContextMountStrategy``
```


## Methods

### toMountConfigJSON

▸ **toMountConfigJSON**(): `string`

#### Returns

`string`

___

### withAccessMode

▸ **withAccessMode**(`accessMode`): ``BetaContextMount``

#### Parameters

| Name | Type |
| :------ | :------ |
| `accessMode` | ``BetaContextMountAccessMode`` |

#### Returns

``BetaContextMount``

___

### withSourcePath

▸ **withSourcePath**(`sourcePath`): ``BetaContextMount``

Set the subpath within the context to mount. Empty string (default) mounts
the entire context. The selected subdirectory's contents are projected to
the mount root.

#### Parameters

| Name | Type |
| :------ | :------ |
| `sourcePath` | `string` |

#### Returns

``BetaContextMount``

___

### withStrategy

▸ **withStrategy**(`strategy`): ``BetaContextMount``

#### Parameters

| Name | Type |
| :------ | :------ |
| `strategy` | ``BetaContextMountStrategy`` |

#### Returns

``BetaContextMount``


`wuying-agentbay-sdk` / BetaContextMountAccessMode

# Enumeration: BetaContextMountAccessMode

## Table of contents

### Enumeration Members

- `ReadOnly`
- `ReadWrite`

## Enumeration Members

### ReadOnly

• **ReadOnly** = ``"readOnly"``

___

### ReadWrite

• **ReadWrite** = ``"readWrite"``


`wuying-agentbay-sdk` / BetaContextMountStrategy

# Enumeration: BetaContextMountStrategy

## Table of contents

### Enumeration Members

- `Performance`
- `Standard`

## Enumeration Members

### Performance

• **Performance** = ``"performance"``

___

### Standard

• **Standard** = ``"standard"``

## Related Resources

- [Context Manager API Reference](context-manager.md)
- [Session API Reference](session.md)

