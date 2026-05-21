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

    /**
     * Known production regions. Unknown entries are NOT rejected — they fall
     * through to the default "agentbay.{region}.aliyuncs.com" pattern with a
     * warning logged.
     */
    private static final List<String> KNOWN_REGIONS = Collections.unmodifiableList(
        Arrays.asList("cn-hangzhou", "ap-southeast-1", "us-east-1"));

    /**
     * Hardcoded mapping for pre-release regions (after stripping the "pre-" prefix).
     * Pre-release hostnames don't follow a single pattern: cn-hangzhou uses
     * "agentbay-pre.*" while ap-southeast-1 uses "wuyingai-pre.*". Unknown entries
     * fall back to "agentbay-pre.{actual}.aliyuncs.com" with a warning logged.
     */
    private static final Map<String, String> PRE_REGION_ENDPOINT_MAP;

    static {
        Map<String, String> m = new LinkedHashMap<>();
        m.put("cn-hangzhou", "agentbay-pre.cn-hangzhou.aliyuncs.com");
        m.put("ap-southeast-1", "wuyingai-pre.ap-southeast-1.aliyuncs.com");
        PRE_REGION_ENDPOINT_MAP = Collections.unmodifiableMap(m);
    }

    private String regionId;
    private String endpoint;
    private int timeoutMs;

    /**
     * Construct from regionId and timeoutMs. Endpoint is derived from regionId.
     * Unknown regions are accepted with a warning logged (no exception is thrown),
     * so newly onboarded regions work without an SDK upgrade.
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
     * Backwards-compatibility constructor. The {@code endpoint} argument is
     * ignored (a deprecation warning is logged) — endpoint is derived from
     * {@code regionId}. Use {@link #Config(String, int)} instead.
     *
     * @deprecated since 0.21.0. The {@code endpoint} parameter is ignored.
     *     Will be removed in a future major version.
     */
    @Deprecated
    public Config(String regionId, String endpoint, int timeoutMs) {
        applyRegion(regionId);
        this.timeoutMs = timeoutMs > 0 ? timeoutMs : DEFAULT_TIMEOUT_MS;
        if (endpoint != null && !endpoint.isEmpty()) {
            logger.warn(
                "[DeprecationWarning] Config(regionId, endpoint=\"{}\", timeoutMs) is deprecated; "
                + "the endpoint argument is ignored and endpoint is derived from regionId. "
                + "Use Config(regionId, timeoutMs) instead.",
                endpoint);
        }
    }

    /**
     * Resolve and apply a regionId, deriving and storing the endpoint. Empty/null
     * falls back to {@link #DEFAULT_REGION}.
     *
     * <p>For "pre-" regions: known entries use the hardcoded mapping; unknown
     * entries log a warning and fall back to {@code agentbay-pre.{actual}.aliyuncs.com}.
     *
     * <p>For non-pre regions: composed by direct pattern substitution. No
     * whitelist validation — any non-empty regionId is accepted so newly
     * onboarded regions work without an SDK upgrade.
     */
    private void applyRegion(String regionId) {
        String id = (regionId == null || regionId.isEmpty()) ? DEFAULT_REGION : regionId;
        if (id.startsWith(PRE_PREFIX)) {
            String actual = id.substring(PRE_PREFIX.length());
            this.regionId = actual;
            String mapped = PRE_REGION_ENDPOINT_MAP.get(actual);
            if (mapped != null) {
                this.endpoint = mapped;
            } else {
                logger.warn(
                    "Unknown pre-release region 'pre-{}'. Falling back to "
                    + "'agentbay-pre.{}.aliyuncs.com'; the request may fail at DNS "
                    + "resolution if the host does not exist. Known pre regions: {}.",
                    actual, actual, PRE_REGION_ENDPOINT_MAP.keySet());
                this.endpoint = "agentbay-pre." + actual + ".aliyuncs.com";
            }
            return;
        }
        if (!KNOWN_REGIONS.contains(id)) {
            logger.warn(
                "Unknown region '{}'. Falling back to 'agentbay.{}.aliyuncs.com'; "
                + "the request may fail at DNS resolution if the host does not exist. "
                + "Known regions: {}.",
                id, id, KNOWN_REGIONS);
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
     * Set a new regionId. Endpoint is re-derived from it. Unknown regions
     * are accepted with a warning logged.
     */
    public void setRegionId(String regionId) {
        applyRegion(regionId);
    }

    public String getEndpoint() {
        return endpoint;
    }

    /**
     * Backwards-compatibility setter. The argument is ignored (a deprecation
     * warning is logged) — endpoint is derived from {@code regionId}.
     *
     * @deprecated since 0.21.0. The endpoint cannot be set directly anymore.
     *     Use {@link #setRegionId(String)} instead. Will be removed in a
     *     future major version.
     */
    @Deprecated
    public void setEndpoint(String endpoint) {
        if (endpoint != null && !endpoint.isEmpty()) {
            logger.warn(
                "[DeprecationWarning] Config.setEndpoint(\"{}\") is deprecated and ignored; "
                + "endpoint is derived from regionId. Use setRegionId(String) instead.",
                endpoint);
        }
    }

    public int getTimeoutMs() {
        return timeoutMs;
    }

    public void setTimeoutMs(int timeoutMs) {
        this.timeoutMs = timeoutMs;
    }
}
