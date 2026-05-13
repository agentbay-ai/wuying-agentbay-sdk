# 💾 Context API Reference

## Overview

The Context module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn about context management and data persistence

## ContextService

### Constructor

```java
public ContextService(AgentBay agentBay)
```

### Methods

### list

```java
public ContextListResult list(ContextListParams params)
```

```java
public ContextListResult list()
```

Lists all available contexts with pagination support.

**Parameters:**
- `params` (ContextListParams): Parameters for listing contexts. If null, defaults will be used.

**Returns:**
- `ContextListResult`: A result object containing the list of Context objects, pagination information, and request ID.

### get

```java
public ContextResult get(String name, boolean create, String regionId)
```

```java
public ContextResult get(String name, boolean create)
```

```java
public ContextResult get(String name)
```

Gets a context by name or ID. Optionally creates it if it doesn't exist.

**Parameters:**
- `name` (String): The name of the context to get.
- `create` (boolean): Whether to create the context if it doesn't exist.
- `regionId` (String): The region ID for the request.

**Returns:**
- `ContextResult`: The ContextResult object containing the Context and request ID.
        The result contains:
        <ul>
        <li>success: true if the operation succeeded</li>
        <li>context: the Context object (if success is true)</li>
        <li>contextId: the ID of the context</li>
        <li>requestId: unique identifier for this API request</li>
        <li>errorMessage: error description (if success is false)</li>
        </ul>

**Throws:**
- `AgentBayException`: if neither name nor contextId is provided, or if create=true with contextId.

### create

```java
public ContextResult create(String name)
```

Creates a new context with the given name.

**Parameters:**
- `name` (String): The name for the new context.

**Returns:**
- `ContextResult`: The created ContextResult object with request ID.

### delete

```java
public com.aliyun.agentbay.model.OperationResult delete(Context context) throws AgentBayException
```

Deletes the specified context.

**Parameters:**
- `context` (Context): The Context object to delete.

**Returns:**
- `com.aliyun.agentbay.model.OperationResult`: OperationResult containing success status and request ID.

### clear

```java
public com.aliyun.agentbay.model.OperationResult clear(String contextId) throws AgentBayException
```

Clears all data in the specified context.

**Parameters:**
- `contextId` (String): The ID of the context to clear.

**Returns:**
- `com.aliyun.agentbay.model.OperationResult`: OperationResult containing success status and request ID.

**Throws:**
- `AgentBayException`: if an API or network error occurs during execution.

### getFileDownloadUrl

```java
public com.aliyun.agentbay.model.FileUrlResult getFileDownloadUrl(String contextId, String filePath) throws AgentBayException
```

Gets a presigned download URL for a file in a context.

**Parameters:**
- `contextId` (String): The ID of the context.
- `filePath` (String): The path of the file to download.

**Returns:**
- `com.aliyun.agentbay.model.FileUrlResult`: FileUrlResult containing the presigned URL, expiration time, and request ID.

Note: The presigned URL expires in 1 hour by default.

### getFileUploadUrl

```java
public com.aliyun.agentbay.model.FileUrlResult getFileUploadUrl(String contextId, String filePath) throws AgentBayException
```

Gets a presigned upload URL for a file in a context.

**Parameters:**
- `contextId` (String): The ID of the context.
- `filePath` (String): The path of the file to upload.

**Returns:**
- `com.aliyun.agentbay.model.FileUrlResult`: FileUrlResult containing the presigned URL, expiration time, and request ID.

Note:The presigned URL expires in 1 hour by default.

### deleteFile

```java
public com.aliyun.agentbay.model.OperationResult deleteFile(String contextId, String filePath) throws AgentBayException
```

Deletes a file in a context.

**Parameters:**
- `contextId` (String): The ID of the context.
- `filePath` (String): The path of the file to delete.

**Returns:**
- `com.aliyun.agentbay.model.OperationResult`: OperationResult containing success status and request ID.

### listFiles

```java
public ContextFileListResult listFiles(String contextId, String parentFolderPath, int pageNumber, int pageSize)
```

```java
public ContextFileListResult listFiles(String contextId, String parentFolderPath, Integer maxResults, String nextToken)
```

```java
public ContextFileListResult listFiles(String contextId, String parentFolderPath)
```

Lists files under a specific folder path in a context using max-results and next-token pagination.

**Parameters:**
- `contextId` (String): The ID of the context.
- `parentFolderPath` (String): The parent folder path to list files from.
- `maxResults` (Integer): Maximum number of results to return (may be null to omit).
- `nextToken` (String): Token for the next page (may be null for the first page).

**Returns:**
- `ContextFileListResult`: ContextFileListResult containing the list of files, next token, and request ID.



## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Context Manager API Reference](../../../api/common-features/basics/context-manager.md)

