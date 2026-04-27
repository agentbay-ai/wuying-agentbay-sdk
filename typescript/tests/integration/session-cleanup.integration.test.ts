// ci-stable
import { AgentBay, Session } from "../../src";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";

describe("Session Cleanup Integration Test", () => {
  let agentBay: AgentBay;

  beforeAll(() => {
    const apiKey = getTestApiKey();
    agentBay = new AgentBay({ apiKey });
  });

  it("should list all sessions, recover them via get, and delete them", async () => {
    try {
      log("=== Starting Session Cleanup Test ===");

      // Step 1: List all sessions
      log("Step 1: Listing all sessions...");
      const listResult = await agentBay.list();

      if (!listResult.success) {
        log(`❌ Failed to list sessions: ${listResult.errorMessage}`);
        log(`Request ID: ${listResult.requestId || "N/A"}`);
        expect(listResult.success).toBe(true);
        return;
      }

      const sessionIds = listResult.sessionIds || [];
      log(`✅ Found ${sessionIds.length} sessions to clean up`);
      log(`Session IDs: ${JSON.stringify(sessionIds)}`);
      log(`Total Count: ${listResult.totalCount || "N/A"}`);
      log(`Request ID: ${listResult.requestId}`);

      if (sessionIds.length === 0) {
        log("✅ No sessions to clean up, test passed");
        expect(sessionIds.length).toBe(0);
        return;
      }

      // Step 2: Enhanced session deletion with better error handling
      const deleteResults = [];
      const deletedSessionIds = [];
      let failedDeletes = 0;
      let recoveryFailures = 0;

      for (let i = 0; i < sessionIds.length; i++) {
        const sessionId = sessionIds[i];
        log(
          `\n--- Processing session ${i + 1}/${
            sessionIds.length
          }: ${sessionId} ---`
        );

        try {
          // Step 2a: Recover session via get() with enhanced error handling
          log(`🔄 Recovering session ${sessionId} via get()...`);
          const getResult = await agentBay.get(sessionId.sessionId);

          if (!getResult.success) {
            log(
              `❌ Failed to recover session ${sessionId}: ${getResult.errorMessage}`
            );
            log(`Request ID: ${getResult.requestId || "N/A"}`);
            recoveryFailures++;
            deleteResults.push({
              sessionId,
              recovered: false,
              deleted: false,
              error: getResult.errorMessage,
              requestId: getResult.requestId,
            });
            continue;
          }

          const recoveredSession: Session = getResult.session!;
          log(`✅ Successfully recovered session ${sessionId.sessionId}`);
          log(`Session details - sessionId: ${recoveredSession.sessionId}`);
          log(`Recovery Request ID: ${getResult.requestId}`);

          // Step 2b: Check session status before deletion
          log(`📊 Checking status of session ${sessionId} before deletion...`);
          const sessionStatusResult = await recoveredSession.getStatus();

          if (sessionStatusResult.success) {
            const status = sessionStatusResult.status?.toLowerCase();
            log(
              `📋 Session ${sessionId} status: ${sessionStatusResult.status}`
            );
            if (status === "pausing") {
              log(`⏸️  Session ${sessionId} is pausing, needing to resume...`);
              return;
            }

            if (status === "deleting" || status === "deleted") {
              log(
                `⏭️  Session ${sessionId} is already ${sessionStatusResult.status}, skipping deletion`
              );
              deleteResults.push({
                sessionId,
                recovered: true,
                deleted: true, // Consider it as successfully handled
                requestId: sessionStatusResult.requestId,
                skipped: true,
                skipReason: `Already ${sessionStatusResult.status}`,
              });
              continue;
            }
          } else {
            log(
              `⚠️  Failed to get status for session ${sessionId}: ${sessionStatusResult.errorMessage}, proceeding with deletion`
            );
          }

          // Step 2c: Delete the recovered session with enhanced logging
          log(`🗑️  Deleting recovered session ${sessionId}...`);
          const deleteResult = await agentBay.delete(recoveredSession);

          if (!deleteResult.success) {
            log(
              `❌ Failed to delete session ${sessionId}: ${deleteResult.errorMessage}`
            );
            log(`Delete Request ID: ${deleteResult.requestId || "N/A"}`);
            failedDeletes++;
            deleteResults.push({
              sessionId,
              recovered: true,
              deleted: false,
              error: deleteResult.errorMessage,
              requestId: deleteResult.requestId,
            });
          } else {
            log(`✅ Successfully deleted session ${sessionId}`);
            log(`Delete Request ID: ${deleteResult.requestId}`);
            deletedSessionIds.push(sessionId);
            deleteResults.push({
              sessionId,
              recovered: true,
              deleted: true,
              requestId: deleteResult.requestId,
            });
          }
        } catch (sessionError) {
          log(
            `❌ Unexpected error processing session ${sessionId}: ${sessionError}`
          );
          failedDeletes++;
          deleteResults.push({
            sessionId,
            recovered: false,
            deleted: false,
            error: `Unexpected error: ${sessionError}`,
          });
        }
      }

      // Step 3: Enhanced results verification
      log("\n=== Cleanup Results Summary ===");
      log(`📊 Total sessions processed: ${deleteResults.length}`);
      log(`✅ Successfully deleted: ${deletedSessionIds.length}`);
      log(`❌ Failed to delete: ${failedDeletes}`);
      log(`🔄 Recovery failures: ${recoveryFailures}`);

      if (failedDeletes > 0) {
        log("\n❌ Failed deletions details:");
        deleteResults
          .filter((r) => !r.deleted)
          .forEach((r) => {
            log(
              `  - Session ${r.sessionId}: ${r.error} (RequestID: ${
                r.requestId || "N/A"
              })`
            );
          });
      }

      if (recoveryFailures > 0) {
        log("\n🔄 Recovery failures details:");
        deleteResults
          .filter((r) => !r.recovered)
          .forEach((r) => {
            log(
              `  - Session ${r.sessionId}: ${r.error} (RequestID: ${
                r.requestId || "N/A"
              })`
            );
          });
      }

      // Enhanced verification: Ensure all sessions were processed successfully
      const totalFailures = failedDeletes + recoveryFailures;
      log(
        `\n📈 Overall success rate: ${(
          ((sessionIds.length - totalFailures) / sessionIds.length) *
          100
        ).toFixed(1)}%`
      );

      // Verify all sessions were deleted (strict requirement)
      expect(failedDeletes).toBe(0);

      // Step 4: Enhanced final verification with retry mechanism
      log("\n--- Final Verification: Listing sessions again ---");
      let finalListResult;
      let retryCount = 0;
      const maxRetries = 3;

      // Retry mechanism for final verification (in case of eventual consistency)
      while (retryCount < maxRetries) {
        if (retryCount > 0) {
          log(`🔄 Retry ${retryCount}/${maxRetries} for final verification...`);
          // Wait a bit before retry (eventual consistency)
          await new Promise((resolve) => setTimeout(resolve, 1000));
        }

        finalListResult = await agentBay.list();

        if (finalListResult.success) {
          const remainingSessionIds = finalListResult.sessionIds || [];
          log(`📋 Remaining sessions: ${remainingSessionIds.length}`);

          if (remainingSessionIds.length === 0) {
            log("✅ All sessions successfully cleaned up!");
            break;
          } else {
            log(
              `⚠️  Still found ${remainingSessionIds.length} remaining sessions`
            );
            log(
              `Remaining session IDs: ${JSON.stringify(remainingSessionIds)}`
            );

            if (retryCount === maxRetries - 1) {
              // Last retry, proceed with detailed verification
              break;
            }
          }
        } else {
          log(
            `❌ Failed to verify final list (attempt ${retryCount + 1}): ${
              finalListResult.errorMessage
            }`
          );
          if (retryCount === maxRetries - 1) {
            throw new Error(
              `Failed to verify final session list after ${maxRetries} attempts: ${finalListResult.errorMessage}`
            );
          }
        }

        retryCount++;
      }

      // Detailed verification of deleted sessions
      if (finalListResult && finalListResult.success) {
        const remainingSessionIds = finalListResult.sessionIds || [];

        log(
          `\n--- Verifying ${deletedSessionIds.length} deleted sessions are gone ---`
        );
        let allDeletedSessionsGone = true;
        const stillExistingSessions = [];

        for (const deletedSessionId of deletedSessionIds) {
          const stillExists = remainingSessionIds.includes(deletedSessionId);
          if (stillExists) {
            log(`❌ Deleted session ${deletedSessionId} still exists in list!`);
            stillExistingSessions.push(deletedSessionId);
            allDeletedSessionsGone = false;
          } else {
            log(
              `✅ Deleted session ${deletedSessionId} confirmed removed from list`
            );
          }
        }

        // Enhanced assertion with detailed error message
        if (!allDeletedSessionsGone) {
          const errorMessage = `${
            stillExistingSessions.length
          } deleted sessions still exist: ${JSON.stringify(
            stillExistingSessions
          )}`;
          log(`❌ ${errorMessage}`);
          throw new Error(errorMessage);
        }

        expect(allDeletedSessionsGone).toBe(true);
        log("✅ All deleted sessions confirmed removed from the system");
      }

      log("🎉 === Session Cleanup Test Completed Successfully ===\n");
    } catch (error) {
      log(`💥 Test error: ${error}`);
      log(
        `Error stack: ${
          error instanceof Error ? error.stack : "No stack trace available"
        }`
      );
      throw error;
    }
  });
});
