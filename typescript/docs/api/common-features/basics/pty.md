# Class: Pty

## 💻 Related Tutorial

- [PTY Terminal Guide](../../../../../docs/guides/common-features/basics/pty-terminal.md) - Learn how to use interactive terminal sessions in cloud environments

## Overview

The PTY module provides interactive terminal sessions in cloud sandbox
environments. Unlike the Command module which executes single commands,
PTY gives you a persistent, interactive shell with real-time streaming
output, terminal resize support, and session lifecycle management.

## Table of contents


### Methods

- [connect](#connect)
- [create](#create)
- [kill](#kill)
- [list](#list)

## Methods

### connect

▸ **connect**(`ptySessionId`, `onData?`): `Promise`\<``PtyHandle``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `ptySessionId` | `string` |
| `onData?` | (`data`: `Uint8Array`) => `void` |

#### Returns

`Promise`\<``PtyHandle``\>

___

### create

▸ **create**(`options?`): `Promise`\<``PtyHandle``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `options` | ``PtyCreateOptions`` |

#### Returns

`Promise`\<``PtyHandle``\>

___

### kill

▸ **kill**(`ptySessionId`): `Promise`\<`void`\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `ptySessionId` | `string` |

#### Returns

`Promise`\<`void`\>

___

### list

▸ **list**(): `Promise`\<``PtySession``[]\>

#### Returns

`Promise`\<``PtySession``[]\>

## Best Practices

1. Always disconnect or wait when done with a PTY handle
2. Use carriage return (\r) to submit commands instead of newline
3. Handle the on_data callback efficiently as it may be called frequently
4. Set terminal size to match the client for correct line wrapping
5. Use appropriate timeouts with wait() to avoid blocking indefinitely


## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

