package com.aliyun.agentbay.test;

import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.LifecyclePolicy;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class LifecyclePolicyTest {

    @Test
    void testDefaults() {
        LifecyclePolicy lp = new LifecyclePolicy();
        assertEquals(5, lp.getIdleReleaseTimeout());
        assertEquals(30, lp.getMaxRuntime());
        assertFalse(lp.isManualRelease());
    }

    @Test
    void testCustomValues() {
        LifecyclePolicy lp = new LifecyclePolicy(10, 120);
        assertEquals(10, lp.getIdleReleaseTimeout());
        assertEquals(120, lp.getMaxRuntime());
        assertFalse(lp.isManualRelease());
    }

    @Test
    void testManualRelease() {
        LifecyclePolicy lp = LifecyclePolicy.manualRelease();
        assertTrue(lp.isManualRelease());
        assertEquals(0, lp.getIdleReleaseTimeout());
        assertEquals(0, lp.getMaxRuntime());
    }

    @Test
    void testRejectsInvalidIdle() {
        assertThrows(IllegalArgumentException.class, () -> new LifecyclePolicy(0, 30));
        assertThrows(IllegalArgumentException.class, () -> new LifecyclePolicy(-1, 30));
    }

    @Test
    void testRejectsInvalidMaxRuntime() {
        assertThrows(IllegalArgumentException.class, () -> new LifecyclePolicy(5, 0));
        assertThrows(IllegalArgumentException.class, () -> new LifecyclePolicy(5, -1));
    }

    @Test
    void testManualReleaseRejectsTimeoutParams() {
        assertThrows(IllegalArgumentException.class, () -> new LifecyclePolicy(10, 30, true));
    }

    @Test
    void testCreateSessionParamsLifecyclePolicy() {
        LifecyclePolicy lp = new LifecyclePolicy(10, 120);
        CreateSessionParams params = new CreateSessionParams();
        params.setLifecyclePolicy(lp);
        assertNotNull(params.getLifecyclePolicy());
        assertEquals(10, params.getLifecyclePolicy().getIdleReleaseTimeout());
    }

    @Test
    @SuppressWarnings("deprecation")
    void testCreateSessionParamsRejectsLifecyclePolicyWithIdleReleaseTimeout() {
        CreateSessionParams params = new CreateSessionParams();
        params.setIdleReleaseTimeout(300);
        LifecyclePolicy lp = new LifecyclePolicy(10, 120);
        assertThrows(IllegalArgumentException.class, () -> params.setLifecyclePolicy(lp));
    }

    @Test
    @SuppressWarnings("deprecation")
    void testCreateSessionParamsRejectsIdleReleaseTimeoutWithLifecyclePolicy() {
        CreateSessionParams params = new CreateSessionParams();
        params.setLifecyclePolicy(new LifecyclePolicy(10, 120));
        assertThrows(IllegalArgumentException.class, () -> params.setIdleReleaseTimeout(300));
    }
}
