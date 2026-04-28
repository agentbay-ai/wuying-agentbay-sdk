package agentbay

import (
	"fmt"
)

// LifecyclePolicy configures session lifecycle: idle release, max runtime, and optional manual release.
type LifecyclePolicy struct {
	// IdleReleaseTimeout is the idle release timeout in minutes.
	IdleReleaseTimeout int32
	// MaxRuntime is the maximum session runtime in minutes.
	MaxRuntime int32
	// ManualRelease when true means the session is released only by explicit user action.
	ManualRelease bool
}

// NewLifecyclePolicy returns defaults: 5 minutes idle release, 30 minutes max runtime, manual release off.
func NewLifecyclePolicy() *LifecyclePolicy {
	return &LifecyclePolicy{
		IdleReleaseTimeout: 5,
		MaxRuntime:         30,
		ManualRelease:      false,
	}
}

// NewLifecyclePolicyManualRelease returns manual release mode (idle and max runtime are unused).
func NewLifecyclePolicyManualRelease() *LifecyclePolicy {
	return &LifecyclePolicy{
		IdleReleaseTimeout: 0,
		MaxRuntime:         0,
		ManualRelease:      true,
	}
}

// NewLifecyclePolicyWithValues validates and returns a LifecyclePolicy.
// When manualRelease is true, idleReleaseTimeout and maxRuntime must be zero.
// When manualRelease is false, idleReleaseTimeout and maxRuntime must be positive.
func NewLifecyclePolicyWithValues(idleReleaseTimeout, maxRuntime int32, manualRelease bool) (*LifecyclePolicy, error) {
	if manualRelease {
		if idleReleaseTimeout != 0 || maxRuntime != 0 {
			return nil, fmt.Errorf("manual release mode cannot set idle release timeout or max runtime")
		}
		return &LifecyclePolicy{
			IdleReleaseTimeout: 0,
			MaxRuntime:         0,
			ManualRelease:      true,
		}, nil
	}
	if idleReleaseTimeout <= 0 || maxRuntime <= 0 {
		return nil, fmt.Errorf("idle release timeout and max runtime must be positive integers")
	}
	return &LifecyclePolicy{
		IdleReleaseTimeout: idleReleaseTimeout,
		MaxRuntime:         maxRuntime,
		ManualRelease:      false,
	}, nil
}
