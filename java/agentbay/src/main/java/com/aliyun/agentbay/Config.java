package com.aliyun.agentbay;

import java.util.Arrays;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Configuration class for AgentBay SDK.
 *
 * <p>Endpoint is no longer a user input — it is derived from {@code regionId} via
 * {@link #REGION_ENDPOINT_MAP}. The {@code endpoint} field is kept on the class as
 * the resolved output (used by AgentBay to initialize the OpenAPI client), but
 * cannot be set directly by callers.
 */
public class Config {
    private static final Logger logger = LoggerFactory.getLogger(Config.class);

    // Browser data path constant
    public static final String BROWSER_DATA_PATH = "/tmp/agentbay_browser";

    // Browser fingerprint persistent path constant
    public static final String BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

    /**
     * Region → unit-service endpoint mapping. Pre-release endpoints are obtained by
     * prefixing the region with "pre-" (e.g. "pre-cn-hangzhou" →
     * agentbay-pre.cn-hangzhou.aliyuncs.com).
     */
    private static final Map<String, String> REGION_ENDPOINT_MAP;

    static {
        Map<String, String> m = new LinkedHashMap<>();
        m.put("cn-hangzhou", "agentbay.cn-hangzhou.aliyuncs.com");
        m.put("ap-southeast-1", "agentbay.ap-southeast-1.aliyuncs.com");
        m.put("us-east-1", "agentbay.us-east-1.aliyuncs.com");
        REGION_ENDPOINT_MAP = Collections.unmodifiableMap(m);
    }

    private static final String DEFAULT_REGION = "cn-hangzhou";
    private static final String PRE_PREFIX = "pre-";
    private static final String DEFAULT_ENDPOINT = REGION_ENDPOINT_MAP.get(DEFAULT_REGION);
    private static final int DEFAULT_TIMEOUT_MS = 60000;

    private String regionId;
    private String endpoint;
    private int timeoutMs;

    /**
     * Construct from regionId and timeoutMs. Endpoint is derived from regionId.
     * Throws {@link IllegalArgumentException} if regionId is not in the supported map.
     */
    public Config(String regionId, int timeoutMs) {
        applyRegion(regionId);
        this.timeoutMs = timeoutMs > 0 ? timeoutMs : DEFAULT_TIMEOUT_MS;
    }

    /**
     * Construct from regionId with the default timeout.
     */
    public Config(String regionId) {
        applyRegion(regionId);
        this.timeoutMs = DEFAULT_TIMEOUT_MS;
    }

    /**
     * No-arg constructor: load configuration from environment variables (with .env fallback).
     */
    public Config() {
        applyRegion(loadRegionId());
        this.timeoutMs = loadTimeoutMs();
    }

    /**
     * Resolve and apply a regionId, deriving and storing the endpoint.
     * Empty/null falls back to {@link #DEFAULT_REGION}.
     */
    private void applyRegion(String regionId) {
        String id = (regionId == null || regionId.isEmpty()) ? DEFAULT_REGION : regionId;
        if (id.startsWith(PRE_PREFIX)) {
            String actual = id.substring(PRE_PREFIX.length());
            if (!REGION_ENDPOINT_MAP.containsKey(actual)) {
                throw new IllegalArgumentException(invalidRegionMessage(id));
            }
            this.regionId = actual;
            this.endpoint = "agentbay-pre." + actual + ".aliyuncs.com";
            return;
        }
        if (!REGION_ENDPOINT_MAP.containsKey(id)) {
            throw new IllegalArgumentException(invalidRegionMessage(id));
        }
        this.regionId = id;
        this.endpoint = REGION_ENDPOINT_MAP.get(id);
    }

    private static String invalidRegionMessage(String regionId) {
        List<String> canonical = Arrays.asList("cn-hangzhou", "ap-southeast-1", "us-east-1");
        StringBuilder supported = new StringBuilder();
        for (int i = 0; i < canonical.size(); i++) {
            if (i > 0) supported.append(", ");
            supported.append(canonical.get(i));
        }
        return "Invalid region_id '" + regionId + "'. Supported regions: " + supported + ". "
                + "For pre-release, use 'pre-' prefix (e.g., 'pre-cn-hangzhou').";
    }

    private String loadRegionId() {
        String envValue = System.getenv("AGENTBAY_REGION_ID");
        return (envValue != null && !envValue.trim().isEmpty()) ? envValue : null;
    }

    private int loadTimeoutMs() {
        String envValue = System.getenv("AGENTBAY_TIMEOUT_MS");
        if (envValue != null && !envValue.trim().isEmpty()) {
            try {
                return Integer.parseInt(envValue);
            } catch (NumberFormatException e) {
                logger.warn("Invalid AGENTBAY_TIMEOUT_MS value: {}, using default", envValue);
            }
        }
        return DEFAULT_TIMEOUT_MS;
    }

    public String getRegionId() {
        return regionId;
    }

    /**
     * Set a new regionId. Endpoint is re-derived from it. Throws if invalid.
     */
    public void setRegionId(String regionId) {
        applyRegion(regionId);
    }

    public String getEndpoint() {
        return endpoint;
    }

    public int getTimeoutMs() {
        return timeoutMs;
    }

    public void setTimeoutMs(int timeoutMs) {
        this.timeoutMs = timeoutMs;
    }
}
