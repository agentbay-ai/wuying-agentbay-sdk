# Context Mount API Reference

## ContextMountAccessMode

```python
class ContextMountAccessMode(Enum)
```

Access mode for context mount

#### READ_WRITE

```python
READ_WRITE = "readWrite"
```

#### READ_ONLY

```python
READ_ONLY = "readOnly"
```

## ContextMountStrategy

```python
class ContextMountStrategy(Enum)
```

Mount strategy for context mount

#### STANDARD

```python
STANDARD = "standard"
```

#### PERFORMANCE

```python
PERFORMANCE = "performance"
```

## ContextMount

```python
@dataclass
class ContextMount()
```

Defines the context mount configuration for direct-mount persistence.

Unlike ContextSync which requires explicit synchronization, ContextMount
provides write-through persistence where data is persisted immediately
without manual sync calls.

**Attributes**:

    context_id: ID of the context to mount
    path: Path where the context should be mounted in the session
    access_mode: Access permission for the mount (read_write or read_only)
    strategy: Mount strategy (standard or performance)

#### context_id: `str`

```python
context_id = None
```

#### path: `str`

```python
path = None
```

#### access_mode: `ContextMountAccessMode`

```python
access_mode = ContextMountAccessMode.READ_WRITE
```

#### strategy: `ContextMountStrategy`

```python
strategy = ContextMountStrategy.STANDARD
```

### new

```python
@classmethod
def new(cls,
        context_id: str,
        path: str,
        access_mode: Optional[ContextMountAccessMode] = None,
        strategy: Optional[ContextMountStrategy] = None)
```

### with_access_mode

```python
def with_access_mode(access_mode: ContextMountAccessMode)
```

### with_strategy

```python
def with_strategy(strategy: ContextMountStrategy)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
