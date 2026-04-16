# Env Module Example

This example shows how to manage session-scoped environment variables with `session.env` on an image that exposes the env MCP tools.

## What it demonstrates

- `session.env.set({"KEY": "value"})` — set variables in the sandbox
- `session.env.get()` — read all variables returned by the service
- `session.env.get(keys=["KEY"])` — read selected keys only
- Overwriting a key with a second `set` call
- Confirming the value in the shell via `session.command.execute_command("echo $KEY")`

## Prerequisites

- Python 3.8+
- `agentbay` installed (e.g. `pip install agentbay` or editable install from this repo)
- `AGENTBAY_API_KEY` set in the environment

## Run

```bash
export AGENTBAY_API_KEY="your-api-key-here"
python main.py
```

The session is created with `image_id="AIO_ubuntu2404"` so env tools are available.

## Expected output

You should see the session id, success lines for `set` / `get`, `KEY` transitioning from `value` to `updated`, and shell stdout containing `updated`. The script raises if any step fails. On exit, the session is deleted.
