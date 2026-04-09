# Env API Reference

## Overview

The Env module provides methods for setting and querying global environment variables within a session sandbox.
Variables set via this module persist across all MCP tools (shell, code interpreter, etc.) within the session.

## Type BoolResult

```go
type BoolResult struct {
	models.ApiResponse
	Success		bool	`json:"success"`
	ErrorMessage	string	`json:"error_message,omitempty"`
}
```

BoolResult represents a boolean operation result

## Type Env

```go
type Env struct {
	Session	interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
		CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
	}
	registrar	EnvToolRegistrar
	toolsOnce	sync.Once
}
```

Env handles environment variable operations in the AgentBay cloud environment.

### Methods

### Get

```go
func (e *Env) Get(keys ...string) (*EnvResult, error)
```

Get retrieves global environment variables from the session sandbox. If keys is nil or empty,
returns all environment variables.

### Set

```go
func (e *Env) Set(envs map[string]string) (*BoolResult, error)
```

Set sets or updates global environment variables in the session sandbox.

### Related Functions

### NewEnv

```go
func NewEnv(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
	CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
}, registrar ...EnvToolRegistrar) *Env
```

NewEnv creates a new Env instance

## Type EnvResult

```go
type EnvResult struct {
	models.ApiResponse
	Success		bool			`json:"success"`
	Envs		map[string]string	`json:"envs"`
	ErrorMessage	string			`json:"error_message,omitempty"`
}
```

EnvResult represents the result of getting environment variables

## Type EnvToolRegistrar

```go
type EnvToolRegistrar interface {
	GetMcpServerForTool(toolName string) string
	AppendMcpTool(name, server string)
}
```

EnvToolRegistrar allows the Env module to register missing tools in the session.

## Type envEntry

```go
type envEntry struct {
	Key	string	`json:"key"`
	Value	string	`json:"value"`
}
```

envEntry is the array element format expected by the backend set_env tool

## Best Practices

1. Use env.set to configure variables before running shell commands or code
2. Both keys and values must be strings
3. Setting a key that already exists will overwrite the previous value
4. Use env.get with specific keys to reduce response size

## Related Resources

- [Session API Reference](session.md)
- [Command API Reference](command.md)

---

*Documentation generated automatically from Go source code.*
