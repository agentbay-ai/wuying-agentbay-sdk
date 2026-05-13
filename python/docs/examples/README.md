# AgentBay Python SDK Examples

This directory contains comprehensive examples demonstrating various features of the AgentBay Python SDK.

## Directory Structure

```
examples/
├── _async/          # Async examples (Source of Truth)
│   ├── browser-use/
│   ├── codespace/
│   ├── common-features/
│   ├── computer-use/
│   └── mobile-use/
└── _sync/           # Sync examples (Auto-generated)
    ├── browser-use/
    ├── codespace/
    ├── common-features/
    ├── computer-use/
    └── mobile-use/
```

## About Async/Sync Versions

- **`_async/`**: Contains asynchronous examples using `AsyncAgentBay` and `async/await` syntax
- **`_sync/`**: Contains synchronous examples using `AgentBay` (auto-generated from async versions)

Both versions provide the same functionality. Choose based on your project requirements:
- Use **async** for modern async/await applications
- Use **sync** for traditional synchronous applications

## Example Categories (in _async/ and _sync/ directories)

### 1. Browser-use Examples

Located in `browser-use/browser/` and `browser-use/extension/`

**Basic Browser Operations:**
- `browser_screenshot.py` - Taking screenshots
- `browser_viewport.py` - Managing viewport sizes
- `browser_type_example.py` - Different browser types

**Navigation and Interaction:**
- `navigation_and_interaction.py` - Browser navigation and element interaction
- `page_analysis.py` - Page metadata and content extraction
- `multi_tab_management.py` - Managing multiple browser tabs

**Advanced Browser Features:**
- `javascript_execution.py` - Executing JavaScript in browser context
- `authentication_flow.py` - Handling authentication and login flows
- `responsive_testing.py` - Testing responsive design across viewports
- `network_monitoring.py` - Monitoring network requests and responses
- `popup_handling.py` - Managing popups and dialogs
- `iframe_handling.py` - Working with iframes

**File Operations:**
- `file_upload_download.py` - File upload/download operations

**Browser Automation:**
- `form_automation.py` - Automated form filling
- `web_scraping.py` - Web scraping techniques
- `cookies_management.py` - Cookie management
- `local_storage_management.py` - Local storage operations
- `screenshot_comparison.py` - Screenshot comparison

**Browser Configuration:**
- `browser_fingerprint_*.py` - Browser fingerprinting
- `browser_context_cookie_persistence.py` - Cookie persistence
- `browser-proxies.py` - Proxy configuration
- `browser_command_args.py` - Browser command arguments
- `browser_replay.py` - Browser session replay

**Extension Development:**
- `basic_extension_usage.py` - Basic extension usage
- `extension_development_workflow.py` - Extension development
- `extension_testing_automation.py` - Extension testing

**Real-world Examples:**
- `search_agentbay_doc*.py` - Documentation search examples
- `game_*.py` - Game automation examples

### 2. Codespace Examples

Located in `codespace/`

- `python_development.py` - Python environment setup and package management
- `nodejs_development.py` - Node.js environment and npm operations
- `git_operations.py` - Git repository initialization and commits
- `database_operations.py` - SQLite database operations
- `text_processing.py` - Text manipulation with grep/sed/awk
- `system_monitoring.py` - System resource monitoring
- `file_compression.py` - File compression and archiving
- `web_server_setup.py` - HTTP server setup and configuration
- `build_automation.py` - Build automation with Makefiles
- `code_execution_example.py` - Code execution patterns
- `enhanced_code_execution.py` - Advanced code execution with streaming
- `jupyter_context_persistence.py` - Jupyter-like Python context persistence
- `jupyter_context_persistence_r_java.py` - R/Java context persistence
- `run_code_streaming_beta.py` - Streaming code execution (beta)

### 3. Common-features Examples

Located in `common-features/basics/` and `common-features/advanced/`

**Session Operations (`basics/session_operations/`):**
- `session_creation.py` - Creating sessions with various configurations
- `session_link_example.py` - Getting session link URLs
- `session_label_management.py` - Managing session labels (CRUD + filtering)
- `session_keep_alive.py` - Keeping sessions alive

**Session Management (`basics/`):**
- `session_get/` - Getting session by ID
- `session_pause_resume/` - Pausing and resuming sessions

**Command & PTY (`basics/`):**
- `command_operations/` - Command execution patterns
- `pty_operations/` - PTY terminal operations

**File System (`basics/file_system/`):**
- `basic_file_operations_example.py` - File read/write/list operations
- `file_transfer_example.py` - Session-based file upload/download
- `watch_directory_example.py` - File change monitoring

**Context & Data Persistence (`basics/`):**
- `context_management/` - Context CRUD, listing with pagination, session binding
- `context_file_transfer/` - Context-based file transfer via presigned URLs
- `data_persistence/` - SyncPolicy, RecyclePolicy, Archive mode, BWList
- `dynamic_context_binding/` - Dynamic context binding during session

**Environment (`basics/`):**
- `env_management/` - Environment variable management
- `environment_operations/` - Environment operations

**Other (`basics/`):**
- `mcp_tool_direct_call/` - MCP tool direct calls

**Advanced Features (`advanced/`):**
- `agent_module/` - Agent module usage
- `batch_operations/` - Batch operations
- `error_handling/` - Comprehensive error handling
- `link_url_session/` - Link URL session management
- `logging_monitoring/` - Logging and monitoring
- `multi_session_management/` - Multi-session coordination
- `network_testing/` - Network diagnostics
- `oss_management/` - OSS operations
- `parallel_execution/` - Parallel execution patterns
- `performance_monitoring/` - Performance monitoring
- `retry_mechanism/` - Retry patterns with circuit breaker
- `screenshot_download/` - Screenshot operations
- `session_metrics/` - Session metrics
- `session_pooling/` - Session pooling for efficiency
- `environment_variables/` - Environment variable management

### 4. Computer-use Examples

Located in `computer-use/computer/`

- `screen_operations.py` - Screenshot capture using `computer.beta_take_screenshot()`
- `windows_app_management_example.py` - Windows application management

### 5. Mobile-use Examples

Located in `mobile-use/`

- `mobile_agent_streaming.py` - Mobile Agent task execution with streaming output
- `mobile_app_operations.py` - Mobile app operations
- `mobile_beta_screenshot.py` - Mobile screenshot capture
- `mobile_bounds_rect.py` - Mobile UI bounds/rect operations
- `mobile_get_adb_url_example.py` - Getting ADB connection URL
- `mobile_simulate_basic_usage.py` - Mobile simulate basic usage
- `mobile_simulate_with_ctx.py` - Mobile simulate with context
- `mobile_ui_automation.py` - Mobile UI automation
- `mobile_system/` - Mobile system operations
- `get_all_ui_elements_xml/` - Get all UI elements as XML

## Getting Started

### Prerequisites

```bash
pip install agentbay
```

### Running Examples

**Async version:**
```bash
python python/docs/examples/_async/codespace/python_development.py
```

**Sync version:**
```bash
python python/docs/examples/_sync/codespace/python_development.py
```

### Environment Variables

Most examples require the `AGENTBAY_API_KEY` environment variable:

```bash
export AGENTBAY_API_KEY="your_api_key_here"
```

## Example Template

### Async Example Template

```python
import asyncio
from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams

async def main():
    client = AsyncAgentBay()
    session = None

    try:
        # Create session
        session_result = await client.create(
            CreateSessionParams(image_id="linux_latest")
        )
        session = session_result.session

        # Your code here
        result = await session.command.execute_command("echo 'Hello'")
        print(result.output)

    finally:
        if session:
            await client.delete(session)

if __name__ == "__main__":
    asyncio.run(main())
```

### Sync Example Template

```python
from agentbay import AgentBay
from agentbay import CreateSessionParams

def main():
    client = AgentBay()
    session = None

    try:
        # Create session
        session_result = client.create(
            CreateSessionParams(image_id="linux_latest")
        )
        session = session_result.session

        # Your code here
        result = session.command.execute_command("echo 'Hello'")
        print(result.output)

    finally:
        if session:
            client.delete(session)

if __name__ == "__main__":
    main()
```

## Contributing

When adding new examples:

1. **Always create async version first** in `_async/` directory
2. **Run the generation script** to create sync version:
   ```bash
   cd python
   make generate-examples-sync
   ```
3. **Verify both versions** work correctly
4. **Update this README** with the new example

## Maintenance

The sync examples are auto-generated from async examples. To regenerate:

```bash
cd python
python scripts/generate_sync.py
```

Or use the Makefile:

```bash
cd python
make generate-examples-sync
```

## Need Help?

- Check the [API Documentation](../api/)
- Visit the [Guides](../../../docs/guides/)
- See the [Quickstart](../../../docs/quickstart/)

## License

These examples are part of the AgentBay SDK and follow the same license.
