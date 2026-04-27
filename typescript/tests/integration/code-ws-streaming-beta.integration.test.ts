// ci-stable
// @ts-nocheck

import { AgentBay, Session } from "../../src";
import { log, logError } from "../../src/utils/logger";

describe("runCode WS streaming (beta) Integration Test", () => {
  let agentBay: AgentBay | null = null;
  let session: Session | null = null;

  jest.setTimeout(120000);

  beforeAll(async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      log(
        "AGENTBAY_API_KEY is not set; skipping WS streaming integration test"
      );
      return;
    }

    agentBay = new AgentBay({ apiKey });
    const imageId = process.env.AGENTBAY_WS_IMAGE_ID || "linux_latest";
    const created = await agentBay.create({ imageId });
    if (!created.success || !created.session) {
      throw new Error(`Failed to create session: ${created.errorMessage}`);
    }
    session = created.session;
    if (!session || !session.wsUrl) {
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

  test("should stream stdout chunks with real-time callbacks", async () => {
    if (!session) return;

    const stdoutChunks: string[] = [];
    const stdoutTimes: number[] = [];
    const errors: unknown[] = [];

    const startMs = Date.now();
    const r = await session.code.runCode(
      "import time\n" +
        "print('hello', flush=True)\n" +
        "time.sleep(1.0)\n" +
        "print(2, flush=True)\n",
      "python",
      60,
      {
        streamBeta: true,
        onStdout: (chunk) => {
          stdoutChunks.push(chunk);
          stdoutTimes.push(Date.now());
        },
        onError: (err) => {
          errors.push(err);
        },
      }
    );
    const endMs = Date.now();

    expect(errors).toEqual([]);
    expect(r.success).toBe(true);
    expect(stdoutChunks.length).toBeGreaterThanOrEqual(2);
    expect(endMs - startMs).toBeGreaterThanOrEqual(1000);

    const joined = stdoutChunks.join("");
    expect(joined).toContain("hello");
    expect(joined).toContain("2");

    let helloT: number | null = null;
    let twoT: number | null = null;
    for (let i = 0; i < stdoutChunks.length; i += 1) {
      const chunk = stdoutChunks[i];
      const t = stdoutTimes[i];
      if (helloT === null && chunk.includes("hello")) {
        helloT = t;
      }
      if (twoT === null && chunk.includes("2")) {
        twoT = t;
      }
    }
    expect(helloT).not.toBeNull();
    expect(twoT).not.toBeNull();
    expect((twoT as number) - (helloT as number)).toBeGreaterThanOrEqual(800);
  }, 60000);
});
