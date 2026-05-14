# Class: CreateSessionParamsClass

## ⚙️ Related Tutorial

- [Session Configuration Guide](../../../../../docs/guides/common-features/basics/session-management.md) - Learn how to configure session parameters for different use cases

## Overview

The CreateSessionParams class provides configuration options for creating AgentBay sessions.
It supports session labels, image selection, context synchronization, and SDK-side idle release timeout.

CreateSessionParams provides a way to configure the parameters for creating a new session
in the AgentBay cloud environment.

## Implements

- ``CreateSessionParamsInterface``

## Table of contents


### Properties

- `betaNetworkId`
- `browserContext`
- `enableBrowserReplay`
- `extraConfigs`
- `imageId`
- `isVpc`
- `loadSkills`
- `mcpPolicyId`
- `policyId`
- `skillNames`

## Properties

```typescript
contextMount: [`ContextMount`](context-mount.md)[]
contextSync: [`ContextSync`](context-sync.md)[]
framework: `string`
idleReleaseTimeout: `number`
labels: `Record`<`string`, `string`>
lifecyclePolicy: `undefined` | [`LifecyclePolicy`](lifecycle-policy.md)
```


### betaNetworkId

• `Optional` **betaNetworkId**: `string`

Beta network ID to bind this session to.

#### Implementation of

`CreateSessionParamsInterface`.`betaNetworkId`

___

### browserContext

• `Optional` **browserContext**: ``BrowserContext``

Optional configuration for browser data synchronization.

#### Implementation of

`CreateSessionParamsInterface`.`browserContext`

___

#### Implementation of

`CreateSessionParamsInterface`.`contextMount`

___

#### Implementation of

`CreateSessionParamsInterface`.`contextSync`

___

### enableBrowserReplay

• `Optional` **enableBrowserReplay**: `boolean`

Whether to enable browser session recording. When undefined, server-side default applies.

#### Implementation of

`CreateSessionParamsInterface`.`enableBrowserReplay`

___

### extraConfigs

• `Optional` **extraConfigs**: ``ExtraConfigs``

Additional configuration options.

#### Implementation of

`CreateSessionParamsInterface`.`extraConfigs`

___

#### Implementation of

`CreateSessionParamsInterface`.`framework`

___

#### Implementation of

`CreateSessionParamsInterface`.`idleReleaseTimeout`

___

### imageId

• `Optional` **imageId**: `string`

Image ID to use for the session.

#### Implementation of

`CreateSessionParamsInterface`.`imageId`

___

### isVpc

• `Optional` **isVpc**: `boolean`

Whether to create a VPC-based session. Defaults to false.

#### Implementation of

`CreateSessionParamsInterface`.`isVpc`

___

#### Implementation of

`CreateSessionParamsInterface`.`labels`

___

#### Implementation of

`CreateSessionParamsInterface`.`lifecyclePolicy`

___

### loadSkills

• `Optional` **loadSkills**: `boolean`

Whether to load skills into the sandbox.

#### Implementation of

`CreateSessionParamsInterface`.`loadSkills`

___

### mcpPolicyId

• `Optional` **mcpPolicyId**: `string`

MCP policy id to apply when creating the session.

#### Implementation of

`CreateSessionParamsInterface`.`mcpPolicyId`

___

### policyId

• `Optional` **policyId**: `string`

Security policy ID (interface field name). Maps to mcpPolicyId internally.

#### Implementation of

`CreateSessionParamsInterface`.`policyId`

___

### skillNames

• `Optional` **skillNames**: `string`[]

Skill names to load.

#### Implementation of

`CreateSessionParamsInterface`.`skillNames`

## Best Practices

1. Configure browser type based on your automation needs (Chrome for compatibility, Firefox for specific features)
2. Use headless mode for server environments and headed mode for debugging
3. Set appropriate user agent strings for web scraping to avoid detection
4. Configure timezone and language settings to match your target audience
5. Enable cookies when session state persistence is required


## Related Resources

- [Session API Reference](session.md)
- [AgentBay API Reference](agentbay.md)

