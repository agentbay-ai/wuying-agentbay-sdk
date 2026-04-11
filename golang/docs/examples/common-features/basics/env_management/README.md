# Env Module Example (Go)

This example shows **session-scoped** environment variables using `session.Env`: `Set`, `Get` with no keys (all) or specific names, overwrite, and a shell command that reads `$DEMO_APP`.

## Prerequisites

- Go 1.21+ (matching the SDK module)
- `AGENTBAY_API_KEY` in the environment

## Run

From this directory:

```bash
export AGENTBAY_API_KEY="your-api-key"
go run main.go
```

The session uses `imageId` `AIO_ubuntu2404`.

## Expected output (illustrative)

- Session ID printed after create.
- Steps 1–5 print `DEMO_APP` / `DEMO_STAGE` values and `echo $DEMO_APP` as `agentbay`.
- Session is deleted in a deferred cleanup.

## See also

- [Env API reference](../../../../api/common-features/basics/env.md)
