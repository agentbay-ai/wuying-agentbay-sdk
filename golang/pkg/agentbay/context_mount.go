package agentbay

import "encoding/json"

// ContextMountAccessMode defines the access mode for context mount
type ContextMountAccessMode string

const (
	// AccessModeReadWrite allows read and write access (default)
	AccessModeReadWrite ContextMountAccessMode = "readWrite"
	// AccessModeReadOnly allows read-only access
	AccessModeReadOnly ContextMountAccessMode = "readOnly"
)

// ContextMountStrategy defines the mount strategy for context mount
type ContextMountStrategy string

const (
	// MountStrategyStandard is the default mount strategy
	MountStrategyStandard ContextMountStrategy = "standard"
	// MountStrategyPerformance is optimized for large files and sequential I/O
	MountStrategyPerformance ContextMountStrategy = "performance"
)

// ContextMount defines the context mount configuration for direct-mount persistence.
// Unlike ContextSync which requires explicit synchronization, ContextMount provides
// write-through persistence where data is persisted immediately.
type ContextMount struct {
	// ContextID is the ID of the context to mount
	ContextID string
	// Path is the path where the context should be mounted in the session
	Path string
	// AccessMode defines the access permission (read_write or read_only)
	AccessMode ContextMountAccessMode
	// Strategy defines the mount strategy (standard or performance)
	Strategy ContextMountStrategy
}

// NewContextMount creates a new context mount configuration with default values.
func NewContextMount(contextID, path string) *ContextMount {
	return &ContextMount{
		ContextID:  contextID,
		Path:       path,
		AccessMode: AccessModeReadWrite,
		Strategy:   MountStrategyStandard,
	}
}

// WithAccessMode sets the access mode and returns the context mount for chaining.
func (cm *ContextMount) WithAccessMode(accessMode ContextMountAccessMode) *ContextMount {
	cm.AccessMode = accessMode
	return cm
}

// WithStrategy sets the mount strategy and returns the context mount for chaining.
func (cm *ContextMount) WithStrategy(strategy ContextMountStrategy) *ContextMount {
	cm.Strategy = strategy
	return cm
}

// mountConfigJSON returns the JSON string for the mountConfig protocol field.
func (cm *ContextMount) mountConfigJSON() (string, error) {
	config := map[string]string{
		"accessMode":  string(cm.AccessMode),
		"storageMode": string(cm.Strategy),
	}
	data, err := json.Marshal(config)
	if err != nil {
		return "", err
	}
	return string(data), nil
}
