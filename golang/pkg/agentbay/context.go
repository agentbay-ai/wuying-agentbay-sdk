package agentbay

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// Context represents a persistent storage context in the AgentBay cloud environment.
type Context struct {
	// ID is the unique identifier of the context.
	ID string

	// Name is the name of the context.
	Name string

	// CreatedAt is the date and time when the Context was created.
	CreatedAt string

	// LastUsedAt is the date and time when the Context was last used.
	LastUsedAt string
}

// ContextResult wraps context operation result and RequestID
type ContextResult struct {
	models.ApiResponse
	Success      bool
	ContextID    string
	Context      *Context
	ErrorMessage string
}

// ContextListResult wraps context list and RequestID
type ContextListResult struct {
	models.ApiResponse
	Success      bool
	Contexts     []*Context
	NextToken    string
	MaxResults   int32
	TotalCount   int32
	ErrorMessage string
}

// ContextCreateResult wraps context creation result and RequestID
type ContextCreateResult struct {
	models.ApiResponse
	ContextID string
}

// ContextModifyResult wraps context modification result and RequestID
type ContextModifyResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// ContextDeleteResult wraps context deletion result and RequestID
type ContextDeleteResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// ContextClearResult wraps context clear operation result and RequestID
type ContextClearResult struct {
	models.ApiResponse
	Success      bool
	Status       string // Current status of the clearing task ("clearing", "available", etc.)
	ContextID    string
	ErrorMessage string
}

// ContextService provides methods to manage persistent contexts in the AgentBay cloud environment.
type ContextService struct {
	// AgentBay is the AgentBay instance.
	AgentBay *AgentBay
}

// ContextListParams contains parameters for listing contexts
type ContextListParams struct {
	MaxResults int32  // Number of results per page
	NextToken  string // Token for the next page
	SessionId  string // Optional session id filter
}

// NewContextListParams creates a new ContextListParams with default values
func NewContextListParams() *ContextListParams {
	return &ContextListParams{
		MaxResults: 10, // Default page size
		NextToken:  "",
		SessionId:  "",
	}
}

// List lists all available contexts with pagination support.
//
// Parameters:
//   - params: *ContextListParams (optional) - Pagination parameters. If nil, default values are used (MaxResults=10).
//
// Returns:
//   - *ContextListResult: A result object containing the list of Context objects, pagination info, and RequestID.
//   - error: An error if the operation fails.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Context.List(nil)
func (cs *ContextService) List(params *ContextListParams) (*ContextListResult, error) {
	if params == nil {
		params = NewContextListParams()
	}

	request := &mcp.ListContextsRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		MaxResults:    tea.Int32(params.MaxResults),
	}

	// Add optional session id filter
	if params.SessionId != "" {
		request.SessionId = tea.String(params.SessionId)
	}

	// Add NextToken if provided
	if params.NextToken != "" {
		request.NextToken = tea.String(params.NextToken)
	}

	// Log API request
	requestInfo := fmt.Sprintf("MaxResults=%d", *request.MaxResults)
	if request.NextToken != nil {
		requestInfo += fmt.Sprintf(", NextToken=%s", *request.NextToken)
	}
	if request.SessionId != nil {
		requestInfo += fmt.Sprintf(", SessionId=%s", *request.SessionId)
	}
	logAPICall("ListContexts", requestInfo)

	response, err := cs.AgentBay.Client.ListContexts(request)

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log API response
	if err != nil {
		logOperationError("ListContexts", err.Error(), true)
		return &ContextListResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Contexts:     []*Context{},
			ErrorMessage: fmt.Sprintf("Failed to list contexts: %v", err),
		}, nil
	}

	// Check for API-level errors
	if response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
			errorMsg := "Unknown error"
			if response.Body.Message != nil {
				errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
			} else {
				errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("ListContexts", requestID, false, nil, string(respJSON))
			return &ContextListResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				Contexts:     []*Context{},
				ErrorMessage: errorMsg,
			}, nil
		}
	}

	var contexts []*Context
	var nextToken string
	var maxResults int32
	var totalCount int32

	if response.Body != nil {
		// Extract pagination information
		if response.Body.NextToken != nil {
			nextToken = *response.Body.NextToken
		}
		// Set maxResults and totalCount from params or response
		maxResults = params.MaxResults
		if response.Body.TotalCount != nil {
			totalCount = *response.Body.TotalCount
		}

		// Extract context data
		if response.Body.Data != nil {
			for _, contextData := range response.Body.Data {
				context := &Context{
					ID:         tea.StringValue(contextData.Id),
					Name:       tea.StringValue(contextData.Name),
					CreatedAt:  tea.StringValue(contextData.CreateTime),
					LastUsedAt: tea.StringValue(contextData.LastUsedTime),
				}
				contexts = append(contexts, context)
			}
		}

		keyFields := map[string]interface{}{
			"max_results":   maxResults,
			"context_count": len(contexts),
			"total_count":   totalCount,
		}
		if nextToken != "" {
			keyFields["has_next_page"] = true
			keyFields["next_token_length"] = len(nextToken)
		} else {
			keyFields["has_next_page"] = false
		}
		respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("ListContexts", requestID, true, keyFields, string(respJSON))
	}

	return &ContextListResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success:      true,
		Contexts:     contexts,
		NextToken:    nextToken,
		MaxResults:   maxResults,
		TotalCount:   totalCount,
		ErrorMessage: "",
	}, nil
}

// Get gets a context by name. Optionally creates it if it doesn't exist.
// Get retrieves an existing context or creates a new one.
//
// Parameters:
//   - name: The name of the context to retrieve or create
//   - create: If true, creates the context if it doesn't exist
//
// Returns:
//   - *ContextResult: Result containing Context object and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
func (cs *ContextService) Get(name string, create bool) (*ContextResult, error) {
	request := &mcp.GetContextRequest{
		Name:          tea.String(name),
		AllowCreate:   tea.Bool(create),
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
	}

	// Add LoginRegionId only when creating (create=true)
	if create && cs.AgentBay.config.RegionID != "" {
		request.LoginRegionId = tea.String(cs.AgentBay.config.RegionID)
	}

	// Log API request
	logAPICall("GetContext", fmt.Sprintf("Name=%s, AllowCreate=%t", name, create))

	response, err := cs.AgentBay.Client.GetContext(request)

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log API response
	if err != nil {
		logOperationError("GetContext", err.Error(), true)
		return &ContextResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			ContextID:    "",
			Context:      nil,
			ErrorMessage: fmt.Sprintf("Failed to get context %s: %v", name, err),
		}, nil
	}

	if response != nil && response.Body != nil {
		// Check for API-level errors
		if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
			errorMsg := "Unknown error"
			if response.Body.Message != nil {
				errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
			} else {
				errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("GetContext", requestID, false, nil, string(respJSON))
			return &ContextResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ContextID:    "",
				Context:      nil,
				ErrorMessage: errorMsg,
			}, nil
		}
	}

	if response.Body == nil || response.Body.Data == nil || response.Body.Data.Id == nil {
		logOperationError("GetContext", "Context ID not found in response", false)
		return &ContextResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			ContextID:    "",
			Context:      nil,
			ErrorMessage: "Context ID not found in response",
		}, nil
	}

	// Create context object
	context := &Context{
		ID:         tea.StringValue(response.Body.Data.Id),
		Name:       tea.StringValue(response.Body.Data.Name),
		CreatedAt:  tea.StringValue(response.Body.Data.CreateTime),
		LastUsedAt: tea.StringValue(response.Body.Data.LastUsedTime),
	}

	keyFields := map[string]interface{}{
		"context_id": context.ID,
		"name":       context.Name,
	}
	if context.CreatedAt != "" {
		keyFields["created_at"] = context.CreatedAt
	}
	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("GetContext", requestID, true, keyFields, string(respJSON))

	return &ContextResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success:      true,
		ContextID:    tea.StringValue(response.Body.Data.Id),
		Context:      context,
		ErrorMessage: "",
	}, nil
}

// Create creates a new context with the given name.
//
// Parameters:
//   - name: The name for the new context.
//
// Returns:
//   - *ContextCreateResult: A result object containing the created context ID and request ID.
//   - error: An error if the operation fails.
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	createResult, _ := client.Context.Create("my-context")
func (cs *ContextService) Create(name string) (*ContextCreateResult, error) {
	result, err := cs.Get(name, true)
	if err != nil {
		return nil, err
	}

	if result == nil || !result.Success || result.ContextID == "" {
		errorMsg := "failed to create context"
		if result != nil && result.ErrorMessage != "" {
			errorMsg = result.ErrorMessage
		}
		return nil, fmt.Errorf("%s", errorMsg)
	}

	return &ContextCreateResult{
		ApiResponse: models.ApiResponse{
			RequestID: result.RequestID,
		},
		ContextID: result.ContextID,
	}, nil
}

// Update updates the specified context.
// Returns a result with success status.
// Update modifies an existing context's properties.
//
// Parameters:
//   - context: Context object with updated properties
//
// Returns:
//   - *ContextModifyResult: Result containing success status and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	contextResult.Context.Name = "new-name"
//	client.Context.Update(contextResult.Context)
func (cs *ContextService) Update(context *Context) (*ContextModifyResult, error) {
	request := &mcp.ModifyContextRequest{
		Id:            tea.String(context.ID),
		Name:          tea.String(context.Name),
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
	}

	// Log API request
	logAPICall("ModifyContext", fmt.Sprintf("Id=%s, Name=%s", context.ID, context.Name))

	response, err := cs.AgentBay.Client.ModifyContext(request)

	// Log API response
	if err != nil {
		logOperationError("ModifyContext", err.Error(), true)
		return nil, fmt.Errorf("failed to update context %s: %v", context.ID, err)
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			errorMsg := "Unknown error"
			if response.Body.Code != nil && response.Body.Message != nil {
				errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
			} else if response.Body.Code != nil {
				errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("ModifyContext", requestID, false, nil, string(respJSON))
			return &ContextModifyResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ErrorMessage: errorMsg,
			}, nil
		}
	}

	keyFields := map[string]interface{}{
		"context_id": context.ID,
		"name":       context.Name,
	}
	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("ModifyContext", requestID, true, keyFields, string(respJSON))

	return &ContextModifyResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success: true,
	}, nil
}

// Delete deletes the specified context.
//
// Parameters:
//   - context: The context object to delete
//
// Returns:
//   - *ContextDeleteResult: Result containing success status and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	client.Context.Delete(contextResult.Context)
func (cs *ContextService) Delete(context *Context) (*ContextDeleteResult, error) {
	request := &mcp.DeleteContextRequest{
		Id:            tea.String(context.ID),
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
	}

	// Log API request
	logAPICall("DeleteContext", fmt.Sprintf("Id=%s", context.ID))

	response, err := cs.AgentBay.Client.DeleteContext(request)

	// Log API response
	if err != nil {
		logOperationError("DeleteContext", err.Error(), true)
		return nil, fmt.Errorf("failed to delete context %s: %v", context.ID, err)
	}

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Check for API-level errors
	if response.Body != nil {
		if response.Body.Success != nil && !*response.Body.Success {
			errorMsg := "Unknown error"
			if response.Body.Code != nil && response.Body.Message != nil {
				errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
			} else if response.Body.Code != nil {
				errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
			}
			respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
			logAPIResponseWithDetails("DeleteContext", requestID, false, nil, string(respJSON))
			return &ContextDeleteResult{
				ApiResponse: models.ApiResponse{
					RequestID: requestID,
				},
				Success:      false,
				ErrorMessage: errorMsg,
			}, nil
		}
	}

	keyFields := map[string]interface{}{
		"context_id": context.ID,
	}
	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("DeleteContext", requestID, true, keyFields, string(respJSON))

	return &ContextDeleteResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success: true,
	}, nil
}

// ContextFileUrlResult represents a presigned URL operation result.
type ContextFileUrlResult struct {
	models.ApiResponse
	Success      bool
	Url          string
	ExpireTime   *int64
	ErrorMessage string
}

// ContextFileEntry represents a file item in a context.
type ContextFileEntry struct {
	FileID      string
	FileName    string
	FilePath    string
	FileType    string
	GmtCreate   string
	GmtModified string
	Size        int64
	Status      string
}

// ContextFileListResult represents the result of listing files under a context path.
type ContextFileListResult struct {
	models.ApiResponse
	Success      bool
	Entries      []*ContextFileEntry
	Count        *int32
	NextToken    string
	MaxResults   *int32
	ErrorMessage string
}

// ContextFileDeleteResult represents the result of deleting a file in a context.
type ContextFileDeleteResult struct {
	models.ApiResponse
	Success      bool
	ErrorMessage string
}

// GetFileDownloadUrl gets a presigned download URL for a file in a context.
//
// Note: The presigned URL expires in 1 hour by default.
//
// Parameters:
//   - contextID: The ID of the context
//   - filePath: The path to the file in the context
//
// Returns:
//   - *ContextFileUrlResult: Result containing the presigned URL, expire time, and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	urlResult, _ := client.Context.GetFileDownloadUrl(contextResult.ContextID, "/data/file.txt")
func (cs *ContextService) GetFileDownloadUrl(contextID string, filePath string) (*ContextFileUrlResult, error) {
	req := &mcp.GetContextFileDownloadUrlRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		ContextId:     tea.String(contextID),
		FilePath:      tea.String(filePath),
	}

	logAPICall("GetContextFileDownloadUrl", fmt.Sprintf("ContextId=%s, FilePath=%s", contextID, filePath))

	resp, err := cs.AgentBay.Client.GetContextFileDownloadUrl(req)
	if err != nil {
		logOperationError("GetContextFileDownloadUrl", err.Error(), true)
		return nil, err
	}

	requestID := models.ExtractRequestID(resp)

	success := false
	var url string
	var expire *int64
	var errorMessage string

	if resp != nil && resp.Body != nil {
		if resp.Body.Success != nil {
			success = *resp.Body.Success
		}

		// Check for API-level errors
		if !success && resp.Body.Code != nil {
			code := tea.StringValue(resp.Body.Code)
			message := tea.StringValue(resp.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			errorMessage = fmt.Sprintf("[%s] %s", code, message)
			respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
			logAPIResponseWithDetails("GetContextFileDownloadUrl", requestID, false, nil, string(respJSON))
			return &ContextFileUrlResult{
				ApiResponse:  models.WithRequestID(requestID),
				Success:      false,
				Url:          "",
				ExpireTime:   nil,
				ErrorMessage: errorMessage,
			}, nil
		}

		if resp.Body.Data != nil {
			if resp.Body.Data.Url != nil {
				url = *resp.Body.Data.Url
			}
			if resp.Body.Data.ExpireTime != nil {
				expire = resp.Body.Data.ExpireTime
			}
		}

		keyFields := map[string]interface{}{
			"context_id": contextID,
			"file_path":  filePath,
		}
		if url != "" {
			keyFields["url_length"] = len(url)
		}
		if expire != nil {
			keyFields["expire_time"] = *expire
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("GetContextFileDownloadUrl", requestID, true, keyFields, string(respJSON))
	}

	return &ContextFileUrlResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      success,
		Url:          url,
		ExpireTime:   expire,
		ErrorMessage: "",
	}, nil
}

// GetFileUploadUrl gets a presigned upload URL for a file in a context.
//
// Note: The presigned URL expires in 1 hour by default.
//
// Parameters:
//   - contextID: The ID of the context
//   - filePath: The path to the file in the context
//
// Returns:
//   - *ContextFileUrlResult: Result containing the presigned URL, expire time, and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	urlResult, _ := client.Context.GetFileUploadUrl(contextResult.ContextID, "/data/file.txt")
func (cs *ContextService) GetFileUploadUrl(contextID string, filePath string) (*ContextFileUrlResult, error) {
	req := &mcp.GetContextFileUploadUrlRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		ContextId:     tea.String(contextID),
		FilePath:      tea.String(filePath),
	}

	logAPICall("GetContextFileUploadUrl", fmt.Sprintf("ContextId=%s, FilePath=%s", contextID, filePath))

	resp, err := cs.AgentBay.Client.GetContextFileUploadUrl(req)
	if err != nil {
		logOperationError("GetContextFileUploadUrl", err.Error(), true)
		return nil, err
	}

	requestID := models.ExtractRequestID(resp)

	success := false
	var url string
	var expire *int64
	var errorMessage string

	if resp != nil && resp.Body != nil {
		if resp.Body.Success != nil {
			success = *resp.Body.Success
		}

		// Check for API-level errors
		if !success && resp.Body.Code != nil {
			code := tea.StringValue(resp.Body.Code)
			message := tea.StringValue(resp.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			errorMessage = fmt.Sprintf("[%s] %s", code, message)
			respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
			logAPIResponseWithDetails("GetContextFileUploadUrl", requestID, false, nil, string(respJSON))
			return &ContextFileUrlResult{
				ApiResponse:  models.WithRequestID(requestID),
				Success:      false,
				Url:          "",
				ExpireTime:   nil,
				ErrorMessage: errorMessage,
			}, nil
		}

		if resp.Body.Data != nil {
			if resp.Body.Data.Url != nil {
				url = *resp.Body.Data.Url
			}
			if resp.Body.Data.ExpireTime != nil {
				expire = resp.Body.Data.ExpireTime
			}
		}

		keyFields := map[string]interface{}{
			"context_id": contextID,
			"file_path":  filePath,
		}
		if url != "" {
			keyFields["url_length"] = len(url)
		}
		if expire != nil {
			keyFields["expire_time"] = *expire
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("GetContextFileUploadUrl", requestID, true, keyFields, string(respJSON))
	}

	return &ContextFileUrlResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      success,
		Url:          url,
		ExpireTime:   expire,
		ErrorMessage: "",
	}, nil
}

// ListFiles lists files under a specific folder path in a context using PageNumber/PageSize pagination.
//
// Parameters:
//   - contextID: The ID of the context
//   - parentFolderPath: The parent folder path to list files from
//   - pageNumber: The page number for pagination
//   - pageSize: The number of items per page
//
// Returns:
//   - *ContextFileListResult: Result containing the list of files and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	fileList, _ := client.Context.ListFiles(contextResult.ContextID, "/", 1, 10)
func (cs *ContextService) ListFiles(contextID string, parentFolderPath string, pageNumber int32, pageSize int32) (*ContextFileListResult, error) {
	req := &mcp.DescribeContextFilesRequest{
		Authorization:    tea.String("Bearer " + cs.AgentBay.APIKey),
		PageNumber:       tea.Int32(pageNumber),
		PageSize:         tea.Int32(pageSize),
		ParentFolderPath: tea.String(parentFolderPath),
		ContextId:        tea.String(contextID),
	}
	logSummary := fmt.Sprintf("ContextId=%s, ParentFolderPath=%s, PageNumber=%d, PageSize=%d", contextID, parentFolderPath, pageNumber, pageSize)
	return cs.describeContextFiles(req, logSummary, contextID, parentFolderPath, pageNumber, pageSize)
}

// ListFilesWithPagination lists files using MaxResults/NextToken pagination (token mode).
// Set maxResults and/or a non-empty nextToken (pass a non-nil pointer to a non-empty string).
// When using this method, PageNumber/PageSize are omitted on the API request, matching the pop API contract.
func (cs *ContextService) ListFilesWithPagination(contextID string, parentFolderPath string, maxResults *int32, nextToken *string) (*ContextFileListResult, error) {
	useTok := maxResults != nil || (nextToken != nil && *nextToken != "")
	if !useTok {
		return nil, fmt.Errorf("ListFilesWithPagination: provide maxResults and/or non-empty nextToken")
	}
	req := &mcp.DescribeContextFilesRequest{
		Authorization:    tea.String("Bearer " + cs.AgentBay.APIKey),
		ParentFolderPath: tea.String(parentFolderPath),
		ContextId:        tea.String(contextID),
	}
	if maxResults != nil {
		req.MaxResults = tea.Int32(*maxResults)
	}
	if nextToken != nil && *nextToken != "" {
		req.NextToken = tea.String(*nextToken)
	}
	parts := []string{
		fmt.Sprintf("ContextId=%s", contextID),
		fmt.Sprintf("ParentFolderPath=%s", parentFolderPath),
	}
	if maxResults != nil {
		parts = append(parts, fmt.Sprintf("MaxResults=%d", *maxResults))
	}
	if nextToken != nil && *nextToken != "" {
		parts = append(parts, fmt.Sprintf("NextToken=%s", *nextToken))
	}
	logSummary := strings.Join(parts, ", ")
	return cs.describeContextFiles(req, logSummary, contextID, parentFolderPath, 0, 0)
}

// describeContextFiles calls DescribeContextFiles and maps the response; pageNumber/pageSize are for logging only when >0.
func (cs *ContextService) describeContextFiles(
	req *mcp.DescribeContextFilesRequest,
	logSummary string,
	contextID string,
	parentFolderPath string,
	pageNumber int32,
	pageSize int32,
) (*ContextFileListResult, error) {
	logAPICall("DescribeContextFiles", logSummary)

	resp, err := cs.AgentBay.Client.DescribeContextFiles(req)
	if err != nil {
		logOperationError("DescribeContextFiles", err.Error(), true)
		return nil, err
	}

	requestID := models.ExtractRequestID(resp)

	entries := []*ContextFileEntry{}
	success := false
	var count *int32
	var errorMessage string
	var nextTok string
	var maxRes *int32

	if resp != nil && resp.Body != nil {
		if resp.Body.Success != nil {
			success = *resp.Body.Success
		}

		// Check for API-level errors
		if !success && resp.Body.Code != nil {
			code := tea.StringValue(resp.Body.Code)
			message := tea.StringValue(resp.Body.Message)
			if message == "" {
				message = "Unknown error"
			}
			errorMessage = fmt.Sprintf("[%s] %s", code, message)
			respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
			logAPIResponseWithDetails("DescribeContextFiles", requestID, false, nil, string(respJSON))
			return &ContextFileListResult{
				ApiResponse:  models.WithRequestID(requestID),
				Success:      false,
				Entries:      []*ContextFileEntry{},
				Count:        nil,
				NextToken:    "",
				MaxResults:   nil,
				ErrorMessage: errorMessage,
			}, nil
		}

		if resp.Body.Count != nil {
			count = resp.Body.Count
		}
		if resp.Body.NextToken != nil {
			nextTok = *resp.Body.NextToken
		}
		if resp.Body.MaxResults != nil {
			maxRes = resp.Body.MaxResults
		}
		for _, it := range resp.Body.Data {
			if it == nil {
				continue
			}
			entry := &ContextFileEntry{}
			if it.FileId != nil {
				entry.FileID = *it.FileId
			}
			if it.FileName != nil {
				entry.FileName = *it.FileName
			}
			if it.FilePath != nil {
				entry.FilePath = *it.FilePath
			}
			if it.FileType != nil {
				entry.FileType = *it.FileType
			}
			if it.GmtCreate != nil {
				entry.GmtCreate = *it.GmtCreate
			}
			if it.GmtModified != nil {
				entry.GmtModified = *it.GmtModified
			}
			if it.Size != nil {
				entry.Size = *it.Size
			}
			if it.Status != nil {
				entry.Status = *it.Status
			}
			entries = append(entries, entry)
		}

		keyFields := map[string]interface{}{
			"context_id":         contextID,
			"parent_folder_path": parentFolderPath,
			"entry_count":        len(entries),
		}
		if pageNumber > 0 || pageSize > 0 {
			keyFields["page_number"] = pageNumber
			keyFields["page_size"] = pageSize
		}
		if count != nil {
			keyFields["total_count"] = *count
		}
		if nextTok != "" {
			keyFields["has_next_page"] = true
			keyFields["next_token_length"] = len(nextTok)
		}
		if maxRes != nil {
			keyFields["max_results"] = *maxRes
		}
		respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
		logAPIResponseWithDetails("DescribeContextFiles", requestID, true, keyFields, string(respJSON))
	}

	return &ContextFileListResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      success,
		Entries:      entries,
		Count:        count,
		NextToken:    nextTok,
		MaxResults:   maxRes,
		ErrorMessage: "",
	}, nil
}

// DeleteFile deletes a file in a context.
//
// Parameters:
//   - contextID: The ID of the context
//   - filePath: The path to the file to delete
//
// Returns:
//   - *ContextFileDeleteResult: Result containing success status and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	client.Context.DeleteFile(contextResult.ContextID, "/data/file.txt")
func (cs *ContextService) DeleteFile(contextID string, filePath string) (*ContextFileDeleteResult, error) {
	req := &mcp.DeleteContextFileRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		ContextId:     tea.String(contextID),
		FilePath:      tea.String(filePath),
	}

	logAPICall("DeleteContextFile", fmt.Sprintf("ContextId=%s, FilePath=%s", contextID, filePath))

	resp, err := cs.AgentBay.Client.DeleteContextFile(req)
	if err != nil {
		logOperationError("DeleteContextFile", err.Error(), true)
		return nil, err
	}

	requestID := models.ExtractRequestID(resp)
	success := false
	var errorMessage string

	if resp != nil && resp.Body != nil {
		if resp.Body.Success != nil {
			success = *resp.Body.Success
		}

		// Check for API-level errors
		if !success && resp.Body.Code != nil {
			code := tea.StringValue(resp.Body.Code)
			message := tea.StringValue(resp.Body.Message)
			if message == "" {
				message = "Failed to delete file"
			}
			errorMessage = fmt.Sprintf("[%s] %s", code, message)
			respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
			logAPIResponseWithDetails("DeleteContextFile", requestID, false, nil, string(respJSON))
		} else {
			keyFields := map[string]interface{}{
				"context_id": contextID,
				"file_path":  filePath,
			}
			respJSON, _ := json.MarshalIndent(resp.Body, "", "  ")
			logAPIResponseWithDetails("DeleteContextFile", requestID, true, keyFields, string(respJSON))
		}
	}

	return &ContextFileDeleteResult{
		ApiResponse:  models.WithRequestID(requestID),
		Success:      success,
		ErrorMessage: errorMessage,
	}, nil
}

// ClearAsync asynchronously initiates a task to clear the context's persistent data.
// This is a non-blocking method that returns immediately after initiating the clearing task.
// The context's state will transition to "clearing" while the operation is in progress.
//
// Parameters:
//   - contextID: Unique ID of the context to clear
//
// Returns:
//   - *ContextClearResult: Result containing task status and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	clearResult, _ := client.Context.ClearAsync(contextResult.ContextID)
func (cs *ContextService) ClearAsync(contextID string) (*ContextClearResult, error) {
	request := &mcp.ClearContextRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		Id:            tea.String(contextID),
	}

	// Log API request
	logAPICall("ClearContext", fmt.Sprintf("ContextId=%s", contextID))

	response, err := cs.AgentBay.Client.ClearContext(request)

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log API response
	if err != nil {
		logOperationError("ClearContext", err.Error(), true)
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: fmt.Sprintf("Failed to start context clearing: %v", err),
		}, nil
	}

	// Check for empty response body
	if response == nil || response.Body == nil {
		respJSON, _ := json.MarshalIndent(response, "", "  ")
		logAPIResponseWithDetails("ClearContext", requestID, false, nil, string(respJSON))
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: "Empty response body",
		}, nil
	}

	// Check for API-level errors
	if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
		errorMsg := "Unknown error"
		if response.Body.Message != nil {
			errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
		} else {
			errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
		}
		respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("ClearContext", requestID, false, nil, string(respJSON))
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: errorMsg,
		}, nil
	}

	// ClearContext API returns success info without Data field
	// Initial status is "clearing" when the task starts
	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	logAPIResponseWithDetails("ClearContext", requestID, true, nil, string(respJSON))
	return &ContextClearResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success:      true,
		ContextID:    contextID,
		Status:       "clearing",
		ErrorMessage: "",
	}, nil
}

// GetClearStatus queries the status of the clearing task.
// This method calls GetContext API directly with contextID and parses the raw response to extract
// the state field, which indicates the current clearing status.
//
// Parameters:
//   - contextID: Unique ID of the context to check
//
// Returns:
//   - *ContextClearResult: Result containing current task status and request ID
//   - error: Error if the operation fails
//
// State Transitions:
//   - "clearing": Data clearing is in progress
//   - "available": Clearing completed successfully (final success state)
//   - "in-use": Context is being used
//   - "pre-available": Context is being prepared
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	contextResult, _ := client.Context.Get("my-context", true)
//	statusResult, _ := client.Context.GetClearStatus(contextResult.ContextID)
func (cs *ContextService) GetClearStatus(contextID string) (*ContextClearResult, error) {
	request := &mcp.GetContextRequest{
		Authorization: tea.String("Bearer " + cs.AgentBay.APIKey),
		ContextId:     tea.String(contextID),
		AllowCreate:   tea.Bool(false),
	}

	// Log API request
	logAPICall("GetContext", fmt.Sprintf("ContextId=%s (for clear status)", contextID))

	response, err := cs.AgentBay.Client.GetContext(request)

	// Extract RequestID
	requestID := models.ExtractRequestID(response)

	// Log API response
	if err != nil {
		logOperationError("GetContext (for clear status)", err.Error(), true)
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: fmt.Sprintf("Failed to get clear status: %v", err),
		}, nil
	}

	// Check for empty response body
	if response == nil || response.Body == nil {
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: "Empty response body",
		}, nil
	}

	// Check for API-level errors
	if response.Body.Success != nil && !*response.Body.Success && response.Body.Code != nil {
		errorMsg := "Unknown error"
		if response.Body.Message != nil {
			errorMsg = fmt.Sprintf("[%s] %s", *response.Body.Code, *response.Body.Message)
		} else {
			errorMsg = fmt.Sprintf("[%s] Unknown error", *response.Body.Code)
		}
		respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
		logAPIResponseWithDetails("GetContext (for clear status)", requestID, false, nil, string(respJSON))
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: errorMsg,
		}, nil
	}

	// Check if data exists
	if response.Body.Data == nil {
		return &ContextClearResult{
			ApiResponse: models.ApiResponse{
				RequestID: requestID,
			},
			Success:      false,
			Status:       "",
			ContextID:    contextID,
			ErrorMessage: "No data in response",
		}, nil
	}

	data := response.Body.Data

	// Extract clearing status from the response data object
	// The server's state field indicates the clearing status:
	// - "clearing": Clearing is in progress
	// - "available": Clearing completed successfully
	// - "in-use": Context is being used
	// - "pre-available": Context is being prepared
	var contextIDValue string
	if data.Id != nil {
		contextIDValue = tea.StringValue(data.Id)
	}
	var state string
	if data.State != nil {
		state = tea.StringValue(data.State)
	} else {
		state = "clearing" // Default to clearing if state is not provided
	}

	respJSON, _ := json.MarshalIndent(response.Body, "", "  ")
	keyFields := map[string]interface{}{
		"context_id": contextIDValue,
		"state":      state,
	}
	logAPIResponseWithDetails("GetContext (for clear status)", requestID, true, keyFields, string(respJSON))

	return &ContextClearResult{
		ApiResponse: models.ApiResponse{
			RequestID: requestID,
		},
		Success:      true,
		ContextID:    contextIDValue,
		Status:       state,
		ErrorMessage: "",
	}, nil
}

// Clear synchronously clears the context's persistent data and waits for the final result.
// This method wraps the ClearAsync and GetClearStatus polling logic.
//
// The clearing process transitions through the following states:
// - "clearing": Data clearing is in progress
// - "available": Clearing completed successfully (final success state)
//
// Parameters:
//   - contextID: Unique ID of the context to clear
//   - timeout: Timeout in seconds to wait for task completion (default: 60)
//   - pollInterval: Interval in seconds between status polls (default: 2)
//
// Returns a ContextClearResult object containing the final task result.
// The status field will be "available" on success, or other states if interrupted.
func (cs *ContextService) Clear(contextID string, timeoutSeconds int, pollIntervalSeconds float64) (*ContextClearResult, error) {
	// 1. Asynchronously start the clearing task
	startResult, err := cs.ClearAsync(contextID)
	if err != nil {
		return nil, err
	}
	if !startResult.Success {
		return startResult, nil
	}

	// Log started clearing task
	LogInfo(fmt.Sprintf("Started context clearing task for: %s", contextID))

	// 2. Poll task status until completion or timeout
	maxAttempts := int(float64(timeoutSeconds) / pollIntervalSeconds)
	attempt := 0

	for attempt < maxAttempts {
		// Wait before querying
		if attempt > 0 {
			time.Sleep(time.Duration(pollIntervalSeconds) * time.Second)
		}
		attempt++

		// Query task status (using GetContext API with context ID)
		statusResult, err := cs.GetClearStatus(contextID)
		if err != nil {
			logOperationError("Clear", fmt.Sprintf("Failed to get clear status: %v", err), false)
			return statusResult, err
		}

		if !statusResult.Success {
			logOperationError("Clear", fmt.Sprintf("Failed to get clear status: %s", statusResult.ErrorMessage), false)
			return statusResult, nil
		}

		LogInfo(fmt.Sprintf("Clear task status: %s (attempt %d/%d)", statusResult.Status, attempt, maxAttempts))

		// Check if completed
		// When clearing is complete, the state changes from "clearing" to "available"
		if statusResult.Status == "available" {
			LogInfo("Context cleared successfully")
			return &ContextClearResult{
				ApiResponse: models.ApiResponse{
					RequestID: startResult.RequestID,
				},
				Success:      true,
				ContextID:    statusResult.ContextID,
				Status:       statusResult.Status,
				ErrorMessage: "",
			}, nil
		} else if statusResult.Status != "clearing" && statusResult.Status != "pre-available" {
			// If status is not "clearing" or "pre-available", and not "available",
			// treat it as a potential error or unexpected state
			logOperationError("Clear", fmt.Sprintf("Context in unexpected state: %s", statusResult.Status), false)
			// Continue polling as the state might transition to "available"
		}
	}

	// Timeout
	errorMsg := fmt.Sprintf("Context clearing timed out after %d seconds", timeoutSeconds)
	logOperationError("Clear", errorMsg, false)
	return nil, fmt.Errorf("%s", errorMsg)
}
