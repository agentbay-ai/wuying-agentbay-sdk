package com.aliyun.agentbay.session;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.agent.Agent;
import com.aliyun.agentbay.browser.Browser;
import com.aliyun.agentbay.computer.Computer;
import com.aliyun.agentbay.mobile.Mobile;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.filesystem.FileSystem;
import com.aliyun.agentbay.git.Git;
import com.aliyun.agentbay.pty.Pty;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.oss.OSS;
import com.aliyun.agentbay.code.Code;
import com.aliyun.agentbay.command.Command;
import com.aliyun.agentbay.env.Env;
import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.mcp.McpToolsResult;
import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.wuyingai20250506.models.*;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.List;
import java.util.Map;

public class Session {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(Session.class);

    private final String sessionId;
    private final AgentBay agentBay;
    private Agent agent;
    private FileSystem fileSystem;
    private OSS oss;
    private Code code;
    private Command command;
    private ContextManager contextManager;
    private Browser browser;
    private Computer computer;
    public Mobile mobile;
    private Git git;
    private Pty pty;
    private Env env;
    private String fileTransferContextId;
    private String appInstanceId;
    private String resourceUrl;
    private String vpcIp;
    private String vpcId;
    private String token;
    private String linkUrl;
    private String wsUrl;
    private WsClient wsClient;
    private okhttp3.OkHttpClient linkHttpClient;
    private Boolean enableBrowserReplay;
    private String imageId;
    private List<McpTool> mcpTools = new java.util.ArrayList<>();

    /**
     * Creates a new Session instance.
     * 
     * <p>Initializes all service instances (Agent, FileSystem, OSS, Code, Command, 
     * ContextManager, Browser, Computer, Mobile) for this session.</p>
     * 
     * @param agentBay The AgentBay client instance
     * @param sessionId The unique identifier for this session
     */
    public Session(AgentBay agentBay, String sessionId) {
        this.sessionId = sessionId;
        this.agentBay = agentBay;
        this.agent = new Agent(this);
        this.fileSystem = new FileSystem(this);
        this.oss = new OSS(this);
        this.code = new Code(this);
        this.command = new Command(this);
        this.contextManager = new ContextManager(this);
        this.browser = new Browser(this);
        this.computer = new Computer(this);
        this.mobile = new Mobile(this);
        this.git = new Git(this);
        this.pty = new Pty(this);
        this.env = new Env(this);
        this.imageId = "";
        this.wsUrl = "";
        this.appInstanceId = "";
        this.vpcIp = "";
        this.vpcId = "";
    }

    /**
     * Get the application instance ID.
     *
     * @return The application instance ID
     */
    public String getAppInstanceId() {
        return appInstanceId;
    }

    /**
     * Set the application instance ID.
     *
     * @param appInstanceId The application instance ID
     */
    public void setAppInstanceId(String appInstanceId) {
        this.appInstanceId = appInstanceId;
    }

    /**
     * Get the VPC IP, populated when upstream returns it (VPC sessions).
     */
    public String getVpcIp() {
        return vpcIp;
    }

    public void setVpcIp(String vpcIp) {
        this.vpcIp = vpcIp;
    }

    /**
     * Get the VPC ID, populated when upstream returns it (VPC sessions).
     */
    public String getVpcId() {
        return vpcId;
    }

    public void setVpcId(String vpcId) {
        this.vpcId = vpcId;
    }

    public String getWsUrl() {
        return wsUrl;
    }

    public void setWsUrl(String wsUrl) {
        this.wsUrl = wsUrl;
    }

    /**
     * Internal: get or create a session-scoped WS client.
     * 
     * <p>This method is internal API by convention. The WS client is lazily initialized
     * and cached for the lifetime of this session. Callers are responsible for calling
     * connect() on the returned client if needed.</p>
     * 
     * @return The WsClient instance for this session
     * @throws RuntimeException if wsUrl or token is not available
     */
    public synchronized WsClient getWsClient() {
        if (this.wsUrl == null || this.wsUrl.trim().isEmpty()) {
            throw new RuntimeException("wsUrl is not available for this session");
        }
        if (this.token == null || this.token.trim().isEmpty()) {
            throw new RuntimeException("token is not available for WS connection");
        }
        if (this.wsClient == null) {
            this.wsClient = new WsClient(this.wsUrl, this.token);
        }
        return this.wsClient;
    }

    private synchronized okhttp3.OkHttpClient getLinkHttpClient() {
        if (this.linkHttpClient == null) {
            this.linkHttpClient = new okhttp3.OkHttpClient.Builder()
                .readTimeout(900, java.util.concurrent.TimeUnit.SECONDS)
                .writeTimeout(900, java.util.concurrent.TimeUnit.SECONDS)
                .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
                .build();
        }
        return this.linkHttpClient;
    }

    private void closeLinkHttpClient() {
        if (this.linkHttpClient != null) {
            this.linkHttpClient.connectionPool().evictAll();
            this.linkHttpClient.dispatcher().executorService().shutdown();
            this.linkHttpClient = null;
        }
    }

    /**
     * Creates a new Session instance with alternative parameter order.
     * 
     * <p>This constructor provides backward compatibility for code that uses
     * the (String, AgentBay) parameter order.</p>
     * 
     * @param sessionId The unique identifier for this session
     * @param agentBay The AgentBay client instance
     */
    public Session(String sessionId, AgentBay agentBay) {
        this(agentBay, sessionId);
    }

    /**
     * Get the session ID.
     *
     * @return The unique identifier for this session
     */
    public String getSessionId() {
        return sessionId;
    }

    /**
     * Get the Git service for this session.
     *
     * @return The Git service instance
     */
    public Git getGit() {
        return git;
    }

    public Pty getPty() {
        return pty;
    }

    /**
     * Get basic session status.
     *
     * <p>This method calls the GetSessionDetail API and returns status only.</p>
     *
     * @return SessionStatusResult containing session status information
     */
    public SessionStatusResult getStatus() {
        try {
            logger.debug("Calling GetSessionDetail API for session: {}", sessionId);
            
            GetSessionDetailRequest request = new GetSessionDetailRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            GetSessionDetailResponse response = agentBay.getClient().getSessionDetail(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new SessionStatusResult(requestId, 0, "", false, "", "Invalid response from GetSessionDetail API");
            }

            GetSessionDetailResponseBody body = response.getBody();
            Integer httpStatusCode = body.getHttpStatusCode() != null ? body.getHttpStatusCode() : 0;
            String code = body.getCode() != null ? body.getCode() : "";
            Boolean success = body.getSuccess() != null ? body.getSuccess() : false;
            String message = body.getMessage() != null ? body.getMessage() : "";

            if (requestId == null || requestId.isEmpty()) {
                requestId = body.getRequestId() != null ? body.getRequestId() : "";
            }

            if (!success && !code.isEmpty()) {
                String errorMessage = message != null && !message.isEmpty() ? message : "Unknown error";
                if (!code.isEmpty()) {
                    errorMessage = "[" + code + "] " + errorMessage;
                }
                return new SessionStatusResult(requestId, httpStatusCode, code, false, "", errorMessage);
            }

            String status = "";
            if (body.getData() != null) {
                GetSessionDetailResponseBody.GetSessionDetailResponseBodyData data = body.getData();
                logger.info("GetSessionDetail API call successful: {}", data);
                status = data.getStatus() != null ? data.getStatus() : "";
            }

            logger.debug("GetSessionDetail API response - RequestId: {}, Success: {}, Status: {}", 
                        requestId, success, status);

            return new SessionStatusResult(requestId, httpStatusCode, code, success, status, "");

        } catch (Exception e) {
            String errorStr = e.getMessage() != null ? e.getMessage() : e.toString();
            String errorCode = "";

            // Try to extract error code from TeaException
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaEx = (com.aliyun.tea.TeaException) e;
                if (teaEx.getData() != null && teaEx.getData().get("Code") != null) {
                    errorCode = teaEx.getData().get("Code").toString();
                }
            }

            // Check for NotFound error
            if (errorStr.contains("InvalidMcpSession.NotFound") || errorStr.contains("NotFound") ||
                "InvalidMcpSession.NotFound".equals(errorCode)) {
                logger.info("Session not found: {}", sessionId);
                logger.debug("GetSessionDetail error details: {}", errorStr);
                return new SessionStatusResult("", 400, errorCode.isEmpty() ? "InvalidMcpSession.NotFound" : errorCode, false, "",
                                              "Session " + sessionId + " not found");
            }

            logger.error("Error calling GetSessionDetail: {}", errorStr, e);
            return new SessionStatusResult("", 0, errorCode, false, "",
                                          "Failed to get session status " + sessionId + ": " + errorStr);
        }
    }

    /**
     * Refresh the backend idle timer for this session.
     *
     * <p>This method calls the RefreshSessionIdleTime API to prevent the session
     * from being automatically terminated due to inactivity.</p>
     *
     * @return OperationResult containing request ID and success status
     */
    public OperationResult keepAlive() {
        try {
            RefreshSessionIdleTimeRequest request = new RefreshSessionIdleTimeRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            RefreshSessionIdleTimeResponse response = agentBay.getClient().refreshSessionIdleTime(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new OperationResult(requestId, false, "", "Invalid response from RefreshSessionIdleTime API");
            }

            Boolean success = response.getBody().getSuccess();
            if (success == null || !success) {
                String code = response.getBody().getCode();
                String message = response.getBody().getMessage();
                String err = message != null && !message.isEmpty() ? message : "Unknown error";
                if (code != null && !code.isEmpty()) {
                    err = "[" + code + "] " + err;
                }
                return new OperationResult(requestId, false, "", err);
            }

            return new OperationResult(requestId, true, "", "");
        } catch (Exception e) {
            String errorCode = "";
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaEx = (com.aliyun.tea.TeaException) e;
                if (teaEx.getData() != null && teaEx.getData().get("Code") != null) {
                    errorCode = teaEx.getData().get("Code").toString();
                }
            }
            OperationResult result = new OperationResult("", false, "", "Failed to keep session alive: " + e.getMessage());
            result.setCode(errorCode);
            return result;
        }
    }

    /**
     * Get the AgentBay client.
     *
     * @return The AgentBay client instance associated with this session
     */
    public AgentBay getAgentBay() {
        return agentBay;
    }

    /**
     * Get the agent for this session.
     *
     * @return The Agent instance for AI-powered automation
     */
    public Agent getAgent() {
        return agent;
    }

    /**
     * Get the file system for this session.
     *
     * @return The FileSystem instance for file operations
     */
    public FileSystem getFileSystem() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides a shorthand way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem fs() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides an alternative way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem getFilesystem() {
        return fileSystem;
    }

    /**
     * Alias for fileSystem.
     * 
     * <p>Provides a shorthand way to access the file system service.</p>
     * 
     * @return The FileSystem instance
     */
    public FileSystem getFiles() {
        return fileSystem;
    }

    /**
     * Call an MCP tool (legacy method, returns raw API response).
     *
     * @param toolName Tool name
     * @param args Tool arguments
     * @return CallMcpToolResponse Raw API response
     * @throws AgentBayException if the call fails
     */
    public CallMcpToolResponse callTool(String toolName, Object args) throws AgentBayException {
        // Server name is optional for API-based tool calls.
        // Some environments do not return ToolList in CreateSession, and the backend
        // can resolve the server by tool name.
        String serverName = getMcpServerForTool(toolName);
        if (serverName == null || serverName.isEmpty()) {
            serverName = null;
        }
        return agentBay.getApiClient().callMcpTool(sessionId, toolName, args, serverName);
    }

    /**
     * Call an MCP tool and return structured OperationResult.
     * 
     * <p>This is the preferred method for calling MCP tools as it provides unified routing logic
     * (LinkUrl, VPC, API) and consistent error handling.</p>
     *
     * @param toolName Tool name
     * @param args Tool arguments
     * @return OperationResult containing parsed response with request ID, success status, and data
     */
    public OperationResult callMcpTool(String toolName, Object args) {
        try {
            String serverName = getMcpServerForTool(toolName);

            // LinkUrl route requires explicit server name. If it's not available,
            // fall back to API-based call to let backend resolve the server.
            if (isNotEmpty(linkUrl) && isNotEmpty(token) && isNotEmpty(serverName)) {
                return callMcpToolLinkUrl(toolName, args, serverName);
            }

            // Fall back to API route
            return callMcpToolApi(toolName, args, serverName);

        } catch (Exception e) {
            String errorCode = "";
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaEx = (com.aliyun.tea.TeaException) e;
                if (teaEx.getData() != null && teaEx.getData().get("Code") != null) {
                    errorCode = teaEx.getData().get("Code").toString();
                }
            }
            OperationResult result = new OperationResult("", false, "",
                "Failed to call MCP tool " + toolName + ": " + e.getMessage());
            result.setCode(errorCode);
            return result;
        }
    }

    /**
     * Checks if a string is not null and not empty.
     * 
     * @param str The string to check
     * @return true if the string is not null and not empty, false otherwise
     */
    private boolean isNotEmpty(String str) {
        return str != null && !str.isEmpty();
    }

    /**
     * Calls an MCP tool via the traditional API route.
     * 
     * This method makes an HTTP API call to invoke the MCP tool and returns
     * the result as an OperationResult. It handles response parsing, error checking,
     * and data extraction.
     * 
     * @param toolName The name of the MCP tool to call
     * @param args The arguments to pass to the tool
     * @param serverName The MCP server name (can be null for server-side resolution)
     * @return OperationResult containing the tool call result
     */
    private OperationResult callMcpToolApi(String toolName, Object args, String serverName) {
        try {
            if (serverName == null || serverName.isEmpty()) {
                serverName = null;
            }

            CallMcpToolResponse response = agentBay.getApiClient().callMcpTool(sessionId, toolName, args, serverName);

            if (response == null || response.getBody() == null) {
                return new OperationResult("", false, "", "No response from MCP tool");
            }

            String requestId = ResponseUtil.extractRequestId(response);
            Boolean success = response.getBody().getSuccess();

            if (success == null || !success) {
                String errorMessage = response.getBody().getMessage();
                return new OperationResult(requestId, false, "",
                    errorMessage != null ? errorMessage : "MCP tool call failed");
            }

            Object data = response.getBody().getData();
            if (data == null) {
                return new OperationResult(requestId, false, "", "No data in response");
            }

            String jsonData;
            if (data instanceof String) {
                jsonData = (String) data;
            } else {
                jsonData = objectMapper.writeValueAsString(data);
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> dataMap = objectMapper.readValue(jsonData, Map.class);

            Boolean isError = (Boolean) dataMap.get("isError");
            if (isError != null && isError) {
                String errorMessage = extractErrorMessageFromContent(dataMap);
                return new OperationResult(requestId, false, "", errorMessage);
            }

            String textContent = extractTextContentFromData(dataMap);
            return new OperationResult(requestId, true, textContent, "");

        } catch (Exception e) {
            String errorCode = "";
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaEx = (com.aliyun.tea.TeaException) e;
                if (teaEx.getData() != null && teaEx.getData().get("Code") != null) {
                    errorCode = teaEx.getData().get("Code").toString();
                }
            }
            OperationResult result = new OperationResult("", false, "",
                "Failed to call MCP tool via API: " + e.getMessage());
            result.setCode(errorCode);
            return result;
        }
    }

    /**
     * Calls an MCP tool via the LinkUrl route (VPC mode).
     * 
     * This method makes a direct HTTP call to the LinkUrl endpoint for faster
     * tool execution in VPC environments. It requires both token and linkUrl to be set.
     * 
     * @param toolName The name of the MCP tool to call
     * @param args The arguments to pass to the tool
     * @param serverName The MCP server name (required for LinkUrl route)
     * @return OperationResult containing the tool call result
     */
    private OperationResult callMcpToolLinkUrl(String toolName, Object args, String serverName) {
        try {
            if (!isNotEmpty(serverName)) {
                return new OperationResult("", false, "",
                    "Server name is required for LinkUrl tool call: " + toolName);
            }

            String requestId = String.format("link-%d-%09d",
                System.currentTimeMillis(),
                new java.util.Random().nextInt(1000000000));

            if (!isNotEmpty(linkUrl) || !isNotEmpty(token)) {
                return new OperationResult(requestId, false, "", "LinkUrl/token not available");
            }

            String url = linkUrl.endsWith("/") ? linkUrl + "callTool" : linkUrl + "/callTool";

            Map<String, Object> bodyParams = new java.util.HashMap<>();
            bodyParams.put("args", args);
            bodyParams.put("server", serverName);
            bodyParams.put("requestId", requestId);
            bodyParams.put("tool", toolName);
            bodyParams.put("token", token);
            String bodyJson = objectMapper.writeValueAsString(bodyParams);

            okhttp3.RequestBody requestBody = okhttp3.RequestBody.create(
                bodyJson,
                okhttp3.MediaType.parse("application/json")
            );

            okhttp3.OkHttpClient httpClient = getLinkHttpClient();

            okhttp3.Request request = new okhttp3.Request.Builder()
                .url(url)
                .header("Content-Type", "application/json")
                .header("X-Access-Token", token)
                .post(requestBody)
                .build();

            try (okhttp3.Response response = httpClient.newCall(request).execute()) {
                if (!response.isSuccessful()) {
                    String respBody = "";
                    try {
                        if (response.body() != null) {
                            respBody = response.body().string();
                        }
                    } catch (Exception ignored) {
                    }
                    logger.error("❌ API Response Failed: CallMcpTool(LinkUrl) Response, RequestId={}", requestId);
                    logger.error("📥 Response: {}", respBody);
                    return new OperationResult(requestId, false, "",
                        "HTTP request failed with code: " + response.code());
                }

                String responseBody = response.body() != null ? response.body().string() : "";
                @SuppressWarnings("unchecked")
                Map<String, Object> outerData = objectMapper.readValue(responseBody, Map.class);

                Object dataField = outerData.get("data");
                if (dataField == null) {
                    return new OperationResult(requestId, false, "", "No data field in LinkUrl response");
                }

                Map<String, Object> parsedData;
                if (dataField instanceof String) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> parsed = objectMapper.readValue((String) dataField, Map.class);
                    parsedData = parsed;
                } else if (dataField instanceof Map) {
                    @SuppressWarnings("unchecked")
                    Map<String, Object> casted = (Map<String, Object>) dataField;
                    parsedData = casted;
                } else {
                    return new OperationResult(requestId, false, "",
                        "Invalid data field type in LinkUrl response");
                }

                Object resultField = parsedData.get("result");
                if (!(resultField instanceof Map)) {
                    return new OperationResult(requestId, false, "",
                        "No result field in LinkUrl response data");
                }

                @SuppressWarnings("unchecked")
                Map<String, Object> resultData = (Map<String, Object>) resultField;
                Boolean isError = (Boolean) resultData.get("isError");
                String textContent = extractTextContentFromData(resultData);

                if (isError != null && isError) {
                    return new OperationResult(requestId, false, "", textContent);
                }
                return new OperationResult(requestId, true, textContent, "");
            }
        } catch (java.io.IOException e) {
            return new OperationResult("", false, "", "HTTP request failed: " + e.getMessage());
        } catch (Exception e) {
            return new OperationResult("", false, "", "Unexpected error in LinkUrl call: " + e.getMessage());
        }
    }

    /**
     * Extracts error message from the content field of an MCP tool response.
     * 
     * @param dataMap The response data map
     * @return The extracted error message, or a default error message if not found
     */
    private String extractErrorMessageFromContent(Map<String, Object> dataMap) {
        Object content = dataMap.get("content");
        if (content instanceof java.util.List && !((java.util.List<?>) content).isEmpty()) {
            Object firstContent = ((java.util.List<?>) content).get(0);
            if (firstContent instanceof Map) {
                Object text = ((Map<?, ?>) firstContent).get("text");
                if (text != null) {
                    return text.toString();
                }
            }
        }
        return "MCP tool execution error";
    }

    /**
     * Extracts text content from the data field of an MCP tool response.
     * 
     * This method looks for text, blob, or data fields in the content array
     * and returns the first non-null value found.
     * 
     * @param dataMap The response data map
     * @return The extracted text content as a string
     */
    private String extractTextContentFromData(Map<String, Object> dataMap) {
        Object content = dataMap.get("content");
        if (content instanceof java.util.List && !((java.util.List<?>) content).isEmpty()) {
            Object firstContent = ((java.util.List<?>) content).get(0);
            if (firstContent instanceof Map) {
                Map<?, ?> contentMap = (Map<?, ?>) firstContent;
                Object text = contentMap.get("text");
                if (text != null) {
                    return text.toString();
                }
                Object blob = contentMap.get("blob");
                if (blob != null) {
                    return blob.toString();
                }
                Object data = contentMap.get("data");
                if (data != null) {
                    return data.toString();
                }
            }
        }
        try {
            return objectMapper.writeValueAsString(dataMap);
        } catch (Exception e) {
            return dataMap.toString();
        }
    }

    /**
     * List available tools
     *
     * @return List of available tools
     * @throws AgentBayException if the call fails
     */  
    private List<Object> listTools() throws AgentBayException {
        String img = imageId;
        if (img == null || img.isEmpty()) {
            img = "linux_latest";
        }
        ListMcpToolsResponse response = agentBay.getApiClient().listMcpTools(img);

        if (response != null && response.getBody() != null && response.getBody().getData() != null) {
            try {
                String dataJson = response.getBody().getData().toString();
                List<Object> toolsList = objectMapper.readValue(dataJson, List.class);
                return toolsList;
            } catch (Exception e) {
                throw new AgentBayException("Failed to parse tools data", e);
            }
        }
        return new java.util.ArrayList<>();
    }

    /**
     * Get runtime metrics for this session via the MCP get_metrics tool.
     *
     * The underlying MCP tool returns a JSON string. This method parses it and returns structured metrics.
     *
     * @return SessionMetricsResult containing structured metrics data
     */
    public SessionMetricsResult getMetrics() {
        try {
            OperationResult result = callMcpTool("get_metrics", new java.util.HashMap<>());

            if (!result.isSuccess()) {
                return new SessionMetricsResult(result.getRequestId(), false, null, result.getErrorMessage());
            }

            @SuppressWarnings("unchecked")
            Map<String, Object> raw = objectMapper.readValue(result.getData(), Map.class);

            SessionMetrics metrics = parseMetrics(raw);
            return new SessionMetricsResult(result.getRequestId(), true, metrics, "", raw);

        } catch (Exception e) {
            String errorCode = "";
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaEx = (com.aliyun.tea.TeaException) e;
                if (teaEx.getData() != null && teaEx.getData().get("Code") != null) {
                    errorCode = teaEx.getData().get("Code").toString();
                }
            }
            SessionMetricsResult result = new SessionMetricsResult("", false, null,
                "Failed to get metrics: " + e.getMessage());
            return result;
        }
    }

    /**
     * Parses raw metrics data from the MCP get_metrics tool response.
     * 
     * This method extracts various metrics including CPU, memory, disk, and network
     * statistics from the raw data map and populates a SessionMetrics object.
     * 
     * @param raw The raw metrics data map from the MCP tool response
     * @return A populated SessionMetrics object
     */
    private SessionMetrics parseMetrics(Map<String, Object> raw) {
        SessionMetrics metrics = new SessionMetrics();
        metrics.setCpuCount(getIntValue(raw, "cpu_count"));
        metrics.setCpuUsedPct(getDoubleValue(raw, "cpu_used_pct"));
        metrics.setDiskTotal(getLongValue(raw, "disk_total"));
        metrics.setDiskUsed(getLongValue(raw, "disk_used"));
        metrics.setMemTotal(getLongValue(raw, "mem_total"));
        metrics.setMemUsed(getLongValue(raw, "mem_used"));

        metrics.setRxRateKBps(getDoubleValueWithFallback(raw,
            "rx_rate_kbyte_per_s", "rx_rate_kbps", "rx_rate_KBps"));
        metrics.setTxRateKBps(getDoubleValueWithFallback(raw,
            "tx_rate_kbyte_per_s", "tx_rate_kbps", "tx_rate_KBps"));
        metrics.setRxUsedKB(getDoubleValueWithFallback(raw,
            "rx_used_kbyte", "rx_used_kb", "rx_used_KB"));
        metrics.setTxUsedKB(getDoubleValueWithFallback(raw,
            "tx_used_kbyte", "tx_used_kb", "tx_used_KB"));

        metrics.setTimestamp(getStringValue(raw, "timestamp"));
        return metrics;
    }

    /**
     * Gets a double value from a map with fallback keys.
     * 
     * Tries each key in order until a non-null value is found, then converts it to double.
     * 
     * @param map The map to search
     * @param keys The keys to try in order
     * @return The first non-null value converted to double, or 0.0 if none found
     */
    private double getDoubleValueWithFallback(Map<String, Object> map, String... keys) {
        for (String key : keys) {
            Object value = map.get(key);
            if (value != null) {
                if (value instanceof Number) {
                    return ((Number) value).doubleValue();
                }
                try {
                    return Double.parseDouble(value.toString());
                } catch (NumberFormatException e) {
                    // Try next key
                }
            }
        }
        return 0.0;
    }

    /**
     * Gets an integer value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The integer value, or 0 if not found or conversion fails
     */
    private int getIntValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0;
        if (value instanceof Number) {
            return ((Number) value).intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException e) {
            return 0;
        }
    }

    /**
     * Gets a long value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The long value, or 0L if not found or conversion fails
     */
    private long getLongValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0L;
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(value.toString());
        } catch (NumberFormatException e) {
            return 0L;
        }
    }

    /**
     * Gets a double value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The double value, or 0.0 if not found or conversion fails
     */
    private double getDoubleValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        if (value == null) return 0.0;
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return Double.parseDouble(value.toString());
        } catch (NumberFormatException e) {
            return 0.0;
        }
    }

    /**
     * Gets a string value from a map.
     * 
     * @param map The map to search
     * @param key The key to look up
     * @return The string value, or empty string if not found
     */
    private String getStringValue(Map<String, Object> map, String key) {
        Object value = map.get(key);
        return value != null ? value.toString() : "";
    }

    /**
     * Gets information about this session
     *
     * @return SessionInfoResult containing SessionInfo and request ID
     * @throws AgentBayException if the operation fails
     */
    public SessionInfoResult info() throws AgentBayException {
        try {
            GetMcpResourceRequest request = new GetMcpResourceRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);
            GetMcpResourceResponse response = agentBay.getApiClient().getClient().getMcpResource(request);

            String requestId = ResponseUtil.extractRequestId(response);

            if (response.getBody() != null && response.getBody().getData() != null) {
                // Extract session info from response data
                GetMcpResourceResponseBody.GetMcpResourceResponseBodyData data = response.getBody().getData();

                SessionInfo sessionInfo = new SessionInfo();

                // Set session ID
                if (data.getSessionId() != null) {
                    sessionInfo.setSessionId(data.getSessionId());
                }

                // Set resource URL
                if (data.getResourceUrl() != null) {
                    sessionInfo.setResourceUrl(data.getResourceUrl());
                }

                // Transfer DesktopInfo fields to SessionInfo
                if (data.getDesktopInfo() != null) {
                    GetMcpResourceResponseBody.GetMcpResourceResponseBodyDataDesktopInfo desktopInfo = data.getDesktopInfo();

                    if (desktopInfo.getAppId() != null) {
                        sessionInfo.setAppId(desktopInfo.getAppId());
                    }
                    if (desktopInfo.getAuthCode() != null) {
                        sessionInfo.setAuthCode(desktopInfo.getAuthCode());
                    }
                    if (desktopInfo.getConnectionProperties() != null) {
                        sessionInfo.setConnectionProperties(desktopInfo.getConnectionProperties());
                    }
                    if (desktopInfo.getResourceId() != null) {
                        sessionInfo.setResourceId(desktopInfo.getResourceId());
                    }
                    if (desktopInfo.getResourceType() != null) {
                        sessionInfo.setResourceType(desktopInfo.getResourceType());
                    }
                    if (desktopInfo.getTicket() != null) {
                        sessionInfo.setTicket(desktopInfo.getTicket());
                    }
                }

                return new SessionInfoResult(requestId, true, sessionInfo, "");
            } else {
                return new SessionInfoResult(requestId, false, null, "No session data found");
            }

        } catch (Exception e) {
            throw new AgentBayException("Failed to get session info for session " + sessionId + ": " + e.getMessage(), e);
        }
    }

    /**
     * Get the OSS service for this session
     *
     * @return OSS instance
     */
    public OSS getOss() {
        return oss;
    }

    /**
     * Get the Code service for this session
     *
     * @return Code instance
     */
    public Code getCode() {
        return code;
    }

    /**
     * Get the Command service for this session
     *
     * @return Command instance
     */
    public Command getCommand() {
        return command;
    }

    /**
     * Get the context manager for this session
     *
     * @return ContextManager instance
     */
    public ContextManager getContext() {
        return contextManager;
    }

    /**
     * Get the browser service for this session
     *
     * @return Browser instance
     */
    public Browser getBrowser() {
        return browser;
    }

    /**
     * Get the computer service for this session
     *
     * @return Computer instance
     */
    public Computer getComputer() {
        return computer;
    }

    /**
     * Get the mobile service for this session
     *
     * @return Mobile instance
     */
    public Mobile getMobile() {
        return mobile;
    }

    /**
     * Get the environment variable service for this session
     *
     * @return Env instance
     */
    public Env getEnv() {
        return env;
    }

    /**
     * Get the file transfer context ID for this session
     *
     * @return File transfer context ID
     */
    public String getFileTransferContextId() {
        return fileTransferContextId;
    }

    /**
     * Set the file transfer context ID for this session
     *
     * @param fileTransferContextId File transfer context ID
     */
    public void setFileTransferContextId(String fileTransferContextId) {
        this.fileTransferContextId = fileTransferContextId;
    }

    /**
     * Get the API key for this session
     *
     * @return API key
     */
    public String getApiKey() {
        return agentBay.getApiKey();
    }

    /**
     * Lists all available MCP tools for this session.
     * 
     * This method retrieves the list of MCP tools that can be called in this session,including their names, descriptions, input schemas, and server information.
     * 
     * @return McpToolsResult containing the list of available tools
     */
    public McpToolsResult listMcpTools() {
        try {
            List<Object> toolsData = listTools();
            McpToolsResult result = new McpToolsResult();
            result.setSuccess(true);

            java.util.List<com.aliyun.agentbay.mcp.McpTool> tools = new java.util.ArrayList<>();
            if (toolsData != null) {
                for (Object toolData : toolsData) {
                    try {
                        if (toolData instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = (Map<String, Object>) toolData;

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        } else if (toolData instanceof String) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = objectMapper.readValue((String) toolData, Map.class);

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) toolMap.get("name"));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            tool.setServer((String) toolMap.get("server"));
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        }
                    } catch (Exception e) {
                    }
                }
            }

            result.setTools(tools);
            return result;
        } catch (AgentBayException e) {
            McpToolsResult result = new McpToolsResult();
            result.setSuccess(false);
            result.setErrorMessage(e.getMessage());
            return result;
        }
    }

    /**
     * Sets the image ID for this session.
     * This is used to specify the base image for the session environment.
     * 
     * @param imageId The image ID to set
     */
    public void setImageId(String imageId) {
        this.imageId = imageId;
    }

    /**
     * Gets the image ID for this session.
     * 
     * @return The image ID, or empty string if not set
     */
    public String getImageId() {
        return imageId;
    }

    /**
     * Gets the enableBrowserReplay flag.
     * This flag determines whether browser recording is enabled for this session.
     * 
     * @return true if browser replay is enabled, false otherwise
     */
    public Boolean getEnableBrowserReplay() {
        return enableBrowserReplay;
    }

    /**
     * Sets the enableBrowserReplay flag.
     * This flag determines whether browser recording is enabled for this session.
     * 
     * @param enableBrowserReplay true to enable browser replay, false to disable
     */
    public void setEnableBrowserReplay(Boolean enableBrowserReplay) {
        this.enableBrowserReplay = enableBrowserReplay;
    }

    /**
     * Get the resource URL for accessing the session
     *
     * @return Resource URL
     */
    public String getResourceUrl() {
        return resourceUrl;
    }

    /**
     * Set the resource URL for accessing the session
     *
     * @param resourceUrl Resource URL
     */
    public void setResourceUrl(String resourceUrl) {
        this.resourceUrl = resourceUrl;
    }

    /**
     * @deprecated Internal SDK use only. Will be removed in a future version.
     */
    @Deprecated
    public String getToken() {
        return token;
    }

    /**
     * Sets the token for LinkUrl tool calls.
     * This token is used for authentication when calling MCP tools via the LinkUrl route.
     * 
     * @param token The authentication token to set
     */
    public void setToken(String token) {
        this.token = token;
    }

    /**
     * @deprecated Internal SDK use only. Will be removed in a future version.
     */
    @Deprecated
    public String getLinkUrl() {
        return linkUrl == null ? "" : linkUrl;
    }

    /**
     * Sets the LinkUrl for direct tool calls.
     * This URL is used for calling MCP tools via the LinkUrl route in VPC environments.
     * 
     * @param linkUrl The LinkUrl to set
     */
    public void setLinkUrl(String linkUrl) {
        this.linkUrl = linkUrl == null ? "" : linkUrl;
    }

    /**
     * Helper method to parse inputSchema which can be a Map, String, or null
     *
     * @param inputSchemaObj The inputSchema object from the tool data
     * @return A Map representing the inputSchema, or an empty Map if parsing fails
     */
    private Map<String, Object> parseInputSchema(Object inputSchemaObj) {
        if (inputSchemaObj == null) {
            return new java.util.HashMap<>();
        }
        
        // If it's already a Map, return it
        if (inputSchemaObj instanceof Map) {
            @SuppressWarnings("unchecked")
            Map<String, Object> schemaMap = (Map<String, Object>) inputSchemaObj;
            return schemaMap;
        }
        
        // If it's a String, try to parse it as JSON
        if (inputSchemaObj instanceof String) {
            String schemaStr = (String) inputSchemaObj;
            if (schemaStr.isEmpty()) {
                return new java.util.HashMap<>();
            }
            try {
                @SuppressWarnings("unchecked")
                Map<String, Object> schemaMap = objectMapper.readValue(schemaStr, Map.class);
                return schemaMap;
            } catch (JsonProcessingException e) {
                logger.warn("Failed to parse inputSchema string as JSON: {}", schemaStr, e);
                return new java.util.HashMap<>();
            }
        }
        
        // For any other type, return empty map
        logger.warn("Unexpected inputSchema type: {}", inputSchemaObj.getClass().getName());
        return new java.util.HashMap<>();
    }

    /**
     * Updates the MCP tools list for this session.
     *
     * Accepts either a JSON string or an already-parsed List of tool definitions.
     * Handles both Map and String representations of tool data.
     *
     * @param toolListData JSON string or List containing the tool definitions
     */
    @SuppressWarnings("unchecked")
    public void updateMcpTools(Object toolListData) {
        try {
            List<Object> toolsData;
            if (toolListData instanceof String) {
                toolsData = objectMapper.readValue((String) toolListData, List.class);
            } else if (toolListData instanceof List) {
                toolsData = (List<Object>) toolListData;
            } else {
                String json = objectMapper.writeValueAsString(toolListData);
                toolsData = objectMapper.readValue(json, List.class);
            }

            java.util.List<com.aliyun.agentbay.mcp.McpTool> tools = new java.util.ArrayList<>();
            if (toolsData != null) {
                for (Object toolData : toolsData) {
                    try {
                        if (toolData instanceof Map) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = (Map<String, Object>) toolData;

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) (toolMap.get("name") != null ? toolMap.get("name") : toolMap.get("Name")));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            Object server = toolMap.get("server");
                            if (server == null) {
                                server = toolMap.get("serverName");
                            }
                            if (server == null) {
                                server = toolMap.get("Server");
                            }
                            tool.setServer((String) server);
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        } else if (toolData instanceof String) {
                            @SuppressWarnings("unchecked")
                            Map<String, Object> toolMap = objectMapper.readValue((String) toolData, Map.class);

                            com.aliyun.agentbay.mcp.McpTool tool = new com.aliyun.agentbay.mcp.McpTool();
                            tool.setName((String) (toolMap.get("name") != null ? toolMap.get("name") : toolMap.get("Name")));
                            tool.setDescription((String) toolMap.get("description"));
                            
                            // Handle inputSchema - it can be a Map, String, or null
                            Map<String, Object> inputSchema = parseInputSchema(toolMap.get("inputSchema"));
                            tool.setInputSchema(inputSchema);
                            
                            Object server = toolMap.get("server");
                            if (server == null) {
                                server = toolMap.get("serverName");
                            }
                            if (server == null) {
                                server = toolMap.get("Server");
                            }
                            tool.setServer((String) server);
                            tool.setTool((String) toolMap.get("tool"));
                            tools.add(tool);
                        }
                    } catch (Exception e) {
                        logger.warn("Failed to parse tool data: {}", toolData, e);
                    }
                }
            }

            this.mcpTools = tools;

        } catch (JsonProcessingException e) {
            throw new RuntimeException(e);
        }
    }

    /**
     * Gets the list of MCP tools available for this session.
     * 
     * @return List of McpTool instances
     */
    public List<McpTool> getMcpTools() {
        return mcpTools;
    }

    /**
     * Sets the list of MCP tools for this session.
     * 
     * @param mcpTools The list of McpTool instances to set
     */
    public void setMcpTools(List<McpTool> mcpTools) {
        this.mcpTools = mcpTools != null ? mcpTools : new java.util.ArrayList<>();
    }

    /**
     * Gets the MCP server name for a specific tool.
     * 
     * This method searches through the available MCP tools to find the server that provides the specified tool.
     * 
     * @param toolName The name of the tool to look up
     * @return The server name, or empty string if not found
     */
    public String getMcpServerForTool(String toolName) {
        if (toolName == null || toolName.isEmpty()) {
            return "";
        }
        for (McpTool tool : mcpTools) {
            if (tool != null && toolName.equals(tool.getName())) {
                String server = tool.getServer();
                if (server != null && !server.isEmpty()) {
                    return server;
                }
            }
        }
        return "";
    }

    /**
     * Gets a connection link for the current session with specified parameters.
     * 
     * This method generates a connection URL that can be used to access the session via the specified protocol and port.
     * 
     * @param protocolType The protocol type to use for the link (e.g., "https")
     * @param port The port number to use for the connection (default open range: [30100, 30199]; other ports require whitelist approval via agentbay_dev@alibabacloud.com)
     * @return OperationResult containing the connection link URL
     * @throws AgentBayException if the request fails
     */
    public OperationResult getLink(String protocolType, Integer port) throws AgentBayException {
        try {
            GetLinkRequest request = new GetLinkRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);
            if (protocolType != null) {
                request.setProtocolType(protocolType);
            }
            if (port != null) {
                request.setPort(port);
            }

            GetLinkResponse response = agentBay.getClient().getLink(request);
            String requestId = ResponseUtil.extractRequestId(response);

            if (response != null && response.getBody() != null && response.getBody().getData() != null) {
                String url = response.getBody().getData().getUrl();
                return new OperationResult(requestId, true, url, "");
            } else {
                return new OperationResult(requestId, false, "", "No URL in response");
            }
        } catch (Exception e) {
            throw new AgentBayException("Failed to get link: " + e.getMessage(), e);
        }
    }

    /**
     * Gets a connection link for the current session with default parameters.
     * 
     * This method generates a connection URL using the default protocol and port.
     * 
     * @return OperationResult containing the connection link URL
     * @throws AgentBayException if the request fails
     */
    public OperationResult getLink() throws AgentBayException {
        return getLink(null, null);
    }


    /**
     * Deletes this session and releases all associated resources.
     * 
     * <p>Context synchronization is not performed before deletion.</p>
     * 
     * @return DeleteResult containing the deletion result
     */
    public DeleteResult delete() {
        return delete(false);
    }

    /**
     * Check if an error message indicates the session is already released/dead.
     * "no alive session found" means the session was already released by the server
     * (e.g., due to idle timeout), which is effectively a successful deletion.
     *
     * @param message The error message to check
     * @return true if the message indicates session is already released
     */
    private boolean isSessionAlreadyReleased(String message) {
        if (message == null) {
            return false;
        }
        String lower = message.toLowerCase();
        return lower.contains("no alive session")
            || lower.contains("no need to release");
    }

    /**
     * Deletes this session with optional context synchronization.
     * 
     * <p>This method uses the DeleteSessionAsync API to release cloud resources.
     * If syncContext is true, it will first synchronize the context (trigger file uploads)
     * before deleting the session. After initiating deletion, it polls the session status
     * until the session is confirmed deleted (NotFound or FINISH) or timeout.</p>
     * 
     * @param syncContext Whether to synchronize context before deletion
     * @return DeleteResult containing the deletion result
     */
    public DeleteResult delete(boolean syncContext) {
        try {
            // Perform context synchronization if needed
            if (syncContext) {
                long syncStartTime = System.currentTimeMillis();

                try {
                    ContextSyncResult syncResult = contextManager.sync();
                    long syncDuration = System.currentTimeMillis() - syncStartTime;
                } catch (Exception e) {
                    long syncDuration = System.currentTimeMillis() - syncStartTime;
                    logger.warn("Failed to trigger context sync after {}ms: {}", syncDuration, e.getMessage());
                    // Continue with deletion even if sync fails
                }
            }

            // Proceed with session deletion using DeleteSessionAsync API
            DeleteSessionAsyncRequest request = new DeleteSessionAsyncRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            DeleteSessionAsyncResponse response;
            String requestId;
            try {
                response = agentBay.getClient().deleteSessionAsync(request);
                requestId = ResponseUtil.extractRequestId(response);
            } catch (Exception deleteEx) {
                // Check if the exception indicates session is already gone
                String deleteErrorStr = deleteEx.getMessage() != null ? deleteEx.getMessage() : deleteEx.toString();
                if (isSessionAlreadyReleased(deleteErrorStr)) {
                    logger.info("Session {} already released during delete call: {}", sessionId, deleteErrorStr);
                    return new DeleteResult("", true, "");
                }
                throw deleteEx; // Re-throw for outer catch to handle
            }

            // Check if the response is successful
            if (response != null && response.getBody() != null) {
                Boolean success = response.getBody().getSuccess();
                if (success != null && !success) {
                    String code = response.getBody().getCode() != null ? response.getBody().getCode() : "Unknown";
                    String message = response.getBody().getMessage() != null 
                        ? response.getBody().getMessage() : "Failed to delete session";
                    // Check if response indicates session is already released
                    if (isSessionAlreadyReleased(message)) {
                        logger.info("Session {} already released: {}", sessionId, message);
                        return new DeleteResult(requestId, true, "");
                    }
                    String errorMessage = "[" + code + "] " + message;
                    return new DeleteResult(requestId, false, errorMessage);
                }
            }

            // Poll for session deletion status
            long pollTimeout = 300_000L; // 5 minutes in milliseconds
            long pollInterval = 1_000L;  // 1 second
            long pollStartTime = System.currentTimeMillis();

            while (true) {
                // Check timeout
                long elapsedTime = System.currentTimeMillis() - pollStartTime;
                if (elapsedTime >= pollTimeout) {
                    String errorMessage = "Timeout waiting for session deletion after " + (pollTimeout / 1000) + "s";
                    return new DeleteResult(requestId, false, errorMessage);
                }

                // Get session status
                SessionStatusResult sessionResult = getStatus();

                // Check if session is deleted (NotFound error)
                if (!sessionResult.isSuccess()) {
                    String errorCode = sessionResult.getCode() != null ? sessionResult.getCode() : "";
                    String errorMessage = sessionResult.getErrorMessage() != null ? sessionResult.getErrorMessage() : "";
                    int httpStatusCode = sessionResult.getHttpStatusCode();

                    // Check for InvalidMcpSession.NotFound, 400 with "not found", or error_message containing "not found"
                    boolean isNotFound = "InvalidMcpSession.NotFound".equals(errorCode)
                        || (httpStatusCode == 400 && (
                            errorMessage.toLowerCase().contains("not found")
                            || errorCode.contains("NotFound")))
                        || errorMessage.toLowerCase().contains("not found");

                    if (isNotFound) {
                        // Session is deleted
                        logger.info("Session {} successfully deleted (NotFound)", sessionId);
                        break;
                    }
                } else if (sessionResult.getStatus() != null && !sessionResult.getStatus().isEmpty()) {
                    // Check session status if we got valid data
                    String status = sessionResult.getStatus();
                    if ("FINISH".equals(status)) {
                        break;
                    }
                }

                // Wait before next poll
                try {
                    Thread.sleep(pollInterval);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return new DeleteResult(requestId, false, 
                        "Delete operation interrupted");
                }
            }

            // Return success result
            return new DeleteResult(requestId, true, "");

        } catch (Exception e) {
            return new DeleteResult(
                "", false, "Failed to delete session " + sessionId + ": " + e.getMessage());
        } finally {
            // Clean up WS client
            WsClient ws = this.wsClient;
            this.wsClient = null;
            if (ws != null) {
                try {
                    ws.close();
                } catch (Exception ignored) {
                }
            }
            // Clean up link HTTP client
            try {
                closeLinkHttpClient();
            } catch (Exception ignored) {
            }
        }
    }

    /**
     * Sets labels for this session.
     * 
     * Labels are key-value pairs that can be used to organize and filter sessions.
     * All keys and values must be non-empty strings.
     * 
     * @param labels Map of label key-value pairs to set
     * @return OperationResult indicating success or failure
     * @throws AgentBayException if the API call fails or validation fails
     * @throws IllegalArgumentException if labels are null or contain invalid keys/values
     */
    public OperationResult setLabels(Map<String, String> labels) throws AgentBayException {
        try {
            // Validate labels
            if (labels == null) {
                throw new IllegalArgumentException("Labels cannot be null");
            }

            // Validate label keys and values
            for (Map.Entry<String, String> entry : labels.entrySet()) {
                String key = entry.getKey();
                String value = entry.getValue();

                if (key == null || key.trim().isEmpty()) {
                    throw new IllegalArgumentException("Label key cannot be null or empty");
                }
                if (value == null || value.trim().isEmpty()) {
                    throw new IllegalArgumentException("Label value cannot be null or empty");
                }
            }

            // Convert labels to JSON string
            String labelsJson = objectMapper.writeValueAsString(labels);

            // Create request
            SetLabelRequest request = new SetLabelRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);
            request.setLabels(labelsJson);

            // Call API
            SetLabelResponse response = agentBay.getClient().setLabel(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);
            return new OperationResult(requestId, true, labelsJson, "");

        } catch (IllegalArgumentException e) {
            throw new AgentBayException("Invalid labels: " + e.getMessage(), e);
        } catch (Exception e) {
            throw new AgentBayException("Failed to set labels: " + e.getMessage(), e);
        }
    }

    /**
     * Gets the labels for this session.
     * 
     * This method retrieves all labels that have been set for this session.
     * 
     * @return OperationResult containing the labels map as JSON string in the data field
     * @throws AgentBayException if the API call fails
     */
    public OperationResult getLabels() throws AgentBayException {
        try {
            // Create request
            GetLabelRequest request = new GetLabelRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(sessionId);

            // Call API
            GetLabelResponse response = agentBay.getClient().getLabel(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);

            // Extract labels from response
            Map<String, Object> responseMap = response.toMap();
            Map<String, Object> body = (Map<String, Object>) responseMap.get("body");
            Map<String, Object> data = body != null ? (Map<String, Object>) body.get("Data") : null;
            String labelsJson = data != null ? (String) data.get("Labels") : null;

            Map<String, String> labels = new java.util.HashMap<>();
            if (labelsJson != null && !labelsJson.isEmpty()) {
                labels = objectMapper.readValue(labelsJson,
                    objectMapper.getTypeFactory().constructMapType(Map.class, String.class, String.class));
            }

            String labelsJsonResult = objectMapper.writeValueAsString(labels);
            return new OperationResult(requestId, true, labelsJsonResult, "");

        } catch (Exception e) {
            throw new AgentBayException("Failed to get labels: " + e.getMessage(), e);
        }
    }

    /**
     * Pauses this session (beta feature).
     * 
     * This method sends a pause request to the backend and polls the session status
     * until it reaches the PAUSED state or times out.
     * 
     * @param timeout Maximum time to wait for pause completion in seconds (default: 600)
     * @param pollInterval Interval between status checks in seconds (default: 2.0)
     * @return SessionPauseResult containing the pause operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionPauseResult betaPause(int timeout, double pollInterval) throws AgentBayException {
        // Validate and set default values for parameters
        if (timeout <= 0) {
            timeout = 600;
        }
        if (pollInterval <= 0) {
            pollInterval = 2.0;
        }
        
        try {
            // Create pause request
            PauseSessionAsyncRequest request = new PauseSessionAsyncRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            // Call pause API
            PauseSessionAsyncResponse response = agentBay.getClient().pauseSessionAsync(request);
            String requestId = ResponseUtil.extractRequestId(response);

            // Check if the initial request was successful
            if (response == null || response.getBody() == null) {
                return new SessionPauseResult(requestId, false, "Invalid response from pause API");
            }

            PauseSessionAsyncResponseBody body = response.getBody();
            Boolean success = body.getSuccess();
            String code = body.getCode() != null ? body.getCode() : "";
            String message = body.getMessage() != null ? body.getMessage() : "";

            // Check for API-level errors
            if (success == null || !success) {
                String errorMessage = message != null && !message.isEmpty() ? message : "Failed to initiate pause";
                if (!code.isEmpty()) {
                    errorMessage = "[" + code + "] " + errorMessage;
                }
                return new SessionPauseResult(requestId, false, errorMessage);
            }

            // Poll for status until PAUSED or timeout
            long startTime = System.currentTimeMillis();
            long timeoutMs = timeout * 1000L;
            long pollIntervalMs = (long) (pollInterval * 1000);

            while (System.currentTimeMillis() - startTime < timeoutMs) {
                try {
                    // Get session information using _getSession
                    GetSessionResult sessionResult = agentBay._getSession(sessionId);
                    
                    if (sessionResult.isSuccess() && sessionResult.getData() != null) {
                        String status = sessionResult.getData().getStatus();
                        // Check if session reached PAUSED state
                        if ("PAUSED".equals(status)) {
                            return new SessionPauseResult(requestId, true, "", status);
                        }
                        
                        // Check if session is still pausing
                        if (!"PAUSING".equals(status)) {
                            return new SessionPauseResult(requestId, false, 
                                "Pause failed, session in unexpected state: " + status, status);
                        }
                    }
                } catch (Exception e) {
                    logger.debug("Failed to get session status: {}", e.getMessage());
                }

                // Sleep before next poll
                try {
                    Thread.sleep(pollIntervalMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return new SessionPauseResult(requestId, false, "Pause operation interrupted", "");
                }
            }

            // Timeout reached
            logger.error("❌ API Operation Error: beta_pause - Timeout waiting for session {} after {}s", sessionId, timeout);
            return new SessionPauseResult(requestId, false, 
                "Timed out after " + timeout + "s waiting for PAUSED state", "");

        } catch (Exception e) {
            throw new AgentBayException("Failed to pause session: " + e.getMessage(), e);
        }
    }

    /**
     * Pauses this session with default parameters (beta feature).
     * 
     * Uses default timeout of 600 seconds and poll interval of 2.0 seconds.
     * 
     * @return SessionPauseResult containing the pause operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionPauseResult betaPause() throws AgentBayException {
        return betaPause(600, 2.0);
    }

    /**
     * Resumes this session and waits until it enters RUNNING state (beta feature).
     * 
     * This method sends a resume request to the backend and polls the session status
     * until it reaches the RUNNING state or the timeout is exceeded.
     * 
     * @param timeout Maximum time to wait in seconds (must be > 0, default 600)
     * @param pollInterval Time between status checks in seconds (must be > 0, default 2.0)
     * @return SessionResumeResult containing the resume operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionResumeResult betaResume(int timeout, double pollInterval) throws AgentBayException {
        // Validate and set default values for parameters
        if (timeout <= 0) {
            timeout = 600;
        }
        if (pollInterval <= 0) {
            pollInterval = 2.0;
        }
        
        try {
            // Create resume request
            ResumeSessionAsyncRequest request = new ResumeSessionAsyncRequest();
            request.setAuthorization("Bearer " + getApiKey());
            request.setSessionId(sessionId);

            // Call resume API
            ResumeSessionAsyncResponse response = agentBay.getClient().resumeSessionAsync(request);
            String requestId = ResponseUtil.extractRequestId(response);

            // Check if the initial request was successful
            if (response == null || response.getBody() == null) {
                return new SessionResumeResult(requestId, false, "Invalid response from resume API");
            }

            ResumeSessionAsyncResponseBody body = response.getBody();
            Boolean success = body.getSuccess();
            String code = body.getCode() != null ? body.getCode() : "";
            String message = body.getMessage() != null ? body.getMessage() : "";

            // Check for API-level errors
            if (success == null || !success) {
                String errorMessage = message != null && !message.isEmpty() ? message : "Failed to initiate resume";
                if (!code.isEmpty()) {
                    errorMessage = "[" + code + "] " + errorMessage;
                }
                return new SessionResumeResult(requestId, false, errorMessage);
            }

            // Poll for status until RUNNING or timeout
            long startTime = System.currentTimeMillis();
            long timeoutMs = timeout * 1000L;
            long pollIntervalMs = (long) (pollInterval * 1000);

            while (System.currentTimeMillis() - startTime < timeoutMs) {
                try {
                    // Get session information using _getSession
                    GetSessionResult sessionResult = agentBay._getSession(sessionId);
                    
                    if (sessionResult.isSuccess() && sessionResult.getData() != null) {
                        String status = sessionResult.getData().getStatus();
                        // Check if session reached RUNNING state
                        if ("RUNNING".equals(status)) {
                            return new SessionResumeResult(requestId, true, "", status);
                        }
                        
                        // Check if session is still resuming
                        if (!"RESUMING".equals(status)) {
                            return new SessionResumeResult(requestId, false, 
                                "Resume failed, session in unexpected state: " + status, status);
                        }
                    }
                } catch (Exception e) {
                    logger.debug("Failed to get session status: {}", e.getMessage());
                    return new SessionResumeResult(requestId, false, "Failed to get session status:{}" + e.getMessage() , "");
                }
                // Sleep before next poll
                try {
                    Thread.sleep(pollIntervalMs);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return new SessionResumeResult(requestId, false, "Resume operation interrupted", "");
                }
            }

            // Timeout reached
            return new SessionResumeResult(requestId, false, 
                "Timed out after " + timeout + "s waiting for RUNNING state", "");

        } catch (Exception e) {
            throw new AgentBayException("Failed to resume session: " + e.getMessage(), e);
        }
    }

    /**
     * Resumes this session with default parameters (beta feature).
     * 
     * Uses default timeout of 600 seconds and poll interval of 2.0 seconds.
     * 
     * @return SessionResumeResult containing the resume operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionResumeResult betaResume() throws AgentBayException {
        return betaResume(600, 2.0);
    }

    /**
     * Returns a string representation of this session.
     * 
     * @return A string containing the session ID and parameters
     */
    @Override
    public String toString() {
        return "Session{" +
                "sessionId='" + sessionId + '\'' +
                '}';
    }
}