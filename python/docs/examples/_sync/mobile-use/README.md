# Mobile Use Examples

This directory contains examples demonstrating mobile UI automation capabilities in AgentBay SDK.

## Overview

Mobile Use environment (`mobile_latest` image) provides cloud-based Android mobile automation with:
- UI element detection and interaction
- Touch gestures (tap, swipe, scroll)
- Text input and key events
- Screenshot capture
- Mobile application management
- ADB (Android Debug Bridge) integration

## Examples

### mobile_agent_streaming.py

Mobile Agent streaming example:
- Execute tasks using Mobile Agent with streaming output
- Real-time reasoning, content, tool call, and tool result callbacks
- Observe mode for screen analysis

### mobile_simulate_basic_usage.py

Mobile simulate basic usage example:
- Simulated mobile interaction without real device
- Tap, swipe, input text operations
- Screenshot capture

### mobile_simulate_with_ctx.py

Mobile simulate with context:
- Mobile simulation with custom context injection
- Context-aware automation flows

### mobile_app_operations.py

Mobile app management:
- Get installed applications
- Start and stop applications
- Application state monitoring

### mobile_beta_screenshot.py

Mobile screenshot capture:
- Using `beta_take_screenshot()` API
- Save screenshots locally

### mobile_bounds_rect.py

Mobile UI bounds/rect operations:
- Get element bounding rectangles
- UI layout analysis

### mobile_ui_automation.py

Mobile UI automation:
- Tap at coordinates
- Swipe gestures
- Text input
- Key events

### mobile_get_adb_url_example.py

ADB URL retrieval example:
- Get ADB connection URL
- Connect external tools to mobile session
- Remote debugging setup

### mobile_system/main.py

Comprehensive mobile system operations:
- Application management
- UI element detection
- Touch interactions
- Text input
- Screenshot capture

### get_all_ui_elements_xml/

Get all UI elements as XML:
- Full UI hierarchy dump
- XML format parsing

## Prerequisites

- Python 3.8 or later
- AgentBay SDK installed: `pip install wuying-agentbay-sdk`
- Valid `AGENTBAY_API_KEY` environment variable

## Quick Start

```bash
# Set your API key
export AGENTBAY_API_KEY=your_api_key_here

# Run the main example
cd mobile_system
python main.py

# Run ADB URL example
cd ..
python mobile_get_adb_url_example.py
```

## Features Demonstrated

### Application Management
- List installed applications
- Filter system applications
- Start applications with monkey command
- Start with specific activity
- Stop applications by command
- Monitor application processes

### UI Element Detection
- Get clickable elements only
- Get complete UI element tree
- Element property inspection
- Resource ID and text extraction
- Hierarchical element structure

### Touch Interactions
- Single tap at coordinates
- Long press
- Swipe gestures with duration
- Multi-point touch
- Drag and drop

### Text Input
- Input text to focused elements
- Send individual key events
- Special keys (HOME, BACK, etc.)
- Keyboard shortcuts

### Screenshot Operations
- Capture full screen
- Save to local file
- Base64 encoding support
- Image format handling

## API Methods Used

| Method | Purpose |
|--------|---------|
| `session.mobile.get_installed_apps()` | Get list of installed applications |
| `session.mobile.start_app()` | Start an application |
| `session.mobile.stop_app_by_cmd()` | Stop application by command |
| `session.mobile.get_clickable_ui_elements()` | Get clickable UI elements |
| `session.mobile.get_all_ui_elements()` | Get complete UI element tree |
| `session.mobile.tap()` | Tap at coordinates |
| `session.mobile.swipe()` | Perform swipe gesture |
| `session.mobile.input_text()` | Input text |
| `session.mobile.send_key()` | Send key event |
| `session.mobile.screenshot()` | Take screenshot |
| `session.mobile.get_adb_url()` | Get ADB connection URL |

## Common Use Cases

### 1. App Testing Automation
- Start app and wait for load
- Get UI elements and find target elements
- Input credentials and submit forms
- Verify results with screenshots

### 2. UI Element Inspection
- Get all elements and find specific elements by text
- Navigate UI hierarchy
- Extract element properties

### 3. Gesture Automation
- Swipe up/down for scrolling
- Swipe left/right for navigation
- Long press for context menus

## Best Practices

1. **Wait for UI Load**: Add delays after starting apps or navigation
2. **Element Verification**: Verify elements exist before interaction
3. **Error Handling**: Check `result.success` for all operations
4. **Resource Cleanup**: Stop apps and delete sessions when done
5. **Screenshot Verification**: Use screenshots to verify UI state
6. **Coordinate Accuracy**: Use element coordinates from UI tree
7. **Gesture Timing**: Adjust swipe duration for different effects
8. **Key Events**: Use appropriate key codes for device buttons

## Related Documentation

- [Mobile Use Guide](../../../../../docs/guides/mobile-use/README.md)
- [Mobile Application Management](../../../../../docs/guides/mobile-use/mobile-application-management.md)
- [Mobile UI Automation](../../../../../docs/guides/mobile-use/mobile-ui-automation.md)

## Troubleshooting

### Application Not Starting

If application fails to start:
- Verify package name is correct
- Check application is installed
- Ensure monkey command syntax is correct
- Try with specific activity

### UI Elements Not Found

If UI elements are missing:
- Wait longer for UI to load
- Check timeout parameter
- Verify app is in correct state
- Take screenshot to inspect UI

### Touch Interactions Not Working

If taps/swipes don't work:
- Verify coordinates are within screen bounds
- Check element is visible and enabled
- Ensure no overlay blocking interaction
- Add delay before interaction

### ADB Connection Issues

If ADB URL doesn't work:
- Verify session is mobile_latest image
- Check network connectivity
- Ensure ADB is installed locally
- Try reconnecting: `adb disconnect` then `adb connect`

### Screenshot Issues

If screenshots fail or are corrupted:
- Check session is active
- Verify sufficient memory
- Try smaller screen resolution
- Handle base64 decoding correctly