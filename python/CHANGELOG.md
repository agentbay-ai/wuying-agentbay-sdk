# Changelog

All notable changes to the Wuying AgentBay SDK will be documented in this file.

## [0.19.0] - 2026-04-16

### Added

- **Git module** (All SDKs): Clone, init, commit, status, log, branch management, diff, and remote operations. Dedicated error types (`GitAuthError`, `GitConflictError`, etc.).
- **Session `appInstanceId`** (All SDKs): Exposed on Session class for tracking cloud instance identity.
- **FileSystem `watch_directory` push mode** (Go, Java, Python): Real-time file monitoring via WebSocket push instead of polling.
- **BrowserOperator** (Go): Added Go BrowserOperator, aligned with other SDKs.

### Changed

- **Deprecated `getLinkUrl` / `getToken`** (All SDKs): Use `linkUrl` / `token` properties instead.
- **FileSystem read/write optimization**: Skip chunking for HTTP LinkUrl channel for better performance.
- **`sync()` exponential backoff** (All SDKs): Polling now uses exponential backoff for more efficient synchronization.

### Fixed

- **Java POP API**: Added automatic retry for transient failures.
- **Java ApiKey**: Fixed null value under concurrent multi-thread access.
- **Java call-for-user**: Fixed platform agent notification not working.
- **FileSystem binary read**: Fixed missing `size` field in `BinaryFileContentResult` for LinkUrl reads.

## [0.18.0] - 2026-03-19

### Added

- **Skills feature (Beta)** (All SDKs): Skills metadata API (`get_metadata`) and session-level skill loading via `skill_ids` parameter in session creation.
- **Agent streaming output (Beta)** (All SDKs): WebSocket-based streaming for agent task execution with `TaskExecution` handle, delivering real-time reasoning and content events via typed callbacks (`on_reasoning`, `on_content`, `on_call_for_user`, `on_error`). Includes `MobileTaskOptions` and `StreamOptions` for structured configuration.

### Breaking Changes

- **MobileUseAgent.execute_task** (All SDKs): Now returns `TaskExecution` instead of `ExecutionResult`. Use `execution.wait(timeout)` to get the result. `ComputerUseAgent` and `BrowserUseAgent` are not affected.

## [0.17.0] - 2026-03-16

### Added

- **run_code WebSocket streaming** (All SDKs): Added WebSocket-based streaming for code execution, enabling real-time output delivery during `run_code` operations.
- **Browser autoLogin & callForUser** (All SDKs): Added `autoLogin` and `callForUser` options for browser sessions, with captcha-solving examples and call-for-user notification channel support.
- **Dynamic context binding** (All SDKs): Support for binding contexts to sessions dynamically at runtime.
- **BrowserSyncMode** (All SDKs): Added `MINIMAL`/`STANDARD` whitelist modes for browser synchronization.
- **Cookbook additions**: 4 new cookbooks (computer use, web scraping, streaming, multi-session), browser login persistence, mobile device simulation, OpenClaw Python/Java web service integration with DingTalk bot and FastAPI, Feishu one-click setup, DingTalk credential auto-apply.

### Changed

- **Removed client-side port range validation** (All SDKs): `getLink` no longer validates port ranges on the client side, deferring to backend enforcement.
- **Logger refactoring** (All SDKs): Replaced direct terminal `print`/`console.log`/`fmt.Print` calls with structured logger calls across Python, TypeScript, Golang, and Java.
- **SSE support for get_link HTTPS URLs**: Added documentation for Server-Sent Events over HTTPS link URLs.

### Fixed

- **watchDirectory race condition** (Python, Golang, TypeScript): Fixed a race condition where file operations performed before the filesystem baseline was established would be lost. Added a "ready" signal mechanism (`ready_event`/`readyCh`/`ready` Promise) so callers can wait for baseline establishment before performing file operations.
- **DirectoryWatcher asyncio event loop isolation** (Python): Fixed asyncio event loop isolation issue in `watch_directory`.
- **TypeScript fixes**: Missing `autoLogin`/`callForUser` params in tests, `toolList` type mismatch in POP SDK models.

### Security

- Dependency updates: Jackson 2.15.2→2.18.6 (Java), npm audit fixes for security vulnerabilities.

## [0.16.0] - 2026-03-02

### Added

- **WebSocket infrastructure** (All SDKs): Persistent WebSocket connections for sessions (`wsUrl`), push notification callbacks (`registerCallback`/`unregisterCallback`), stream cancellation with `WsCancelledError`, and a true synchronous WS client for Python.
- **Session keep-alive & idle release timeout** (All SDKs): Prevent idle timeout disconnections; configurable `idle_release_timeout` in session creation.
- **New API models** (All SDKs): MQTT token, volume operations, skills metadata listing, and official skills sandbox APIs.
- **Java enhancements**: Auto release support, `executeCommand` stdout/stderr separation, browser agent interface unification.
- **Python enhancements**: Browser agent interface unification, page use login API.
- **Screenshot improvements**: Full-page screenshot support, type/mime_type fields, beta long screenshot with JPEG quality.
- **Context sync**: Optional ID filtering for context synchronization.
- **Cookbook**: LangChain DeepAgents skills sandbox; renamed Moltbot to OpenClaw.
- **Developer tools**: Tiered knowledge builder for AI context files; enhanced Config class with defaults.

### Changed

- **Browser Agent → Operator** (All SDKs): Migrated `session.browser.agent` to `session.browser.operator` for unified browser automation interface naming. In Java and Python, `session.browser.agent` is kept as a deprecated alias with a warning; in TypeScript it has been directly replaced.
- **Removed 50s timeout cap on `execute_command`** (All SDKs): The SDK-side 50-second timeout limit has been removed. Custom `timeout_ms` values are now passed through to the backend without capping. Note: the backend gateway may still enforce its own timeout.
- Added managed proxy support, clear API, and removed legacy Java browser config.

### Fixed

- macOS SSL compatibility for WsClient (Python); drop malformed WS messages without invocationId.
- Browser: destroy not resetting params, `get_window` title null, browser.agent crash.
- Mobile: null `link_url` in screenshot, `get_installed_apps` error.
- Pause/Resume for both async and sync APIs; protobuf compatibility; dotenv loading guard.
- Unit test stability improvements across CI.

### Security

- Dependency updates: protobuf 3.20.3→5.29.6, setuptools, urllib3, lodash, axios, js-yaml, next 14.2.33→15.5.10.

## [0.15.0] - 2026-01-24

### Added

#### 🌐 Network (All SDKs)
- **Beta network management APIs**: Introduced beta network lifecycle APIs (create/describe) and `network_id` support in session params.

#### 🔗 MCP Session Routing (All SDKs)
- **LinkUrl routing**: Added LinkUrl-based routing for MCP sessions (tool calls and command execution), with integration tests and examples.
- **MCP agent environment variables**: Support passing environment variables when starting Page Use Agent MCP.

#### 📱 Mobile Beta Screenshot & UI Elements
- **Mobile beta screenshots**: Added beta screenshot APIs (including JSON response handling) and documentation/examples.
- **UI element formats**: Added support for retrieving all UI elements in **JSON/XML** formats.

#### 🧰 Code Assistant Cookbook
- **Code generation & analysis tools**: Added Qwen Code Generator and Mistral Codestral Analyzer packages plus integration guides/scripts for data analysis workflows.

#### 🤖 Agent Module
- **`execute_task` output schema**: Added support for output schema in task execution options across SDKs.

### Changed

#### ⚠️ Breaking Changes
- **Pause/Resume marked as beta**: Renamed `Pause/Resume` to `BetaPause/BetaResume` (and snake_case equivalents) across SDKs to indicate experimental status.
- **VPC routing cleanup**: Removed VPC chain/session params and legacy VPC-only logic; keep LinkUrl direct tool-call path as the unified route.

### Fixed

- **Task timeout correctness**: Fixed task execution timeout handling to wait for task termination.
- **Server recording flag**: Fixed `enableRecord=False` not taking effect (backend behavior exposed via SDK tests).
- **TypeScript docs/code cleanup**: Removed CDATA artifacts and improved import formatting in agent implementation.
- **Java SDK fixes**: Added missing `getMobile` API and updated dependency naming cleanup.

## [0.14.0] - 2026-01-10

### Added

#### ☕ Java SDK
- **Formal Release**: Introduced comprehensive support for the Java SDK, enabling Java developers to build agentic applications.
- **Four Major Environments**: Full support for Browser, Computer, Mobile, and CodeSpace environments.
- **Core Capabilities**: Support for session management, file operations (including `delete_file`), and multi-region configuration.
- **Code Execution**: Enabled `run_code` and `run_command` support within the Java SDK.
- **Observability**: Integrated session metrics and standardized logging.

#### 📱 Mobile Agent
- **Formal Launch**: Introduced the Mobile Agent (Natural Language Task Execution) across Python, TypeScript, Go, and Java SDKs.
- **Natural Language Control**: Support for executing mobile tasks using natural language via `execute_task`.
- **ADB Connection**: Added support for retrieving ADB connection URLs via `get_adb_url`.

#### 📊 Observability & Metrics
- **Session Metrics**: Implemented unified session metrics collection across all SDKs (Python, TypeScript, Go, Java).
- **SLS Logging**: Added support for SLS-formatted logs to improve log analysis capabilities.

#### 🛠️ Core Enhancements
- **CodeSpace Languages**: Added support for **R** and **Java** language execution in CodeSpace.
- **Binary Files**: Added comprehensive support for binary file reading (`read_file`) across all SDKs.
- **Session List Filtering**: Added `status` parameter to `agentbay.list()` for filtering sessions by status (RUNNING, PAUSED, etc.).
- **Ergonomic Aliases**: Introduced API aliases to improve usability and success rates for LLM interactions.

### Changed

#### ⚠️ Breaking Changes
- **Agent Task Execution**: Removed `max_step_retries` parameter. In `execute_task_and_wait`, replaced `max_try_times` with `timeout` (seconds).
- **Filesystem**: Renamed `error` field to `error_message` in `UploadResult` and `DownloadResult` objects.
- **Session API**: Renamed `GetSession` method to `GetStatus` across all SDKs. The old `GetSession` is now internal or removed.

#### Other Changes
- **Documentation**: Added warnings regarding service restrictions for overseas users.

### Fixed

- **File System**: Fixed an MQTT size limit error in `write_file` by optimizing content splitting.
- **Stability**: Resolved various issues related to session status checks, timeouts, and file transfers.
- **CI/CD**: Fixed version file paths and workflow configurations for smoother releases.

## [0.13.0] - 2025-12-19

### Core SDK capabilities (user-visible)

#### 🐍 Python API architecture (migration required)
- **Sync/async split**: Python SDK now provides separate sync and async APIs (`AgentBay` vs `AsyncAgentBay`, etc.).
- **Unified naming**: Removed `_async` suffix from method names; async APIs are `await`-able with the same method names as sync.
- **Unified imports**: Public imports were consolidated under `agentbay`.

#### 🧑‍💻 Code Execution (`run_code`)
- **Rich outputs (backward compatible)**: Added `EnhancedCodeExecutionResult` to support multi-format outputs (HTML/Markdown/images/SVG/LaTeX/charts) while keeping compatibility with `CodeExecutionResult`. (See commit `46cffd02`.)
- **Jupyter-like persistence**: Added docs/examples for long-lived code execution workflows in CodeSpace.

#### 🧾 Command execution
- **Structured outputs**: Standardized command execution outputs to expose `stdout` and `stderr` as explicit fields across SDKs. (See commit `c404ae48`.)
- **Correctness**: Fixed parsing of `exit_code` from command execution responses. (See commit `25d543cb`.)

#### 🤖 Agent module
- **BrowserUseAgent task API**: Introduced/extended task-oriented APIs for BrowserUseAgent. (See commit `c69b3596`.)
- **`execute_task` refinement**: Refined task execution API and updated docs/examples/tests accordingly. (See commit `aa98c5d8`.)

#### 📁 Context filesystem
- **`delete_file` (all languages)**: Added `delete_file` support with tests and examples.
- **Internal context loading**: Switched to `GetAndLoadInternalContext` to avoid incorrect context listing behavior.

#### 🔄 Context sync API
- **`sync_context` → `sync` (breaking)**: Renamed context sync API for consistency across SDKs and removed the legacy alias.

#### 🌍 Multi-region configuration
- **`region_id` support across SDKs**: Added region selection support for Python/TypeScript/Go.

#### 🖥️ Computer & window automation
- **Window API simplification (breaking)**: Removed `timeout` parameter from `get_active_window` across languages.
- **Typed screenshot results (TypeScript)**: `computer.screenshot()` returns a typed `ScreenshotResult`.
- **Cross-platform reliability**: Added/expanded window management integration tests (Python + Go).

#### 📱 Mobile automation
- **Mobile UI bounds**: Added `bounds_rect` support for mobile UI elements (Python), including tests and examples.

#### ☁️ OSS
- **Parameter naming**: Standardized Python OSS client `securityToken` → `security_token` and updated tests/docs.

#### 🐹 Go SDK
- **File transfer**: Added file transfer support in Go SDK with integration tests.
- **Session deletion semantics**: Adjusted delete session flow to align with async deletion API behavior.

### Developer experience (docs & reference)

- **Async programming docs**: Added/updated sync-vs-async comparison and v0.12.x → v0.13.x migration guide.
- **API reference**: Regenerated API docs for Python/TypeScript/Go and improved doc generation metadata filtering.

### Examples & cookbook (end-to-end usage)

- **Mobile login persistence cookbook**: Added `cookbook/mobile/app-login-persistence` examples covering cross-session login state for multiple apps. (See commit `0e47976b`.)
- **NL mobile control cookbook**: Added a LangChain-based NL mobile control example with a web demo and tests.

### Quality, CI, and release tooling

- **Smart integration test workflow**: Added/iterated `.aoneci/smart-integration-test.yaml` (multi-language, improved reporting, AI analysis prompts, and stability improvements).
- **Examples inspection workflow**: Added/iterated `.aoneci/example-check.yaml` (multi-language examples verification with AI analysis and DingTalk notifications).
- **KB preprocessing**: Added/iterated `preprocess_kb` pipeline to generate knowledge-base-friendly docs in batches.
- **llms artifacts**: Updated `llms.txt` / `llms-full.txt` generation workflow and content.

## [0.12.0] - 2025-11-28

### Added

#### 📱 Mobile Simulation
- **Device Simulation Support**: Added support for mobile device simulation features
  - Enhanced mobile testing capabilities
  - Support for simulating various mobile device characteristics

#### ⏸️ Session Pause & Resume
- **Session Control**: Added support for pausing and resuming sessions
  - `pause()` / `pause_async()`: Pause a running session to save resources
  - `resume()` / `resume_async()`: Resume a paused session
  - Available across Python, TypeScript, and Golang SDKs

### Fixed

#### 🐛 Bug Fixes
- **Browser Automation**: Fixed browser-use timeout issues
- **Context Management**: Fixed issue where `get_session` was creating a new context ID instead of returning the real one
- **Context Sync**: Fixed `sync` call to correctly use `context_id` and `path` together
- **Session Control**: Fixed return value handling when pause or resume backend operations fail
- **Local Testing**: Fixed issue preventing browser tests from running locally
- **Python SDK**: Simplified exception log output for cleaner logs
- **Infrastructure**: Updated logo fallback path for Aone compatibility

### Documentation

- **Use Cases**: Improved Use Cases section UX in README
- **Examples**: Updated Quick Start examples to use `CodeSpace` `run_code`
- **General**: Regenerated API documentation and improved code examples
- **Golang**: Added new examples for Golang SDK

## [0.11.0] - 2025-11-18

### Added

#### 🖱️ Browser Fingerprint Persistence
- **Fingerprint Management**: Support for browser fingerprint persistence and customization
  - Local fingerprint file synchronization
  - Custom fingerprint construction
  - Cross-session fingerprint persistence
  - Enhanced browser anti-detection capabilities

#### 📸 Browser Screenshot Enhancement
- **Long Screenshot Support**: Capture full-page screenshots beyond viewport
  - Support for scrolling screenshots
  - Automatic page stitching
  - Network idle waiting for complete rendering

#### 🔄 Cross-Platform Context Sync
- **MappingPolicy**: New policy for cross-platform context synchronization
  - Flexible path mapping between different platforms
  - Support for Windows/Linux/macOS path translation
  - Enhanced context portability

#### 📚 Cookbook Examples
- **E-Commerce Inspector**: Browser automation for e-commerce data extraction and analysis
- **AI Code Assistant**: Code generation and execution in isolated sandbox environment
- **Data Analysis**: Automated data processing and visualization with AI-driven insights

### Changed

#### 🔒 OSS Security Enhancement
- **Breaking Change**: `securityToken` is now required for OSS operations
  - Enhanced security for object storage operations
  - Updated documentation and examples

#### ⌨️ Key Normalization
- **Improved Case Compatibility**: Better handling of key names in `press_keys` tool
  - Automatic case normalization for common keys
  - Support for both uppercase and lowercase key names
  - Consistent behavior across all SDKs

#### 🧹 API Surface Cleanup
- **API Privatization**: Internal APIs marked as private across all SDKs
  - Python: Private methods prefixed with `_`
  - TypeScript: Internal APIs marked as private
  - Golang: Internal packages and unexported functions
  - Cleaner public API documentation
  - Removed deprecated APIs and properties

#### 📖 Documentation Overhaul
- **Comprehensive Documentation Enhancement**: Major documentation improvements
  - Migrated examples from separate docs to source code
  - Metadata-driven documentation generation
  - Inline examples for all public APIs
  - Fixed broken links across all documentation
  - Simplified and clarified API examples
  - Enhanced API reference with comprehensive usage examples

#### 🎯 Session Recovery
- **File Transfer Context**: Automatic context creation for recovered sessions
  - Better handling of session recovery scenarios
  - Improved file transfer reliability

### Fixed

#### 🐛 Bug Fixes
- **SDK Version Reporting**: Fixed version detection in SdkStats module
- **Context Sync**: Removed invalid `sync_id` parameter in ContextSyncResult
- **Session Info**: Handle NotFound errors gracefully with clear error messages
- **Mobile API**: Aligned mobile API naming across SDKs with MCP tool specification
- **UIElement Bounds**: Handle bounds string format correctly in Golang and TypeScript
- **Screenshot Timeout**: Fixed timeout issues caused by network idle waiting
- **Documentation**: Fixed RST code block rendering and markdown formatting issues

### Removed

#### 🗑️ Deprecated APIs
- **Cleanup**: Removed all deprecated APIs and properties
  - Cleaner codebase
  - Reduced maintenance burden
  - Clear upgrade path for users

## [0.10.0] - 2025-10-31

### Added

#### 🤖 AI Context Support
- **AI Coding Assistant Integration**: Added llms.txt and llms-full.txt files for better AI assistant context
  - Comprehensive codebase documentation for AI tools
  - Enhanced development experience with Claude Code and similar assistants
  - Structured project information for better AI understanding

#### 🔧 MCP Tool Enhancement
- **Unified MCP Tool API**: New public API for MCP tool invocation across all SDKs
  - Python: `session.call_mcp_tool(tool, args)` for direct MCP tool calls
  - TypeScript: `session.callMcpTool(tool, args)` for direct MCP tool calls
  - Golang: `session.CallMcpTool(tool, args)` for direct MCP tool calls
  - Simplified tool invocation without manual server discovery
  - Better error handling and response parsing

#### 📊 SDK Statistics & Tracking
- **SDK Stats Module**: Automatic SDK usage tracking and version reporting
  - Auto-detection of SDK version from package metadata
  - Release tracking for Python, TypeScript, and Golang
  - Statistics collection for better service improvement

#### 🗑️ Context Management Enhancement
- **Context Clear API**: New API for clearing context data
  - Python: `context.clear(context_id)` with status polling
  - TypeScript: `context.clear(contextId)` with status polling
  - Golang: `context.Clear(contextId)` with status polling
  - Asynchronous clearing with status monitoring
  - Non-blocking operation with completion detection

#### 🌐 Browser Automation Enhancement
- **Browser Type Selection**: Support for different browser types
  - Choose between Chrome and Chromium browsers
  - `browser_type` option in `BrowserOption` across all SDKs (values: "chrome", "chromium", or None for default)
  - Default browser selection per image type
  - Browser-specific optimization and compatibility

- **Browser Navigation & Arguments**: Enhanced browser initialization
  - `default_navigate_url` parameter for automatic page navigation
  - `cmd_args` parameter for custom browser command line arguments
  - Better control over browser startup behavior

- **Golang Browser Support**: Added full browser automation for Golang SDK
  - `session.Browser` interface matching Python and TypeScript
  - Complete browser API implementation
  - Browser context and page management

#### 📱 Mobile Enhancement
- **ADB Connection URL**: Direct ADB connection support for mobile automation
  - Python: `session.mobile.get_adb_url()` returns ADB connection URL
  - TypeScript: `session.mobile.getAdbUrl()` returns ADB connection URL
  - Golang: `session.Mobile.GetAdbUrl()` returns ADB connection URL
  - Enable external ADB client connections
  - Enhanced mobile automation capabilities

#### 📝 Enhanced Logging System
- **Comprehensive Logging Infrastructure**: Unified logging across all SDKs
  - File logging support with log rotation
  - Environment-based log level configuration (`AGENTBAY_LOG_LEVEL`)
  - API call and response logging with sanitization
  - Process and thread information in async operations
  - Python: loguru-based logging with enhanced formatting
  - TypeScript: winston-based logging with color support
  - Golang: structured logging with context support

#### 📋 Code Execution Enhancement
- **Code Execution Output Logging**: Better visibility for code execution
  - Detailed output logging for `run_code` operations
  - Comprehensive integration tests for code execution
  - Better error reporting and debugging

#### 📄 Data Persistence Enhancement
- **File Compression Support**: Archive mode for data persistence
  - Compress files before upload to reduce storage costs
  - Archive mode configuration in context sync
  - Automatic decompression on download
  - Support for .tar.gz format

### Changed

#### 🔄 Session Link Access Model
- **Breaking Change**: Session Link access changed from whitelist to paid subscription
  - Whitelist-based access deprecated
  - New subscription-based access model
  - Updated documentation with new access requirements

#### 🎨 Browser Context Management
- **Browser Replay Context Sync**: Fixed context synchronization behavior
  - Only sync browser replay context when `sync_context` is explicitly False
  - Better control over context persistence
  - Reduced unnecessary sync operations

#### 📚 Documentation Reorganization
- **Documentation Structure Improvement**: Better organized documentation
  - Updated API documentation links to new directory structure
  - Added custom images guide with comprehensive examples
  - Enhanced session management documentation
  - Added markdown link checker for quality assurance
  - Fixed 166 broken markdown links across documentation
  - Production environment recommendations for image types

### Fixed

#### 🐛 Browser Issues
- **Browser Image ID**: Fixed browser image references
  - Corrected `browser-latest` to `browser_latest` across all SDKs
  - Fixed default browser type values (none/undefined/nil)
  - Fixed browser type example syntax errors
  - Fixed bad reference links in browser API documents
  - Fixed browser page creation to use context 0

#### 🔧 TypeScript Issues
- **ESLint Compliance**: Fixed TypeScript code quality issues
  - Fixed `prefer-const` errors in API client
  - Improved error handling consistency
  - Better code organization

#### 📁 File System Issues
- **File Search Functionality**: Fixed filesystem example issues
  - Corrected file search implementation
  - Better error handling in filesystem operations
  - Fixed OSS sync file deletion issues

#### 📱 Mobile Issues
- **Mobile UI Element Methods**: Aligned mobile.py with ui.py implementation
  - Consistent method signatures across modules
  - Added JSON parsing in `get_clickable_ui_elements`
  - Fixed screenshot saving in automation examples

#### 🧪 Testing Issues
- **Test Case Quality**: Improved test reliability
  - Fixed bad test case design for browser type switching
  - Fixed mobile getAdbUrl unit tests across SDKs
  - Improved pytest configuration and compatibility
  - Fixed BoolResult parameter order in tests

### Documentation

- **Comprehensive Documentation Updates**: Major improvements across all areas
  - Added comprehensive custom images guide
  - Updated data persistence documentation with archive mode
  - Added Windows application management examples
  - Added logging documentation for all SDKs
  - Removed outdated logging and mobile examples docs
  - Added production environment recommendations
  - Updated Session Link access documentation
  - Fixed markdown link issues and emoji anchor compatibility

## [0.9.0] - 2025-10-15

### Added

#### 🎯 Platform-Specific Automation Modules
- **Computer Module**: New dedicated module for desktop/Windows automation across all SDKs
  - Desktop UI interaction APIs: `click_mouse()`, `move_mouse()`, `drag_mouse()`, `press_keys()`, `scroll()`
  - Screen information: `get_screen_size()`, `screenshot()`
  - Integration with MCP tools for advanced automation
  - Python: `session.computer.*`, TypeScript: `session.computer.*`, Golang: `session.Computer.*`
- **Mobile Module**: New dedicated module for Android device automation across all SDKs
  - Touch interaction: `tap()`, `swipe()`, `long_press()`
  - Input methods: `input_text()`, `send_key()` with KeyCode support
  - UI element detection: `get_clickable_ui_elements()`
  - Device configuration: `configure()` for setting device properties
  - Android-only support (mobile_latest image)
  - Python: `session.mobile.*`, TypeScript: `session.mobile.*`, Golang: `session.Mobile.*`

#### 📊 Session Management Enhancement
- **Get Session API**: Retrieve existing session information by session ID
  - Python: `agentbay.get(session_id)` returns `SessionResult`
  - TypeScript: `agentBay.get(sessionId)` returns `SessionResult`
  - Golang: `agentBay.Get(sessionID)` returns `*SessionResult`
  - Returns session object with VPC configuration, network info, and resource URL
  - Non-throwing error handling: check `result.success` and `result.error_message`
- **List Sessions API**: Retrieve paginated list of sessions with label filtering
  - Python: `agentbay.list(labels, page, limit)` returns `SessionListResult`
  - TypeScript: `agentBay.list(labels, page, limit)` returns `SessionListResult`
  - Golang: `agentBay.List(labels, page, limit)` returns `*SessionListResult`
  - Support for page-based pagination (page numbers start from 1)
  - Label filtering with key-value pairs
  - Returns session IDs, total count, and pagination metadata

#### 🗄️ Data Lifecycle Management
- **RecyclePolicy**: Control context data retention lifecycle
  - Lifecycle options: `1day`, `3days`, `5days`, `10days`, `15days`, `30days`, `90days`, `180days`, `360days`, `forever`
  - Path-specific policies: apply different lifecycles to different directories
  - Path validation: wildcard patterns not supported, use exact directory paths
  - Integration with ContextSync for automatic data cleanup
  - Python: `RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_30DAYS, paths=["/data"])`
  - TypeScript: `new RecyclePolicy(Lifecycle.LIFECYCLE_30DAYS, ["/data"])`
  - Golang: `&RecyclePolicy{Lifecycle: Lifecycle_30Days, Paths: []string{"/data"}}`

#### 🔒 VPC Session Authentication Enhancement
- **Token-based Authentication**: VPC sessions now support token authentication
  - Automatic token management for secure VPC session access
  - Token included in session creation response
  - Used for MCP tool calls and resource access in VPC environments

#### 🔧 API Schema Validation
- **MCP Field Validation**: Enhanced MCP tool parameter validation
  - Renamed `schema` to `field_schema` to align with MCP standard
  - Better error messages for invalid tool parameters
  - Improved type checking for tool inputs

### Changed (Breaking Changes)

#### ⚠️ API Response Structure Changes
- **SessionListResult.Sessions Removed**: Breaking change in session list response
  - **Removed**: `SessionListResult.Sessions` field (contained full Session objects)
  - **Use instead**: `SessionListResult.SessionIds` (list of session ID strings)
  - **Rationale**: Reduce response payload size and improve performance
  - **Migration**: Use `agentbay.get(session_id)` to retrieve full Session objects for specific sessions
  - **Before**: `result.Sessions[0].command.execute_command(...)`
  - **After**:
    ```python
    session_id = result.SessionIds[0]
    session_result = agentbay.get(session_id)
    session_result.session.command.execute_command(...)
    ```

#### 🔄 Error Handling Consistency
- **Unified Error Handling**: All APIs now use Result objects instead of raising exceptions
  - `context.get()` returns `ContextResult` (no longer raises `AgentBayError`)
  - `context.create()` returns `ContextResult` (no longer raises `AgentBayError`)
  - **Migration Required**: Replace `try-except AgentBayError` with `if not result.success` pattern
  - All error messages now follow `[ErrorCode] Message` format
  - **Before**:
    ```python
    try:
        result = agentbay.context.get("my-context")
        context = result.context
    except AgentBayError as e:
        print(f"Error: {e}")
    ```
  - **After**:
    ```python
    result = agentbay.context.get("my-context")
    if not result.success:
        print(f"Error: {result.error_message}")
    else:
        context = result.context
    ```

### Deprecated

- **UI Module**: All methods marked for removal in a future version
  - `session.ui.click()` → Use `session.computer.click_mouse()` or `session.mobile.tap()`
  - `session.ui.type()` → Use `session.computer.press_keys()` or `session.mobile.input_text()`
  - `session.ui.mouse_move()` → Use `session.computer.move_mouse()`
  - `session.ui.screenshot()` → Use `session.computer.screenshot()` or `session.mobile.screenshot()`
  - Migration guide: Use platform-specific `computer` or `mobile` modules
- **Window Module**: Some methods deprecated
  - Deprecated methods will be replaced by Computer module equivalents in a future version
- **Context Fields**:
  - `ContextResult.state` marked for removal in a future version
  - `ContextResult.os_type` marked for removal in a future version

### Enhanced

- **Error Messages**: Improved error reporting with structured `[Code] Message` format across all APIs
- **API-level Error Handling**: Enhanced error parsing for `context.get()`, `context.list()`, and `agentbay.create_session()`
- **ContextResult.error_message**: Added for consistent error reporting in context operations
- **ContextListResult.error_message**: Added for consistent error reporting in list operations

### Documentation

- **Documentation Restructure**: Major documentation organization improvements
  - **New Cookbook**: Real-world examples and recipes for common scenarios
  - **Restructured Guides**:
    - Common Features split into Basics, Advanced, and Configuration sections
    - Computer Use guide updated with new Computer module APIs
    - Mobile Use guide updated with new Mobile module APIs and Android-only clarification
    - CodeSpace guide enhanced with code execution examples
  - **API Reference Updates**: Aligned with actual SDK implementation across all three languages
  - **Migration Guides**: Added for breaking changes and deprecated APIs
  - Net documentation changes: +993 lines across 28 new files, 16 modified files, 14 deleted files

### Fixed

- **Documentation Accuracy**: Fixed incorrect iOS support claim in Mobile Use guide (Android only)
- **API Documentation**: Corrected method signatures and return types across all language SDKs
- **Example Code**: All code examples verified against actual SDK implementation

## [0.8.0] - 2025-09-19

### Added

- **Context Sync with Callback Support**: Enhanced context synchronization capabilities
  - **Asynchronous Context Sync**: Added callback-based asynchronous context sync functionality
  - **Synchronous Context Sync**: Support for blocking synchronous context sync operations
  - **Flexible Sync Options**: Two calling modes - with callback for async, without for sync
  - **Context Sync Examples**: Comprehensive examples demonstrating both sync modes
- **Enhanced Logging System**: Upgraded to loguru-based logging infrastructure
  - **File Logging**: Support for logging to files for better debugging and analysis
  - **Environment-based Log Levels**: Configurable log levels via environment variables
  - **Process & Thread Information**: Enhanced log output with process and thread details for async operations
  - **DEBUG Level Support**: More detailed logging information at DEBUG level (default: INFO)
- **Data Persistence Examples**: Comprehensive data persistence examples across all SDKs
  - **Cross-language Examples**: Updated examples for Python, TypeScript, and Golang
  - **Context Management**: Enhanced examples showing context binding and persistence
  - **Session Recovery**: Documentation and examples for session recovery scenarios
- **Browser-Use Documentation**: Complete browser automation documentation suite
  - **Core Features Guide**: Comprehensive documentation for browser context, proxies, stealth mode, extensions, and captcha handling
  - **Advanced Features Guide**: In-depth coverage of PageUse Agent and AI-powered browser interactions
  - **Code Examples**: Practical examples demonstrating browser automation workflows
  - **Integration Guide**: Documentation for seamless integration with community tools and frameworks

### Changed

- **Session Management**: Simplified session interface
  - **Removed resourceUrl**: Eliminated resourceUrl parameter from session creation for cleaner API
  - **Streamlined Session Creation**: Simplified session parameters and initialization
- **Build System**: Modernized Python package management
  - **Removed setup.py**: Transitioned from setup.py to setup.cfg for cleaner package configuration
  - **Poetry Integration**: Enhanced CI/CD with Poetry-based publishing workflows
- **Example Improvements**: Enhanced code quality and consistency across examples
  - **Better Error Handling**: Improved error handling patterns in SDK examples
  - **Parameter Standardization**: Consistent parameter setup across all examples
  - **Code Cleanup**: Improved readability and maintainability of browser examples

### Fixed

- **Browser Cookie Persistence**: Resolved browser cookie persistence issues in examples
  - **CDP Session Management**: Fixed CDP session variable handling in cookie persistence examples
  - **Browser Connection**: Improved browser connection stability for persistent sessions
- **Unit Test Reliability**: Enhanced test stability and coverage
  - **Test Case Updates**: Updated filesystem test cases for better failure scenario handling
  - **Test Consistency**: Fixed unit test failures and improved test reliability
- **Session Parameter Handling**: Fixed session creation parameter issues in automation examples

### Documentation

- **Comprehensive Documentation Updates**: Major improvements across all documentation areas
  - **API Key Usage**: Updated best practices for API key usage and security
  - **Parallel Workflows**: Added examples and documentation for parallel workflow execution
  - **Automation Guides**: Enhanced automation documentation with English translations
  - **Application & Window Management**: Added comprehensive documentation for application and window operations
  - **Session Recovery**: New documentation covering session recovery patterns and best practices
  - **File Operations**: Updated file operations guides with session usage examples
  - **Best Practices**: Enhanced best practices documentation for API key usage and file search results handling

## [0.7.0] - 2025-09-02

### Added

- **AI Browser Extension**: New browser extension capabilities for enhanced automation
  - **Python Extension Support**: Added `extension.py` module for browser extension functionality
  - **TypeScript Extension Support**: Complete extension API implementation with examples
  - **Extension Integration**: Seamless integration with browser automation workflows
  - **Extension Testing**: Comprehensive test coverage for extension functionality
- **Enhanced File System API**: Major improvements to file operations across all SDKs
  - **Streamlined API**: Updated method signatures for better consistency
  - **Session Integration**: Better integration with session management for file operations
  - **Comprehensive Testing**: Expanded test coverage with integration and unit tests
- **Documentation & Guides**: Comprehensive documentation improvements
  - **Large File Handling Guide**: Detailed guide for handling large files efficiently
  - **File Operations Guide**: Updated comprehensive guide with session usage examples
  - **API Documentation**: Complete API reference updates across all SDKs
  - **Usage Examples**: Updated examples and documentation for better developer experience

### Changed

- **File System API**: Breaking changes to improve consistency and usability
  - **Method Naming**: Standardized method names across Python, TypeScript, and Golang SDKs
  - **Return Types**: Enhanced return types for better type safety and error handling
  - **Session Context**: Improved integration with session management for file operations
- **Documentation Structure**: Major documentation reorganization
  - **API Reference**: Updated API documentation to match actual implementation
  - **Command API**: Updated method names and return value references across all documentation
  - **Context Manager**: Enhanced documentation with detailed return object information

### Fixed

- **Browser Automation**: Resolved browser-related issues
  - **Page Variables**: Fixed support for variables in page_use_act functionality
- **Python Package**: Resolved Python-specific issues
  - **Module Imports**: Added missing `__init__.py` in agentbay models directory
  - **API Examples**: Fixed incorrect API usage examples in Python README
- **Test Infrastructure**: Improved test reliability and organization
  - **Test Organization**: Moved test files to appropriate integration directories
  - **Deprecated Tests**: Removed outdated integration tests
  - **Test Coverage**: Enhanced test coverage for new features

### Documentation

- **Comprehensive Updates**: Major documentation improvements across all areas
  - **Getting Started**: Updated quickstart documentation and first session guides
  - **API Reference**: Complete API documentation updates for all modules
  - **Examples**: Updated SDK usage examples and documentation
  - **Guides**: New and updated guides for file operations and large file handling

## [0.6.0] - 2025-08-23

### Added

- **Browser Proxy Support**: New proxy configuration for browser automation across Python and TypeScript
  - **BrowserProxy Class**: Support for custom and wuying proxy types
    - Custom proxy with server, username, password configuration
    - Wuying proxy with "restricted" and "polling" strategies
    - Configurable pool size for polling strategy
  - **Proxy Integration**: Seamless integration with browser initialization
    - Automatic proxy configuration during browser setup
    - Support for both authenticated and anonymous proxy connections
- **Browser Stealth Mode & Fingerprinting**: Enhanced browser automation capabilities
  - **Stealth Mode**: Browser stealth mode support to avoid detection
  - **Browser Fingerprinting**: Configurable browser fingerprint options
    - Custom user agent, viewport, timezone, and locale settings
    - Enhanced privacy and anti-detection capabilities
- **Context File Management APIs**: Complete file operations within contexts across all SDKs
  - **File URL Operations**: Presigned URL support for secure file access
    - `get_file_download_url()` / `GetFileDownloadUrl()` for secure file downloads
    - `get_file_upload_url()` / `GetFileUploadUrl()` for secure file uploads
  - **File Management**: Full CRUD operations for context files
    - `list_files()` / `ListFiles()` with pagination support for context file listing
    - `delete_file()` / `DeleteFile()` for context file deletion
    - Enhanced error handling and response parsing for all file operations
- **Session Management Enhancements**: Improved session creation and management
  - **Policy Support**: Optional `policy_id` parameter in session creation
  - **Session List Response Models**: Enhanced session listing with proper response models
- **Browser Agent Improvements**: Enhanced AI-powered browser interactions
  - **Direct ObserveResult Support**: PageUse act API can now accept ObserveResult directly
  - **TypeScript Browser Agent**: Merged browser agent functionality to TypeScript SDK
  - **Enhanced Parameter Handling**: Improved parameter type conversion and validation
- **Development & Testing Infrastructure**: Enhanced development experience
  - **Pre-commit Hooks**: Added secret detection in pre-commit hooks
  - **Local Benchmark Testing**: Added local benchmark test support for PageUseAgent API
  - **Page Task Framework**: Initial version of page task framework
  - **Auto Publishing**: Enhanced CI/CD with auto publishing workflows

### Changed

- **Browser Configuration**: Enhanced browser setup with advanced options
  - **Breaking Change**: `BrowserOption` now supports proxy, stealth mode, and fingerprinting
  - Automatic proxy validation and configuration during browser initialization
  - Better error handling for proxy connection and stealth mode issues
- **Browser Agent API**: Improved browser automation interface
  - Enhanced parameter naming and validation in ExtractOptions, ObserveOptions, and ActOptions
  - Better timeout handling with default MCP tool call timeout for PageUseAgent
  - Improved error handling and response parsing
- **Context API Enhancement**: Improved context service implementation
  - Enhanced error handling and response parsing across all context operations
  - Better pagination support with `ContextListParams` for large context lists
  - Improved integration with session creation and context synchronization
- **Documentation & Examples**: Updated documentation and examples
  - Updated Python examples with session params
  - Aligned TypeScript examples with latest API changes
  - Updated README and examples documentation

### Fixed

- **Browser VPC Environment**: Resolved VPC-specific browser issues
  - Fixed browser endpoint URL population for VPC environment
  - Better CDP endpoint management for VPC and non-VPC sessions
- **Browser Agent API**: Enhanced browser automation reliability
  - Fixed parameter type conversion in observation API
  - Fixed bad naming in browser agent methods and options
  - Improved error handling for browser agent operations
- **PageUseAgent Integration**: Resolved PageUseAgent API issues
  - Fixed run_sudoku functionality
  - Aligned examples with latest PageUseAgent API revision
  - Fixed benchmark test integration with PageAgent
- **Context File Operations**: Enhanced context file management reliability
  - Fixed presigned URL generation and expiration handling
  - Improved file listing pagination and response parsing
  - Better error handling for file upload/download operations
- **Cross-Platform Compatibility**: Improved SDK consistency
  - Standardized method signatures across Python, TypeScript, and Golang
  - Fixed async/await patterns in TypeScript and Python implementations
  - Better error handling and response structure consistency

## [0.5.0] - 2025-08-06

### Added

- **Browser Automation & AI Browser**: Comprehensive browser automation capabilities with AI-powered interactions
  - AIBrowser interface with Playwright integration
  - Browser Context for persistent data across sessions (cookies, local storage, session storage)
  - Browser Agent with natural language operations (Act, Observe, Extract)
  - Support for complex web automation tasks through Agent module integration
- **VPC Session Support**: Enhanced security and networking capabilities
  - VPC-based session creation with `is_vpc` parameter
  - Specialized system tools (get_resource, system_screenshot, release_resource)
  - Browser tools availability in VPC sessions (cdp, pageuse-mcp-server, playwright)
  - Network isolation for sensitive operations
- **Agent Module**: AI-powered task execution framework
  - Natural language task execution with `ExecuteTask()` method
  - Task status monitoring and management
  - Task termination capabilities
  - Integration with browser automation for complex web operations
- **Unified MCP Tool Interface**: Standardized tool calling mechanism across all modules
  - `CallMcpTool()` method for unified tool invocation
  - Support for both VPC and non-VPC tool calling patterns
  - Automatic server discovery for tools
  - Enhanced error handling and debugging capabilities
- **Comprehensive Interface Architecture**: Complete interface definitions for better modularity
  - FileSystemInterface, SessionInterface, WindowInterface, ApplicationInterface
  - CommandInterface, CodeInterface, UIInterface, OSSInterface
  - AgentBayInterface for main client operations
  - Mock generation support for all interfaces
- **Enhanced Context Management**: Improved context synchronization and pagination
  - Context list pagination with `ListContexts` API
  - Enhanced context binding and persistence
  - Better error handling for context operations
- **Quality Assurance Infrastructure**: Automated quality check scripts for all languages
  - One-click quality check scripts (`quality-check.sh`) for Python, TypeScript, and Golang
  - Comprehensive linting, formatting, and security scanning
  - Automated unit and integration testing
  - CI/CD integration support
- **Documentation & Examples**: Comprehensive documentation and example improvements
  - Agent module documentation and examples for all languages
  - VPC session tutorials and API reference
  - Browser automation architecture documentation
  - AI-powered web interactions tutorial
  - Updated API reference with new modules and interfaces

### Changed

- **Architecture Refactoring**: Major structural improvements for better maintainability
  - Interfaces-first design with dependency injection
  - Removal of circular dependencies between modules
  - Unified MCP tool calling across all components
- **Session Management**: Enhanced session capabilities and VPC support
  - VPC session detection and handling
  - Network interface IP and HTTP port management for VPC sessions
  - Improved session lifecycle management
- **Error Handling**: Improved error handling and logging across all SDKs
  - Better error messages for VPC configuration issues
  - Enhanced debugging information with request IDs
  - Sanitized error reporting for security
- **Testing Infrastructure**: Significantly expanded test coverage
  - Comprehensive unit tests for all modules
  - Integration tests for VPC sessions and browser automation
  - API-level comprehensive testing for command and filesystem operations
- **Module Separation**: Code execution moved from Command to dedicated Code module
  - `RunCode` method moved from Command module to Code module
  - Clear separation of concerns between shell commands and code execution
  - Improved API consistency across all language implementations

### Fixed

- **VPC Session Compatibility**: Fixed issues with VPC-based tool calling
  - Proper HTTP endpoint construction for VPC sessions
  - Network configuration validation
  - Server discovery for VPC environments
- **Browser Context Persistence**: Fixed browser data persistence across sessions
  - Cookie synchronization improvements
  - Context cleanup on session termination
  - Resource management for browser instances
- **Interface Consistency**: Fixed inconsistencies across language implementations
  - Standardized method signatures across Python, TypeScript, and Golang
  - Consistent error handling patterns
  - Unified response structures

### Security

- **Enhanced Security Scanning**: Improved security measures across all SDKs
  - Dependency vulnerability scanning with pip-audit, npm audit, and govulncheck
  - Code security analysis with bandit, snyk, and gosec
  - Secure credential handling for VPC sessions
- **Network Isolation**: VPC sessions provide enhanced security through network isolation
  - Private network environments for sensitive operations
  - Controlled access policies
  - Secure resource access patterns

## [0.4.0] - 2025-07-18

### Added

- **Enhanced Configuration**: Support for setting SDK configuration via three methods (environment variables, config files, code parameters) in Python, Golang, and TypeScript.
- **API Response Improvements**: All API responses now include a `request_id` field for better traceability and debugging.
- **Session Label Pagination**: `listByLabels` now supports pagination parameters.
- **GetLink API**: Added support for specifying protocol type and port when retrieving links.
- **OSS Persistence**: Added support for persistent storage with OSS.
- **Ticket Parameter**: Some APIs now support a ticket parameter.
- **Context Sync & Management**: Introduced context manager and context sync APIs and implementations.
- **Automated Quality Scripts**: Added one-click quality check scripts (lint/format/security scan) and multi-language automated testing.
- **Comprehensive Unit & Integration Tests**: Significantly expanded and improved tests for TypeScript, Go, and Python SDKs.
- **Documentation Restructure**: API reference is now split by language, with many new tutorials and examples.
- **Type/Interface Enhancements**: Many new interfaces and type definitions for better IDE support across Golang, TypeScript, and Python.

### Changed

- **API Compatibility**: Standardized some API parameters and response formats.
- **Error Handling**: Improved error handling and logging across SDKs.
- **Default Timeout**: Default timeout changed to 60 seconds.
- **Documentation**: Major updates to README, Getting Started, API Reference, and Tutorials.
- **Code Structure**: Refactored directory structure; examples, tests, and scripts are now modularized.

### Fixed

- **Session Deletion/Management**: Fixed issues with session deletion and state management.
- **File System**: Fixed issues with large file chunking and read/write consistency.
- **Unit Tests**: Fixed compatibility and edge cases in multi-language unit tests.
- **CI/CD**: Fixed cross-platform line endings and environment variable loading issues.
- **API Responses**: Fixed incomplete response structures in some APIs.

## [0.3.0] - 2025-06-16

### Added

- **Session Labels**: Added support for organizing and filtering sessions with labels
  - Set and get session labels
  - List sessions by label filters
- **Code Execution**: Added support for running code in multiple languages (Python, JavaScript, etc.)
- **Window Management**: 
  - Added support for listing, activating, and manipulating windows
  - Window resizing, focusing, and positioning
  - Get window properties and child windows
- **OSS Integration**: Added Object Storage Service functionality
  - File upload/download to/from OSS buckets
  - Anonymous upload/download via URLs
  - OSS environment initialization
- **Context Management**: 
  - Create, list, and delete contexts
  - Bind sessions to contexts for persistence
  - Get context information
- **UI Enhancement**: 
  - Added support for screenshots
  - UI element detection and interaction
  - Mobile-specific operations (click, swipe, send keys)
- **Enhanced Image ID Support**: Added ability to specify custom image IDs when creating sessions
- **Application Management**: Added support for listing, launching, and stopping applications

### Changed

- Updated API client to support the latest AgentBay backend features
- Improved error handling and reporting across all SDK components
- Enhanced documentation with examples for new features
- Enhanced TypeScript type definitions for better IDE support
- Standardized response formats across all operations

### Fixed

- Various bug fixes and performance improvements
- Type compatibility issues in filesystem operations
- Session management edge cases
- Command execution timeouts
- File reading/writing inconsistencies

## [0.1.0] - 2025-05-15

### Added

- **Core SDK Implementation**: Initial implementation for Python, TypeScript, and Golang
- **Session Management**: 
  - Create, list, and delete sessions
  - Get session information
- **Command Execution**: 
  - Execute basic shell commands
- **Basic File Operations**: 
  - Read and write files
  - Create and delete directories
  - List directory contents
- **Authentication**: API key-based authentication
- **Configuration**: Environment-based configuration
- **Documentation**: Initial API reference and examples
