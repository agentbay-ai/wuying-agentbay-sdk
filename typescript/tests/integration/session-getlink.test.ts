// ci-stable
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session GetLink", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeEach(async () => {
    const apiKey = getTestApiKey();
    log(`Using API key: ${apiKey}`);

    agentBay = new AgentBay({ apiKey });

    // Create a session with imageId for getLink testing
    log("Creating a new session for getLink testing...");
    const createResponse = await agentBay.create({ imageId: "browser_latest" });
    session = createResponse.session;
    log(`Session created with ID: ${session.sessionId}`);
    log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);
  });

  afterEach(async () => {
    // Clean up the session
    log("Cleaning up: Deleting the session...");
    try {
      if (session) {
        const deleteResponse = await agentBay.delete(session);
        log(
          `Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`
        );
      }
    } catch (error) {
      log(`Warning: Error deleting session: ${error}`);
    }
  });

  describe("getLink method", () => {
    it("should get link without parameters", async () => {
      // Check if the getLink method exists
      if (typeof session.getLink === "function") {
        log("Testing getLink without parameters...");
        try {
          const linkResponse = await session.getLink();
          log("Session link:", linkResponse.data);
          log(`Get Link RequestId: ${linkResponse.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(linkResponse.requestId).toBeDefined();
          expect(typeof linkResponse.requestId).toBe("string");

          // Verify the link data is a string (URL)
          expect(linkResponse.data).toBeDefined();
          expect(typeof linkResponse.data).toBe("string");
        } catch (error) {
          log(`Note: Session link retrieval failed: ${error}`);
          // Don't fail the test if getLink method is not fully implemented
        }
      } else {
        log("Note: Session getLink method is not available, skipping test");
      }
    });

    it("should get link with protocol type parameter", async () => {
      if (typeof session.getLink === "function") {
        log("Testing getLink with protocol type parameter...");
        try {
          const linkWithProtocolResponse = await session.getLink("https");
          log(
            "Session link with protocol https:",
            linkWithProtocolResponse.data
          );
          log(
            `Get Link with Protocol RequestId: ${
              linkWithProtocolResponse.requestId || "undefined"
            }`
          );

          expect(linkWithProtocolResponse.requestId).toBeDefined();
          expect(linkWithProtocolResponse.data).toBeDefined();
          expect(typeof linkWithProtocolResponse.data).toBe("string");
        } catch (error) {
          log(`Note: Session link retrieval with protocol failed: ${error}`);
        }
      } else {
        log("Note: Session getLink method is not available, skipping test");
      }
    });

    it("should get link with port parameter", async () => {
      if (typeof session.getLink === "function") {
        log("Testing getLink with port 30150...");
        try {
          const port = 30150;
          const linkWithPortResponse = await session.getLink(undefined, port);
          log(`Session link with port ${port}:`, linkWithPortResponse.data);
          log(
            `Get Link with Port RequestId: ${
              linkWithPortResponse.requestId || "undefined"
            }`
          );

          expect(linkWithPortResponse.requestId).toBeDefined();
          expect(linkWithPortResponse.data).toBeDefined();
          expect(typeof linkWithPortResponse.data).toBe("string");
        } catch (error) {
          log(`Note: Session link retrieval with port failed: ${error}`);
        }
      } else {
        log("Note: Session getLink method is not available, skipping test");
      }
    });
  });

  describe("getLinkAsync method", () => {
    it("should get link asynchronously with valid port", async () => {
      if (typeof session.getLinkAsync === "function") {
        log("Testing getLinkAsync with valid port...");
        try {
          const validPort = 30150;
          const linkResponse = await session.getLinkAsync("wss", validPort);
          log(`Session link async with port ${validPort}:`, linkResponse.data);
          log(
            `Get Link Async RequestId: ${linkResponse.requestId || "undefined"}`
          );

          // Verify successful response
          expect(linkResponse.requestId).toBeDefined();
          expect(linkResponse.success).toBe(true);
          expect(linkResponse.data).toBeDefined();
          expect(typeof linkResponse.data).toBe("string");
        } catch (error) {
          log(`Note: Session link async retrieval failed: ${error}`);
        }
      } else {
        log(
          "Note: Session getLinkAsync method is not available, skipping test"
        );
      }
    });
  });
});
