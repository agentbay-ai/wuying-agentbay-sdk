package com.aliyun.agentbay.browser;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.aliyun.agentbay.exception.BrowserException;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.microsoft.playwright.BrowserContext;
import com.microsoft.playwright.CDPSession;
import com.microsoft.playwright.Page;

/**
 * BrowserOperator handles browser automation and small parts of agentic logic.
 * 
 * <p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
 * we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>
 */
public class BrowserOperator extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SERVER_BROWSER_USE = "wuying_browseruse";

    private final Browser browser;

    public BrowserOperator(Session session, Browser browser) {
        super(session);
        this.browser = browser;
    }

    /**
     * Get page and context index from Playwright Page object.
     * Matches Python _get_page_and_context_index method.
     * 
     * @param page Playwright Page object
     * @return PageContextIndex containing page ID and context index
     * @throws BrowserException if indices cannot be determined
     */
    private PageContextIndex getPageAndContextIndex(Page page) throws BrowserException {
        if (page == null) {
            return new PageContextIndex(null, 0);
        }

        try {
            BrowserContext context = page.context();
            CDPSession cdpSession = context.newCDPSession(page);
            Object targetInfoResponse = cdpSession.send("Target.getTargetInfo");
            cdpSession.detach();

            String pageIndex;
            if (targetInfoResponse instanceof JsonObject) {
                JsonObject response = (JsonObject) targetInfoResponse;
                JsonObject targetInfo = response.getAsJsonObject("targetInfo");
                pageIndex = targetInfo.get("targetId").getAsString();
            } else if (targetInfoResponse instanceof Map) {
                @SuppressWarnings("unchecked")
                Map<String, Object> response = (Map<String, Object>) targetInfoResponse;
                @SuppressWarnings("unchecked")
                Map<String, Object> targetInfo = (Map<String, Object>) response.get("targetInfo");
                pageIndex = (String) targetInfo.get("targetId");
            } else {
                Gson gson = new Gson();
                String json = gson.toJson(targetInfoResponse);
                JsonObject response = gson.fromJson(json, JsonObject.class);
                JsonObject targetInfo = response.getAsJsonObject("targetInfo");
                pageIndex = targetInfo.get("targetId").getAsString();
            }

            return new PageContextIndex(pageIndex, 0);
        } catch (Exception e) {
            throw new BrowserException("Failed to get page index: " + e.getMessage());
        }
    }

    /**
     * Helper class to hold page and context indices.
     */
    private static class PageContextIndex {
        final String pageIndex;
        final int contextIndex;

        PageContextIndex(String pageIndex, int contextIndex) {
            this.pageIndex = pageIndex;
            this.contextIndex = contextIndex;
        }
    }

    /**
     * Navigates a specific page to the given URL.
     *
     * @param url The URL to navigate to
     * @return A string indicating the result of the navigation
     * @throws BrowserException if browser is not initialized
     */
    public String navigate(String url) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser must be initialized before calling navigate.");
        }
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("url", url);
            OperationResult response = callMcpToolTimeout("page_use_navigate", args);
            if (response.isSuccess()) {
                return response.getData();
            } else {
                return "Navigation failed: " + response.getErrorMessage();
            }
        } catch (Exception e) {
            throw new BrowserException("Failed to navigate: " + e.getMessage());
        }
    }

    /**
     * Closes the remote browser operator session.
     * This will terminate the browser process managed by the operator.
     *
     * @return true if successful, false otherwise
     * @throws BrowserException if operation fails
     */
    public boolean close() throws BrowserException {
        try {
            OperationResult response = callMcpToolTimeout("page_use_close_session", new HashMap<>());
            if (response.isSuccess()) {
                return true;
            } else {
                return false;
            }
        } catch (Exception e) {
            throw new BrowserException("Failed to call close: " + e.getMessage());
        }
    }

    /**
     * Takes a screenshot of the specified page.
     *
     * @param page The Playwright Page object to take a screenshot of. If null, the operator's currently focused page will be used
     * @param fullPage Whether to capture the full scrollable page
     * @param quality The quality of the image (0-100), for JPEG format
     * @param clip An object specifying the clipping region {x, y, width, height}
     * @param timeout Custom timeout for the operation in seconds
     * @return A base64 encoded data URL of the screenshot, or an error message
     * @throws BrowserException if browser is not initialized
     */
    public String screenshot(Page page, boolean fullPage, int quality, Map<String, Double> clip, Integer timeout) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser must be initialized before calling screenshot.");
        }
        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeScreenshot(indices.contextIndex, indices.pageIndex, fullPage, quality, clip, timeout);
        } catch (Exception e) {
            throw new BrowserException("Failed to call screenshot: " + e.getMessage());
        }
    }

    /**
     * Overloaded screenshot method with default parameters.
     * 
     * @param page The Playwright Page object to take a screenshot of
     * @return A base64 encoded data URL of the screenshot
     * @throws BrowserException if browser is not initialized
     */
    public String screenshot(Page page) throws BrowserException {
        return screenshot(page, true, 80, null, null);
    }

    /**
     * Execute screenshot with parameters.
     * 
     * @param contextId Browser context ID
     * @param pageId Page ID (can be null)
     * @param fullPage Whether to capture the full scrollable page
     * @param quality The quality of the image (0-100)
     * @param clip Clipping region
     * @param timeout Custom timeout
     * @return Screenshot data or error message
     */
    private String executeScreenshot(int contextId, String pageId, boolean fullPage, int quality,
                                     Map<String, Double> clip, Integer timeout) {
        Map<String, Object> args = new HashMap<>();
        args.put("context_id", contextId);
        if (pageId != null) args.put("page_id", pageId);
        args.put("full_page", fullPage);
        args.put("quality", quality);
        if (clip != null) args.put("clip", clip);
        if (timeout != null) args.put("timeout", timeout);

        OperationResult response = callMcpToolTimeout("page_use_screenshot", args);
        if (response.isSuccess()) {
            return response.getData();
        } else {
            return "Screenshot failed: " + response.getErrorMessage();
        }
    }

    /**
     * Perform an action on a web page.
     * Uses synchronous execution.
     *
     * @param page The Playwright Page object to act on. If null, the operator's currently focused page will be used automatically
     * @param actionInput The action to perform (either ActOptions or ObserveResult)
     * @return The result of the action
     * @throws BrowserException if browser is not initialized
     */
    public ActResult act(Page page, Object actionInput) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeAct(actionInput, indices.contextIndex, indices.pageIndex);
        } catch (Exception e) {
            throw new BrowserException("Failed to act: " + e.getMessage());
        }
    }

    /**
     * Perform an action on a web page without explicit Playwright Page.
     * This overload allows using the agent independently of Playwright.
     * Uses the default context (index 0) and currently focused page.
     *
     * @param actionInput The action to perform (either ActOptions or ObserveResult)
     * @return The result of the action
     * @throws BrowserException if browser is not initialized
     */
    public ActResult act(Object actionInput) throws BrowserException {
        return act(null, actionInput);
    }

    /**
     * Perform an action on the page asynchronously - matches Python act_async method
     * Uses asynchronous execution with task polling for long-running operations
     *
     * @param actionInput Either ActOptions or ObserveResult describing the action
     * @param page Playwright page object (null to use currently focused page)
     * @return ActResult containing success status and execution details
     * @throws BrowserException if browser is not initialized or action fails
     *
     */
    public ActResult actAsync(Object actionInput, Page page) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeActAsync(actionInput, indices.contextIndex, indices.pageIndex);
        } catch (Exception e) {
            throw new BrowserException("Failed to act async: " + e.getMessage());
        }
    }

    /**
     * Perform an action on the page asynchronously without explicit Playwright Page
     * This overload allows using the agent independently of Playwright
     * Uses the default context (index 0) and currently focused page
     *
     * @param actionInput Either ActOptions or ObserveResult describing the action
     * @return ActResult containing success status and execution details
     * @throws BrowserException if browser is not initialized or action fails
     *
     */
    public ActResult actAsync(Object actionInput) throws BrowserException {
        return actAsync(actionInput, null);
    }

    /**
     * Build common act arguments from actionInput.
     */
    private Map<String, Object> buildActArgs(Object actionInput, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = new HashMap<>();
        args.put("context_id", contextId);
        if (pageId != null) args.put("page_id", pageId);

        if (actionInput instanceof ActOptions) {
            ActOptions options = (ActOptions) actionInput;
            args.put("action", options.getAction());
            if (options.getVariables() != null) args.put("variables", options.getVariables());
            if (options.getTimeout() != null) args.put("timeout", options.getTimeout());
            if (options.getUseVision() != null) args.put("use_vision", options.getUseVision());
        } else if (actionInput instanceof ObserveResult) {
            ObserveResult result = (ObserveResult) actionInput;
            try {
                Map<String, Object> actionDict = new HashMap<>();
                actionDict.put("method", result.getMethod());
                actionDict.put("arguments", result.getArguments());
                args.put("action", objectMapper.writeValueAsString(actionDict));
            } catch (Exception e) {
                throw new BrowserException("Failed to serialize action: " + e.getMessage());
            }
        }
        args.values().removeIf(java.util.Objects::isNull);
        return args;
    }

    private String getActTaskName(Object actionInput) {
        if (actionInput instanceof ActOptions) {
            return ((ActOptions) actionInput).getAction();
        } else if (actionInput instanceof ObserveResult) {
            return ((ObserveResult) actionInput).getMethod();
        }
        return "act";
    }

    /**
     * @param actionInput Either ActOptions or ObserveResult
     * @param contextId Browser context ID
     * @param pageId Page ID
     * @return ActResult containing success status and execution details
     * @throws BrowserException if the action fails
     */
    private ActResult executeAct(Object actionInput, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = buildActArgs(actionInput, contextId, pageId);
        String taskName = getActTaskName(actionInput);

        OperationResult response = callMcpToolTimeout("page_use_act", args);
        if (!response.isSuccess()) {
            throw new BrowserException("Act failed: " + response.getErrorMessage());
        }

        try {
            // page_use_act returns steps directly (JSON array) or error object (JSON map)
            // parseJsonResponse wraps arrays as {steps: [...], is_done: true, success: true}
            Map<String, Object> responseData = parseJsonResponse(response.getData());
            Object steps = responseData.get("steps");
            boolean success = Boolean.TRUE.equals(responseData.get("success"));
            String taskStatus;
            if (steps != null) {
                taskStatus = steps instanceof String ? (String) steps : objectMapper.writeValueAsString(steps);
            } else {
                taskStatus = "No actions have been executed.";
            }
            return new ActResult(success, taskStatus, taskName);
        } catch (Exception e) {
            throw new BrowserException("Failed to parse act response: " + e.getMessage());
        }
    }

    /**
     * Returns the result synchronously to the caller (simulated sync via polling).
     *
     * @param actionInput Either ActOptions or ObserveResult
     * @param contextId Browser context ID
     * @param pageId Page ID
     * @return ActResult containing success status and execution details
     * @throws BrowserException if the action fails
     */
    private ActResult executeActAsync(Object actionInput, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = buildActArgs(actionInput, contextId, pageId);
        String taskName = getActTaskName(actionInput);

        System.out.println("actAsync: " + taskName);
        OperationResult response = callMcpToolTimeout("page_use_act_async", args);
        if (!response.isSuccess()) {
            throw new BrowserException("Failed to start act task: " + response.getErrorMessage());
        }

        try {
            Map<String, Object> responseData = parseJsonResponse(response.getData());
            String taskId = (String) responseData.get("task_id");
            if (taskId == null) {
                throw new BrowserException("No task_id in async act response: " + responseData);
            }

            int timeoutSec = 300;
            if (actionInput instanceof ActOptions) {
                Integer t = ((ActOptions) actionInput).getTimeout();
                if (t != null) timeoutSec = t;
            }
            long startTs = System.currentTimeMillis();

            while (true) {
                Thread.sleep(3000);

                Map<String, Object> params = new HashMap<>();
                params.put("task_id", taskId);
                OperationResult result = callMcpToolTimeout("page_use_get_act_result", params);

                if (result.isSuccess() && result.getData() != null && !result.getData().isEmpty()) {
                    Map<String, Object> data = parseJsonResponse(result.getData());

                    Object steps = data.get("steps");
                    boolean isDone = Boolean.TRUE.equals(data.get("is_done"));
                    boolean success = Boolean.TRUE.equals(data.get("success"));
                    String noActionMsg = "No actions have been executed.";

                    if (isDone) {
                        String taskStatus;
                        if (steps != null) {
                            taskStatus = steps instanceof String ? (String) steps : objectMapper.writeValueAsString(steps);
                        } else {
                            taskStatus = noActionMsg;
                        }
                        System.out.println("Task " + taskId + ":" + taskName + " is done. Success: " + success + ". " + taskStatus);
                        return new ActResult(success, taskStatus, taskName);
                    }

                    String taskStatus = steps != null ? steps.toString() : noActionMsg;
                    System.out.println("Task " + taskId + ":" + taskName + " in progress. " + taskStatus);
                }

                long elapsed = (System.currentTimeMillis() - startTs) / 1000;
                if (elapsed >= timeoutSec) {
                    throw new BrowserException("Task " + taskId + ":" + taskName + " Act timeout after " + timeoutSec + "s");
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BrowserException("Act task interrupted: " + e.getMessage());
        } catch (BrowserException e) {
            throw e;
        } catch (Exception e) {
            throw new BrowserException("Failed to parse act response: " + e.getMessage());
        }
    }

    /**
     * Parse JSON response - helper method for parsing API responses.
     * 
     * @param data JSON string to parse
     * @return Parsed map of response data
     * @throws Exception if parsing fails
     */
    @SuppressWarnings("unchecked")
    private Map<String, Object> parseJsonResponse(String data) throws Exception {
        if (data == null || data.isEmpty()) {
            return new HashMap<>();
        }
        String trimmed = data.trim();
        if (trimmed.startsWith("[")) {
            // Response is a JSON Array - wrap it in a Map with "steps" key
            List<Object> list = objectMapper.readValue(trimmed, new TypeReference<List<Object>>(){});
            Map<String, Object> result = new HashMap<>();
            result.put("steps", list);
            result.put("is_done", true);
            result.put("success", true);
            return result;
        }
        return objectMapper.readValue(trimmed, new TypeReference<Map<String, Object>>(){});
    }

    /**
     * Observe elements or state on a web page.
     *
     * @param page The Playwright Page object to observe. If null, the operator's currently focused page will be used
     * @param options Options to configure the observation behavior
     * @return A tuple containing a success boolean and a list of observation results
     * @throws BrowserException if browser is not initialized
     */
    public ObserveResultTuple observe(Page page, ObserveOptions options) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            Map<String, Object> args = new HashMap<>();
            // Use Python-compatible parameter names
            args.put("page_id", indices.pageIndex);
            args.put("context_id", indices.contextIndex);
            args.putAll(options.toMap());

            OperationResult result = callMcpTool("page_use_observe", args);
            return parseObserveResult(result);
        } catch (Exception e) {
            return new ObserveResultTuple(false, new ArrayList<>());
        }
    }

    /**
     * Observe elements or state on a web page without explicit Playwright Page.
     * This overload allows using the agent independently of Playwright.
     * Uses the default context (index 0) and currently focused page.
     *
     * @param options Options to configure the observation behavior
     * @return ObserveResultTuple containing success status and list of observation results
     * @throws BrowserException if browser is not initialized or observation fails
     */
    public ObserveResultTuple observe(ObserveOptions options) throws BrowserException {
        return observe(null, options);
    }

    private ObserveResultTuple parseObserveResult(OperationResult result) {
        if (!result.isSuccess()) {
            return new ObserveResultTuple(false, new ArrayList<>());
        }

        try {
            List<Map<String, Object>> observeResults = objectMapper.readValue(
                result.getData(),
                new TypeReference<List<Map<String, Object>>>(){}
            );

            List<ObserveResult> results = new ArrayList<>();
            if (observeResults != null) {
                for (Map<String, Object> item : observeResults) {
                    String selector = (String) item.get("selector");
                    String description = (String) item.get("description");
                    String method = (String) item.get("method");
                    String argumentsStr = (String) item.get("arguments");

                    Map<String, Object> arguments;
                    try {
                        arguments = objectMapper.readValue(argumentsStr, new TypeReference<Map<String, Object>>(){});
                    } catch (Exception e) {
                        arguments = new HashMap<>();
                    }

                    results.add(new ObserveResult(selector, description, method, arguments));
                }
            }

            return new ObserveResultTuple(true, results);
        } catch (Exception e) {
            return new ObserveResultTuple(false, new ArrayList<>());
        }
    }

    /**
     * Tuple class to hold observe operation results.
     */
    public static class ObserveResultTuple {
        private final boolean success;
        private final List<ObserveResult> results;

        public ObserveResultTuple(boolean success, List<ObserveResult> results) {
            this.success = success;
            this.results = results;
        }

        public boolean isSuccess() { return success; }
        public List<ObserveResult> getResults() { return results; }
    }

    /**
     * Extract information from a web page.
     * Uses synchronous execution.
     *
     * @param page The Playwright Page object to extract from. If null, the operator's currently focused page will be used
     * @param options Options to configure the extraction, including schema
     * @param <T> The type of data to extract
     * @return A tuple containing a success boolean and the extracted data as a Pydantic model instance, or null on failure
     * @throws BrowserException if browser is not initialized
     */
    public <T> ExtractResultTuple<T> extract(Page page, ExtractOptions<T> options) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeExtract(options, indices.contextIndex, indices.pageIndex);
        } catch (Exception e) {
            throw new BrowserException("Failed to extract: " + e.getMessage());
        }
    }

    /**
     * Extract structured data from the page without explicit Playwright Page.
     * This overload allows using the agent independently of Playwright.
     * Uses the default context (index 0) and currently focused page.
     *
     * @param options ExtractOptions containing instruction, schema, and extraction parameters
     * @param <T> The type of data to extract (must match the schema class)
     * @return ExtractResultTuple containing success status and extracted data of type T
     * @throws BrowserException if browser is not initialized or extraction fails
     */
    public <T> ExtractResultTuple<T> extract(ExtractOptions<T> options) throws BrowserException {
        return extract(null, options);
    }

    /**
     * Extract structured data from the page asynchronously - matches Python extract_async method
     * Uses asynchronous execution with task polling for complex extraction operations
     *
     * @param options ExtractOptions containing instruction, schema, and extraction parameters
     * @param page Playwright page object (null to use currently focused page)
     * @param <T> The type of data to extract (must match the schema class)
     * @return ExtractResultTuple containing success status and extracted data of type T
     * @throws BrowserException if browser is not initialized or extraction fails
     *
     */
    public <T> ExtractResultTuple<T> extractAsync(ExtractOptions<T> options, Page page) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeExtractAsync(options, indices.contextIndex, indices.pageIndex);
        } catch (Exception e) {
            throw new BrowserException("Failed to extract async: " + e.getMessage());
        }
    }

    /**
     * Extract structured data from the page asynchronously without explicit Playwright Page
     * This overload allows using the agent independently of Playwright
     * Uses the default context (index 0) and currently focused page
     *
     * @param options ExtractOptions containing instruction, schema, and extraction parameters
     * @param <T> The type of data to extract (must match the schema class)
     * @return ExtractResultTuple containing success status and extracted data of type T
     * @throws BrowserException if browser is not initialized or extraction fails
     *
     */
    public <T> ExtractResultTuple<T> extractAsync(ExtractOptions<T> options) throws BrowserException {
        return extractAsync(options, null);
    }

    /**
     * Execute extract synchronously - calls page_use_extract which waits for completion
     * on the server side and returns the result directly. No client-side polling needed.
     *
     * @param options ExtractOptions containing instruction and schema
     * @param contextId Browser context ID
     * @param pageId Page ID
     * @param <T> The type of data to extract
     * @return ExtractResultTuple containing success status and extracted data
     * @throws BrowserException if extraction fails
     */
    private <T> ExtractResultTuple<T> executeExtract(ExtractOptions<T> options, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = new HashMap<>();
        args.put("context_id", contextId);
        if (pageId != null) args.put("page_id", pageId);
        args.putAll(options.toMap());
        args.values().removeIf(java.util.Objects::isNull);

        OperationResult response = callMcpToolTimeout("page_use_extract", args);
        if (!response.isSuccess()) {
            throw new BrowserException("Extract failed: " + response.getErrorMessage());
        }

        try {
            // page_use_extract returns the extracted data directly
            Map<String, Object> responseData = parseJsonResponse(response.getData());
            T extractedObject = objectMapper.convertValue(responseData, options.getSchema());
            return new ExtractResultTuple<>(true, extractedObject);
        } catch (Exception e) {
            throw new BrowserException("Failed to parse extract response: " + e.getMessage());
        }
    }

    /**
     * Returns the result synchronously to the caller (simulated sync via polling).
     *
     * @param options ExtractOptions containing instruction and schema
     * @param contextId Browser context ID
     * @param pageId Page ID
     * @param <T> The type of data to extract
     * @return ExtractResultTuple containing success status and extracted data
     * @throws BrowserException if extraction fails
     */
    private <T> ExtractResultTuple<T> executeExtractAsync(ExtractOptions<T> options, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = new HashMap<>();
        args.put("context_id", contextId);
        if (pageId != null) args.put("page_id", pageId);
        args.putAll(options.toMap());
        args.values().removeIf(java.util.Objects::isNull);

        System.out.println("extractAsync: " + options.getInstruction());
        OperationResult response = callMcpToolTimeout("page_use_extract_async", args);
        if (!response.isSuccess()) {
            throw new BrowserException("Failed to start extraction task");
        }

        // Parse task_id from response
        try {
            Map<String, Object> responseData = parseJsonResponse(response.getData());
            String taskId = (String) responseData.get("task_id");

            if (taskId == null) {
                // Extraction completed immediately
                try {
                    T extractedObject = objectMapper.convertValue(responseData, options.getSchema());
                    return new ExtractResultTuple<>(true, extractedObject);
                } catch (Exception e) {
                    throw new BrowserException("No task_id and failed to validate response as result: " + e.getMessage() + ", data: " + responseData);
                }
            }

            Integer clientTimeout = options.getTimeout();
            int timeoutSec = (clientTimeout != null) ? clientTimeout : 300;
            long startTs = System.currentTimeMillis();

            while (true) {
                Thread.sleep(3000);

                Map<String, Object> extractParams = new HashMap<>();
                extractParams.put("task_id", taskId);
                OperationResult result = callMcpToolTimeout("page_use_get_extract_result", extractParams);

                if (result.isSuccess() && result.getData() != null && !result.getData().trim().isEmpty()) {
                    if (isPendingMcpResponse(result.getData())) {
                        long elapsed = (System.currentTimeMillis() - startTs) / 1000;
                        System.out.println("Task " + taskId + ": No extract result yet (elapsed=" + elapsed + "s)");
                        continue;
                    }
                    Map<String, Object> extractResult = parseJsonResponse(result.getData());
                    System.out.println("Task " + taskId + ": Extract completed (result length=" + result.getData().length() + ")");
                    T extractedObject = objectMapper.convertValue(extractResult, options.getSchema());
                    return new ExtractResultTuple<>(true, extractedObject);
                }

                long elapsed = (System.currentTimeMillis() - startTs) / 1000;
                System.out.println("Task " + taskId + ": No extract result yet (elapsed=" + elapsed + "s)");
                if (elapsed >= timeoutSec) {
                    throw new BrowserException("Task " + taskId + ": Extract timeout after " + timeoutSec + "s");
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BrowserException("Extract task interrupted: " + e.getMessage());
        } catch (BrowserException e) {
            throw e;
        } catch (Exception e) {
            throw new BrowserException("Failed to parse extract response: " + e.getMessage());
        }
    }

    /**
     * Check if a poll response is the "pending" fallback from Session.extractTextContentFromData.
     * When MCP response has content=[], Session serializes the entire wrapper map as fallback,
     * returning something like '{"isError":false,"content":[]}'.
     */
    private boolean isPendingMcpResponse(String data) {
        if (data == null || data.isEmpty()) return true;
        try {
            Map<String, Object> parsed = parseJsonResponse(data);
            if (parsed.containsKey("isError") && parsed.containsKey("content")) {
                Object content = parsed.get("content");
                if (content instanceof List && ((List<?>) content).isEmpty()) {
                    return true;
                }
            }
        } catch (Exception e) {
            // If we can't parse it, it's not a pending response
        }
        return false;
    }


    /**
     * Tuple class to hold extract operation results.
     * 
     * @param <T> The type of extracted data
     */
    public static class ExtractResultTuple<T> {
        private final boolean success;
        private final T data;

        public ExtractResultTuple(boolean success, T data) {
            this.success = success;
            this.data = data;
        }

        public boolean isSuccess() { return success; }
        public T getData() { return data; }
    }

   /**
     * Observe elements or state on a web page asynchronously - matches Python observe (which uses observe_async internally).
     * Uses asynchronous execution with task polling.
     *
     * @param options Options to configure the observation behavior
     * @param page Playwright page object (null to use currently focused page)
     * @return ObserveResultTuple containing success status and list of observation results
     * @throws BrowserException if browser is not initialized or observation fails
     */
    public ObserveResultTuple observeAsync(ObserveOptions options, Page page) throws BrowserException {
        if (!browser.isInitialized()) {
            throw new BrowserException("Browser is not initialized");
        }

        try {
            PageContextIndex indices = getPageAndContextIndex(page);
            return executeObserveAsync(options, indices.contextIndex, indices.pageIndex);
        } catch (Exception e) {
            throw new BrowserException("Failed to observe async: " + e.getMessage());
        }
    }

    /**
     * Observe elements or state on a web page asynchronously without explicit Playwright Page.
     *
     * @param options Options to configure the observation behavior
     * @return ObserveResultTuple containing success status and list of observation results
     * @throws BrowserException if browser is not initialized or observation fails
     */
    public ObserveResultTuple observeAsync(ObserveOptions options) throws BrowserException {
        return observeAsync(options, null);
    }

    /**
     * Execute observe with async task polling - matches Python _execute_observe.
     *
     * @param options ObserveOptions containing instruction and parameters
     * @param contextId Browser context ID
     * @param pageId Page ID
     * @return ObserveResultTuple containing success status and results
     * @throws BrowserException if observation fails
     */
    private ObserveResultTuple executeObserveAsync(ObserveOptions options, int contextId, String pageId) throws BrowserException {
        Map<String, Object> args = new HashMap<>();
        args.put("context_id", contextId);
        if (pageId != null) args.put("page_id", pageId);
        args.putAll(options.toMap());
        args.values().removeIf(java.util.Objects::isNull);

        System.out.println("observeAsync: " + options.getInstruction());
        OperationResult response = callMcpToolTimeout("page_use_observe_async", args);
        if (!response.isSuccess()) {
            throw new BrowserException("Failed to start observe task: " + response.getErrorMessage());
        }

        try {
            Map<String, Object> responseData = parseJsonResponse(response.getData());
            String taskId = (String) responseData.get("task_id");
            if (taskId == null) {
                throw new BrowserException("No task_id in observe response: " + responseData);
            }

            int timeoutSec = 300;
            long startTs = System.currentTimeMillis();

            while (true) {
                Thread.sleep(3000);

                Map<String, Object> params = new HashMap<>();
                params.put("task_id", taskId);
                OperationResult result = callMcpToolTimeout("page_use_get_observe_result", params);

                if (result.isSuccess() && result.getData() != null && !result.getData().isEmpty()) {
                    if (isPendingMcpResponse(result.getData())) {
                        long elapsed = (System.currentTimeMillis() - startTs) / 1000;
                        System.out.println("Task " + taskId + ": No observe result yet (elapsed=" + elapsed + "s)");
                        continue;
                    }
                    ObserveResultTuple observeResult = parseObserveResult(result);
                    System.out.println("Task " + taskId + ": Observe completed (" +
                            (observeResult.getResults() != null ? observeResult.getResults().size() : 0) + " results)");
                    return observeResult;
                }

                long elapsed = (System.currentTimeMillis() - startTs) / 1000;
                System.out.println("Task " + taskId + ": No observe result yet (elapsed=" + elapsed + "s)");
                if (elapsed >= timeoutSec) {
                    throw new BrowserException("Task " + taskId + ": Observe timeout after " + timeoutSec + "s");
                }
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new BrowserException("Observe task interrupted: " + e.getMessage());
        } catch (BrowserException e) {
            throw e;
        } catch (Exception e) {
            throw new BrowserException("Failed to parse observe response: " + e.getMessage());
        }
    }

    /**
     * Call MCP tool with timeout - matches Python _call_mcp_tool_timeout method.
     * 
     * @param name Tool name
     * @param args Tool arguments
     * @return Operation result
     */
    private OperationResult callMcpToolTimeout(String name, Map<String, Object> args) {
        return callMcpTool(name, args);
    }

    // Convenience methods for common operations (matching existing functionality)

    /**
     * Navigate to a URL using act method.
     * 
     * @param page Playwright page object
     * @param url URL to navigate to
     * @return ActResult
     * @throws BrowserException if operation fails
     */
    public ActResult navigateTo(Page page, String url) throws BrowserException {
        return act(page, new ActOptions("goto('" + url + "')"));
    }

    /**
     * Click on an element using act method.
     * 
     * @param page Playwright page object
     * @param selector Element selector
     * @return ActResult
     * @throws BrowserException if operation fails
     */
    public ActResult click(Page page, String selector) throws BrowserException {
        return act(page, new ActOptions("click('" + selector + "')"));
    }

    /**
     * Type text into an input field using act method.
     * 
     * @param page Playwright page object
     * @param selector Input field selector
     * @param text Text to type
     * @return ActResult
     * @throws BrowserException if operation fails
     */
    public ActResult type(Page page, String selector, String text) throws BrowserException {
        return act(page, new ActOptions("fill('" + selector + "', '" + text + "')"));
    }

    /**
     * Take a screenshot using act method.
     * 
     * @param page Playwright page object
     * @return ActResult
     * @throws BrowserException if operation fails
     */
    public ActResult takeScreenshot(Page page) throws BrowserException {
        return act(page, new ActOptions("screenshot()"));
    }
}