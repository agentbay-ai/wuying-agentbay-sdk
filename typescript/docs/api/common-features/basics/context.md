# Class: ContextService

## 💾 Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context management and data persistence

Provides methods to manage persistent contexts in the AgentBay cloud environment.

## Table of contents


### Methods

- [clear](#clear)
- [clearAsync](#clearasync)
- [create](#create)
- [delete](#delete)
- [deleteFile](#deletefile)
- [get](#get)
- [getFileDownloadUrl](#getfiledownloadurl)
- [getFileUploadUrl](#getfileuploadurl)
- [list](#list)
- [listFiles](#listfiles)
- [update](#update)

## Methods

### clear

▸ **clear**(`contextId`, `timeout?`, `pollInterval?`): `Promise`\<`ClearContextResult`\>

Synchronously clear the context's persistent data and wait for the final result.

This method wraps the `clearAsync` and `getClearStatus` polling logic,
providing the simplest and most direct way to handle clearing tasks.

The clearing process transitions through the following states:
- "clearing": Data clearing is in progress
- "available": Clearing completed successfully (final success state)

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId` | `string` | `undefined` | Unique ID of the context to clear. |
| `timeout` | `number` | `60` | (Optional) Timeout in seconds to wait for task completion, default is 60 seconds. |
| `pollInterval` | `number` | `2.0` | (Optional) Interval in seconds between status polls, default is 2 seconds. |

#### Returns

`Promise`\<`ClearContextResult`\>

A ClearContextResult object containing the final task result.
         The status field will be "available" on success, or other states if interrupted.

**`Throws`**

APIError - If the task fails to complete within the specified timeout.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const getResult = await agentBay.context.get('my-context');
if (getResult.success) {
  const clearResult = await agentBay.context.clear(getResult.context.id);
  console.log('Context cleared:', clearResult.success);
  console.log('Final status:', clearResult.status);
}
```

___

### clearAsync

▸ **clearAsync**(`contextId`): `Promise`\<`ClearContextResult`\>

Asynchronously initiate a task to clear the context's persistent data.

This is a non-blocking method that returns immediately after initiating the clearing task
on the backend. The context's state will transition to "clearing" while the operation
is in progress.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | Unique ID of the context to clear. |

#### Returns

`Promise`\<`ClearContextResult`\>

A ClearContextResult object indicating the task has been successfully started,
         with status field set to "clearing".

**`Throws`**

APIError - If the backend API rejects the clearing request (e.g., invalid ID).

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const getResult = await agentBay.context.get('my-context');
if (getResult.success) {
  const clearResult = await agentBay.context.clearAsync(getResult.context.id);
  console.log('Clear task started:', clearResult.success);
  console.log('Status:', clearResult.status);
}
```

___

### create

▸ **create**(`name`): `Promise`\<`ContextResult`\>

Creates a new context with the given name.
Corresponds to Python's create() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `name` | `string` | The name for the new context. |

#### Returns

`Promise`\<`ContextResult`\>

ContextResult with created context data and requestId

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.context.create('my-new-context');
if (result.success) {
  console.log(`Context ID: ${result.context.id}`);
  console.log(`Context Name: ${result.context.name}`);
}
```

___

### delete

▸ **delete**(`context`): `Promise`\<`OperationResult`\>

Deletes the specified context.
Corresponds to Python's delete() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `context` | ``Context`` | The Context object to delete. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult with requestId

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const getResult = await agentBay.context.get('my-context');
if (getResult.success && getResult.context) {
  const deleteResult = await agentBay.context.delete(getResult.context);
  console.log('Context deleted:', deleteResult.success);
}
```

___

### deleteFile

▸ **deleteFile**(`contextId`, `filePath`): `Promise`\<`OperationResult`\>

Delete a file in a context.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file to delete. |

#### Returns

`Promise`\<`OperationResult`\>

OperationResult indicating success or failure.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const contextResult = await agentBay.context.get('my-context');
if (contextResult.success) {
  const deleteResult = await agentBay.context.deleteFile(contextResult.context.id, '/data/file.txt');
  console.log('File deleted:', deleteResult.success);
}
```

___

### get

▸ **get**(`name`, `create?`): `Promise`\<`ContextResult`\>

Retrieves an existing context or creates a new one.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `name` | `string` | `undefined` | The name of the context to retrieve or create. |
| `create` | `boolean` | `false` | If true, creates the context if it doesn't exist. Defaults to false. |

#### Returns

`Promise`\<`ContextResult`\>

Promise resolving to ContextResult containing the Context object.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.context.get('my-context', true);
if (result.success) {
  console.log(`Context ID: ${result.context.id}`);
  console.log(`Context Name: ${result.context.name}`);
}
```

**`See`**

[update](#update), [list](#list)

### getFileDownloadUrl

▸ **getFileDownloadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned download URL for a file in a context.

Note: The presigned URL expires in 1 hour by default.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file in the context. |

#### Returns

`Promise`\<`FileUrlResult`\>

FileUrlResult with the presigned URL and expiration time.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const contextResult = await agentBay.context.get('my-context');
if (contextResult.success) {
  const urlResult = await agentBay.context.getFileDownloadUrl(contextResult.context.id, '/data/file.txt');
  console.log('Download URL:', urlResult.url);
  console.log('Expires at:', urlResult.expireTime);
}
```

___

### getFileUploadUrl

▸ **getFileUploadUrl**(`contextId`, `filePath`): `Promise`\<`FileUrlResult`\>

Get a presigned upload URL for a file in a context.

Note: The presigned URL expires in 1 hour by default.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `string` | The ID of the context. |
| `filePath` | `string` | The path to the file in the context. |

#### Returns

`Promise`\<`FileUrlResult`\>

FileUrlResult with the presigned URL and expiration time.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const contextResult = await agentBay.context.get('my-context', true);
if (contextResult.success) {
  const urlResult = await agentBay.context.getFileUploadUrl(contextResult.context.id, '/data/file.txt');
  console.log('Upload URL:', urlResult.url);
  console.log('Expires at:', urlResult.expireTime);
}
```

___

### list

▸ **list**(`params?`): `Promise`\<`ContextListResult`\>

Lists all available contexts with pagination support.
Corresponds to Python's list() method

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `params?` | `ContextListParams` | Optional parameters for listing contexts. |

#### Returns

`Promise`\<`ContextListResult`\>

ContextListResult with contexts list and pagination information

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const result = await agentBay.context.list({ maxResults: 10 });
if (result.success) {
  console.log(`Total contexts: ${result.totalCount}`);
  console.log(`Page has ${result.contexts.length} contexts`);
}
```

___

### listFiles

▸ **listFiles**(`contextId`, `parentFolderPath`, `pageNumber?`, `pageSize?`, `maxResults?`, `nextToken?`): `Promise`\<`ContextFileListResult`\>

List files under a specific folder path in a context.

#### Parameters

| Name | Type | Default value | Description |
| :------ | :------ | :------ | :------ |
| `contextId` | `string` | `undefined` | The ID of the context. |
| `parentFolderPath` | `string` | `undefined` | The parent folder path to list files from. |
| `pageNumber` | `number` | `1` | Page number for pagination (default: 1). Ignored when `maxResults` or `nextToken` is set. |
| `pageSize` | `number` | `50` | Number of files per page (default: 50). Ignored when `maxResults` or `nextToken` is set. |
| `maxResults?` | `number` | `undefined` | Maximum entries per request (token-based pagination). When set with or without `nextToken`, token pagination is used instead of page number/size. |
| `nextToken?` | `string` | `undefined` | Pagination token from a previous response. |

#### Returns

`Promise`\<`ContextFileListResult`\>

ContextFileListResult with file entries and total count.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const contextResult = await agentBay.context.get('my-context');
if (contextResult.success) {
  const listResult = await agentBay.context.listFiles(contextResult.context.id, '/data');
  console.log(`Found ${listResult.entries.length} files`);
  console.log(`Total count: ${listResult.count}`);
}
```

___

### update

▸ **update**(`context`): `Promise`\<`OperationResult`\>

Updates a context's name.

#### Parameters

| Name | Type | Description |
| :------ | :------ | :------ |
| `context` | ``Context`` | The Context object with updated name. |

#### Returns

`Promise`\<`OperationResult`\>

Promise resolving to OperationResult with success status.

**`Example`**

```typescript
const agentBay = new AgentBay({ apiKey: 'your_api_key' });
const getResult = await agentBay.context.get('old-name');
if (getResult.success && getResult.context) {
  getResult.context.name = 'new-name';
  const updateResult = await agentBay.context.update(getResult.context);
  console.log('Context updated:', updateResult.success);
}
```

**`See`**

[get](#get), [list](#list)

## Related Resources

- [Session API Reference](session.md)
- [Context Manager API Reference](context-manager.md)

