# AgentBay Python SDK API Reference

This directory contains auto-generated API reference documentation.

## Quick Links

- [📁 Synchronous API (`sync/`)](#synchronous-api)
- [⚡ Asynchronous API (`async/`)](#asynchronous-api)
- [📦 Common Classes (`common/`)](#common-classes)

## Synchronous vs Asynchronous

AgentBay provides both synchronous and asynchronous APIs with identical interfaces:

| Feature | Sync API | Async API |
|-|-|-|
| **Use Case** | Simple scripts, linear workflows | Concurrent operations, high performance |
| **Performance** | Sequential execution | 4-6x faster for parallel tasks |
| **Syntax** | `result = agent.create()` | `result = await agent.create()` |
| **Import** | `from agentbay import AgentBay` | `from agentbay import AsyncAgentBay` |

See [Synchronous vs Asynchronous Guide](../guides/async-programming/sync-vs-async.md) for detailed comparison.

---

## Synchronous API

All synchronous API classes are in the `sync/` directory:

- [AgentBay](sync/agentbay.md) - `agentbay.agentbay`
- [Network](sync/network.md) - `agentbay.beta_network`
- [Session](sync/session.md) - `agentbay.session`
- [Command](sync/command.md) - `agentbay.command`
- [Context](sync/context.md) - `agentbay.context`
- [Context Manager](sync/context-manager.md) - `agentbay.context_manager`
- [File System](sync/filesystem.md) - `agentbay.filesystem`
- [Agent](sync/agent.md) - `agentbay.agent`
- [OSS](sync/oss.md) - `agentbay.oss`
- [Browser](sync/browser.md) - `agentbay.browser`
- [BrowserOperator](sync/browser-operator.md) - `agentbay.browser_operator`
- [Extension](sync/extension.md) - `agentbay.extension`
- [Code](sync/code.md) - `agentbay.code`
- [Computer](sync/computer.md) - `agentbay.computer`
- [Mobile](sync/mobile.md) - `agentbay.mobile`
- [BrowserFingerprint](sync/fingerprint.md) - `agentbay.fingerprint`
- [MobileSimulate](sync/mobile-simulate.md) - `agentbay.mobile_simulate`
- [SessionParams](sync/session-params.md) - `agentbay.agentbay._common.params.session_params`
- [Git](sync/git.md) - `agentbay.git.git`
- [Pty](sync/pty.md) - `agentbay.pty`

## Asynchronous API

All asynchronous API classes are in the `async/` directory:

- [AsyncAgentBay](async/async-agentbay.md) - `agentbay.agentbay`
- [AsyncNetwork](async/async-network.md) - `agentbay.beta_network`
- [AsyncSession](async/async-session.md) - `agentbay.session`
- [AsyncCommand](async/async-command.md) - `agentbay.command`
- [AsyncContext](async/async-context.md) - `agentbay.context`
- [AsyncContextManager](async/async-context-manager.md) - `agentbay.context_manager`
- [AsyncFileSystem](async/async-filesystem.md) - `agentbay.filesystem`
- [AsyncAgent](async/async-agent.md) - `agentbay.agent`
- [AsyncOss](async/async-oss.md) - `agentbay.oss`
- [AsyncBrowser](async/async-browser.md) - `agentbay.browser`
- [AsyncBrowserOperator](async/async-browser-operator.md) - `agentbay.browser_operator`
- [AsyncExtension](async/async-extension.md) - `agentbay.extension`
- [AsyncCode](async/async-code.md) - `agentbay.code`
- [AsyncComputer](async/async-computer.md) - `agentbay.computer`
- [AsyncMobile](async/async-mobile.md) - `agentbay.mobile`
- [AsyncBrowserFingerprint](async/async-fingerprint.md) - `agentbay.fingerprint`
- [AsyncMobileSimulate](async/async-mobile-simulate.md) - `agentbay.mobile_simulate`
- [AsyncSessionParams](async/async-session-params.md) - `agentbay.agentbay._common.params.session_params`
- [AsyncGit](async/async-git.md) - `agentbay.git.git`
- [AsyncPty](async/async-pty.md) - `agentbay.pty`

## Common Classes

Shared classes used by both sync and async APIs are in the `common/` directory:

- [Configuration](common/config.md) - `agentbay._common.config`
- [Exceptions](common/exceptions.md) - `agentbay._common.exceptions`
- [Logging](common/logging.md) - `agentbay._common.logger`
- [Context Sync](common/context-sync.md) - `agentbay._common.params.context_sync`
- [Code Execution Models](common/code-models.md) - `agentbay._common.models.code`
- [Browser Models](common/browser-models.md) - `agentbay._common.models.browser`
- [Response Models](common/response-models.md) - `agentbay._common.models.response`
- [Browser Operator Models](common/browser-operator-models.md) - `agentbay._common.models.browser_operator`

---

**Note**: This documentation is auto-generated from source code. Run `python scripts/generate_api_docs.py` to regenerate.