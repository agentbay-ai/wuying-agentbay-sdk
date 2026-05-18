package agentbay

import "encoding/json"

// BetaContextMountAccessMode defines the access mode for context mount
type BetaContextMountAccessMode string

const (
	// BetaAccessModeReadWrite allows read and write access (default)
	BetaAccessModeReadWrite BetaContextMountAccessMode = "readWrite"
	// BetaAccessModeReadOnly allows read-only access
	BetaAccessModeReadOnly BetaContextMountAccessMode = "readOnly"
)

// BetaContextMountStrategy defines the mount strategy for context mount
type BetaContextMountStrategy string

const (
	// BetaMountStrategyStandard is the default mount strategy
	BetaMountStrategyStandard BetaContextMountStrategy = "standard"
	// BetaMountStrategyPerformance is optimized for large files and sequential I/O
	BetaMountStrategyPerformance BetaContextMountStrategy = "performance"
)

// BetaContextMount defines the context mount configuration for direct-mount persistence.
// Unlike ContextSync which requires explicit synchronization, BetaContextMount provides
// write-through persistence where data is persisted immediately.
//
// IMPORTANT: BetaContextMount requires ImageID="aio-ubuntu-2404" on the session.
// Other images do not provide a real OSS-backed mount — writes are not persisted to
// the shared context store and are invisible to other sessions even with the same
// ContextID and mount path.
//
// Use WithSourcePath() to mount only a subdirectory of the context. The subdirectory's
// contents are projected to the mount root.
type BetaContextMount struct {
	// ContextID is the ID of the context to mount
	ContextID string
	// Path is the path where the context should be mounted in the session
	Path string
	// AccessMode defines the access permission (read_write or read_only)
	AccessMode BetaContextMountAccessMode
	// Strategy defines the mount strategy (standard or performance)
	Strategy BetaContextMountStrategy
	// SourcePath is the subpath within the context to mount; empty string mounts entire context
	SourcePath string
}

// NewBetaContextMount creates a new context mount configuration with default values.
func NewBetaContextMount(contextID, path string) *BetaContextMount {
	return &BetaContextMount{
		ContextID:  contextID,
		Path:       path,
		AccessMode: BetaAccessModeReadWrite,
		Strategy:   BetaMountStrategyStandard,
		SourcePath: "",
	}
}

// WithAccessMode sets the access mode and returns the context mount for chaining.
func (cm *BetaContextMount) WithAccessMode(accessMode BetaContextMountAccessMode) *BetaContextMount {
	cm.AccessMode = accessMode
	return cm
}

// WithStrategy sets the mount strategy and returns the context mount for chaining.
func (cm *BetaContextMount) WithStrategy(strategy BetaContextMountStrategy) *BetaContextMount {
	cm.Strategy = strategy
	return cm
}

// WithSourcePath sets the subpath within the context to mount and returns the
// context mount for chaining. Empty string (default) mounts the entire context.
// The selected subdirectory's contents are projected to the mount root.
func (cm *BetaContextMount) WithSourcePath(sourcePath string) *BetaContextMount {
	cm.SourcePath = sourcePath
	return cm
}

// mountConfigJSON returns the JSON string for the mountConfig protocol field.
func (cm *BetaContextMount) mountConfigJSON() (string, error) {
	config := map[string]string{
		"accessMode":  string(cm.AccessMode),
		"storageMode": string(cm.Strategy),
		"sourcePath":  cm.SourcePath,
	}
	data, err := json.Marshal(config)
	if err != nil {
		return "", err
	}
	return string(data), nil
}
