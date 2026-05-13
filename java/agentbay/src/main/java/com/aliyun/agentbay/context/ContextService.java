package com.aliyun.agentbay.context;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import java.util.ArrayList;
import java.util.List;

public class ContextService {
    private final AgentBay agentBay;

    public ContextService(AgentBay agentBay) {
        this.agentBay = agentBay;
    }

    /**
     * Lists all available contexts with pagination support.
     *
     * @param params Parameters for listing contexts. If null, defaults will be used.
     * @return A result object containing the list of Context objects, pagination information, and request ID.
     * 
     */
    public ContextListResult list(ContextListParams params) {
        try {
            if (params == null) {
                params = new ContextListParams();
            }

            int maxResults = params.getMaxResults() != null ? params.getMaxResults() : 10;
            ListContextsRequest request = new ListContextsRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setMaxResults(maxResults);
            request.setNextToken(params.getNextToken());

            ListContextsResponse response = agentBay.getClient().listContexts(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new ContextListResult(requestId, false, new ArrayList<>(),
                    null, null, null, "Invalid response from API");
            }

            List<Context> contexts = new ArrayList<>();
            ListContextsResponseBody body = response.getBody();

            if (body.getData() != null) {
                for (ListContextsResponseBody.ListContextsResponseBodyData contextData : body.getData()) {
                    Context context = new Context();
                    context.setContextId(contextData.getId());
                    context.setName(contextData.getName());
                    context.setState(contextData.getState());
                    context.setCreatedAt(contextData.getCreateTime());
                    context.setUpdatedAt(contextData.getLastUsedTime());
                    context.setOsType(contextData.getOsType() != null ? contextData.getOsType() : "");
                    contexts.add(context);
                }
            }

            return new ContextListResult(
                requestId,
                body.getSuccess() != null ? body.getSuccess() : false,
                contexts,
                body.getNextToken(),
                body.getMaxResults(),
                body.getTotalCount(),
                ""
            );

        } catch (Exception e) {
            return new ContextListResult("", false, new ArrayList<>(),
                null, null, null, "Failed to list contexts: " + e.getMessage());
        }
    }

    /**
     * Lists all available contexts with default parameters.
     *
     * @return A result object containing the list of Context objects.
     */
    public ContextListResult list() {
        return list(null);
    }

    /**
     * Gets a context by name or ID. Optionally creates it if it doesn't exist.
     *
     * @param name     The name of the context to get.
     * @param create   Whether to create the context if it doesn't exist.
     * @param regionId The region ID for the request.
     * @return The ContextResult object containing the Context and request ID.
     *         The result contains:
     *         <ul>
     *         <li>success: true if the operation succeeded</li>
     *         <li>context: the Context object (if success is true)</li>
     *         <li>contextId: the ID of the context</li>
     *         <li>requestId: unique identifier for this API request</li>
     *         <li>errorMessage: error description (if success is false)</li>
     *         </ul>
     * @throws AgentBayException if neither name nor contextId is provided, or if create=true with contextId.
     * 
     */
    public ContextResult get(String name, boolean create, String regionId) {
        try {
            
            GetContextRequest request = new GetContextRequest();
            request.setName(name);
            request.setAllowCreate(create);
            request.setLoginRegionId(regionId);
            request.setAuthorization("Bearer " + agentBay.getApiKey());

            GetContextResponse response = agentBay.getClient().getContext(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new ContextResult(requestId, false, "", null, "Invalid response from API");
            }

            GetContextResponseBody body = response.getBody();

            // Check for API-level errors
            if (!Boolean.TRUE.equals(body.getSuccess()) && body.getCode() != null) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new ContextResult(requestId, false, "", null,
                    "[" + code + "] " + message);
            }

            if (body.getData() == null) {
                return new ContextResult(requestId, false, "", null,
                    "Context not found" + (create ? " and could not be created" : ""));
            }

            GetContextResponseBody.GetContextResponseBodyData data = body.getData();
            String contextId = data.getId();

            Context context = new Context();
            context.setContextId(contextId);
            // Use name from response if it's not null and not empty, otherwise use the provided name
            String contextName = data.getName();
            context.setName((contextName != null && !contextName.isEmpty()) ? contextName : name);
            context.setState(data.getState() != null ? data.getState() : "available");
            context.setCreatedAt(data.getCreateTime());
            context.setUpdatedAt(data.getLastUsedTime());
            context.setOsType(data.getOsType() != null ? data.getOsType() : "");

            return new ContextResult(
                requestId,
                body.getSuccess() != null ? body.getSuccess() : false,
                contextId,
                context,
                ""
            );

        } catch (Exception e) {
            return new ContextResult("", false, "", null,
                "Failed to get context " + name + ": " + e.getMessage());
        }
    }

    /**
     * Gets a context by name. Optionally creates it if it doesn't exist.
     *
     * @param name   The name of the context to get.
     * @param create Whether to create the context if it doesn't exist.
     * @return The ContextResult object containing the Context and request ID.
     */
    public ContextResult get(String name, boolean create) {
        return get(name, create, create ? agentBay.getRegionId() : null);
    }

    /**
     * Gets a context by name without creating it.
     *
     * @param name The name of the context to get.
     * @return The ContextResult object containing the Context and request ID.
     */
    public ContextResult get(String name) {
        return get(name, false, null);
    }

    /**
     * Creates a new context with the given name.
     *
     * @param name The name for the new context.
     * @return The created ContextResult object with request ID.
     * 
     */
    public ContextResult create(String name) {
        return get(name, true);
    }

    /**
     * Deletes the specified context.
     *
     * @param context The Context object to delete.
     * @return OperationResult containing success status and request ID.
     * 
     */
    public com.aliyun.agentbay.model.OperationResult delete(Context context) throws AgentBayException {
        try {
            DeleteContextRequest request = new DeleteContextRequest();
            request.setId(context.getContextId());
            request.setAuthorization("Bearer " + agentBay.getApiKey());

            DeleteContextResponse response = agentBay.getClient().deleteContext(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new com.aliyun.agentbay.model.OperationResult(
                    requestId, false, null, "Invalid response from API"
                );
            }

            DeleteContextResponseBody body = response.getBody();
            boolean success = Boolean.TRUE.equals(body.getSuccess());

            String errorMessage = "";
            if (!success) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                errorMessage = "[" + code + "] " + message;
            }

            return new com.aliyun.agentbay.model.OperationResult(
                requestId, success, success ? "true" : "false", errorMessage
            );

        } catch (Exception e) {
            throw new AgentBayException("Failed to delete context " + context.getContextId() + ": " + e.getMessage(), e);
        }
    }

    /**
     * Clears all data in the specified context.
     *
     * @param contextId The ID of the context to clear.
     * @return OperationResult containing success status and request ID.
     * @throws AgentBayException if an API or network error occurs during execution.
     * 
     */
    public com.aliyun.agentbay.model.OperationResult clear(String contextId) throws AgentBayException {
        try {
            com.aliyun.wuyingai20250506.models.ClearContextRequest request = new com.aliyun.wuyingai20250506.models.ClearContextRequest();
            request.setId(contextId);
            request.setAuthorization("Bearer " + agentBay.getApiKey());

            com.aliyun.wuyingai20250506.models.ClearContextResponse response = agentBay.getClient().clearContext(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new com.aliyun.agentbay.model.OperationResult(
                    requestId, false, null, "Invalid response from API"
                );
            }

            com.aliyun.wuyingai20250506.models.ClearContextResponseBody body = response.getBody();
            boolean success = Boolean.TRUE.equals(body.getSuccess());

            String errorMessage = "";
            if (!success) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                errorMessage = "[" + code + "] " + message;
            }

            return new com.aliyun.agentbay.model.OperationResult(
                requestId, success, success ? "true" : "false", errorMessage
            );

        } catch (Exception e) {
            throw new AgentBayException("Failed to clear context " + contextId + ": " + e.getMessage(), e);
        }
    }

    /**
     * Gets a presigned download URL for a file in a context.
     *
     * @param contextId The ID of the context.
     * @param filePath  The path of the file to download.
     * @return FileUrlResult containing the presigned URL, expiration time, and request ID.
     * 
     * Note: The presigned URL expires in 1 hour by default.
     * 
     */
    public com.aliyun.agentbay.model.FileUrlResult getFileDownloadUrl(String contextId, String filePath) throws AgentBayException {
        try {
            GetContextFileDownloadUrlRequest request = new GetContextFileDownloadUrlRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setContextId(contextId);
            request.setFilePath(filePath);

            GetContextFileDownloadUrlResponse response = agentBay.getClient().getContextFileDownloadUrl(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new com.aliyun.agentbay.model.FileUrlResult(
                    requestId, false, "", null, "Invalid response from API"
                );
            }

            GetContextFileDownloadUrlResponseBody body = response.getBody();

            if (!Boolean.TRUE.equals(body.getSuccess())) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new com.aliyun.agentbay.model.FileUrlResult(
                    requestId, false, "", null, "[" + code + "] " + message
                );
            }

            GetContextFileDownloadUrlResponseBody.GetContextFileDownloadUrlResponseBodyData data = body.getData();
            String url = data != null ? data.getUrl() : "";
            Long expireTime = data != null ? data.getExpireTime() : null;

            return new com.aliyun.agentbay.model.FileUrlResult(
                requestId, true, url, expireTime, ""
            );

        } catch (Exception e) {
            throw new AgentBayException("Failed to get file download URL: " + e.getMessage(), e);
        }
    }

    /**
     * Gets a presigned upload URL for a file in a context.
     *
     * @param contextId The ID of the context.
     * @param filePath  The path of the file to upload.
     * @return FileUrlResult containing the presigned URL, expiration time, and request ID.
     * 
     * Note:The presigned URL expires in 1 hour by default.
     * 
     */
    public com.aliyun.agentbay.model.FileUrlResult getFileUploadUrl(String contextId, String filePath) throws AgentBayException {
        try {
            GetContextFileUploadUrlRequest request = new GetContextFileUploadUrlRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setContextId(contextId);
            request.setFilePath(filePath);

            GetContextFileUploadUrlResponse response = agentBay.getClient().getContextFileUploadUrl(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new com.aliyun.agentbay.model.FileUrlResult(
                    requestId, false, "", null, "Invalid response from API"
                );
            }

            GetContextFileUploadUrlResponseBody body = response.getBody();

            if (!Boolean.TRUE.equals(body.getSuccess())) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new com.aliyun.agentbay.model.FileUrlResult(
                    requestId, false, "", null, "[" + code + "] " + message
                );
            }

            GetContextFileUploadUrlResponseBody.GetContextFileUploadUrlResponseBodyData data = body.getData();
            String url = data != null ? data.getUrl() : "";
            Long expireTime = data != null ? data.getExpireTime() : null;

            return new com.aliyun.agentbay.model.FileUrlResult(
                requestId, true, url, expireTime, ""
            );

        } catch (Exception e) {
            throw new AgentBayException("Failed to get file upload URL: " + e.getMessage(), e);
        }
    }

    /**
     * Deletes a file in a context.
     *
     * @param contextId The ID of the context.
     * @param filePath  The path of the file to delete.
     * @return OperationResult containing success status and request ID.
     * 
     */
    public com.aliyun.agentbay.model.OperationResult deleteFile(String contextId, String filePath) throws AgentBayException {
        try {
            DeleteContextFileRequest request = new DeleteContextFileRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setContextId(contextId);
            request.setFilePath(filePath);

            DeleteContextFileResponse response = agentBay.getClient().deleteContextFile(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new com.aliyun.agentbay.model.OperationResult(
                    requestId, false, null, "Invalid response from API"
                );
            }

            DeleteContextFileResponseBody body = response.getBody();
            boolean success = Boolean.TRUE.equals(body.getSuccess());

            String errorMessage = "";
            if (!success) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Failed to delete file";
                errorMessage = "[" + code + "] " + message;
            }

            return new com.aliyun.agentbay.model.OperationResult(
                requestId, success, success ? "true" : "false", errorMessage
            );

        } catch (Exception e) {
            throw new AgentBayException("Failed to delete file: " + e.getMessage(), e);
        }
    }

    /**
     * Lists files under a specific folder path in a context.
     *
     * @param contextId The ID of the context.
     * @param parentFolderPath The parent folder path to list files from.
     * @param pageNumber The page number for pagination. Default is 1.
     * @param pageSize The number of items per page. Default is 50.
     * @return ContextFileListResult containing the list of files and request ID.
     * 
     */
    public ContextFileListResult listFiles(String contextId, String parentFolderPath, int pageNumber, int pageSize) {
        try {
            DescribeContextFilesRequest request = new DescribeContextFilesRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setContextId(contextId);
            request.setParentFolderPath(parentFolderPath);
            request.setPageNumber(pageNumber);
            request.setPageSize(pageSize);

            DescribeContextFilesResponse response = agentBay.getClient().describeContextFiles(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new ContextFileListResult(
                    requestId, false, new ArrayList<>(), null, "Invalid response from API"
                );
            }

            DescribeContextFilesResponseBody body = response.getBody();

            if (!Boolean.TRUE.equals(body.getSuccess())) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new ContextFileListResult(
                    requestId, false, new ArrayList<>(), null, "[" + code + "] " + message
                );
            }

            List<FileInfo> entries = new ArrayList<>();
            if (body.getData() != null) {
                for (DescribeContextFilesResponseBody.DescribeContextFilesResponseBodyData data : body.getData()) {
                    FileInfo fileInfo = new FileInfo();
                    fileInfo.setFileId(data.getFileId());
                    fileInfo.setFileName(data.getFileName());
                    fileInfo.setFilePath(data.getFilePath());
                    fileInfo.setFileType(data.getFileType());
                    fileInfo.setGmtCreate(data.getGmtCreate());
                    fileInfo.setGmtModified(data.getGmtModified());
                    fileInfo.setSize(data.getSize());
                    fileInfo.setStatus(data.getStatus());
                    entries.add(fileInfo);
                }
            }

            return new ContextFileListResult(
                requestId, true, entries, body.getCount(), body.getNextToken(), ""
            );

        } catch (Exception e) {
            return new ContextFileListResult(
                "", false, new ArrayList<>(), null, "Failed to list files: " + e.getMessage()
            );
        }
    }

    /**
     * Lists files under a specific folder path in a context using max-results and next-token pagination.
     *
     * @param contextId The ID of the context.
     * @param parentFolderPath The parent folder path to list files from.
     * @param maxResults Maximum number of results to return (may be null to omit).
     * @param nextToken Token for the next page (may be null for the first page).
     * @return ContextFileListResult containing the list of files, next token, and request ID.
     */
    public ContextFileListResult listFiles(String contextId, String parentFolderPath, Integer maxResults, String nextToken) {
        try {
            DescribeContextFilesRequest request = new DescribeContextFilesRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setContextId(contextId);
            request.setParentFolderPath(parentFolderPath);
            request.setMaxResults(maxResults);
            request.setNextToken(nextToken);

            DescribeContextFilesResponse response = agentBay.getClient().describeContextFiles(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new ContextFileListResult(
                    requestId, false, new ArrayList<>(), null, "Invalid response from API"
                );
            }

            DescribeContextFilesResponseBody body = response.getBody();

            if (!Boolean.TRUE.equals(body.getSuccess())) {
                String code = body.getCode() != null ? body.getCode() : "Unknown";
                String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new ContextFileListResult(
                    requestId, false, new ArrayList<>(), null, "[" + code + "] " + message
                );
            }

            List<FileInfo> entries = new ArrayList<>();
            if (body.getData() != null) {
                for (DescribeContextFilesResponseBody.DescribeContextFilesResponseBodyData data : body.getData()) {
                    FileInfo fileInfo = new FileInfo();
                    fileInfo.setFileId(data.getFileId());
                    fileInfo.setFileName(data.getFileName());
                    fileInfo.setFilePath(data.getFilePath());
                    fileInfo.setFileType(data.getFileType());
                    fileInfo.setGmtCreate(data.getGmtCreate());
                    fileInfo.setGmtModified(data.getGmtModified());
                    fileInfo.setSize(data.getSize());
                    fileInfo.setStatus(data.getStatus());
                    entries.add(fileInfo);
                }
            }

            return new ContextFileListResult(
                requestId, true, entries, body.getCount(), body.getNextToken(), ""
            );

        } catch (Exception e) {
            return new ContextFileListResult(
                "", false, new ArrayList<>(), null, "Failed to list files: " + e.getMessage()
            );
        }
    }

    /**
     * Lists files under a specific folder path in a context with default pagination.
     *
     * @param contextId The ID of the context.
     * @param parentFolderPath The parent folder path to list files from.
     * @return ContextFileListResult containing the list of files and request ID.
     */
    public ContextFileListResult listFiles(String contextId, String parentFolderPath) {
        return listFiles(contextId, parentFolderPath, 1, 50);
    }
}