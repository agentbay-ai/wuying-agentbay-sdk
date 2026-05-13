# Lifecycle Policy API Reference

## ⏱ Related Tutorial

- [Session Lifecycle Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Learn how to control session lifecycle with idle release, max runtime, and manual release

## Overview

The LifecyclePolicy class provides fine-grained control over session lifecycle.
It supports idle release timeout, maximum runtime, and manual release options.
All time values are in minutes. When set, SDK takes full control of session lifecycle
and overrides console defaults.

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

## Best Practices

1. Use LifecyclePolicy instead of the deprecated idle_release_timeout parameter for new code
2. Set max_runtime to prevent runaway sessions from consuming resources indefinitely
3. Use manual_release=true for interactive workflows where session duration is unpredictable
4. The backend requires idle_release_timeout >= 3 minutes

## Related Resources

- [Session Params API Reference](session-params.md)
- [Session API Reference](session.md)

---

*Documentation generated automatically from Go source code.*
