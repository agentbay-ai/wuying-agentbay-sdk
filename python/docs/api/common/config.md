# Configuration API Reference

## Config

```python
class Config()
```

Configuration object for AgentBay client.

The preferred input is ``region_id``; the SDK derives the endpoint from it
via direct pattern substitution. ``endpoint`` is retained as a deprecated
fallback: when ``region_id`` is not set the value of ``endpoint`` is used
as-is. When both are set, ``region_id`` wins and ``endpoint`` is ignored.
Either form emits a ``DeprecationWarning``.

.. deprecated:: 0.22.0
    ``endpoint`` parameter. Use ``region_id`` instead.

### __init__

```python
def __init__(self, timeout_ms: Optional[int] = None,
             region_id: Optional[str] = None,
             endpoint: Optional[str] = None)
```

#### BROWSER_RECORD_PATH

```python
BROWSER_RECORD_PATH = "/home/wuying/record"
```

## See Also

- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)

---

*Documentation generated automatically from source code using pydoc-markdown.*
