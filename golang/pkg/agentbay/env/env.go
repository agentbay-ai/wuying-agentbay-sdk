package env

import (
	"encoding/json"
	"fmt"
	"sync"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// EnvResult represents the result of getting environment variables
type EnvResult struct {
	models.ApiResponse
	Success      bool              `json:"success"`
	Envs         map[string]string `json:"envs"`
	ErrorMessage string            `json:"error_message,omitempty"`
}

// BoolResult represents a boolean operation result
type BoolResult struct {
	models.ApiResponse
	Success      bool   `json:"success"`
	ErrorMessage string `json:"error_message,omitempty"`
}

// envEntry is the array element format expected by the backend set_env tool
type envEntry struct {
	Key   string `json:"key"`
	Value string `json:"value"`
}

const envServer = "wuying_system"

var envToolNames = []string{"set_env", "get_env"}

// EnvToolRegistrar allows the Env module to register missing tools in the session.
type EnvToolRegistrar interface {
	GetMcpServerForTool(toolName string) string
	AppendMcpTool(name, server string)
}

// Env handles environment variable operations in the AgentBay cloud environment.
type Env struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
	registrar     EnvToolRegistrar
	toolsOnce     sync.Once
}

// NewEnv creates a new Env instance
func NewEnv(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
}, registrar ...EnvToolRegistrar) *Env {
	e := &Env{Session: session}
	if len(registrar) > 0 {
		e.registrar = registrar[0]
	}
	return e
}

func (e *Env) ensureEnvToolsRegistered() {
	if e.registrar == nil {
		return
	}
	e.toolsOnce.Do(func() {
		for _, name := range envToolNames {
			if e.registrar.GetMcpServerForTool(name) == "" {
				e.registrar.AppendMcpTool(name, envServer)
			}
		}
	})
}

// Set sets or updates global environment variables in the session sandbox.
func (e *Env) Set(envs map[string]string) (*BoolResult, error) {
	e.ensureEnvToolsRegistered()
	if len(envs) == 0 {
		return nil, fmt.Errorf("envs must not be empty")
	}

	entries := make([]envEntry, 0, len(envs))
	for k, v := range envs {
		entries = append(entries, envEntry{Key: k, Value: v})
	}

	args := map[string]interface{}{
		"envs": entries,
	}

	result, err := e.Session.CallMcpTool("set_env", args)
	if err != nil {
		return &BoolResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to set environment variables: %v", err),
		}, nil
	}

	return &BoolResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      result.Success,
		ErrorMessage: result.ErrorMessage,
	}, nil
}

// Get retrieves global environment variables from the session sandbox.
// If keys is nil or empty, returns all environment variables.
func (e *Env) Get(keys ...string) (*EnvResult, error) {
	e.ensureEnvToolsRegistered()
	args := map[string]interface{}{}
	if len(keys) > 0 {
		args["keys"] = keys
	}

	result, err := e.Session.CallMcpTool("get_env", args)
	if err != nil {
		return &EnvResult{
			Success:      false,
			ErrorMessage: fmt.Sprintf("Failed to get environment variables: %v", err),
		}, nil
	}

	envs := make(map[string]string)
	if result.Success && result.Data != "" {
		if err := json.Unmarshal([]byte(result.Data), &envs); err != nil {
			// Return success but with empty envs if parsing fails
			return &EnvResult{
				ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
				Success:      result.Success,
				Envs:         envs,
				ErrorMessage: "",
			}, nil
		}
	}

	return &EnvResult{
		ApiResponse:  models.ApiResponse{RequestID: result.RequestID},
		Success:      result.Success,
		Envs:         envs,
		ErrorMessage: result.ErrorMessage,
	}, nil
}
