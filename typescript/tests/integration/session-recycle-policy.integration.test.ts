// ci-stable
import { AgentBay, Context, Session } from "../../src";
import {
  ContextSync,
  SyncPolicy,
  newSyncPolicy,
  Lifecycle,
} from "../../src/context-sync";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session RecyclePolicy", () => {
  describe("create session with custom recyclePolicy", () => {
    let agentBay: AgentBay;
    let session: Session;
    let context: Context;

    beforeEach(() => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
    });

    afterEach(async () => {
      if (session) {
        try {
          log("Cleaning up session with custom recyclePolicy...");
          const deleteResponse = await agentBay.delete(session);
          log(
            `Delete Session RequestId: ${
              deleteResponse.requestId || "undefined"
            }`
          );
        } catch (error) {
          log(`Warning: Error deleting session: ${error}`);
        }
      }
      if (context) {
        try {
          log("Cleaning up context...");
          const deleteContextResponse = await agentBay.context.delete(context);
          log(
            `Delete Context RequestId: ${
              deleteContextResponse.requestId || "undefined"
            }`
          );
        } catch (error) {
          log(`Warning: Error deleting context: ${error}`);
        }
      }
    });

    it("should create session with custom recyclePolicy using Lifecycle_1Day", async () => {
      // Create a real context first
      const contextName = `test-recycle-context-${Date.now()}`;
      log(`Creating real context with name: ${contextName}`);
      const createContextResponse = await agentBay.context.create(contextName);
      context = createContextResponse.context!;
      expect(context).toBeDefined();
      expect(context.id).toBeDefined();
      log(`Context created - ID: ${context.id}, Name: ${context.name}`);

      const customSyncPolicy: SyncPolicy = {
        ...newSyncPolicy(),
        recyclePolicy: {
          lifecycle: Lifecycle.Lifecycle_1Day,
          paths: [""],
        },
      };

      const contextSync = new ContextSync(
        context.id,
        "/home/wuying",
        customSyncPolicy
      );

      log("Creating session with custom recyclePolicy...");
      log(
        `RecyclePolicy lifecycle: ${customSyncPolicy.recyclePolicy?.lifecycle}`
      );
      log(
        `RecyclePolicy paths: ${JSON.stringify(
          customSyncPolicy.recyclePolicy?.paths
        )}`
      );

      const createResponse = await agentBay.create({
        labels: { test: "recyclePolicy", lifecycle: "1day" },
        contextSync: [contextSync],
      });

      expect(createResponse.success).toBe(true);
      expect(createResponse.requestId).toBeDefined();
      expect(typeof createResponse.requestId).toBe("string");
      expect(createResponse.requestId!.length).toBeGreaterThan(0);
      expect(createResponse.session).toBeDefined();
      expect(createResponse.errorMessage).toBeUndefined();

      session = createResponse.session!;
      log(`Session created successfully with ID: ${session.sessionId}`);
      log(
        `Create Session RequestId: ${createResponse.requestId || "undefined"}`
      );

      expect(session.sessionId).toBeDefined();
      expect(session.sessionId.length).toBeGreaterThan(0);

      log(
        "Session with custom recyclePolicy created and verified successfully"
      );
    });
  });

  describe("recyclePolicy validation", () => {
    it("should throw error when creating ContextSync with invalid recyclePolicy path", () => {
      const invalidSyncPolicy: SyncPolicy = {
        ...newSyncPolicy(),
        recyclePolicy: {
          lifecycle: Lifecycle.Lifecycle_1Day,
          paths: ["/invalid/path/*"],
        },
      };

      log("Testing ContextSync creation with invalid recyclePolicy path...");
      log(`Invalid path: ${invalidSyncPolicy.recyclePolicy?.paths[0]}`);

      expect(() => {
        new ContextSync(
          "test-invalid-context",
          "/test/path",
          invalidSyncPolicy
        );
      }).toThrow(/Wildcard patterns are not supported in path/);

      log("ContextSync correctly threw error for invalid recyclePolicy path");
    });

    it("should throw error when creating ContextSync with invalid lifecycle", () => {
      log("Testing ContextSync creation with invalid lifecycle...");

      const invalidSyncPolicy: SyncPolicy = {
        ...newSyncPolicy(),
        recyclePolicy: {
          lifecycle: "invalid_lifecycle" as any,
          paths: [""],
        },
      };

      log(`Invalid lifecycle: ${invalidSyncPolicy.recyclePolicy?.lifecycle}`);

      expect(() => {
        new ContextSync(
          "invalid-lifecycle-context",
          "/test/path",
          invalidSyncPolicy
        );
      }).toThrow(
        /Invalid lifecycle value: invalid_lifecycle\. Valid values are:/
      );

      log("ContextSync correctly threw error for invalid lifecycle");
    });

    it("should throw error when creating ContextSync with combined invalid configuration", () => {
      log(
        "Testing ContextSync creation with combined invalid lifecycle and invalid paths..."
      );

      const combinedInvalidSyncPolicy: SyncPolicy = {
        ...newSyncPolicy(),
        recyclePolicy: {
          lifecycle: "invalid_lifecycle" as any,
          paths: ["/invalid/path/*"],
        },
      };

      log(
        `Invalid lifecycle: ${combinedInvalidSyncPolicy.recyclePolicy?.lifecycle}`
      );
      log(`Invalid path: ${combinedInvalidSyncPolicy.recyclePolicy?.paths[0]}`);

      expect(() => {
        new ContextSync(
          "combined-invalid-context",
          "/test/path",
          combinedInvalidSyncPolicy
        );
      }).toThrow(
        /Invalid lifecycle value: invalid_lifecycle\. Valid values are:/
      );

      log(
        "ContextSync correctly threw error for combined invalid configuration"
      );
    });
  });
});
