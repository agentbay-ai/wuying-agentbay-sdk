package com.aliyun.agentbay.context;

import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Consumer;
import java.util.stream.Collectors;

public class ContextManager {
    private static final ObjectMapper objectMapper = new ObjectMapper();

    private final Session session;

    public ContextManager(Session session) {
        this.session = session;
    }

    /**
     * Get context info for the session.
     * 
     * @return ContextInfoResult containing status data
     */
    public ContextInfoResult info() {
        return info(null, null, null);
    }

    /**
     * Get information about context synchronization status.
     *
     * @param contextId Optional ID of the context to get information for
     * @param path Optional path where the context is mounted
     * @param taskType Optional type of task to get information for (e.g., "upload", "download")
     * @return ContextInfoResult Result object containing context status data and request ID
     */
    public ContextInfoResult info(String contextId, String path, String taskType) {
        try {
            GetContextInfoRequest request = new GetContextInfoRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());

            if (contextId != null) {
                request.setContextId(contextId);
            }
            if (path != null) {
                request.setPath(path);
            }
            if (taskType != null) {
                request.setTaskType(taskType);
            }
            GetContextInfoResponse response = session.getAgentBay().getClient().getContextInfo(request);

            String requestId = ResponseUtil.extractRequestId(response);
            List<ContextStatusData> contextStatusData = new ArrayList<>();

            if (response != null && response.getBody() != null) {
                GetContextInfoResponseBody body = response.getBody();
                
                // Check for API-level errors
                Boolean bodySuccess = body.getSuccess();
                if (bodySuccess != null && !bodySuccess && body.getCode() != null) {
                    String code = body.getCode();
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    String errorMessage = String.format("[%s] %s", code, message);
                    return new ContextInfoResult(requestId, false, contextStatusData, errorMessage);
                }
                
                if (body.getData() != null) {
                    String contextStatus = body.getData().getContextStatus();
                    if (contextStatus != null && !contextStatus.isEmpty()) {
                        try {
                            // Parse the context status JSON
                            JsonNode statusItems = objectMapper.readTree(contextStatus);
                            for (JsonNode item : statusItems) {
                                if ("data".equals(item.get("type").asText())) {
                                    String dataString = item.get("data").asText();
                                    JsonNode dataItems = objectMapper.readTree(dataString);
                                    for (JsonNode dataItem : dataItems) {
                                        Map<String, Object> itemMap = objectMapper.convertValue(dataItem, Map.class);
                                        contextStatusData.add(ContextStatusData.fromMap(itemMap));
                                    }
                                }
                            }
                        } catch (Exception e) {
                        }
                    }
                }
            }

            return new ContextInfoResult(requestId, true, contextStatusData, "");

        } catch (Exception e) {
            return new ContextInfoResult("", false, new ArrayList<>(), "Failed to get context info: " + e.getMessage());
        }
    }

    /**
     * Sync context data (trigger upload).
     * 
     * @return ContextSyncResult indicating success/failure
     */
    public ContextSyncResult sync() {
        return sync(null, null, null);
    }

    /**
     * Synchronize a context with the session.
     *
     * @param contextId Optional ID of the context to synchronize
     * @param path Optional path where the context should be mounted; not limited to
     *             the path specified when creating the session (other backend-allowed
     *             paths are acceptable)
     * @param mode Optional synchronization mode (e.g., "upload", "download")
     * @return ContextSyncResult Result object containing success status and request ID
     */
    public ContextSyncResult sync(String contextId, String path, String mode) {
        try {
            SyncContextRequest request = new SyncContextRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());

            if (contextId != null) {
                request.setContextId(contextId);
            }
            if (path != null) {
                request.setPath(path);
            }
            if (mode != null) {
                request.setMode(mode);
            }
            SyncContextResponse response = session.getAgentBay().getClient().syncContext(request);

            String requestId = ResponseUtil.extractRequestId(response);
            boolean success = false;
            String errorMessage = "";

            if (response != null && response.getBody() != null) {
                SyncContextResponseBody body = response.getBody();
                success = body.getSuccess() != null ? body.getSuccess() : false;
                
                // Check for API-level errors
                if (!success && body.getCode() != null) {
                    String code = body.getCode();
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    errorMessage = String.format("[%s] %s", code, message);
                }
            }

            return new ContextSyncResult(requestId, success, errorMessage);

        } catch (Exception e) {
            return new ContextSyncResult("", false, "Failed to sync context: " + e.getMessage());
        }
    }

    /**
     * Sync context data with callback mode (non-blocking).
     * Returns immediately and calls the callback when sync completes.
     *
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(Consumer<Boolean> callback) {
        return sync(null, null, null, callback);
    }

    /**
     * Sync context data with optional parameters and callback mode (non-blocking).
     * Returns immediately and calls the callback when sync completes.
     *
     * @param contextId Optional ID of the context to synchronize
     * @param path Optional path where the context should be mounted
     * @param mode Optional synchronization mode (e.g., "upload", "download")
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback) {
        return sync(contextId, path, mode, callback, 150, 500);
    }

    /**
     * Sync context data with optional parameters and callback mode (non-blocking).
     * Returns immediately and calls the callback when sync completes.
     *
     * @param contextId Optional ID of the context to synchronize
     * @param path Optional path where the context should be mounted
     * @param mode Optional synchronization mode (e.g., "upload", "download")
     * @param callback Callback function that receives success status (true if successful, false otherwise)
     * @param maxRetries Maximum number of retries for polling completion status (default: 150)
     * @param retryInterval Initial interval in milliseconds for exponential backoff polling (default: 500)
     * @return ContextSyncResult indicating initial sync trigger success/failure
     */
    public ContextSyncResult sync(String contextId, String path, String mode, Consumer<Boolean> callback,
                                  int maxRetries, int retryInterval) {
        // First trigger the sync
        ContextSyncResult syncResult = sync(contextId, path, mode);

        if (!syncResult.isSuccess()) {
            // If sync trigger failed, call callback with false
            if (callback != null) {
                callback.accept(false);
            }
            return syncResult;
        }

        // Start polling in background thread
        if (callback != null) {
            Thread pollThread = new Thread(() -> {
                pollForCompletion(callback, contextId, path, maxRetries, retryInterval);
            });
            pollThread.setDaemon(true);
            pollThread.start();
        }

        return syncResult;
    }

    /**
     * Polls the info interface to check if sync is completed and calls callback.
     * 
     * <p>This method continuously polls the context status until all sync tasks
     * (upload/download) are completed or failed, or until the maximum number of
     * retries is reached.</p>
     *
     * @param callback Callback function that receives success status
     * @param contextId ID of the context to check
     * @param path Path to check
     * @param maxRetries Maximum number of retries
     * @param retryInterval Initial interval in milliseconds for exponential backoff polling
     */
    private void pollForCompletion(Consumer<Boolean> callback, String contextId, String path,
                                   int maxRetries, int retryInterval) {
        int maxInterval = 5000;
        double backoffFactor = 1.1;
        int currentInterval = retryInterval;

        for (int retry = 0; retry < maxRetries; retry++) {
            try {
                ContextInfoResult infoResult = info(contextId, path, null);

                boolean allCompleted = true;
                boolean hasFailure = false;
                boolean hasSyncTasks = false;

                for (ContextStatusData item : infoResult.getContextStatusData()) {
                    String taskType = item.getTaskType();
                    if (taskType == null || (!"upload".equals(taskType) && !"download".equals(taskType))) {
                        continue;
                    }

                    hasSyncTasks = true;
                    if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                        allCompleted = false;
                        break;
                    }

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                if (allCompleted || !hasSyncTasks) {
                    if (hasFailure) {
                        callback.accept(false);
                    } else if (hasSyncTasks) {
                        callback.accept(true);
                    } else {
                        callback.accept(true);
                    }
                    return;
                }
                Thread.sleep(currentInterval);
                currentInterval = Math.min((int) (currentInterval * backoffFactor), maxInterval);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                callback.accept(false);
                return;
            } catch (Exception e) {
                try {
                    Thread.sleep(currentInterval);
                    currentInterval = Math.min((int) (currentInterval * backoffFactor), maxInterval);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    callback.accept(false);
                    return;
                }
            }
        }

        callback.accept(false);
    }

    /**
     * Sync context data and wait for completion
     *
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait() {
        return syncAndWait(null, null, null);
    }

    /**
     * Sync context data with optional parameters and wait for completion
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait(String contextId, String path, String mode) {
        return syncAndWait(contextId, path, mode, 150, 500);
    }

    /**
     * Sync context data with optional parameters and wait for completion
     *
     * @param contextId Context ID (optional)
     * @param path Path (optional)
     * @param mode Sync mode (optional)
     * @param maxRetries Maximum number of retries for polling completion status (default: 150)
     * @param retryInterval Initial interval in milliseconds for exponential backoff polling (default: 500)
     * @return ContextSyncResult indicating success/failure after waiting for completion
     */
    public ContextSyncResult syncAndWait(String contextId, String path, String mode,
                                         int maxRetries, int retryInterval) {
        ContextSyncResult syncResult = sync(contextId, path, mode);

        if (!syncResult.isSuccess()) {
            return syncResult;
        }

        int maxInterval = 5000;
        double backoffFactor = 1.1;
        int currentInterval = retryInterval;

        for (int retry = 0; retry < maxRetries; retry++) {
            try {
                ContextInfoResult infoResult = info(contextId, path, null);

                boolean allCompleted = true;
                boolean hasFailure = false;
                boolean hasSyncTasks = false;

                for (ContextStatusData item : infoResult.getContextStatusData()) {
                    String taskType = item.getTaskType();
                    if (taskType == null || (!"upload".equals(taskType) && !"download".equals(taskType))) {
                        continue;
                    }

                    hasSyncTasks = true;
                    if (!"Success".equals(item.getStatus()) && !"Failed".equals(item.getStatus())) {
                        allCompleted = false;
                        break;
                    }

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                if (allCompleted || !hasSyncTasks) {
                    if (hasFailure) {
                        return new ContextSyncResult(syncResult.getRequestId(), false);
                    } else if (hasSyncTasks) {
                        return new ContextSyncResult(syncResult.getRequestId(), true);
                    } else {
                        return new ContextSyncResult(syncResult.getRequestId(), true);
                    }
                }
                Thread.sleep(currentInterval);
                currentInterval = Math.min((int) (currentInterval * backoffFactor), maxInterval);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new ContextSyncResult(syncResult.getRequestId(), false);
            } catch (Exception e) {
                try {
                    Thread.sleep(currentInterval);
                    currentInterval = Math.min((int) (currentInterval * backoffFactor), maxInterval);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    return new ContextSyncResult(syncResult.getRequestId(), false);
                }
            }
        }

        return new ContextSyncResult(syncResult.getRequestId(), false);
    }

    /**
     * Dynamically binds one or more contexts to the current session.
     *
     * <pre>{@code
     * ContextSync cs = ContextSync.create(contextId, "/tmp/ctx-data", null);
     * ContextBindResult result = session.getContext().bind(cs);
     * System.out.println("Bind success: " + result.isSuccess());
     * }</pre>
     *
     * @param contexts List of ContextSync objects to bind
     * @param waitForCompletion Whether to poll until all bindings are confirmed
     * @return ContextBindResult with the result of the operation
     */
    public ContextBindResult bind(List<ContextSync> contexts, boolean waitForCompletion) {
        if (contexts == null || contexts.isEmpty()) {
            return new ContextBindResult("", false, "At least one context is required");
        }

        try {
            List<BindContextsRequest.BindContextsRequestPersistenceDataList> persistenceDataList = new ArrayList<>();
            for (ContextSync ctx : contexts) {
                BindContextsRequest.BindContextsRequestPersistenceDataList item =
                    new BindContextsRequest.BindContextsRequestPersistenceDataList();
                item.setContextId(ctx.getContextId());
                item.setPath(ctx.getPath());
                if (ctx.getPolicy() != null) {
                    Map<String, Object> policyMap = ctx.getPolicy().toMap();
                    item.setPolicy(objectMapper.writeValueAsString(policyMap));
                }
                persistenceDataList.add(item);
            }

            BindContextsRequest request = new BindContextsRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());
            request.setPersistenceDataList(persistenceDataList);

            BindContextsResponse response = session.getAgentBay().getClient().bindContexts(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response != null && response.getBody() != null) {
                BindContextsResponseBody body = response.getBody();
                if (body.getSuccess() != null && !body.getSuccess()) {
                    String code = body.getCode() != null ? body.getCode() : "Unknown";
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    return new ContextBindResult(requestId, false, String.format("[%s] %s", code, message));
                }
            }

            if (waitForCompletion) {
                List<String> contextIds = contexts.stream()
                    .map(ContextSync::getContextId)
                    .collect(Collectors.toList());
                pollForBindCompletion(contextIds, 60, 2000);
            }

            return new ContextBindResult(requestId, true);
        } catch (Exception e) {
            return new ContextBindResult("", false, "Failed to bind contexts: " + e.getMessage());
        }
    }

    /**
     * Binds a single context to the current session.
     *
     * @param context The ContextSync object to bind
     * @return ContextBindResult with the result of the operation
     */
    public ContextBindResult bind(ContextSync context) {
        List<ContextSync> list = new ArrayList<>();
        list.add(context);
        return bind(list, true);
    }

    /**
     * Lists all context bindings for the current session.
     *
     * <pre>{@code
     * ContextBindingsResult result = session.getContext().listBindings();
     * for (ContextBinding b : result.getBindings()) {
     *     System.out.println("Context " + b.getContextId() + " at " + b.getPath());
     * }
     * }</pre>
     *
     * @return ContextBindingsResult with the list of bindings
     */
    public ContextBindingsResult listBindings() {
        try {
            DescribeSessionContextsRequest request = new DescribeSessionContextsRequest();
            request.setAuthorization("Bearer " + session.getApiKey());
            request.setSessionId(session.getSessionId());

            DescribeSessionContextsResponse response =
                session.getAgentBay().getClient().describeSessionContexts(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response != null && response.getBody() != null) {
                DescribeSessionContextsResponseBody body = response.getBody();
                if (body.getSuccess() != null && !body.getSuccess()) {
                    String code = body.getCode() != null ? body.getCode() : "Unknown";
                    String message = body.getMessage() != null ? body.getMessage() : "Unknown error";
                    return new ContextBindingsResult(requestId, false, new ArrayList<>(),
                        String.format("[%s] %s", code, message));
                }

                List<ContextBinding> bindings = new ArrayList<>();
                if (body.getData() != null) {
                    for (DescribeSessionContextsResponseBody.DescribeSessionContextsResponseBodyData item : body.getData()) {
                        bindings.add(new ContextBinding(
                            item.getContextId(),
                            item.getContextName(),
                            item.getPath(),
                            item.getPolicy(),
                            item.getBindTime()
                        ));
                    }
                }

                return new ContextBindingsResult(requestId, true, bindings);
            }

            return new ContextBindingsResult(requestId != null ? requestId : "", false, new ArrayList<>(),
                "Empty response");
        } catch (Exception e) {
            return new ContextBindingsResult("", false, new ArrayList<>(),
                "Failed to list bindings: " + e.getMessage());
        }
    }

    private void pollForBindCompletion(List<String> expectedContextIds, int maxRetries, int retryIntervalMs) {
        for (int i = 0; i < maxRetries; i++) {
            try {
                ContextBindingsResult result = listBindings();
                if (result.isSuccess()) {
                    Set<String> boundIds = new HashSet<>();
                    for (ContextBinding b : result.getBindings()) {
                        boundIds.add(b.getContextId());
                    }
                    if (boundIds.containsAll(expectedContextIds)) {
                        return;
                    }
                }
                Thread.sleep(retryIntervalMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return;
            }
        }
    }
}
