package command

import (
	"encoding/json"
	"fmt"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// CommandResult represents the result of a command execution
type CommandResult struct {
	// Embed the basic API response structure
	models.ApiResponse
	// Success indicates whether the command execution was successful
	Success bool `json:"success"`
	// Output contains the command execution output (for backward compatibility, equals stdout + stderr)
	Output string `json:"output"`
	// ErrorMessage contains error message if the operation failed
	ErrorMessage string `json:"error_message,omitempty"`
	// ExitCode is the exit code of the command execution. Default is 0.
	ExitCode int `json:"exit_code"`
	// Stdout is the standard output from the command execution
	Stdout string `json:"stdout"`
	// Stderr is the standard error from the command execution
	Stderr string `json:"stderr"`
	// TraceID is the trace ID for error tracking. Only present when exit_code != 0. Used for quick problem localization.
	TraceID string `json:"trace_id,omitempty"`
}

// Command handles command execution operations in the AgentBay cloud environment.
type Command struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
}

// NewCommand creates a new Command instance
func NewCommand(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
}) *Command {
	return &Command{
		Session: session,
	}
}

// ==================== Option Definitions ====================

// commandOptions holds the configuration for command execution
type commandOptions struct {
	timeoutMs int
	cwd       string
	envs      map[string]string
}

// CommandOption is a function type for configuring ExecuteCommand options.
// This enables the Functional Options pattern for flexible and extensible API design.
type CommandOption func(*commandOptions)

// WithTimeoutMs sets the timeout for command execution in milliseconds.
//
// Example:
//
//	cmd.ExecuteCommand("ls -la", WithTimeoutMs(5000))
func WithTimeoutMs(timeoutMs int) CommandOption {
	return func(opts *commandOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// WithCwd sets the working directory for command execution.
// If not set, the command runs in the default session directory.
//
// Example:
//
//	cmd.ExecuteCommand("pwd", WithCwd("/tmp"))
func WithCwd(cwd string) CommandOption {
	return func(opts *commandOptions) {
		opts.cwd = cwd
	}
}

// WithEnvs sets environment variables for command execution.
// These variables are set for the command execution only.
//
// Example:
//
//	cmd.ExecuteCommand("echo $VAR", WithEnvs(map[string]string{"VAR": "value"}))
func WithEnvs(envs map[string]string) CommandOption {
	return func(opts *commandOptions) {
		opts.envs = envs
	}
}

// ExecuteCommand executes a shell command in the session environment.
//
// This method supports both the legacy signature (command string, timeoutMs ...int)
// and the Functional Options pattern for flexible configuration.
//
// Legacy usage (backward compatible):
//   - cmd.ExecuteCommand("ls -la")
//   - cmd.ExecuteCommand("ls -la", 5000)
//
// Functional Options usage (recommended for new code):
//   - cmd.ExecuteCommand("ls -la", WithTimeoutMs(5000))
//   - cmd.ExecuteCommand("pwd", WithCwd("/tmp"), WithEnvs(map[string]string{"VAR": "value"}))
//
// Parameters:
//   - command: The shell command to execute
//   - options: Either an int (timeoutMs in milliseconds) for legacy usage, or
//     CommandOption functions for Functional Options pattern.
//     Default is 50000ms (50s).
//
// Returns:
//   - *CommandResult: Result containing command output, exit code, stdout,
//     stderr, trace_id, and request ID
//   - error: Error if the operation fails
//
// Example:
//
//	// Default usage
//	cmd.ExecuteCommand("ls")
//
//	// Legacy usage (backward compatible)
//	cmd.ExecuteCommand("ls", 5000)
//
//	// New style with Functional Options
//	cmd.ExecuteCommand("ls", WithTimeoutMs(5000))
//
//	// Combined options
//	cmd.ExecuteCommand("pwd",
//	    WithTimeoutMs(5000),
//	    WithCwd("/tmp"),
//	    WithEnvs(map[string]string{"FOO": "bar"}),
//	)
func (c *Command) ExecuteCommand(command string, options ...interface{}) (*CommandResult, error) {
	// Default configuration
	opts := &commandOptions{
		timeoutMs: 1000, // Default 1 second
		cwd:       "",
		envs:      nil,
	}

	// Handle both old and new styles
	for _, opt := range options {
		switch v := opt.(type) {
		case int: // Old: ExecuteCommand("ls", 5000)
			if v > 0 {
				opts.timeoutMs = v
			}
		case CommandOption: // New: ExecuteCommand("ls", WithTimeoutMs(5000))
			if v != nil {
				v(opts)
			}
		}
	}

	return c.executeCommandInternal(command, opts.timeoutMs, opts.cwd, opts.envs)
}

// Run is an alias of ExecuteCommand.
func (c *Command) Run(command string, options ...interface{}) (*CommandResult, error) {
	return c.ExecuteCommand(command, options...)
}

// Exec is an alias of ExecuteCommand.
func (c *Command) Exec(command string, options ...interface{}) (*CommandResult, error) {
	return c.ExecuteCommand(command, options...)
}

// executeCommandInternal is the internal implementation of command execution
func (c *Command) executeCommandInternal(
	command string,
	timeout int,
	cwd string,
	envs map[string]string,
) (*CommandResult, error) {
	// Note: In Go, envs is typed as map[string]string, which enforces type safety at compile time.
	// All keys and values are guaranteed to be strings by the type system.
	// This validation is kept for consistency with other SDKs and documentation purposes.

	// Build request arguments
	args := map[string]interface{}{
		"command":    command,
		"timeout_ms": timeout,
	}
	if cwd != "" {
		args["cwd"] = cwd
	}
	if len(envs) > 0 {
		args["envs"] = envs
	}

	// Use Session's CallMcpTool method
	result, err := c.Session.CallMcpTool("shell", args)
	if err != nil {
		return nil, fmt.Errorf("failed to execute command: %w", err)
	}

	if result.Success {
		parsed := parseShellPayload(result.Data)
		return &CommandResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Success:      parsed.exitCode == 0,
			Output:       parsed.stdout + parsed.stderr,
			ExitCode:     parsed.exitCode,
			Stdout:       parsed.stdout,
			Stderr:       parsed.stderr,
			TraceID:      parsed.traceID,
			ErrorMessage: result.ErrorMessage,
		}, nil
	} else {
		rawErr := result.ErrorMessage
		parsed := parseShellPayload(rawErr)
		effectiveExitCode := parsed.exitCode
		if effectiveExitCode == 0 {
			effectiveExitCode = 1
		}
		effectiveError := parsed.stderr
		if effectiveError == "" {
			effectiveError = rawErr
		}
		if effectiveError == "" {
			effectiveError = "Failed to execute command"
		}
		return &CommandResult{
			ApiResponse: models.ApiResponse{
				RequestID: result.RequestID,
			},
			Success:      false,
			Output:       parsed.stdout + parsed.stderr,
			ExitCode:     effectiveExitCode,
			Stdout:       parsed.stdout,
			Stderr:       parsed.stderr,
			TraceID:      parsed.traceID,
			ErrorMessage: effectiveError,
		}, nil
	}
}

// parsedShellPayload holds the parsed fields from a shell-tool MCP response.
type parsedShellPayload struct {
	stdout   string
	stderr   string
	exitCode int
	traceID  string
}

// looksLikeWrappedShellPayload conservatively determines whether a parsed JSON
// map looks like the shell-tool wrapped envelope {exit_code, stdout, stderr}.
//
// Different sandbox images return data in different shapes:
//   - Wrapped (code_latest): {"exit_code":0,"stdout":"...","stderr":"..."}
//   - Raw (imgc-* / openclaw): the command's stdout returned verbatim
//
// We require strong signals to avoid mistaking user command JSON output
// for the wrapper:
//  1. Integer exit_code + at least one string stdout/stderr, OR
//  2. Both string stdout and stderr present.
func looksLikeWrappedShellPayload(data map[string]interface{}) bool {
	_, hasStdout := data["stdout"].(string)
	_, hasStderr := data["stderr"].(string)
	exitCodeVal, hasExitCode := data["exit_code"]
	hasIntExitCode := false
	if hasExitCode {
		if floatVal, ok := exitCodeVal.(float64); ok {
			hasIntExitCode = floatVal == float64(int(floatVal))
		}
	}
	if hasIntExitCode && (hasStdout || hasStderr) {
		return true
	}
	return hasStdout && hasStderr
}

// parseShellPayload parses a shell-tool MCP response payload.
// It detects the wrapped format conservatively; anything else is treated
// as raw command output returned verbatim.
func parseShellPayload(rawData string) parsedShellPayload {
	if rawData == "" {
		return parsedShellPayload{}
	}
	var dataMap map[string]interface{}
	if err := json.Unmarshal([]byte(rawData), &dataMap); err == nil {
		if looksLikeWrappedShellPayload(dataMap) {
			stdout, _ := dataMap["stdout"].(string)
			stderr, _ := dataMap["stderr"].(string)
			exitCode := 0
			if val, ok := dataMap["exit_code"].(float64); ok {
				exitCode = int(val)
			}
			traceID, _ := dataMap["traceId"].(string)
			return parsedShellPayload{
				stdout:   stdout,
				stderr:   stderr,
				exitCode: exitCode,
				traceID:  traceID,
			}
		}
	}
	// Raw stdout: return the entire payload verbatim.
	return parsedShellPayload{stdout: rawData}
}
