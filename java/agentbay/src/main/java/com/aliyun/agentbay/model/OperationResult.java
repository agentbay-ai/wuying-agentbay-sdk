package com.aliyun.agentbay.model;

/**
 * Operation result class similar to Python's OperationResult.
 * Contains success status, data, and error message for MCP tool operations.
 */
public class OperationResult {
    private String requestId;
    private boolean success;
    private String data;
    private String errorMessage;
    private String code;
    private String message;
    private Integer httpStatusCode;

    public OperationResult() {
    }

    public OperationResult(String requestId, boolean success, String data, String errorMessage) {
        this.requestId = requestId;
        this.success = success;
        this.data = data;
        this.errorMessage = errorMessage;
    }

    public OperationResult(String requestId, boolean success, String data, String code, String message, String errorMessage, Integer httpStatusCode) {
        this.requestId = requestId;
        this.success = success;
        this.data = data;
        this.code = code;
        this.message = message;
        this.errorMessage = errorMessage;
        this.httpStatusCode = httpStatusCode;
    }

    public String getRequestId() {
        return requestId;
    }

    public void setRequestId(String requestId) {
        this.requestId = requestId;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getData() {
        return data;
    }

    public void setData(String data) {
        this.data = data;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public Integer getHttpStatusCode() {
        return httpStatusCode;
    }

    public void setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
    }

    @Override
    public String toString() {
        return "OperationResult{" +
                "requestId='" + requestId + '\'' +
                ", success=" + success +
                ", data='" + data + '\'' +
                ", errorMessage='" + errorMessage + '\'' +
                ", code='" + code + '\'' +
                ", httpStatusCode=" + httpStatusCode +
                '}';
    }
}