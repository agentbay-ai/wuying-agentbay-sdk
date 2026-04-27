package com.aliyun.agentbay;

import com.aliyun.agentbay.browser.BrowserContext;
import com.aliyun.agentbay.browser.BrowserSyncMode;
import com.aliyun.agentbay.client.ApiClient;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.AuthenticationException;
import com.aliyun.agentbay.mobile.MobileSimulate;
import com.aliyun.agentbay.mobile.MobileSimulateConfig;
import com.aliyun.agentbay.mobile.MobileSimulateMode;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.network.BetaNetworkService;
import com.aliyun.agentbay.skills.BetaSkillsService;

import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.util.ResponseUtil;
import com.aliyun.agentbay.util.Version;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.aliyun.teaopenapi.models.Config;
import com.aliyun.wuyingai20250506.Client;
import com.aliyun.wuyingai20250506.models.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;


/**
 * AgentBay represents the main client for interacting with the AgentBay cloud runtime
 * environment.
 *
 * <p>This class provides the entry point for creating and managing sessions in the
 * AgentBay cloud environment. It handles authentication, session lifecycle management,
 * and provides access to various services including context management, mobile simulation,
 * and network services.</p>
 */

public class AgentBay {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final Logger logger = LoggerFactory.getLogger(AgentBay.class);

    private String apiKey;
    private String regionId;
    public Client client;
    private ApiClient apiClient;
    private ConcurrentHashMap<String, Session> sessions;
    private MobileSimulate mobileSimulate;
    private BetaNetworkService betaNetwork;
    private BetaSkillsService betaSkills;

    public AgentBay() throws AgentBayException {
        this(null, null);
    }

    public AgentBay(String apiKey) throws AgentBayException {
        this(apiKey, null);
    }

    public AgentBay(String apiKey, com.aliyun.agentbay.Config config) throws AgentBayException {
        if (config == null) {
            config = new com.aliyun.agentbay.Config();
        }

        if (apiKey == null || apiKey.trim().isEmpty()) {
            apiKey = System.getenv("AGENTBAY_API_KEY");
            if (apiKey == null || apiKey.trim().isEmpty()) {
                throw new AuthenticationException(
                    "API key is required. Provide it as a parameter or set the " +
                    "AGENTBAY_API_KEY environment variable"
                );
            }
        }

        this.apiKey = apiKey;
        this.regionId = config.getRegionId();
        this.sessions = new ConcurrentHashMap<>();

        try {
            // Initialize the OpenAPI client
            Config clientConfig = new Config();
            clientConfig.setEndpoint(config.getEndpoint());
            clientConfig.setAccessKeyId("Bearer");
            clientConfig.setAccessKeySecret(apiKey);
            clientConfig.setReadTimeout(config.getTimeoutMs());
            clientConfig.setConnectTimeout(config.getTimeoutMs());

            this.client = new Client(clientConfig);
            this.apiClient = new ApiClient(this.client, apiKey);
            this.mobileSimulate = new MobileSimulate(this);
            this.betaNetwork = new BetaNetworkService(this);
            this.betaSkills = new BetaSkillsService(this);
        } catch (Exception e) {
            throw new AgentBayException("Failed to initialize AgentBay client", e);
        }
    }


    /**
     * Internal method to get session information by session ID.
     *
     * This method calls the GetSession API and returns raw session data without creating a Session object.
     * This method is public to allow access from Session class for polling operations.
     *
     * @param sessionId The ID of the session to retrieve
     * @return GetSessionResult containing session information
     */
    public GetSessionResult _getSession(String sessionId) {
        try {
            GetSessionRequest request = new GetSessionRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setSessionId(sessionId);

            GetSessionResponse response = client.getSession(request);

            String requestId = ResponseUtil.extractRequestId(response);

            if (response == null || response.getBody() == null) {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Invalid response from GetSession API"
                );
            }

            GetSessionResponseBody body = response.getBody();
            Boolean success = body.getSuccess();
            String code = body.getCode();
            String message = body.getMessage();

            // Check for API-level errors
            if (success == null || !success) {
                String errorMsg = message != null ? message : "Unknown error";
                if (code != null) {
                    errorMsg = "[" + code + "] " + errorMsg;
                }
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    errorMsg
                );
            }

            // Extract session data
            GetSessionData data = null;
            if (body.getData() != null) {
                GetSessionResponseBody.GetSessionResponseBodyData responseData = body.getData();
                data = new GetSessionData(
                    responseData.getSessionId(),
                    responseData.getAppInstanceId(),
                    responseData.getResourceId(),
                    responseData.getResourceUrl(),
                    responseData.getVpcResource() != null ? responseData.getVpcResource() : false,
                    responseData.getNetworkInterfaceIp(),
                    responseData.getHttpPort(),
                    responseData.getToken(),
                    responseData.getLinkUrl(),
                    responseData.getWsUrl(),
                    body.getCode() != null ? body.getCode() : "",
                    toolListToString(responseData.getToolList()),
                    success,
                    responseData.getStatus() != null ? responseData.getStatus() : ""
                );
            }

            return new GetSessionResult(
                requestId,
                true,
                data,
                ""
            );
        } catch (com.aliyun.tea.TeaException e) {
            String errorStr = e.getMessage();
            String requestId = "";
            if (e.getData() != null && e.getData().get("RequestId") != null) {
                requestId = e.getData().get("RequestId").toString();
            }

            // Check if this is an expected business error (e.g., session not found)
            if (errorStr != null && (errorStr.contains("InvalidMcpSession.NotFound") ||
                                     errorStr.contains("NotFound"))) {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Session " + sessionId + " not found"
                );
            } else {
                return new GetSessionResult(
                    requestId,
                    false,
                    null,
                    "Failed to get session " + sessionId + ": " + errorStr
                );
            }
        } catch (Exception e) {
            return new GetSessionResult(
                "",
                false,
                null,
                "Failed to get session " + sessionId + ": " + e.getMessage()
            );
        }
    }

    /**
     * Get a session by its ID from remote server.
     * This method calls the GetSession API to retrieve session information and creates a Session object.
     * This method fetches from the remote server, enabling session recovery scenarios.
     *
     * @param sessionId The ID of the session to retrieve. Must be a non-empty string.
     * @return SessionResult containing the Session instance, request ID, and success status.
     * @throws AgentBayException if the API request fails
     */
    public SessionResult get(String sessionId) throws AgentBayException {
        // Validate input
        if (sessionId == null || sessionId.trim().isEmpty()) {
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage("session_id is required");
            result.setRequestId("");
            return result;
        }

        // Call GetSession API
        GetSessionResult getResult = _getSession(sessionId);

        // Check if the API call was successful
        if (!getResult.isSuccess()) {
            String errorMsg = getResult.getErrorMessage() != null ? getResult.getErrorMessage() : "Unknown error";
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage("Failed to get session " + sessionId + ": " + errorMsg);
            result.setRequestId(getResult.getRequestId());
            return result;
        }

        // Create the Session object
        Session session = new Session(sessionId, this);

        // Set ResourceUrl from GetSession response
        if (getResult.getData() != null) {
            GetSessionData data = getResult.getData();
            session.setResourceUrl(data.getResourceUrl());
            session.setToken(data.getToken());
            session.setLinkUrl(data.getLinkUrl());
            session.setWsUrl(data.getWsUrl());
            if (data.getAppInstanceId() != null) {
                session.setAppInstanceId(data.getAppInstanceId());
            }
            if (data.getToolList() != null && !data.getToolList().isEmpty()) {
                session.updateMcpTools(data.getToolList());
            }
        }

        SessionResult result = new SessionResult();
        result.setRequestId(getResult.getRequestId());
        result.setSuccess(true);
        result.setSession(session);
        return result;
    }



    /**
     * Get the underlying OpenAPI client
     *
     * @return Client instance
     */
    public Client getClient() {
        return client;
    }

    /**
     * Get the API client (internal use)
     *
     * @return ApiClient instance
     */
    public ApiClient getApiClient() {
        return apiClient;
    }

    /**
     * Get mobile simulate service for this AgentBay instance
     *
     * @return MobileSimulate instance
     */
    public MobileSimulate getMobileSimulate() {
        return mobileSimulate;
    }

    /**
     * Get beta network service (trial feature).
     *
     * @return BetaNetworkService instance
     */
    public BetaNetworkService getBetaNetwork() {
        return betaNetwork;
    }

    /**
     * Get beta skills service (trial feature).
     *
     * @return BetaSkillsService instance
     */
    public BetaSkillsService getBetaSkills() {
        return betaSkills;
    }

    /**
     * Get the API key
     *
     * @return The API key
     */
    public String getApiKey() {
        return apiKey;
    }

    /**
     * Get the region ID
     *
     * @return The region ID
     */
    public String getRegionId() {
        return regionId;
    }

    /**
     * Create a new session with CreateSessionParams
     *
     * @param params Parameters for creating the session
     * @return SessionResult containing the created session information
     * @throws AgentBayException if the session creation fails
     */
    public SessionResult create(CreateSessionParams params) throws AgentBayException {
        try {
            if (params == null) {
                params = new CreateSessionParams();
            }
            CreateMcpSessionRequest request = new CreateMcpSessionRequest();
            request.authorization = "Bearer " + apiKey;

            // Handle context syncs
            if (params.getContextSyncs() != null && !params.getContextSyncs().isEmpty()) {
                List<CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList> persistenceDataList =
                    new ArrayList<>();

                for (ContextSync cs : params.getContextSyncs()) {
                    String policyJson = null;
                    if (cs.getPolicy() != null) {
                        try {
                            // Convert policy to Map first, then to JSON
                            Map<String, Object> policyMap = cs.getPolicy().toMap();
                            policyJson = objectMapper.writeValueAsString(policyMap);
                        } catch (Exception e) {
                        }
                    }

                    CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList persistenceData =
                        new CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList();
                    persistenceData.setContextId(cs.getContextId());
                    persistenceData.setPath(cs.getPath());
                    persistenceData.setPolicy(policyJson);

                    persistenceDataList.add(persistenceData);
                }

                request.setPersistenceDataList(persistenceDataList);
            }

            // Add BrowserContext as a ContextSync if provided
            if (params.getBrowserContext() != null) {
                BrowserContext browserContext = params.getBrowserContext();

                // Create a new SyncPolicy with default values for browser context
                UploadPolicy uploadPolicy = new UploadPolicy(
                    browserContext.isAutoUpload(),
                    UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
                    30
                );

                // Build whitelist based on sync mode
                List<WhiteList> whiteLists = new ArrayList<>();
                BrowserSyncMode syncMode = browserContext.getSyncMode();

                if (syncMode == BrowserSyncMode.MINIMAL) {
                    // MINIMAL mode: only Cookies + Local State
                    whiteLists.add(new WhiteList("/Local State", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Cookies", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Cookies-journal", new ArrayList<>()));
                } else {
                    // STANDARD mode: login state + anti-risk-control data
                    // Auth core
                    whiteLists.add(new WhiteList("/Local State", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Cookies", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Cookies-journal", new ArrayList<>()));
                    // Anti-risk-control device fingerprint (localStorage / IndexedDB)
                    whiteLists.add(new WhiteList("/Default/Local Storage", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/IndexedDB", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Session Storage", new ArrayList<>()));
                    // Saved passwords and form autofill
                    whiteLists.add(new WhiteList("/Default/Login Data", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Login Data-journal", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Login Data For Account", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Login Data For Account-journal", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Web Data", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Web Data-journal", new ArrayList<>()));
                    // Browser settings and permission consistency
                    whiteLists.add(new WhiteList("/Default/Preferences", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Secure Preferences", new ArrayList<>()));
                    // Network behavior consistency (HSTS / QUIC)
                    whiteLists.add(new WhiteList("/Default/TransportSecurity", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Network Persistent State", new ArrayList<>()));
                    // Rendering fingerprint stability
                    whiteLists.add(new WhiteList("/Default/GPUCache", new ArrayList<>()));
                    // Cross-domain password matching
                    whiteLists.add(new WhiteList("/Default/Affiliation Database", new ArrayList<>()));
                    whiteLists.add(new WhiteList("/Default/Affiliation Database-journal", new ArrayList<>()));
                }
                BWList bwList = new BWList(whiteLists);

                SyncPolicy syncPolicy = new SyncPolicy(
                    uploadPolicy,
                    DownloadPolicy.defaultPolicy(),
                    DeletePolicy.defaultPolicy(),
                    ExtractPolicy.defaultPolicy(),
                    RecyclePolicy.defaultPolicy(),
                    bwList
                );

                // Serialize the sync_policy to JSON
                String policyJson = null;
                try {
                    Map<String, Object> policyMap = syncPolicy.toMap();
                    policyJson = objectMapper.writeValueAsString(policyMap);
                } catch (Exception e) {
                }

                // Create browser context sync item
                CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList browserContextSync =
                    new CreateMcpSessionRequest.CreateMcpSessionRequestPersistenceDataList();
                browserContextSync.setContextId(browserContext.getContextId());
                browserContextSync.setPath(com.aliyun.agentbay.Config.BROWSER_DATA_PATH);
                browserContextSync.setPolicy(policyJson);

                // Add to persistence data list or create new one if not exists
                if (request.getPersistenceDataList() == null) {
                    request.setPersistenceDataList(new ArrayList<>());
                }
                request.getPersistenceDataList().add(browserContextSync);
            }

            // Set image ID if provided
            if (params.getImageId() != null) {
                request.setImageId(params.getImageId());
            }

            // SDK idle release timeout (seconds)
            Integer idleReleaseTimeout = params.getIdleReleaseTimeout();
            if (idleReleaseTimeout != null) {
                request.setTimeout(idleReleaseTimeout);
            }

            // Set labels if provided
            if (params.getLabels() != null && !params.getLabels().isEmpty()) {
                try {
                    String labelsJson = objectMapper.writeValueAsString(params.getLabels());
                    request.setLabels(labelsJson);
                } catch (Exception e) {
                }
            }

            // Set policy ID if provided
            if (params.getPolicyId() != null && !params.getPolicyId().isEmpty()) {
                request.setMcpPolicyId(params.getPolicyId());
            }

            // Beta: Set network ID if provided
            if (params.getBetaNetworkId() != null && !params.getBetaNetworkId().isEmpty()) {
                request.setNetworkId(params.getBetaNetworkId());
            }

            // Add skills loading if requested
            if (params.getLoadSkills() != null && params.getLoadSkills()) {
                request.setLoadSkill(true);
                if (params.getSkillNames() != null && !params.getSkillNames().isEmpty()) {
                    request.setSkills(params.getSkillNames());
                }
            }

            // Set enable_record when user explicitly sets enable_browser_replay
            // When null (not set), don't send the field - let server decide the default
            if (params.getEnableBrowserReplay() != null) {
                request.setEnableRecord(params.getEnableBrowserReplay());
            }

            // Note: ExtraConfigs is handled automatically by MobileExtraConfig during session creation
            // The mobile configuration will be applied after session is created
            // See: session.mobile.configure() call below

            // Add SDK stats for tracking
            String framework = params.getFramework() != null ? params.getFramework() : "";
            String sdkStatsJson = String.format(
                "{\"source\":\"sdk\",\"sdk_language\":\"%s\",\"sdk_version\":\"%s\",\"is_release\":%s,\"framework\":\"%s\"}",
                Version.getSdkLanguage(),
                Version.getVersionString(),
                Version.isRelease(),
                framework
            );
            request.setSdkStats(sdkStatsJson);

            // Add LoginRegionId if region_id is set
            if (this.regionId != null && !this.regionId.isEmpty()) {
                request.setLoginRegionId(this.regionId);
            }
            CreateMcpSessionResponse response = client.createMcpSession(request);

            if (response == null || response.getBody() == null) {
                String requestId = response != null ? ResponseUtil.extractRequestId(response) : "";
                SessionResult result = new SessionResult();
                result.setSuccess(false);
                result.setErrorMessage("Invalid response from create session API");
                result.setRequestId(requestId);
                return result;
            }

            SessionResult result = new SessionResult();
            String requestId = ResponseUtil.extractRequestId(response);
            result.setRequestId(requestId);

            // Check for API-level errors (body.Success and body.Code)
            if (response.getBody().getSuccess() != null && !response.getBody().getSuccess()) {
                String code = response.getBody().getCode() != null ? response.getBody().getCode() : "Unknown";
                String message = response.getBody().getMessage() != null ? response.getBody().getMessage() : "Unknown error";
                result.setSuccess(false);
                result.setErrorMessage(String.format("[%s] %s", code, message));
                return result;
            }

            // Check if data exists
            if (response.getBody().getData() == null) {
                result.setSuccess(false);
                result.setErrorMessage("Invalid response format: 'Data' field is missing");
                return result;
            }

            // Check for data-level errors (data.Success and data.ErrMsg)
            if (response.getBody().getData().getSuccess() != null && !response.getBody().getData().getSuccess()) {
                String errorMsg = response.getBody().getData().getErrMsg() != null ?
                    response.getBody().getData().getErrMsg() : "Session creation failed";
                result.setSuccess(false);
                result.setErrorMessage(errorMsg);
                return result;
            }

            // Extract session ID from response data
            String sessionId = null;
            try {
                sessionId = response.getBody().getData().getSessionId();
            } catch (Exception e) {
            }

            if (sessionId == null || sessionId.isEmpty()) {
                result.setSuccess(false);
                result.setErrorMessage("SessionId not found in response");
                return result;
            }

            result.setSessionId(sessionId);
            result.setSuccess(true);

            // Create and cache the session
            Session session = new Session(result.getSessionId(), this);
            if (params.getImageId() != null) {
                session.setImageId(params.getImageId());
            }

            // Set browser recording state (pass through user's explicit setting, or null for server default)
            session.setEnableBrowserReplay(params.getEnableBrowserReplay());

            // LinkUrl/token may be returned by the server for direct tool calls.
            if (response.getBody().getData() != null) {
                if (response.getBody().getData().getResourceUrl() != null) {
                    session.setResourceUrl(response.getBody().getData().getResourceUrl());
                }
                if (response.getBody().getData().getToken() != null) {
                    session.setToken(response.getBody().getData().getToken());
                }
                if (response.getBody().getData().getLinkUrl() != null) {
                    session.setLinkUrl(response.getBody().getData().getLinkUrl());
                }
                if (response.getBody().getData().getWsUrl() != null) {
                    session.setWsUrl(response.getBody().getData().getWsUrl());
                }
                if (response.getBody().getData().getAppInstanceId() != null) {
                    session.setAppInstanceId(response.getBody().getData().getAppInstanceId());
                }
                if (response.getBody().getData().getToolList() != null) {
                    session.updateMcpTools(response.getBody().getData().getToolList());
                }
            }

            sessions.put(result.getSessionId(), session);
            result.setSession(session);

            // Populate skills if loadSkills was requested
            // Process mobile configuration if provided
            if (params.getExtraConfigs() != null && params.getExtraConfigs().getMobile() != null) {
                try {
                    session.mobile.configure(params.getExtraConfigs().getMobile());
                } catch (Exception e) {
                }
            }

            // If we have persistence data, wait for context synchronization
            boolean needsContextSync = (params.getContextSyncs() != null && !params.getContextSyncs().isEmpty()) ||
                                      (params.getBrowserContext() != null);
            Set<String> waitContextIds = new HashSet<>();
            if (params.getContextSyncs() != null) {
                for (ContextSync cs : params.getContextSyncs()) {
                    Boolean wait = cs.getBetaWaitForCompletion();
                    if (wait == null || wait) {
                        if (cs.getContextId() != null && !cs.getContextId().isEmpty()) {
                            waitContextIds.add(cs.getContextId());
                        }
                    }
                }
            }
            if (params.getBrowserContext() != null && params.getBrowserContext().getContextId() != null) {
                waitContextIds.add(params.getBrowserContext().getContextId());
            }
            if (needsContextSync && !waitContextIds.isEmpty()) {
                waitForContextSynchronization(session, waitContextIds);
            }

            // Handle mobile simulate if configured
            if (params.getExtraConfigs() != null &&
                params.getExtraConfigs().getMobile() != null &&
                params.getExtraConfigs().getMobile().getSimulateConfig() != null) {

                MobileSimulateConfig simConfig = params.getExtraConfigs().getMobile().getSimulateConfig();
                if (simConfig.isSimulate() && simConfig.getSimulatePath() != null) {
                    waitForMobileSimulate(session, simConfig);
                }
            }
            return result;
        } catch (Exception e) {
            SessionResult result = new SessionResult();
            result.setSuccess(false);
            result.setErrorMessage(e.getMessage());
            // Try to extract requestId if exception has it (for ClientException cases)
            if (e instanceof com.aliyun.tea.TeaException) {
                com.aliyun.tea.TeaException teaException = (com.aliyun.tea.TeaException) e;
                if (teaException.getData() != null && teaException.getData().get("RequestId") != null) {
                    result.setRequestId(teaException.getData().get("RequestId").toString());
                }
            }
            return result;
        }
    }

    /**
     * Wait for mobile simulate to complete
     *
     * @param session The session to wait for mobile simulate
     * @param simConfig Mobile simulate configuration
     */
    private void waitForMobileSimulate(Session session, MobileSimulateConfig simConfig) {
        String mobileSimPath = simConfig.getSimulatePath();
        MobileSimulateMode mobileSimMode = simConfig.getSimulateMode();

        if (mobileSimPath == null || mobileSimPath.isEmpty()) {
            return;
        }

        try {
            String devInfoFilePath = mobileSimPath + "/dev_info.json";
            String wyaApplyOption = "";

            if (mobileSimMode == null || mobileSimMode == MobileSimulateMode.PROPERTIES_ONLY) {
                wyaApplyOption = "";
            } else if (mobileSimMode == MobileSimulateMode.SENSORS_ONLY) {
                wyaApplyOption = "-sensors";
            } else if (mobileSimMode == MobileSimulateMode.PACKAGES_ONLY) {
                wyaApplyOption = "-packages";
            } else if (mobileSimMode == MobileSimulateMode.SERVICES_ONLY) {
                wyaApplyOption = "-services";
            } else if (mobileSimMode == MobileSimulateMode.ALL) {
                wyaApplyOption = "-all";
            }

            String command = String.format("chmod -R a+rwx %s; wya apply %s %s",
                                          mobileSimPath, wyaApplyOption, devInfoFilePath).trim();
            CommandResult cmdResult = session.getCommand().executeCommand(command, 300000);
            if (cmdResult.isSuccess()) {
                // no-op
            } else {
            }
        } catch (Exception e) {
        }
    }

    /**
     * Wait for context synchronization to complete
     *
     * Uses exponential backoff to balance between quick response and server load:
     * - Starts with short intervals (0.5s) for fast completion detection
     * - Gradually increases intervals (up to 5s max) to reduce server load
     * - Uses exponential backoff factor of 1.1
     *
     * @param session The session to wait for context synchronization
     */
    private void waitForContextSynchronization(Session session, Set<String> waitContextIds) {
        if (waitContextIds == null || waitContextIds.isEmpty()) {
            return;
        }
        // Exponential backoff configuration
        // Starts with short intervals (0.5s) for fast completion detection
        // Gradually increases intervals (up to 5s max) to reduce server load
        // Uses exponential backoff factor of 1.1
        long initialInterval = 500; // Start with 0.5 seconds (500ms) for quick response
        long maxInterval = 5000; // Maximum interval (5s) to avoid excessive delays
        double backoffFactor = 1.1; // Multiply interval by this factor each retry
        int maxRetries = 50; // Maximum number of retries

        double currentInterval = initialInterval;

        for (int retry = 0; retry < maxRetries; retry++) {
            boolean shouldContinue = false;

            try {
                // Get context status data
                ContextInfoResult infoResult = session.getContext().info();

                boolean hasFailure = false;
                Map<String, String> statusByContextId = new HashMap<>();

                for (ContextStatusData item : infoResult.getContextStatusData()) {
                    if (!waitContextIds.contains(item.getContextId())) {
                        continue;
                    }
                    statusByContextId.put(item.getContextId(), item.getStatus());

                    if ("Failed".equals(item.getStatus())) {
                        hasFailure = true;
                    }
                }

                boolean allCompleted = true;
                for (String ctxId : waitContextIds) {
                    String st = statusByContextId.get(ctxId);
                    if (st == null || (!"Success".equals(st) && !"Failed".equals(st))) {
                        allCompleted = false;
                        break;
                    }
                }

                if (allCompleted) {
                    if (hasFailure) {
                    } else {
                    }
                    break; // Exit loop, no need to sleep or backoff
                }

                // Need to continue polling
                shouldContinue = true;
            } catch (Exception e) {
                // On error, continue polling with backoff
                shouldContinue = true;
            }

            // Apply exponential backoff before next retry (if continuing)
            if (shouldContinue && retry < maxRetries - 1) {
                try {
                    // Sleep with current interval
                    Thread.sleep((long) currentInterval);

                    // Exponential backoff: increase interval for next retry, capped at maxInterval
                    currentInterval = Math.min(currentInterval * backoffFactor, maxInterval);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        }
    }

    /**
     * Get context service for this AgentBay instance
     *
     * @return ContextService instance
     */
    public ContextService getContextService() {
        return new ContextService(this);
    }

    /**
     * Get context service for this AgentBay instance (alias for getContextService)
     *
     * @return ContextService instance
     */
    public ContextService getContext() {
        return getContextService();
    }


    /**
     * Returns paginated list of sessions filtered by labels.
     *
     * @param labels Labels to filter sessions (optional)
     * @param page Page number for pagination starting from 1 (optional)
     * @param limit Maximum number of items per page (default: 10)
     * @param status Status to filter sessions: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED (optional)
     * @return SessionListResult containing paginated list of session information
     */
    public SessionListResult list(
            java.util.Map<String, String> labels,
            Integer page,
            Integer limit,
            String status) {
        try {
            // Set default values
            if (limit == null) {
                limit = 10;
            }

            // Validate status parameter
            if (status != null && !com.aliyun.agentbay.enums.SessionStatus.isValid(status)) {
                return new SessionListResult(
                    "",
                    false,
                    "Invalid status '" + status + "'. Must be one of: RUNNING, PAUSING, PAUSED, RESUMING, DELETING, DELETED",
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Validate page number
            if (page != null && page < 1) {
                return new SessionListResult(
                    "",
                    false,
                    "Cannot reach page " + page + ": Page number must be >= 1",
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Calculate next_token based on page number
            String nextToken = "";
            if (page != null && page > 1) {
                // We need to fetch pages 1 through page-1 to get the next_token
                int currentPage = 1;
                while (currentPage < page) {
                    // Make API call to get next_token
                    String labelsJson = labels != null ? objectMapper.writeValueAsString(labels) : "{}";
                    ListSessionRequest request = new ListSessionRequest();
                    request.setAuthorization("Bearer " + apiKey);
                    request.setLabels(labelsJson);
                    request.setMaxResults(limit);
                    request.setStatus(status);
                    if (nextToken != null && !nextToken.isEmpty()) {
                        request.setNextToken(nextToken);
                    }

                    ListSessionResponse response = client.listSession(request);
                    String requestId = ResponseUtil.extractRequestId(response);
                    ListSessionResponseBody body = response.getBody();

                    if (body == null || !body.getSuccess()) {
                        String errorMessage = body != null ? body.getMessage() : "Unknown error";
                        return new SessionListResult(
                            requestId,
                            false,
                            "Cannot reach page " + page + ": " + errorMessage,
                            new ArrayList<>(),
                            "",
                            limit,
                            0
                        );
                    }

                    nextToken = body.getNextToken();
                    if (nextToken == null || nextToken.isEmpty()) {
                        // No more pages available
                        return new SessionListResult(
                            requestId,
                            false,
                            "Cannot reach page " + page + ": No more pages available",
                            new ArrayList<>(),
                            "",
                            limit,
                            body.getTotalCount() != null ? body.getTotalCount() : 0
                        );
                    }
                    currentPage++;
                }
            }

            // Make the actual request for the desired page
            String labelsJson = labels != null ? objectMapper.writeValueAsString(labels) : "{}";
            ListSessionRequest request = new ListSessionRequest();
            request.setAuthorization("Bearer " + apiKey);
            request.setLabels(labelsJson);
            request.setMaxResults(limit);
            request.setStatus(status);
            if (nextToken != null && !nextToken.isEmpty()) {
                request.setNextToken(nextToken);
            }

            ListSessionResponse response = client.listSession(request);

            // Extract request ID
            String requestId = ResponseUtil.extractRequestId(response);
            ListSessionResponseBody body = response.getBody();

            // Check for errors in the response
            if (body == null || !body.getSuccess()) {
                String errorMessage = body != null ? body.getMessage() : "Unknown error";
                return new SessionListResult(
                    requestId,
                    false,
                    "Failed to list sessions: " + errorMessage,
                    new ArrayList<>(),
                    "",
                    limit,
                    0
                );
            }

            // Extract session data
            List<SessionListResult.SessionInfo> sessionInfos = new ArrayList<>();
            if (body.getData() != null) {
                for (ListSessionResponseBody.ListSessionResponseBodyData sessionData : body.getData()) {
                    String sessionId = sessionData.getSessionId();
                    String sessionStatus = sessionData.getSessionStatus();
                    if (sessionId != null) {
                        sessionInfos.add(new SessionListResult.SessionInfo(
                            sessionId,
                            sessionStatus != null ? sessionStatus : "UNKNOWN"
                        ));
                    }
                }
            }

            // Return SessionListResult with request ID and pagination info
            return new SessionListResult(
                requestId,
                true,
                "",
                sessionInfos,
                body.getNextToken() != null ? body.getNextToken() : "",
                body.getMaxResults() != null ? body.getMaxResults() : limit,
                body.getTotalCount() != null ? body.getTotalCount() : 0
            );

        } catch (Exception e) {
            return new SessionListResult(
                "",
                false,
                "Failed to list sessions: " + e.getMessage(),
                new ArrayList<>(),
                "",
                limit != null ? limit : 10,
                0
            );
        }
    }

    /**
     * Returns paginated list of sessions with default parameters.
     *
     * @return SessionListResult containing paginated list of session information
     */
    public SessionListResult list() {
        return list(null, null, null, null);
    }

    public SessionListResult list(String status){
        return list(null, null, null, status);
    }
    /**
     * Delete a session without context synchronization.
     *
     * @param session The session to delete
     * @return DeleteResult
     */
    public DeleteResult delete(Session session) {
        return delete(session, false);
    }

    /**
     * Delete a session with optional context synchronization.
     *
     * @param session The session to delete
     * @param syncContext Whether to sync context before deletion
     * @return DeleteResult
     */
    public DeleteResult delete(Session session, boolean syncContext) {
        if (session == null) {
            return new DeleteResult("", false, "Session is null");
        }

        try {
            DeleteResult result = session.delete(syncContext);

            // Remove from sessions map
            sessions.remove(session.getSessionId());

            return result;
        } catch (Exception e) {
            logger.error("Failed to delete session {}: {}", session.getSessionId(), e.getMessage(), e);
            return new DeleteResult("", false,
                "Failed to delete session " + session.getSessionId() + ": " + e.getMessage());
        }
    }

    /**
     * Pause a session (beta feature), putting it into a dormant state.
     *
     * This is a convenience method that delegates to the session's betaPause method.
     *
     * @param session The session to pause
     * @param timeout Maximum time to wait for pause completion in seconds (default: 600)
     * @param pollInterval Interval between status checks in seconds (default: 2.0)
     * @return SessionPauseResult containing the pause operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionPauseResult betaPause(Session session, int timeout, double pollInterval)
            throws AgentBayException {
        try {
            return session.betaPause(timeout, pollInterval);
        } catch (Exception e) {
            return new SessionPauseResult("", false, "Failed to pause session: " + session.getSessionId() + " - " + e.getMessage());
        }
    }

    /**
     * Pause a session with default parameters (beta feature).
     *
     * Uses default timeout of 600 seconds and poll interval of 2.0 seconds.
     *
     * @param session The session to pause
     * @return SessionPauseResult containing the pause operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionPauseResult betaPause(Session session) throws AgentBayException {
        return betaPause(session, 600, 2.0);
    }

    /**
     * Resume a paused session and wait until it enters RUNNING state (beta feature).
     *
     * This is a convenience method that delegates to the session's betaResume method.
     *
     * @param session The session to resume
     * @param timeout Maximum time to wait for resume completion in seconds (default: 600)
     * @param pollInterval Interval between status checks in seconds (default: 2.0)
     * @return SessionResumeResult containing the resume operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionResumeResult betaResume(Session session, int timeout, double pollInterval)
            throws AgentBayException {
        try {
            return session.betaResume(timeout, pollInterval);
        } catch (Exception e) {
            return new SessionResumeResult("", false, "Failed to resume session: " + session.getSessionId() + " - " + e.getMessage());
        }
    }

    /**
     * Resume a paused session with default parameters (beta feature).
     *
     * Uses default timeout of 600 seconds and poll interval of 2.0 seconds.
     *
     * @param session The session to resume
     * @return SessionResumeResult containing the resume operation result
     * @throws AgentBayException if the API call fails
     */
    public SessionResumeResult betaResume(Session session) throws AgentBayException {
        return betaResume(session, 600, 2.0);
    }

    private static String toolListToString(Object toolList) {
        if (toolList == null) {
            return null;
        }
        if (toolList instanceof String) {
            return (String) toolList;
        }
        try {
            return new ObjectMapper().writeValueAsString(toolList);
        } catch (Exception e) {
            return null;
        }
    }

}