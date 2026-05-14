# Context Mount API Reference

## Related Tutorial

- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md) - Learn about context mount and data persistence

## Class ContextMount

```java
public class ContextMount
```

ContextMount provides direct-mount write-through persistence where data is persisted immediately without manual sync calls. Unlike ContextSync which requires explicit synchronization, mounted paths act as live persistent storage.

### Enums

#### AccessMode

```java
public enum AccessMode {
    READ_WRITE("readWrite"),
    READ_ONLY("readOnly");
}
```

#### Strategy

```java
public enum Strategy {
    STANDARD("standard"),
    PERFORMANCE("performance");
}
```

### Constructors

#### create

```java
public static ContextMount create(String contextId, String path)
```

Creates a new ContextMount with default access mode (READ_WRITE) and strategy (STANDARD).

**Parameters:**

| Name | Type | Description |
| :------ | :------ | :------ |
| `contextId` | `String` | The ID of the context to mount |
| `path` | `String` | The path where the context should be mounted in the session |

**Returns:** `ContextMount`

### Methods

#### withAccessMode

```java
public ContextMount withAccessMode(AccessMode accessMode)
```

Sets the access mode and returns the context mount for chaining.

#### withStrategy

```java
public ContextMount withStrategy(Strategy strategy)
```

Sets the mount strategy and returns the context mount for chaining.

#### toMountConfigJSON

```java
public String toMountConfigJSON()
```

Serializes the mount configuration to a JSON string for the API protocol.

**Returns:** `String` - JSON string like `{"accessMode":"readWrite","storageMode":"standard"}`

#### Getters

```java
public String getContextId()
public String getPath()
public AccessMode getAccessMode()
public Strategy getStrategy()
```

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)
- [Context Sync API Reference](context-sync.md)

---

*Documentation generated from Java source code.*
