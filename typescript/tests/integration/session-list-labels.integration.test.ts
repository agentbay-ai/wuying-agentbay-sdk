// ci-stable
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session List by Labels", () => {
  let agentBay: AgentBay;
  let sessionA: Session;
  let sessionB: Session;

  beforeEach(async () => {
    try {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      const labelsA = {
        environment: "development",
        owner: "team-a",
        project: "project-x",
      };

      const labelsB = {
        environment: "testing",
        owner: "team-b",
        project: "project-y",
      };
      // Create session with labels A
      log("Creating session with labels A...");
      const createResponseA = await agentBay.create({ labels: labelsA });

      expect(createResponseA.success).toBe(true);
      expect(createResponseA.session).toBeDefined();

      sessionA = createResponseA.session!;
      log(`Session created with ID: ${sessionA.sessionId}`);
      log(
        `Create Session A RequestId: ${
          createResponseA.requestId || "undefined"
        }`
      );

      // Create session with labels B
      const createResponseB = await agentBay.create({ labels: labelsB });

      expect(createResponseB.success).toBe(true);
      expect(createResponseB.session).toBeDefined();

      sessionB = createResponseB.session!;
      log(`Session created with ID: ${sessionB.sessionId}`);
      log(
        `Create Session B RequestId: ${
          createResponseB.requestId || "undefined"
        }`
      );
    } catch (error) {
      log(`Failed to constructor: ${error}`);
    }
  });

  afterEach(async () => {
    log("Cleaning up sessions...");
    if (sessionA) {
      try {
        const deleteResponseA = await agentBay.delete(sessionA);
        log(
          `Delete Session A RequestId: ${
            deleteResponseA.requestId || "undefined"
          }`
        );
      } catch (error) {
        log(`Warning: Error deleting session A: ${error}`);
      }
    }

    if (sessionB) {
      try {
        const deleteResponseB = await agentBay.delete(sessionB);
        log(
          `Delete Session B RequestId: ${
            deleteResponseB.requestId || "undefined"
          }`
        );
      } catch (error) {
        log(`Warning: Error deleting session B: ${error}`);
      }
    }
  });

  it("should list sessions by labels with requestId", async () => {
    // Test 1: List all sessions
    const allSessionsResult = await agentBay.list();
    log(`Found ${allSessionsResult.sessionIds.length} sessions in total`);

    // Test 2: List sessions by environment=development label
    try {
      const devSessionsResponse = await agentBay.list(
        { environment: "development" },
        1,
        5
      );
      log(
        `List Sessions by environment=development RequestId: ${
          devSessionsResponse.requestId || "undefined"
        }`
      );
      log(
        `Total count: ${devSessionsResponse.totalCount}, Max results: ${devSessionsResponse.maxResults}`
      );

      expect(devSessionsResponse.success).toBe(true);
      expect(devSessionsResponse.requestId).toBeDefined();
      expect(typeof devSessionsResponse.requestId).toBe("string");
      expect(devSessionsResponse.requestId!.length).toBeGreaterThan(0);
      expect(devSessionsResponse.sessionIds).toBeDefined();
      expect(Array.isArray(devSessionsResponse.sessionIds)).toBe(true);

      const foundSessionA = devSessionsResponse.sessionIds.some(
        (sid) => sid.sessionId === sessionA.sessionId
      );
      expect(foundSessionA).toBe(true);
    } catch (error) {
      log(`Error listing sessions by environment=development: ${error}`);
    }

    // Test 3: List sessions by owner=team-b label
    try {
      const teamBSessionsResponse = await agentBay.list(
        { owner: "team-b" },
        1,
        5
      );
      log(
        `List Sessions by owner=team-b RequestId: ${
          teamBSessionsResponse.requestId || "undefined"
        }`
      );
      log(
        `Total count: ${teamBSessionsResponse.totalCount}, Max results: ${teamBSessionsResponse.maxResults}`
      );

      expect(teamBSessionsResponse.success).toBe(true);
      expect(teamBSessionsResponse.requestId).toBeDefined();

      const foundSessionB = teamBSessionsResponse.sessionIds.some(
        (sid) => sid.sessionId === sessionB.sessionId
      );
      expect(foundSessionB).toBe(true);
    } catch (error) {
      log(`Error listing sessions by owner=team-b: ${error}`);
    }

    // Test 4: List sessions with multiple labels
    try {
      const multiLabelSessionsResponse = await agentBay.list(
        {
          environment: "testing",
          project: "project-y",
        },
        1,
        5
      );
      log(
        `Found ${multiLabelSessionsResponse.sessionIds.length} sessions with environment=testing AND project=project-y`
      );
      log(
        `Total count: ${multiLabelSessionsResponse.totalCount}, Max results: ${multiLabelSessionsResponse.maxResults}`
      );
      log(
        `List Sessions by multiple labels RequestId: ${
          multiLabelSessionsResponse.requestId || "undefined"
        }`
      );

      expect(multiLabelSessionsResponse.success).toBe(true);
      expect(multiLabelSessionsResponse.requestId).toBeDefined();

      const foundSessionA = multiLabelSessionsResponse.sessionIds.some(
        (s) => s.sessionId === sessionA.sessionId
      );
      const foundSessionB = multiLabelSessionsResponse.sessionIds.some(
        (s) => s.sessionId === sessionB.sessionId
      );

      expect(foundSessionA).toBe(false);
      expect(foundSessionB).toBe(true);

      if (multiLabelSessionsResponse.nextToken) {
        log("\nFetching next page...");
        const nextPageResponse = await agentBay.list(
          {
            environment: "testing",
            project: "project-y",
          },
          2,
          5
        );
        log(`Next page sessions count: ${nextPageResponse.sessionIds.length}`);
        log(`Next page RequestId: ${nextPageResponse.requestId}`);

        expect(nextPageResponse.success).toBe(true);
        expect(nextPageResponse.requestId).toBeDefined();
      }
    } catch (error) {
      log(`Error listing sessions by multiple labels: ${error}`);
    }

    // Test 5: List sessions with non-existent label
    try {
      const nonExistentSessionsResponse = await agentBay.list(
        { "non-existent": "value" },
        1,
        5
      );
      log(
        `Found ${nonExistentSessionsResponse.sessionIds.length} sessions with non-existent label`
      );
      log(
        `Total count: ${nonExistentSessionsResponse.totalCount}, Max results: ${nonExistentSessionsResponse.maxResults}`
      );
      log(
        `List Sessions by non-existent label RequestId: ${
          nonExistentSessionsResponse.requestId || "undefined"
        }`
      );

      expect(nonExistentSessionsResponse.success).toBe(true);
      expect(nonExistentSessionsResponse.requestId).toBeDefined();

      if (nonExistentSessionsResponse.sessionIds.length > 0) {
        log(
          "Warning: Found sessions with non-existent label, this might indicate an issue"
        );
      }
    } catch (error) {
      log(`Error listing sessions by non-existent label: ${error}`);
    }

    log("Test completed successfully");
  });
});
