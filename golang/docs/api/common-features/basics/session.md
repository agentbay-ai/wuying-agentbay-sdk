# Session API Reference

## 🔧 Related Tutorial

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Detailed tutorial on session lifecycle and management

## Overview

The Session class represents an active cloud environment instance in AgentBay. It provides access to all service modules (filesystem, command, browser, code, etc.) and manages the lifecycle of the cloud environment.

## Type Session

```go
type Session struct {
	AgentBay	*AgentBay
	SessionID	string
	ImageId		string	// ImageId used when creating this session
	McpTools	[]McpTool

	// Application instance ID
	AppInstanceId	string

	// Resource URL for accessing the session
	ResourceUrl	string

	// VpcIp / VpcId are returned only for sessions created on a custom VPC network.
	// For default-network sessions both fields are empty.
	VpcIp	string
	VpcId	string

	// LinkUrl-based direct tool call (non-VPC)
	Token	string
	LinkUrl	string

	// WS URL for long connection (optional, for streaming output)
	WsUrl	string

	wsClient	*internal.WsClient

	// Shared HTTP client for LinkUrl calls (lazy initialized)
	linkHttpClient	*http.Client

	// Browser replay enabled flag
	EnableBrowserReplay	*bool

	// File, command and code handlers
	FileSystem	*filesystem.FileSystem
	Command		*command.Command
	Code		*code.Code
	Oss		*oss.OSSManager

	// Git for version control
	Git	*git.Git

	// Platform-specific automation modules
	Computer	*computer.Computer
	Mobile		*mobile.Mobile

	// Browser for web automation
	Browser	*browser.Browser

	// Agent for task execution
	Agent	*agent.Agent

	Env	*env.Env

	// Context management
	Context	*ContextManager

	// PTY for interactive terminal sessions
	Pty	*pty.Pty
}
```

Session represents a session in the AgentBay cloud environment.

> **⚠️ Note**: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and
MobileUseAgent), we do not provide services for overseas users registered with **alibabacloud.com**.

### Methods

### AppendMcpTool

```go
func (s *Session) AppendMcpTool(name, server string)
```

AppendMcpTool adds an MCP tool entry to the session's tool list.

### BetaPause

```go
func (s *Session) BetaPause(timeout int, pollInterval float64) (*models.SessionPauseResult, error)
```

BetaPause synchronously pauses this session (beta), putting it into a dormant state to reduce
resource usage and costs. BetaPause puts the session into a PAUSED state where computational
resources are significantly reduced. The session state is preserved and can be resumed later to
continue work.

Note: This feature is currently in whitelist-only access. Contact agentbay_dev@alibabacloud.com to
request access.

Parameters:
  - timeout: Timeout in seconds to wait for the session to pause. Defaults to 600 seconds.
  - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.

Returns:
  - *models.SessionPauseResult: Result containing success status, request ID, and error message if
    any.
  - error: Error if the operation fails at the transport level

Behavior:

- Initiates pause operation through the PauseSessionAsync API - Polls session status until PAUSED
state or timeout - Returns detailed result with success status and request tracking

Exceptions:

- Returns error result (not Go error) for API-level errors like invalid session ID - Returns error
result for timeout conditions - Returns Go error for transport-level failures

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
result, _ := client.Create(nil)
defer result.Session.Delete()
pauseResult, _ := result.Session.BetaPause(300, 2.0)
```

### BetaResume

```go
func (s *Session) BetaResume(timeout int, pollInterval float64) (*models.SessionResumeResult, error)
```

BetaResume synchronously resumes this session (beta) from a paused state to continue work.
BetaResume restores the session from PAUSED state back to RUNNING state. All previous session state
and data are preserved during resume operation.

Parameters:
  - timeout: Timeout in seconds to wait for the session to resume. Defaults to 600 seconds.
  - pollInterval: Interval in seconds between status polls. Defaults to 2.0 seconds.

Returns:
  - *models.SessionResumeResult: Result containing success status, request ID, and error message if
    any.
  - error: Error if the operation fails at the transport level

Behavior:

- Initiates resume operation through the ResumeSessionAsync API - Polls session status until RUNNING
state or timeout - Returns detailed result with success status and request tracking

Exceptions:

- Returns error result (not Go error) for API-level errors like invalid session ID - Returns error
result for timeout conditions - Returns Go error for transport-level failures

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
result, _ := client.Create(nil)
defer result.Session.Delete()
result.Session.BetaPause(300, 2.0)
resumeResult, _ := result.Session.BetaResume(300, 2.0)
```

### CallMcpTool

```go
func (s *Session) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error)
```

### Delete

```go
func (s *Session) Delete(syncContext ...bool) (*DeleteResult, error)
```

Delete deletes this session. Delete deletes the session and releases all associated resources.

Parameters:
  - syncContext: Optional boolean to synchronize context data before deletion. If true, uploads all
    context data to OSS. Defaults to false.

Returns:
  - *DeleteResult: Result containing success status and request ID
  - error: Error if the operation fails

Behavior:

- If syncContext is true: Uploads all context data to OSS before deletion - If syncContext is false:
Deletes immediately without sync - Continues with deletion even if context sync fails - Releases all
associated resources (browser, computer, mobile, etc.)

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
deleteResult, _ := result.Session.Delete()
```

### Files

```go
func (s *Session) Files() *filesystem.FileSystem
```

Files returns the FileSystem module (alias of FileSystem).

### Filesystem

```go
func (s *Session) Filesystem() *filesystem.FileSystem
```

Filesystem returns the FileSystem module (alias of FileSystem).

### Fs

```go
func (s *Session) Fs() *filesystem.FileSystem
```

Fs returns the FileSystem module (alias of FileSystem).

### GetBrowser

```go
func (s *Session) GetBrowser() *browser.Browser
```

GetBrowser returns the Browser instance for this session.

### GetEnableBrowserReplay

```go
func (s *Session) GetEnableBrowserReplay() *bool
```

GetEnableBrowserReplay returns whether browser replay is enabled for this session. Returns nil if
not explicitly set (server default applies).

### GetLabels

```go
func (s *Session) GetLabels() (*LabelResult, error)
```

GetLabels gets the labels for this session.

Returns:
  - *LabelResult: Result containing labels as JSON string and request ID
  - error: Error if the operation fails

Behavior:

- Retrieves the labels that were previously set for this session - Returns labels as a JSON string -
Can be used to identify and filter sessions

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
labelResult, _ := result.Session.GetLabels()
```

### GetLink

```go
func (s *Session) GetLink(protocolType *string, port *int32, options *string) (*LinkResult, error)
```

GetLink gets the link for this session. GetLink retrieves an access link for the session.

Parameters:
  - protocolType: Protocol type for the link (optional, reserved for future use)
  - port: Specific port number to access (default open range: [30100, 30199]; other ports require
    whitelist approval via agentbay_dev@alibabacloud.com)
  - options: Additional options (optional)

Returns:
  - *LinkResult: Result containing the access URL and request ID
  - error: Error if port is out of range or operation fails

Behavior:

- Without port: Returns the default session access URL - With port: Returns URL for accessing
specific port-mapped service - Default open port range: [30100, 30199]; other ports require
whitelist approval

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
port := int32(30100)
linkResult, _ := result.Session.GetLink(nil, &port, nil)
```

### GetMcpServerForTool

```go
func (s *Session) GetMcpServerForTool(toolName string) string
```

GetMcpServerForTool returns the MCP server name that provides the given tool.

### GetMetrics

```go
func (s *Session) GetMetrics() (*models.SessionMetricsResult, error)
```

GetMetrics retrieves runtime metrics for this session.

The underlying service returns a JSON string. This method parses it and returns structured metrics.

### GetStatus

```go
func (s *Session) GetStatus() (*SessionStatusResult, error)
```

GetStatus retrieves basic session status for the current session. This method calls the
GetSessionDetail API and returns status only.

### GetStreamingWsClient

```go
func (s *Session) GetStreamingWsClient() (WsStreamingClient, error)
```

GetStreamingWsClient returns a WS streaming client for this session.

### GetWsClient

```go
func (s *Session) GetWsClient() (interface{}, error)
```

### GetWsUrl

```go
func (s *Session) GetWsUrl() string
```

### Info

```go
func (s *Session) Info() (*InfoResult, error)
```

Info gets information about this session. Info retrieves detailed information about the current
session.

Returns:
  - *InfoResult: Result containing SessionInfo object and request ID
  - error: Error if the operation fails or session not found

Behavior:

- Retrieves current session metadata from the backend - Includes resource URL, type, and connection
properties - Information is fetched in real-time from the API

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
infoResult, _ := result.Session.Info()
```

### KeepAlive

```go
func (s *Session) KeepAlive() (*KeepAliveResult, error)
```

KeepAlive refreshes the backend idle timer for this session. It calls the RefreshSessionIdleTime
API.

### ListMcpTools

```go
func (s *Session) ListMcpTools() (*McpToolsResult, error)
```

ListMcpTools lists MCP tools available for this session. It uses the ImageId from the session
creation, or "linux_latest" as default.

Returns:
  - *McpToolsResult: Result containing list of MCP tools and request ID
  - error: Error if the operation fails

Behavior:

- Uses the ImageId from session creation - Defaults to "linux_latest" if ImageId is empty -
Retrieves all available MCP tools for the specified image - Does not store tools on the Session (no
caching)

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
toolsResult, _ := result.Session.ListMcpTools()
```

### LogDebug

```go
func (s *Session) LogDebug(msg string)
```

LogDebug delegates to agentbay.LogDebug (implements agent.McpSessionLogger).

### LogError

```go
func (s *Session) LogError(msg string)
```

LogError delegates to agentbay.LogError (implements agent.McpSessionLogger).

### LogInfo

```go
func (s *Session) LogInfo(msg string)
```

LogInfo delegates to agentbay.LogInfo (implements agent.McpSessionLogger).

### LogWarn

```go
func (s *Session) LogWarn(msg string)
```

LogWarn delegates to agentbay.LogWarn (implements agent.McpSessionLogger).

### SetLabels

```go
func (s *Session) SetLabels(labels map[string]string) (*LabelResult, error)
```

SetLabels sets the labels for this session.

Parameters:
  - labels: Labels to set for the session as a map of key-value pairs

Returns:
  - *LabelResult: Result containing request ID
  - error: Error if validation fails or operation fails

Behavior:

- Validates that labels map is not nil or empty - All keys and values must be non-empty strings
- Converts labels to JSON and sends to the backend - Labels can be used for session filtering and
organization

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
labels := map[string]string{"env": "test"}
labelResult, _ := result.Session.SetLabels(labels)
```

### Related Functions

### NewSession

```go
func NewSession(agentBay *AgentBay, sessionID string) *Session
```

NewSession creates a new Session object.

## Type CreateSessionParams

```go
type CreateSessionParams struct {
	// Labels are custom labels for the Session. These can be used for organizing and filtering sessions.
	Labels	map[string]string

	// ImageId specifies the image ID to use for the session.
	ImageId	string

	// IdleReleaseTimeout specifies the SDK-side idle release timeout in seconds.
	// Default is 300 seconds. Deprecated for new code: use LifecyclePolicy (minutes).
	IdleReleaseTimeout	int32

	// LifecyclePolicy configures idle release and max runtime in minutes, and optional manual release.
	// Mutually exclusive with IdleReleaseTimeout when that field is set (greater than zero).
	LifecyclePolicy	*LifecyclePolicy

	// ContextSync is a list of context synchronization configurations.
	// These configurations define how contexts should be synchronized and mounted.
	ContextSync	[]*ContextSync

	// BetaContextMount is a list of context mount configurations for direct-mount persistence.
	BetaContextMount	[]*BetaContextMount

	// PolicyId specifies the policy ID to apply when creating the session.
	PolicyId	string

	// BetaNetworkId specifies the beta network ID to bind this session to.
	BetaNetworkId	string

	// ExtraConfigs contains extra configuration settings for different session types
	ExtraConfigs	*models.ExtraConfigs

	// Framework specifies the framework name for tracking (e.g., "langchain"). Empty string means direct call.
	Framework	string

	// EnableBrowserReplay specifies whether to enable browser recording for this session.
	// When nil (not set), server-side default behavior applies.
	EnableBrowserReplay	*bool

	// BrowserContext specifies persistent browser context configuration for this session.
	// When set, the session will be bound to the given cloud context and browser state will
	// persist across sessions.
	BrowserContext	*BrowserContext

	// LoadSkills when true, loads skills into the sandbox. Use BetaSkills.GetMetadata() to discover available skills.
	LoadSkills	bool

	// SkillNames filter which skills to load by name. When LoadSkills is true and this is empty, loads all visible skills.
	SkillNames	[]string
}
```

CreateSessionParams provides a way to configure the parameters for creating a new session in the
AgentBay cloud environment.

### Methods

### AddBetaContextMount

```go
func (p *CreateSessionParams) AddBetaContextMount(contextMount *BetaContextMount) *CreateSessionParams
```

AddBetaContextMount adds a context mount configuration to the session parameters.

### AddContextSync

```go
func (p *CreateSessionParams) AddContextSync(contextID, path string, policy *SyncPolicy) *CreateSessionParams
```

AddContextSync adds a context sync configuration to the session parameters.

### AddContextSyncConfig

```go
func (p *CreateSessionParams) AddContextSyncConfig(contextSync *ContextSync) *CreateSessionParams
```

AddContextSyncConfig adds a pre-configured context sync to the session parameters.

### GetExtraConfigsJSON

```go
func (p *CreateSessionParams) GetExtraConfigsJSON() (string, error)
```

GetExtraConfigsJSON returns the extra configs as a JSON string.

### GetLabelsJSON

```go
func (p *CreateSessionParams) GetLabelsJSON() (string, error)
```

GetLabelsJSON returns the labels as a JSON string.

### WithBetaContextMount

```go
func (p *CreateSessionParams) WithBetaContextMount(contextMounts []*BetaContextMount) *CreateSessionParams
```

WithBetaContextMount sets the context mount configurations for the session parameters.

### WithBetaNetworkId

```go
func (p *CreateSessionParams) WithBetaNetworkId(betaNetworkId string) *CreateSessionParams
```

WithBetaNetworkId sets the beta network ID for the session parameters and returns the updated
parameters.

### WithBrowserContext

```go
func (p *CreateSessionParams) WithBrowserContext(browserContext *BrowserContext) *CreateSessionParams
```

WithBrowserContext sets the browser context configuration for the session parameters.

### WithContextSync

```go
func (p *CreateSessionParams) WithContextSync(contextSyncs []*ContextSync) *CreateSessionParams
```

WithContextSync sets the context sync configurations for the session parameters.

### WithEnableBrowserReplay

```go
func (p *CreateSessionParams) WithEnableBrowserReplay(enableBrowserReplay bool) *CreateSessionParams
```

WithEnableBrowserReplay sets the browser replay flag for the session parameters and returns the
updated parameters.

### WithExtraConfigs

```go
func (p *CreateSessionParams) WithExtraConfigs(extraConfigs *models.ExtraConfigs) *CreateSessionParams
```

WithExtraConfigs sets the extra configurations for the session parameters and returns the updated
parameters.

### WithIdleReleaseTimeout

```go
func (p *CreateSessionParams) WithIdleReleaseTimeout(timeoutSeconds int32) *CreateSessionParams
```

WithIdleReleaseTimeout sets the SDK-side idle release timeout in seconds and returns the updated
parameters. Only positive values are accepted.

### WithImageId

```go
func (p *CreateSessionParams) WithImageId(imageId string) *CreateSessionParams
```

WithImageId sets the image ID for the session parameters and returns the updated parameters.

### WithLabels

```go
func (p *CreateSessionParams) WithLabels(labels map[string]string) *CreateSessionParams
```

WithLabels sets the labels for the session parameters and returns the updated parameters.

### WithLifecyclePolicy

```go
func (p *CreateSessionParams) WithLifecyclePolicy(lp *LifecyclePolicy) (*CreateSessionParams, error)
```

WithLifecyclePolicy sets the lifecycle policy (minutes). Mutually exclusive with IdleReleaseTimeout
when IdleReleaseTimeout > 0.

### WithLoadSkills

```go
func (p *CreateSessionParams) WithLoadSkills(loadSkills bool) *CreateSessionParams
```

WithLoadSkills sets whether to load skills into the sandbox.

### WithPolicyId

```go
func (p *CreateSessionParams) WithPolicyId(policyId string) *CreateSessionParams
```

WithPolicyId sets the policy ID for the session parameters and returns the updated parameters.

### WithSkillNames

```go
func (p *CreateSessionParams) WithSkillNames(names []string) *CreateSessionParams
```

WithSkillNames sets the skill names to load. When LoadSkills is true and this is empty, loads all
visible skills.

### Related Functions

### NewCreateSessionParams

```go
func NewCreateSessionParams() *CreateSessionParams
```

NewCreateSessionParams creates a new CreateSessionParams with default values.

## Type SessionResult

```go
type SessionResult struct {
	models.ApiResponse
	Session		*Session
	Success		bool
	ErrorMessage	string
}
```

SessionResult wraps Session object and RequestID

## Type SessionListResult

```go
type SessionListResult struct {
	models.ApiResponse
	SessionIds	[]map[string]interface{}	// Session objects with ID and status
	NextToken	string				// Token for the next page
	MaxResults	int32				// Number of results per page
	TotalCount	int32				// Total number of results
}
```

SessionListResult wraps Session list and RequestID

## Type InfoResult

```go
type InfoResult struct {
	models.ApiResponse
	Info	*SessionInfo
}
```

InfoResult wraps SessionInfo and RequestID

## Type LabelResult

```go
type LabelResult struct {
	models.ApiResponse
	Labels	string
}
```

LabelResult wraps label operation result and RequestID

## Type LinkResult

```go
type LinkResult struct {
	models.ApiResponse
	Link	string
}
```

LinkResult wraps link result and RequestID

## Type DeleteResult

```go
type DeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

DeleteResult wraps deletion operation result and RequestID

## Type McpToolsResult

```go
type McpToolsResult struct {
	models.ApiResponse
	Tools	[]McpTool
}
```

McpToolsResult wraps MCP tools list and RequestID

## Type McpTool

```go
type McpTool struct {
	Name		string			`json:"name"`		// Tool name
	Description	string			`json:"description"`	// Tool description
	InputSchema	map[string]interface{}	`json:"inputSchema"`	// Input parameter schema
	Server		string			`json:"server"`		// Server name that provides this tool
	Tool		string			`json:"tool"`		// Tool identifier
}
```

McpTool represents an MCP tool with complete information

### Methods

### GetName

```go
func (m *McpTool) GetName() string
```

GetName returns the tool name

### GetServer

```go
func (m *McpTool) GetServer() string
```

GetServer returns the server name that provides this tool

## Type SessionInfo

```go
type SessionInfo struct {
	SessionId		string
	ResourceUrl		string
	AppId			string
	AuthCode		string
	ConnectionProperties	string
	ResourceId		string
	ResourceType		string
	Ticket			string
}
```

SessionInfo contains information about a session.

## Functions

### NewSession

```go
func NewSession(agentBay *AgentBay, sessionID string) *Session
```

NewSession creates a new Session object.

### NewCreateSessionParams

```go
func NewCreateSessionParams() *CreateSessionParams
```

NewCreateSessionParams creates a new CreateSessionParams with default values.

## Related Resources

- [FileSystem API Reference](filesystem.md)
- [Command API Reference](command.md)
- [Context API Reference](context.md)
- [Context Manager API Reference](context-manager.md)
- [OSS API Reference](../advanced/oss.md)

---

*Documentation generated automatically from Go source code.*
