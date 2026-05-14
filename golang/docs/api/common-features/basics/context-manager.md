# Context Manager API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type ContextStatusData

```go
type ContextStatusData struct {
	ContextId	string	`json:"contextId"`
	Path		string	`json:"path"`
	ErrorMessage	string	`json:"errorMessage"`
	Status		string	`json:"status"`
	StartTime	int64	`json:"startTime"`
	FinishTime	int64	`json:"finishTime"`
	TaskType	string	`json:"taskType"`
}
```

ContextStatusData represents the parsed context status data

## Type ContextStatusItem

```go
type ContextStatusItem struct {
	Type	string	`json:"type"`
	Data	string	`json:"data"`
}
```

ContextStatusItem represents an item in the context status response

## Type ContextInfoResult

```go
type ContextInfoResult struct {
	models.ApiResponse
	Success			bool
	ContextStatusData	[]ContextStatusData	// Parsed context status data
	ErrorMessage		string
}
```

ContextInfoResult wraps context info result and RequestID

## Type ContextSyncResult

```go
type ContextSyncResult struct {
	models.ApiResponse
	Success		bool
	ErrorMessage	string
}
```

ContextSyncResult wraps context sync result and RequestID

## Type ContextManager

```go
type ContextManager struct {
	Session interface {
		GetAPIKey() string
		GetClient() *mcp.Client
		GetSessionId() string
	}
}
```

ContextManager handles context operations for a specific session.

### Methods

### Bind

```go
func (cm *ContextManager) Bind(contexts []*ContextSync, waitForCompletion bool) (*ContextBindResult, error)
```

Bind dynamically binds one or more contexts to the current session.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
result, _ := client.Create(nil)
session := result.Session
contextSync, _ := agentbay.NewContextSync(contextID, "/tmp/ctx-data", nil)
bindResult, _ := session.Context.Bind([]*ContextSync{contextSync}, true)
```

### Info

```go
func (cm *ContextManager) Info() (*ContextInfoResult, error)
```

Info retrieves context information for the current session.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
info, _ := result.Session.Context.Info()
```

### InfoWithParams

```go
func (cm *ContextManager) InfoWithParams(contextId, path, taskType string) (*ContextInfoResult, error)
```

InfoWithParams retrieves context information for the current session with optional parameters.

### ListBindings

```go
func (cm *ContextManager) ListBindings() (*ContextBindingsResult, error)
```

ListBindings lists all context bindings for the current session.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
result, _ := client.Create(nil)
session := result.Session
bindingsResult, _ := session.Context.ListBindings()
for _, b := range bindingsResult.Bindings {
    fmt.Printf("Context %s at %s\n", b.ContextID, b.Path)
}
```

### Mount

```go
func (cm *ContextManager) Mount(contexts []*ContextMount, waitForCompletion bool) (*ContextBindResult, error)
```

Mount dynamically mounts one or more contexts to the current session with write-through persistence.
Unlike Bind which uses sync-based persistence, Mount provides direct-mount persistence where data is
persisted immediately without manual sync calls.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"))
result, _ := client.Create(nil)
session := result.Session
mount := agentbay.NewContextMount(contextID, "/mnt/data")
mountResult, _ := session.Context.Mount([]*ContextMount{mount}, true)
```

### Sync

```go
func (cm *ContextManager) Sync() (*ContextSyncResult, error)
```

Sync synchronizes the context for the current session.

### SyncWithCallback

```go
func (cm *ContextManager) SyncWithCallback(contextId, path, mode string, callback SyncCallback, maxRetries int, retryInterval int) (*ContextSyncResult, error)
```

SyncWithCallback synchronizes the context with callback support (dual-mode). If callback is
provided, it runs in background and calls callback when complete. If callback is nil, it waits for
completion before returning.

Example (Synchronous mode - waits for completion):


package main

import (

	"fmt"

	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)

func main() {

	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	result, err := client.Create(nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	session := result.Session


	// Get or create a context

	contextResult, err := client.Context.Get("my-context", true)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}


	// Synchronous mode: callback is nil, so it waits for completion

	syncResult, err := session.Context.SyncWithCallback(

		contextResult.ContextID,

		"/mnt/persistent",

		"upload",

		nil,  // No callback - synchronous mode

		10,   // maxRetries

		1000, // retryInterval in milliseconds

	)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	fmt.Printf("Sync completed - Success: %v\n", syncResult.Success)


	// Output: No sync tasks found

	// Output: Sync completed - Success: true


	session.Delete()

}

Example (Asynchronous mode - with callback):


package main

import (

	"fmt"

	"os"

	"time"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

)

func main() {

	client, err := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	result, err := client.Create(nil)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	session := result.Session


	// Get or create a context

	contextResult, err := client.Context.Get("my-context", true)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}


	// Asynchronous mode: with callback, returns immediately

	syncResult, err := session.Context.SyncWithCallback(

		contextResult.ContextID,

		"/mnt/persistent",

		"upload",

		func(success bool) {

			if success {

				fmt.Println("Context sync completed successfully")

			} else {

				fmt.Println("Context sync failed or timed out")

			}

		},

		150,  // maxRetries

		500, // retryInterval in milliseconds (initial interval for exponential backoff)

	)

	if err != nil {

		fmt.Printf("Error: %v\n", err)

		os.Exit(1)

	}

	fmt.Printf("Sync triggered - Success: %v\n", syncResult.Success)


	// Wait for callback to complete

	time.Sleep(5 * time.Second)


	// Output: Sync triggered - Success: true

	// Output: Context sync completed successfully


	session.Delete()

}

### SyncWithParams

```go
func (cm *ContextManager) SyncWithParams(contextId, path, mode string) (*ContextSyncResult, error)
```

SyncWithParams synchronizes the context for the current session with optional parameters.

**Example:**

```go
client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
result, _ := client.Create(nil)
defer result.Session.Delete()
session := result.Session
_, _ = session.Context.SyncWithCallback(
	"project-data",
	"/mnt/shared",
	"upload",
	func(success bool, message string) {
		fmt.Printf("Sync callback -> success: %v message: %s\n", success, message)
	},
	20,
	500,
)
```

### Related Functions

### NewContextManager

```go
func NewContextManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *ContextManager
```

NewContextManager creates a new ContextManager object.

## Functions

### NewContextManager

```go
func NewContextManager(session interface {
	GetAPIKey() string
	GetClient() *mcp.Client
	GetSessionId() string
}) *ContextManager
```

NewContextManager creates a new ContextManager object.

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
