# Core Concepts

Before we start programming, let's understand the essential concepts you need to know to use AgentBay effectively.

> **Multi-language support:** Code examples use Python for illustration. The concepts apply to all SDKs. See: [Python](../../python/README.md) | [TypeScript](../../typescript/README.md) | [Golang](../../golang/README.md) | [Java](../../java/README.md)

## 🌐 What is AgentBay?

AgentBay is a cloud sandbox platform built for AI agents, providing on-demand isolated environments. You can think of it as:
- Cloud-based sandboxes that support different platforms (Linux, Windows, Browser, Android)
- Environments that can be created and destroyed instantly via API
- Designed for AI agents to browse the web, automate desktops, test mobile apps, and execute code

### 📦 AgentBay Class - Your Cloud Gateway

In the SDK, the `AgentBay` class is your main interface for interacting with the cloud service:

```python
from agentbay import AgentBay

# Create AgentBay client instance
agent_bay = AgentBay()
```

The **AgentBay class** serves as your **Session Manager** to create, delete, and manage cloud sessions.

**Basic usage pattern:**
```python
# 1. Initialize client
agent_bay = AgentBay()

# 2. Create session (uses linux_latest by default)
session = agent_bay.create().session

# 3. Use session for your tasks
# ... your automation tasks ...

# 4. Clean up resources
agent_bay.delete(session)
```

**Learn more**: [SDK Configuration Guide](../guides/common-features/configuration/sdk-configuration.md)

## 🔗 Session

A **session** is your connection to a cloud environment. It's like renting a computer in the cloud for a specific period of time.

### Key Characteristics:
- **Temporary**: Sessions are created when you need them and destroyed when you're done
- **Isolated**: Each session is completely separate from others
- **Billable**: You pay for the time your session is active

### Basic Usage:
```python
# Create a session
session = agent_bay.create().session

# Use the session for your tasks
session.command.execute_command("echo 'Hello World'")

# Always clean up when done
agent_bay.delete(session)
```

### Session Lifecycle:
```
Create Session → Use Session → Delete Session
      ↓             ↓              ↓
  Allocate      Execute         Release
  Resources     Operations      Resources
```

### Session Release

Sessions must be released when you're done to free cloud resources. There are **two ways** to release a session:

**1. Manual Release (Recommended)**
```python
# Explicitly delete when done
agent_bay.delete(session)
```

**2. Automatic Timeout Release**
- If not manually deleted, sessions are automatically released after a timeout period
- Use `LifecyclePolicy` for fine-grained control: idle timeout, max runtime, or manual-only release (all in **minutes**)
- Legacy option: `idle_release_timeout` (seconds, default: 300) — still works but deprecated in favor of `LifecyclePolicy`
- After timeout, the session is released and cannot be recovered

**Important**: Always manually delete sessions when finished. This is a best practice for resource management.

**Example (Python):**
```python
from agentbay import AgentBay, CreateSessionParams, LifecyclePolicy

agent_bay = AgentBay()

# Recommended: use LifecyclePolicy (minutes) for new code
params = CreateSessionParams(
    image_id="linux_latest",
    lifecycle_policy=LifecyclePolicy(idle_release_timeout=10, max_runtime=60),
)
session = agent_bay.create(params).session
```

**Learn more**: [Session Management Guide](../guides/common-features/basics/session-management.md)

## 🖥️ Image Types

When creating a session, you must choose an **image type** - this determines what kind of environment you get and what you can do with it.

### Official System Images:

The following table shows the latest official system images provided by AgentBay:

| Image ID | Environment | Best For |
|----------|-------------|----------|
| `linux_latest` | Computer Use | General computing, server tasks (default if not specified) |
| `windows_latest` | Computer Use | General Windows tasks, .NET development, Windows apps |
| `browser_latest` | Browser Use | Web scraping, browser automation, testing websites |
| `code_latest` | CodeSpace  | Coding, development tools, programming tasks |
| `mobile_latest` | Mobile Use | Mobile app testing, Android automation |

**Note**:
- If you don't specify an `image_id`, AgentBay will automatically use `linux_latest` as the default environment.
- These are the current latest versions of official system images. You can also create and use **custom images** through the AgentBay console to meet your specific requirements.

**⚠️ Production Environment Recommendation**:
- The `xxxx_latest` images are automatically updated to newer versions, which may introduce API incompatibilities with older SDK versions.
- **For production environments**, it is strongly recommended to use **custom images** with fixed versions to ensure stability and avoid unexpected breaking changes.
- Learn more about custom images and how to create them: [Custom Images Guide](../guides/common-features/advanced/custom-images.md)

### Choosing the Right Image:

**Windows Environment Example:**
```python
from agentbay import CreateSessionParams

# Create Windows environment and automate notepad
params = CreateSessionParams(image_id="windows_latest")
session = agent_bay.create(params).session

# Start Notepad application
session.computer.start_app("notepad.exe")
# Returns: ProcessListResult with started process info

# Input text into notepad
session.computer.input_text("Hello from Windows!")
# Returns: BoolResult with success status

agent_bay.delete(session)
```

**Browser Environment Example:**
```python
# Create browser environment
params = CreateSessionParams(image_id="browser_latest")
session = agent_bay.create(params).session

# Initialize and navigate
from agentbay import BrowserOption
session.browser.initialize(BrowserOption())
session.browser.operator.navigate("https://www.baidu.com")
print("Web navigation successful")

agent_bay.delete(session)
```

**CodeSpace Environment Example:**
```python
# Create development environment and execute code
params = CreateSessionParams(image_id="code_latest")
session = agent_bay.create(params).session

# Execute code
result = session.code.run_code("print('Hello from CodeSpace!')", "python")
# result.success = True
# result.result = "Hello from CodeSpace!"

agent_bay.delete(session)
```

**Mobile Environment Example:**
```python
# Create Android environment and send HOME key
params = CreateSessionParams(image_id="mobile_latest")
session = agent_bay.create(params).session

# Press HOME key to return to home screen
from agentbay import KeyCode
session.mobile.send_key(KeyCode.HOME)
# Returns: BoolResult with success status
# Example: result.success = True (returns to Android home screen)

agent_bay.delete(session)
```

**Important**: Different images support different features. Choose the image that matches your specific use case.

**Learn more about each environment:**
- [Computer Use Guide](../guides/computer-use/README.md) - Windows/Linux automation
- [Browser Use Guide](../guides/browser-use/README.md) - Web automation and scraping
- [CodeSpace Guide](../guides/codespace/README.md) - Code execution environments
- [Mobile Use Guide](../guides/mobile-use/README.md) - Android automation

## 💾 Data Permanence - Temporary vs Persistent

Understanding data permanence is crucial when using cloud environments:

### Temporary Data (Default Behavior)
- **All data in a session is temporary by default**
- **Everything is lost when the session ends**
- Suitable for: processing tasks, temporary files, cache

```python
# This data will be LOST when session ends
session.file_system.write_file("/tmp/temp_data.txt", "This will disappear")
```

### Persistent Data (Context)
- **Data that survives across sessions**
- **Must be explicitly configured**
- Suitable for: project files, configurations, important results

```python
from agentbay import ContextSync

# Create persistent storage
context = agent_bay.context.get("my-project", create=True).context
context_sync = ContextSync.new(context.id, "/home/wuying")

# Create session with persistent data
params = CreateSessionParams(context_syncs=[context_sync])
session = agent_bay.create(params).session

# This data will be SAVED across sessions
session.file_system.write_file("/home/wuying/important.txt", "This will persist")
```

**Critical Rule**: If you need to keep data, you MUST use Context. Otherwise, it will be lost forever when the session ends.

**Learn more**: 
- [Data Persistence Guide](../guides/common-features/basics/data-persistence.md)
- [File Operations Guide](../guides/common-features/basics/file-operations.md)

## 🔍 Understanding API Results and Request IDs

When you call AgentBay APIs, the results are wrapped in result objects that contain more than just your data:

```python
# Example API call
result = session.command.execute_command("echo hello")

# The result object contains:
print(result.success)      # True/False - whether the operation succeeded
print(result.output)       # Your actual data (command output)
print(result.request_id)   # Request ID for troubleshooting
```

### What is a Request ID?
Every API call to AgentBay gets a unique **Request ID** - a special identifier like `"ABC12345-XXXX-YYYY-ZZZZ-123456789ABC"`.

**Why Request IDs matter:**
- **Troubleshooting**: If something goes wrong, you can provide this ID to support for faster problem resolution
- **Tracking**: Helps track individual operations in logs
- **Debugging**: Makes it easier to identify which specific API call had issues

**When you might need it:**
- API calls fail unexpectedly
- Performance issues with specific operations
- When contacting support about problems

**Example troubleshooting:**
```python
result = session.command.execute_command("some_command")
if not result.success:
    print(f"Command failed! Request ID: {result.request_id}")
    # Share this Request ID with support for faster help
```

Don't worry about Request IDs for normal usage - they're just there when you need them for debugging!

**Learn more**: [Common Features Guide](../guides/common-features/README.md)

## 🚀 Quick Start

Now you understand the essentials:

1. **AgentBay** = Cloud computing platform
2. **Session** = Your temporary connection to a cloud computer
3. **Image** = The type of environment (Linux/Windows/Browser/Code/Mobile)
4. **Data** = Temporary by default, use Context for persistence

Ready to create your first session? Check out the [First Session Guide](first-session.md) - a 5-minute hands-on tutorial!
