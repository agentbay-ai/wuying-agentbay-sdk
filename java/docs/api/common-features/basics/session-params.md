# ⚙️ Session-params API Reference

## Overview

The CreateSessionParams class provides configuration options for creating AgentBay sessions.
It supports session labels, image selection, context synchronization, and SDK-side idle release timeout.


## 📚 Tutorial

[Session Configuration Guide](../../../../../docs/guides/common-features/basics/session-management.md)

Learn how to configure session parameters for different use cases

## CreateSessionParams

Parameters for creating a new session in the AgentBay cloud environment.

<p>Supports various configuration options including labels, context synchronization,
browser context, policy management, browser replay, and mobile extra configurations.</p>

### Constructor

```java
public CreateSessionParams()
```

Create a new CreateSessionParams instance with default values(contextSyncs: empty list,idleReleaseTimeout: 300 seconds).

### Methods

### setBrowserContext

```java
public void setBrowserContext(BrowserContext browserContext)
```

Set the browser context and automatically merge extension and fingerprint context syncs.

**Parameters:**
- `browserContext` (BrowserContext): Browser context configuration

### getImageId

```java
public String getImageId()
```

Get the ID of the image to use for the session.

**Returns:**
- `String`: image ID, or null if not set

### setImageId

```java
public void setImageId(String imageId)
```

Set the ID of the image to use for the session.

**Parameters:**
- `imageId` (String): image ID

### getIdleReleaseTimeout

```java
public Integer getIdleReleaseTimeout()
```

Get the SDK-side idle release timeout in seconds.

**Returns:**
- `Integer`: idle release timeout in seconds, or null if not set

### setIdleReleaseTimeout

```java
public void setIdleReleaseTimeout(Integer idleReleaseTimeout)
```

Set the SDK-side idle release timeout in seconds.

**Parameters:**
- `idleReleaseTimeout` (Integer): idle release timeout in seconds

**Throws:**
- `IllegalArgumentException`: if {@link #lifecyclePolicy} is already set

### getLifecyclePolicy

```java
public LifecyclePolicy getLifecyclePolicy()
```

Gets the lifecycle policy (minutes-based), if set.

**Returns:**
- `LifecyclePolicy`: lifecycle policy, or null

### setLifecyclePolicy

```java
public void setLifecyclePolicy(LifecyclePolicy lifecyclePolicy)
```

Sets the lifecycle policy. Mutually exclusive with {@link #idleReleaseTimeout}.

**Parameters:**
- `lifecyclePolicy` (LifecyclePolicy): lifecycle configuration

**Throws:**
- `IllegalArgumentException`: if idle release timeout was already set (non-null)

### getLabels

```java
public Map<String, String> getLabels()
```

Get the custom labels for the Session.

**Returns:**
- `Map<String,String>`: labels map, or null if not set

### setLabels

```java
public void setLabels(Map<String, String> labels)
```

Set the custom labels for the Session.

**Parameters:**
- `labels` (Map<String,String>): labels map

### getContextSyncs

```java
public List<ContextSync> getContextSyncs()
```

Get the list of context synchronization configurations.

**Returns:**
- `List<ContextSync>`: list of context syncs, or null if not set

### setContextSyncs

```java
public void setContextSyncs(List<ContextSync> contextSyncs)
```

Set the list of context synchronization configurations.

**Parameters:**
- `contextSyncs` (List<ContextSync>): list of context syncs

### getBrowserContext

```java
public BrowserContext getBrowserContext()
```

Get the browser context configuration.

**Returns:**
- `BrowserContext`: browser context, or null if not set

### getFramework

```java
public String getFramework()
```

Get the framework name (e.g., "langchain").
This is used for SDK statistics tracking.

**Returns:**
- `String`: framework name, or null if not set

### setFramework

```java
public void setFramework(String framework)
```

Set the framework name (e.g., "langchain").
This is used for SDK statistics tracking.

**Parameters:**
- `framework` (String): framework name

### getPolicyId

```java
public String getPolicyId()
```

Get the policy ID to apply when creating the session.

**Returns:**
- `String`: Policy ID, or null if not set

### setPolicyId

```java
public void setPolicyId(String policyId)
```

Set the policy ID to apply when creating the session.

**Parameters:**
- `policyId` (String): Policy ID

### getEnableBrowserReplay

```java
public Boolean getEnableBrowserReplay()
```

Get whether browser replay recording is enabled.

**Returns:**
- `Boolean`: true if enabled, false if disabled, null if not set

### setEnableBrowserReplay

```java
public void setEnableBrowserReplay(Boolean enableBrowserReplay)
```

Set whether to enable browser replay recording for the session.

**Parameters:**
- `enableBrowserReplay` (Boolean): true to enable, false to disable

### getExtraConfigs

```java
public ExtraConfigs getExtraConfigs()
```

Get Advanced configuration parameters for mobile environments.

**Returns:**
- `ExtraConfigs`: ExtraConfigs instance, or null if not set

### setExtraConfigs

```java
public void setExtraConfigs(ExtraConfigs extraConfigs)
```

Set Advanced configuration parameters for mobile environments.

**Parameters:**
- `extraConfigs` (ExtraConfigs): Advanced configuration parameters

### getBetaNetworkId

```java
public String getBetaNetworkId()
```

Get the Beta network ID to bind this session to.

**Returns:**
- `String`: beta network ID, or null if not set

### setBetaNetworkId

```java
public void setBetaNetworkId(String betaNetworkId)
```

Set the Beta network ID to bind this session to.

**Parameters:**
- `betaNetworkId` (String): beta network ID

### getLoadSkills

```java
public Boolean getLoadSkills()
```

Get whether to load skills into the sandbox.

**Returns:**
- `Boolean`: true to load skills, null or false otherwise

### setLoadSkills

```java
public void setLoadSkills(Boolean loadSkills)
```

Set whether to load skills into the sandbox.

**Parameters:**
- `loadSkills` (Boolean): true to load skills

### getSkillNames

```java
public List<String> getSkillNames()
```

Get skill names to load.

**Returns:**
- `List<String>`: list of skill names, or null

### setSkillNames

```java
public void setSkillNames(List<String> skillNames)
```

Set skill names to load. Loads all visible skills when loadSkills=true and this is not specified.

**Parameters:**
- `skillNames` (List<String>): list of skill names



## 💡 Best Practices

- Configure browser type based on your automation needs (Chrome for compatibility, Firefox for specific features)
- Use headless mode for server environments and headed mode for debugging
- Set appropriate user agent strings for web scraping to avoid detection
- Configure timezone and language settings to match your target audience
- Enable cookies when session state persistence is required

## 🔗 Related Resources

- [Session API Reference](../../../api/common-features/basics/session.md)
- [AgentBay API Reference](../../../api/common-features/basics/agentbay.md)

