package agentbay

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"

	"math/rand"

	"github.com/alibabacloud-go/tea/dara"
	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/agent"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/browser"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/code"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/computer"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/env"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/filesystem"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/git"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/internal"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/mobile"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/pty"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/oss"
)

// SessionResult wraps Session object and RequestID
type SessionResult struct {
	models.ApiResponse
	Session      *Session
	Success      bool
	ErrorMessage string
}

// SessionListResult wraps Session list and RequestID
type SessionListResult struct {
	models.ApiResponse
	SessionIds []map[string]interface{} // Session objects with ID and status
	NextToken  string                   // Token for the next page
	MaxResults int32                    // Number of results per page
	TotalCount int32                    // Total number of results
}

// InfoResult wraps SessionInfo and RequestID
type InfoResult struct {
	models.ApiResponse
	Info *SessionInfo
}

// LabelResult wraps label operation result and RequestID
type LabelResult struct {
	models.ApiResponse
	Labels string
}

// LinkResult wraps link result and RequestID
type LinkResult struct {
	models.ApiResponse
	Link string
}

// DeleteResult wraps deletion operation result and RequestID
type DeleteResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// KeepAliveResult wraps keep-alive operation result and RequestID
type KeepAliveResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// McpTool represents an MCP tool with complete information
type McpTool struct {
	Name        string                 `json:"name"`        // Tool name
	Description string                 `json:"description"` // Tool description
	InputSchema map[string]interface{} `json:"inputSchema"` // Input parameter schema
	Server      string                 `json:"server"`      // Server name that provides this tool
	Tool        string                 `json:"tool"`        // Tool identifier
}

// GetName returns the tool name
func (m *McpTool) GetName() string {
	return m.Name
}

// GetServer returns the server name that provides this tool
func (m *McpTool) GetServer() string {
	return m.Server
}

// McpToolsResult wraps MCP tools list and RequestID
type McpToolsResult struct {
	models.ApiResponse
	Tools []McpTool
}

// SessionInfo contains information about a session.
type SessionInfo struct {
	SessionId            string
	ResourceUrl          string
	AppId                string
	AuthCode             string
	ConnectionProperties string
	ResourceId           string
	ResourceType         string
	Ticket               string
}

// Session represents a session in the AgentBay cloud environment.
//
// > **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.
type Session struct {
	AgentBay  *AgentBay
	SessionID string
	ImageId   string // ImageId used when creating this session
	McpTools  []McpTool

	// Application instance ID
	AppInstanceId string

	// Resource URL for accessing the session
	ResourceUrl string

	// LinkUrl-based direct tool call (non-VPC)
	Token   string
	LinkUrl string

	// WS URL for long connection (optional, for streaming output)
	WsUrl string

	wsClient *internal.WsClient

	// Shared HTTP client for LinkUrl calls (lazy initialized)
	linkHttpClient *http.Client

	// Browser replay enabled flag
	EnableBrowserReplay *bool

	// File, command and code handlers
	FileSystem *filesystem.FileSystem
	Command    *command.Command
	Code       *code.Code
	Oss        *oss.OSSManager

	// Git for version control
	Git *git.Git

	// Platform-specific automation modules
	Computer *computer.Computer
	Mobile   *mobile.Mobile

	// Browser for web automation
	Browser *browser.Browser

	// Agent for task execution
	Agent *agent.Agent

	Env *env.Env

	// Context management
	Context *ContextManager

	// PTY for interactive terminal sessions
	Pty *pty.Pty
}

func (s *Session) getLinkHttpClient() *http.Client {
	if s.linkHttpClient == nil {
		s.linkHttpClient = &http.Client{Timeout: 900 * time.Second}
	}
	return s.linkHttpClient
}

func (s *Session) GetWsUrl() string {
	return s.WsUrl
}

func (s *Session) GetMcpTools() []McpTool {
	return s.McpTools
}

func (s *Session) GetWsClient() (interface{}, error) {
	if s.WsUrl == "" {
		return nil, fmt.Errorf("ws url is not available for this session")
	}
	if s.Token == "" {
		return nil, fmt.Errorf("token is not available for WS connection")
	}
	if s.wsClient == nil {
		s.wsClient = internal.NewWsClient(s.WsUrl, s.Token, LogDebug)
	}
	if err := s.wsClient.Connect(); err != nil {
		return nil, err
	}
	return s.wsClient, nil
}

// SessionStatusResult represents the result of Session.GetStatus().
// It only contains status (no extra detail fields).
type SessionStatusResult struct {
	models.ApiResponse
	HttpStatusCode int32
	Code           string
	Success        bool
	Status         string
	ErrorMessage   string
}

// GetStatus retrieves basic session status for the current session.
// This method calls the GetSessionDetail API and returns status only.
func (s *Session) GetStatus() (*SessionStatusResult, error) {
	getSessionDetailRequest := &mcp.GetSessionDetailRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *getSessionDetailRequest.SessionId)
	logAPICall("GetSessionDetail", requestParams)

	response, err := s.GetClient().GetSessionDetail(getSessionDetailRequest)
	if err != nil {
		errorStr := err.Error()
		if strings.Contains(errorStr, "InvalidMcpSession.NotFound") || strings.Contains(errorStr, "NotFound") {
			LogInfo(fmt.Sprintf("Session not found: %s", s.SessionID))
			LogDebug(fmt.Sprintf("GetSessionDetail error details: %s", errorStr))
			return &SessionStatusResult{
				ApiResponse: models.ApiResponse{
					RequestID: "",
				},
				HttpStatusCode: 400,
				Code:           "InvalidMcpSession.NotFound",
				Success:        false,
				ErrorMessage:   fmt.Sprintf("Session %s not found", s.SessionID),
			}, nil
		}
		logOperationError("GetSessionDetail", err.Error(), true)
		return nil, err
	}

	requestID := models.ExtractRequestID(response)
	if requestID == "" && response != nil && response.Body != nil && response.Body.RequestId != nil {
		requestID = tea.StringValue(response.Body.RequestId)
	}
	if requestID == "" {
		// Some backends may omit RequestId for GetSessionDetail; keep it non-empty for diagnostics.
		requestID = fmt.Sprintf("get-session-detail-%d-%d", time.Now().UnixMilli(), rand.Intn(1000000000))
	}
	result := &SessionStatusResult{
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
			logOperationError("GetSessionDetail", result.ErrorMessage, false)
			return result, nil
		}

		if response.Body.Data != nil && response.Body.Data.GetStatus() != nil {
			result.Status = *response.Body.Data.GetStatus()
		}

		keyFields := map[string]interface{}{}
		if result.Status != "" {
			keyFields["status"] = result.Status
		}
		logAPIResponseWithDetails("GetSessionDetail", requestID, result.Success, keyFields, "")
	}

	return result, nil
}

// KeepAlive refreshes the backend idle timer for this session.
// It calls the RefreshSessionIdleTime API.
func (s *Session) KeepAlive() (*KeepAliveResult, error) {
	request := &mcp.RefreshSessionIdleTimeRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
	}

	logAPICall("RefreshSessionIdleTime", fmt.Sprintf("SessionId=%s", s.SessionID))

	response, err := s.GetClient().RefreshSessionIdleTime(request)
	if err != nil {
		logOperationError("RefreshSessionIdleTime", err.Error(), true)
		return &KeepAliveResult{
			ApiResponse: models.WithRequestID(""),
			Success:     false,
			ErrorMessage: fmt.Sprintf(
				"Failed to refresh session idle time for session %s: %v",
				s.SessionID,
				err,
			),
		}, nil
	}

	requestID := models.ExtractRequestID(response)
	if requestID == "" && response != nil && response.Body != nil && response.Body.RequestId != nil {
		requestID = tea.StringValue(response.Body.RequestId)
	}
	if requestID == "" {
		requestID = fmt.Sprintf("refresh-idle-%d-%d", time.Now().UnixMilli(), rand.Intn(1000000000))
	}

	if response != nil && response.Body != nil && response.Body.Success != nil && !*response.Body.Success {
		code := ""
		message := "Unknown error"
		if response.Body.Code != nil {
			code = tea.StringValue(response.Body.Code)
		}
		if response.Body.Message != nil && tea.StringValue(response.Body.Message) != "" {
			message = tea.StringValue(response.Body.Message)
		}
		errorMessage := message
		if code != "" {
			errorMessage = fmt.Sprintf("[%s] %s", code, message)
		}
		logOperationError("RefreshSessionIdleTime", errorMessage, false, requestID)
		return &KeepAliveResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: errorMessage,
		}, nil
	}

	logAPIResponseWithDetails(
		"RefreshSessionIdleTime",
		requestID,
		true,
		map[string]interface{}{"session_id": s.SessionID},
		"",
	)
	return &KeepAliveResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      true,
		ErrorMessage: "",
	}, nil
}

// NewSession creates a new Session object.
func NewSession(agentBay *AgentBay, sessionID string) *Session {
	session := &Session{
		AgentBay:  agentBay,
		SessionID: sessionID,
	}

	// Initialize filesystem, command and code handlers
	session.FileSystem = filesystem.NewFileSystem(session)
	session.Command = command.NewCommand(session)
	session.Code = code.NewCode(session)
	session.Oss = oss.NewOss(session)

	// Initialize Git
	session.Git = git.NewGit(session.Command)

	// Initialize Browser
	session.Browser = browser.NewBrowser(session)

	// Initialize platform-specific automation modules
	session.Computer = computer.NewComputer(session)
	session.Mobile = mobile.NewMobile(session)

	// Initialize Agent
	session.Agent = agent.NewAgent(session)

	session.Env = env.NewEnv(session, session)

	// Initialize context manager
	session.Context = NewContextManager(session)

	// Initialize PTY module
	session.Pty = pty.NewPty(session)

	return session
}

// Fs returns the FileSystem module (alias of FileSystem).
func (s *Session) Fs() *filesystem.FileSystem {
	return s.FileSystem
}

// Filesystem returns the FileSystem module (alias of FileSystem).
func (s *Session) Filesystem() *filesystem.FileSystem {
	return s.FileSystem
}

// Files returns the FileSystem module (alias of FileSystem).
func (s *Session) Files() *filesystem.FileSystem {
	return s.FileSystem
}

// GetFileUploadUrl returns a presigned upload URL for the given context and file path.
// This method implements the FileTransferCapableSession interface for lazy loading.
func (s *Session) GetFileUploadUrl(contextID string, filePath string) (bool, string, string, string, *int64, error) {
	result, err := s.AgentBay.Context.GetFileUploadUrl(contextID, filePath)
	if err != nil {
		return false, "", err.Error(), "", nil, err
	}
	return result.Success, result.Url, result.ErrorMessage, result.RequestID, result.ExpireTime, nil
}

// GetFileDownloadUrl returns a presigned download URL for the given context and file path.
// This method implements the FileTransferCapableSession interface for lazy loading.
func (s *Session) GetFileDownloadUrl(contextID string, filePath string) (bool, string, string, string, *int64, error) {
	result, err := s.AgentBay.Context.GetFileDownloadUrl(contextID, filePath)
	if err != nil {
		return false, "", err.Error(), "", nil, err
	}
	return result.Success, result.Url, result.ErrorMessage, result.RequestID, result.ExpireTime, nil
}

// GetAPIKey returns the API key for this session.
func (s *Session) GetAPIKey() string {
	return s.AgentBay.APIKey
}

// GetClient returns the HTTP client for this session.
func (s *Session) GetClient() *mcp.Client {
	return s.AgentBay.Client
}

// GetSessionId returns the session ID for this session.
func (s *Session) GetSessionId() string {
	return s.SessionID
}

// GetBrowser returns the Browser instance for this session.
func (s *Session) GetBrowser() *browser.Browser {
	return s.Browser
}

// LogDebug delegates to agentbay.LogDebug (implements agent.McpSessionLogger).
func (s *Session) LogDebug(msg string) {
	LogDebug(msg)
}

// LogInfo delegates to agentbay.LogInfo (implements agent.McpSessionLogger).
func (s *Session) LogInfo(msg string) {
	LogInfo(msg)
}

// LogWarn delegates to agentbay.LogWarn (implements agent.McpSessionLogger).
func (s *Session) LogWarn(msg string) {
	LogWarn(msg)
}

// LogError delegates to agentbay.LogError (implements agent.McpSessionLogger).
func (s *Session) LogError(msg string) {
	LogError(msg)
}

// GetImageID returns the image ID for this session.
func (s *Session) GetImageID() string {
	return s.ImageId
}

// GetSessionID returns the session ID for this session (browser interface method).
func (s *Session) GetSessionID() string {
	return s.SessionID
}

// GetEnableBrowserReplay returns whether browser replay is enabled for this session.
// Returns nil if not explicitly set (server default applies).
func (s *Session) GetEnableBrowserReplay() *bool {
	return s.EnableBrowserReplay
}

// GetToken returns the token for LinkUrl-based direct tool calls.
//
// Deprecated: Internal SDK use only. Will be removed in a future version.
func (s *Session) GetToken() string {
	return s.Token
}

// GetLinkUrl returns the LinkUrl for LinkUrl-based direct tool calls.
//
// Deprecated: Internal SDK use only. Will be removed in a future version.
func (s *Session) GetLinkUrl() string {
	return s.LinkUrl
}

// Wrapper methods for browser.SessionInterface compatibility

// CallMcpTool is a wrapper that converts the result to browser.McpToolResult
func (s *Session) CallMcpToolForBrowser(toolName string, args interface{}) (*browser.McpToolResult, error) {
	if toolName == "stopChrome" {
		result, err := s.CallMcpTool(toolName, args)
		if err != nil {
			return nil, err
		}
		return &browser.McpToolResult{
			Success:      result.Success,
			Data:         result.Data,
			ErrorMessage: result.ErrorMessage,
		}, nil
	}

	result, err := s.CallMcpTool(toolName, args)
	if err != nil {
		return nil, err
	}

	// Convert models.McpToolResult to browser.McpToolResult
	return &browser.McpToolResult{
		Success:      result.Success,
		Data:         result.Data,
		ErrorMessage: result.ErrorMessage,
	}, nil
}

// GetLinkForBrowser is a wrapper that converts the result to browser.LinkResult
func (s *Session) GetLinkForBrowser(protocolType *string, port *int32, options *string) (*browser.LinkResult, error) {
	result, err := s.GetLink(protocolType, port, options)
	if err != nil {
		return nil, err
	}

	// Convert LinkResult to browser.LinkResult
	return &browser.LinkResult{
		Link: result.Link,
	}, nil
}

// GetCommand returns the command handler for this session.
func (s *Session) GetCommand() *command.Command {
	return s.Command
}

// Delete deletes this session.
// Delete deletes the session and releases all associated resources.
//
// Parameters:
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
// - Releases all associated resources (browser, computer, mobile, etc.)
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	deleteResult, _ := result.Session.Delete()
func (s *Session) Delete(syncContext ...bool) (*DeleteResult, error) {
	userRequestedSync := len(syncContext) > 0 && syncContext[0]

	// Perform context synchronization if needed
	if userRequestedSync {
		syncStartTime := time.Now()

		// Sync all contexts
		syncResult, err := s.Context.SyncWithCallback("", "", "", nil, 150, 1500)
		LogInfo("Synced all contexts")

		if err != nil {
			syncDuration := time.Since(syncStartTime)
			logOperationError("Delete", fmt.Sprintf("Failed to trigger context sync after %v: %v", syncDuration, err), false)
			// Continue with deletion even if sync fails
		} else {
			syncDuration := time.Since(syncStartTime)
			if syncResult.Success {
				// Context sync successful
				_ = syncDuration
			} else {
				// Context sync failed, continue with deletion
				_ = syncDuration
			}
		}
	}

	// Proceed with session deletion using DeleteSessionAsync
	deleteSessionRequest := &mcp.DeleteSessionAsyncRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *deleteSessionRequest.SessionId)
	logAPICall("DeleteSessionAsync", requestParams)

	response, err := s.GetClient().DeleteSessionAsync(deleteSessionRequest)

	// Log API response
	if err != nil {
		logOperationError("DeleteSessionAsync", err.Error(), true)
		return &DeleteResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to delete session %s: %v", s.SessionID, err),
		}, nil
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)
	if requestID == "" && response != nil && response.Body != nil && response.Body.RequestId != nil {
		requestID = tea.StringValue(response.Body.RequestId)
	}
	if requestID == "" {
		// Last resort: keep it non-empty for diagnostics even if server didn't provide it.
		requestID = fmt.Sprintf("delete-%d-%d", time.Now().UnixMilli(), rand.Intn(1000000000))
	}

	// Check if the response is success
	if response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			errorMsg := "Failed to delete session"
			if response.Body.Code != nil && response.Body.Message != nil {
				errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
			} else if response.Body.Code != nil {
				errorMsg = fmt.Sprintf("[%s] Failed to delete session", *response.Body.Code)
			}
			responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("DeleteSessionAsync", requestID, false, nil, string(responseJSON))
			return &DeleteResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ErrorMessage: errorMsg,
			}, nil
		}
	}

	// Poll for session deletion status
	LogInfo(fmt.Sprintf("Waiting for session %s to be deleted... (DeleteRequestId=%s)", s.SessionID, requestID))
	pollTimeout := 5 * time.Minute  // 5 minutes timeout
	pollInterval := 1 * time.Second // Poll every 1 second
	pollStartTime := time.Now()
	pollCount := 0

	for {
		pollCount++
		// Check timeout
		elapsedTime := time.Since(pollStartTime)
		if elapsedTime >= pollTimeout {
			errorMsg := fmt.Sprintf("Timeout waiting for session deletion after %v", pollTimeout)
			LogInfo(errorMsg)
			return &DeleteResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ErrorMessage: errorMsg,
			}, nil
		}

		// Get session status
		statusResult, err := s.GetStatus()

		// Check if session is deleted (NotFound error)
		if err != nil {
			// If GetSessionDetail returns an error, it might be NotFound
			errorStr := err.Error()
			if strings.Contains(errorStr, "InvalidMcpSession.NotFound") || strings.Contains(errorStr, "NotFound") {
				// Session is deleted
				LogInfo(fmt.Sprintf("Session %s successfully deleted (NotFound)", s.SessionID))
				break
			} else {
				// Other error, continue polling
				LogDebug(fmt.Sprintf("Get session error (will retry): %v", err))
				// Continue to next poll iteration
			}
		} else if statusResult != nil && !statusResult.Success {
			errorCode := statusResult.Code
			errorMessage := statusResult.ErrorMessage
			httpStatusCode := statusResult.HttpStatusCode

			// Check for InvalidMcpSession.NotFound, 400 with "not found", or error_message containing "not found"
			isNotFound := errorCode == "InvalidMcpSession.NotFound" ||
				(httpStatusCode == 400 && (strings.Contains(strings.ToLower(errorMessage), "not found") ||
					strings.Contains(errorMessage, "NotFound") ||
					strings.Contains(strings.ToLower(errorCode), "not found"))) ||
				strings.Contains(strings.ToLower(errorMessage), "not found")

			if isNotFound {
				// Session is deleted
				LogInfo(fmt.Sprintf("Session %s successfully deleted (NotFound)", s.SessionID))
				break
			} else {
				// Other error, continue polling
				LogDebug(fmt.Sprintf("Get session error (will retry): %s", errorMessage))
				// Continue to next poll iteration
			}
		} else if statusResult != nil && statusResult.Status != "" {
			// Check session status if we got valid data
			status := statusResult.Status
			// Print at info level so users can see progress even if debug logs are disabled.
			LogInfo(fmt.Sprintf("Session status: %s (DeleteRequestId=%s, GetStatusRequestId=%s)", status, requestID, statusResult.RequestID))
			// Treat DELETED as terminal too. Some backends never return FINISH for delete.
			if status == "FINISH" || status == "DELETED" {
				LogInfo(fmt.Sprintf("Session %s successfully deleted (status=%s, DeleteRequestId=%s)", s.SessionID, status, requestID))
				break
			}
			// Additional hint if stuck in DELETING for a long time.
			if status == "DELETING" && pollCount%30 == 0 {
				LogInfo(fmt.Sprintf("Session still deleting... (elapsed=%v, DeleteRequestId=%s)", elapsedTime.Truncate(time.Second), requestID))
			}
		}

		// Wait before next poll
		time.Sleep(pollInterval)
	}

	// Log successful deletion
	keyFields := map[string]interface{}{
		"session_id": s.SessionID,
	}
	logAPIResponseWithDetails("DeleteSessionAsync", requestID, true, keyFields, "")

	// Return success result with request ID
	return &DeleteResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success: true,
	}, nil
}

// ValidateLabels validates labels parameter for label operations.
// Returns error message if validation fails, empty string if validation passes
func (s *Session) ValidateLabels(labels map[string]string) string {
	// Check if labels is nil
	if labels == nil {
		return "Labels cannot be nil. Please provide a valid labels map."
	}

	// Check if labels map is empty
	if len(labels) == 0 {
		return "Labels cannot be empty. Please provide at least one label."
	}

	for key, value := range labels {
		// Check key validity
		if key == "" || len(strings.TrimSpace(key)) == 0 {
			return "Label keys cannot be empty. Please provide valid keys."
		}

		// Check value validity
		if value == "" || len(strings.TrimSpace(value)) == 0 {
			return "Label values cannot be empty. Please provide valid values."
		}
	}

	// Validation passed
	return ""
}

// SetLabels sets the labels for this session.
//
// Parameters:
//   - labels: Labels to set for the session as a map of key-value pairs
//
// Returns:
//   - *LabelResult: Result containing request ID
//   - error: Error if validation fails or operation fails
//
// Behavior:
//
// - Validates that labels map is not nil or empty
// - All keys and values must be non-empty strings
// - Converts labels to JSON and sends to the backend
// - Labels can be used for session filtering and organization
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	labels := map[string]string{"env": "test"}
//	labelResult, _ := result.Session.SetLabels(labels)
func (s *Session) SetLabels(labels map[string]string) (*LabelResult, error) {
	// Validate labels using the validation function
	if validationError := s.ValidateLabels(labels); validationError != "" {
		return &LabelResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Labels: "",
		}, fmt.Errorf("%s", validationError)
	}

	// Convert labels to JSON string
	labelsJSON, err := json.Marshal(labels)
	if err != nil {
		return &LabelResult{
			ApiResponse: models.ApiResponse{
				RequestID: "",
			},
			Labels: "",
		}, fmt.Errorf("failed to marshal labels to JSON: %v", err)
	}

	setLabelRequest := &mcp.SetLabelRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		Labels:        tea.String(string(labelsJSON)),
		SessionId:     tea.String(s.SessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s, Labels=%s", *setLabelRequest.SessionId, *setLabelRequest.Labels)
	logAPICall("SetLabel", requestParams)

	response, err := s.GetClient().SetLabel(setLabelRequest)

	// Log API response
	if err != nil {
		logOperationError("SetLabel", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log successful response
	keyFields := map[string]interface{}{
		"session_id":   s.SessionID,
		"labels_count": len(labels),
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("SetLabel", requestID, true, keyFields, string(responseJSON))

	return &LabelResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Labels: string(labelsJSON),
	}, nil
}

// GetLabels gets the labels for this session.
//
// Returns:
//   - *LabelResult: Result containing labels as JSON string and request ID
//   - error: Error if the operation fails
//
// Behavior:
//
// - Retrieves the labels that were previously set for this session
// - Returns labels as a JSON string
// - Can be used to identify and filter sessions
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	labelResult, _ := result.Session.GetLabels()
func (s *Session) GetLabels() (*LabelResult, error) {
	getLabelRequest := &mcp.GetLabelRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *getLabelRequest.SessionId)
	logAPICall("GetLabel", requestParams)

	response, err := s.GetClient().GetLabel(getLabelRequest)

	// Log API response
	if err != nil {
		logOperationError("GetLabel", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	var labels string
	var labelsCount int = 0
	if response != nil && response.Body != nil && response.Body.Data != nil && response.Body.Data.Labels != nil {
		labels = *response.Body.Data.Labels
		// Parse labels to count them
		var labelsMap map[string]interface{}
		if err := json.Unmarshal([]byte(labels), &labelsMap); err == nil {
			labelsCount = len(labelsMap)
		}
	}

	// Log successful response
	keyFields := map[string]interface{}{
		"session_id":   s.SessionID,
		"labels_count": labelsCount,
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("GetLabel", requestID, true, keyFields, string(responseJSON))

	return &LabelResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Labels: labels,
	}, nil
}

// GetLink gets the link for this session.
// GetLink retrieves an access link for the session.
//
// Parameters:
//   - protocolType: Protocol type for the link (optional, reserved for future use)
//   - port: Specific port number to access (default open range: [30100, 30199]; other ports require whitelist approval via agentbay_dev@alibabacloud.com)
//   - options: Additional options (optional)
//
// Returns:
//   - *LinkResult: Result containing the access URL and request ID
//   - error: Error if port is out of range or operation fails
//
// Behavior:
//
// - Without port: Returns the default session access URL
// - With port: Returns URL for accessing specific port-mapped service
// - Default open port range: [30100, 30199]; other ports require whitelist approval
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	port := int32(30100)
//	linkResult, _ := result.Session.GetLink(nil, &port, nil)
func (s *Session) GetLink(protocolType *string, port *int32, options *string) (*LinkResult, error) {
	getLinkRequest := &mcp.GetLinkRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
		ProtocolType:  protocolType,
		Port:          port,
		Option:        options,
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *getLinkRequest.SessionId)
	if getLinkRequest.ProtocolType != nil {
		requestParams += fmt.Sprintf(", ProtocolType=%s", *getLinkRequest.ProtocolType)
	}
	if getLinkRequest.Port != nil {
		requestParams += fmt.Sprintf(", Port=%d", *getLinkRequest.Port)
	}
	if getLinkRequest.Option != nil {
		requestParams += ", Options=provided"
	}
	logAPICall("GetLink", requestParams)

	response, err := s.GetClient().GetLink(getLinkRequest)

	// Log API response
	if err != nil {
		logOperationError("GetLink", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	var link string
	if response != nil && response.Body != nil && response.Body.Data != nil {
		data := response.Body.Data
		if data.Url != nil {
			link = *data.Url
		}
	}

	// Log successful response
	keyFields := map[string]interface{}{
		"session_id": s.SessionID,
		"url":        link,
	}
	if getLinkRequest.ProtocolType != nil {
		keyFields["protocol_type"] = *getLinkRequest.ProtocolType
	}
	if getLinkRequest.Port != nil {
		keyFields["port"] = *getLinkRequest.Port
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("GetLink", requestID, true, keyFields, string(responseJSON))

	return &LinkResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Link: link,
	}, nil
}

// Info gets information about this session.
// Info retrieves detailed information about the current session.
//
// Returns:
//   - *InfoResult: Result containing SessionInfo object and request ID
//   - error: Error if the operation fails or session not found
//
// Behavior:
//
// - Retrieves current session metadata from the backend
// - Includes resource URL, type, and connection properties
// - Information is fetched in real-time from the API
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	infoResult, _ := result.Session.Info()
func (s *Session) Info() (*InfoResult, error) {
	getMcpResourceRequest := &mcp.GetMcpResourceRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		SessionId:     tea.String(s.SessionID),
	}

	// Log API request
	requestParams := fmt.Sprintf("SessionId=%s", *getMcpResourceRequest.SessionId)
	logAPICall("GetMcpResource", requestParams)

	response, err := s.GetClient().GetMcpResource(getMcpResourceRequest)

	// Log API response
	if err != nil {
		// Check if this is an expected business error (e.g., session not found)
		errorStr := err.Error()
		errorCode := ""

		// Try to extract error code from the error
		if strings.Contains(errorStr, "InvalidMcpSession.NotFound") || strings.Contains(errorStr, "NotFound") {
			errorCode = "InvalidMcpSession.NotFound"
		}

		if errorCode == "InvalidMcpSession.NotFound" {
			// This is an expected error - session doesn't exist
			// Use info level logging without stack trace, but with red color for visibility
			LogInfo(fmt.Sprintf("Session not found: %s", s.SessionID))
			LogDebug(fmt.Sprintf("GetMcpResource error details: %s", errorStr))
			return &InfoResult{
				ApiResponse: models.ApiResponse{
					RequestID: "",
				},
				Info: nil,
			}, fmt.Errorf("Session %s not found", s.SessionID)
		}

		// This is an unexpected error - log with full error
		logOperationError("GetMcpResource", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	if response != nil && response.Body != nil && response.Body.Data != nil {
		sessionInfo := &SessionInfo{
			SessionId:            "",
			ResourceUrl:          "",
			AppId:                "",
			AuthCode:             "",
			ConnectionProperties: "",
			ResourceId:           "",
			ResourceType:         "",
			Ticket:               "",
		}

		if response.Body.Data.SessionId != nil {
			sessionInfo.SessionId = *response.Body.Data.SessionId
		}

		if response.Body.Data.ResourceUrl != nil {
			sessionInfo.ResourceUrl = *response.Body.Data.ResourceUrl
		}

		// Transfer DesktopInfo fields to SessionInfo
		if response.Body.Data.DesktopInfo != nil {
			if response.Body.Data.DesktopInfo.AppId != nil {
				sessionInfo.AppId = *response.Body.Data.DesktopInfo.AppId
			}
			if response.Body.Data.DesktopInfo.AuthCode != nil {
				sessionInfo.AuthCode = *response.Body.Data.DesktopInfo.AuthCode
			}
			if response.Body.Data.DesktopInfo.ConnectionProperties != nil {
				sessionInfo.ConnectionProperties = *response.Body.Data.DesktopInfo.ConnectionProperties
			}
			if response.Body.Data.DesktopInfo.ResourceId != nil {
				sessionInfo.ResourceId = *response.Body.Data.DesktopInfo.ResourceId
			}
			if response.Body.Data.DesktopInfo.ResourceType != nil {
				sessionInfo.ResourceType = *response.Body.Data.DesktopInfo.ResourceType
			}
			if response.Body.Data.DesktopInfo.Ticket != nil {
				sessionInfo.Ticket = *response.Body.Data.DesktopInfo.Ticket
			}
		}

		// Log successful response
		keyFields := map[string]interface{}{
			"session_id":    sessionInfo.SessionId,
			"resource_url":  sessionInfo.ResourceUrl,
			"resource_type": sessionInfo.ResourceType,
		}
		if sessionInfo.AppId != "" {
			keyFields["app_id"] = sessionInfo.AppId
		}
		if sessionInfo.ResourceId != "" {
			keyFields["resource_id"] = sessionInfo.ResourceId
		}
		responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("GetMcpResource", requestID, true, keyFields, string(responseJSON))

		return &InfoResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Info: sessionInfo,
		}, nil
	}

	return nil, fmt.Errorf("failed to get session info: empty response data")
}

// ListMcpTools lists MCP tools available for this session.
// It uses the ImageId from the session creation, or "linux_latest" as default.
//
// Returns:
//   - *McpToolsResult: Result containing list of MCP tools and request ID
//   - error: Error if the operation fails
//
// Behavior:
//
// - Uses the ImageId from session creation
// - Defaults to "linux_latest" if ImageId is empty
// - Retrieves all available MCP tools for the specified image
// - Does not store tools on the Session (no caching)
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	toolsResult, _ := result.Session.ListMcpTools()
func (s *Session) ListMcpTools() (*McpToolsResult, error) {
	// Use session's ImageId, or default to "linux_latest" if empty
	imageId := s.ImageId
	if imageId == "" {
		imageId = "linux_latest"
	}

	listMcpToolsRequest := &mcp.ListMcpToolsRequest{
		Authorization: tea.String("Bearer " + s.GetAPIKey()),
		ImageId:       tea.String(imageId),
	}

	// Log API request
	requestParams := fmt.Sprintf("ImageId=%s", *listMcpToolsRequest.ImageId)
	logAPICall("ListMcpTools", requestParams)

	response, err := s.GetClient().ListMcpTools(listMcpToolsRequest)

	// Log API response
	if err != nil {
		logOperationError("ListMcpTools", err.Error(), true)
		return nil, err
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Parse the response data
	var tools []McpTool
	if response != nil && response.Body != nil && response.Body.Data != nil {
		// The Data field is a JSON string, so we need to unmarshal it
		var toolsData []map[string]interface{}
		if err := json.Unmarshal([]byte(*response.Body.Data), &toolsData); err != nil {
			logOperationError("ListMcpTools", fmt.Sprintf("Error unmarshaling tools data: %v", err), false)
			return &McpToolsResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Tools: []McpTool{},
			}, nil
		}

		// Convert the parsed data to McpTool structs
		for _, toolData := range toolsData {
			tool := McpTool{}
			if name, ok := toolData["name"].(string); ok {
				tool.Name = name
			}
			if description, ok := toolData["description"].(string); ok {
				tool.Description = description
			}
			if inputSchema, ok := toolData["inputSchema"].(map[string]interface{}); ok {
				tool.InputSchema = inputSchema
			}
			if server, ok := toolData["server"].(string); ok {
				tool.Server = server
			}
			if toolIdentifier, ok := toolData["tool"].(string); ok {
				tool.Tool = toolIdentifier
			}
			tools = append(tools, tool)
		}
	}

	// Do not store MCP tool lists in Session.

	// Log successful response
	keyFields := map[string]interface{}{
		"image_id":    imageId,
		"tools_count": len(tools),
	}
	responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("ListMcpTools", requestID, true, keyFields, string(responseJSON))

	return &McpToolsResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Tools: tools,
	}, nil
}

func (s *Session) getMcpServerForTool(toolName string) string {
	return s.GetMcpServerForTool(toolName)
}

// GetMcpServerForTool returns the MCP server name that provides the given tool.
func (s *Session) GetMcpServerForTool(toolName string) string {
	for _, tool := range s.McpTools {
		if tool.Name == toolName && tool.Server != "" {
			return tool.Server
		}
	}
	return ""
}

// AppendMcpTool adds an MCP tool entry to the session's tool list.
func (s *Session) AppendMcpTool(name, server string) {
	s.McpTools = append(s.McpTools, McpTool{Name: name, Server: server})
}

// CallMcpTool calls an MCP tool using the OpenAPI route.
//
// This is the unified public API for calling MCP tools. All feature modules
// (Command, Code, Agent, etc.) use this method internally.
//
// Parameters:
//   - toolName: Name of the MCP tool to call
//   - args: Arguments to pass to the tool (typically a map or struct)
//   - autoGenSession: Optional boolean to auto-generate session if not exists (default: false)
//
// Returns:
//   - *models.McpToolResult: Result containing:
//   - Success: Whether the tool call was successful
//   - Data: Tool output data (text content extracted from response)
//   - ErrorMessage: Error message if the call failed
//   - RequestID: Unique identifier for the API request
//   - error: Error if the call fails at the transport level
//
// Behavior:
//
// - Uses traditional API calls
// - Parses response data to extract text content from content[0].text
// - Handles the isError flag in responses
// - Returns structured error information
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	args := map[string]interface{}{"command": "ls -la"}
//	toolResult, _ := result.Session.CallMcpTool("execute_command", args)

func (s *Session) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error) {
	serverName := s.getMcpServerForTool(toolName)
	// Normalize press_keys arguments for better case compatibility
	if toolName == "press_keys" {
		// Try to extract and normalize the keys field
		if argsMap, ok := args.(map[string]interface{}); ok {
			if keys, exists := argsMap["keys"]; exists {
				if keysArray, isArray := keys.([]interface{}); isArray {
					// Convert []interface{} to []string
					keysStr := make([]string, 0, len(keysArray))
					for _, k := range keysArray {
						if keyStr, isString := k.(string); isString {
							keysStr = append(keysStr, keyStr)
						}
					}
					// Normalize keys
					normalizedKeys := NormalizeKeys(keysStr)
					// Convert back to []interface{}
					normalizedKeysInterface := make([]interface{}, len(normalizedKeys))
					for i, k := range normalizedKeys {
						normalizedKeysInterface[i] = k
					}
					// Create a copy of args to avoid modifying the original
					argsCopy := make(map[string]interface{})
					for k, v := range argsMap {
						argsCopy[k] = v
					}
					argsCopy["keys"] = normalizedKeysInterface
					args = argsCopy
					LogDebug(fmt.Sprintf("Normalized press_keys arguments: %v", argsCopy))
				}
			}
		}
	}

	// Marshal arguments to JSON
	argsJSON, err := json.Marshal(args)
	if err != nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("Failed to marshal args: %v", err),
			RequestID:    "",
		}, nil
	}

	// Prefer LinkUrl-based direct tool call when LinkUrl/Token are present.
	// LinkUrl route requires explicit server name. If it's not available,
	// fall back to API-based call to let backend resolve the server.
	if s.LinkUrl != "" && s.Token != "" && serverName != "" {
		return s.callMcpToolLinkUrl(toolName, args, serverName)
	}

	// Use traditional API call
	return s.callMcpToolAPI(toolName, string(argsJSON), false, serverName)
}

// callMcpToolLinkUrl handles MCP tool calls via LinkUrl direct connection (POST JSON).
func (s *Session) callMcpToolLinkUrl(toolName string, args interface{}, serverName string) (*models.McpToolResult, error) {
	if serverName == "" {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("server not found for tool: %s", toolName),
			RequestID:    "",
		}, nil
	}

	linkUrl := s.LinkUrl
	token := s.Token
	if linkUrl == "" || token == "" {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: "linkUrl/token not available",
			RequestID:    "",
		}, nil
	}

	requestID := fmt.Sprintf("link-%d-%09d", time.Now().UnixMilli(), rand.Intn(1000000000))
	logAPICall("CallMcpTool(LinkUrl)", fmt.Sprintf("Tool=%s, RequestId=%s", toolName, requestID))

	payload := map[string]interface{}{
		"args":      args,
		"server":    serverName,
		"requestId": requestID,
		"tool":      toolName,
		"token":     token,
	}
	bodyBytes, err := json.Marshal(payload)
	if err != nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("failed to marshal payload: %v", err),
			RequestID:    requestID,
		}, nil
	}

	req, err := http.NewRequest("POST", strings.TrimRight(linkUrl, "/")+"/callTool", bytes.NewReader(bodyBytes))
	if err != nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("failed to create request: %v", err),
			RequestID:    requestID,
		}, nil
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Access-Token", token)

	resp, err := s.getLinkHttpClient().Do(req)
	if err != nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("HTTP request failed: %v", err),
			RequestID:    requestID,
		}, nil
	}
	defer resp.Body.Close()

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		b, _ := io.ReadAll(io.LimitReader(resp.Body, 8192))
		logAPIResponseWithDetails(
			"CallMcpTool(LinkUrl) Response",
			requestID,
			false,
			map[string]interface{}{
				"http_status": resp.StatusCode,
				"tool_name":   toolName,
			},
			string(b),
		)
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("HTTP request failed with code: %d", resp.StatusCode),
			RequestID:    requestID,
		}, nil
	}

	var outer map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&outer); err != nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("failed to decode response: %v", err),
			RequestID:    requestID,
		}, nil
	}

	dataField, ok := outer["data"]
	if !ok || dataField == nil {
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: "No data field in LinkUrl response",
			RequestID:    requestID,
		}, nil
	}

	var parsedData map[string]interface{}
	switch v := dataField.(type) {
	case string:
		if err := json.Unmarshal([]byte(v), &parsedData); err != nil {
			return &models.McpToolResult{
				Success:      false,
				Data:         "",
				ErrorMessage: fmt.Sprintf("failed to parse data field JSON: %v", err),
				RequestID:    requestID,
			}, nil
		}
	case map[string]interface{}:
		parsedData = v
	default:
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: "Invalid data field type in LinkUrl response",
			RequestID:    requestID,
		}, nil
	}

	resultField, ok := parsedData["result"].(map[string]interface{})
	if !ok || resultField == nil {
		logAPIResponseWithDetails(
			"CallMcpTool(LinkUrl) Response",
			requestID,
			false,
			map[string]interface{}{
				"tool_name": toolName,
			},
			"missing result field",
		)
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: "No result field in LinkUrl response data",
			RequestID:    requestID,
		}, nil
	}

	isError := false
	if v, exists := resultField["isError"]; exists {
		if b, ok := v.(bool); ok {
			isError = b
		}
	}

	textContent := s.extractTextContentFromResponse(resultField)
	keyFields := map[string]interface{}{
		"tool_name": toolName,
		"server":    serverName,
		"is_error":  isError,
		"data_len":  len(textContent),
	}
	if isError {
		logAPIResponseWithDetails(
			"CallMcpTool(LinkUrl) Response",
			requestID,
			false,
			keyFields,
			textContent,
		)
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: textContent,
			RequestID:    requestID,
		}, nil
	}

	logAPIResponseWithDetails(
		"CallMcpTool(LinkUrl) Response",
		requestID,
		true,
		keyFields,
		"",
	)
	return &models.McpToolResult{
		Success:      true,
		Data:         textContent,
		ErrorMessage: "",
		RequestID:    requestID,
	}, nil
}

// GetMetrics retrieves runtime metrics for this session.
//
// The underlying service returns a JSON string. This method parses it and returns structured metrics.
func (s *Session) GetMetrics() (*models.SessionMetricsResult, error) {
	toolResult, err := s.CallMcpTool("get_metrics", map[string]interface{}{})
	if err != nil {
		return &models.SessionMetricsResult{
			Success:      false,
			Metrics:      nil,
			Raw:          nil,
			ErrorMessage: err.Error(),
		}, err
	}

	return models.ParseSessionMetrics(toolResult), nil
}

// callMcpToolAPI handles traditional API-based MCP tool calls
func (s *Session) callMcpToolAPI(toolName, argsJSON string, autoGenSession bool, serverName string) (*models.McpToolResult, error) {
	// Helper function to convert string to *string
	stringPtr := func(s string) *string { return &s }
	boolPtr := func(b bool) *bool { return &b }

	callToolRequest := &mcp.CallMcpToolRequest{
		Authorization:  stringPtr(fmt.Sprintf("Bearer %s", s.GetAPIKey())),
		SessionId:      stringPtr(s.SessionID),
		Name:           stringPtr(toolName),
		Args:           stringPtr(argsJSON),
		AutoGenSession: boolPtr(autoGenSession),
		ExternalUserId: stringPtr(""),
		ImageId:        stringPtr(""),
	}
	if serverName != "" {
		callToolRequest.Server = stringPtr(serverName)
	}

	// Log API request
	requestParams := fmt.Sprintf("Tool=%s, SessionId=%s, ArgsLength=%d", toolName, s.SessionID, len(argsJSON))
	logAPICall("CallMcpTool", requestParams)

	response, err := s.GetClient().CallMcpTool(callToolRequest)

	// Log API response
	if err != nil {
		logOperationError("CallMcpTool", fmt.Sprintf("API request failed: %v", err), true)
		return &models.McpToolResult{
			Success:      false,
			Data:         "",
			ErrorMessage: fmt.Sprintf("API request failed: %v", err),
			RequestID:    "",
		}, nil
	}

	// Extract request ID
	requestID := ""
	if response.Body != nil && response.Body.GetRequestId() != nil {
		requestID = *response.Body.GetRequestId()
	}

	// Check for API-level errors
	if response.Body != nil && response.Body.Data != nil {
		// Log successful response
		var responseLength int = 0
		if dataStr, ok := response.Body.Data.(string); ok {
			responseLength = len(dataStr)
		}

		keyFields := map[string]interface{}{
			"tool_name":       toolName,
			"session_id":      s.SessionID,
			"response_length": responseLength,
		}
		responseJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("CallMcpTool", requestID, true, keyFields, string(responseJSON))

		// For run_code tool, extract and log the actual code execution output
		if toolName == "run_code" && response.Body.Data != nil {
			var dataStr string
			if str, ok := response.Body.Data.(string); ok {
				dataStr = str
			} else if dataBytes, err := json.Marshal(response.Body.Data); err == nil {
				dataStr = string(dataBytes)
			}
			if dataStr != "" {
				logCodeExecutionOutput(requestID, dataStr)
			}
		}

		// Parse response data to extract text content
		var dataObj map[string]interface{}
		if str, ok := response.Body.Data.(string); ok {
			// If data is a string, try to parse it as JSON
			if err := json.Unmarshal([]byte(str), &dataObj); err != nil {
				// If parsing fails, return the raw string
				return &models.McpToolResult{
					Success:      true,
					Data:         str,
					ErrorMessage: "",
					RequestID:    requestID,
				}, nil
			}
		} else if obj, ok := response.Body.Data.(map[string]interface{}); ok {
			// If data is already a map, use it directly
			dataObj = obj
		} else {
			// For other types, try to marshal and unmarshal
			if dataBytes, err := json.Marshal(response.Body.Data); err == nil {
				if err := json.Unmarshal(dataBytes, &dataObj); err != nil {
					// If parsing fails, return the marshaled string
					return &models.McpToolResult{
						Success:      true,
						Data:         string(dataBytes),
						ErrorMessage: "",
						RequestID:    requestID,
					}, nil
				}
			}
		}

		// Extract text content from the parsed data
		textContent := s.extractTextContentFromResponse(dataObj)

		// Check for errors in the response
		isError := false
		if isErrorVal, exists := dataObj["isError"]; exists {
			if isErrorBool, ok := isErrorVal.(bool); ok {
				isError = isErrorBool
			}
		}

		if isError {
			logOperationError("CallMcpTool", fmt.Sprintf("Tool returned error: %s", textContent), false, requestID)
			return &models.McpToolResult{
				Success:      false,
				Data:         "",
				ErrorMessage: textContent,
				RequestID:    requestID,
			}, nil
		}

		return &models.McpToolResult{
			Success:      true,
			Data:         textContent,
			ErrorMessage: "",
			RequestID:    requestID,
		}, nil
	}

	// Handle empty or error response
	errorMsg := "Empty response from CallMcpTool"
	logOperationError("CallMcpTool", errorMsg, false)
	return &models.McpToolResult{
		Success:      false,
		Data:         "",
		ErrorMessage: errorMsg,
		RequestID:    requestID,
	}, nil
}

// extractTextContentFromResponse extracts text content from various response formats
func (s *Session) extractTextContentFromResponse(data interface{}) string {
	if data == nil {
		return ""
	}

	// Try to extract text from different response formats
	if dataMap, ok := data.(map[string]interface{}); ok {
		// Check for content array first
		if content, exists := dataMap["content"]; exists {
			if contentArray, isArray := content.([]interface{}); isArray && len(contentArray) > 0 {
				if v, ok := contentArray[0].(string); ok && v != "" {
					return v
				}
				if contentItem, isMap := contentArray[0].(map[string]interface{}); isMap {
					if v, ok := contentItem["text"].(string); ok && v != "" {
						return v
					}
					if v, ok := contentItem["blob"].(string); ok && v != "" {
						return v
					}
					if v, ok := contentItem["data"].(string); ok && v != "" {
						return v
					}
				}
			}
		}

		// Check for direct result field
		if result, exists := dataMap["result"]; exists {
			if resultMap, isMap := result.(map[string]interface{}); isMap {
				if content, contentExists := resultMap["content"]; contentExists {
					if contentArray, isArray := content.([]interface{}); isArray && len(contentArray) > 0 {
						if v, ok := contentArray[0].(string); ok && v != "" {
							return v
						}
						if contentItem, isMap := contentArray[0].(map[string]interface{}); isMap {
							if v, ok := contentItem["text"].(string); ok && v != "" {
								return v
							}
							if v, ok := contentItem["blob"].(string); ok && v != "" {
								return v
							}
							if v, ok := contentItem["data"].(string); ok && v != "" {
								return v
							}
						}
					}
				}
			}
		}
	}

	// If no text content found, return JSON representation
	if dataBytes, err := json.Marshal(data); err == nil {
		return string(dataBytes)
	}

	return ""
}

// BetaPause synchronously pauses this session (beta), putting it into a dormant state to reduce resource usage and costs.
// BetaPause puts the session into a PAUSED state where computational resources are significantly reduced.
// The session state is preserved and can be resumed later to continue work.
//
// Note: This feature is currently in whitelist-only access.
// Contact agentbay_dev@alibabacloud.com to request access.
//
// Parameters:
//   - timeout: Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
//   - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.
//
// Returns:
//   - *models.SessionPauseResult: Result containing success status, request ID, and error message if any.
//   - error: Error if the operation fails at the transport level
//
// Behavior:
//
// - Initiates pause operation through the PauseSessionAsync API
// - Polls session status until PAUSED state or timeout
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
//	pauseResult, _ := result.Session.BetaPause(300, 2.0)
func (s *Session) BetaPause(timeout int, pollInterval float64) (*models.SessionPauseResult, error) {
	// Set default values if not provided
	if timeout <= 0 {
		timeout = 600
	}
	if pollInterval <= 0 {
		pollInterval = 2.0
	}

	// Create pause request
	request := &mcp.PauseSessionAsyncRequest{}
	request.SetAuthorization(fmt.Sprintf("Bearer %s", s.GetAPIKey()))
	request.SetSessionId(s.SessionID)

	// Call PauseSessionAsync API to initiate the pause operation
	response, err := s.GetClient().PauseSessionAsync(request)
	if err != nil {
		return &models.SessionPauseResult{
			ApiResponse:  models.WithRequestID(""),
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to call PauseSessionAsync API: %v", err),
		}, nil
	}

	// Extract request ID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response.Body == nil {
		return &models.SessionPauseResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: "Invalid response body",
		}, nil
	}

	body := response.Body
	if !dara.IsNil(body.Success) && !*body.Success {
		errorMessage := fmt.Sprintf("[%s] %s", tea.StringValue(body.Code), tea.StringValue(body.Message))
		if errorMessage == "[]" {
			errorMessage = "Unknown error"
		}
		return &models.SessionPauseResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: errorMessage,
			Code:         tea.StringValue(body.Code),
			Message:      tea.StringValue(body.Message),
			HTTPCode:     tea.Int32Value(body.HttpStatusCode),
		}, nil
	}

	// Pause initiated successfully
	LogInfo(fmt.Sprintf("PauseSessionAsync: Session %s pause initiated successfully", s.SessionID))

	// Poll for session status until PAUSED or timeout
	startTime := time.Now()
	maxAttempts := int(float64(timeout) / pollInterval)

	for attempt := 0; attempt < maxAttempts; attempt++ {
		// Get session status
		getSessionResult, err := s.AgentBay.getSession(s.SessionID)
		if err != nil || !getSessionResult.Success {
			errorMessage := "Failed to get session status"
			if err != nil {
				errorMessage = fmt.Sprintf("Failed to get session status: %v", err)
			} else if getSessionResult.ErrorMessage != "" {
				errorMessage = fmt.Sprintf("Failed to get session status: %s", getSessionResult.ErrorMessage)
			}
			return &models.SessionPauseResult{
				ApiResponse:  models.WithRequestID(getSessionResult.GetRequestID()),
				Success:      false,
				ErrorMessage: errorMessage,
			}, nil
		}

		// Check session status
		if getSessionResult.Data != nil {
			status := getSessionResult.Data.Status
			if status == "" {
				status = "UNKNOWN"
			}
			LogInfo(fmt.Sprintf("Session status: %s (attempt %d/%d)", status, attempt+1, maxAttempts))

			// Check if session is paused
			if status == "PAUSED" {
				elapsed := time.Since(startTime)
				LogInfo(fmt.Sprintf("Session paused successfully in %v", elapsed))
				return &models.SessionPauseResult{
					ApiResponse: models.WithRequestID(getSessionResult.GetRequestID()),
					Success:     true,
					Status:      status,
				}, nil
			} else if status == "PAUSING" {
				// Normal transitioning state, continue polling
			} else {
				// Any other status is unexpected - pause API succeeded but session is not pausing/paused
				elapsed := time.Since(startTime)
				errorMessage := fmt.Sprintf("Session pause failed: unexpected state '%s' after %v", status, elapsed)
				LogWarn(errorMessage)
				return &models.SessionPauseResult{
					ApiResponse:  models.WithRequestID(getSessionResult.GetRequestID()),
					Success:      false,
					ErrorMessage: errorMessage,
					Status:       status,
				}, nil
			}
		}

		// Wait before next query (using time.Sleep to avoid blocking)
		// Only wait if we're not at the last attempt
		if attempt < maxAttempts-1 {
			time.Sleep(time.Duration(pollInterval*1000) * time.Millisecond)
		}
	}

	// Timeout
	elapsed := time.Since(startTime)
	errorMessage := fmt.Sprintf("Session pause timed out after %v", elapsed)
	LogError(errorMessage)
	return &models.SessionPauseResult{
		ApiResponse:  models.WithRequestID(""),
		Success:      false,
		ErrorMessage: errorMessage,
	}, nil
}

// BetaResume synchronously resumes this session (beta) from a paused state to continue work.
// BetaResume restores the session from PAUSED state back to RUNNING state.
// All previous session state and data are preserved during resume operation.
//
// Parameters:
//   - timeout: Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
//   - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.
//
// Returns:
//   - *models.SessionResumeResult: Result containing success status, request ID, and error message if any.
//   - error: Error if the operation fails at the transport level
//
// Behavior:
//
// - Initiates resume operation through the ResumeSessionAsync API
// - Polls session status until RUNNING state or timeout
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
//	result.Session.BetaPause(300, 2.0)
//	resumeResult, _ := result.Session.BetaResume(300, 2.0)
func (s *Session) BetaResume(timeout int, pollInterval float64) (*models.SessionResumeResult, error) {
	// Set default values if not provided
	if timeout <= 0 {
		timeout = 600
	}
	if pollInterval <= 0 {
		pollInterval = 2.0
	}

	// Create resume request
	request := &mcp.ResumeSessionAsyncRequest{}
	request.SetAuthorization(fmt.Sprintf("Bearer %s", s.GetAPIKey()))
	request.SetSessionId(s.SessionID)

	// Call ResumeSessionAsync API to initiate the resume operation
	response, err := s.GetClient().ResumeSessionAsync(request)
	if err != nil {
		return &models.SessionResumeResult{
			ApiResponse:  models.WithRequestID(""),
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to call ResumeSessionAsync API: %v", err),
		}, nil
	}

	// Extract request ID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response.Body == nil {
		return &models.SessionResumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: "Invalid response body",
		}, nil
	}

	body := response.Body
	if !dara.IsNil(body.Success) && !*body.Success {
		errorMessage := fmt.Sprintf("[%s] %s", tea.StringValue(body.Code), tea.StringValue(body.Message))
		if errorMessage == "[]" {
			errorMessage = "Unknown error"
		}
		return &models.SessionResumeResult{
			ApiResponse:  models.WithRequestID(requestID),
			Success:      false,
			ErrorMessage: errorMessage,
			Code:         tea.StringValue(body.Code),
			Message:      tea.StringValue(body.Message),
			HTTPCode:     tea.Int32Value(body.HttpStatusCode),
		}, nil
	}

	// Resume initiated successfully
	LogInfo(fmt.Sprintf("ResumeSessionAsync: Session %s resume initiated successfully", s.SessionID))

	// Poll for session status until RUNNING or timeout
	startTime := time.Now()
	maxAttempts := int(float64(timeout) / pollInterval)

	for attempt := 0; attempt < maxAttempts; attempt++ {
		// Get session status
		getSessionResult, err := s.AgentBay.getSession(s.SessionID)
		if err != nil || !getSessionResult.Success {
			errorMessage := "Failed to get session status"
			if err != nil {
				errorMessage = fmt.Sprintf("Failed to get session status: %v", err)
			} else if getSessionResult.ErrorMessage != "" {
				errorMessage = fmt.Sprintf("Failed to get session status: %s", getSessionResult.ErrorMessage)
			}
			return &models.SessionResumeResult{
				ApiResponse:  models.WithRequestID(getSessionResult.GetRequestID()),
				Success:      false,
				ErrorMessage: errorMessage,
			}, nil
		}

		// Check session status
		if getSessionResult.Data != nil {
			status := getSessionResult.Data.Status
			if status == "" {
				status = "UNKNOWN"
			}
			LogInfo(fmt.Sprintf("Session status: %s (attempt %d/%d)", status, attempt+1, maxAttempts))

			// Check if session is running
			if status == "RUNNING" {
				elapsed := time.Since(startTime)
				LogInfo(fmt.Sprintf("Session resumed successfully in %v", elapsed))
				return &models.SessionResumeResult{
					ApiResponse: models.WithRequestID(getSessionResult.GetRequestID()),
					Success:     true,
					Status:      status,
				}, nil
			} else if status == "RESUMING" {
				// Normal transitioning state, continue polling
			} else {
				// Any other status is unexpected - resume API succeeded but session is not resuming/running
				elapsed := time.Since(startTime)
				errorMessage := fmt.Sprintf("Session resume failed: unexpected state '%s' after %v", status, elapsed)
				LogWarn(errorMessage)
				return &models.SessionResumeResult{
					ApiResponse:  models.WithRequestID(getSessionResult.GetRequestID()),
					Success:      false,
					ErrorMessage: errorMessage,
					Status:       status,
				}, nil
			}
		}

		// Wait before next query (using time.Sleep to avoid blocking)
		// Only wait if we're not at the last attempt
		if attempt < maxAttempts-1 {
			time.Sleep(time.Duration(pollInterval*1000) * time.Millisecond)
		}
	}

	// Timeout
	elapsed := time.Since(startTime)
	errorMessage := fmt.Sprintf("Session resume timed out after %v", elapsed)
	LogError(errorMessage)
	return &models.SessionResumeResult{
		ApiResponse:  models.WithRequestID(""),
		Success:      false,
		ErrorMessage: errorMessage,
	}, nil
}
