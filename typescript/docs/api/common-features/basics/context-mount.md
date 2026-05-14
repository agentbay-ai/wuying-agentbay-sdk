# Class: ContextMount

## Table of contents


### Properties


### Methods

- [toMountConfigJSON](#tomountconfigjson)
- [withAccessMode](#withaccessmode)
- [withStrategy](#withstrategy)

## Properties

```typescript
accessMode: ``ContextMountAccessMode``
contextId: `string`
path: `string`
strategy: ``ContextMountStrategy``
```


## Methods

### toMountConfigJSON

▸ **toMountConfigJSON**(): `string`

#### Returns

`string`

___

### withAccessMode

▸ **withAccessMode**(`accessMode`): [`ContextMount`](context-mount.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `accessMode` | ``ContextMountAccessMode`` |

#### Returns

[`ContextMount`](context-mount.md)

___

### withStrategy

▸ **withStrategy**(`strategy`): [`ContextMount`](context-mount.md)

#### Parameters

| Name | Type |
| :------ | :------ |
| `strategy` | ``ContextMountStrategy`` |

#### Returns

[`ContextMount`](context-mount.md)


`wuying-agentbay-sdk` / ContextMountAccessMode

# Enumeration: ContextMountAccessMode

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


`wuying-agentbay-sdk` / ContextMountStrategy

# Enumeration: ContextMountStrategy

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
