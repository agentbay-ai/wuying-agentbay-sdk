# PTY Terminal Example

Demonstrates interactive pseudo-terminal (PTY) sessions: create, input echo, resize, list, disconnect/reconnect, kill, and graceful exit with `wait`.

## Features Demonstrated

- Create a PTY with `onData` output handling
- Send shell input and verify output
- Resize terminal dimensions
- List active PTY sessions on the sandbox session
- Disconnect locally and `connect` to the same server-side PTY
- `kill` and read exit code -9
- `exit` the shell and await exit code 0

## Running the Example

1. Install the SDK:

```bash
npm install wuying-agentbay-sdk
```

2. Set your API key:

```bash
export AGENTBAY_API_KEY=your_api_key_here
```

3. Run (from this directory):

```bash
npx ts-node pty-example.ts
```

## Related

- [PTY API reference](../../../../api/common-features/basics/pty.md) (if generated in your tree)
- TypeScript integration tests: `typescript/tests/integration/pty.integration.test.ts`
