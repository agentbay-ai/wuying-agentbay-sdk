package agentbay

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// ContextStatusData represents the parsed context status data
type ContextStatusData struct {
	ContextId    string `json:"contextId"`
	Path         string `json:"path"`
	ErrorMessage string `json:"errorMessage"`
	Status       string `json:"status"`
	StartTime    int64  `json:"startTime"`
	FinishTime   int64  `json:"finishTime"`
	TaskType     string `json:"taskType"`
}

// ContextStatusItem represents an item in the context status response
type ContextStatusItem struct {
	Type string `json:"type"`
	Data string `json:"data"`
}

// ContextInfoResult wraps context info result and RequestID
type ContextInfoResult struct {
	models.ApiResponse
	Success           bool
	ContextStatusData []ContextStatusData // Parsed context status data
	ErrorMessage      string
}

// ContextSyncResult wraps context sync result and RequestID
type ContextSyncResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// ContextBinding represents a single context binding entry returned by DescribeSessionContexts.
type ContextBinding struct {
	ContextID   string
	ContextName string
	Path        string
	Policy      string
	BindTime    string
}

// ContextBindResult wraps the result of a Bind operation.
type ContextBindResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// ContextBindingsResult wraps the result of a ListBindings operation.
type ContextBindingsResult struct {
	models.ApiResponse
	Success      bool
	Bindings     []ContextBinding
	ErrorMessage string
}

// SyncCallback defines the callback function type for async sync operations
type SyncCallback func(success bool)

// ContextManager handles context operations for a specific session.
type ContextManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}

// NewContextManager creates a new ContextManager object.
func NewContextManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *ContextManager {
	return &ContextManager{
		Session: session,
	}
}

// Info retrieves context information for the current session.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	info, _ := result.Session.Context.Info()
func (cm *ContextManager) Info() (*ContextInfoResult, error) {
	return cm.InfoWithParams("", "", "")
}

// InfoWithParams retrieves context information for the current session with optional parameters.
func (cm *ContextManager) InfoWithParams(contextId, path, taskType string) (*ContextInfoResult, error) {
	request := &mcp.GetContextInfoRequest{
		Authorization: tea.String("Bearer " + cm.Session.GetAPIKey()),
		SessionId:     tea.String(cm.Session.GetSessionId()),
	}

	// Set optional parameters if provided
	if contextId != "" {
		request.ContextId = tea.String(contextId)
	}
	if path != "" {
		request.Path = tea.String(path)
	}
	if taskType != "" {
		request.TaskType = tea.String(taskType)
	}

	// Log API request
	requestInfo := fmt.Sprintf("SessionId=%s", *request.SessionId)
	if request.ContextId != nil {
		requestInfo += fmt.Sprintf(", ContextId=%s", *request.ContextId)
	}
	if request.Path != nil {
		requestInfo += fmt.Sprintf(", Path=%s", *request.Path)
	}
	if request.TaskType != nil {
		requestInfo += fmt.Sprintf(", TaskType=%s", *request.TaskType)
	}
	logAPICall("GetContextInfo", requestInfo)

	response, err := cm.Session.GetClient().GetContextInfo(request)

	// Log API response
	if err != nil {
		logOperationError("GetContextInfo", err.Error(), true)
		return nil, fmt.Errorf("failed to get context info: %w", err)
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response != nil && response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("GetContextInfo", requestID, false, nil, string(respJSON))
			return &ContextInfoResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:           false,
				ContextStatusData: []ContextStatusData{},
				ErrorMessage:      fmt.Sprintf("[%s] %s", code, message),
			}, nil
		}
	}

	// Parse the context status data
	var contextStatusData []ContextStatusData
	if response.Body != nil && response.Body.Data != nil {
		contextStatus := tea.StringValue(response.Body.Data.ContextStatus)
		if contextStatus != "" {
			// First, parse the outer array
			var statusItems []ContextStatusItem
			if err := json.Unmarshal([]byte(contextStatus), &statusItems); err != nil {
				LogError(fmt.Sprintf("Error parsing context status: %v", err))
			} else {
				// Process each item in the array
				for _, item := range statusItems {
					if item.Type == "data" {
						// Parse the inner data string
						var dataItems []ContextStatusData
						if err := json.Unmarshal([]byte(item.Data), &dataItems); err != nil {
							LogError(fmt.Sprintf("Error parsing context status data: %v", err))
						} else {
							contextStatusData = append(contextStatusData, dataItems...)
						}
					}
				}
			}
		}
	}

	keyFields := map[string]interface{}{
		"session_id":    cm.Session.GetSessionId(),
		"context_count": len(contextStatusData),
	}
	if contextId != "" {
		keyFields["context_id"] = contextId
	}
	if path != "" {
		keyFields["path"] = path
	}
	if taskType != "" {
		keyFields["task_type"] = taskType
	}
	if response != nil && response.Body != nil {
		respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("GetContextInfo", requestID, true, keyFields, string(respJSON))
	}

	return &ContextInfoResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success:           true,
		ContextStatusData: contextStatusData,
		ErrorMessage:      "",
	}, nil
}

// Sync synchronizes the context for the current session.
func (cm *ContextManager) Sync() (*ContextSyncResult, error) {
	return cm.SyncWithParams("", "", "")
}

// SyncWithCallback synchronizes the context with callback support (dual-mode).
// If callback is provided, it runs in background and calls callback when complete.
// If callback is nil, it waits for completion before returning.
//
// Example (Synchronous mode - waits for completion):
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		result, err := client.Create(nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Get or create a context
//		contextResult, err := client.Context.Get("my-context", true)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//
//		// Synchronous mode: callback is nil, so it waits for completion
//		syncResult, err := session.Context.SyncWithCallback(
//			contextResult.ContextID,
//			"/mnt/persistent",
//			"upload",
//			nil,  // No callback - synchronous mode
//			10,   // maxRetries
//			1000, // retryInterval in milliseconds
//		)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		fmt.Printf("Sync completed - Success: %v\n", syncResult.Success)
//
//		// Output: No sync tasks found
//		// Output: Sync completed - Success: true
//
//		session.Delete()
//	}
//
// Example (Asynchronous mode - with callback):
//
//	package main
//	import (
//		"fmt"
//		"os"
//		"time"
//		"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
//	)
//	func main() {
//		client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		result, err := client.Create(nil)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		session := result.Session
//
//		// Get or create a context
//		contextResult, err := client.Context.Get("my-context", true)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//
//		// Asynchronous mode: with callback, returns immediately
//		syncResult, err := session.Context.SyncWithCallback(
//			contextResult.ContextID,
//			"/mnt/persistent",
//			"upload",
//			func(success bool) {
//				if success {
//					fmt.Println("Context sync completed successfully")
//				} else {
//					fmt.Println("Context sync failed or timed out")
//				}
//			},
//			150,  // maxRetries
//			500, // retryInterval in milliseconds (initial interval for exponential backoff)
//		)
//		if err != nil {
//			fmt.Printf("Error: %v\n", err)
//			os.Exit(1)
//		}
//		fmt.Printf("Sync triggered - Success: %v\n", syncResult.Success)
//
//		// Wait for callback to complete
//		time.Sleep(5 * time.Second)
//
//		// Output: Sync triggered - Success: true
//		// Output: Context sync completed successfully
//
//		session.Delete()
//	}
func (cm *ContextManager) SyncWithCallback(contextId, path, mode string, callback SyncCallback, maxRetries int, retryInterval int) (*ContextSyncResult, error) {
	// First, trigger the sync operation
	syncResult, err := cm.SyncWithParams(contextId, path, mode)
	if err != nil {
		return nil, err
	}

	// If sync failed, return immediately
	if !syncResult.Success {
		return syncResult, nil
	}

	// If callback is provided, start polling in background (async mode)
	if callback != nil {
		go cm.pollForCompletion(callback, contextId, path, maxRetries, retryInterval)
		return syncResult, nil
	}

	// If no callback, wait for completion (sync mode)
	finalSuccess, err := cm.pollForCompletionSync(contextId, path, maxRetries, retryInterval)
	if err != nil {
		return nil, err
	}

	return &ContextSyncResult{
		ApiResponse: syncResult.ApiResponse,
		Success:     finalSuccess,
	}, nil
}

// SyncWithParams synchronizes the context for the current session with optional parameters.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	session := result.Session
//	_, _ = session.Context.SyncWithCallback(
//		"project-data",
//		"/mnt/shared",
//		"upload",
//		func(success bool, message string) {
//			fmt.Printf("Sync callback -> success: %v message: %s\n", success, message)
//		},
//		20,
//		500,
//	)
func (cm *ContextManager) SyncWithParams(contextId, path, mode string) (*ContextSyncResult, error) {
	// Validate that contextId and path are provided together or both omitted
	hasContextId := contextId != ""
	hasPath := path != ""

	if hasContextId != hasPath {
		return nil, fmt.Errorf(
			"contextId and path must be provided together or both omitted. " +
				"If you want to sync a specific context, both contextId and path are required. " +
				"If you want to sync all contexts, omit both parameters.",
		)
	}

	request := &mcp.SyncContextRequest{
		Authorization: tea.String("Bearer " + cm.Session.GetAPIKey()),
		SessionId:     tea.String(cm.Session.GetSessionId()),
	}

	// Set optional parameters if provided
	if contextId != "" {
		request.ContextId = tea.String(contextId)
	}
	if path != "" {
		request.Path = tea.String(path)
	}
	// Set mode, default to "upload" if empty or not provided
	if mode == "" {
		mode = "upload"
	}
	request.Mode = tea.String(mode)

	// Log API request
	requestInfo := fmt.Sprintf("SessionId=%s", *request.SessionId)
	if request.ContextId != nil {
		requestInfo += fmt.Sprintf(", ContextId=%s", *request.ContextId)
	}
	if request.Path != nil {
		requestInfo += fmt.Sprintf(", Path=%s", *request.Path)
	}
	if request.Mode != nil {
		requestInfo += fmt.Sprintf(", Mode=%s", *request.Mode)
	}
	logAPICall("SyncContext", requestInfo)

	response, err := cm.Session.GetClient().SyncContext(request)

	// Log API response
	if err != nil {
		logOperationError("SyncContext", err.Error(), true)
		return nil, fmt.Errorf("failed to sync context: %w", err)
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response != nil && response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("SyncContext", requestID, false, nil, string(respJSON))
			return &ContextSyncResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
			}, nil
		}
	}

	var success bool
	if response.Body != nil {
		success = tea.BoolValue(response.Body.Success)
	}

	keyFields := map[string]interface{}{
		"session_id": cm.Session.GetSessionId(),
		"mode":       mode,
	}
	if contextId != "" {
		keyFields["context_id"] = contextId
	}
	if path != "" {
		keyFields["path"] = path
	}
	if response != nil && response.Body != nil {
		respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("SyncContext", requestID, success, keyFields, string(respJSON))
	}

	return &ContextSyncResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success: success,
	}, nil
}

// pollForCompletion polls the info interface to check if sync is completed and calls callback.
// Uses exponential backoff: retryInterval is the initial interval in ms, grows by factor 1.1 up to 5000ms.
func (cm *ContextManager) pollForCompletion(callback SyncCallback, contextId, path string, maxRetries, retryInterval int) {
	maxInterval := 5000
	backoffFactor := 1.1
	currentInterval := retryInterval

	for retry := 0; retry < maxRetries; retry++ {
		infoResult, err := cm.InfoWithParams(contextId, path, "")
		if err != nil {
			LogError(fmt.Sprintf("Error checking context status on attempt %d: %v", retry+1, err))
			time.Sleep(time.Duration(currentInterval) * time.Millisecond)
			newInterval := int(float64(currentInterval) * backoffFactor)
			if newInterval > maxInterval {
				currentInterval = maxInterval
			} else {
				currentInterval = newInterval
			}
			continue
		}

		allCompleted := true
		hasFailure := false
		hasSyncTasks := false

		for _, item := range infoResult.ContextStatusData {
			if item.TaskType != "upload" && item.TaskType != "download" {
				continue
			}

			hasSyncTasks = true
			LogDebug(fmt.Sprintf("Sync task %s status: %s, path: %s", item.ContextId, item.Status, item.Path))

			if item.Status != "Success" && item.Status != "Failed" {
				allCompleted = false
				break
			}

			if item.Status == "Failed" {
				hasFailure = true
				LogError(fmt.Sprintf("Sync failed for context %s: %s", item.ContextId, item.ErrorMessage))
			}
		}

		if allCompleted || !hasSyncTasks {
			if hasFailure {
				LogInfo("Context sync completed with failures")
				callback(false)
			} else if hasSyncTasks {
				LogInfo("Context sync completed successfully")
				callback(true)
			} else {
				LogInfo("No sync tasks found")
				callback(true)
			}
			return
		}

		LogDebug(fmt.Sprintf("Waiting for context sync to complete, attempt %d/%d, next interval: %dms", retry+1, maxRetries, currentInterval))
		time.Sleep(time.Duration(currentInterval) * time.Millisecond)
		newInterval := int(float64(currentInterval) * backoffFactor)
		if newInterval > maxInterval {
			currentInterval = maxInterval
		} else {
			currentInterval = newInterval
		}
	}

	LogWarn(fmt.Sprintf("Context sync polling timed out after %d attempts", maxRetries))
	callback(false)
}

// Bind dynamically binds one or more contexts to the current session.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
//	result, _ := client.Create(nil)
//	session := result.Session
//	contextSync, _ := agentbay.NewContextSync(contextID, "/tmp/ctx-data", nil)
//	bindResult, _ := session.Context.Bind([]*ContextSync{contextSync}, true)
func (cm *ContextManager) Bind(contexts []*ContextSync, waitForCompletion bool) (*ContextBindResult, error) {
	if len(contexts) == 0 {
		return &ContextBindResult{
			Success:      false,
			ErrorMessage: "At least one context is required",
		}, nil
	}

	var persistenceDataList []*mcp.BindContextsRequestPersistenceDataList
	for _, ctx := range contexts {
		item := &mcp.BindContextsRequestPersistenceDataList{
			ContextId: tea.String(ctx.ContextID),
			Path:      tea.String(ctx.Path),
		}
		if ctx.Policy != nil {
			policyJSON, err := json.Marshal(ctx.Policy)
			if err == nil {
				item.Policy = tea.String(string(policyJSON))
			}
		}
		persistenceDataList = append(persistenceDataList, item)
	}

	request := &mcp.BindContextsRequest{
		Authorization:       tea.String("Bearer " + cm.Session.GetAPIKey()),
		SessionId:           tea.String(cm.Session.GetSessionId()),
		PersistenceDataList: persistenceDataList,
	}

	contextIDs := make([]string, len(contexts))
	for i, ctx := range contexts {
		contextIDs[i] = ctx.ContextID
	}
	logAPICall("BindContexts", fmt.Sprintf("SessionId=%s, Contexts=%v", cm.Session.GetSessionId(), contextIDs))

	response, err := cm.Session.GetClient().BindContexts(request)
	if err != nil {
		logOperationError("BindContexts", err.Error(), true)
		return nil, fmt.Errorf("failed to bind contexts: %w", err)
	}

	requestID := models.ExtractRequestID(response)

	if response != nil && response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("BindContexts", requestID, false, nil, string(respJSON))
			return &ContextBindResult{
				ApiResponse:  models.ApiResponse{RequestID: requestID},
				Success:      false,
				ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
			}, nil
		}
	}

	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("BindContexts", requestID, true, map[string]interface{}{
		"context_count": len(contexts),
	}, string(respJSON))

	if waitForCompletion {
		cm.pollForBindCompletion(contextIDs, 60, 2000)
	}

	return &ContextBindResult{
		ApiResponse: models.ApiResponse{RequestID: requestID},
		Success:     true,
	}, nil
}

// BetaMount dynamically mounts one or more contexts to the current session with write-through persistence.
// Unlike Bind which uses sync-based persistence, BetaMount provides direct-mount persistence
// where data is persisted immediately without manual sync calls.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
//	result, _ := client.Create(nil)
//	session := result.Session
//	mount := agentbay.NewBetaContextMount(contextID, "/mnt/data")
//	mountResult, _ := session.Context.BetaMount([]*BetaContextMount{mount}, true)
func (cm *ContextManager) BetaMount(contexts []*BetaContextMount, waitForCompletion bool) (*ContextBindResult, error) {
	if len(contexts) == 0 {
		return &ContextBindResult{
			Success:      false,
			ErrorMessage: "At least one context mount is required",
		}, nil
	}

	var persistenceDataList []*mcp.BindContextsRequestPersistenceDataList
	for _, ctx := range contexts {
		item := &mcp.BindContextsRequestPersistenceDataList{
			ContextId: tea.String(ctx.ContextID),
			Path:      tea.String(ctx.Path),
			Type:      tea.String("mount"),
			MountConfig: &mcp.BindContextsRequestPersistenceDataListMountConfig{
				AccessMode:  tea.String(string(ctx.AccessMode)),
				StorageMode: tea.String(string(ctx.Strategy)),
				SourcePath:  tea.String(ctx.SourcePath),
			},
		}
		persistenceDataList = append(persistenceDataList, item)
	}

	request := &mcp.BindContextsRequest{
		Authorization:       tea.String("Bearer " + cm.Session.GetAPIKey()),
		SessionId:           tea.String(cm.Session.GetSessionId()),
		PersistenceDataList: persistenceDataList,
	}

	contextIDs := make([]string, len(contexts))
	for i, ctx := range contexts {
		contextIDs[i] = ctx.ContextID
	}
	logAPICall("BindContexts(Mount)", fmt.Sprintf("SessionId=%s, Contexts=%v", cm.Session.GetSessionId(), contextIDs))

	response, err := cm.Session.GetClient().BindContexts(request)
	if err != nil {
		logOperationError("BindContexts(Mount)", err.Error(), true)
		return nil, fmt.Errorf("failed to mount contexts: %w", err)
	}

	requestID := models.ExtractRequestID(response)

	if response != nil && response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("BindContexts(Mount)", requestID, false, nil, string(respJSON))
			return &ContextBindResult{
				ApiResponse:  models.ApiResponse{RequestID: requestID},
				Success:      false,
				ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
			}, nil
		}
	}

	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("BindContexts(Mount)", requestID, true, map[string]interface{}{
		"context_count": len(contexts),
	}, string(respJSON))

	return &ContextBindResult{
		ApiResponse: models.ApiResponse{RequestID: requestID},
		Success:     true,
	}, nil
}

// ListBindings lists all context bindings for the current session.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
//	result, _ := client.Create(nil)
//	session := result.Session
//	bindingsResult, _ := session.Context.ListBindings()
//	for _, b := range bindingsResult.Bindings {
//	    fmt.Printf("Context %s at %s\n", b.ContextID, b.Path)
//	}
func (cm *ContextManager) ListBindings() (*ContextBindingsResult, error) {
	request := &mcp.DescribeSessionContextsRequest{
		Authorization: tea.String("Bearer " + cm.Session.GetAPIKey()),
		SessionId:     tea.String(cm.Session.GetSessionId()),
	}

	logAPICall("DescribeSessionContexts", fmt.Sprintf("SessionId=%s", cm.Session.GetSessionId()))

	response, err := cm.Session.GetClient().DescribeSessionContexts(request)
	if err != nil {
		logOperationError("DescribeSessionContexts", err.Error(), true)
		return nil, fmt.Errorf("failed to list bindings: %w", err)
	}

	requestID := models.ExtractRequestID(response)

	if response != nil && response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			code := tea.StringValue(response.Body.Code)
			message := tea.StringValue(response.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("DescribeSessionContexts", requestID, false, nil, string(respJSON))
			return &ContextBindingsResult{
				ApiResponse:  models.ApiResponse{RequestID: requestID},
				Success:      false,
				ErrorMessage: fmt.Sprintf("[%s] %s", code, message),
			}, nil
		}
	}

	var bindings []ContextBinding
	if response.Body != nil && response.Body.Data != nil {
		for _, item := range response.Body.Data {
			bindings = append(bindings, ContextBinding{
				ContextID:   tea.StringValue(item.ContextId),
				ContextName: tea.StringValue(item.ContextName),
				Path:        tea.StringValue(item.Path),
				Policy:      tea.StringValue(item.Policy),
				BindTime:    tea.StringValue(item.BindTime),
			})
		}
	}

	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("DescribeSessionContexts", requestID, true, map[string]interface{}{
		"binding_count": len(bindings),
	}, string(respJSON))

	return &ContextBindingsResult{
		ApiResponse: models.ApiResponse{RequestID: requestID},
		Success:     true,
		Bindings:    bindings,
	}, nil
}

// pollForBindCompletion polls ListBindings until all expected contexts are bound.
func (cm *ContextManager) pollForBindCompletion(expectedContextIDs []string, maxRetries, retryIntervalMs int) bool {
	for i := 0; i < maxRetries; i++ {
		result, err := cm.ListBindings()
		if err == nil && result.Success {
			boundIDs := make(map[string]bool)
			for _, b := range result.Bindings {
				boundIDs[b.ContextID] = true
			}
			allBound := true
			for _, id := range expectedContextIDs {
				if !boundIDs[id] {
					allBound = false
					break
				}
			}
			if allBound {
				return true
			}
		}
		time.Sleep(time.Duration(retryIntervalMs) * time.Millisecond)
	}
	return false
}

// pollForCompletionSync is the synchronous version of polling for sync completion.
func (cm *ContextManager) pollForCompletionSync(contextId, path string, maxRetries, retryInterval int) (bool, error) {
	maxInterval := 5000
	backoffFactor := 1.1
	currentInterval := retryInterval

	for retry := 0; retry < maxRetries; retry++ {
		infoResult, err := cm.InfoWithParams(contextId, path, "")
		if err != nil {
			LogError(fmt.Sprintf("Error checking context status on attempt %d: %v", retry+1, err))
			time.Sleep(time.Duration(currentInterval) * time.Millisecond)
			newInterval := int(float64(currentInterval) * backoffFactor)
			if newInterval > maxInterval {
				currentInterval = maxInterval
			} else {
				currentInterval = newInterval
			}
			continue
		}

		allCompleted := true
		hasFailure := false
		hasSyncTasks := false

		for _, item := range infoResult.ContextStatusData {
			if item.TaskType != "upload" && item.TaskType != "download" {
				continue
			}

			hasSyncTasks = true
			LogDebug(fmt.Sprintf("Sync task %s status: %s, path: %s", item.ContextId, item.Status, item.Path))

			if item.Status != "Success" && item.Status != "Failed" {
				allCompleted = false
				break
			}

			if item.Status == "Failed" {
				hasFailure = true
				LogError(fmt.Sprintf("Sync failed for context %s: %s", item.ContextId, item.ErrorMessage))
			}
		}

		if allCompleted || !hasSyncTasks {
			if hasFailure {
				LogInfo("Context sync completed with failures")
				return false, nil
			} else if hasSyncTasks {
				LogInfo("Context sync completed successfully")
				return true, nil
			} else {
				LogInfo("No sync tasks found")
				return true, nil
			}
		}

		LogDebug(fmt.Sprintf("Waiting for context sync to complete, attempt %d/%d, next interval: %dms", retry+1, maxRetries, currentInterval))
		time.Sleep(time.Duration(currentInterval) * time.Millisecond)
		newInterval := int(float64(currentInterval) * backoffFactor)
		if newInterval > maxInterval {
			currentInterval = maxInterval
		} else {
			currentInterval = newInterval
		}
	}

	LogWarn(fmt.Sprintf("Context sync polling timed out after %d attempts", maxRetries))
	return false, nil
}
