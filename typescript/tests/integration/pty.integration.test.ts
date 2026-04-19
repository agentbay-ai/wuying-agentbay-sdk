import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";

const IMAGE_ID = "linux_latest";

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

jest.setTimeout(120000);

describe("PTY Integration", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeAll(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    const result = await agentBay.create({ imageId: IMAGE_ID });
    expect(result.success).toBe(true);
    session = result.session!;
  });

  afterAll(async () => {
    try {
      if (session) await agentBay.delete(session);
    } catch (e) {
      console.warn("Failed to delete session:", e);
    }
  });

  test("create and echo", async () => {
    const chunks: Uint8Array[] = [];
    const handle = await session.pty.create({
      onData: (data) => chunks.push(data),
    });
    expect(handle.ptySessionId).toBeTruthy();
    expect(handle.isConnected).toBe(true);

    await sleep(1000);
    await handle.sendInput(new TextEncoder().encode("echo 'PTY_TS_OK_12345'\r"));
    await sleep(2000);

    const combined = Buffer.concat(chunks).toString("utf-8");
    expect(combined).toContain("PTY_TS_OK_12345");

    handle.disconnect();
  });

  test("ctrl+c interrupt", async () => {
    const chunks: Uint8Array[] = [];
    const handle = await session.pty.create({
      onData: (data) => chunks.push(data),
    });
    await sleep(1000);

    await handle.sendInput(new TextEncoder().encode("sleep 100\r"));
    await sleep(1000);

    await handle.sendInput(new Uint8Array([0x03]));
    await sleep(2000);

    const combined = Buffer.concat(chunks).toString("utf-8");
    expect(combined).toMatch(/\^C|\$/);

    handle.disconnect();
  });

  test("resize", async () => {
    const chunks: Uint8Array[] = [];
    const handle = await session.pty.create({
      onData: (data) => chunks.push(data),
    });
    await sleep(1000);

    await handle.resize(120, 40);
    await sleep(1000);

    await handle.sendInput(
      new TextEncoder().encode('echo "cols=$(tput cols) lines=$(tput lines)"\r')
    );
    await sleep(2000);

    const combined = Buffer.concat(chunks).toString("utf-8");
    expect(combined).toContain("cols=120");
    expect(combined).toContain("lines=40");

    handle.disconnect();
  });

  test("list sessions", async () => {
    const handle = await session.pty.create();
    await sleep(1000);

    const sessions = await session.pty.list();
    const ids = sessions.map((s) => s.ptySessionId);
    expect(ids).toContain(handle.ptySessionId);

    handle.disconnect();
  });

  test("disconnect and reconnect", async () => {
    const output1: Uint8Array[] = [];
    const handle1 = await session.pty.create({
      onData: (data) => output1.push(data),
    });
    await sleep(1000);

    await handle1.sendInput(
      new TextEncoder().encode("echo 'BEFORE_DISCONNECT'\r")
    );
    await sleep(1000);

    const ptyId = handle1.ptySessionId;
    handle1.disconnect();
    expect(handle1.isConnected).toBe(false);

    const output2: Uint8Array[] = [];
    const handle2 = await session.pty.connect(ptyId, (data) =>
      output2.push(data)
    );
    expect(handle2.isConnected).toBe(true);

    await handle2.sendInput(
      new TextEncoder().encode("echo 'AFTER_RECONNECT'\r")
    );
    await sleep(2000);

    const combined = Buffer.concat(output2).toString("utf-8");
    expect(combined).toContain("AFTER_RECONNECT");

    handle2.disconnect();
  });

  test("exit with exit code", async () => {
    const handle = await session.pty.create();
    await sleep(1000);

    await handle.sendInput(new TextEncoder().encode("exit\r"));
    const exitCode = await handle.wait(10000);
    expect(typeof exitCode).toBe("number");
    expect(handle.isConnected).toBe(false);
  });

  test("kill with exit code -9", async () => {
    const handle = await session.pty.create();
    await sleep(1000);

    await handle.kill();
    const exitCode = await handle.wait(10000);
    expect(exitCode).toBe(-9);
  });

  test("multiple ptys", async () => {
    const output1: Uint8Array[] = [];
    const output2: Uint8Array[] = [];
    const handle1 = await session.pty.create({
      onData: (data) => output1.push(data),
    });
    const handle2 = await session.pty.create({
      onData: (data) => output2.push(data),
    });
    await sleep(1000);

    await handle1.sendInput(new TextEncoder().encode("echo 'FROM_PTY_1'\r"));
    await handle2.sendInput(new TextEncoder().encode("echo 'FROM_PTY_2'\r"));
    await sleep(2000);

    const combined1 = Buffer.concat(output1).toString("utf-8");
    const combined2 = Buffer.concat(output2).toString("utf-8");
    expect(combined1).toContain("FROM_PTY_1");
    expect(combined2).toContain("FROM_PTY_2");

    handle1.disconnect();
    handle2.disconnect();
  });
});
