# 🌐 Env API Reference

## Overview

The Env module provides methods for setting and querying global environment variables within a session sandbox.
Variables set via this module persist across all MCP tools (shell, code interpreter, etc.) within the session.


## Env

Environment variable management service for AgentBay sessions.

<p>Provides methods to set and get global environment variables that persist
across all MCP tools (shell, code interpreter, etc.) within a session.</p>

### Constructor

```java
public Env(Session session)
```

### Methods

### set

```java
public BoolResult set(Map<String, String> envs)
```

Set or update global environment variables in the session sandbox.

**Parameters:**
- `envs` (Map<String,String>): Map of environment variable key-value pairs. Must not be empty.

**Returns:**
- `BoolResult`: BoolResult indicating success or failure

**Throws:**
- `IllegalArgumentException`: if envs is null or empty

### get

```java
public EnvResult get(String... keys)
```

Get global environment variables from the session sandbox.

**Parameters:**
- `keys` (String): Optional specific variable names to retrieve. If empty or null, returns all.

**Returns:**
- `EnvResult`: EnvResult containing the variable key-value pairs



## EnvResult

Result of environment variable get operations.

### Constructor

```java
public EnvResult()
```

```java
public EnvResult(String requestId, boolean success, Map<String, String> envs, String errorMessage)
```

### Methods

### isSuccess

```java
public boolean isSuccess()
```

### setSuccess

```java
public void setSuccess(boolean success)
```

### getEnvs

```java
public Map<String, String> getEnvs()
```

### setEnvs

```java
public void setEnvs(Map<String, String> envs)
```

### getErrorMessage

```java
public String getErrorMessage()
```

### setErrorMessage

```java
public void setErrorMessage(String errorMessage)
```



## BoolResult

### Constructor

```java
public BoolResult()
```

```java
public BoolResult(String requestId, boolean success, Boolean data, String errorMessage)
```

### Methods

### isSuccess

```java
public boolean isSuccess()
```

### setSuccess

```java
public void setSuccess(boolean success)
```

### getData

```java
public Boolean getData()
```

### setData

```java
public void setData(Boolean data)
```

### getErrorMessage

```java
public String getErrorMessage()
```

### setErrorMessage

```java
public void setErrorMessage(String errorMessage)
```



## 💡 Best Practices

- Use env.set to configure variables before running shell commands or code
- Both keys and values must be strings
- Setting a key that already exists will overwrite the previous value
- Use env.get with specific keys to reduce response size

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [Command API Reference](../../../api/common-features/basics/command.md)

