// ci-stable
import { AgentBay, Session, WsCancelledError } from "../../src";
import { log, logError } from "../../src/utils/logger";

describe("WS stream cancel Integration Test", () => {
  let agentBay: AgentBay | null = null;
  let session: Session | null = null;

  jest.setTimeout(120000);

  beforeAll(async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      log(
        "AGENTBAY_API_KEY is not set; skipping WS stream cancel integration test"
      );
      return;
    }

    agentBay = new AgentBay({ apiKey });
    const imageId = process.env.AGENTBAY_WS_IMAGE_ID || "linux_latest";
    const created = await agentBay.create({ imageId });
    if (!created.success || !created.session) {
      throw new Error(`Failed to create session: ${created.errorMessage}`);
    }
    const s = created.session;
    session = s;
    if (!s.wsUrl) {
      throw new Error("wsUrl is empty in CreateMcpSession response");
    }
  });

  afterAll(async () => {
    if (session) {
      try {
        await session.delete();
      } catch (e) {
        logError("Failed to delete session:", e);
      }
    }
  });

  test("cancel should reject waitEnd with WsCancelledError", async () => {
    if (!session) return;

    const wsClient = await session.getWsClient();
    let target = "wuying_codespace";
    for (const tool of session.mcpTools || []) {
      try {
        if (tool && tool.name === "run_code" && tool.server) {
          target = tool.server;
          break;
        }
      } catch (_e) {
        continue;
      }
    }

    const events: Record<string, any>[] = [];
    const ends: Record<string, any>[] = [];
    const errors: Error[] = [];

    const handle = await wsClient.callStream({
      target,
      data: {
        method: "run_code",
        mode: "stream",
        params: {
          language: "python",
          timeoutS: 60,
          code:
            "import time\n" +
            "print(0, flush=True)\n" +
            "time.sleep(10)\n" +
            "print(1, flush=True)\n",
        },
      },
      onEvent: (_invocationId, data) => {
        events.push(data);
      },
      onEnd: (_invocationId, data) => {
        ends.push(data);
      },
      onError: (_invocationId, err) => {
        errors.push(err);
      },
    });

    await new Promise((r) => setTimeout(r, 500));
    await handle.cancel();

    const t0 = Date.now();
    await expect(handle.waitEnd()).rejects.toBeInstanceOf(WsCancelledError);
    expect(Date.now() - t0).toBeLessThan(2000);
    expect(ends).toEqual([]);
    expect(errors.length).toBe(1);
    expect(errors[0]).toBeInstanceOf(WsCancelledError);
    expect(events.length).toBeGreaterThanOrEqual(0);
  });
});
