package com.aliyun.agentbay.test;

import com.aliyun.agentbay.Config;
import org.junit.Test;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertTrue;
import static org.junit.Assert.fail;

/**
 * Unit tests for the region → endpoint mapping introduced by the multi-region refactor.
 */
public class ConfigRegionEndpointMappingTest {

    @Test
    public void testNullRegionFallsBackToDefault() {
        Config cfg = new Config((String) null);
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testEmptyRegionFallsBackToDefault() {
        Config cfg = new Config("");
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testCnHangzhouMapsToHangzhouUnit() {
        Config cfg = new Config("cn-hangzhou");
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testApSoutheast1MapsCorrectly() {
        Config cfg = new Config("ap-southeast-1");
        assertEquals("ap-southeast-1", cfg.getRegionId());
        assertEquals("agentbay.ap-southeast-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testUsEast1MapsCorrectly() {
        Config cfg = new Config("us-east-1");
        assertEquals("us-east-1", cfg.getRegionId());
        assertEquals("agentbay.us-east-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testPrePrefixStripsRegionAndUsesPreEndpoint() {
        Config cfg = new Config("pre-cn-hangzhou");
        // pre- prefix is stripped from the stored region.
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay-pre.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testInvalidRegionThrows() {
        try {
            new Config("us-west-1");
            fail("Expected IllegalArgumentException for invalid region");
        } catch (IllegalArgumentException e) {
            String msg = e.getMessage();
            assertTrue("Message should include the invalid region: " + msg, msg.contains("us-west-1"));
            assertTrue("Message should list supported regions: " + msg, msg.contains("cn-hangzhou"));
            assertTrue("Message should mention pre- prefix: " + msg, msg.contains("pre-"));
        }
    }

    @Test
    public void testInvalidPreRegionThrows() {
        try {
            new Config("pre-us-west-1");
            fail("Expected IllegalArgumentException for invalid pre- region");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("pre-us-west-1"));
        }
    }

    @Test
    public void testTwoArgConstructorAcceptsTimeout() {
        Config cfg = new Config("cn-hangzhou", 30000);
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
        assertEquals(30000, cfg.getTimeoutMs());
    }

    @Test
    public void testZeroOrNegativeTimeoutFallsBackToDefault() {
        Config cfg = new Config("cn-hangzhou", 0);
        assertEquals(60000, cfg.getTimeoutMs());

        Config cfg2 = new Config("cn-hangzhou", -1);
        assertEquals(60000, cfg2.getTimeoutMs());
    }

    @Test
    public void testSetRegionIdReDerivesEndpoint() {
        Config cfg = new Config("cn-hangzhou");
        cfg.setRegionId("us-east-1");
        assertEquals("us-east-1", cfg.getRegionId());
        assertEquals("agentbay.us-east-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testSetRegionIdRejectsInvalid() {
        Config cfg = new Config("cn-hangzhou");
        try {
            cfg.setRegionId("us-west-1");
            fail("Expected IllegalArgumentException");
        } catch (IllegalArgumentException e) {
            // region should remain unchanged on failure
            assertEquals("cn-hangzhou", cfg.getRegionId());
        }
    }
}
