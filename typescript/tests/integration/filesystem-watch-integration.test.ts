// ci-stable
import { AgentBay, Session } from "../../src";
import { log } from "../../src/utils/logger";
import { FileChangeEvent } from "../../src/filesystem/filesystem";
import { getTestApiKey } from "../utils/test-helpers";

describe("FileSystem Watch Directory Integration Tests", () => {
  let agentBay: AgentBay;
  let session: Session;

  beforeAll(async () => {
    // Skip if no API key
    const apiKey = getTestApiKey();
    if (!apiKey) {
      log(
        "Skipping integration test: AGENTBAY_API_KEY environment variable not set"
      );
      return;
    }

    log("=== Testing watch_directory functionality ===");

    // Initialize AgentBay client
    agentBay = new AgentBay({ apiKey });
    expect(agentBay).toBeDefined();
    log("✅ AgentBay client initialized");

    // Create session with code_latest ImageId
    const sessionResult = await agentBay.create({
      imageId: "code_latest",
    });
    expect(sessionResult.success).toBe(true);
    expect(sessionResult.session).toBeDefined();

    session = sessionResult.session!;
    log(`✅ Session created successfully with ID: ${session.sessionId}`);
  });

  afterAll(async () => {
    if (session && agentBay) {
      log("\n7. Cleaning up session...");
      const deleteResult = await agentBay.delete(session);
      if (deleteResult.success) {
        log("✅ Session deleted successfully");
      } else {
        log(`❌ Failed to delete session: ${deleteResult.errorMessage}`);
      }
    }
  });

  it("should NOT trigger callbacks after watch is stopped", async () => {
    const apiKey = getTestApiKey();
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const testDir = `/tmp/watch_stop_test_ts_${Date.now()}`;

    log(`\n1. Creating test directory: ${testDir}`);
    const createDirResult = await session.fileSystem.createDirectory(testDir);
    expect(createDirResult.success).toBe(true);

    const detectedEvents: FileChangeEvent[] = [];
    const fileChangeCallback = (events: FileChangeEvent[]) => {
      detectedEvents.push(...events);
      log(`🔔 Callback triggered with ${events.length} events`);
    };

    let shouldStop = false;
    const stopSignal = {
      get aborted() {
        return shouldStop;
      },
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
      onabort: null,
      reason: undefined,
      throwIfAborted: () => {},
    } as AbortSignal;

    log("\n2. Starting directory monitoring...");
    const { monitoring, ready } = session.fileSystem.watchDirectory(
      testDir,
      fileChangeCallback,
      500,
      stopSignal
    );
    await ready;
    log("✅ Monitoring started");

    log("\n3. Creating a file (should trigger events)...");
    const writeResult = await session.fileSystem.writeFile(
      `${testDir}/before_stop.txt`,
      "before stop"
    );
    expect(writeResult.success).toBe(true);

    await new Promise((resolve) => setTimeout(resolve, 3000));
    const eventsBeforeStop = detectedEvents.length;
    log(`Events before stop: ${eventsBeforeStop}`);
    expect(eventsBeforeStop).toBeGreaterThan(0);

    log("\n4. Stopping directory monitoring...");
    shouldStop = true;
    await monitoring;
    log("✅ Monitoring stopped");

    log("\n5. Creating a file AFTER stop (should NOT trigger events)...");
    const writeAfter = await session.fileSystem.writeFile(
      `${testDir}/after_stop.txt`,
      "after stop"
    );
    expect(writeAfter.success).toBe(true);

    await new Promise((resolve) => setTimeout(resolve, 3000));
    const eventsAfterStop = detectedEvents.length;
    const newEvents = eventsAfterStop - eventsBeforeStop;
    log(`Events after stop: ${eventsAfterStop}, new: ${newEvents}`);

    expect(newEvents).toBe(0);
    log("✅ No events after stop — negative verification passed!");
  });

  it("should detect exactly 5 events from 3 writeFile operations", async () => {
    const apiKey = getTestApiKey();
    if (!apiKey) {
      log("Skipping test: AGENTBAY_API_KEY not set");
      return;
    }

    const testDir = "/tmp/watch_test_integration_ts";

    // Create the test directory
    log(`\n1. Creating test directory: ${testDir}`);
    const createDirResult = await session.fileSystem.createDirectory(testDir);
    expect(createDirResult.success).toBe(true);
    log("✅ Test directory created");

    // Storage for detected events
    const detectedEvents: FileChangeEvent[] = [];
    const callbackCalls: number[] = [];

    const fileChangeCallback = (events: FileChangeEvent[]) => {
      callbackCalls.push(events.length);
      detectedEvents.push(...events);
      log(`\n🔔 Callback triggered with ${events.length} events:`);
      for (const event of events) {
        log(`   - ${event.eventType}: ${event.path} (${event.pathType})`);
      }
    };

    // Start directory monitoring
    log("\n2. Starting directory monitoring...");

    // Create a simple stop mechanism
    let shouldStop = false;
    const stopSignal = {
      get aborted() {
        return shouldStop;
      },
      addEventListener: (_type: string, _listener: any) => {
        /* no-op */
      },
      removeEventListener: (_type: string, _listener: any) => {
        /* no-op */
      },
      dispatchEvent: (_event: any) => false,
      onabort: null,
      reason: undefined,
      throwIfAborted: () => {
        /* no-op */
      },
    } as AbortSignal;

    const { monitoring, ready } = session.fileSystem.watchDirectory(
      testDir,
      fileChangeCallback,
      500, // Poll every 0.5 seconds for faster testing
      stopSignal
    );
    log("✅ Directory monitoring started");

    // Wait for baseline to be established before performing file operations
    await ready;

    try {
      // Test 1: Create a new file
      log("\n3. Creating a new file...");
      const writeResult = await session.fileSystem.writeFile(
        `${testDir}/test1.txt`,
        "Initial content"
      );
      log(`Write file result: ${writeResult.success}`);
      expect(writeResult.success).toBe(true);

      // Wait for detection
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Test 2: Modify the file
      log("\n4. Modifying the file...");
      const modifyResult = await session.fileSystem.writeFile(
        `${testDir}/test1.txt`,
        "Modified content"
      );
      log(`Modify file result: ${modifyResult.success}`);
      expect(modifyResult.success).toBe(true);

      // Wait for detection
      await new Promise((resolve) => setTimeout(resolve, 2000));

      // Test 3: Create another file
      log("\n5. Creating another file...");
      const writeResult2 = await session.fileSystem.writeFile(
        `${testDir}/test2.txt`,
        "Second file content"
      );
      log(`Write second file result: ${writeResult2.success}`);
      expect(writeResult2.success).toBe(true);

      // Wait for detection
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } finally {
      // Stop monitoring
      log("\n6. Stopping directory monitoring...");
      shouldStop = true;
      await monitoring;
      log("✅ Directory monitoring stopped");
    }

    // Analyze results
    log("\n=== RESULTS ===");
    log(`Total callback calls: ${callbackCalls.length}`);
    log(`Total events detected: ${detectedEvents.length}`);
    log(`Callback call sizes: [${callbackCalls.join(", ")}]`);

    log("\nDetected events:");
    for (let i = 0; i < detectedEvents.length; i++) {
      log(
        `  ${i + 1}. ${detectedEvents[i].eventType}: ${
          detectedEvents[i].path
        } (${detectedEvents[i].pathType})`
      );
    }

    // Verify exact number of events - must be exactly 5
    // writeFile to non-existent file produces: create + modify (2 events)
    // writeFile to existing file produces: modify (1 event)
    // Expected: test1.txt creation (create+modify) + test1.txt modification (modify) + test2.txt creation (create+modify) = 5 events
    const expectedEvents = 5;
    if (detectedEvents.length !== expectedEvents) {
      log(
        `❌ Expected exactly ${expectedEvents} events, got ${detectedEvents.length}`
      );
      log("Expected breakdown:");
      log("  - writeFile test1.txt (new): create + modify = 2 events");
      log("  - writeFile test1.txt (existing): modify = 1 event");
      log("  - writeFile test2.txt (new): create + modify = 2 events");
      log("  - Total: 2 + 1 + 2 = 5 events");
    } else {
      log(`✅ Captured expected number of events: ${detectedEvents.length}`);
    }

    expect(detectedEvents.length).toBe(expectedEvents);

    // Verify event types and counts
    const createEvents = detectedEvents.filter(
      (event) => event.eventType === "create"
    ).length;
    const modifyEvents = detectedEvents.filter(
      (event) => event.eventType === "modify"
    ).length;

    log("\nEvent type breakdown:");
    log(`  Create events: ${createEvents} (expected: 2)`);
    log(`  Modify events: ${modifyEvents} (expected: 3)`);

    // Strict validation of event types
    const expectedCreateEvents = 2;
    const expectedModifyEvents = 3;

    expect(createEvents).toBe(expectedCreateEvents);
    expect(modifyEvents).toBe(expectedModifyEvents);
    expect(detectedEvents.length).toBe(expectedEvents);

    if (
      createEvents === expectedCreateEvents &&
      modifyEvents === expectedModifyEvents
    ) {
      log("✅ Event type distribution is correct");
    } else {
      log("❌ Event type distribution is incorrect");
      throw new Error(
        `Event type validation failed: got ${createEvents} create + ${modifyEvents} modify, expected ${expectedCreateEvents} create + ${expectedModifyEvents} modify`
      );
    }

    // Verify deduplication
    const eventKeys = new Set<string>();
    let duplicates = 0;
    for (const event of detectedEvents) {
      const eventKey = `${event.eventType}:${event.path}:${event.pathType}`;
      if (eventKeys.has(eventKey)) {
        duplicates++;
      } else {
        eventKeys.add(eventKey);
      }
    }

    log("\nDeduplication check:");
    log(`  Unique events: ${eventKeys.size}`);
    log(`  Duplicate events: ${duplicates}`);

    if (duplicates === 0) {
      log("✅ Event deduplication is working correctly");
    } else {
      log("⚠️  Some duplicate events were detected");
    }

    // Summary
    if (
      detectedEvents.length === expectedEvents &&
      createEvents === expectedCreateEvents &&
      modifyEvents === expectedModifyEvents
    ) {
      log("\n✅ watch_directory integration test completed successfully!");
      log("All expected events were detected with correct types.");
    } else {
      log("\n❌ watch_directory integration test failed!");
      log(
        `Expected ${expectedEvents} events (${expectedCreateEvents} create + ${expectedModifyEvents} modify), got ${detectedEvents.length} events (${createEvents} create + ${modifyEvents} modify)`
      );
      throw new Error("Integration test validation failed");
    }
  });
});
