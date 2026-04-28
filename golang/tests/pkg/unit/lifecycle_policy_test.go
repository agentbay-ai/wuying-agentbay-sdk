package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func TestLifecyclePolicyDefaults(t *testing.T) {
	lp := agentbay.NewLifecyclePolicy()
	if lp.IdleReleaseTimeout != 5 {
		t.Errorf("expected IdleReleaseTimeout=5, got %d", lp.IdleReleaseTimeout)
	}
	if lp.MaxRuntime != 30 {
		t.Errorf("expected MaxRuntime=30, got %d", lp.MaxRuntime)
	}
	if lp.ManualRelease {
		t.Error("expected ManualRelease=false")
	}
}

func TestLifecyclePolicyManualRelease(t *testing.T) {
	lp := agentbay.NewLifecyclePolicyManualRelease()
	if !lp.ManualRelease {
		t.Error("expected ManualRelease=true")
	}
	if lp.IdleReleaseTimeout != 0 {
		t.Errorf("expected IdleReleaseTimeout=0, got %d", lp.IdleReleaseTimeout)
	}
	if lp.MaxRuntime != 0 {
		t.Errorf("expected MaxRuntime=0, got %d", lp.MaxRuntime)
	}
}

func TestLifecyclePolicyCustomValues(t *testing.T) {
	lp, err := agentbay.NewLifecyclePolicyWithValues(10, 120, false)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if lp.IdleReleaseTimeout != 10 {
		t.Errorf("expected 10, got %d", lp.IdleReleaseTimeout)
	}
	if lp.MaxRuntime != 120 {
		t.Errorf("expected 120, got %d", lp.MaxRuntime)
	}
}

func TestLifecyclePolicyValidation(t *testing.T) {
	_, err := agentbay.NewLifecyclePolicyWithValues(0, 30, false)
	if err == nil {
		t.Error("expected error for idle=0")
	}
	_, err = agentbay.NewLifecyclePolicyWithValues(5, -1, false)
	if err == nil {
		t.Error("expected error for max=-1")
	}
	_, err = agentbay.NewLifecyclePolicyWithValues(10, 30, true)
	if err == nil {
		t.Error("expected error for manual_release with timeout params")
	}
}

func TestCreateSessionParamsWithLifecyclePolicy(t *testing.T) {
	lp := agentbay.NewLifecyclePolicy()
	params, err := agentbay.NewCreateSessionParams().WithLifecyclePolicy(lp)
	if err != nil {
		t.Fatalf("unexpected error: %v", err)
	}
	if params.LifecyclePolicy == nil {
		t.Error("expected LifecyclePolicy to be set")
	}
	if params.LifecyclePolicy.IdleReleaseTimeout != 5 {
		t.Errorf("expected 5, got %d", params.LifecyclePolicy.IdleReleaseTimeout)
	}
}
