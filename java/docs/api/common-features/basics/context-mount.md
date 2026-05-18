# 📂 Context-mount API Reference

## Overview

[Beta] BetaContextMount provides direct-mount write-through persistence where data is persisted immediately without manual sync calls. Unlike ContextSync, mounted paths act as live persistent storage. Requires imageId=aio-ubuntu-2404 on the session.


## 📚 Tutorial

[Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)

Learn how Context Mount provides direct-mount write-through persistence

## BetaContextMount

[Beta] Defines the context mount configuration for direct-mount persistence.

<p>Unlike ContextSync which requires explicit synchronization, BetaContextMount provides
write-through persistence where data is persisted immediately without manual sync calls.</p>

<p><b>IMPORTANT:</b> BetaContextMount requires {@code imageId="aio-ubuntu-2404"} on
the session. Other images do not provide a real OSS-backed mount — writes are not
persisted to the shared context store and are invisible to other sessions even with
the same contextId and mount path.</p>

<p>Use {@link #withSourcePath(String)} to mount only a subdirectory of the context.
The subdirectory's contents are projected to the mount root.</p>

### Constructor

```java
public BetaContextMount()
```

```java
public BetaContextMount(String contextId, String path)
```

```java
public BetaContextMount(String contextId, String path, AccessMode accessMode, Strategy strategy)
```

### Methods

### create

```java
public static BetaContextMount create(String contextId, String path)
```

### withAccessMode

```java
public BetaContextMount withAccessMode(AccessMode accessMode)
```

### withStrategy

```java
public BetaContextMount withStrategy(Strategy strategy)
```

### withSourcePath

```java
public BetaContextMount withSourcePath(String sourcePath)
```

Set the subpath within the context to mount. Empty string (default) mounts
the entire context. The selected subdirectory's contents are projected to
the mount root.

### getAccessMode

```java
public AccessMode getAccessMode()
```

### setAccessMode

```java
public void setAccessMode(AccessMode accessMode)
```

### getStrategy

```java
public Strategy getStrategy()
```

### setStrategy

```java
public void setStrategy(Strategy strategy)
```

### getSourcePath

```java
public String getSourcePath()
```

### setSourcePath

```java
public void setSourcePath(String sourcePath)
```



## 🔗 Related Resources

- [Context Manager API Reference](../../../api/common-features/basics/context-manager.md)
- [Session API Reference](../../../api/common-features/basics/session.md)

