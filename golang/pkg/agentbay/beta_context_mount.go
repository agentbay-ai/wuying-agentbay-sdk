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
type BetaContextMount struct {
	// ContextID is the ID of the context to mount
	ContextID string
	// Path is the path where the context should be mounted in the session
	Path string
	// AccessMode defines the access permission (read_write or read_only)
	AccessMode BetaContextMountAccessMode
	// Strategy defines the mount strategy (standard or performance)
	Strategy BetaContextMountStrategy
}

// NewBetaContextMount creates a new context mount configuration with default values.
func NewBetaContextMount(contextID, path string) *BetaContextMount {
	return &BetaContextMount{
		ContextID:  contextID,
		Path:       path,
		AccessMode: BetaAccessModeReadWrite,
		Strategy:   BetaMountStrategyStandard,
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

// mountConfigJSON returns the JSON string for the mountConfig protocol field.
func (cm *BetaContextMount) mountConfigJSON() (string, error) {
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
