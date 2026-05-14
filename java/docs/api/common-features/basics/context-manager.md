# 🗂️ Context-manager API Reference

## Overview

The Context-manager module provides specialized functionality for the AgentBay cloud platform. It includes various methods and utilities to interact with cloud services and manage resources.

## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn about context management and data persistence

## ContextManager

### Constructor

```java
public ContextManager(Session session)
```

### Methods

### info

```java
public ContextInfoResult info()
```

```java
public ContextInfoResult info(String contextId, String path, String taskType)
```

Get information about context synchronization status.

**Parameters:**
- `contextId` (String): Optional ID of the context to get information for
- `path` (String): Optional path where the context is mounted
- `taskType` (String): Optional type of task to get information for (e.g., "upload", "download")

**Returns:**
- `ContextInfoResult`: ContextInfoResult Result object containing context status data and request ID

### sync

```java
public ContextSyncResult sync()
```

```java
public ContextSyncResult sync(String contextId, String path, String mode)
```

```java
public ContextSyncResult sync(Consumer<Boolean> callback)
```

```java
public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback)
```

```java
public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback, int maxRetries, int retryInterval)
```

Sync context data with optional parameters and callback mode (non-blocking).
Returns immediately and calls the callback when sync completes.

**Parameters:**
- `contextId` (String): Optional ID of the context to synchronize
- `path` (String): Optional path where the context should be mounted
- `mode` (String): Optional synchronization mode (e.g., "upload", "download")
- `callback` (Consumer<Boolean>): Callback function that receives success status (true if successful, false otherwise)
- `maxRetries` (int): Maximum number of retries for polling completion status (default: 150)
- `retryInterval` (int): Initial interval in milliseconds for exponential backoff polling (default: 500)

**Returns:**
- `ContextSyncResult`: ContextSyncResult indicating initial sync trigger success/failure

### syncAndWait

```java
public ContextSyncResult syncAndWait()
```

```java
public ContextSyncResult syncAndWait(String contextId, String path, String mode)
```

```java
public ContextSyncResult syncAndWait(String contextId, String path, String mode, int maxRetries, int retryInterval)
```

Sync context data with optional parameters and wait for completion

**Parameters:**
- `contextId` (String): Context ID (optional)
- `path` (String): Path (optional)
- `mode` (String): Sync mode (optional)
- `maxRetries` (int): Maximum number of retries for polling completion status (default: 150)
- `retryInterval` (int): Initial interval in milliseconds for exponential backoff polling (default: 500)

**Returns:**
- `ContextSyncResult`: ContextSyncResult indicating success/failure after waiting for completion

### bind

```java
public ContextBindResult bind(List<ContextSync> contexts, boolean waitForCompletion)
```

```java
public ContextBindResult bind(ContextSync context)
```

```java
public ContextBindResult bind(BetaContextMount context)
```

```java
public ContextBindResult bind(BetaContextMount context, boolean waitForCompletion)
```

Dynamically binds one or more contexts to the current session.

<pre>{@code
ContextSync cs = ContextSync.create(contextId, "/tmp/ctx-data", null);
ContextBindResult result = session.getContext().bind(cs);
System.out.println("Bind success: " + result.isSuccess());
}</pre>

**Parameters:**
- `contexts` (List<ContextSync>): List of ContextSync objects to bind
- `waitForCompletion` (boolean): Whether to poll until all bindings are confirmed

**Returns:**
- `ContextBindResult`: ContextBindResult with the result of the operation

### listBindings

```java
public ContextBindingsResult listBindings()
```

Lists all context bindings for the current session.

<pre>{@code
ContextBindingsResult result = session.getContext().listBindings();
for (ContextBinding b : result.getBindings()) {
    System.out.println("Context " + b.getContextId() + " at " + b.getPath());
}
}</pre>

**Returns:**
- `ContextBindingsResult`: ContextBindingsResult with the list of bindings



## 🔗 Related Resources

- [Context API Reference](../../../api/common-features/basics/context.md)
- [Session API Reference](../../../api/common-features/basics/session.md)

