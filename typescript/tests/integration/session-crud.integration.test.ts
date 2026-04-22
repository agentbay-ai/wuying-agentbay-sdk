// ci-stable
import { AgentBay, Session, CreateSessionParams } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session CRUD", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeEach(() => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
  });

  it("should create, list, and delete a session with requestId", async () => {
    // Create a session
    log("Creating a new session...");
    const params: CreateSessionParams = {
      imageId: "linux_latest",
    };
    const createResponse = await agentBay.create(params);

    // Verify SessionResult structure
    expect(createResponse.success).toBe(true);
    expect(createResponse.requestId).toBeDefined();
    expect(typeof createResponse.requestId).toBe("string");
    expect(createResponse.requestId!.length).toBeGreaterThan(0);
    expect(createResponse.session).toBeDefined();
    expect(createResponse.errorMessage).toBeUndefined();

    session = createResponse.session!;
    log(`Session created with ID: ${session.sessionId}`);
    log(`Create Session RequestId: ${createResponse.requestId || "undefined"}`);

    // Ensure session ID is not empty
    expect(session.sessionId).toBeDefined();
    expect(session.sessionId.length).toBeGreaterThan(0);

    // List sessions
    log("Listing sessions...");
    const listResult = await agentBay.list();

    // Ensure at least one session (the one we just created)
    expect(listResult.sessionIds.length).toBeGreaterThanOrEqual(1);

    // Check if our created session is in the list
    const found = listResult.sessionIds.some(
      (sid) => sid.sessionId === session.sessionId
    );
    expect(found).toBe(true);

    // Delete the session
    log("Deleting the session...");
    const deleteResponse = await agentBay.delete(session);
    log(`Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`);

    // Verify DeleteResult structure
    expect(deleteResponse.success).toBe(true);
    expect(deleteResponse.requestId).toBeDefined();
    expect(typeof deleteResponse.requestId).toBe("string");
    expect(deleteResponse.requestId!.length).toBeGreaterThan(0);
    expect(deleteResponse.errorMessage).toBeUndefined();

    // List sessions again to ensure it's deleted
    const listResultAfterDelete = await agentBay.list();

    // Check if the deleted session is not in the list
    const stillExists = listResultAfterDelete.sessionIds.some(
      (sid) => sid.sessionId === session.sessionId
    );
    expect(stillExists).toBe(false);
  });
});
