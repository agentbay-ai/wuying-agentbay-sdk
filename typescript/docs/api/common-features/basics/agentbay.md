# Class: AgentBay

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

Main class for interacting with the AgentBay cloud runtime environment.

## Table of contents


### Properties


### Methods

- [betaPauseAsync](#betapauseasync)
- [betaResumeAsync](#betaresumeasync)
- [create](#create)
- [delete](#delete)
- [get](#get)
- [list](#list)

## Properties

```typescript
betaNetwork: [`BetaNetworkService`](../advanced/network.md)
betaSkills: ``BetaSkillsService``
client: ``Client``
context: [`ContextService`](context.md)
network: [`BetaNetworkService`](../advanced/network.md)
```


## Methods

### betaPauseAsync

▸ **betaPauseAsync**(`session`, `timeout?`, `pollInterval?`): `Promise`\<`SessionPauseResult`\>

Asynchronously pause a session, putting it into a dormant state.

**Note**: This feature is currently in whitelist-only access.
Contact agentbay_dev@alibabacloud.com to request access.

This method directly calls the PauseSessionAsync API without waiting for the session
to reach the PAUSED state.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to pause. |
| `timeout` | `number` | `600` | Timeout in seconds to wait for the session to pause. Defaults to 600 seconds. |
| `pollInterval` | `number` | `2.0` | Interval in seconds between status polls. Defaults to 2.0 seconds. |

#### Returns

`Promise`\<`SessionPauseResult`\>

SessionPauseResult indicating success or failure and request ID

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const session = (await agentBay.create()).session;
const pauseResult = await agentBay.betaPauseAsync(session);
await agentBay.betaResumeAsync(session);
await session.delete();
```

**`Remarks`**

**Behavior:**
- This method does not wait for the session to reach the PAUSED state
- It only submits the pause request to the API
- The session state transitions from RUNNING -> PAUSING -> PAUSED
- Paused sessions consume fewer resources but maintain their state

**`See`**

[betaResumeAsync](#betaresumeasync), [Session.betaPauseAsync](session.md#betapauseasync)

___

### betaResumeAsync

▸ **betaResumeAsync**(`session`, `timeout?`, `pollInterval?`): `Promise`\<`SessionResumeResult`\>

Asynchronously resume a session from a paused state.

This method directly calls the ResumeSessionAsync API without waiting for the session
to reach the RUNNING state.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to resume. |
| `timeout` | `number` | `600` | Timeout in seconds to wait for the session to resume. Defaults to 600 seconds. |
| `pollInterval` | `number` | `2.0` | Interval in seconds between status polls. Defaults to 2.0 seconds. |

#### Returns

`Promise`\<`SessionResumeResult`\>

SessionResumeResult indicating success or failure and request ID

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const session = (await agentBay.create()).session;
await agentBay.betaPauseAsync(session);
const resumeResult = await agentBay.betaResumeAsync(session);
await session.delete();
```

**`Remarks`**

**Behavior:**
- This method does not wait for the session to reach the RUNNING state
- It only submits the resume request to the API
- The session state transitions from PAUSED -> RESUMING -> RUNNING
- Only sessions in PAUSED state can be resumed

**`See`**

[betaPauseAsync](#betapauseasync), [Session.betaResumeAsync](session.md#betaresumeasync)

___

### create

▸ **create**(`params?`): `Promise`\<`SessionResult`\>

Creates a new AgentBay session with specified configuration.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params` | ``CreateSessionParamsInterface`` | Configuration parameters for the session: - labels: Key-value pairs for session metadata - imageId: Custom image ID for the session environment - contextSync: Array of context synchronization configurations - browserContext: Browser-specific context configuration - policyId: Security policy ID - enableBrowserReplay: Enable browser session recording - extraConfigs: Additional configuration options - framework: Framework identifier for tracking |

#### Returns

`Promise`\<`SessionResult`\>

Promise resolving to SessionResult containing:
         - success: Whether session creation succeeded
         - session: Session object for interacting with the environment
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if creation failed

**`Throws`**

Error if API call fails or authentication is invalid.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create({ labels: { project: 'demo' } });
if (result.success) {
  await result.session.filesystem.readFile('/etc/hostname');
  await result.session.delete();
}
```

**`Remarks`**

**Behavior:**
- Creates a new isolated cloud runtime environment
- Automatically creates file transfer context if not provided
- Waits for context synchronization if contextSync is specified
- Browser replay creates a separate recording context

**`See`**

[get](#get), [list](#list), [Session.delete](session.md#delete)

___

### delete

▸ **delete**(`session`, `syncContext?`): `Promise`\<``DeleteResult``\>

Delete a session by session object.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `session` | [`Session`](session.md) | `undefined` | The session to delete. |
| `syncContext` | `boolean` | `false` | Whether to sync context data (trigger file uploads) before deleting the session. Defaults to false. |

#### Returns

`Promise`\<``DeleteResult``\>

DeleteResult indicating success or failure and request ID

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  await agentBay.delete(result.session);
}
```

___

### get

▸ **get**(`sessionId`): `Promise`\<`SessionResult`\>

Get a session by its ID.

This method retrieves a session by calling the GetSession API
and returns a SessionResult containing the Session object and request ID.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `sessionId` | `string` | The ID of the session to retrieve |

#### Returns

`Promise`\<`SessionResult`\>

Promise resolving to SessionResult with the Session instance, request ID, and success status

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const createResult = await agentBay.create();
if (createResult.success) {
  const result = await agentBay.get(createResult.session.sessionId);
  await result.session?.filesystem.readFile('/etc/hostname');
  await result.session?.delete();
}
```

### list

▸ **list**(`labels?`, `page?`, `limit?`, `status?`, `imageId?`): `Promise`\<``SessionListResult``\>

Returns paginated list of session IDs filtered by labels and status.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `labels` | `Record`\<`string`, `string`\> | `{}` | Optional labels to filter sessions (defaults to empty object) |
| `page?` | `number` | `undefined` | Optional page number for pagination (starting from 1, defaults to 1) |
| `limit` | `number` | `10` | Optional maximum number of items per page (defaults to 10) |
| `status?` | `string` | `undefined` | Optional status to filter sessions. Must be one of: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED (defaults to undefined) |
| `imageId?` | `string` | `undefined` | - |

#### Returns

`Promise`\<``SessionListResult``\>

SessionListResult - Paginated list of session IDs that match the labels and status

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: "your_api_key" });
const result = await agentBay.list({ project: "demo" }, 1, 10, "RUNNING");
if (result.success) {
 log(`Found ${result.sessionIds.length} sessions`);
}
```

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

