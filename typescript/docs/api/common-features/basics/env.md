# Class: Env

## Overview

The Env module provides methods for setting and querying global environment variables within a session sandbox.
Variables set via this module persist across all MCP tools (shell, code interpreter, etc.) within the session.

## Table of contents


### Methods

- [get](#get)
- [set](#set)

## Methods

### get

▸ **get**(`keys?`): `Promise`\<``EnvResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `keys?` | `string`[] |

#### Returns

`Promise`\<``EnvResult``\>

___

### set

▸ **set**(`envs`): `Promise`\<``BoolResult``\>

#### Parameters

| Name | Type |
| :------ | :------ |
| `envs` | `Record`\<`string`, `string`\> |

#### Returns

`Promise`\<``BoolResult``\>

## Best Practices

1. Use env.set to configure variables before running shell commands or code
2. Both keys and values must be strings
3. Setting a key that already exists will overwrite the previous value
4. Use env.get with specific keys to reduce response size


## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

