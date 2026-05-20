package com.aliyun.agentbay.test;

import com.aliyun.agentbay.Config;
import org.junit.Test;

import static org.junit.Assert.assertEquals;

/**
 * Unit tests for the region → endpoint mapping introduced by the multi-region refactor.
 *
 * <p>Endpoint is derived from {@code regionId} by direct pattern substitution; there
 * is no whitelist, so any non-empty regionId is accepted as-is.
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
    public void testUnknownRegionIsAcceptedAsPattern() {
        // No whitelist — any non-empty region composes a pattern-based endpoint.
        Config cfg = new Config("us-west-1");
        assertEquals("us-west-1", cfg.getRegionId());
        assertEquals("agentbay.us-west-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testPrePrefixOnUnknownRegionAlsoComposes() {
        Config cfg = new Config("pre-us-west-1");
        assertEquals("us-west-1", cfg.getRegionId());
        assertEquals("agentbay-pre.us-west-1.aliyuncs.com", cfg.getEndpoint());
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
}
