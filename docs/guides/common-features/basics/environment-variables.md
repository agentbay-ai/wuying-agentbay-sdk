# Environment Variables Guide

This guide covers the environment variable management capabilities in AgentBay SDK. The env module allows you to set, query, and manage global environment variables in cloud sessions.

> **Multi-language support:** Code examples use Python. The env API is available in all SDKs with similar patterns. See: [Python](../../../../python/README.md) | [TypeScript](../../../../typescript/README.md) | [Golang](../../../../golang/README.md) | [Java](../../../../java/README.md)

> **Async API Support**: This guide uses synchronous API by default. For async/await syntax, replace `AgentBay` with `AsyncAgentBay` and add `await` to method calls.

## Table of Contents

- [Overview](#overview)
- [Setting Environment Variables](#setting-environment-variables)
- [Getting Environment Variables](#getting-environment-variables)
- [Overwriting Variables](#overwriting-variables)
- [Shell Visibility](#shell-visibility)
- [Multi-Language Examples](#multi-language-examples)
- [Best Practices](#best-practices)

<a id="overview"></a>
## Overview

The `session.env` module provides methods to manage **global** environment variables that persist across all MCP tools within a session. Once set, variables are visible to shell commands, code interpreters, and other tools running in the same session.

### Key Features

- Set one or more environment variables at once
- Query all or specific variables by key
- Variables persist for the lifetime of the session
- Visible to shell commands (`echo $VAR`), code execution, and all other tools

### When to Use

| Scenario | Approach |
|----------|----------|
| Configure API keys or tokens for tools | `session.env.set({"API_KEY": "..."})` |
| Set PATH or language-specific vars | `session.env.set({"PATH": "/custom/bin:$PATH"})` |
| Per-command env vars (one-off) | `session.command.execute_command("VAR=val cmd")` |
| Inspect current environment | `session.env.get()` |

<a id="setting-environment-variables"></a>
## Setting Environment Variables

### Basic Usage

```python
from agentbay import AgentBay

agent_bay = AgentBay()
result = agent_bay.create()
session = result.session

# Set one or more variables
set_result = session.env.set({
    "DATABASE_URL": "postgres://localhost:5432/mydb",
    "LOG_LEVEL": "debug",
})

print(f"Success: {set_result.success}")

# Clean up
agent_bay.delete(session)
```

### Validation Rules

- The `envs` dictionary must not be empty
- Both keys and values must be strings
- Passing an empty dict raises a `ValueError`

```python
# This raises ValueError
session.env.set({})

# This also raises ValueError (non-string key)
session.env.set({123: "value"})
```

<a id="getting-environment-variables"></a>
## Getting Environment Variables

### Get All Variables

```python
result = session.env.get()
if result.success:
    for key, value in result.envs.items():
        print(f"{key}={value}")
```

### Get Specific Variables

```python
result = session.env.get(keys=["DATABASE_URL", "LOG_LEVEL"])
if result.success:
    print(result.envs["DATABASE_URL"])  # postgres://localhost:5432/mydb
    print(result.envs["LOG_LEVEL"])     # debug
```

<a id="overwriting-variables"></a>
## Overwriting Variables

Calling `set` with an existing key overwrites its value:

```python
session.env.set({"MY_VAR": "original"})
result = session.env.get(keys=["MY_VAR"])
print(result.envs["MY_VAR"])  # "original"

session.env.set({"MY_VAR": "updated"})
result = session.env.get(keys=["MY_VAR"])
print(result.envs["MY_VAR"])  # "updated"
```

<a id="shell-visibility"></a>
## Shell Visibility

Variables set via `session.env.set` are immediately visible to shell commands:

```python
session.env.set({"GREETING": "Hello from AgentBay!"})

cmd_result = session.command.execute_command("echo $GREETING")
print(cmd_result.stdout)  # "Hello from AgentBay!"
```

This also applies to code execution and other MCP tools running within the same session.

<a id="multi-language-examples"></a>
## Multi-Language Examples

### TypeScript

```typescript
import { AgentBay } from "@anthropic/agentbay";

const agentBay = new AgentBay();
const { session } = await agentBay.create();

await session.env.set({ NODE_ENV: "production", PORT: "3000" });

const result = await session.env.get(["NODE_ENV"]);
console.log(result.envs["NODE_ENV"]); // "production"

await agentBay.delete(session);
```

### Go

```go
package main

import (
    "fmt"
    agentbay "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

func main() {
    ab, _ := agentbay.NewAgentBay()
    session, _ := ab.Create()
    defer ab.Delete(session)

    session.Env.Set(map[string]string{
        "GO_ENV": "production",
    })

    result, _ := session.Env.Get("GO_ENV")
    fmt.Println(result.Envs["GO_ENV"]) // "production"
}
```

### Java

```java
import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.session.Session;
import com.aliyun.agentbay.model.EnvResult;

import java.util.HashMap;
import java.util.Map;

public class EnvExample {
    public static void main(String[] args) throws Exception {
        AgentBay agentBay = new AgentBay();
        Session session = agentBay.createSession();

        Map<String, String> envs = new HashMap<>();
        envs.put("JAVA_ENV", "production");
        session.getEnv().set(envs);

        EnvResult result = session.getEnv().get("JAVA_ENV");
        System.out.println(result.getEnvs().get("JAVA_ENV")); // "production"

        agentBay.deleteSession(session);
    }
}
```

<a id="best-practices"></a>
## Best Practices

1. **Set variables early** — Configure environment variables before running commands or code that depend on them.

2. **Use descriptive key names** — Follow the `UPPER_SNAKE_CASE` convention for environment variable names.

3. **Query specific keys** — When you only need a few variables, pass their names to `get()` to reduce response size.

4. **String values only** — Both keys and values must be strings. Convert numbers or booleans to strings before setting.

5. **No delete API** — To effectively "unset" a variable, set it to an empty string:
   ```python
   session.env.set({"OBSOLETE_VAR": ""})
   ```

6. **Session-scoped** — Variables are scoped to the session lifetime. They do not persist after session deletion.

## Related Resources

- [Command Execution Guide](command-execution.md) — Running shell commands that use env variables
- [Session Management Guide](session-management.md) — Creating and managing sessions
- [Python API Reference](../../../../python/docs/api/sync/env.md)
- [TypeScript API Reference](../../../../typescript/docs/api/common-features/basics/env.md)
- [Go API Reference](../../../../golang/docs/api/common-features/basics/env.md)
- [Java API Reference](../../../../java/docs/api/common-features/basics/env.md)
