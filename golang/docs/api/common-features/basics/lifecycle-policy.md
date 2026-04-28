# Lifecycle Policy API Reference

## Type LifecyclePolicy

```go
type LifecyclePolicy struct {
	// IdleReleaseTimeout is the idle release timeout in minutes.
	IdleReleaseTimeout	int32
	// MaxRuntime is the maximum session runtime in minutes.
	MaxRuntime	int32
	// ManualRelease when true means the session is released only by explicit user action.
	ManualRelease	bool
}
```

LifecyclePolicy configures session lifecycle: idle release, max runtime, and optional manual
release.

### Related Functions

### NewLifecyclePolicy

```go
func NewLifecyclePolicy() *LifecyclePolicy
```

NewLifecyclePolicy returns defaults: 5 minutes idle release, 30 minutes max runtime, manual release
off.

### NewLifecyclePolicyManualRelease

```go
func NewLifecyclePolicyManualRelease() *LifecyclePolicy
```

NewLifecyclePolicyManualRelease returns manual release mode (idle and max runtime are unused).

### NewLifecyclePolicyWithValues

```go
func NewLifecyclePolicyWithValues(idleReleaseTimeout, maxRuntime int32, manualRelease bool) (*LifecyclePolicy, error)
```

NewLifecyclePolicyWithValues validates and returns a LifecyclePolicy. When manualRelease is true,
idleReleaseTimeout and maxRuntime must be zero. When manualRelease is false, idleReleaseTimeout and
maxRuntime must be positive.

## Functions

### NewLifecyclePolicy

```go
func NewLifecyclePolicy() *LifecyclePolicy
```

NewLifecyclePolicy returns defaults: 5 minutes idle release, 30 minutes max runtime, manual release
off.

### NewLifecyclePolicyWithValues

```go
func NewLifecyclePolicyWithValues(idleReleaseTimeout, maxRuntime int32, manualRelease bool) (*LifecyclePolicy, error)
```

NewLifecyclePolicyWithValues validates and returns a LifecyclePolicy. When manualRelease is true,
idleReleaseTimeout and maxRuntime must be zero. When manualRelease is false, idleReleaseTimeout and
maxRuntime must be positive.

---

*Documentation generated automatically from Go source code.*
