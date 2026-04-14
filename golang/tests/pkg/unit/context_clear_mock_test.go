package agentbay_test

import (
	"testing"

	"github.com/alibabacloud-go/tea/tea"
	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/stretchr/testify/assert"
)

// TestContext_ClearAsync_ResponseStructure verifies the ClearContext response struct shape
func TestContext_ClearAsync_ResponseStructure(t *testing.T) {
	mockResponse := &mcp.ClearContextResponse{
		Body: &mcp.ClearContextResponseBody{
			Success:   tea.Bool(true),
			RequestId: tea.String("test-request-id"),
			Code:      nil,
			Message:   nil,
		},
	}
	assert.NotNil(t, mockResponse)
	assert.NotNil(t, mockResponse.Body)
	assert.True(t, tea.BoolValue(mockResponse.Body.Success))
	assert.Equal(t, "test-request-id", tea.StringValue(mockResponse.Body.RequestId))
}

// TestContext_ClearAsync_ErrorResponseStructure verifies error result structure
func TestContext_ClearAsync_ErrorResponseStructure(t *testing.T) {
	result := &agentbay.ContextClearResult{
		Success:      false,
		Status:       "",
		ContextID:    "invalid-context-id",
		ErrorMessage: "Failed to start context clearing: some error",
	}
	assert.False(t, result.Success)
	assert.NotEmpty(t, result.ErrorMessage)
	assert.Equal(t, "invalid-context-id", result.ContextID)
}

// TestContextClearResult_Initialization verifies result struct field assignment
func TestContextClearResult_Initialization(t *testing.T) {
	result := &agentbay.ContextClearResult{
		Success:      true,
		Status:       "clearing",
		ContextID:    "context-123",
		ErrorMessage: "",
	}

	assert.True(t, result.Success)
	assert.Equal(t, "clearing", result.Status)
	assert.Equal(t, "context-123", result.ContextID)
	assert.Empty(t, result.ErrorMessage)
}

// TestContextClearResult_Defaults verifies zero-value defaults of ContextClearResult
func TestContextClearResult_Defaults(t *testing.T) {
	result := &agentbay.ContextClearResult{}

	assert.False(t, result.Success)
	assert.Empty(t, result.Status)
	assert.Empty(t, result.ContextID)
	assert.Empty(t, result.ErrorMessage)
}

// TestContextClearResult_AllStatuses verifies all known status values are valid strings
func TestContextClearResult_AllStatuses(t *testing.T) {
	statuses := []string{"clearing", "available", "", "FAILURE"}
	for _, status := range statuses {
		result := &agentbay.ContextClearResult{
			Status: status,
		}
		assert.Equal(t, status, result.Status)
	}
}

// TestContextClearResult_SuccessAndFailureFields verifies Success/ErrorMessage fields
func TestContextClearResult_SuccessAndFailureFields(t *testing.T) {
	// Success case
	success := &agentbay.ContextClearResult{
		Success: true,
		Status:  "available",
	}
	assert.True(t, success.Success)
	assert.Empty(t, success.ErrorMessage)

	// Failure case
	failure := &agentbay.ContextClearResult{
		Success:      false,
		Status:       "FAILURE",
		ErrorMessage: "context clearing failed",
	}
	assert.False(t, failure.Success)
	assert.Equal(t, "FAILURE", failure.Status)
	assert.NotEmpty(t, failure.ErrorMessage)
}
