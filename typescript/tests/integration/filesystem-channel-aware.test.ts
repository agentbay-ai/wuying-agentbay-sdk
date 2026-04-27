// ci-stable
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

const TestPathPrefix = "/tmp";

function logChannelInfo(session: Session): void {
  const linkUrl = session.getLinkUrl?.() ?? "";
  const token = session.getToken?.() ?? "";
  if (linkUrl && token) {
    log("[Channel] Using HTTP (LinkUrl) channel");
  } else {
    log("[Channel] Using MQTT (API) channel");
  }
}

describe("fileSystem channel-aware", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeEach(async () => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });

    log("Creating a new session for channel-aware fileSystem testing...");
    const createResponse = await agentBay.create({ imageId: "linux_latest" });

    if (!createResponse.success || !createResponse.session) {
      throw new Error(
        `Failed to create session: ${
          createResponse.errorMessage || "Unknown error"
        }`
      );
    }

    session = createResponse.session;
    log(`Session created with ID: ${session.sessionId}`);
  });

  afterEach(async () => {
    log("Cleaning up: Deleting the session...");
    try {
      if (session) {
        await agentBay.delete(session);
      }
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });

  it("should read and write a small file via HTTP channel", async () => {
    if (!session.fileSystem) {
      log("FileSystem not available, skipping test");
      return;
    }

    logChannelInfo(session);

    const content = "Hello, channel-aware filesystem!";
    const path = `${TestPathPrefix}/channel_test_small.txt`;

    const writeResponse = await session.fileSystem.writeFile(
      path,
      content,
      "overwrite"
    );
    expect(writeResponse.success).toBe(true);

    const readResponse = await session.fileSystem.readFile(path);
    expect(readResponse.success).toBe(true);
    expect(readResponse.content).toBe(content);
    log(`[PASS] Small file roundtrip: ${content.length} bytes`);
  });

  it("should read and write a medium file (~60KB) via HTTP channel", async () => {
    if (!session.fileSystem) {
      log("FileSystem not available, skipping test");
      return;
    }

    logChannelInfo(session);

    const content = "A".repeat(60 * 1024); // 60KB
    const path = `${TestPathPrefix}/channel_test_medium.txt`;

    const writeResponse = await session.fileSystem.writeFile(
      path,
      content,
      "overwrite"
    );
    expect(writeResponse.success).toBe(true);

    const readResponse = await session.fileSystem.readFile(path);
    expect(readResponse.success).toBe(true);
    expect(readResponse.content).toBe(content);
    log(`[PASS] Medium file roundtrip: ${content.length} bytes`);
  });

  it("should read and write a large file (~200KB) via HTTP channel", async () => {
    if (!session.fileSystem) {
      log("FileSystem not available, skipping test");
      return;
    }

    logChannelInfo(session);

    const content = "B".repeat(200 * 1024); // 200KB
    const path = `${TestPathPrefix}/channel_test_large.txt`;

    const writeResponse = await session.fileSystem.writeFile(
      path,
      content,
      "overwrite"
    );
    expect(writeResponse.success).toBe(true);

    const readResponse = await session.fileSystem.readFile(path);
    expect(readResponse.success).toBe(true);
    expect(readResponse.content).toBe(content);
    log(`[PASS] Large file roundtrip: ${content.length} bytes`);
  });

  it("should support append mode via HTTP channel", async () => {
    if (!session.fileSystem) {
      log("FileSystem not available, skipping test");
      return;
    }

    logChannelInfo(session);

    const path = `${TestPathPrefix}/channel_test_append.txt`;

    const writeResponse = await session.fileSystem.writeFile(
      path,
      "first part",
      "overwrite"
    );
    expect(writeResponse.success).toBe(true);

    const appendResponse = await session.fileSystem.writeFile(
      path,
      " second part",
      "append"
    );
    expect(appendResponse.success).toBe(true);

    const readResponse = await session.fileSystem.readFile(path);
    expect(readResponse.success).toBe(true);
    expect(readResponse.content).toBe("first part second part");
    log("[PASS] Append mode works correctly");
  });

  it("should handle unicode content via HTTP channel", async () => {
    if (!session.fileSystem) {
      log("FileSystem not available, skipping test");
      return;
    }

    logChannelInfo(session);

    const content = "你好世界 🌍 こんにちは 안녕하세요 مرحبا";
    const path = `${TestPathPrefix}/channel_test_unicode.txt`;

    const writeResponse = await session.fileSystem.writeFile(
      path,
      content,
      "overwrite"
    );
    expect(writeResponse.success).toBe(true);

    const readResponse = await session.fileSystem.readFile(path);
    expect(readResponse.success).toBe(true);
    expect(readResponse.content).toBe(content);
    log("[PASS] Unicode content roundtrip");
  });
});
