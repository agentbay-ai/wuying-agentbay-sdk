<div align="center">

[![arXiv](https://img.shields.io/badge/Paper-arXiv-b31b1b.svg?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2512.04367)
[![PyPI Downloads](https://img.shields.io/pypi/dm/wuying-agentbay-sdk?label=PyPI%20Downloads&logo=python&logoColor=white&cacheSeconds=86400)](https://pypi.org/project/wuying-agentbay-sdk/)
[![NPM Downloads](https://img.shields.io/npm/dm/wuying-agentbay-sdk?label=NPM%20Downloads&logo=npm)](https://www.npmjs.com/package/wuying-agentbay-sdk)
[![Go Report Card](https://goreportcard.com/badge/github.com/agentbay-ai/wuying-agentbay-sdk/golang)](https://goreportcard.com/report/github.com/agentbay-ai/wuying-agentbay-sdk/golang)
[![Maven Central](https://img.shields.io/maven-central/v/com.aliyun/agentbay-sdk?color=blue&logo=apache-maven)](https://central.sonatype.com/artifact/com.aliyun/agentbay-sdk)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](https://github.com/agentbay-ai/wuying-agentbay-sdk/blob/main/LICENSE)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/agentbay-ai/wuying-agentbay-sdk)

</div>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="./assets/Agentbay-dark.png" width="800px">
    <source media="(prefers-color-scheme: light)" srcset="./assets/Agentbay-light.png" width="800px">
    <img src="./assets/Agentbay-light.png" alt="AgentBay" width="800px" />
  </picture>
</p>

<p align="center">
  <b>The Cloud Sandbox Built for AI Agents</b>
</p>

AgentBay provides **on-demand cloud sandboxes** for AI agents — isolated environments with browser, desktop, mobile, and code execution capabilities. Create a sandbox in seconds, let your agent do its work, and tear it down when done. No infrastructure to manage.

With SDKs for **Python**, **TypeScript**, **Golang**, and **Java**, AgentBay gives your agents a full cloud environment through a simple API: execute commands, browse the web, automate desktop apps, test mobile UIs, or run code — all in secure, disposable sandboxes.

---

## 🎯 What You Can Do

<table>
<tr>
<td width="50%" align="center" valign="top">
  <img src="./assets/Browser Use@2x.png" width="460px" alt="Browser Use"/>
  <h3>🌐 Browser Use</h3>
  <p>Automate web operations including content scraping, testing, and workflows. Cross-browser compatible with natural language control and remote access.</p>
  <p><a href="docs/guides/browser-use/README.md">Learn more →</a></p>
</td>
<td width="50%" align="center" valign="top">
  <img src="./assets/Computer Use@2x.png" width="460px" alt="Computer Use"/>
  <h3>🖥️ Computer Use</h3>
  <p>Cloud desktop environment for enterprise application automation. Standardized interfaces enable legacy software automation with intelligent resource scheduling.</p>
  <p><a href="docs/guides/computer-use/README.md">Learn more →</a></p>
</td>
</tr>
<tr>
<td width="50%" align="center" valign="top">
  <img src="./assets/Mobile Use@2x.png" width="460px" alt="Mobile Use"/>
  <h3>📱 Mobile Use</h3>
  <p>Cloud-based mobile environment for intelligent app automation. Precise UI recognition and control with parallel task processing for testing scenarios.</p>
  <p><a href="docs/guides/mobile-use/README.md">Learn more →</a></p>
</td>
<td width="50%" align="center" valign="top">
  <img src="./assets/Code Space@2x.png" width="460px" alt="Code Space"/>
  <h3>💻 Code Space</h3>
  <p>Professional cloud development environment supporting multi-language code generation, compilation, and debugging. Secure, intelligent automated programming experience.</p>
  <p><a href="docs/guides/codespace/README.md">Learn more →</a></p>
</td>
</tr>
</table>

## ✅ Prerequisites

Before using the SDK, you need to:

1. Register an Alibaba Cloud account: [https://aliyun.com](https://aliyun.com)
2. Get APIKEY credentials: [AgentBay Console](https://agentbay.console.aliyun.com/service-management)
3. Set environment variable:
   - For Linux/MacOS:
     ```bash
     export AGENTBAY_API_KEY=your_api_key_here
     ```
   - For Windows:
     ```cmd
     setx AGENTBAY_API_KEY your_api_key_here
     ```

## 📦 Installation

| Language | Install Command | Documentation |
|----------|----------------|---------------|
| Python | `pip install wuying-agentbay-sdk` | [Python Docs](python/README.md) |
| TypeScript | `npm install wuying-agentbay-sdk` | [TypeScript Docs](typescript/README.md) |
| Golang | `go get github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay` | [Golang Docs](golang/README.md) |
| Java | See Maven snippet below | [Java Docs](java/README.md) |

<details>
<summary>Java Maven dependency</summary>

```xml
<dependency>
    <groupId>com.aliyun</groupId>
    <artifactId>agentbay-sdk</artifactId>
    <version>0.19.0</version>
</dependency>
```

</details>

## 🚀 Quick Start

### Python

```python
from agentbay import AgentBay, CreateSessionParams

agent_bay = AgentBay()

# Create a cloud sandbox (options: "code_latest", "browser_latest", "desktop_latest")
session = agent_bay.create(CreateSessionParams(image_id="code_latest")).session

# Execute code in the sandbox
result = session.code.run_code("print('Hello AgentBay')", "python")
if result.success:
    print(result.result)  # Hello AgentBay

agent_bay.delete(session)
```

### TypeScript

```typescript
import { AgentBay } from 'wuying-agentbay-sdk';

const agentBay = new AgentBay();

// Create a cloud sandbox
const session = (await agentBay.create({ imageId: "code_latest" })).session;

// Execute code in the sandbox
const result = await session.code.runCode("print('Hello AgentBay')", "python");
if (result.success) {
    console.log(result.result);  // Hello AgentBay
}

await agentBay.delete(session);
```

### Golang

```go
import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"

client, _ := agentbay.NewAgentBay("", nil)

// Create a cloud sandbox
result, _ := client.Create(agentbay.NewCreateSessionParams().WithImageId("code_latest"))
session := result.Session

// Execute code in the sandbox
res, _ := session.Code.RunCode("print('Hello AgentBay')", "python")
fmt.Println(res.Output)  // Hello AgentBay

client.Delete(session, false)
```

### Java

```java
import com.aliyun.agentbay.*;

AgentBay agentBay = new AgentBay();

// Create a cloud sandbox
CreateSessionParams params = new CreateSessionParams().setImageId("code_latest");
Session session = agentBay.create(params).getSession();

// Execute code in the sandbox
CodeExecutionResult result = session.getCode().runCode("print('Hello AgentBay')", "python");
if (result.isSuccess()) {
    System.out.println(result.getResult());  // Hello AgentBay
}

agentBay.delete(session, false);
```

## 📚 Documentation

> **New to AgentBay?** Start with the [Quick Start Tutorial](docs/quickstart/README.md) — you'll be up and running in 5 minutes.

| Resource | Description |
|----------|-------------|
| [Quick Start Tutorial](docs/quickstart/README.md) | Get started in 5 minutes |
| [Core Concepts](docs/quickstart/basic-concepts.md) | Understand sessions, environments, and sandboxes |
| [Feature Guides](docs/guides/README.md) | In-depth guides for each capability |
| [API Reference](python/docs/api/) | Complete API docs ([Python](python/docs/api/) · [TypeScript](typescript/docs/api/) · [Golang](golang/docs/api/) · [Java](java/docs/api/)) |
| [Cookbook](cookbook/README.md) | Real-world examples and recipes |

## 🔧 Core Features

### 🎛️ Session Management
- **Session Lifecycle** — Create, manage, and delete cloud sandboxes on demand
- **Environment Configuration** — Configure regions, endpoints, and sandbox images
- **Session Monitoring** — Monitor status and health

### 🛠️ Built-in Modules
- **Command Execution** — Run shell commands in cloud sandboxes
- **File Operations** — Upload, download, and manage files
- **Context & Data Persistence** — Save and retrieve data across sessions
- **Git Operations** — Clone, commit, and manage repositories remotely

## 🤖 AI-Assisted Development

If you're using AI coding assistants (Claude, Cursor, GitHub Copilot, etc.) to develop with AgentBay SDK, use these files as context:

- **[llms.txt](./llms.txt)** — Concise overview (~14k tokens, ~55 KB)
- **[llms-full.txt](./llms-full.txt)** — Full SDK source, API docs, and examples (~211k tokens, ~827 KB)

## 🆘 Get Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)

## 📞 Contact

Welcome to visit our product website and join our community!

- 🌐 **AgentBay International Website**: [https://www.alibabacloud.com/product/agentbay](https://www.alibabacloud.com/product/agentbay)
- 🇨🇳 **AgentBay China Website (Chinese)**: [https://www.aliyun.com/product/agentbay](https://www.aliyun.com/product/agentbay)
- 💬 **Discord Community**: [Join on Discord](https://discord.gg/tzX52463Cp)
- 💼 **DingTalk Group**: [Click to join](https://qr.dingtalk.com/action/joingroup?code=v1,k1,ZlCDtu+p3xq2MqVoIA3nYrvEWA21Gq86N91t9OuythQ=&_dt_no_comment=1&origin=11)

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
