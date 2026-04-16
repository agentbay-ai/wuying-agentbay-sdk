# PTY Terminal Example

Demonstrates interactive pseudo-terminal (PTY) sessions in Go: create, echo input, resize, list, disconnect/reconnect, kill, and graceful exit with `Wait`.

## Features Demonstrated

- Create a PTY with an `OnData` callback
- Send shell input and observe output
- Resize the terminal
- List PTY sessions via `Pty.List`
- `Disconnect` locally and `Connect` to the same `ptySessionId`
- `Kill` and read exit code -9
- Send `exit` and `Wait` for exit code 0

## Running the Example

1. Add the module dependency:

```bash
go get github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay
```

2. Set your API key:

```bash
export AGENTBAY_API_KEY=your_api_key_here
```

3. Run from this directory:

```bash
go run main.go
```

## Related

- Go package: `golang/pkg/agentbay/pty`
- Integration tests: `golang/tests/pkg/integration/pty_integration_test.go`
