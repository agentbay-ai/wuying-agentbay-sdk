// ci-stable
import { AgentBay } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";

describe("Region ID Integration Tests", () => {
  let apiKey: string;

  beforeAll(() => {
    apiKey = getTestApiKey();
  });

  describe("AgentBay initialization", () => {
    test("should create AgentBay client with region_id", () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      expect(client.getRegionId()).toBe("cn-hangzhou");
    });
    test("should fall back to default when region_id is empty", () => {
      const config = {
        timeout_ms: 60000,
        region_id: "",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      // Empty string is treated as "not provided" → default cn-hangzhou
      expect(client.getRegionId()).toBe("cn-hangzhou");
    });
  });

  describe("Session creation with region_id", () => {
    test("should create session successfully with region_id", async () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      const sessionResult = await client.create({ imageId: "linux_latest" });

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.session!.sessionId).toBeDefined();

      // Clean up
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 60000);

    test("should create session successfully without region_id", async () => {
      const client = new AgentBay({ apiKey });

      const sessionResult = await client.create({ imageId: "linux_latest" });

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.session!.sessionId).toBeDefined();

      // Clean up
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 60000);
  });

  describe("Context operations with region_id", () => {
    test("should create context successfully with region_id", async () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      const contextName = `test-context-typescript-region-id-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.context).toBeDefined();
      expect(contextResult.context!.id).toBeDefined();
      expect(contextResult.context!.name).toBe(contextName);

      // Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
    }, 30000);

    test("should get existing context without create (no LoginRegionId)", async () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      // Try to get non-existent context without create
      const contextName = `non-existent-context-${Date.now()}`;
      const contextResult = await client.context.get(contextName, false);

      // Should fail for non-existent context
      expect(contextResult.success).toBe(false);
      expect(contextResult.context).toBeUndefined();
    }, 30000);

    test("should create context successfully without region_id", async () => {
      const client = new AgentBay({ apiKey });

      const contextName = `test-context-no-region-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.context).toBeDefined();
      expect(contextResult.context!.id).toBeDefined();

      // Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
    }, 30000);
  });

  describe("End-to-end workflow with region_id", () => {
    test("should complete full workflow with region_id", async () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey,
        config: config,
      });

      // 1. Create context
      const contextName = `e2e-test-context-${Date.now()}`;
      const contextResult = await client.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // 2. Create session
      const sessionResult = await client.create({ imageId: "linux_latest" });
      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();

      // 3. Get session info
      const sessionInfo = await sessionResult.session.info();
      const resultSessionInfo = sessionInfo.data;
      expect(sessionInfo.success).toBe(true);
      expect(resultSessionInfo.sessionId).toBe(
        sessionResult.session!.sessionId
      );

      // 4. Clean up
      if (contextResult.context) {
        await client.context.delete(contextResult.context);
      }
      if (sessionResult.session) {
        await sessionResult.session.delete();
      }
    }, 90000);
  });
});
