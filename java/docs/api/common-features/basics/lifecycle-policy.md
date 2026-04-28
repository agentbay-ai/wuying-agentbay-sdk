# ⏱ Lifecycle-policy API Reference

## Overview

The LifecyclePolicy class provides fine-grained control over session lifecycle.
It supports idle release timeout, maximum runtime, and manual release options.
All time values are in minutes. When set, SDK takes full control of session lifecycle
and overrides console defaults.


## 📚 Tutorial

[Session Lifecycle Guide](../../../../../docs/guides/common-features/basics/session-management.md)

Learn how to control session lifecycle with idle release, max runtime, and manual release

## LifecyclePolicy

Lifecycle policy for session management.

Controls how and when a session is automatically released.
When used, SDK takes full control of lifecycle - console defaults are overridden.
All time values are in MINUTES.

### Constructor

```java
public LifecyclePolicy()
```

Default constructor: idle=5min, max=30min, manual=false

```java
public LifecyclePolicy(int idleReleaseTimeout, int maxRuntime)
```

Custom timeouts constructor.

**Parameters:**
- `idleReleaseTimeout` (int): idle timeout in minutes (must be positive)
- `maxRuntime` (int): maximum runtime in minutes (must be positive)

```java
public LifecyclePolicy(int idleReleaseTimeout, int maxRuntime, boolean manualRelease)
```

Full constructor with manual release validation.

**Parameters:**
- `idleReleaseTimeout` (int): idle timeout in minutes
- `maxRuntime` (int): maximum runtime in minutes
- `manualRelease` (boolean): when true, idle and max cannot be non-zero defaults

### Methods

### manualRelease

```java
public static LifecyclePolicy manualRelease()
```

Factory method for manual release mode.

**Returns:**
- `LifecyclePolicy`: policy with manual release only (no automatic idle/max limits)

### getIdleReleaseTimeout

```java
public int getIdleReleaseTimeout()
```

### getMaxRuntime

```java
public int getMaxRuntime()
```

### isManualRelease

```java
public boolean isManualRelease()
```



## 💡 Best Practices

- Use LifecyclePolicy instead of the deprecated idle_release_timeout parameter for new code
- Set max_runtime to prevent runaway sessions from consuming resources indefinitely
- Use manual_release=true for interactive workflows where session duration is unpredictable
- The backend requires idle_release_timeout >= 3 minutes

## 🔗 Related Resources

- [Session Params API Reference](../../../api/common-features/basics/session-params.md)
- [Session API Reference](../../../api/common-features/basics/session.md)

