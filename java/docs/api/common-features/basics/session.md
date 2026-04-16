# 🔧 Session API Reference

## Overview

The Session class represents an active cloud environment instance in AgentBay. It provides access to all service modules (filesystem, command, browser, code, etc.) and manages the lifecycle of the cloud environment.


## 📚 Tutorial

[Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md)

Detailed tutorial on session lifecycle and management

## Session

### Constructor

```java
public Session(AgentBay agentBay, String sessionId)
```

Creates a new Session instance.

<p>Initializes all service instances (Agent, FileSystem, OSS, Code, Command, 
ContextManager, Browser, Computer, Mobile) for this session.</p>

**Parameters:**
- `agentBay` (AgentBay): The AgentBay client instance
- `sessionId` (String): The unique identifier for this session

```java
public Session(String sessionId, AgentBay agentBay)
```

Creates a new Session instance with alternative parameter order.

<p>This constructor provides backward compatibility for code that uses
the (String, AgentBay) parameter order.</p>

**Parameters:**
- `sessionId` (String): The unique identifier for this session
- `agentBay` (AgentBay): The AgentBay client instance

### Methods

### getAppInstanceId

```java
public String getAppInstanceId()
```

Get the application instance ID.

**Returns:**
- `String`: The application instance ID

### setAppInstanceId

```java
public void setAppInstanceId(String appInstanceId)
```

Set the application instance ID.

**Parameters:**
- `appInstanceId` (String): The application instance ID

### getWsUrl

```java
public String getWsUrl()
```

### setWsUrl

```java
public void setWsUrl(String wsUrl)
```

### getSessionId

```java
public String getSessionId()
```

Get the session ID.

**Returns:**
- `String`: The unique identifier for this session

### getGit

```java
public Git getGit()
```

Get the Git service for this session.

**Returns:**
- `Git`: The Git service instance

### getPty

```java
public Pty getPty()
```

### keepAlive

```java
public OperationResult keepAlive()
```

Refresh the backend idle timer for this session.

<p>This method calls the RefreshSessionIdleTime API to prevent the session
from being automatically terminated due to inactivity.</p>

**Returns:**
- `OperationResult`: OperationResult containing request ID and success status

### getAgentBay

```java
public AgentBay getAgentBay()
```

Get the AgentBay client.

**Returns:**
- `AgentBay`: The AgentBay client instance associated with this session

### getAgent

```java
public Agent getAgent()
```

Get the agent for this session.

**Returns:**
- `Agent`: The Agent instance for AI-powered automation

### getFileSystem

```java
public FileSystem getFileSystem()
```

Get the file system for this session.

**Returns:**
- `FileSystem`: The FileSystem instance for file operations

### fs

```java
public FileSystem fs()
```

Alias for fileSystem.

<p>Provides a shorthand way to access the file system service.</p>

**Returns:**
- `FileSystem`: The FileSystem instance

### getFilesystem

```java
public FileSystem getFilesystem()
```

Alias for fileSystem.

<p>Provides an alternative way to access the file system service.</p>

**Returns:**
- `FileSystem`: The FileSystem instance

### getFiles

```java
public FileSystem getFiles()
```

Alias for fileSystem.

<p>Provides a shorthand way to access the file system service.</p>

**Returns:**
- `FileSystem`: The FileSystem instance

### getMetrics

```java
public SessionMetricsResult getMetrics()
```

Get runtime metrics for this session via the MCP get_metrics tool.

The underlying MCP tool returns a JSON string. This method parses it and returns structured metrics.

**Returns:**
- `SessionMetricsResult`: SessionMetricsResult containing structured metrics data

### info

```java
public SessionInfoResult info() throws AgentBayException
```

Gets information about this session

**Returns:**
- `SessionInfoResult`: SessionInfoResult containing SessionInfo and request ID

**Throws:**
- `AgentBayException`: if the operation fails

### getOss

```java
public OSS getOss()
```

Get the OSS service for this session

**Returns:**
- `OSS`: OSS instance

### getCode

```java
public Code getCode()
```

Get the Code service for this session

**Returns:**
- `Code`: Code instance

### getCommand

```java
public Command getCommand()
```

Get the Command service for this session

**Returns:**
- `Command`: Command instance

### getContext

```java
public ContextManager getContext()
```

Get the context manager for this session

**Returns:**
- `ContextManager`: ContextManager instance

### getBrowser

```java
public Browser getBrowser()
```

Get the browser service for this session

**Returns:**
- `Browser`: Browser instance

### getComputer

```java
public Computer getComputer()
```

Get the computer service for this session

**Returns:**
- `Computer`: Computer instance

### getMobile

```java
public Mobile getMobile()
```

Get the mobile service for this session

**Returns:**
- `Mobile`: Mobile instance

### getEnv

```java
public Env getEnv()
```

Get the environment variable service for this session

**Returns:**
- `Env`: Env instance

### getFileTransferContextId

```java
public String getFileTransferContextId()
```

Get the file transfer context ID for this session

**Returns:**
- `String`: File transfer context ID

### setFileTransferContextId

```java
public void setFileTransferContextId(String fileTransferContextId)
```

Set the file transfer context ID for this session

**Parameters:**
- `fileTransferContextId` (String): File transfer context ID

### getApiKey

```java
public String getApiKey()
```

Get the API key for this session

**Returns:**
- `String`: API key

### listMcpTools

```java
public McpToolsResult listMcpTools()
```

Lists all available MCP tools for this session.

This method retrieves the list of MCP tools that can be called in this session,including their names, descriptions, input schemas, and server information.

**Returns:**
- `McpToolsResult`: McpToolsResult containing the list of available tools

### setImageId

```java
public void setImageId(String imageId)
```

Sets the image ID for this session.
This is used to specify the base image for the session environment.

**Parameters:**
- `imageId` (String): The image ID to set

### getImageId

```java
public String getImageId()
```

Gets the image ID for this session.

**Returns:**
- `String`: The image ID, or empty string if not set

### getEnableBrowserReplay

```java
public Boolean getEnableBrowserReplay()
```

Gets the enableBrowserReplay flag.
This flag determines whether browser recording is enabled for this session.

**Returns:**
- `Boolean`: true if browser replay is enabled, false otherwise

### setEnableBrowserReplay

```java
public void setEnableBrowserReplay(Boolean enableBrowserReplay)
```

Sets the enableBrowserReplay flag.
This flag determines whether browser recording is enabled for this session.

**Parameters:**
- `enableBrowserReplay` (Boolean): true to enable browser replay, false to disable

### getResourceUrl

```java
public String getResourceUrl()
```

Get the resource URL for accessing the session

**Returns:**
- `String`: Resource URL

### setResourceUrl

```java
public void setResourceUrl(String resourceUrl)
```

Set the resource URL for accessing the session

**Parameters:**
- `resourceUrl` (String): Resource URL

### getToken

```java
public String getToken()
```

### setToken

```java
public void setToken(String token)
```

Sets the token for LinkUrl tool calls.
This token is used for authentication when calling MCP tools via the LinkUrl route.

**Parameters:**
- `token` (String): The authentication token to set

### getLinkUrl

```java
public String getLinkUrl()
```

### setLinkUrl

```java
public void setLinkUrl(String linkUrl)
```

Sets the LinkUrl for direct tool calls.
This URL is used for calling MCP tools via the LinkUrl route in VPC environments.

**Parameters:**
- `linkUrl` (String): The LinkUrl to set

### getMcpTools

```java
public List<McpTool> getMcpTools()
```

Gets the list of MCP tools available for this session.

**Returns:**
- `List<McpTool>`: List of McpTool instances

### setMcpTools

```java
public void setMcpTools(List<McpTool> mcpTools)
```

Sets the list of MCP tools for this session.

**Parameters:**
- `mcpTools` (List<McpTool>): The list of McpTool instances to set

### getMcpServerForTool

```java
public String getMcpServerForTool(String toolName)
```

Gets the MCP server name for a specific tool.

This method searches through the available MCP tools to find the server that provides the specified tool.

**Parameters:**
- `toolName` (String): The name of the tool to look up

**Returns:**
- `String`: The server name, or empty string if not found

### getLink

```java
public OperationResult getLink(String protocolType, Integer port) throws AgentBayException
```

```java
public OperationResult getLink() throws AgentBayException
```

Gets a connection link for the current session with specified parameters.

This method generates a connection URL that can be used to access the session via the specified protocol and port.

**Parameters:**
- `protocolType` (String): The protocol type to use for the link (e.g., "https")
- `port` (Integer): The port number to use for the connection (default open range: [30100, 30199]; other ports require whitelist approval via agentbay_dev@alibabacloud.com)

**Returns:**
- `OperationResult`: OperationResult containing the connection link URL

**Throws:**
- `AgentBayException`: if the request fails

### delete

```java
public DeleteResult delete()
```

```java
public DeleteResult delete(boolean syncContext)
```

Deletes this session with optional context synchronization.

<p>This method uses the DeleteSessionAsync API to release cloud resources.
If syncContext is true, it will first synchronize the context (trigger file uploads)
before deleting the session. After initiating deletion, it polls the session status
until the session is confirmed deleted (NotFound or FINISH) or timeout.</p>

**Parameters:**
- `syncContext` (boolean): Whether to synchronize context before deletion

**Returns:**
- `DeleteResult`: DeleteResult containing the deletion result

### setLabels

```java
public OperationResult setLabels(Map<String, String> labels) throws AgentBayException
```

Sets labels for this session.

Labels are key-value pairs that can be used to organize and filter sessions.
All keys and values must be non-empty strings.

**Parameters:**
- `labels` (Map<String,String>): Map of label key-value pairs to set

**Returns:**
- `OperationResult`: OperationResult indicating success or failure

**Throws:**
- `AgentBayException`: if the API call fails or validation fails
- `IllegalArgumentException`: if labels are null or contain invalid keys/values

### getLabels

```java
public OperationResult getLabels() throws AgentBayException
```

Gets the labels for this session.

This method retrieves all labels that have been set for this session.

**Returns:**
- `OperationResult`: OperationResult containing the labels map as JSON string in the data field

**Throws:**
- `AgentBayException`: if the API call fails

### betaPause

```java
public SessionPauseResult betaPause(int timeout, double pollInterval) throws AgentBayException
```

```java
public SessionPauseResult betaPause() throws AgentBayException
```

Pauses this session (beta feature).

This method sends a pause request to the backend and polls the session status
until it reaches the PAUSED state or times out.

**Parameters:**
- `timeout` (int): Maximum time to wait for pause completion in seconds (default: 600)
- `pollInterval` (double): Interval between status checks in seconds (default: 2.0)

**Returns:**
- `SessionPauseResult`: SessionPauseResult containing the pause operation result

**Throws:**
- `AgentBayException`: if the API call fails

### betaResume

```java
public SessionResumeResult betaResume(int timeout, double pollInterval) throws AgentBayException
```

```java
public SessionResumeResult betaResume() throws AgentBayException
```

Resumes this session and waits until it enters RUNNING state (beta feature).

This method sends a resume request to the backend and polls the session status
until it reaches the RUNNING state or the timeout is exceeded.

**Parameters:**
- `timeout` (int): Maximum time to wait in seconds (must be > 0, default 600)
- `pollInterval` (double): Time between status checks in seconds (must be > 0, default 2.0)

**Returns:**
- `SessionResumeResult`: SessionResumeResult containing the resume operation result

**Throws:**
- `AgentBayException`: if the API call fails



## 🔗 Related Resources

- [FileSystem API Reference](../../../api/common-features/basics/filesystem.md)
- [Command API Reference](../../../api/common-features/basics/command.md)
- [Context API Reference](../../../api/common-features/basics/context.md)
- [Context Manager API Reference](../../../api/common-features/basics/context-manager.md)
- [OSS API Reference](../../../api/common-features/advanced/oss.md)

