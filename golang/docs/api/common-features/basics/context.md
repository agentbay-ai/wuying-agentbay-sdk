# Context API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type Context

```go
type Context struct {
	// ID is the unique identifier of the context.
	ID	string

	// Name is the name of the context.
	Name	string

	// CreatedAt is the date and time when the Context was created.
	CreatedAt	string

	// LastUsedAt is the date and time when the Context was last used.
	LastUsedAt	string
}
```

Context represents a persistent storage context in the AgentBay cloud environment.

## Type ContextResult

```go
type ContextResult struct {
	models.ApiResponse
	Success		bool
	ContextID	string
	Context		*Context
	ErrorMessage	string
}
```

ContextResult wraps context operation result and RequestID

## Type ContextListResult

```go
type ContextListResult struct {
	models.ApiResponse
	Success		bool
	Contexts	[]*Context
	NextToken	string
	MaxResults	int32
	TotalCount	int32
	ErrorMessage	string
}
```

ContextListResult wraps context list and RequestID

## Type ContextCreateResult

```go
type ContextCreateResult struct {
	models.ApiResponse
	ContextID	string
}
```

ContextCreateResult wraps context creation result and RequestID

## Type ContextModifyResult

```go
type ContextModifyResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextModifyResult wraps context modification result and RequestID

## Type ContextDeleteResult

```go
type ContextDeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextDeleteResult wraps context deletion result and RequestID

## Type ContextClearResult

```go
type ContextClearResult struct {
	models.ApiResponse
	Success		bool
	Status		string	// Current status of the clearing task ("clearing", "available", etc.)
	ContextID	string
	ErrorMessage	string
}
```

ContextClearResult wraps context clear operation result and RequestID

## Type ContextService

```go
type ContextService struct {
	// AgentBay is the AgentBay instance.
	AgentBay *AgentBay
}
```

ContextService provides methods to manage persistent contexts in the AgentBay cloud environment.

### Methods

### Clear

```go
func (cs *ContextService) Clear(contextID string, timeoutSeconds int, pollIntervalSeconds float64) (*ContextClearResult, error)
```

Clear synchronously clears the context's persistent data and waits for the final result. This method
wraps the ClearAsync and GetClearStatus polling logic.

The clearing process transitions through the following states: - "clearing": Data clearing is in
progress - "available": Clearing completed successfully (final success state)

Parameters:
  - contextID: Unique ID of the context to clear
  - timeout: Timeout in seconds to wait for task completion (default: 60)
  - pollInterval: Interval in seconds between status polls (default: 2)

Returns a ContextClearResult object containing the final task result. The status field will be
"available" on success, or other states if interrupted.

### ClearAsync

```go
func (cs *ContextService) ClearAsync(contextID string) (*ContextClearResult, error)
```

ClearAsync asynchronously initiates a task to clear the context's persistent data. This is a
non-blocking method that returns immediately after initiating the clearing task. The context's state
will transition to "clearing" while the operation is in progress.

Parameters:
  - contextID: Unique ID of the context to clear

Returns:
  - *ContextClearResult: Result containing task status and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
clearResult, _ := client.Context.ClearAsync(contextResult.ContextID)
```

### Create

```go
func (cs *ContextService) Create(name string) (*ContextCreateResult, error)
```

Create creates a new context with the given name.

Parameters:
  - name: The name for the new context.

Returns:
  - *ContextCreateResult: A result object containing the created context ID and request ID.
  - error: An error if the operation fails.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
createResult, _ := client.Context.Create("my-context")
```

### Delete

```go
func (cs *ContextService) Delete(context *Context) (*ContextDeleteResult, error)
```

Delete deletes the specified context.

Parameters:
  - context: The context object to delete

Returns:
  - *ContextDeleteResult: Result containing success status and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
client.Context.Delete(contextResult.Context)
```

### DeleteFile

```go
func (cs *ContextService) DeleteFile(contextID string, filePath string) (*ContextFileDeleteResult, error)
```

DeleteFile deletes a file in a context.

Parameters:
  - contextID: The ID of the context
  - filePath: The path to the file to delete

Returns:
  - *ContextFileDeleteResult: Result containing success status and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
client.Context.DeleteFile(contextResult.ContextID, "/data/file.txt")
```

### Get

```go
func (cs *ContextService) Get(name string, create bool) (*ContextResult, error)
```

Get gets a context by name. Optionally creates it if it doesn't exist. Get retrieves an existing
context or creates a new one.

Parameters:
  - name: The name of the context to retrieve or create
  - create: If true, creates the context if it doesn't exist

Returns:
  - *ContextResult: Result containing Context object and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
```

### GetClearStatus

```go
func (cs *ContextService) GetClearStatus(contextID string) (*ContextClearResult, error)
```

GetClearStatus queries the status of the clearing task. This method calls GetContext API directly
with contextID and parses the raw response to extract the state field, which indicates the current
clearing status.

Parameters:
  - contextID: Unique ID of the context to check

Returns:
  - *ContextClearResult: Result containing current task status and request ID
  - error: Error if the operation fails

State Transitions:
  - "clearing": Data clearing is in progress
  - "available": Clearing completed successfully (final success state)
  - "in-use": Context is being used
  - "pre-available": Context is being prepared

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
statusResult, _ := client.Context.GetClearStatus(contextResult.ContextID)
```

### GetFileDownloadUrl

```go
func (cs *ContextService) GetFileDownloadUrl(contextID string, filePath string) (*ContextFileUrlResult, error)
```

GetFileDownloadUrl gets a presigned download URL for a file in a context.

Note: The presigned URL expires in 1 hour by default.

Parameters:
  - contextID: The ID of the context
  - filePath: The path to the file in the context

Returns:
  - *ContextFileUrlResult: Result containing the presigned URL, expire time, and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
urlResult, _ := client.Context.GetFileDownloadUrl(contextResult.ContextID, "/data/file.txt")
```

### GetFileUploadUrl

```go
func (cs *ContextService) GetFileUploadUrl(contextID string, filePath string) (*ContextFileUrlResult, error)
```

GetFileUploadUrl gets a presigned upload URL for a file in a context.

Note: The presigned URL expires in 1 hour by default.

Parameters:
  - contextID: The ID of the context
  - filePath: The path to the file in the context

Returns:
  - *ContextFileUrlResult: Result containing the presigned URL, expire time, and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
urlResult, _ := client.Context.GetFileUploadUrl(contextResult.ContextID, "/data/file.txt")
```

### List

```go
func (cs *ContextService) List(params *ContextListParams) (*ContextListResult, error)
```

List lists all available contexts with pagination support.

Parameters:
  - params: *ContextListParams (optional) - Pagination parameters. If nil, default values are used
    (MaxResults=10).

Returns:
  - *ContextListResult: A result object containing the list of Context objects, pagination info,
    and RequestID.
  - error: An error if the operation fails.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Context.List(nil)
```

### ListFiles

```go
func (cs *ContextService) ListFiles(contextID string, parentFolderPath string, pageNumber int32, pageSize int32) (*ContextFileListResult, error)
```

ListFiles lists files under a specific folder path in a context using PageNumber/PageSize
pagination.

Parameters:
  - contextID: The ID of the context
  - parentFolderPath: The parent folder path to list files from
  - pageNumber: The page number for pagination
  - pageSize: The number of items per page

Returns:
  - *ContextFileListResult: Result containing the list of files and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
fileList, _ := client.Context.ListFiles(contextResult.ContextID, "/", 1, 10)
```

### ListFilesWithPagination

```go
func (cs *ContextService) ListFilesWithPagination(contextID string, parentFolderPath string, maxResults *int32, nextToken *string) (*ContextFileListResult, error)
```

ListFilesWithPagination lists files using MaxResults/NextToken pagination (token mode). Set
maxResults and/or a non-empty nextToken (pass a non-nil pointer to a non-empty string). When using
this method, PageNumber/PageSize are omitted on the API request, matching the pop API contract.

### Update

```go
func (cs *ContextService) Update(context *Context) (*ContextModifyResult, error)
```

Update updates the specified context. Returns a result with success status. Update modifies an
existing context's properties.

Parameters:
  - context: Context object with updated properties

Returns:
  - *ContextModifyResult: Result containing success status and request ID
  - error: Error if the operation fails

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
contextResult, _ := client.Context.Get("my-context", true)
contextResult.Context.Name = "new-name"
client.Context.Update(contextResult.Context)
```

## Type ContextListParams

```go
type ContextListParams struct {
	MaxResults	int32	// Number of results per page
	NextToken	string	// Token for the next page
	SessionId	string	// Optional session id filter
}
```

ContextListParams contains parameters for listing contexts

### Related Functions

### NewContextListParams

```go
func NewContextListParams() *ContextListParams
```

NewContextListParams creates a new ContextListParams with default values

## Type ContextFileUrlResult

```go
type ContextFileUrlResult struct {
	models.ApiResponse
	Success		bool
	Url		string
	ExpireTime	*int64
	ErrorMessage	string
}
```

ContextFileUrlResult represents a presigned URL operation result.

## Type ContextFileEntry

```go
type ContextFileEntry struct {
	FileID		string
	FileName	string
	FilePath	string
	FileType	string
	GmtCreate	string
	GmtModified	string
	Size		int64
	Status		string
}
```

ContextFileEntry represents a file item in a context.

## Type ContextFileListResult

```go
type ContextFileListResult struct {
	models.ApiResponse
	Success		bool
	Entries		[]*ContextFileEntry
	Count		*int32
	NextToken	string
	MaxResults	*int32
	ErrorMessage	string
}
```

ContextFileListResult represents the result of listing files under a context path.

## Type ContextFileDeleteResult

```go
type ContextFileDeleteResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextFileDeleteResult represents the result of deleting a file in a context.

## Functions

### NewContextListParams

```go
func NewContextListParams() *ContextListParams
```

NewContextListParams creates a new ContextListParams with default values

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
