package agentbay_test

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/unit/mock"
	"github.com/golang/mock/gomock"
	"github.com/stretchr/testify/assert"
)

func TestAgentBay_Create_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior
	params := &agentbay.CreateSessionParams{
		Labels: map[string]string{"env": "test"},
	}
	expectedResult := &agentbay.SessionResult{
		Session: &agentbay.Session{
			SessionID: "new_session_id",
		},
	}
	mockAgentBay.EXPECT().Create(params).Return(expectedResult, nil)

	// Test Create method call
	result, err := mockAgentBay.Create(params)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "new_session_id", result.Session.SessionID)
}

func TestAgentBay_Delete_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior
	session := &agentbay.Session{
		SessionID: "test_session_id",
	}
	expectedResult := &agentbay.DeleteResult{
		Success: true,
	}
	mockAgentBay.EXPECT().Delete(session).Return(expectedResult, nil)

	// Test Delete method call
	result, err := mockAgentBay.Delete(session)

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.True(t, result.Success)
}

func TestAgentBay_List_NoLabels_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior - list all sessions without labels
	expectedResult := &agentbay.SessionListResult{
		SessionIds: []map[string]interface{}{
			{"sessionId": "session-1"},
			{"sessionId": "session-2"},
			{"sessionId": "session-3"},
		},
		MaxResults: 10,
		TotalCount: 3,
	}
	mockAgentBay.EXPECT().List("", nil, nil, nil, "").Return(expectedResult, nil)

	// Test List method call without labels
	result, err := mockAgentBay.List("", nil, nil, nil, "")

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.SessionIds, 3)
	// Extract sessionId from the first session data
	sessionData := result.SessionIds[0]
	if sessionId, exists := sessionData["sessionId"]; exists {
		assert.Equal(t, "session-1", sessionId)
	}
	assert.Equal(t, int32(10), result.MaxResults)
	assert.Equal(t, int32(3), result.TotalCount)
}

func TestAgentBay_List_WithLabels_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior - list sessions with labels
	labels := map[string]string{"env": "prod"}
	expectedResult := &agentbay.SessionListResult{
		SessionIds: []map[string]interface{}{
			{"sessionId": "session-prod-1"},
		},
		MaxResults: 10,
		TotalCount: 1,
	}
	mockAgentBay.EXPECT().List("", labels, nil, nil, "").Return(expectedResult, nil)

	// Test List method call with labels
	result, err := mockAgentBay.List("", labels, nil, nil, "")

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.SessionIds, 1)
	// Extract sessionId from the session data
	sessionData := result.SessionIds[0]
	if sessionId, exists := sessionData["sessionId"]; exists {
		assert.Equal(t, "session-prod-1", sessionId)
	}
}

func TestAgentBay_List_WithPagination_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior - list sessions with pagination
	labels := map[string]string{"env": "prod"}
	page := 2
	limit := int32(5)
	expectedResult := &agentbay.SessionListResult{
		SessionIds: []map[string]interface{}{
			{"sessionId": "session-6"},
			{"sessionId": "session-7"},
		},
		MaxResults: 5,
		TotalCount: 10,
	}
	mockAgentBay.EXPECT().List("", labels, &page, &limit, "").Return(expectedResult, nil)

	// Test List method call with pagination
	result, err := mockAgentBay.List("", labels, &page, &limit, "")

	// Verify call success
	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.SessionIds, 2)
	// Extract sessionId from the first session data
	sessionData := result.SessionIds[0]
	if sessionId, exists := sessionData["sessionId"]; exists {
		assert.Equal(t, "session-6", sessionId)
	}
	assert.Equal(t, int32(5), result.MaxResults)
	assert.Equal(t, int32(10), result.TotalCount)
}

func TestAgentBay_Error_WithMockClient(t *testing.T) {
	ctrl := gomock.NewController(t)
	defer ctrl.Finish()

	// Create mock AgentBay
	mockAgentBay := mock.NewMockAgentBayInterface(ctrl)

	// Set expected behavior - return error
	mockAgentBay.EXPECT().List("", nil, nil, nil, "").Return(nil, assert.AnError)

	// Test error case
	result, err := mockAgentBay.List("", nil, nil, nil, "")

	// Verify error handling
	assert.Error(t, err)
	assert.Nil(t, result)
}
