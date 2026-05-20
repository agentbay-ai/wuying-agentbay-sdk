package com.aliyun.agentbay;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Configuration class for AgentBay SDK.
 *
 * <p>Endpoint is no longer a user input — it is derived from {@code regionId} by
 * direct pattern substitution ({@code agentbay.{regionId}.aliyuncs.com}, or
 * {@code agentbay-pre.{regionId}.aliyuncs.com} when the regionId has a
 * {@code pre-} prefix). The {@code endpoint} field is kept on the class as the
 * resolved output (used by AgentBay to initialize the OpenAPI client), but
 * cannot be set directly by callers.
 */
public class Config {
    private static final Logger logger = LoggerFactory.getLogger(Config.class);

    // Browser data path constant
    public static final String BROWSER_DATA_PATH = "/tmp/agentbay_browser";

    // Browser fingerprint persistent path constant
    public static final String BROWSER_FINGERPRINT_PERSIST_PATH = "/tmp/browser_fingerprint";

    private static final String DEFAULT_REGION = "cn-hangzhou";
    private static final String PRE_PREFIX = "pre-";
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
     * Resolve and apply a regionId, deriving and storing the endpoint by direct
     * pattern substitution. Empty/null falls back to {@link #DEFAULT_REGION}.
     * No whitelist validation — any non-empty regionId is accepted so newly
     * onboarded regions work without an SDK upgrade.
     */
    private void applyRegion(String regionId) {
        String id = (regionId == null || regionId.isEmpty()) ? DEFAULT_REGION : regionId;
        if (id.startsWith(PRE_PREFIX)) {
            String actual = id.substring(PRE_PREFIX.length());
            this.regionId = actual;
            this.endpoint = "agentbay-pre." + actual + ".aliyuncs.com";
            return;
        }
        this.regionId = id;
        this.endpoint = "agentbay." + id + ".aliyuncs.com";
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
