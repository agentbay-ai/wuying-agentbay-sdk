package com.aliyun.agentbay.context;

import com.aliyun.agentbay.model.ApiResponse;

import java.util.ArrayList;
import java.util.List;

/**
 * Result of file listing operation.
 */
public class ContextFileListResult extends ApiResponse {
    private boolean success;
    private List<FileInfo> entries;
    private Integer count;
    private String nextToken;
    private String errorMessage;

    public ContextFileListResult() {
        super();
        this.entries = new ArrayList<>();
    }

    public ContextFileListResult(String requestId, boolean success, List<FileInfo> entries, Integer count, String errorMessage) {
        this(requestId, success, entries, count, null, errorMessage);
    }

    public ContextFileListResult(String requestId, boolean success, List<FileInfo> entries, Integer count,
        String nextToken, String errorMessage) {
        super(requestId);
        this.success = success;
        this.entries = entries != null ? entries : new ArrayList<>();
        this.count = count;
        this.nextToken = nextToken;
        this.errorMessage = errorMessage;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public List<FileInfo> getEntries() {
        return entries;
    }

    public void setEntries(List<FileInfo> entries) {
        this.entries = entries != null ? entries : new ArrayList<>();
    }

    public Integer getCount() {
        return count;
    }

    public void setCount(Integer count) {
        this.count = count;
    }

    public String getNextToken() {
        return nextToken;
    }

    public void setNextToken(String nextToken) {
        this.nextToken = nextToken;
    }

    public String getErrorMessage() {
        return errorMessage;
    }

    public void setErrorMessage(String errorMessage) {
        this.errorMessage = errorMessage;
    }
}
