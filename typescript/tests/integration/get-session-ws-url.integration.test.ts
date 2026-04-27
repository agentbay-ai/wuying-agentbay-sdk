// ci-stable
import { AgentBay, Session } from "../../src";
import { log, logError } from "../../src/utils/logger";

describe("GetSession wsUrl Integration Test", () => {
  let agentBay: AgentBay | null = null;
  let session: Session | null = null;

  jest.setTimeout(120000);

  beforeAll(async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      log(
        "AGENTBAY_API_KEY is not set; skipping GetSession wsUrl integration test"
      );
      return;
    }

    agentBay = new AgentBay({ apiKey });
    const imageId = process.env.AGENTBAY_GET_SESSION_IMAGE_ID || "linux_latest";
    const created = await agentBay.create({ imageId });
    if (!created.success || !created.session) {
      throw new Error(`Failed to create session: ${created.errorMessage}`);
    }
    session = created.session;
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

  test("should populate wsUrl on restored session", async () => {
    if (!agentBay || !session) return;

    const r = await agentBay.get(session.sessionId);
    expect(r.success).toBe(true);
    expect(r.session).toBeTruthy();
    expect(r.session?.wsUrl).toBeTruthy();
    expect(String(r.session?.wsUrl)).toMatch(/^wss?:\/\//);
  });
});
