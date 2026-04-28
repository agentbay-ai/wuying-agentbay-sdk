# Lifecycle Policy API Reference

## LifecyclePolicy

```python
class LifecyclePolicy()
```

Lifecycle policy for session management.

Controls how and when a session is automatically released.
When used, SDK takes full control of lifecycle — console defaults are overridden.

All time values are in MINUTES.

**Attributes**:

    idle_release_timeout: Minutes of inactivity before auto-release (default: 5).
    max_runtime: Maximum total runtime in minutes from creation (default: 30).
    manual_release: If True, disables all auto-release; session only ends via delete().

### __init__

```python
def __init__(self, idle_release_timeout: Optional[int] = None,
             max_runtime: Optional[int] = None,
             manual_release: bool = False)
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
