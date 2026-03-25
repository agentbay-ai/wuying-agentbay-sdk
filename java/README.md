# AgentBay SDK for Java

> Execute commands, operate files, and run code in cloud environments

## 📦 Installation

> **Note:** Please check [Maven Central](https://central.sonatype.com/artifact/com.aliyun/agentbay-sdk) for the latest version number and replace `LATEST_VERSION` below.

### Maven
```xml
<dependency>
    <groupId>com.aliyun</groupId>
    <artifactId>agentbay-sdk</artifactId>
    <version>LATEST_VERSION</version>
</dependency>
```

### Gradle
```gradle
implementation 'com.aliyun:agentbay-sdk:LATEST_VERSION'
```

## 🚀 Prerequisites

Before using the SDK, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get API credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Set environment variable: `export AGENTBAY_API_KEY=your_api_key`

## 🚀 Quick Start

```java
import com.aliyun.agentbay.*;

// Create session
AgentBay agentBay = new AgentBay();
CreateSessionParams params = new CreateSessionParams();
SessionResult result = agentBay.create(params);

if (result.isSuccess()) {
    Session session = result.getSession();

    // Execute command
    CommandResult cmdResult = session.getCommand().executeCommand("ls -la");
    System.out.println(cmdResult.getOutput());

    // File operations
    session.getFileSystem().writeFile("/tmp/test.txt", "Hello World");
    FileContentResult content = session.getFileSystem().readFile("/tmp/test.txt");
    System.out.println(content.getContent());  // Hello World

    // Clean up
    session.delete();
}
```

## ⚙️ Configuration

### Using Environment Variables (Recommended)

The SDK automatically reads configuration from environment variables:

```bash
export AGENTBAY_API_KEY=your_api_key
export AGENTBAY_ENDPOINT=wuyingai.cn-shanghai.aliyuncs.com  # Optional
export AGENTBAY_REGION_ID=cn-shanghai                       # Optional
export AGENTBAY_TIMEOUT_MS=60000                            # Optional
```

```java
AgentBay agentBay = new AgentBay();
```

### Explicit Configuration

You can also provide configuration explicitly:

```java
String apiKey = "your_api_key";
Config config = new Config("cn-shanghai", "wuyingai.cn-shanghai.aliyuncs.com", 60000);
AgentBay agentBay = new AgentBay(apiKey, config);
```

Or just override the API key:

```java
AgentBay agentBay = new AgentBay("your_api_key");
```

### Configuration Priority

The SDK uses the following precedence order (highest to lowest):
1. Explicitly passed configuration in code
2. Environment variables
3. Default configuration

## 📖 Complete Documentation

### 🆕 New Users
- [📚 Quick Start Tutorial](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/quickstart/README.md) - Get started in 5 minutes
- [🎯 Core Concepts](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/quickstart/basic-concepts.md) - Understand cloud environments and sessions

### 🚀 Experienced Users
**Choose Your Cloud Environment:**
- 🌐 [Browser Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/browser-use/README.md) - Web scraping, browser testing, form automation
- 🖥️ [Computer Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/computer-use/README.md) - Windows desktop automation, UI testing
- 📱 [Mobile Use](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/mobile-use/README.md) - Android UI testing, mobile app automation
- 💻 [CodeSpace](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/codespace/README.md) - Code execution, development environments

**Additional Resources:**
- [📖 Feature Guides](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/README.md) - Complete feature introduction
- [🔧 Java API Reference](docs/api/README.md) - Detailed API documentation
- [💻 Java Examples](docs/examples/README.md) - Complete example code
- [📋 Logging Configuration](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/guides/common-features/configuration/logging.md) - Configure logging levels and output

## 🔧 Core Features Quick Reference

### Session Management
```java
// Create session
SessionResult result = agentBay.create(new CreateSessionParams());
Session session = result.getSession();

// List sessions by labels
Map<String, String> labels = new HashMap<>();
labels.put("environment", "production");
SessionListResult listResult = agentBay.list(labels, 10);

// Delete session
session.delete();
```

### File Operations
```java
// Read and write files
session.getFileSystem().writeFile("/path/file.txt", "content");
FileContentResult content = session.getFileSystem().readFile("/path/file.txt");
System.out.println(content.getContent());

// List directory
DirectoryListResult files = session.getFileSystem().listDirectory("/path");
```

### Command Execution
```java
// Execute command
CommandResult result = session.getCommand().executeCommand("java MyClass.java");
System.out.println(result.getOutput());
```

### Data Persistence
```java
// Create context
Context context = agentBay.getContext().get("my-project", true).getContext();

// Create session with context
ContextSync contextSync = ContextSync.create(
    context.getId(),
    "/tmp/data",
    SyncPolicy.defaultPolicy()
);
CreateSessionParams params = new CreateSessionParams()
    .setContextSyncs(Arrays.asList(contextSync));
Session session = agentBay.create(params).getSession();
```

### Code Execution
```java
// Run code in isolated environment
CreateSessionParams params = new CreateSessionParams().setImageId("code_latest");
Session session = agentBay.create(params).getSession();

CodeExecutionResult result = session.getCode().runCode("print('Hello World')", "python");
if (result.isSuccess()) {
    System.out.println(result.getResult());  // Hello World
}
```

## 🆘 Get Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation](https://github.com/agentbay-ai/wuying-agentbay-sdk/tree/main/docs/README.md)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE) file for details.
