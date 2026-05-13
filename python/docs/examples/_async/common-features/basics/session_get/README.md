# Get API Example

This example demonstrates how to use the `get` API to retrieve a session by its ID.

## Description

The `get` API allows you to retrieve a session object by providing its session ID. This is useful when you have a session ID from a previous operation and want to access or manage that session.

## Prerequisites

- Python 3.8 or higher
- Valid API key set in `AGENTBAY_API_KEY` environment variable
- agentbay package installed

## Installation

```bash
pip install agentbay
```

## Usage

```bash
# Set your API key
export AGENTBAY_API_KEY="your-api-key-here"

# Run the example
python main.py
```

## API Reference

### get

```python
async def get(session_id: str) -> SessionResult
```

Get a session by its ID.

**Parameters:**
- `session_id` (str): The ID of the session to retrieve

**Returns:**
- `SessionResult`: Result object containing:
  - `success` (bool): Whether the operation succeeded
  - `session` (Session): The Session instance if successful
  - `request_id` (str): The API request ID
  - `error_message` (str): Error message if failed

## Expected Output

```
Creating a session...
Created session with ID: session-xxxxxxxxxxxxx

Retrieving session using Get API...
Successfully retrieved session:
  Session ID: session-xxxxxxxxxxxxx
  Request ID: DAD825FE-2CD8-19C8-BB30-CC3BA26B9398

Session is ready for use

Cleaning up...
Session session-xxxxxxxxxxxxx deleted successfully

Attempting to get the deleted session...
Expected behavior: Cannot retrieve deleted session
Error message: Failed to get session: session not found or has been deleted
```

## Notes

- The session ID must be valid and from an existing session
- The get API internally calls the GetSession API endpoint
- The returned session object can be used for all session operations (commands, files, etc.)
- Always clean up sessions when done to avoid resource waste
- Attempting to get a deleted session will return an error, demonstrating proper lifecycle management

## Error Handling

The `get` method returns a `SessionResult` object with error information:

1. **Empty session_id**: Result will have `success=False`
2. **Non-existent session**: Result will have `success=False`
3. **Deleted session**: Result will have `success=False`