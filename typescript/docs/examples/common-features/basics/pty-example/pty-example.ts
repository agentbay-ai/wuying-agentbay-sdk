import { AgentBay, log, logError } from 'wuying-agentbay-sdk';

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY || 'akm-xxx';
  if (!process.env.AGENTBAY_API_KEY) {
    log('Warning: Set AGENTBAY_API_KEY for a real run.');
  }

  const agentBay = new AgentBay({ apiKey });
  log('\nCreating session with default image (CreateSessionParams equivalent)...');
  const createResponse = await agentBay.create({});
  if (!createResponse.success || !createResponse.session) {
    logError('Failed to create session', createResponse);
    process.exit(1);
  }
  const session = createResponse.session;
  log(`Session: ${session.sessionId}\n`);

  try {
    // 1. Create PTY and echo
    const chunks: Uint8Array[] = [];
    const handle = await session.pty.create({
      onData: (data) => chunks.push(data),
    });
    log(`1. Created PTY: ${handle.ptySessionId}`);
    await sleep(1000);
    await handle.sendInput(
      new TextEncoder().encode("echo 'AGENTBAY_PTY_EXAMPLE_ECHO'\r")
    );
    await sleep(2000);
    const combined = Buffer.concat(chunks).toString('utf-8');
    log(
      `   Echo output contains marker: ${combined.includes('AGENTBAY_PTY_EXAMPLE_ECHO')}\n`
    );

    // 2. Resize
    await handle.resize(120, 40);
    await sleep(1000);
    await handle.sendInput(
      new TextEncoder().encode('echo "cols=$(tput cols) lines=$(tput lines)"\r')
    );
    await sleep(2000);
    const afterResize = Buffer.concat(chunks).toString('utf-8');
    log(
      `2. Resize 120x40; cols=120 in output: ${afterResize.includes('cols=120')}\n`
    );

    // 3. List
    const listed = await session.pty.list();
    const ids = listed.map((s) => s.ptySessionId);
    log(
      `3. List PTY sessions: count=${listed.length}, id present: ${ids.includes(handle.ptySessionId)}\n`
    );

    // 4. Disconnect / reconnect
    const ptyId = handle.ptySessionId;
    handle.disconnect();
    const out2: Uint8Array[] = [];
    const handle2 = await session.pty.connect(ptyId, (data) => out2.push(data));
    await sleep(1000);
    await handle2.sendInput(
      new TextEncoder().encode("echo 'AGENTBAY_PTY_EXAMPLE_RECONNECT'\r")
    );
    await sleep(2000);
    const text2 = Buffer.concat(out2).toString('utf-8');
    log(
      `4. Reconnect OK: ${text2.includes('AGENTBAY_PTY_EXAMPLE_RECONNECT')}\n`
    );
    handle2.disconnect();

    // 5. Kill
    const killHandle = await session.pty.create();
    await sleep(1000);
    await killHandle.kill();
    const killCode = await killHandle.wait(10000);
    log(`5. Kill exit code: ${killCode} (expected -9)\n`);

    // 6. Exit with wait
    const exitHandle = await session.pty.create();
    await sleep(1000);
    await exitHandle.sendInput(new TextEncoder().encode('exit\r'));
    const exitCode = await exitHandle.wait(10000);
    log(`6. Shell exit code: ${exitCode} (expected 0)`);
    log('\nPTY example completed.');
  } finally {
    log('\nDeleting session...');
    try {
      await agentBay.delete(session);
      log('Session deleted.');
    } catch (e) {
      log(`Error deleting session: ${e}`);
    }
  }
}

main().catch((error) => {
  logError('Error in main:', error);
  process.exit(1);
});
