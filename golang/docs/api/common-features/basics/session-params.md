# Session Params API Reference

## ⚙️ Related Tutorial

- [Session Configuration Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Learn how to configure session parameters for different use cases

## Overview

The CreateSessionParams class provides configuration options for creating AgentBay sessions.
It supports session labels, image selection, context synchronization, and SDK-side idle release timeout.

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

## Type ListSessionParams

```go
type ListSessionParams struct {
	MaxResults	int32			// Number of results per page
	NextToken	string			// Token for the next page
	Labels		map[string]string	// Labels to filter by
}
```

ListSessionParams contains parameters for listing sessions

### Related Functions

### NewListSessionParams

```go
func NewListSessionParams() *ListSessionParams
```

NewListSessionParams creates a new ListSessionParams with default values

## Functions

### NewCreateSessionParams

```go
func NewCreateSessionParams() *CreateSessionParams
```

NewCreateSessionParams creates a new CreateSessionParams with default values.

### NewListSessionParams

```go
func NewListSessionParams() *ListSessionParams
```

NewListSessionParams creates a new ListSessionParams with default values

## Best Practices

1. Configure browser type based on your automation needs (Chrome for compatibility, Firefox for specific features)
2. Use headless mode for server environments and headed mode for debugging
3. Set appropriate user agent strings for web scraping to avoid detection
4. Configure timezone and language settings to match your target audience
5. Enable cookies when session state persistence is required

## Related Resources

- [Session API Reference](session.md)
- [AgentBay API Reference](agentbay.md)

---

*Documentation generated automatically from Go source code.*
