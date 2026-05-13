# Common Features Examples

This directory contains examples demonstrating features available across all AgentBay environment types (browser, computer, mobile, and codespace).

## Directory Structure

```
common-features/
├── basics/          # Fundamental features for all users
└── advanced/        # Advanced features and integrations
```

## Basics

Essential features that every AgentBay user should know:

### [session_operations](basics/session_operations/)
Session lifecycle management examples:
- Creating sessions with default parameters
- Session creation with labels and context
- Getting session link URLs
- Label management (CRUD + filtering)
- Keep-alive operations

### [session_get](basics/session_get/)
Session retrieval:
- Getting session by ID
- Session information retrieval

### [session_pause_resume](basics/session_pause_resume/)
Session pause and resume operations

### [command_operations](basics/command_operations/)
Command execution patterns:
- Executing shell commands
- Command output handling

### [pty_operations](basics/pty_operations/)
PTY terminal operations:
- Interactive terminal sessions
- Command streaming

### [file_system](basics/file_system/)
File operations in cloud environments:
- Reading and writing files
- Directory operations
- File transfer between local and cloud
- Directory monitoring and change detection

### [context_management](basics/context_management/)
Context creation and management:
- Creating and managing contexts
- Data storage and retrieval
- Cross-session data sharing
- Paginated context listing

### [context_file_transfer](basics/context_file_transfer/)
Context-based file transfer:
- Upload/download files via presigned URLs
- Upload/download directories

### [data_persistence](basics/data_persistence/)
Data persistence across sessions:
- SyncPolicy and RecyclePolicy configuration
- Archive upload mode
- BWList (whitelist/blacklist) filtering
- Context synchronization demonstration

### [dynamic_context_binding](basics/dynamic_context_binding/)
Dynamic context binding:
- Binding contexts to sessions at runtime

### [env_management](basics/env_management/)
Environment management:
- Environment variable configuration

### [mcp_tool_direct_call](basics/mcp_tool_direct_call/)
MCP tool direct calls:
- Invoking MCP tools directly

## Advanced

Advanced features for power users and integrations:

### [agent_module](advanced/agent_module/)
AI-powered automation:
- Using Agent for task execution
- Natural language task descriptions
- Intelligent automation workflows

### [oss_management](advanced/oss_management/)
Object Storage Service integration:
- OSS environment initialization
- File upload to OSS
- File download from OSS
- Anonymous upload/download

### [screenshot_download](advanced/screenshot_download/)
Screenshot capture and download:
- Taking screenshots
- Downloading screenshots locally
- Image format handling

### [session_metrics](advanced/session_metrics/)
Session metrics and monitoring:
- Collecting session usage metrics
- Performance tracking

### [link_url_session](advanced/link_url_session/)
Link URL session management:
- Using link URLs for session access

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run any example
cd basics/session_creation
python main.py

cd ../file_system
python main.py
```

## Usage

Each subdirectory contains specific examples with detailed documentation. Check the individual README files and Python scripts for complete usage examples.

## Best Practices

1. **Always Clean Up**: Delete sessions when done to free resources
2. **Error Handling**: Check `result.success` before using data
3. **Use Labels**: Organize sessions with meaningful labels
4. **Context Sync**: Use context synchronization for data persistence
5. **Resource Limits**: Be aware of concurrent session limits

## Related Documentation

- [Session Management Guide](../../../../../docs/guides/common-features/basics/session-management.md)
- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md)
- [Data Persistence Guide](../../../../../docs/guides/common-features/basics/data-persistence.md)
- [Agent Modules Guide](../../../../../docs/guides/common-features/advanced/agent-modules.md)

## Troubleshooting

### Resource Creation Delay

If you see "The system is creating resources" message:
- Wait 90 seconds and retry
- This is normal for resource initialization
- Consider using session pooling for production

### API Key Issues

Ensure your API key is properly set:
```bash
export AGENTBAY_API_KEY=your_api_key_here
# Verify
echo $AGENTBAY_API_KEY
```

### Context Synchronization Timeout

For large contexts:
- Increase timeout settings
- Use selective synchronization
- Consider splitting into smaller contexts

