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

#### access_mode: `BetaContextMountAccessMode`

```python
access_mode = BetaContextMountAccessMode.READ_WRITE
```

#### strategy: `BetaContextMountStrategy`

```python
strategy = BetaContextMountStrategy.STANDARD
```

### new

```python
@classmethod
def new(cls,
        context_id: str,
        path: str,
        access_mode: Optional[BetaContextMountAccessMode] = None,
        strategy: Optional[BetaContextMountStrategy] = None)
```

### with_access_mode

```python
def with_access_mode(access_mode: BetaContextMountAccessMode)
```

### with_strategy

```python
def with_strategy(strategy: BetaContextMountStrategy)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
