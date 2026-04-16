# Class: Session

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management

## Overview

The Session class represents an active cloud environment instance in AgentBay. It provides access to all service modules (filesystem, command, browser, code, etc.) and manages the lifecycle of the cloud environment.

Represents a session in the AgentBay cloud environment.

## Hierarchy

- **`Session`**

  ↳ ``LocalSession``

## Table of contents


### Properties

- [enableBrowserReplay](#enablebrowserreplay)

### Accessors

- [files](#files)
- [filesystem](#filesystem)
- [fs](#fs)

### Methods

- [betaPauseAsync](#betapauseasync)
- [betaResumeAsync](#betaresumeasync)
- [callMcpTool](#callmcptool)
- [delete](#delete)
- [getLabels](#getlabels)
- [getLink](#getlink)
- [getLinkAsync](#getlinkasync)
- [getMetrics](#getmetrics)
- [info](#info)
- [keepAlive](#keepalive)
- [keepAliveAsync](#keepaliveasync)
- [listMcpTools](#listmcptools)
- [setLabels](#setlabels)

## Properties

```typescript
agent: [`Agent`](../advanced/agent.md)
appInstanceId: `string` = `""`
browser: [`Browser`](../../browser-use/browser.md)
code: [`Code`](../../codespace/code.md)
command: [`Command`](command.md)
computer: [`Computer`](../../computer-use/computer.md)
context: [`ContextManager`](context-manager.md)
env: [`Env`](env.md)
fileSystem: [`FileSystem`](filesystem.md)
git: [`Git`](../advanced/git.md)
linkUrl: `string` = `""`
mcpTools: `McpTool`[] = `[]`
mobile: [`Mobile`](../../mobile-use/mobile.md)
oss: [`Oss`](../advanced/oss.md)
pty: [`Pty`](pty.md)
resourceUrl: `string` = `""`
sessionId: `string`
token: `string` = `""`
wsUrl: `string` = `""`
```


### enableBrowserReplay

• `Optional` **enableBrowserReplay**: `boolean`

___

## Accessors

### files

• `get` **files**(): [`FileSystem`](filesystem.md)

Alias of fileSystem.

#### Returns

[`FileSystem`](filesystem.md)

___

### filesystem

• `get` **filesystem**(): [`FileSystem`](filesystem.md)

Alias of fileSystem.

#### Returns

[`FileSystem`](filesystem.md)

___

### fs

• `get` **fs**(): [`FileSystem`](filesystem.md)

Alias of fileSystem.

#### Returns

[`FileSystem`](filesystem.md)

## Methods

### betaPauseAsync

▸ **betaPauseAsync**(`timeout?`, `pollInterval?`): `Promise`\<`SessionPauseResult`\>

Asynchronously pause this session (beta), putting it into a dormant state.

**Note**: This feature is currently in whitelist-only access.
Contact agentbay_dev@alibabacloud.com to request access.

This method calls the PauseSessionAsync API to initiate the pause operation and then polls
the GetSession API to check the session status until it becomes PAUSED or until timeout is reached.
During the paused state, resource usage and costs are reduced while session state is preserved.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeout` | `number` | `600` | Timeout in seconds to wait for the session to pause. Defaults to 600 seconds. |
| `pollInterval` | `number` | `2.0` | Interval in seconds between status polls. Defaults to 2.0 seconds. |

#### Returns

`Promise`\<`SessionPauseResult`\>

Promise resolving to SessionPauseResult containing:
         - success: Whether the pause operation succeeded
         - requestId: Unique identifier for this API request
         - status: Final session status (should be "PAUSED" if successful)
         - errorMessage: Error description if pause failed

**`Throws`**

Error if the API call fails or network issues occur.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const pauseResult = await result.session.betaPauseAsync();
  if (pauseResult.success) {
    console.log('Session paused successfully');
  }
}
```

**`Remarks`**

**Behavior:**
- Initiates pause operation through PauseSessionAsync API
- Polls session status until PAUSED state or timeout
- Session state transitions: RUNNING -> PAUSING -> PAUSED
- All session state is preserved during pause

**Important Notes:**
- Paused sessions cannot perform operations (deletion, task execution, etc.)
- Use [betaResumeAsync](#betaresumeasync) to restore the session to RUNNING state
- During pause, both resource usage and costs are lower
- If timeout is exceeded, returns with success=false

**`See`**

[betaResumeAsync](#betaresumeasync)

___

### betaResumeAsync

▸ **betaResumeAsync**(`timeout?`, `pollInterval?`): `Promise`\<`SessionResumeResult`\>

Asynchronously resume this session (beta) from a paused state.

This method calls the ResumeSessionAsync API to initiate the resume operation and then polls
the GetSession API to check the session status until it becomes RUNNING or until timeout is reached.
After resuming, the session restores full functionality and can perform all operations normally.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `timeout` | `number` | `600` | Timeout in seconds to wait for the session to resume. Defaults to 600 seconds. |
| `pollInterval` | `number` | `2.0` | Interval in seconds between status polls. Defaults to 2.0 seconds. |

#### Returns

`Promise`\<`SessionResumeResult`\>

Promise resolving to SessionResumeResult containing:
         - success: Whether the resume operation succeeded
         - requestId: Unique identifier for this API request
         - status: Final session status (should be "RUNNING" if successful)
         - errorMessage: Error description if resume failed

**`Throws`**

Error if the API call fails or network issues occur.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.get('paused_session_id');
if (result.success) {
  const resumeResult = await result.session.betaResumeAsync();
  if (resumeResult.success) {
    console.log('Session resumed successfully');
  }
}
```

**`Remarks`**

**Behavior:**
- Initiates resume operation through ResumeSessionAsync API
- Polls session status until RUNNING state or timeout
- Session state transitions: PAUSED -> RESUMING -> RUNNING
- All previous session state is restored during resume

**Important Notes:**
- Only sessions in PAUSED state can be resumed
- After resume, the session can perform all operations normally
- Use [betaPauseAsync](#betapauseasync) to put a session into PAUSED state
- If timeout is exceeded, returns with success=false

**`See`**

[betaPauseAsync](#betapauseasync)

___

### callMcpTool

▸ **callMcpTool**(`toolName`, `args`, `autoGenSession?`): `Promise`\<``McpToolResult``\>

Call an MCP tool and return the result in a format compatible with Agent.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `toolName` | `string` | `undefined` | Name of the MCP tool to call |
| `args` | `any` | `undefined` | Arguments to pass to the tool |
| `autoGenSession` | `boolean` | `false` | Whether to automatically generate session if not exists (default: false) |

#### Returns

`Promise`\<``McpToolResult``\>

McpToolResult containing the response data

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const shellResult = await result.session.callMcpTool('shell', { command: "echo 'Hello'" });
  console.log(`Output: ${shellResult.data}`);
  await result.session.delete();
}
```

**`Remarks`**

For press_keys tool, key names are automatically normalized to correct case format.
This improves case compatibility (e.g., "CTRL" -> "Ctrl", "tab" -> "Tab").

___

### delete

▸ **delete**(`syncContext?`): `Promise`\<``DeleteResult``\>

Deletes the session and releases all associated resources.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `syncContext` | `boolean` | `false` | Whether to synchronize context data before deletion. If true, uploads all context data to OSS. If false but browser replay is enabled, syncs only the recording context. Defaults to false. |

#### Returns

`Promise`\<``DeleteResult``\>

Promise resolving to DeleteResult containing:
         - success: Whether deletion succeeded
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if deletion failed

**`Throws`**

Error if the API call fails or network issues occur.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  await result.session.fileSystem.writeFile('/tmp/data.txt', 'data');
  const deleteResult = await result.session.delete(true);
  console.log('Session deleted:', deleteResult.success);
}
```

**`Remarks`**

**Behavior:**
- If `syncContext=true`: Uploads all context data to OSS before deletion
- If `syncContext=false` but browser replay enabled: Syncs only recording context
- If `syncContext=false` and no browser replay: Deletes immediately without sync
- Continues with deletion even if context sync fails
- Releases all associated resources (browser, computer, mobile, etc.)

**Best Practices:**
- Use `syncContext=true` when you need to preserve context data for later retrieval
- For temporary sessions, use `syncContext=false` for faster cleanup
- Always call `delete()` when done to avoid resource leaks
- Handle deletion errors gracefully in production code

**`See`**

[info](#info), [ContextManager.sync](context-manager.md#sync)

___

### getLabels

▸ **getLabels**(): `Promise`\<`OperationResult`\>

Gets the labels for this session.

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the labels as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  await result.session.setLabels({ project: 'demo', env: 'test' });
  const getResult = await result.session.getLabels();
  console.log('Labels:', JSON.stringify(getResult.data));
  await result.session.delete();
}
```

___

### getLink

▸ **getLink**(`protocolType?`, `port?`, `options?`): `Promise`\<`OperationResult`\>

Retrieves an access link for the session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `protocolType?` | `string` | Protocol type for the link (optional, reserved for future use) |
| `port?` | `number` | Specific port number to access (default open range: [30100, 30199]; other ports require whitelist approval via agentbay_dev@alibabacloud.com). If not specified, returns the default session link. |
| `options?` | `string` | - |

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult containing:
         - success: Whether the operation succeeded
         - data: String URL for accessing the session
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if operation failed

**`Throws`**

Error if the API call fails or port is out of valid range.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const linkResult = await result.session.getLink();
  console.log(`Session link: ${linkResult.data}`);
  await result.session.delete();
}
```

**`Remarks`**

**Behavior:**
- Without port: Returns the default session access URL
- With port: Returns URL for accessing specific port-mapped service
- Default open port range: [30100, 30199]; other ports require whitelist approval
- For ADB connections, use `session.mobile.getAdbUrl()` with appropriate ADB public key

**Best Practices:**
- Use default link for general session access
- Use port-specific links when you've started services on specific ports
- Validate port range before calling to avoid errors

**`See`**

[info](#info)

___

### getLinkAsync

▸ **getLinkAsync**(`protocolType?`, `port?`, `options?`): `Promise`\<`OperationResult`\>

Asynchronously get a link associated with the current session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `protocolType?` | `string` | Optional protocol type to use for the link |
| `port?` | `number` | Optional port to use for the link (default open range: [30100, 30199]; other ports require whitelist approval) |
| `options?` | `string` | - |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult containing the link as data and request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const linkResult = await result.session.getLinkAsync(undefined, 30150);
  console.log(`Port link: ${linkResult.data}`);
  await result.session.delete();
}
```

### getMetrics

▸ **getMetrics**(): `Promise`\<``SessionMetricsResult``\>

Get runtime metrics for this session.

The underlying service returns a JSON string. This method parses it and
returns a structured result.

#### Returns

`Promise`\<``SessionMetricsResult``\>

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: "your_api_key" });
const create = await agentBay.create({ imageId: "linux_latest" });
if (create.success && create.session) {
  const metrics = await create.session.getMetrics();
  console.log(metrics.data);
  await create.session.delete();
}
```

### info

▸ **info**(): `Promise`\<`OperationResult`\>

Retrieves detailed information about the current session.

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult containing:
         - success: Whether the operation succeeded (always true if no exception)
         - data: SessionInfo object with the following fields:
           - sessionId (string): The session identifier
           - resourceUrl (string): URL for accessing the session
           - appId (string): Application ID (for desktop sessions)
           - authCode (string): Authentication code
           - connectionProperties (string): Connection configuration
           - resourceId (string): Resource identifier
           - resourceType (string): Type of resource (e.g., "Desktop")
           - ticket (string): Access ticket
         - requestId: Unique identifier for this API request
         - errorMessage: Error description if operation failed

**`Throws`**

Error if the API request fails or response is invalid.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const infoResult = await result.session.info();
  console.log(`Session ID: ${infoResult.data.sessionId}`);
  console.log(`Resource URL: ${infoResult.data.resourceUrl}`);
  await result.session.delete();
}
```

**`Remarks`**

**Behavior:**
- This method calls the GetMcpResource API to retrieve session metadata
- The returned SessionInfo contains:
  - sessionId: The session identifier
  - resourceUrl: URL for accessing the session
  - Desktop-specific fields (appId, authCode, connectionProperties, etc.)
    are populated from the DesktopInfo section of the API response
- Session info is retrieved from the AgentBay API in real-time
- The resourceUrl can be used for browser-based access
- Desktop-specific fields (appId, authCode) are only populated for desktop sessions
- This method does not modify the session state

**`See`**

[delete](#delete), [getLink](#getlink)

___

### keepAlive

▸ **keepAlive**(): `Promise`\<`OperationResult`\>

Refresh the backend idle timer for this session.

This method calls the RefreshSessionIdleTime API.

#### Returns

`Promise`\<`OperationResult`\>

___

### keepAliveAsync

▸ **keepAliveAsync**(): `Promise`\<`OperationResult`\>

Alias of keepAlive for API compatibility.

#### Returns

`Promise`\<`OperationResult`\>

___

### listMcpTools

▸ **listMcpTools**(`imageId?`): `Promise`\<`McpToolsResult`\>

List MCP tools available for this session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `imageId?` | `string` | Optional image ID, defaults to session's imageId or "linux_latest" |

#### Returns

`Promise`\<`McpToolsResult`\>

McpToolsResult containing tools list and request ID

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const toolsResult = await result.session.listMcpTools();
  console.log(`Found ${toolsResult.tools.length} MCP tools`);
  await result.session.delete();
}
```

___

### setLabels

▸ **setLabels**(`labels`): `Promise`\<`OperationResult`\>

Sets the labels for this session.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `labels` | `Record`\<`string`, `string`\> | The labels to set for the session. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure with request ID

**`Throws`**

Error if the operation fails (matching Python SessionError)

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.create();
if (result.success) {
  const setResult = await result.session.setLabels({ project: 'demo', env: 'test' });
  console.log('Labels set:', setResult.success);
  await result.session.delete();
}
```

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../../common-features/advanced/oss.md)

