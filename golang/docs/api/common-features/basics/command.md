# Command API Reference

## ⚡ Related Tutorial

- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md) - Learn how to execute commands in sessions

## Overview

The Command module provides methods for executing shell commands within a session in the AgentBay cloud environment.
Commands support configurable timeouts and optional working directory or environment settings.

Command templates for various AgentBay operations.

This module contains shell command templates used by different modules
to execute operations in remote environments.

Template naming convention:
- Use descriptive names that clearly indicate the operation
- Group templates by functionality (mobile, desktop, network, etc.)
- Use consistent parameter naming across similar templates

Parameter conventions:
- Use snake_case for parameter names
- Include descriptive parameter names (e.g., lock_switch, package_list)
- Document expected parameter types and values

## Type Command

```go
type Command struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
}
```

Command handles command execution operations in the AgentBay cloud environment.

### Methods

### Exec

```go
func (c *Command) Exec(command string, options ...interface{}) (*CommandResult, error)
```

Exec is an alias of ExecuteCommand.

### ExecuteCommand

```go
func (c *Command) ExecuteCommand(command string, options ...interface{}) (*CommandResult, error)
```

ExecuteCommand executes a shell command in the session environment.

This method supports both the legacy signature (command string, timeoutMs ...int) and the Functional
Options pattern for flexible configuration.

Legacy usage (backward compatible):
  - cmd.ExecuteCommand("ls -la")
  - cmd.ExecuteCommand("ls -la", 5000)

Functional Options usage (recommended for new code):
  - cmd.ExecuteCommand("ls -la", WithTimeoutMs(5000))
  - cmd.ExecuteCommand("pwd", WithCwd("/tmp"), WithEnvs(map[string]string{"VAR": "value"}))

Parameters:
  - command: The shell command to execute
  - options: Either an int (timeoutMs in milliseconds) for legacy usage, or CommandOption functions
    for Functional Options pattern. Default is 50000ms (50s).

Returns:
  - *CommandResult: Result containing command output, exit code, stdout, stderr, trace_id, and
    request ID
  - error: Error if the operation fails

**Example:**

```go
// Default usage

cmd.ExecuteCommand("ls")

// Legacy usage (backward compatible)

cmd.ExecuteCommand("ls", 5000)

// New style with Functional Options

cmd.ExecuteCommand("ls", WithTimeoutMs(5000))

// Combined options

cmd.ExecuteCommand("pwd",
    WithTimeoutMs(5000),
    WithCwd("/tmp"),
    WithEnvs(map[string]string{"FOO": "bar"}),
)
```

### Run

```go
func (c *Command) Run(command string, options ...interface{}) (*CommandResult, error)
```

Run is an alias of ExecuteCommand.

### Related Functions

### NewCommand

```go
func NewCommand(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
}) *Command
```

NewCommand creates a new Command instance

## Type CommandOption

```go
type CommandOption func(*commandOptions)
```

CommandOption is a function type for configuring ExecuteCommand options. This enables the Functional
Options pattern for flexible and extensible API design.

### Related Functions

### WithCwd

```go
func WithCwd(cwd string) CommandOption
```

WithCwd sets the working directory for command execution. If not set, the command runs in the
default session directory.

**Example:**

```go
cmd.ExecuteCommand("pwd", WithCwd("/tmp"))
```

### WithEnvs

```go
func WithEnvs(envs map[string]string) CommandOption
```

WithEnvs sets environment variables for command execution. These variables are set for the command
execution only.

**Example:**

```go
cmd.ExecuteCommand("echo $VAR", WithEnvs(map[string]string{"VAR": "value"}))
```

### WithTimeoutMs

```go
func WithTimeoutMs(timeoutMs int) CommandOption
```

WithTimeoutMs sets the timeout for command execution in milliseconds.

**Example:**

```go
cmd.ExecuteCommand("ls -la", WithTimeoutMs(5000))
```

## Type CommandResult

```go
type CommandResult struct {
	// Embed the basic API response structure
	models.ApiResponse
	// Success indicates whether the command execution was successful
	Success	bool	`json:"success"`
	// Output contains the command execution output (for backward compatibility, equals stdout + stderr)
	Output	string	`json:"output"`
	// ErrorMessage contains error message if the operation failed
	ErrorMessage	string	`json:"error_message,omitempty"`
	// ExitCode is the exit code of the command execution. Default is 0.
	ExitCode	int	`json:"exit_code"`
	// Stdout is the standard output from the command execution
	Stdout	string	`json:"stdout"`
	// Stderr is the standard error from the command execution
	Stderr	string	`json:"stderr"`
	// TraceID is the trace ID for error tracking. Only present when exit_code != 0. Used for quick problem localization.
	TraceID	string	`json:"trace_id,omitempty"`
}
```

CommandResult represents the result of a command execution

## Type commandOptions

```go
type commandOptions struct {
	timeoutMs	int
	cwd		string
	envs		map[string]string
}
```

commandOptions holds the configuration for command execution

## Type parsedShellPayload

```go
type parsedShellPayload struct {
	stdout		string
	stderr		string
	exitCode	int
	traceID		string
}
```

parsedShellPayload holds the parsed fields from a shell-tool MCP response.

## Functions

### GetMobileCommandTemplate

```go
func GetMobileCommandTemplate(templateName string) (string, bool)
```

GetMobileCommandTemplate returns a mobile command template by name

## Best Practices

1. Always specify appropriate timeout values based on expected command duration
2. Handle command execution errors gracefully
3. Use absolute paths when referencing files in commands
4. Be aware that commands run with session user permissions
5. Clean up temporary files created by commands

## Related Resources

- [Session API Reference](session.md)
- [FileSystem API Reference](filesystem.md)

---

*Documentation generated automatically from Go source code.*
