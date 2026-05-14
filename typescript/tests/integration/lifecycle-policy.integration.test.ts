import { AgentBay, CreateSessionParams, LifecyclePolicy } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";

describe("LifecyclePolicy integration", () => {
  const imageId = "linux_latest";

  it("should create session with custom lifecycle policy", async () => {
    const agentBay = new AgentBay({ apiKey: getTestApiKey() });
    const policy = new LifecyclePolicy({
      idleReleaseTimeout: 10,
      maxRuntime: 60,
    });
    const params: CreateSessionParams = {
      imageId,
      labels: {
        test: "lifecycle-policy",
        sdk: "typescript",
        case: "custom",
      },
      lifecyclePolicy: policy,
    };
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();
    const session = result.session!;
    try {
      const cmdResult = await session.command.executeCommand("echo hello");
      expect(cmdResult.output?.trim()).toBe("hello");
    } finally {
      await agentBay.delete(session);
    }
  }, 120000);

  it("should create session with manual release", async () => {
    const agentBay = new AgentBay({ apiKey: getTestApiKey() });
    const policy = new LifecyclePolicy({ manualRelease: true });
    const params: CreateSessionParams = {
      imageId,
      labels: {
        test: "lifecycle-policy",
        sdk: "typescript",
        case: "manual",
      },
      lifecyclePolicy: policy,
    };
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();
    const session = result.session!;
    try {
      const cmdResult = await session.command.executeCommand("echo manual");
      expect(cmdResult.output?.trim()).toBe("manual");
    } finally {
      await agentBay.delete(session);
    }
  }, 120000);

  it("should create session with default lifecycle policy", async () => {
    const agentBay = new AgentBay({ apiKey: getTestApiKey() });
    const params: CreateSessionParams = {
      imageId,
      labels: {
        test: "lifecycle-policy",
        sdk: "typescript",
        case: "default",
      },
      lifecyclePolicy: new LifecyclePolicy(),
    };
    const result = await agentBay.create(params);
    expect(result.success).toBe(true);
    expect(result.session).toBeDefined();
    const session = result.session!;
    await agentBay.delete(session);
  }, 120000);
});
