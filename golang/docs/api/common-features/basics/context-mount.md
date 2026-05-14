# Context Mount API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type ContextMount

```go
type ContextMount struct {
	// ContextID is the ID of the context to mount
	ContextID	string
	// Path is the path where the context should be mounted in the session
	Path	string
	// AccessMode defines the access permission (read_write or read_only)
	AccessMode	ContextMountAccessMode
	// Strategy defines the mount strategy (standard or performance)
	Strategy	ContextMountStrategy
}
```

ContextMount defines the context mount configuration for direct-mount persistence. Unlike
ContextSync which requires explicit synchronization, ContextMount provides write-through persistence
where data is persisted immediately.

### Methods

### WithAccessMode

```go
func (cm *ContextMount) WithAccessMode(accessMode ContextMountAccessMode) *ContextMount
```

WithAccessMode sets the access mode and returns the context mount for chaining.

### WithStrategy

```go
func (cm *ContextMount) WithStrategy(strategy ContextMountStrategy) *ContextMount
```

WithStrategy sets the mount strategy and returns the context mount for chaining.

### Related Functions

### NewContextMount

```go
func NewContextMount(contextID, path string) *ContextMount
```

NewContextMount creates a new context mount configuration with default values.

## Type ContextMountAccessMode

```go
type ContextMountAccessMode string
```

ContextMountAccessMode defines the access mode for context mount

## Type ContextMountStrategy

```go
type ContextMountStrategy string
```

ContextMountStrategy defines the mount strategy for context mount

## Functions

### NewContextMount

```go
func NewContextMount(contextID, path string) *ContextMount
```

NewContextMount creates a new context mount configuration with default values.

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
