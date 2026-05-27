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
    public void testPreCnHangzhouUsesHardcodedMapping() {
        Config cfg = new Config("pre-cn-hangzhou");
        // pre- prefix is stripped from the stored region.
        assertEquals("cn-hangzhou", cfg.getRegionId());
        assertEquals("agentbay-pre.cn-hangzhou.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testPreApSoutheast1UsesWuyingaiPreHost() {
        // ap-southeast-1 uses the "wuyingai-pre.*" convention (different from
        // cn-hangzhou's "agentbay-pre.*"), so it must come from the hardcoded map.
        Config cfg = new Config("pre-ap-southeast-1");
        assertEquals("ap-southeast-1", cfg.getRegionId());
        assertEquals("wuyingai-pre.ap-southeast-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testUnknownRegionIsAcceptedWithWarning() {
        // Soft whitelist — unknown regions emit a logger.warn (not asserted
        // here) and still compose the pattern-based endpoint. No validation
        // error: newly onboarded regions work without an SDK upgrade.
        Config cfg = new Config("us-west-1");
        assertEquals("us-west-1", cfg.getRegionId());
        assertEquals("agentbay.us-west-1.aliyuncs.com", cfg.getEndpoint());
    }

    @Test
    public void testUnknownPreRegionFallsBackToDefaultPattern() {
        // Unknown pre regions log a warning and fall back to the default
        // agentbay-pre.{actual}.aliyuncs.com pattern.
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

    @Test
    @SuppressWarnings("deprecation")
    public void testDeprecatedConstructorRegionIdWinsOverEndpoint() {
        // When both regionId and endpoint are passed, regionId wins and
        // endpoint is ignored (a deprecation warning is logged).
        Config cfg = new Config("ap-southeast-1", "should-be-ignored.example.com", 30000);
        assertEquals("ap-southeast-1", cfg.getRegionId());
        assertEquals("agentbay.ap-southeast-1.aliyuncs.com", cfg.getEndpoint());
        assertEquals(30000, cfg.getTimeoutMs());
    }

    @Test
    @SuppressWarnings("deprecation")
    public void testDeprecatedConstructorUsesEndpointWhenRegionIsNull() {
        // Backwards compat fallback: when regionId is null/empty, the
        // user-supplied endpoint is honored as-is (with a deprecation warning).
        Config cfg = new Config(null, "fallback.example.com", 30000);
        assertEquals("fallback.example.com", cfg.getEndpoint());
        assertEquals(30000, cfg.getTimeoutMs());
    }

    @Test
    @SuppressWarnings("deprecation")
    public void testDeprecatedSetEndpointAppliesValue() {
        // setEndpoint is deprecated but still applies the value — callers who
        // relied on the old API keep working until the next major version.
        Config cfg = new Config("cn-hangzhou");
        cfg.setEndpoint("custom.example.com");
        assertEquals("custom.example.com", cfg.getEndpoint());
    }
}
