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
 * <p>The preferred input is {@code regionId}; the SDK derives the endpoint from
 * it via direct pattern substitution ({@code agentbay.{regionId}.aliyuncs.com},
 * or {@code agentbay-pre.{regionId}.aliyuncs.com} when the regionId has a
 * {@code pre-} prefix). {@code endpoint} is retained as a deprecated fallback:
 * when {@code regionId} is not set the user-supplied {@code endpoint} is used
 * as-is. When both are set, {@code regionId} wins and {@code endpoint} is
 * ignored. Either form emits a deprecation warning.
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
     *
     * <p>Reads {@code AGENTBAY_REGION_ID} (preferred). If unset, falls back to
     * the deprecated {@code AGENTBAY_ENDPOINT} env var (a warning is logged).
     * If neither is set, the default region applies.
     */
    public Config() {
        String envRegion = loadRegionId();
        if (envRegion != null) {
            applyRegion(envRegion);
        } else {
            String envEndpoint = loadEnvEndpoint();
            if (envEndpoint != null) {
                logger.warn(
                    "[DeprecationWarning] AGENTBAY_ENDPOINT=\"{}\" is deprecated; "
                    + "set AGENTBAY_REGION_ID instead. The value is used as a "
                    + "fallback and will be removed in a future major version.",
                    envEndpoint);
                this.regionId = DEFAULT_REGION;
                this.endpoint = envEndpoint;
            } else {
                applyRegion(null);
            }
        }
        this.timeoutMs = loadTimeoutMs();
    }

    /**
     * Backwards-compatibility constructor. The {@code endpoint} argument is
     * honored only when {@code regionId} is null/empty (a deprecation warning
     * is logged either way). When both are set, {@code regionId} wins and
     * {@code endpoint} is ignored. Use {@link #Config(String, int)} instead.
     *
     * @deprecated since 0.22.0. The {@code endpoint} parameter is a fallback only.
     *     Will be removed in a future major version.
     */
    @Deprecated
    public Config(String regionId, String endpoint, int timeoutMs) {
        boolean hasRegion = regionId != null && !regionId.isEmpty();
        boolean hasEndpoint = endpoint != null && !endpoint.isEmpty();
        if (hasRegion) {
            applyRegion(regionId);
            if (hasEndpoint) {
                logger.warn(
                    "[DeprecationWarning] Config(regionId=\"{}\", endpoint=\"{}\", "
                    + "timeoutMs) ignores the endpoint argument because regionId "
                    + "is also set. Use Config(regionId, timeoutMs) instead.",
                    regionId, endpoint);
            }
        } else if (hasEndpoint) {
            logger.warn(
                "[DeprecationWarning] Config(regionId=null, endpoint=\"{}\", "
                + "timeoutMs) is deprecated; pass regionId instead. The endpoint "
                + "is used as a fallback and will be removed in a future major version.",
                endpoint);
            this.regionId = DEFAULT_REGION;
            this.endpoint = endpoint;
        } else {
            applyRegion(null);
        }
        this.timeoutMs = timeoutMs > 0 ? timeoutMs : DEFAULT_TIMEOUT_MS;
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

    private String loadEnvEndpoint() {
        String envValue = System.getenv("AGENTBAY_ENDPOINT");
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

    /**
     * Backwards-compatibility setter. Sets the endpoint directly, overriding
     * any value previously derived from {@code regionId}. A deprecation
     * warning is always logged.
     *
     * @deprecated since 0.22.0. Use {@link #setRegionId(String)} instead so
     *     the endpoint stays in sync with the region. Will be removed in a
     *     future major version.
     */
    @Deprecated
    public void setEndpoint(String endpoint) {
        if (endpoint != null && !endpoint.isEmpty()) {
            logger.warn(
                "[DeprecationWarning] Config.setEndpoint(\"{}\") is deprecated; "
                + "use setRegionId(String) instead. The value is applied as-is "
                + "and will be removed in a future major version.",
                endpoint);
            this.endpoint = endpoint;
        }
    }

    public int getTimeoutMs() {
        return timeoutMs;
    }

    public void setTimeoutMs(int timeoutMs) {
        this.timeoutMs = timeoutMs;
    }
}
