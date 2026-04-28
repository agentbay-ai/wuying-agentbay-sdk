package agentbay

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	openapiutil "github.com/alibabacloud-go/darabonba-openapi/v2/utils"
	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// SessionStatus represents the status of a session
type SessionStatus string

// Session status constants
const (
	SessionStatusRunning  SessionStatus = "RUNNING"  // Session is running
	SessionStatusPaused   SessionStatus = "PAUSED"   // Session is paused
	SessionStatusPausing  SessionStatus = "PAUSING"  // Session is being paused
	SessionStatusResuming SessionStatus = "RESUMING" // Session is being resumed
	SessionStatusDeleted  SessionStatus = "DELETED"  // Session is deleted
	SessionStatusDeleting SessionStatus = "DELETING" // Session is being deleted
	SessionStatusUnknown  SessionStatus = "UNKNOWN"  // Session status is unknown
)

// String returns the string representation of SessionStatus
func (s SessionStatus) String() string {
	return string(s)
}

// IsValid checks if the session status is valid
func (s SessionStatus) IsValid() bool {
	switch s {
	case SessionStatusRunning, SessionStatusPaused, SessionStatusPausing,
		SessionStatusResuming, SessionStatusDeleted, SessionStatusDeleting, SessionStatusUnknown:
		return true
	default:
		return false
	}
}

// GetValidStatuses returns all valid session status values
func GetValidStatuses() []SessionStatus {
	return []SessionStatus{
		SessionStatusRunning,
		SessionStatusPaused,
		SessionStatusPausing,
		SessionStatusResuming,
		SessionStatusDeleted,
		SessionStatusDeleting,
		SessionStatusUnknown,
	}
}

// Option is a function that sets optional parameters for AgentBay client.
type Option func(*AgentBayConfig)

// AgentBayConfig holds optional configuration for the AgentBay client.
type AgentBayConfig struct {
	cfg     *Config
	envFile string
}

// WithConfig returns an Option that sets the configuration for the AgentBay client.
func WithConfig(cfg *Config) Option {
	return func(c *AgentBayConfig) {
		c.cfg = cfg
	}
}

// WithEnvFile returns an Option that sets a custom .env file path for the AgentBay client.
func WithEnvFile(envFile string) Option {
	return func(c *AgentBayConfig) {
		c.envFile = envFile
	}
}

// AgentBay represents the main client for interacting with the AgentBay cloud runtime environment.
type AgentBay struct {
	APIKey         string
	Client         *mcp.Client
	Context        *ContextService
	MobileSimulate *MobileSimulateService
	BetaNetwork    *BetaNetworkService
	BetaSkills     *BetaSkillsService
	config         Config
}

// NewAgentBay creates a new AgentBay client.
// If apiKey is empty, it will look for the AGENTBAY_API_KEY environment variable.
func NewAgentBay(apiKey string, opts ...Option) (*AgentBay, error) {
	if apiKey == "" {
		apiKey = os.Getenv("AGENTBAY_API_KEY")
		if apiKey == "" {
			return nil, fmt.Errorf("API key is required. Provide it as a parameter or set the AGENTBAY_API_KEY environment variable")
		}
	}

	// Apply options safely
	config_option := &AgentBayConfig{}
	for _, opt := range opts {
		if opt != nil {
			opt(config_option)
		}
	}

	// Load configuration using loadConfig function
	// This will load from environment variables, .env file (searched upward), or use defaults
	config := loadConfig(config_option.cfg, config_option.envFile)

	// Create API client
	apiConfig := &openapiutil.Config{
		RegionId:       tea.String(""),
		Endpoint:       tea.String(config.Endpoint),
		ReadTimeout:    tea.Int(config.TimeoutMs),
		ConnectTimeout: tea.Int(config.TimeoutMs),
	}

	client, err := mcp.NewClient(apiConfig)
	if err != nil {
		return nil, fmt.Errorf("create openapi client fails: %v", err)
	}

	// Create AgentBay instance
	agentBay := &AgentBay{
		APIKey:      apiKey,
		Client:      client,
		Context:     nil, // Will be initialized after creation
		BetaNetwork: nil, // Will be initialized after creation
		BetaSkills:  nil, // Will be initialized after creation
		config:      config,
	}

	// Initialize context service
	agentBay.Context = &ContextService{AgentBay: agentBay}
	agentBay.BetaNetwork = &BetaNetworkService{AgentBay: agentBay}
	agentBay.BetaSkills = &BetaSkillsService{AgentBay: agentBay}

	return agentBay, nil
}

// NewAgentBayWithDefaults creates a new AgentBay client using default configuration.
// This is a convenience function that allows calling NewAgentBay without a config parameter.
func NewAgentBayWithDefaults(apiKey string) (*AgentBay, error) {
	return NewAgentBay(apiKey, nil)
}

// Create creates a new session in the AgentBay cloud environment.
// If params is nil, default parameters will be used.
// Create creates a new AgentBay session with specified configuration.
//
// Parameters:
//   - params: Configuration parameters for the session (optional)
//   - Labels: Key-value pairs for session metadata
//   - ImageId: Custom image ID for the session environment
//   - PolicyId: Security policy ID
//   - ExtraConfigs: Additional configuration options
//
// Returns:
//   - *SessionResult: Result containing Session object and request ID
//   - error: Error if the operation fails
//
// Behavior:
//
// - Creates a new isolated cloud runtime environment
// - Waits for session to be ready before returning
// - For VPC sessions, includes VPC-specific configuration
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
func (a *AgentBay) Create(params *CreateSessionParams) (*SessionResult, error) {
	if params == nil {
		params = NewCreateSessionParams()
	} else {
		// Create a deep copy of params to avoid modifying the original object
		params = a.copyCreateSessionParams(params)
	}
	if params.LifecyclePolicy != nil && params.IdleReleaseTimeout > 0 {
		return nil, fmt.Errorf("lifecycle policy and IdleReleaseTimeout are mutually exclusive")
	}

	// Flag to indicate if we need to wait for mobile simulate
	needsMobileSim := false
	var mobileSimMode models.MobileSimulateMode
	var mobileSimPath string

	// Process mobile simulate configuration
	if params.ExtraConfigs != nil && params.ExtraConfigs.Mobile != nil && params.ExtraConfigs.Mobile.SimulateConfig != nil {
		// Check if simulated context id is provided
		mobileSimContextID := params.ExtraConfigs.Mobile.SimulateConfig.SimulatedContextID
		if mobileSimContextID != "" {
			mobileSimContextSync := &ContextSync{
				ContextID: mobileSimContextID,
				Path:      MobileInfoDefaultPath,
			}
			if params.ContextSync == nil {
				params.ContextSync = []*ContextSync{}
			}
			LogDebug(fmt.Sprintf("Adding context sync for mobile simulate: %+v", mobileSimContextSync))
			params.ContextSync = append(params.ContextSync, mobileSimContextSync)
		}

		// Check if we need to execute mobile simulate command
		if params.ExtraConfigs.Mobile.SimulateConfig.Simulate {
			mobileSimPath = params.ExtraConfigs.Mobile.SimulateConfig.SimulatePath
			if mobileSimPath != "" {
				needsMobileSim = true
				mobileSimMode = params.ExtraConfigs.Mobile.SimulateConfig.SimulateMode
			}
		}
	}

	createSessionRequest := &mcp.CreateMcpSessionRequest{
		Authorization: tea.String("Bearer " + a.APIKey),
	}

	// Only set enable_record when user explicitly sets enable_browser_replay
	// When nil (not set), don't send the field - let server decide the default
	if params.EnableBrowserReplay != nil {
		createSessionRequest.EnableRecord = params.EnableBrowserReplay
	}

	// Add SDK stats for tracking
	isRelease := isReleaseVersion()
	framework := ""
	if params != nil {
		framework = params.Framework
	}
	sdkStatsJSON := fmt.Sprintf(`{"source":"sdk","sdk_language":"golang","sdk_version":"%s","is_release":%t,"framework":"%s"}`, Version, isRelease, framework)
	createSessionRequest.SdkStats = tea.String(sdkStatsJSON)

	// Add LoginRegionId if region_id is set
	if a.config.RegionID != "" {
		createSessionRequest.LoginRegionId = tea.String(a.config.RegionID)
	}

	// Add image_id if provided
	if params.ImageId != "" {
		createSessionRequest.ImageId = tea.String(params.ImageId)
	}

	// Add PolicyId if provided
	if params.PolicyId != "" {
		createSessionRequest.McpPolicyId = tea.String(params.PolicyId)
	}

	// Beta: Add NetworkId if provided
	if params.BetaNetworkId != "" {
		createSessionRequest.NetworkId = tea.String(params.BetaNetworkId)
	}

	// Lifecycle policy (minutes, full takeover)
	if params.LifecyclePolicy != nil {
		lp := params.LifecyclePolicy
		if lp.ManualRelease {
			createSessionRequest.ManualRelease = tea.Bool(true)
		} else {
			// Validate non-manual policy has valid values
			if lp.IdleReleaseTimeout <= 0 || lp.MaxRuntime <= 0 {
				return nil, fmt.Errorf("LifecyclePolicy: IdleReleaseTimeout and MaxRuntime must be positive when ManualRelease is false; use NewLifecyclePolicy() or NewLifecyclePolicyWithValues()")
			}
			createSessionRequest.Timeout = tea.Int32(lp.IdleReleaseTimeout)
			createSessionRequest.MaxRuntime = tea.Int32(lp.MaxRuntime)
		}
	} else if params.IdleReleaseTimeout > 0 {
		// Legacy SDK idle release timeout (seconds)
		createSessionRequest.Timeout = tea.Int32(params.IdleReleaseTimeout)
	}

	// Add labels if provided
	if len(params.Labels) > 0 {
		labelsJSON, err := params.GetLabelsJSON()
		if err != nil {
			return nil, fmt.Errorf("failed to marshal labels to JSON: %v", err)
		}
		createSessionRequest.Labels = tea.String(labelsJSON)
	}

	// Add extra configs if provided
	if params.ExtraConfigs != nil {
		extraConfigsJSON, err := params.GetExtraConfigsJSON()
		if err != nil {
			return nil, fmt.Errorf("failed to marshal extra configs to JSON: %v", err)
		}
		if extraConfigsJSON != "" {
			createSessionRequest.ExtraConfigs = tea.String(extraConfigsJSON)
		}
	}

	// Add skills loading if requested
	if params.LoadSkills {
		createSessionRequest.LoadSkill = tea.Bool(true)
		if len(params.SkillNames) > 0 {
			skillPtrs := make([]*string, len(params.SkillNames))
			for i, name := range params.SkillNames {
				skillPtrs[i] = tea.String(name)
			}
			createSessionRequest.Skills = skillPtrs
		}
	}

	// Flag to indicate if we need to wait for context synchronization
	needsContextSync := false
	waitContextIDs := map[string]struct{}{}

	// Add context sync configurations if provided
	var persistenceDataList []*mcp.CreateMcpSessionRequestPersistenceDataList

	if len(params.ContextSync) > 0 {
		for _, contextSync := range params.ContextSync {
			persistenceItem := &mcp.CreateMcpSessionRequestPersistenceDataList{
				ContextId: tea.String(contextSync.ContextID),
				Path:      tea.String(contextSync.Path),
			}

			// Convert policy to JSON string if provided
			if contextSync.Policy != nil {
				policyJSON, err := json.Marshal(contextSync.Policy)
				if err != nil {
					return nil, fmt.Errorf("failed to marshal context sync policy to JSON: %v", err)
				}
				persistenceItem.Policy = tea.String(string(policyJSON))
			}

			persistenceDataList = append(persistenceDataList, persistenceItem)
			if contextSync.BetaWaitForCompletion == nil || *contextSync.BetaWaitForCompletion {
				waitContextIDs[contextSync.ContextID] = struct{}{}
			}
		}
	}

	// Add BrowserContext as a persistence item if provided
	if params.BrowserContext != nil {
		item, err := buildBrowserContextPersistenceDataListItem(params.BrowserContext)
		if err != nil {
			return nil, fmt.Errorf("failed to build browser context persistence item: %w", err)
		}
		persistenceDataList = append(persistenceDataList, item)
		needsContextSync = true
		if params.BrowserContext.ContextID != "" {
			waitContextIDs[params.BrowserContext.ContextID] = struct{}{}
		}
	}

	// Add mobile simulate context sync if needed
	if params.ExtraConfigs != nil && params.ExtraConfigs.Mobile != nil &&
		params.ExtraConfigs.Mobile.SimulateConfig != nil &&
		params.ExtraConfigs.Mobile.SimulateConfig.Simulate &&
		params.ExtraConfigs.Mobile.SimulateConfig.SimulatedContextID != "" {

		simContextID := params.ExtraConfigs.Mobile.SimulateConfig.SimulatedContextID
		LogInfo(fmt.Sprintf("Adding context sync for mobile simulate: &{ContextID:%s Path:%s Policy:<nil>}", simContextID, MobileInfoDefaultPath))

		// Check if already exists in persistenceDataList
		exists := false
		for _, item := range persistenceDataList {
			if tea.StringValue(item.ContextId) == simContextID {
				exists = true
				break
			}
		}

		if !exists {
			mobilePersistence := &mcp.CreateMcpSessionRequestPersistenceDataList{
				ContextId: tea.String(simContextID),
				Path:      tea.String(MobileInfoDefaultPath),
			}
			persistenceDataList = append(persistenceDataList, mobilePersistence)
		}
		if simContextID != "" {
			waitContextIDs[simContextID] = struct{}{}
		}
	}

	if len(persistenceDataList) > 0 {
		createSessionRequest.PersistenceDataList = persistenceDataList
		needsContextSync = true
	}

	// Log API request with all set parameters
	requestParams := fmt.Sprintf("ImageId=%s", tea.StringValue(createSessionRequest.ImageId))

	// Add PolicyId if set
	if createSessionRequest.McpPolicyId != nil && *createSessionRequest.McpPolicyId != "" {
		requestParams += fmt.Sprintf(", PolicyId=%s", *createSessionRequest.McpPolicyId)
	}

	// Add Labels if set
	if createSessionRequest.Labels != nil && *createSessionRequest.Labels != "" {
		labelsStr := *createSessionRequest.Labels
		// Truncate long labels for readability
		if len(labelsStr) > 100 {
			labelsStr = labelsStr[:97] + "..."
		}
		requestParams += fmt.Sprintf(", Labels=%s", labelsStr)
	}

	// Add PersistenceDataList count if set
	if len(createSessionRequest.PersistenceDataList) > 0 {
		requestParams += fmt.Sprintf(", PersistenceDataList=%d items", len(createSessionRequest.PersistenceDataList))
	}

	// Add ExtraConfigs if set
	if createSessionRequest.ExtraConfigs != nil && *createSessionRequest.ExtraConfigs != "" {
		extraConfigsStr := *createSessionRequest.ExtraConfigs
		// Truncate long extra configs for readability
		if len(extraConfigsStr) > 100 {
			extraConfigsStr = extraConfigsStr[:97] + "..."
		}
		requestParams += fmt.Sprintf(", ExtraConfigs=%s", extraConfigsStr)
	}

	logAPICall("CreateMcpSession", requestParams)

	response, err := a.Client.CreateMcpSession(createSessionRequest)

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log API response
	if err != nil {
		logOperationError("CreateMcpSession", err.Error(), true)
		return nil, err
	}

	// Check if the session creation was successful
	if response == nil || response.Body == nil || response.Body.Data == nil {
		return nil, fmt.Errorf("invalid response from CreateMcpSession")
	}

	// Check if there's an error message in the response
	if response.Body.Data.Success != nil && !*response.Body.Data.Success {
		errMsg := "session creation failed"
		if response.Body.Data.ErrMsg != nil {
			errMsg = *response.Body.Data.ErrMsg
		}
		responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("CreateMcpSession", requestID, false, nil, string(responseJSON))
		return nil, fmt.Errorf("%s", errMsg)
	}

	// Check if SessionId is present
	if response.Body.Data.SessionId == nil {
		return nil, fmt.Errorf("no session ID returned from CreateMcpSession")
	}

	// Create a new session object
	session := NewSession(a, *response.Body.Data.SessionId)
	session.ImageId = params.ImageId

	// Set AppInstanceId and ResourceUrl
	if response.Body.Data.GetAppInstanceId() != nil {
		session.AppInstanceId = *response.Body.Data.GetAppInstanceId()
	}
	if response.Body.Data.ResourceUrl != nil {
		session.ResourceUrl = *response.Body.Data.ResourceUrl
	}

	// LinkUrl/token may be returned by the server for direct tool calls.
	if response.Body.Data.Token != nil {
		session.Token = *response.Body.Data.Token
	}
	if response.Body.Data.LinkUrl != nil {
		session.LinkUrl = *response.Body.Data.LinkUrl
	}
	if response.Body.Data.WsUrl != nil {
		session.WsUrl = *response.Body.Data.WsUrl
	}
	if response.Body.Data.ToolList != nil {
		session.McpTools = parseToolListToMcpTools(response.Body.Data.ToolList)
	}

	// Set browser recording state
	session.EnableBrowserReplay = params.EnableBrowserReplay

	// Log successful session creation
	keyFields := map[string]interface{}{
		"session_id":   session.SessionID,
		"resource_url": session.ResourceUrl,
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("CreateMcpSession", requestID, true, keyFields, string(responseJSON))

	// Apply mobile configuration if provided
	if params.ExtraConfigs != nil && params.ExtraConfigs.Mobile != nil {
		if err := session.Mobile.Configure(params.ExtraConfigs.Mobile); err != nil {
			logOperationError("ApplyMobileConfiguration", err.Error(), false)
		}
	}

	// If we have persistence data, wait for context synchronization
	if needsContextSync && len(waitContextIDs) > 0 {
		LogInfo("Waiting for context synchronization to complete...")

		// Exponential backoff configuration
		// Starts with short intervals (0.5s) for fast completion detection
		// Gradually increases intervals (up to 5s max) to reduce server load
		// Uses exponential backoff factor of 1.1
		const initialInterval = 500 * time.Millisecond // Start with 0.5 seconds for quick response
		const maxInterval = 5000 * time.Millisecond    // Maximum interval to avoid excessive delays
		const backoffFactor = 1.1                      // Multiply interval by this factor each retry
		const maxRetries = 50                          // Maximum number of retries

		currentInterval := initialInterval

		for retry := 0; retry < maxRetries; retry++ {
			// Get context status data
			infoResult, err := session.Context.Info()
			if err != nil {
				LogError(fmt.Sprintf("Error getting context info on attempt %d: %v", retry+1, err))
				time.Sleep(currentInterval)
				// Exponential backoff: increase interval for next retry, capped at maxInterval
				currentInterval = time.Duration(float64(currentInterval) * backoffFactor)
				if currentInterval > maxInterval {
					currentInterval = maxInterval
				}
				continue
			}

			hasFailure := false
			statusByContextID := map[string]string{}

			for _, item := range infoResult.ContextStatusData {
				if _, ok := waitContextIDs[item.ContextId]; !ok {
					continue
				}
				statusByContextID[item.ContextId] = item.Status
				LogDebug(fmt.Sprintf("Context %s status: %s, path: %s", item.ContextId, item.Status, item.Path))

				if item.Status == "Failed" {
					hasFailure = true
					LogError(fmt.Sprintf("Context synchronization failed for %s: %s", item.ContextId, item.ErrorMessage))
				}
			}

			allCompleted := true
			for ctxID := range waitContextIDs {
				st, ok := statusByContextID[ctxID]
				if !ok || (st != "Success" && st != "Failed") {
					allCompleted = false
					break
				}
			}

			if allCompleted {
				if hasFailure {
					LogWarn("Context synchronization completed with failures")
				} else {
					LogInfo("Context synchronization completed successfully")
				}
				break
			}

			LogDebug(fmt.Sprintf("Waiting for context synchronization, attempt %d/%d, next interval: %.2fs", retry+1, maxRetries, currentInterval.Seconds()))
			time.Sleep(currentInterval)

			// Exponential backoff: increase interval for next retry, capped at maxInterval
			currentInterval = time.Duration(float64(currentInterval) * backoffFactor)
			if currentInterval > maxInterval {
				currentInterval = maxInterval
			}
		}
	}

	// If we need to do mobile simulate by command, wait for it
	if needsMobileSim && mobileSimPath != "" {
		a.waitForMobileSimulate(session, mobileSimPath, mobileSimMode)
	}

	// Return result with RequestID
	return &SessionResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Session: session,
		Success: true,
	}, nil
}

// waitForMobileSimulate waits for mobile simulate command to complete.
func (a *AgentBay) waitForMobileSimulate(session *Session, mobileSimPath string, mobileSimMode models.MobileSimulateMode) error {
	LogInfo("⏳ Mobile simulate: Waiting for completion")

	if session.Mobile == nil {
		LogWarn("Mobile module not found in session, skipping mobile simulate")
		return nil
	}
	if session.Command == nil {
		LogWarn("Command module not found in session, skipping mobile simulate")
		return nil
	}
	if mobileSimPath == "" {
		LogWarn("Mobile simulate path is empty, skipping mobile simulate")
		return nil
	}

	// Run mobile simulate command
	startTime := time.Now()
	devInfoFilePath := mobileSimPath + "/" + MobileInfoFileName
	wyaApplyOption := ""

	switch mobileSimMode {
	case models.MobileSimulateModePropertiesOnly, "":
		wyaApplyOption = ""
	case models.MobileSimulateModeSensorsOnly:
		wyaApplyOption = " -sensors"
	case models.MobileSimulateModePackagesOnly:
		wyaApplyOption = " -packages"
	case models.MobileSimulateModeServicesOnly:
		wyaApplyOption = " -services"
	case models.MobileSimulateModeAll:
		wyaApplyOption = " -all"
	}

	command := fmt.Sprintf("chmod -R a+rwx %s; wya apply%s %s", mobileSimPath, wyaApplyOption, devInfoFilePath)
	LogInfo(fmt.Sprintf("⏳ Waiting for mobile simulate completion, command: %s", command))

	cmdResult, err := session.Command.ExecuteCommand(command)
	if err != nil {
		LogError(fmt.Sprintf("Failed to execute mobile simulate command: %v", err))
		return nil
	}

	duration := time.Since(startTime)
	LogInfo(fmt.Sprintf("✅ Mobile simulate completed with mode: %s, duration: %.2f seconds", mobileSimMode, duration.Seconds()))
	LogDebug(fmt.Sprintf("   Output: %s", cmdResult.Output))

	return nil
}

// ListSessionParams contains parameters for listing sessions
type ListSessionParams struct {
	MaxResults int32             // Number of results per page
	NextToken  string            // Token for the next page
	Labels     map[string]string // Labels to filter by
}

// NewListSessionParams creates a new ListSessionParams with default values
func NewListSessionParams() *ListSessionParams {
	return &ListSessionParams{
		MaxResults: 10, // Default page size
		NextToken:  "",
		Labels:     make(map[string]string),
	}
}

// List returns paginated list of session IDs filtered by labels and status.
//
// Parameters:
//   - status: Optional status to filter sessions (can be empty string or SessionStatus for no filtering)
//   - labels: Optional labels to filter sessions (can be nil for no filtering)
//   - page: Optional page number for pagination (starting from 1, nil or 0 for first page)
//   - limit: Optional maximum number of items per page (nil or 0 uses default of 10)
//
// Returns:
//   - *SessionListResult: Paginated list of session IDs that match the filters
//   - error: An error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.List("", nil, nil, nil)
//	// Or using enum:
//	result, _ := client.List(SessionStatusRunning.String(), nil, nil, nil)
func (a *AgentBay) List(status string, labels map[string]string, page *int, limit *int32) (*SessionListResult, error) {
	// Validate status parameter if provided
	if status != "" {
		sessionStatus := SessionStatus(status)
		if !sessionStatus.IsValid() {
			validStatuses := GetValidStatuses()
			var statusStrings []string
			for _, s := range validStatuses {
				statusStrings = append(statusStrings, string(s))
			}
			return &SessionListResult{
					ApiResponse: models.ApiResponse{
						RequestID: "",
					},
					SessionIds: []map[string]interface{}{},
					NextToken:  "",
					MaxResults: 0,
					TotalCount: 0,
				}, fmt.Errorf("invalid session status '%s'. Valid values are: [%s]",
					status, strings.Join(statusStrings, ", "))
		}
	}

	// Set default values
	if labels == nil {
		labels = make(map[string]string)
	}
	actualLimit := int32(10)
	if limit != nil && *limit > 0 {
		actualLimit = *limit
	}

	// Validate page number
	if page != nil && *page < 1 {
		return &SessionListResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			SessionIds: []map[string]interface{}{},
			NextToken:  "",
			MaxResults: actualLimit,
			TotalCount: 0,
		}, fmt.Errorf("cannot reach page %d: Page number must be >= 1", *page)
	}

	// Convert labels to JSON
	labelsJSON, err := json.Marshal(labels)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal labels to JSON: %v", err)
	}

	// Calculate next_token based on page number
	nextToken := ""
	if page != nil && *page > 1 {
		// We need to fetch pages 1 through page-1 to get the next_token
		currentPage := 1
		for currentPage < *page {
			// Make API call to get next_token
			listSessionRequest := &mcp.ListSessionRequest{
				Authorization: tea.String("Bearer " + a.APIKey),
				Labels:        tea.String(string(labelsJSON)),
				MaxResults:    tea.Int32(actualLimit),
			}
			if nextToken != "" {
				listSessionRequest.NextToken = tea.String(nextToken)
			}

			response, err := a.Client.ListSession(listSessionRequest)
			if err != nil {
				return &SessionListResult{
					ApiResponse: models.ApiResponse{
						RequestID: models.ExtractRequestID(response),
					},
					SessionIds: []map[string]interface{}{},
					NextToken:  "",
					MaxResults: actualLimit,
					TotalCount: 0,
				}, fmt.Errorf("cannot reach page %d: %v", *page, err)
			}

			if response.Body == nil || response.Body.Success == nil || !*response.Body.Success {
				errorMsg := "Unknown error"
				if response.Body != nil && response.Body.Message != nil {
					errorMsg = *response.Body.Message
				} else if response.Body != nil && response.Body.Code != nil {
					errorMsg = *response.Body.Code
				}
				return &SessionListResult{
					ApiResponse: models.ApiResponse{
						RequestID: models.ExtractRequestID(response),
					},
					SessionIds: []map[string]interface{}{},
					NextToken:  "",
					MaxResults: actualLimit,
					TotalCount: 0,
				}, fmt.Errorf("cannot reach page %d: %s", *page, errorMsg)
			}

			if response.Body.NextToken == nil || *response.Body.NextToken == "" {
				// No more pages available
				totalCount := int32(0)
				if response.Body.TotalCount != nil {
					totalCount = *response.Body.TotalCount
				}
				return &SessionListResult{
					ApiResponse: models.ApiResponse{
						RequestID: models.ExtractRequestID(response),
					},
					SessionIds: []map[string]interface{}{},
					NextToken:  "",
					MaxResults: actualLimit,
					TotalCount: totalCount,
				}, fmt.Errorf("cannot reach page %d: No more pages available", *page)
			}
			nextToken = *response.Body.NextToken
			currentPage++
		}
	}

	// Make the actual request for the desired page
	listSessionRequest := &mcp.ListSessionRequest{
		Authorization: tea.String("Bearer " + a.APIKey),
		Labels:        tea.String(string(labelsJSON)),
		MaxResults:    tea.Int32(actualLimit),
	}
	if nextToken != "" {
		listSessionRequest.NextToken = tea.String(nextToken)
	}

	// Add status filter if provided
	if status != "" {
		listSessionRequest.Status = tea.String(status)
	}

	// Log API request
	requestParams := fmt.Sprintf("Labels=%s, MaxResults=%d", *listSessionRequest.Labels, *listSessionRequest.MaxResults)
	if listSessionRequest.NextToken != nil {
		requestParams += fmt.Sprintf(", NextToken=%s", *listSessionRequest.NextToken)
	}
	if listSessionRequest.Status != nil {
		requestParams += fmt.Sprintf(", Status=%s", *listSessionRequest.Status)
	}
	logAPICall("ListSession", requestParams)

	response, err := a.Client.ListSession(listSessionRequest)

	// Log API response
	if err != nil {
		logOperationError("ListSession", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	if response != nil && response.Body != nil {
		LogDebug(fmt.Sprintf("Response from ListSession: %+v", response.Body))
	}

	// Check for errors in the response
	if response.Body == nil || response.Body.Success == nil || !*response.Body.Success {
		errorMsg := "Unknown error"
		if response.Body != nil && response.Body.Message != nil {
			errorMsg = *response.Body.Message
		} else if response.Body != nil && response.Body.Code != nil {
			errorMsg = *response.Body.Code
		}
		logOperationError("ListSession", fmt.Sprintf("failed to list sessions: %s", errorMsg), false)
		return &SessionListResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			SessionIds: []map[string]interface{}{},
			NextToken:  "",
			MaxResults: actualLimit,
			TotalCount: 0,
		}, fmt.Errorf("failed to list sessions: %s", errorMsg)
	}

	var sessionIds []map[string]interface{}
	var nextTokenResult string
	var maxResults int32 = actualLimit
	var totalCount int32

	if response.Body != nil {
		// Extract pagination information
		if response.Body.NextToken != nil {
			nextTokenResult = *response.Body.NextToken
		}
		if response.Body.MaxResults != nil {
			maxResults = *response.Body.MaxResults
		}
		if response.Body.TotalCount != nil {
			totalCount = *response.Body.TotalCount
		}

		// Extract session data
		if response.Body.Data != nil {
			for _, sessionData := range response.Body.Data {
				if sessionData.SessionId != nil {
					sessionStatus := "UNKNOWN"
					if sessionData.SessionStatus != nil {
						sessionStatus = *sessionData.SessionStatus
					}
					// Create a structured session object with both ID and status
					sessionInfo := map[string]interface{}{
						"sessionId":     *sessionData.SessionId,
						"sessionStatus": sessionStatus,
					}
					sessionIds = append(sessionIds, sessionInfo)
				}
			}
		}
	}

	// Log successful response
	keyFields := map[string]interface{}{
		"session_count": len(sessionIds),
		"total_count":   totalCount,
		"max_results":   maxResults,
		"has_next_page": nextTokenResult != "",
	}
	if nextTokenResult != "" {
		keyFields["next_token"] = nextTokenResult
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("ListSession", requestID, true, keyFields, string(responseJSON))

	return &SessionListResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		SessionIds: sessionIds,
		NextToken:  nextTokenResult,
		MaxResults: maxResults,
		TotalCount: totalCount,
	}, nil
}

// ListByStatus returns paginated list of session IDs filtered by SessionStatus enum and labels.
// This is a convenience method that accepts SessionStatus enum instead of string.
//
// Parameters:
//   - status: SessionStatus enum to filter sessions (use empty SessionStatus("") for no filtering)
//   - labels: Optional labels to filter sessions (can be nil for no filtering)
//   - page: Optional page number for pagination (starting from 1, nil or 0 for first page)
//   - limit: Optional maximum number of items per page (nil or 0 uses default of 10)
//
// Returns:
//   - *SessionListResult: Paginated list of session IDs that match the filters
//   - error: An error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.ListByStatus(SessionStatusRunning, nil, nil, nil)
//	result, _ := client.ListByStatus("", nil, nil, nil) // No status filter
func (a *AgentBay) ListByStatus(status SessionStatus, labels map[string]string, page *int, limit *int32) (*SessionListResult, error) {
	return a.List(status.String(), labels, page, limit)
}

// Delete deletes a session from the AgentBay cloud environment.
//
// Parameters:
//   - session: The session to delete
//   - syncContext: Optional boolean to synchronize context data before deletion.
//     If true, uploads all context data to OSS. Defaults to false.
//
// Returns:
//   - *DeleteResult: Result containing success status and request ID
//   - error: Error if the operation fails
//
// Behavior:
//
// - If syncContext is true: Uploads all context data to OSS before deletion
// - If syncContext is false: Deletes immediately without sync
// - Continues with deletion even if context sync fails
// - Releases all associated resources
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	client.Delete(result.Session, true)
func (a *AgentBay) Delete(session *Session, syncContext ...bool) (*DeleteResult, error) {
	result, err := session.Delete(syncContext...)
	return result, err
}

// GetSessionResult represents the result of GetSession operation
type GetSessionResult struct {
	models.ApiResponse
	HttpStatusCode int32
	Code           string
	Success        bool
	Data           *GetSessionData
	ErrorMessage   string
}

// ContextInfo represents a context in the GetSession response
type ContextInfo struct {
	Name string
	ID   string
}

// GetSessionData represents the data returned by GetSession API
type GetSessionData struct {
	AppInstanceID      string
	ResourceID         string
	SessionID          string
	Success            bool
	HttpPort           string
	NetworkInterfaceIP string
	Token              string
	LinkUrl            string
	WsUrl              string
	VpcResource        bool
	ResourceUrl        string
	Status             string
	ToolList           string
	Contexts           []ContextInfo
}

func parseToolListToMcpTools(toolList interface{}) []McpTool {
	if toolList == nil {
		return []McpTool{}
	}

	var items []map[string]interface{}

	switch v := toolList.(type) {
	case string:
		if v == "" {
			return []McpTool{}
		}
		if err := json.Unmarshal([]byte(v), &items); err != nil {
			logOperationError("ParseToolList", fmt.Sprintf("Error unmarshaling ToolList: %v", err), false)
			return []McpTool{}
		}
	case []interface{}:
		for _, elem := range v {
			if m, ok := elem.(map[string]interface{}); ok {
				items = append(items, m)
			}
		}
	default:
		raw, err := json.Marshal(toolList)
		if err != nil {
			logOperationError("ParseToolList", fmt.Sprintf("Error marshaling ToolList: %v", err), false)
			return []McpTool{}
		}
		if err := json.Unmarshal(raw, &items); err != nil {
			logOperationError("ParseToolList", fmt.Sprintf("Error unmarshaling ToolList: %v", err), false)
			return []McpTool{}
		}
	}

	tools := make([]McpTool, 0, len(items))
	for _, item := range items {
		name := ""
		if v, ok := item["name"].(string); ok && v != "" {
			name = v
		} else if v, ok := item["Name"].(string); ok && v != "" {
			name = v
		}

		server := ""
		if v, ok := item["server"].(string); ok && v != "" {
			server = v
		} else if v, ok := item["serverName"].(string); ok && v != "" {
			server = v
		} else if v, ok := item["Server"].(string); ok && v != "" {
			server = v
		}

		description := ""
		if v, ok := item["description"].(string); ok && v != "" {
			description = v
		} else if v, ok := item["Description"].(string); ok && v != "" {
			description = v
		}

		inputSchema := map[string]interface{}{}
		if v, ok := item["inputSchema"].(map[string]interface{}); ok {
			inputSchema = v
		} else if v, ok := item["input_schema"].(map[string]interface{}); ok {
			inputSchema = v
		}

		toolID := ""
		if v, ok := item["tool"].(string); ok && v != "" {
			toolID = v
		} else if v, ok := item["Tool"].(string); ok && v != "" {
			toolID = v
		}

		tools = append(tools, McpTool{
			Name:        name,
			Server:      server,
			Description: description,
			InputSchema: inputSchema,
			Tool:        toolID,
		})
	}

	return tools
}

// getSession retrieves session information by session ID (internal).
func (a *AgentBay) getSession(sessionID string) (*GetSessionResult, error) {
	getSessionRequest := &mcp.GetSessionRequest{
		Authorization: tea.String("Bearer " + a.APIKey),
		SessionId:     tea.String(sessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *getSessionRequest.SessionId)
	logAPICall("GetSession", requestParams)

	response, err := a.Client.GetSession(getSessionRequest)

	// Log API response
	if err != nil {
		// Check if this is an expected business error (e.g., session not found)
		errorStr := err.Error()
		if strings.Contains(errorStr, "InvalidMcpSession.NotFound") || strings.Contains(errorStr, "NotFound") {
			// This is an expected error - session doesn't exist
			// Use info level logging without stack trace, but with red color for visibility
			LogInfo(fmt.Sprintf("Session not found: %s", sessionID))
			LogDebug(fmt.Sprintf("GetSession error details: %s", errorStr))
			return &GetSessionResult{
				ApiResponse: models.ApiResponse{
					RequestID: "",
				},
				HttpStatusCode: 400,
				Code:           "InvalidMcpSession.NotFound",
				Success:        false,
				ErrorMessage:   fmt.Sprintf("Session %s not found", sessionID),
			}, nil
		} else {
			// This is an unexpected error - log with stack trace
			logOperationError("GetSession", err.Error(), true)
			return nil, err
		}
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	result := &GetSessionResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
	}

	if response != nil && response.Body != nil {
		if response.Body.HttpStatusCode != nil {
			result.HttpStatusCode = *response.Body.HttpStatusCode
		}
		if response.Body.Code != nil {
			result.Code = *response.Body.Code
		}
		if response.Body.Success != nil {
			result.Success = *response.Body.Success
		}

		// Check for API-level errors
		if !result.Success && response.Body.Code != nil {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			result.ErrorMessage = fmt.Sprintf("[%s] %s", code, message)
			logOperationError("GetSession", result.ErrorMessage, false)
			return result, nil
		}

		if response.Body.Data != nil {
			data := &GetSessionData{}
			if response.Body.Data.GetAppInstanceId() != nil {
				data.AppInstanceID = *response.Body.Data.GetAppInstanceId()
			}
			if response.Body.Data.GetResourceId() != nil {
				data.ResourceID = *response.Body.Data.GetResourceId()
			}
			if response.Body.Data.GetSessionId() != nil {
				data.SessionID = *response.Body.Data.GetSessionId()
			}
			if response.Body.Data.GetSuccess() != nil {
				data.Success = *response.Body.Data.GetSuccess()
			}
			if response.Body.Data.GetHttpPort() != nil {
				data.HttpPort = *response.Body.Data.GetHttpPort()
			}
			if response.Body.Data.GetNetworkInterfaceIp() != nil {
				data.NetworkInterfaceIP = *response.Body.Data.GetNetworkInterfaceIp()
			}
			if response.Body.Data.GetToken() != nil {
				data.Token = *response.Body.Data.GetToken()
			}
			if response.Body.Data.GetLinkUrl() != nil {
				data.LinkUrl = *response.Body.Data.GetLinkUrl()
			}
			if response.Body.Data.GetWsUrl() != nil {
				data.WsUrl = *response.Body.Data.GetWsUrl()
			}
			if response.Body.Data.GetVpcResource() != nil {
				data.VpcResource = *response.Body.Data.GetVpcResource()
			}
			if response.Body.Data.GetResourceUrl() != nil {
				data.ResourceUrl = *response.Body.Data.GetResourceUrl()
			}
			if response.Body.Data.GetStatus() != nil {
				data.Status = *response.Body.Data.GetStatus()
			}
			if response.Body.Data.GetToolList() != nil {
				if s, ok := response.Body.Data.GetToolList().(string); ok {
					data.ToolList = s
				} else {
					raw, err := json.Marshal(response.Body.Data.GetToolList())
					if err == nil {
						data.ToolList = string(raw)
					}
				}
			}
			// Extract contexts list from response
			if response.Body.Data.GetContexts() != nil {
				contexts := []ContextInfo{}
				for _, ctx := range response.Body.Data.GetContexts() {
					if ctx != nil {
						contextInfo := ContextInfo{}
						if ctx.GetName() != nil {
							contextInfo.Name = *ctx.GetName()
						}
						if ctx.GetId() != nil {
							contextInfo.ID = *ctx.GetId()
						}
						if contextInfo.Name != "" || contextInfo.ID != "" {
							contexts = append(contexts, contextInfo)
						}
					}
				}
				data.Contexts = contexts
			}
			result.Data = data

			// Log successful response
			keyFields := map[string]interface{}{
				"session_id":   data.SessionID,
				"resource_url": data.ResourceUrl,
				"resource_id":  data.ResourceID,
				"app_instance": data.AppInstanceID,
				"vpc_resource": data.VpcResource,
			}
			if data.HttpPort != "" {
				keyFields["http_port"] = data.HttpPort
			}
			if data.NetworkInterfaceIP != "" {
				keyFields["network_interface_ip"] = data.NetworkInterfaceIP
			}
			responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("GetSession", requestID, true, keyFields, string(responseJSON))
		}

		result.ErrorMessage = ""
	}

	return result, nil
}

// Get retrieves a session by its ID.
// This method calls the GetSession API and returns a SessionResult containing the Session object and request ID.
//
// Parameters:
//   - sessionID: The ID of the session to retrieve
//
// Returns:
//   - *SessionResult: Result containing the Session instance, request ID, and success status
//   - error: An error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	createResult, _ := client.Create(nil)
//	sessionID := createResult.Session.SessionID
//	result, _ := client.Get(sessionID)
//	defer result.Session.Delete()
func (a *AgentBay) Get(sessionID string) (*SessionResult, error) {
	if sessionID == "" {
		return &SessionResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: "session_id is required",
		}, nil
	}

	// Call GetSession API
	getResult, err := a.getSession(sessionID)
	if err != nil {
		errorMsg := fmt.Sprintf("failed to get session %s: %v", sessionID, err)
		logOperationError("Get", errorMsg, true)
		return &SessionResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: errorMsg,
		}, nil
	}

	// Check if the API call was successful
	if !getResult.Success {
		errorMsg := "unknown error"
		if getResult.Data != nil && !getResult.Data.Success {
			errorMsg = "Session not found"
		}
		fullErrorMsg := fmt.Sprintf("failed to get session %s: %s", sessionID, errorMsg)
		logOperationError("Get", fullErrorMsg, false)
		return &SessionResult{
			ApiResponse: models.ApiResponse{
				RequestID: getResult.RequestID,
			},
			Success:      false,
			ErrorMessage: fullErrorMsg,
		}, nil
	}

	// Create the Session object
	session := NewSession(a, sessionID)

	// Set VPC-related information and ResourceUrl from GetSession response
	if getResult.Data != nil {
		session.AppInstanceId = getResult.Data.AppInstanceID
		session.ResourceUrl = getResult.Data.ResourceUrl
		session.McpTools = parseToolListToMcpTools(getResult.Data.ToolList)
		session.Token = getResult.Data.Token
		session.LinkUrl = getResult.Data.LinkUrl
		session.WsUrl = getResult.Data.WsUrl
	}

	// Log successful retrieval
	keyFields := map[string]interface{}{
		"session_id":   sessionID,
		"resource_url": session.ResourceUrl,
	}
	if getResult.Data != nil {
		if getResult.Data.ResourceID != "" {
			keyFields["resource_id"] = getResult.Data.ResourceID
		}
	}
	logAPIResponseWithDetails("Get", getResult.RequestID, true, keyFields, "")

	return &SessionResult{
		ApiResponse: models.ApiResponse{
			RequestID: getResult.RequestID,
		},
		Success: true,
		Session: session,
	}, nil
}

// BetaPause synchronously pauses a session (beta), putting it into a dormant state to reduce resource usage and costs.
// BetaPause puts the session into a PAUSED state where computational resources are significantly reduced.
// The session state is preserved and can be resumed later to continue work.
//
// Note: This feature is currently in whitelist-only access.
// Contact agentbay_dev@alibabacloud.com to request access.
//
// Parameters:
//   - session: The session to pause.
//   - timeout: Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
//   - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.
//
// Returns:
//   - *models.SessionPauseResult: Result containing success status, request ID, and error message if any.
//   - error: Error if the operation fails at the transport level
//
// Behavior:
//
// - Delegates to session's BetaPause method for actual implementation
// - Returns detailed result with success status and request tracking
//
// Exceptions:
//
// - Returns error result (not Go error) for API-level errors like invalid session ID
// - Returns error result for timeout conditions
// - Returns Go error for transport-level failures
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	pauseResult, _ := client.BetaPause(result.Session, 300, 2.0)
//	client.BetaResume(result.Session, 300, 2.0)
func (ab *AgentBay) BetaPause(session *Session, timeout int, pollInterval float64) (*models.SessionPauseResult, error) {
	// Use default values if not provided
	if timeout <= 0 {
		timeout = 600
	}
	if pollInterval <= 0 {
		pollInterval = 2.0
	}

	// Call session's BetaPause method with provided parameters
	return session.BetaPause(timeout, pollInterval)
}

// BetaResume synchronously resumes a session (beta) from a paused state to continue work.
// BetaResume restores the session from PAUSED state back to RUNNING state.
// All previous session state and data are preserved during resume operation.
//
// Parameters:
//   - session: The session to resume.
//   - timeout: Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
//   - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.
//
// Returns:
//   - *models.SessionResumeResult: Result containing success status, request ID, and error message if any.
//   - error: Error if the operation fails at the transport level
//
// Behavior:
//
// - Delegates to session's BetaResume method for actual implementation
// - Returns detailed result with success status and request tracking
//
// Exceptions:
//
// - Returns error result (not Go error) for API-level errors like invalid session ID
// - Returns error result for timeout conditions
// - Returns Go error for transport-level failures
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	client.BetaPause(result.Session, 300, 2.0)
//	resumeResult, _ := client.BetaResume(result.Session, 300, 2.0)
func (ab *AgentBay) BetaResume(session *Session, timeout int, pollInterval float64) (*models.SessionResumeResult, error) {
	// Use default values if not provided
	if timeout <= 0 {
		timeout = 600
	}
	if pollInterval <= 0 {
		pollInterval = 2.0
	}

	// Call session's BetaResume method with provided parameters
	return session.BetaResume(timeout, pollInterval)
}

// GetRegionID returns the region ID from config
func (a *AgentBay) GetRegionID() string {
	return a.config.RegionID
}

// copyCreateSessionParams creates a deep copy of CreateSessionParams to avoid modifying the original object.
func (a *AgentBay) copyCreateSessionParams(params *CreateSessionParams) *CreateSessionParams {
	copy := &CreateSessionParams{
		ImageId:             params.ImageId,
		IdleReleaseTimeout:  params.IdleReleaseTimeout,
		PolicyId:            params.PolicyId,
		BetaNetworkId:       params.BetaNetworkId,
		Framework:           params.Framework,
		EnableBrowserReplay: params.EnableBrowserReplay,
		LoadSkills:          params.LoadSkills,
	}

	if params.LifecyclePolicy != nil {
		lpCopy := *params.LifecyclePolicy
		copy.LifecyclePolicy = &lpCopy
	}

	// Deep copy Labels map
	if params.Labels != nil {
		copy.Labels = make(map[string]string)
		for k, v := range params.Labels {
			copy.Labels[k] = v
		}
	}

	// Deep copy ContextSync slice
	if params.ContextSync != nil {
		copy.ContextSync = make([]*ContextSync, 0, len(params.ContextSync))
		for _, cs := range params.ContextSync {
			csCopy := &ContextSync{
				ContextID:             cs.ContextID,
				Path:                  cs.Path,
				BetaWaitForCompletion: cs.BetaWaitForCompletion,
			}
			// Copy Policy if it exists (assuming SyncPolicy is a struct that can be shallow copied)
			if cs.Policy != nil {
				csCopy.Policy = cs.Policy
			}
			copy.ContextSync = append(copy.ContextSync, csCopy)
		}
	}

	// Copy ExtraConfigs (shallow copy as it's a pointer to a complex struct)
	// If deep copy is needed, we would need to implement a deep copy method for ExtraConfigs
	copy.ExtraConfigs = params.ExtraConfigs

	// Copy BrowserContext (shallow copy is sufficient as it is immutable in typical usage)
	copy.BrowserContext = params.BrowserContext

	if params.SkillNames != nil {
		copy.SkillNames = make([]string, len(params.SkillNames))
		for i, name := range params.SkillNames {
			copy.SkillNames[i] = name
		}
	}

	return copy
}
