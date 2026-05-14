package agentbay

import (
	"encoding/json"
	"fmt"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
)

// CreateSessionParams provides a way to configure the parameters for creating a new session
// in the AgentBay cloud environment.
type CreateSessionParams struct {
	// Labels are custom labels for the Session. These can be used for organizing and filtering sessions.
	Labels map[string]string

	// ImageId specifies the image ID to use for the session.
	ImageId string

	// IdleReleaseTimeout specifies the SDK-side idle release timeout in seconds.
	// Default is 300 seconds. Deprecated for new code: use LifecyclePolicy (minutes).
	IdleReleaseTimeout int32

	// LifecyclePolicy configures idle release and max runtime in minutes, and optional manual release.
	// Mutually exclusive with IdleReleaseTimeout when that field is set (greater than zero).
	LifecyclePolicy *LifecyclePolicy

	// ContextSync is a list of context synchronization configurations.
	// These configurations define how contexts should be synchronized and mounted.
	ContextSync []*ContextSync

	// ContextMount is a list of context mount configurations for direct-mount persistence.
	ContextMount []*ContextMount

	// PolicyId specifies the policy ID to apply when creating the session.
	PolicyId string

	// BetaNetworkId specifies the beta network ID to bind this session to.
	BetaNetworkId string

	// ExtraConfigs contains extra configuration settings for different session types
	ExtraConfigs *models.ExtraConfigs

	// Framework specifies the framework name for tracking (e.g., "langchain"). Empty string means direct call.
	Framework string

	// EnableBrowserReplay specifies whether to enable browser recording for this session.
	// When nil (not set), server-side default behavior applies.
	EnableBrowserReplay *bool

	// BrowserContext specifies persistent browser context configuration for this session.
	// When set, the session will be bound to the given cloud context and browser state will
	// persist across sessions.
	BrowserContext *BrowserContext

	// LoadSkills when true, loads skills into the sandbox. Use BetaSkills.GetMetadata() to discover available skills.
	LoadSkills bool

	// SkillNames filter which skills to load by name. When LoadSkills is true and this is empty, loads all visible skills.
	SkillNames []string
}

// NewCreateSessionParams creates a new CreateSessionParams with default values.
func NewCreateSessionParams() *CreateSessionParams {
	return &CreateSessionParams{
		Labels:       make(map[string]string),
		ContextSync:  make([]*ContextSync, 0),
		ContextMount: make([]*ContextMount, 0),
	}
}

// WithLabels sets the labels for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithLabels(labels map[string]string) *CreateSessionParams {
	p.Labels = labels
	return p
}

// WithImageId sets the image ID for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithImageId(imageId string) *CreateSessionParams {
	p.ImageId = imageId
	return p
}

// WithIdleReleaseTimeout sets the SDK-side idle release timeout in seconds and returns the updated parameters.
// Only positive values are accepted.
func (p *CreateSessionParams) WithIdleReleaseTimeout(timeoutSeconds int32) *CreateSessionParams {
	if timeoutSeconds > 0 {
		p.IdleReleaseTimeout = timeoutSeconds
	}
	return p
}

// WithLifecyclePolicy sets the lifecycle policy (minutes). Mutually exclusive with IdleReleaseTimeout when IdleReleaseTimeout > 0.
func (p *CreateSessionParams) WithLifecyclePolicy(lp *LifecyclePolicy) (*CreateSessionParams, error) {
	if lp != nil && p.IdleReleaseTimeout > 0 {
		return nil, fmt.Errorf("lifecycle policy cannot be used together with IdleReleaseTimeout; clear IdleReleaseTimeout first")
	}
	p.LifecyclePolicy = lp
	return p, nil
}

// WithPolicyId sets the policy ID for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithPolicyId(policyId string) *CreateSessionParams {
	p.PolicyId = policyId
	return p
}

// WithBetaNetworkId sets the beta network ID for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithBetaNetworkId(betaNetworkId string) *CreateSessionParams {
	p.BetaNetworkId = betaNetworkId
	return p
}

// WithExtraConfigs sets the extra configurations for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithExtraConfigs(extraConfigs *models.ExtraConfigs) *CreateSessionParams {
	p.ExtraConfigs = extraConfigs
	return p
}

// WithEnableBrowserReplay sets the browser replay flag for the session parameters and returns the updated parameters.
func (p *CreateSessionParams) WithEnableBrowserReplay(enableBrowserReplay bool) *CreateSessionParams {
	p.EnableBrowserReplay = &enableBrowserReplay
	return p
}

// WithBrowserContext sets the browser context configuration for the session parameters.
func (p *CreateSessionParams) WithBrowserContext(browserContext *BrowserContext) *CreateSessionParams {
	p.BrowserContext = browserContext
	return p
}

// WithLoadSkills sets whether to load skills into the sandbox.
func (p *CreateSessionParams) WithLoadSkills(loadSkills bool) *CreateSessionParams {
	p.LoadSkills = loadSkills
	return p
}

// WithSkillNames sets the skill names to load. When LoadSkills is true and this is empty, loads all visible skills.
func (p *CreateSessionParams) WithSkillNames(names []string) *CreateSessionParams {
	p.SkillNames = names
	return p
}

// GetLabelsJSON returns the labels as a JSON string.
func (p *CreateSessionParams) GetLabelsJSON() (string, error) {
	if len(p.Labels) == 0 {
		return "", nil
	}

	labelsJSON, err := json.Marshal(p.Labels)
	if err != nil {
		return "", err
	}

	return string(labelsJSON), nil
}

// GetExtraConfigsJSON returns the extra configs as a JSON string.
func (p *CreateSessionParams) GetExtraConfigsJSON() (string, error) {
	if p.ExtraConfigs == nil {
		return "", nil
	}

	return p.ExtraConfigs.ToJSON()
}

// AddContextSync adds a context sync configuration to the session parameters.
func (p *CreateSessionParams) AddContextSync(contextID, path string, policy *SyncPolicy) *CreateSessionParams {
	contextSync := &ContextSync{
		ContextID: contextID,
		Path:      path,
		Policy:    policy,
	}
	p.ContextSync = append(p.ContextSync, contextSync)
	return p
}

// AddContextSyncConfig adds a pre-configured context sync to the session parameters.
func (p *CreateSessionParams) AddContextSyncConfig(contextSync *ContextSync) *CreateSessionParams {
	p.ContextSync = append(p.ContextSync, contextSync)
	return p
}

// WithContextSync sets the context sync configurations for the session parameters.
func (p *CreateSessionParams) WithContextSync(contextSyncs []*ContextSync) *CreateSessionParams {
	p.ContextSync = contextSyncs
	return p
}

// AddContextMount adds a context mount configuration to the session parameters.
func (p *CreateSessionParams) AddContextMount(contextMount *ContextMount) *CreateSessionParams {
	p.ContextMount = append(p.ContextMount, contextMount)
	return p
}

// WithContextMount sets the context mount configurations for the session parameters.
func (p *CreateSessionParams) WithContextMount(contextMounts []*ContextMount) *CreateSessionParams {
	p.ContextMount = contextMounts
	return p
}
