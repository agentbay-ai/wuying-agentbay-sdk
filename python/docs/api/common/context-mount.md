# Context Mount [Beta] API Reference

## BetaContextMountAccessMode

```python
class BetaContextMountAccessMode(Enum)
```

Access mode for context mount (beta)

#### READ_WRITE

```python
READ_WRITE = "readWrite"
```

#### READ_ONLY

```python
READ_ONLY = "readOnly"
```

## BetaContextMountStrategy

```python
class BetaContextMountStrategy(Enum)
```

Mount strategy for context mount (beta)

#### STANDARD

```python
STANDARD = "standard"
```

#### PERFORMANCE

```python
PERFORMANCE = "performance"
```

## BetaContextMount

```python
@dataclass
class BetaContextMount()
```

[Beta] Defines the context mount configuration for direct-mount persistence.

Unlike ContextSync which requires explicit synchronization, BetaContextMount
provides write-through persistence where data is persisted immediately
without manual sync calls.

IMPORTANT: BetaContextMount requires image_id="aio-ubuntu-2404" on the
session. Other images do not provide a real OSS-backed mount — writes are
not persisted to the shared context store and are invisible to other
sessions even with the same context_id and mount path.

**Attributes**:

    context_id: ID of the context to mount
    path: Path where the context should be mounted in the session
    access_mode: Access permission for the mount (read_write or read_only)
    strategy: Mount strategy (standard or performance)
    source_path: Subpath within the context to mount; empty string mounts entire context

#### context_id: `str`

```python
context_id = None
```

#### path: `str`

```python
path = None
```

#### access_mode: `BetaContextMountAccessMode`

```python
access_mode = BetaContextMountAccessMode.READ_WRITE
```

#### strategy: `BetaContextMountStrategy`

```python
strategy = BetaContextMountStrategy.STANDARD
```

#### source_path: `str`

```python
source_path = ""
```

### new

```python
@classmethod
def new(cls,
        context_id: str,
        path: str,
        access_mode: Optional[BetaContextMountAccessMode] = None,
        strategy: Optional[BetaContextMountStrategy] = None,
        source_path: Optional[str] = None)
```

### with_access_mode

```python
def with_access_mode(access_mode: BetaContextMountAccessMode)
```

### with_strategy

```python
def with_strategy(strategy: BetaContextMountStrategy)
```

### with_source_path

```python
def with_source_path(source_path: str)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
