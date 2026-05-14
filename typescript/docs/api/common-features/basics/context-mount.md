# Class: BetaContextMount

[Beta] Represents a context mount configuration for direct-mount persistence.

## Table of contents


### Properties


### Methods

- `toMountConfigJSON`
- `withAccessMode`
- `withStrategy`

## Properties

```typescript
accessMode: ``BetaContextMountAccessMode``
contextId: `string`
path: `string`
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
