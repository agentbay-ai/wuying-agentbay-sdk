# Env Module Example (TypeScript)

This example shows how to manage **session-scoped** environment variables with `session.env`: set values, read all or selected keys, overwrite a key, and confirm the values appear in `session.command` output.

## Prerequisites

- Node.js 16+
- `AGENTBAY_API_KEY` set in your environment
- When developing this repo, the example imports from `typescript/src` via a relative path. For a standalone project, install `wuying-agentbay-sdk`, run `npm run build` in the package if needed, and change the import to `wuying-agentbay-sdk`.

## Run

From the repository `typescript` directory (so `wuying-agentbay-sdk` resolves):

```bash
export AGENTBAY_API_KEY="your-api-key"
npx ts-node docs/examples/common-features/basics/env-management/main.ts
```

## Expected output (illustrative)

- Session is created with `imageId` `linux_latest`.
- Logs for set, get-all, get-by-keys, overwrite, and `echo $DEMO_APP` showing `agentbay`.
- Session is deleted at the end.

## See also

- [Env API reference](../../../../api/common-features/basics/env.md)
