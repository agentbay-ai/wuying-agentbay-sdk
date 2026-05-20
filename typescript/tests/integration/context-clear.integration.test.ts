// ci-stable
import { AgentBay } from "../../src/agent-bay";
import { ClearContextResult } from "../../src/types/api-response";
import { APIError } from "../../src/exceptions";

// Helper function to get test API key from environment
function getTestAPIKey(): string {
  return process.env.AGENTBAY_API_KEY || "";
}

describe("Context Clear Integration Tests", () => {
  let agentBay: AgentBay;

  beforeAll(() => {
    const apiKey = getTestAPIKey();
    agentBay = new AgentBay({ apiKey });
  });

  describe("clearAsync", () => {
    it("should successfully initiate context clearing", async () => {
      // Create a test context first
      const contextName = `test-context-async-${Date.now()}`;
      const createResult = await agentBay.context.create(contextName);

      if (!createResult.success || !createResult.contextId) {
        throw new Error("Failed to create test context");
      }

      console.log(
        `✓ Created test context: ${contextName} (ID: ${createResult.contextId})`
      );

      // Test ClearAsync
      const result = await agentBay.context.clearAsync(createResult.contextId);

      console.log("✓ ClearAsync result:");
      console.log(`  - Success: ${result.success}`);
      console.log(`  - Status: ${result.status}`);
      console.log(`  - ContextID: ${result.contextId}`);
      console.log(`  - ErrorMessage: ${result.errorMessage}`);
      console.log(`  - RequestID: ${result.requestId}`);

      expect(result.success).toBe(true);
      expect(result.contextId).toBe(createResult.contextId);
      expect(result.status).toBe("clearing");

      // Clean up
      if (createResult.contextId) {
        const ctx = new (await import("../../src/context")).Context(
          createResult.contextId,
          contextName
        );
        const deleteResult = await agentBay.context.delete(ctx);
        if (deleteResult.success) {
          console.log(`✓ Deleted test context: ${createResult.contextId}`);
        }
      }
    });
  });

  describe("clear", () => {
    it("should complete clearing successfully", async () => {
      // Create a test context first
      const contextName = `test-context-clear-${Date.now()}`;
      const createResult = await agentBay.context.create(contextName);

      if (!createResult.success || !createResult.contextId) {
        throw new Error("Failed to create test context");
      }

      console.log(
        `✓ Created test context: ${contextName} (ID: ${createResult.contextId})`
      );

      // Test Clear (synchronous with short timeout)
      let result: ClearContextResult;
      let error: Error | undefined;

      try {
        result = await agentBay.context.clear(createResult.contextId, 30, 2.0);
      } catch (e) {
        error = e as Error;
      }

      console.log("✓ Clear result:");
      if (error) {
        console.log(`  - Error: ${error.message}`);
      } else if (result!) {
        console.log(`  - Success: ${result.success}`);
        console.log(`  - Status: ${result.status}`);
        console.log(`  - ContextID: ${result.contextId}`);
        console.log(`  - ErrorMessage: ${result.errorMessage}`);
        console.log(`  - RequestID: ${result.requestId}`);
      }

      // Note: This might timeout or succeed depending on server processing time
      if (error) {
        console.log(
          "Note: Clear timed out (this is expected if processing takes longer than 30s)"
        );
        expect(error).toBeInstanceOf(APIError);
        expect(error.message).toContain("timed out");
      } else {
        expect(result!.success).toBe(true);
        expect(result!.contextId).toBe(createResult.contextId);
      }

      // Clean up
      if (createResult.contextId) {
        const ctx = new (await import("../../src/context")).Context(
          createResult.contextId,
          contextName
        );
        const deleteResult = await agentBay.context.delete(ctx);
        if (deleteResult.success) {
          console.log(`✓ Deleted test context: ${createResult.contextId}`);
        }
      }
    });
  });

  describe("clearAsync with invalid ID", () => {
    it("should handle invalid context ID", async () => {
      // Test ClearAsync with invalid ID
      let result: ClearContextResult;
      let error: Error | undefined;

      try {
        result = await agentBay.context.clearAsync("invalid-context-id-12345");
      } catch (e) {
        error = e as Error;
      }

      if (error) {
        console.log(
          `✓ Expected error for invalid context ID: ${error.message}`
        );
        expect(error).toBeInstanceOf(APIError);
      } else if (result!) {
        console.log("✓ ClearAsync result:");
        console.log(`  - Success: ${result.success}`);
        console.log(`  - ErrorMessage: ${result.errorMessage}`);

        expect(result.success).toBe(false);
        expect(result.errorMessage).toBeDefined();
      }
    });
  });

  describe("full lifecycle test", () => {
    it("should test complete context clear lifecycle", async () => {
      // Create a test context
      const contextName = `test-context-lifecycle-${Date.now()}`;
      const createResult = await agentBay.context.create(contextName);

      if (!createResult.success || !createResult.contextId) {
        throw new Error("Failed to create test context");
      }

      console.log(
        `✓ Created test context: ${contextName} (ID: ${createResult.contextId})`
      );

      // Step 1: Test ClearAsync
      console.log("\nStep 1: Testing ClearAsync...");
      const asyncResult = await agentBay.context.clearAsync(
        createResult.contextId
      );
      console.log(
        `✓ ClearAsync completed - Success: ${asyncResult.success}, Status: ${asyncResult.status}`
      );
      expect(asyncResult.success).toBe(true);

      // Step 2: Test Clear (with shorter timeout for testing)
      console.log("\nStep 2: Testing Clear (synchronous)...");
      let clearResult: ClearContextResult;
      let clearError: Error | undefined;

      try {
        clearResult = await agentBay.context.clear(
          createResult.contextId,
          10,
          1.0
        );
      } catch (e) {
        clearError = e as Error;
      }

      if (clearError) {
        console.log(`Note: Clear timed out or failed: ${clearError.message}`);
      } else if (clearResult!) {
        console.log(
          `✓ Clear completed - Success: ${clearResult.success}, Status: ${clearResult.status}`
        );
      }

      // Step 3: Verify context still exists
      console.log("\nStep 3: Verifying context exists after clear...");
      const getResult = await agentBay.context.get(contextName, false);
      if (getResult.success && getResult.context) {
        console.log(
          `✓ Context still exists - ID: ${getResult.context.id}, Name: ${getResult.context.name}, State: ${getResult.context.state}`
        );
      }

      // Clean up
      console.log("\nStep 4: Cleaning up test context...");
      if (createResult.contextId) {
        const ctx = new (await import("../../src/context")).Context(
          createResult.contextId,
          contextName
        );
        const deleteResult = await agentBay.context.delete(ctx);
        if (deleteResult.success) {
          console.log(`✓ Deleted test context: ${createResult.contextId}`);
        }
      }
    });
  });

  describe("multiple clear calls", () => {
    it("should handle multiple clear calls", async () => {
      // Create a test context
      const contextName = `test-context-multi-${Date.now()}`;
      const createResult = await agentBay.context.create(contextName);

      if (!createResult.success || !createResult.contextId) {
        throw new Error("Failed to create test context");
      }

      console.log(
        `✓ Created test context: ${contextName} (ID: ${createResult.contextId})`
      );

      // Call ClearAsync multiple times
      for (let i = 1; i <= 3; i++) {
        console.log(`\nTest call ${i}:`);
        const result = await agentBay.context.clearAsync(
          createResult.contextId
        );
        console.log(
          `  ✓ Success: ${result.success}, Status: ${result.status}, RequestID: ${result.requestId}`
        );
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      // Clean up
      if (createResult.contextId) {
        const ctx = new (await import("../../src/context")).Context(
          createResult.contextId,
          contextName
        );
        const deleteResult = await agentBay.context.delete(ctx);
        if (deleteResult.success) {
          console.log(`✓ Deleted test context: ${createResult.contextId}`);
        }
      }
    });
  });
});
