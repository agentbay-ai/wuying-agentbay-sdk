# Context Sync API Reference

## 🚀 Related Tutorial

- [First Session Tutorial](../../../../../docs/quickstart/first-session.md) - Get started with creating your first AgentBay session

## Type ContextSync

```go
type ContextSync struct {
	// ContextID is the ID of the context to synchronize
	ContextID	string	`json:"contextId"`
	// Path is the path where the context should be mounted
	Path	string	`json:"path"`
	// Policy defines the synchronization policy
	Policy	*SyncPolicy	`json:"policy,omitempty"`
	// BetaWaitForCompletion controls whether session creation should wait for this context's
	// initial download to finish. If set to false, the SDK will not block Create() on this
	// context. If nil, it defaults to waiting (backward compatible).
	BetaWaitForCompletion	*bool	`json:"-"`
}
```

ContextSync defines the context synchronization configuration

### Methods

### WithBetaWaitForCompletion

```go
func (cs *ContextSync) WithBetaWaitForCompletion(wait bool) *ContextSync
```

WithBetaWaitForCompletion sets BetaWaitForCompletion for chaining.

### WithPolicy

```go
func (cs *ContextSync) WithPolicy(policy *SyncPolicy) (*ContextSync, error)
```

WithPolicy sets the policy and returns the context sync for chaining

### Related Functions

### NewContextSync

```go
func NewContextSync(contextID, path string, policy *SyncPolicy) (*ContextSync, error)
```

NewContextSync creates a new context sync configuration

## Type SyncPolicy

```go
type SyncPolicy struct {
	// UploadPolicy defines the upload policy
	UploadPolicy	*UploadPolicy	`json:"uploadPolicy,omitempty"`
	// DownloadPolicy defines the download policy
	DownloadPolicy	*DownloadPolicy	`json:"downloadPolicy,omitempty"`
	// DeletePolicy defines the delete policy
	DeletePolicy	*DeletePolicy	`json:"deletePolicy,omitempty"`
	// ExtractPolicy defines the extract policy
	ExtractPolicy	*ExtractPolicy	`json:"extractPolicy,omitempty"`
	// RecyclePolicy defines the recycle policy
	RecyclePolicy	*RecyclePolicy	`json:"recyclePolicy,omitempty"`
	// BWList defines the black and white list
	BWList	*BWList	`json:"bwList,omitempty"`
	// MappingPolicy defines the mapping policy for cross-platform context synchronization
	MappingPolicy	*MappingPolicy	`json:"mappingPolicy,omitempty"`
}
```

SyncPolicy defines the synchronization policy

### Related Functions

### NewSyncPolicy

```go
func NewSyncPolicy() *SyncPolicy
```

NewSyncPolicy creates a new sync policy with default values

## Type UploadPolicy

```go
type UploadPolicy struct {
	// AutoUpload enables automatic upload
	AutoUpload	bool	`json:"autoUpload"`
	// UploadStrategy defines the upload strategy
	UploadStrategy	UploadStrategy	`json:"uploadStrategy"`
	// UploadMode defines the upload mode
	UploadMode	UploadMode	`json:"uploadMode"`
}
```

UploadPolicy defines the upload policy for context synchronization

### Related Functions

### NewUploadPolicy

```go
func NewUploadPolicy() *UploadPolicy
```

NewUploadPolicy creates a new upload policy with default values

## Type DownloadPolicy

```go
type DownloadPolicy struct {
	// AutoDownload enables automatic download
	AutoDownload	bool	`json:"autoDownload"`
	// DownloadStrategy defines the download strategy
	DownloadStrategy	DownloadStrategy	`json:"downloadStrategy"`
}
```

DownloadPolicy defines the download policy for context synchronization

### Related Functions

### NewDownloadPolicy

```go
func NewDownloadPolicy() *DownloadPolicy
```

NewDownloadPolicy creates a new download policy with default values

## Type DeletePolicy

```go
type DeletePolicy struct {
	// SyncLocalFile enables synchronization of local file deletions
	SyncLocalFile bool `json:"syncLocalFile"`
}
```

DeletePolicy defines the delete policy for context synchronization

### Related Functions

### NewDeletePolicy

```go
func NewDeletePolicy() *DeletePolicy
```

NewDeletePolicy creates a new delete policy with default values

## Type ExtractPolicy

```go
type ExtractPolicy struct {
	// Extract enables file extraction
	Extract	bool	`json:"extract"`
	// DeleteSrcFile enables deletion of source file after extraction
	DeleteSrcFile	bool	`json:"deleteSrcFile"`
	// ExtractToCurrentFolder enables extraction to current folder
	ExtractToCurrentFolder	bool	`json:"extractToCurrentFolder"`
}
```

ExtractPolicy defines the extract policy for context synchronization

### Related Functions

### NewExtractPolicy

```go
func NewExtractPolicy() *ExtractPolicy
```

NewExtractPolicy creates a new extract policy with default values

## Type RecyclePolicy

```go
type RecyclePolicy struct {
	// Lifecycle defines how long the context data should be retained
	Lifecycle	Lifecycle	`json:"lifecycle"`
	// Paths specifies which directories or files should be subject to the recycle policy
	Paths	[]string	`json:"paths"`
}
```

RecyclePolicy defines the recycle policy for context synchronization

The RecyclePolicy determines how long context data should be retained and which paths are subject to
the policy.

Lifecycle field determines the data retention period:
  - Lifecycle1Day: Keep data for 1 day
  - Lifecycle3Days: Keep data for 3 days
  - Lifecycle5Days: Keep data for 5 days
  - Lifecycle10Days: Keep data for 10 days
  - Lifecycle15Days: Keep data for 15 days
  - Lifecycle30Days: Keep data for 30 days
  - Lifecycle90Days: Keep data for 90 days
  - Lifecycle180Days: Keep data for 180 days
  - Lifecycle360Days: Keep data for 360 days
  - LifecycleForever: Keep data permanently (default)

Paths field specifies which directories or files should be subject to the recycle policy:
  - Must use exact directory/file paths
  - Wildcard patterns (* ? [ ]) are NOT supported
  - Empty string "" means apply to all paths in the context
  - Multiple paths can be specified as a slice
  - Default: []string{""} (applies to all paths)

### Related Functions

### NewRecyclePolicy

```go
func NewRecyclePolicy() *RecyclePolicy
```

NewRecyclePolicy creates a new recycle policy with default values

## Type WhiteList

```go
type WhiteList struct {
	// Path is the path to include in the white list
	Path	string	`json:"path"`
	// ExcludePaths are the paths to exclude from the white list
	ExcludePaths	[]string	`json:"excludePaths,omitempty"`
	// IsPathRegex indicates whether Path is a regex pattern (default: false)
	IsPathRegex	bool	`json:"isPathRegex"`
	// IsExcludeRegex indicates whether ExcludePaths entries are regex patterns (default: false)
	IsExcludeRegex	bool	`json:"isExcludeRegex"`
}
```

WhiteList defines the white list configuration

When IsPathRegex is false (default), Path must be an exact absolute directory path and wildcard
characters (* ? [ ]) are not allowed. When IsPathRegex is true, Path is treated as a regex pattern
(e.g. "/home/wuying/.*").

When IsExcludeRegex is false (default), ExcludePaths entries must be exact paths and wildcard
characters are not allowed. When IsExcludeRegex is true, ExcludePaths entries are treated as regex
patterns.

## Type BWList

```go
type BWList struct {
	// WhiteLists defines the white lists
	WhiteLists []*WhiteList `json:"whiteLists,omitempty"`
}
```

BWList defines the black and white list configuration

## Type MappingPolicy

```go
type MappingPolicy struct {
	// Path is the original path from a different OS that should be mapped to the current context path
	Path string `json:"path"`
}
```

MappingPolicy defines the mapping policy for cross-platform context synchronization

### Related Functions

### NewMappingPolicy

```go
func NewMappingPolicy() *MappingPolicy
```

NewMappingPolicy creates a new mapping policy with default values

## Type UploadStrategy

```go
type UploadStrategy string
```

UploadStrategy defines the upload strategy for context synchronization

## Type DownloadStrategy

```go
type DownloadStrategy string
```

DownloadStrategy defines the download strategy for context synchronization

## Type UploadMode

```go
type UploadMode string
```

UploadMode defines the upload mode for context synchronization

## Type Lifecycle

```go
type Lifecycle string
```

Lifecycle defines the lifecycle options for recycle policy

## Functions

### NewContextSync

```go
func NewContextSync(contextID, path string, policy *SyncPolicy) (*ContextSync, error)
```

NewContextSync creates a new context sync configuration

### NewSyncPolicy

```go
func NewSyncPolicy() *SyncPolicy
```

NewSyncPolicy creates a new sync policy with default values

### NewUploadPolicy

```go
func NewUploadPolicy() *UploadPolicy
```

NewUploadPolicy creates a new upload policy with default values

### NewDownloadPolicy

```go
func NewDownloadPolicy() *DownloadPolicy
```

NewDownloadPolicy creates a new download policy with default values

### NewDeletePolicy

```go
func NewDeletePolicy() *DeletePolicy
```

NewDeletePolicy creates a new delete policy with default values

### NewExtractPolicy

```go
func NewExtractPolicy() *ExtractPolicy
```

NewExtractPolicy creates a new extract policy with default values

### NewRecyclePolicy

```go
func NewRecyclePolicy() *RecyclePolicy
```

NewRecyclePolicy creates a new recycle policy with default values

### NewMappingPolicy

```go
func NewMappingPolicy() *MappingPolicy
```

NewMappingPolicy creates a new mapping policy with default values

## Related Resources

- [Session API Reference](session.md)
- [Context API Reference](context.md)

---

*Documentation generated automatically from Go source code.*
