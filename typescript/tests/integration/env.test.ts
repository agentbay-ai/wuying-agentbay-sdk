// ci-stable
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

const ENV_TEST_IMAGE = "AIO_ubuntu2404";

describe("Env", () => {
  jest.setTimeout(60000);

  let agentBay: AgentBay;
  let session: Session;

  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
    log("Creating a new session for Env testing...");
    const createResponse = await agentBay.create({ imageId: ENV_TEST_IMAGE });
    session = createResponse.session!;
    log(`Session created with ID: ${session.sessionId}`);
  });

  afterEach(async () => {
    if (session) {
      log("Cleaning up: Deleting the session...");
      await agentBay.delete(session);
      log("Session deleted");
    }
  });

  test("set basic env vars", async () => {
    const result = await session.env.set({
      TEST_KEY: "test_value",
      ANOTHER_KEY: "another_value",
    });
    expect(result.success).toBe(true);
    expect(result.requestId).toBeTruthy();
  }, 30000);

  test("get all env vars", async () => {
    await session.env.set({ SDK_TEST_A: "value_a" });
    const result = await session.env.get();
    expect(result.success).toBe(true);
    expect(result.envs).toBeDefined();
    expect(result.envs["SDK_TEST_A"]).toBe("value_a");
  }, 30000);

  test("get specific keys", async () => {
    await session.env.set({ GET_KEY_1: "val1", GET_KEY_2: "val2" });
    const result = await session.env.get(["GET_KEY_1", "GET_KEY_2"]);
    expect(result.success).toBe(true);
    expect(result.envs["GET_KEY_1"]).toBe("val1");
    expect(result.envs["GET_KEY_2"]).toBe("val2");
  }, 30000);

  test("overwrite existing key", async () => {
    await session.env.set({ OVERWRITE_KEY: "original" });
    const r1 = await session.env.get(["OVERWRITE_KEY"]);
    expect(r1.envs["OVERWRITE_KEY"]).toBe("original");

    await session.env.set({ OVERWRITE_KEY: "updated" });
    const r2 = await session.env.get(["OVERWRITE_KEY"]);
    expect(r2.envs["OVERWRITE_KEY"]).toBe("updated");
  }, 30000);

  test("env visible in shell", async () => {
    await session.env.set({ SHELL_VISIBLE_VAR: "hello_from_env" });
    const result = await session.command.executeCommand(
      "echo $SHELL_VISIBLE_VAR",
      5000
    );
    expect(result.success).toBe(true);
    expect(result.stdout).toContain("hello_from_env");
  }, 30000);

  test("set empty dict throws", async () => {
    await expect(session.env.set({})).rejects.toThrow();
  }, 30000);
});
