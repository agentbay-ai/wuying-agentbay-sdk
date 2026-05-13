# Codespace Examples

This directory contains examples demonstrating code execution capabilities in AgentBay SDK.

## Overview

Codespace environment (`linux_latest` image) provides cloud-based code execution with:
- Python, JavaScript, R, and Java runtime support
- File system operations
- Command execution
- Package installation and management
- Development environment setup

## Examples

### Code Execution
- **code_execution_example.py**: Basic Python and JavaScript code execution
- **enhanced_code_execution.py**: Advanced code execution with streaming and error handling
- **run_code_streaming_beta.py**: WS streaming stdout/stderr for `run_code()` (beta, async-only)
- **jupyter_context_persistence.py**: Jupyter-like Python context persistence across consecutive `run_code()` calls within the same session
- **jupyter_context_persistence_r_java.py**: Jupyter-like R and Java context persistence across consecutive `run_code()` calls within the same session
- **python_development.py**: Python development workflow
- **nodejs_development.py**: Node.js development setup
- **web_server_setup.py**: Web server configuration

### File Operations
- **file_compression.py**: File compression and archiving
- **text_processing.py**: Text file processing operations

### System Operations
- **system_monitoring.py**: System resource monitoring
- **git_operations.py**: Git repository management
- **database_operations.py**: Database setup and operations

### Build and Automation
- **build_automation.py**: Automated build processes

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run any example
python code_execution_example.py
```

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.code.run_code()` | Execute Python, JavaScript, R, or Java code |
| `session.file_system.write_file()` | Write content to a file |
| `session.file_system.read_file()` | Read content from a file |
| `session.command.execute_command()` | Execute shell commands |

## Common Use Cases

### Development Workflows
- Set up development environments
- Install packages and dependencies
- Run automated tests
- Build and deploy applications

### Data Processing
- Process large datasets
- Run data analysis scripts
- Generate reports and visualizations

### Automation Tasks
- Automated testing and CI/CD
- System administration tasks
- File processing and manipulation

## Best Practices

1. **Environment Setup**: Install required packages before running code
2. **Error Handling**: Check execution results for errors
3. **Resource Management**: Clean up temporary files and processes
4. **Security**: Avoid executing untrusted code
5. **Performance**: Consider memory and CPU usage for large operations

## Related Documentation

- [Codespace Guide](../../../../../docs/guides/codespace/code-execution.md)
- [File Operations Guide](../../../../../docs/guides/common-features/basics/file-operations.md)
- [Command Execution Guide](../../../../../docs/guides/common-features/basics/command-execution.md)

## Troubleshooting

### Code Execution Fails
- Check syntax errors in the code
- Verify required packages are installed
- Check memory and timeout limits

### Package Installation Issues
- Use correct package manager (pip for Python, npm for Node.js)
- Check network connectivity
- Verify package names and versions

### File Permission Issues
- Ensure proper file permissions
- Use appropriate file paths
- Check disk space availability