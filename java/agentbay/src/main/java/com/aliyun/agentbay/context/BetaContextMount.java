package com.aliyun.agentbay.context;

import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.LinkedHashMap;
import java.util.Map;

/**
 * [Beta] Defines the context mount configuration for direct-mount persistence.
 *
 * <p>Unlike ContextSync which requires explicit synchronization, BetaContextMount provides
 * write-through persistence where data is persisted immediately without manual sync calls.</p>
 *
 * <p><b>IMPORTANT:</b> BetaContextMount requires {@code imageId="aio-ubuntu-2404"} on
 * the session. Other images do not provide a real OSS-backed mount — writes are not
 * persisted to the shared context store and are invisible to other sessions even with
 * the same contextId and mount path.</p>
 *
 * <p>Use {@link #withSourcePath(String)} to mount only a subdirectory of the context.
 * The subdirectory's contents are projected to the mount root.</p>
 */
public class BetaContextMount {

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
    private String sourcePath;

    public BetaContextMount() {
        this.accessMode = AccessMode.READ_WRITE;
        this.strategy = Strategy.STANDARD;
        this.sourcePath = "";
    }

    public BetaContextMount(String contextId, String path) {
        this.contextId = contextId;
        this.path = path;
        this.accessMode = AccessMode.READ_WRITE;
        this.strategy = Strategy.STANDARD;
        this.sourcePath = "";
    }

    public BetaContextMount(String contextId, String path, AccessMode accessMode, Strategy strategy) {
        this.contextId = contextId;
        this.path = path;
        this.accessMode = accessMode != null ? accessMode : AccessMode.READ_WRITE;
        this.strategy = strategy != null ? strategy : Strategy.STANDARD;
        this.sourcePath = "";
    }

    public static BetaContextMount create(String contextId, String path) {
        return new BetaContextMount(contextId, path);
    }

    public BetaContextMount withAccessMode(AccessMode accessMode) {
        this.accessMode = accessMode;
        return this;
    }

    public BetaContextMount withStrategy(Strategy strategy) {
        this.strategy = strategy;
        return this;
    }

    /**
     * Set the subpath within the context to mount. Empty string (default) mounts
     * the entire context. The selected subdirectory's contents are projected to
     * the mount root.
     */
    public BetaContextMount withSourcePath(String sourcePath) {
        this.sourcePath = sourcePath != null ? sourcePath : "";
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

    public String getSourcePath() {
        return sourcePath;
    }

    public void setSourcePath(String sourcePath) {
        this.sourcePath = sourcePath != null ? sourcePath : "";
    }

    /**
     * Returns the mount config as a JSON string for the protocol layer.
     */
    public String toMountConfigJSON() {
        try {
            Map<String, String> config = new LinkedHashMap<>();
            config.put("accessMode", accessMode.getValue());
            config.put("storageMode", strategy.getValue());
            config.put("sourcePath", sourcePath);
            return objectMapper.writeValueAsString(config);
        } catch (Exception e) {
            return "{\"accessMode\":\"" + accessMode.getValue() + "\",\"storageMode\":\"" + strategy.getValue() + "\",\"sourcePath\":\"" + sourcePath + "\"}";
        }
    }
}
