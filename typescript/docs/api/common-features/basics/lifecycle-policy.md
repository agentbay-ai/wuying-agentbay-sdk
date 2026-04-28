# Class: LifecyclePolicy

## ⏱ Related Tutorial

- [Session Lifecycle Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Learn how to control session lifecycle with idle release, max runtime, and manual release

## Overview

The LifecyclePolicy class provides fine-grained control over session lifecycle.
It supports idle release timeout, maximum runtime, and manual release options.
All time values are in minutes. When set, SDK takes full control of session lifecycle
and overrides console defaults.

Lifecycle policy for session management.

Controls how and when a session is automatically released.
When used, SDK takes full control of lifecycle — console defaults are overridden.
All time values are in MINUTES.

Three control dimensions:
- **idleReleaseTimeout**: Minutes of inactivity before auto-release (default: 5)
- **maxRuntime**: Absolute maximum session duration from creation (default: 30)
- **manualRelease**: Disable all auto-release; session only ends via `delete()`

## Table of contents


### Properties

- [idleReleaseTimeout](#idlereleasetimeout)
- [manualRelease](#manualrelease)
- [maxRuntime](#maxruntime)

## Properties

### idleReleaseTimeout

• `Readonly` **idleReleaseTimeout**: `number`

Minutes of inactivity before auto-release (default: 5).

___

### manualRelease

• `Readonly` **manualRelease**: `boolean`

When true, disables all auto-release; session only ends via delete().

___

### maxRuntime

• `Readonly` **maxRuntime**: `number`

Maximum session runtime in minutes from creation (default: 30).

## Best Practices

1. Use LifecyclePolicy instead of the deprecated idle_release_timeout parameter for new code
2. Set max_runtime to prevent runaway sessions from consuming resources indefinitely
3. Use manual_release=true for interactive workflows where session duration is unpredictable
4. The backend requires idle_release_timeout >= 3 minutes


## Related Resources

- [Session Params API Reference](session-params.md)
- [Session API Reference](session.md)

