# Context Mount [Beta] API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type BetaContextMount

```go
type BetaContextMount struct {
	// ContextID is the ID of the context to mount
	ContextID	string
	// Path is the path where the context should be mounted in the session
	Path	string
	// AccessMode defines the access permission (read_write or read_only)
	AccessMode	BetaContextMountAccessMode
	// Strategy defines the mount strategy (standard or performance)
	Strategy	BetaContextMountStrategy
}
```

BetaContextMount defines the context mount configuration for direct-mount persistence. Unlike
ContextSync which requires explicit synchronization, BetaContextMount provides write-through
persistence where data is persisted immediately.

### Methods

### WithAccessMode

```go
func (cm *BetaContextMount) WithAccessMode(accessMode BetaContextMountAccessMode) *BetaContextMount
```

WithAccessMode sets the access mode and returns the context mount for chaining.

### WithStrategy

```go
func (cm *BetaContextMount) WithStrategy(strategy BetaContextMountStrategy) *BetaContextMount
```

WithStrategy sets the mount strategy and returns the context mount for chaining.

### Related Functions

### NewBetaContextMount

```go
func NewBetaContextMount(contextID, path string) *BetaContextMount
```

NewBetaContextMount creates a new context mount configuration with default values.

## Type BetaContextMountAccessMode

```go
type BetaContextMountAccessMode string
```

BetaContextMountAccessMode defines the access mode for context mount

## Type BetaContextMountStrategy

```go
type BetaContextMountStrategy string
```

BetaContextMountStrategy defines the mount strategy for context mount

## Functions

### NewBetaContextMount

```go
func NewBetaContextMount(contextID, path string) *BetaContextMount
```

NewBetaContextMount creates a new context mount configuration with default values.

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
