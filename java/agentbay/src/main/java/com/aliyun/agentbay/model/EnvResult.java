package com.aliyun.agentbay.model;

import java.util.HashMap;
import java.util.Map;

/**
 * Result of environment variable get operations.
 */
public class EnvResult extends ApiResponse {
    private boolean success;
    private Map<String, String> envs;
    private String errorMessage;

    public EnvResult() {
        this("", false, new HashMap<>(), "");
    }

    public EnvResult(String requestId, boolean success, Map<String, String> envs, String errorMessage) {
        super(requestId);
        this.success = success;
        this.envs = envs != null ? envs : new HashMap<>();
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public Map<String, String> getEnvs() {
        return envs;
    }

    public void setEnvs(Map<String, String> envs) {
        this.envs = envs;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
