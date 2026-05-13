# Computer Use Examples

This directory contains examples demonstrating Windows desktop automation capabilities in AgentBay SDK.

## Overview

Computer Use environment (`windows_latest` image) provides cloud-based Windows desktop automation with:
- Application management (start, stop, list)
- Window operations (maximize, minimize, resize, close)
- Focus management
- Desktop UI automation workflows
- Process monitoring

## Examples

### screen_operations.py

Screenshot capture example demonstrating:
- Using `computer.beta_take_screenshot()` API to capture screen
- Saving screenshots to local files (JPG format)
- Uses `linux_latest` image (no GUI required for screenshot API)

### windows_app_management_example.py

Comprehensive Windows application management example demonstrating:

1. **Finding Installed Applications**
   - Discover all applications in Windows start menu
   - Filter system applications
   - Search for specific applications

2. **Launching Applications**
   - Start applications by command
   - Monitor spawned processes
   - Track process IDs

3. **Monitoring Running Applications**
   - List currently visible applications
   - Get application window information
   - Track application states

4. **Stopping Applications**
   - Stop by process ID (PID)
   - Stop by process name
   - Graceful termination

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the example
cd computer
python windows_app_management_example.py
```

## Features Demonstrated

### Application Discovery
- Find installed applications in start menu
- Filter system applications
- Search by application name
- Get application start commands

### Process Management
- Start applications by command
- Monitor process creation
- Track process IDs and names
- List visible applications with windows

### Application Control
- Stop applications by PID
- Stop applications by process name
- Graceful vs forceful termination
- Error handling for process operations

### Window Operations
- List all windows
- Focus specific windows
- Maximize/minimize windows
- Close windows
- Get window information

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.computer.get_installed_apps()` | Get list of installed applications |
| `session.computer.start_app()` | Start an application |
| `session.computer.list_visible_apps()` | List currently visible applications |
| `session.computer.stop_app_by_pid()` | Stop application by process ID |
| `session.computer.stop_app_by_pname()` | Stop application by process name |
| `session.window.list_windows()` | List all windows |
| `session.window.focus_window()` | Focus a specific window |
| `session.window.maximize_window()` | Maximize a window |
| `session.window.minimize_window()` | Minimize a window |
| `session.window.close_window()` | Close a window |
| `session.ui.screenshot()` | Take a screenshot |
| `session.ui.click()` | Click at coordinates |
| `session.ui.type()` | Type text |
| `session.ui.key()` | Send keyboard key |

## Common Use Cases

### 1. Automated Testing
- Start application and wait for window
- Interact with UI elements
- Verify results with screenshots

### 2. Application Monitoring
- Monitor running applications
- Track application lifecycle
- Performance monitoring

### 3. Automated Workflows
- Open applications in sequence
- Perform data entry tasks
- Generate reports and save files

## Best Practices

1. **Wait for Application Load**: Add delays after starting applications
2. **Error Handling**: Always check `result.success` before proceeding
3. **Resource Cleanup**: Stop applications and delete sessions when done
4. **Process Identification**: Use PIDs for reliable process management
5. **Retry Logic**: Implement retries for resource creation delays
6. **Window Focus**: Ensure window has focus before UI interactions
7. **Screenshot Verification**: Use screenshots to verify UI state

## Related Documentation

- [Computer Use Guide](../../../../../docs/guides/computer-use/README.md)
- [Computer Application Management](../../../../../docs/guides/computer-use/computer-application-management.md)
- [Computer UI Automation](../../../../../docs/guides/computer-use/computer-ui-automation.md)
- [Window Management](../../../../../docs/guides/computer-use/window-management.md)

## Troubleshooting

### Resource Creation Delay

If you see "Resource creation in progress" message:
- Wait 90 seconds and retry
- This is normal for Windows session initialization
- Consider session pooling for production

### Application Not Found

If application is not in the list:
- Check application is installed in start menu
- Try using full path to executable
- Verify application name spelling

### Application Won't Start

If application fails to start:
- Verify start command is correct
- Check application permissions
- Ensure application is compatible with Windows version
- Review application dependencies

### Window Operations Fail

If window operations don't work:
- Verify window handle is valid
- Check window still exists
- Ensure window is not minimized (for some operations)
- Wait for window to be ready

### UI Automation Issues

If UI interactions fail:
- Take screenshot to verify UI state
- Ensure window has focus
- Add delays between actions
- Verify coordinates are correct
- Check for popup dialogs blocking interaction