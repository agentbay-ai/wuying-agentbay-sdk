# Class: ContextManager

## 🗂️ Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

## Table of contents


### Methods

- [bind](#bind)
- [info](#info)
- [infoWithParams](#infowithparams)
- [listBindings](#listbindings)
- [sync](#sync)

## Methods

### bind

▸ **bind**(`contexts`, `waitForCompletion?`): `Promise`\<`ContextBindResult`\>

Dynamically binds one or more contexts to the current session.

Accepts both ContextSync (sync-based persistence) and BetaContextMount (direct-mount
write-through persistence) objects. They can be mixed in a single call.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contexts` | [`ContextSync`](context-sync.md) \| ``BetaContextMount`` \| ([`ContextSync`](context-sync.md) \| ``BetaContextMount``)[] | `undefined` | One or more ContextSync or BetaContextMount objects |
| `waitForCompletion` | `boolean` | `true` | Whether to poll until all bindings are confirmed (default: true) |

#### Returns

`Promise`\<`ContextBindResult`\>

Promise resolving to ContextBindResult

**`Example`**

```typescript
const contextSync = new ContextSync(context.id, '/tmp/ctx-data');
const result = await session.context.bind(contextSync);

const contextMount = new BetaContextMount(context.id, '/mnt/data');
const result2 = await session.context.bind(contextMount);
```

___

### info

▸ **info**(): `Promise`\<``ContextInfoResult``\>

Gets information about context synchronization status for the current session.

#### Returns

`Promise`\<``ContextInfoResult``\>

Promise resolving to ContextInfoResult containing context status data and request ID

**`Throws`**

Error if the API call fails

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const info = await result.session.context.info();
  console.log(`Context count: ${info.contextStatusData.length}`);
  await result.session.delete();
}
```

___

### infoWithParams

▸ **infoWithParams**(`contextId?`, `path?`, `taskType?`): `Promise`\<``ContextInfoResult``\>

Gets information about context synchronization status with optional filter parameters.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId?` | `string` | Optional context ID to filter results |
| `path?` | `string` | Optional path to filter results |
| `taskType?` | `string` | Optional task type to filter results (e.g., "upload", "download") |

#### Returns

`Promise`\<``ContextInfoResult``\>

Promise resolving to ContextInfoResult containing filtered context status data and request ID

**`Throws`**

Error if the API call fails

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const info = await result.session.context.infoWithParams('SdkCtx-xxx', '/mnt/persistent');
  console.log(`Context status: ${info.contextStatusData[0]?.status}`);
  await result.session.delete();
}
```

___

### listBindings

▸ **listBindings**(): `Promise`\<`ContextBindingsResult`\>

Lists all context bindings for the current session.

#### Returns

`Promise`\<`ContextBindingsResult`\>

Promise resolving to ContextBindingsResult with the list of bindings

**`Example`**

```typescript
const result = await session.context.listBindings();
for (const binding of result.bindings) {
  console.log(`Context ${binding.contextId} bound at ${binding.path}`);
}
```

___

### sync

▸ **sync**(`contextId?`, `path?`, `mode?`, `callback?`, `maxRetries?`, `retryInterval?`): `Promise`\<``ContextSyncResult``\>

Synchronizes a context with the session. Supports both async and callback modes.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId?` | `string` | `undefined` | Optional context ID to synchronize. If provided, `path` must also be provided. |
| `path?` | `string` | `undefined` | Optional path where the context should be mounted. If provided, `contextId` must also be provided. |
| `mode?` | `string` | `undefined` | Optional synchronization mode (e.g., "upload", "download") |
| `callback?` | ``SyncCallback`` | `undefined` | Optional callback function. If provided, runs in background and calls callback when complete |
| `maxRetries` | `number` | `150` | Maximum number of retries for polling completion status (default: 150) |
| `retryInterval` | `number` | `500` | Initial interval in milliseconds for exponential backoff polling (default: 500). Interval grows by factor 1.1 up to 5000ms. |

#### Returns

`Promise`\<``ContextSyncResult``\>

Promise resolving to ContextSyncResult with success status and request ID

**`Throws`**

Error if the API call fails

**`Throws`**

Error if `contextId` or `path` is provided without the other parameter.
              Both must be provided together, or both must be omitted.

**`Example`**

Sync all contexts (no parameters):
```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const syncResult = await result.session.context.sync();
  console.log(`Sync: ${syncResult.success}`);
  await result.session.delete();
}
```

**`Example`**

Sync specific context with path:
```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const ctxResult = await agentBay.context.get('my-context', true);
  const syncResult = await result.session.context.sync(ctxResult.context!.id, '/mnt/persistent', 'upload');
  console.log(`Sync: ${syncResult.success}`);
  await result.session.delete();
}
```

## Related Resources

- [Context API Reference](context.md)
- [Session API Reference](session.md)

