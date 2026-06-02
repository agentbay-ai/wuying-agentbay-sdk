package interfaces

import (
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

//go:generate mockgen -destination=../../../tests/pkg/unit/mock/mock_agentbay.go -package=mock github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/interface AgentBayInterface

// AgentBayInterface defines the interface for AgentBay operations
type AgentBayInterface interface {
	// Create creates a new session
	Create(params *agentbay.CreateSessionParams) (*agentbay.SessionResult, error)

	// Delete deletes a session
	Delete(session *agentbay.Session, syncContext ...bool) (*agentbay.DeleteResult, error)

	// List returns paginated list of Sessions filtered by status and labels
	List(status string, labels map[string]string, page *int, limit *int32, imageId string) (*agentbay.SessionListResult, error)

	// BetaPause synchronously pauses a session (beta)
	BetaPause(session *agentbay.Session, timeout int, pollInterval float64) (*models.SessionPauseResult, error)

	// BetaResume synchronously resumes a session (beta)
	BetaResume(session *agentbay.Session, timeout int, pollInterval float64) (*models.SessionResumeResult, error)
}
