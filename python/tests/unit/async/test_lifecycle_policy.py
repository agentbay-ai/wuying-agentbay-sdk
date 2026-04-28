import pytest
from agentbay._common.params.lifecycle_policy import LifecyclePolicy
from agentbay._common.params.session_params import CreateSessionParams


class TestLifecyclePolicy:
    def test_default_values(self):
        policy = LifecyclePolicy()
        assert policy.idle_release_timeout == 5
        assert policy.max_runtime == 30
        assert policy.manual_release is False

    def test_custom_values(self):
        policy = LifecyclePolicy(idle_release_timeout=10, max_runtime=120)
        assert policy.idle_release_timeout == 10
        assert policy.max_runtime == 120
        assert policy.manual_release is False

    def test_manual_release(self):
        policy = LifecyclePolicy(manual_release=True)
        assert policy.manual_release is True
        assert policy.idle_release_timeout == 0
        assert policy.max_runtime == 0

    def test_manual_release_rejects_idle_release_timeout(self):
        with pytest.raises(ValueError, match="manual_release"):
            LifecyclePolicy(manual_release=True, idle_release_timeout=10)

    def test_manual_release_rejects_max_runtime(self):
        with pytest.raises(ValueError, match="manual_release"):
            LifecyclePolicy(manual_release=True, max_runtime=60)

    def test_idle_release_timeout_must_be_positive_int(self):
        with pytest.raises(ValueError):
            LifecyclePolicy(idle_release_timeout=0)
        with pytest.raises(ValueError):
            LifecyclePolicy(idle_release_timeout=-1)
        with pytest.raises(ValueError):
            LifecyclePolicy(idle_release_timeout=1.5)

    def test_max_runtime_must_be_positive_int(self):
        with pytest.raises(ValueError):
            LifecyclePolicy(max_runtime=0)
        with pytest.raises(ValueError):
            LifecyclePolicy(max_runtime=-1)
        with pytest.raises(ValueError):
            LifecyclePolicy(max_runtime=1.5)

    def test_only_idle_release_timeout_custom(self):
        policy = LifecyclePolicy(idle_release_timeout=10)
        assert policy.idle_release_timeout == 10
        assert policy.max_runtime == 30  # default

    def test_only_max_runtime_custom(self):
        policy = LifecyclePolicy(max_runtime=60)
        assert policy.idle_release_timeout == 5  # default
        assert policy.max_runtime == 60


class TestCreateSessionParamsLifecyclePolicy:
    def test_lifecycle_policy_accepted(self):
        policy = LifecyclePolicy(idle_release_timeout=10, max_runtime=120)
        params = CreateSessionParams(lifecycle_policy=policy)
        assert params.lifecycle_policy is policy
        assert params.idle_release_timeout is None

    def test_lifecycle_policy_and_idle_release_timeout_mutually_exclusive(self):
        policy = LifecyclePolicy(max_runtime=60)
        with pytest.raises(ValueError, match="deprecated"):
            CreateSessionParams(lifecycle_policy=policy, idle_release_timeout=300)

    def test_old_idle_release_timeout_still_works(self):
        params = CreateSessionParams(idle_release_timeout=300)
        assert params.idle_release_timeout == 300
        assert params.lifecycle_policy is None
