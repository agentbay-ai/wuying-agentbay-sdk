package com.aliyun.agentbay.context;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Defines the context mount configuration for direct-mount persistence.
 *
 * <p>Unlike ContextSync which requires explicit synchronization, ContextMount provides
 * write-through persistence where data is persisted immediately without manual sync calls.</p>
 */
public class ContextMount {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Access mode for context mount.
     */
    public enum AccessMode {
        READ_WRITE("readWrite"),
        READ_ONLY("readOnly");

        private final String value;

        AccessMode(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    /**
     * Mount strategy for context mount.
     */
    public enum Strategy {
        STANDARD("standard"),
        PERFORMANCE("performance");

        private final String value;

        Strategy(String value) {
            this.value = value;
        }

        public String getValue() {
            return value;
        }
    }

    private String contextId;
    private String path;
    private AccessMode accessMode;
    private Strategy strategy;

    public ContextMount() {
        this.accessMode = AccessMode.READ_WRITE;
        this.strategy = Strategy.STANDARD;
    }

    public ContextMount(String contextId, String path) {
        this.contextId = contextId;
        this.path = path;
        this.accessMode = AccessMode.READ_WRITE;
        this.strategy = Strategy.STANDARD;
    }

    public ContextMount(String contextId, String path, AccessMode accessMode, Strategy strategy) {
        this.contextId = contextId;
        this.path = path;
        this.accessMode = accessMode != null ? accessMode : AccessMode.READ_WRITE;
        this.strategy = strategy != null ? strategy : Strategy.STANDARD;
    }

    public static ContextMount create(String contextId, String path) {
        return new ContextMount(contextId, path);
    }

    public ContextMount withAccessMode(AccessMode accessMode) {
        this.accessMode = accessMode;
        return this;
    }

    public ContextMount withStrategy(Strategy strategy) {
        this.strategy = strategy;
        return this;
    }

    public String getContextId() {
        return contextId;
    }

    public void setContextId(String contextId) {
        this.contextId = contextId;
    }

    public String getPath() {
        return path;
    }

    public void setPath(String path) {
        this.path = path;
    }

    public AccessMode getAccessMode() {
        return accessMode;
    }

    public void setAccessMode(AccessMode accessMode) {
        this.accessMode = accessMode;
    }

    public Strategy getStrategy() {
        return strategy;
    }

    public void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }

    /**
     * Returns the mount config as a JSON string for the protocol layer.
     */
    public String toMountConfigJSON() {
        try {
            Map<String, String> config = new LinkedHashMap<>();
            config.put("accessMode", accessMode.getValue());
            config.put("storageMode", strategy.getValue());
            return objectMapper.writeValueAsString(config);
        } catch (Exception e) {
            return "{\"accessMode\":\"" + accessMode.getValue() + "\",\"storageMode\":\"" + strategy.getValue() + "\"}";
        }
    }
}
