// ci-stable
import { AgentBay, CreateSessionParams, Session } from "../../src";
import {
  ContextSync,
  newContextSync,
  newUploadPolicy,
  newSyncPolicy,
  UploadMode,
} from "../../src/context-sync";
import { FileSystem } from "../../src/filesystem/filesystem";
import { log } from "../../src/utils/logger";

function getTestAPIKey(): string {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    log(
      "Warning: AGENTBAY_API_KEY environment variable not set. Using default test key."
    );
    return "akm-xxx"; // Replace with your test API key
  }
  return apiKey;
}

function generateUniqueId(): string {
  const timestamp = Date.now() * 1000 + Math.floor(Math.random() * 1000);
  const randomPart = Math.floor(Math.random() * 10000);
  return `${timestamp}-${randomPart}`;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

describe("Context Sync Upload Mode Integration Tests", () => {
  let agentBay: AgentBay;
  let uniqueId: string;

  beforeAll(async () => {
    const apiKey = getTestAPIKey();
    agentBay = new AgentBay({ apiKey });
    uniqueId = generateUniqueId();

    log(`Using unique ID for test: ${uniqueId}`);
  });

  describe("Basic Functionality Tests", () => {
    test("should create session with default File upload mode", async () => {
      log(
        "\n=== Testing basic functionality with default File upload mode ==="
      );

      // Step 1: Use context.get method to generate contextId
      const contextName = `test-context-${uniqueId}`;
      log(`Creating context with name: ${contextName}`);

      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);
      expect(contextResult.contextId).toBeDefined();
      expect(contextResult.contextId).not.toBe("");

      log(`Generated contextId: ${contextResult.contextId}`);
      log(`Context get request ID: ${contextResult.requestId}`);

      // Step 2: Create session with contextSync using default File uploadMode
      const syncPolicy = newSyncPolicy(); // Uses default uploadMode "File"

      const contextSync = new ContextSync(
        contextResult.contextId,
        "/tmp/test",
        syncPolicy
      );

      const sessionParams = {
        labels: {
          test: `upload-mode-${uniqueId}`,
          type: "basic-functionality",
        },
        contextSync: [contextSync],
      };

      log("Creating session with default File upload mode...");
      const sessionResult = await agentBay.create(sessionParams);

      // Step 3: Verify session creation success
      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.requestId).toBeDefined();
      expect(sessionResult.requestId).not.toBe("");

      const session = sessionResult.session!;

      log(`✅ Session created successfully!`);
      log(`Session ID: ${session.sessionId}`);
      log(`Session creation request ID: ${sessionResult.requestId}`);

      // Get session status
      const sessionInfo = await session.getStatus();
      expect(sessionInfo.success).toBe(true);
      expect(sessionInfo.status).toBeDefined();

      log(`Status: ${sessionInfo.status}`);
      log(`Get status request ID: ${sessionInfo.requestId}`);

      // Delete session after test
      await agentBay.delete(session, true);

      log("✅ All basic functionality tests passed!");
    });
  });

  describe("Upload Mode Validation Tests", () => {
    test("should work with contextId and path using Archive mode and write file", async () => {
      log(
        "\n=== Testing contextId and path usage with Archive mode and code execution ==="
      );

      const contextName = `archive-mode-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.contextId).toBeDefined();
      expect(contextResult.contextId).not.toBe("");

      log(`Generated contextId: ${contextResult.contextId}`);

      // Use newSyncPolicy and modify uploadMode to Archive
      const syncPolicy = newSyncPolicy();
      syncPolicy.uploadPolicy!.uploadMode = UploadMode.Archive; // Set uploadMode to Archive

      const contextSync = newContextSync(
        contextResult.contextId,
        "/tmp/archive-mode-test",
        syncPolicy
      );

      expect(contextSync.contextId).toBe(contextResult.contextId);
      expect(contextSync.path).toBe("/tmp/archive-mode-test");
      expect(contextSync.policy?.uploadPolicy?.uploadMode).toBe(
        UploadMode.Archive
      );

      log(
        "✅ newContextSync works correctly with contextId and path using Archive mode"
      );

      // Create session with the contextSync
      const sessionParams = {
        labels: {
          test: `archive-mode-${uniqueId}`,
          type: "contextId-path-validation",
        },
        contextSync: [contextSync],
      };

      log("Creating session with Archive mode contextSync...");
      const sessionResult = await agentBay.create(sessionParams);

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();
      expect(sessionResult.requestId).toBeDefined();

      const session = sessionResult.session!;
      // Get session status
      const sessionInfo = await session.getStatus();
      expect(sessionInfo.success).toBe(true);
      expect(sessionInfo.status).toBeDefined();

      log(`Status: ${sessionInfo.status}`);

      log(`✅ Session created successfully with ID: ${session.sessionId}`);
      log(`Session creation request ID: ${sessionResult.requestId}`);

      // Write a 5KB file using FileSystem
      log("Writing 5KB file using FileSystem...");

      const fileSystem = new FileSystem(session);

      // Generate 5KB content (approximately 5120 bytes)
      const contentSize = 5 * 1024; // 5KB
      const baseContent =
        "Archive mode test successful! This is a test file created in the session path. ";
      const repeatedContent = baseContent.repeat(
        Math.ceil(contentSize / baseContent.length)
      );
      const fileContent = repeatedContent.substring(0, contentSize);

      // Create file path in the session path directory
      const filePath = "/tmp/archive-mode-test/test-file-5kb.txt";

      log(`Creating file: ${filePath}`);
      log(`File content size: ${fileContent.length} bytes`);

      const writeResult = await fileSystem.writeFile(
        filePath,
        fileContent,
        "overwrite"
      );

      // Verify file write success
      expect(writeResult.success).toBe(true);
      expect(writeResult.requestId).toBeDefined();
      expect(writeResult.requestId).not.toBe("");

      log(`✅ File write successful!`);
      log(`Write file request ID: ${writeResult.requestId}`);

      // Trigger upload by deleting session with syncContext=true
      log("Deleting session with syncContext=true to trigger upload...");
      const deleteResult = await agentBay.delete(session, true);

      expect(deleteResult.success).toBe(true);
      expect(deleteResult.requestId).toBeDefined();

      log(`✅ Session deleted with sync successful!`);
      log(`Delete request ID: ${deleteResult.requestId}`);

      // Wait for OSS upload to complete
      await new Promise((resolve) => setTimeout(resolve, 5000));

      // List files in context sync directory
      log("Listing files in context sync directory...");

      // Use the sync directory path
      const syncDirPath = "/tmp/archive-mode-test";

      const listResult = await agentBay.context.listFiles(
        contextResult.contextId,
        syncDirPath,
        1,
        10
      );

      // Verify ListFiles success
      expect(listResult.success).toBe(true);
      expect(listResult.requestId).toBeDefined();
      expect(listResult.requestId).not.toBe("");

      log(`✅ List files successful!`);
      log(`List files request ID: ${listResult.requestId}`);
      log(`Total files found: ${listResult.entries.length}`);

      if (listResult.entries.length > 0) {
        log("📋 Files in context sync directory:");
        listResult.entries.forEach((entry, index) => {
          log(`  [${index}] FilePath: ${entry.filePath}`);
          log(`      FileType: ${entry.fileType}`);
          log(`      FileName: ${entry.fileName}`);
          log(`      Size: ${entry.size} bytes`);
        });
      } else {
        log("No files found in context sync directory");
      }

      log(
        "✅ Archive mode contextSync with contextId and path works correctly, and file operations completed successfully"
      );
    });
  });
  describe("Upload Mode Validation Tests", () => {
    test("should throw error when using invalid uploadMode with newContextSync", async () => {
      log("\n=== Testing invalid uploadMode with newContextSync ===");

      const contextName = `invalid-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Create invalid upload policy
      const invalidUploadPolicy = newUploadPolicy();
      (invalidUploadPolicy as any).uploadMode = "InvalidMode"; // Invalid value

      const invalidSyncPolicy = newSyncPolicy();
      invalidSyncPolicy.uploadPolicy = invalidUploadPolicy;

      // Test with newContextSync - should throw error during validation
      expect(() => {
        newContextSync(contextResult.contextId, "/tmp/test", invalidSyncPolicy);
      }).toThrow(
        `Invalid uploadMode value: InvalidMode. Valid values are: ${UploadMode.File}, ${UploadMode.Archive}`
      );

      log("✅ newContextSync correctly threw error for invalid uploadMode");
    });

    test("should throw error when using invalid uploadMode with withPolicy", async () => {
      log("\n=== Testing invalid uploadMode with withPolicy ===");

      const contextName = `invalid-policy-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Create a valid context sync first
      const contextSync = new ContextSync(contextResult.contextId, "/tmp/test");

      // Create invalid upload policy
      const invalidUploadPolicy = newUploadPolicy();
      (invalidUploadPolicy as any).uploadMode = "WrongValue"; // Invalid value

      const invalidSyncPolicy = newSyncPolicy();
      invalidSyncPolicy.uploadPolicy = invalidUploadPolicy;

      // Test with withPolicy - should throw error during validation
      expect(() => {
        contextSync.withPolicy(invalidSyncPolicy);
      }).toThrow(
        `Invalid uploadMode value: WrongValue. Valid values are: ${UploadMode.File}, ${UploadMode.Archive}`
      );

      log("✅ withPolicy correctly threw error for invalid uploadMode");
    });

    test("should accept valid uploadMode values", async () => {
      log("\n=== Testing valid uploadMode values ===");

      const contextName = `valid-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success).toBe(true);

      // Test "File" mode
      const fileUploadPolicy = newUploadPolicy();
      fileUploadPolicy.uploadMode = UploadMode.File;

      const fileSyncPolicy = newSyncPolicy();
      fileSyncPolicy.uploadPolicy = fileUploadPolicy;

      expect(() => {
        newContextSync(
          contextResult.contextId,
          "/tmp/test-file",
          fileSyncPolicy
        );
      }).not.toThrow();

      log("✅ 'File' uploadMode accepted successfully");

      // Test "Archive" mode
      const archiveUploadPolicy = newUploadPolicy();
      archiveUploadPolicy.uploadMode = UploadMode.Archive;

      const archiveSyncPolicy = newSyncPolicy();
      archiveSyncPolicy.uploadPolicy = archiveUploadPolicy;

      expect(() => {
        newContextSync(
          contextResult.contextId,
          "/tmp/test-archive",
          archiveSyncPolicy
        );
      }).not.toThrow();

      log("✅ 'Archive' uploadMode accepted successfully");
    });
  });

  test.skip(
    "should store excluded paths as individual files when using Archive mode with archiveExcludePaths",
    async () => {
       // Online not yet published, skipping for now

      log(
        "\n=== Testing Archive mode with archiveExcludePaths (hybrid storage) ==="
      );

      const contextName = `archive-exclude-context-${uniqueId}`;
      const contextResult = await agentBay.context.get(contextName, true);

      expect(contextResult.success).toBe(true);
      expect(contextResult.contextId).toBeDefined();
      expect(contextResult.contextId).not.toBe("");

      const syncPath = `/tmp/archive-exclude-${uniqueId}`;
      const syncPolicy = newSyncPolicy();
      syncPolicy.uploadPolicy!.uploadMode = UploadMode.Archive;
      syncPolicy.uploadPolicy!.archiveExcludePaths = ["important/", "config.json"];

      expect(syncPolicy.uploadPolicy?.archiveExcludePaths).toEqual([
        "important/",
        "config.json",
      ]);

      const contextSync = newContextSync(
        contextResult.contextId,
        syncPath,
        syncPolicy
      );

      const sessionParams = {
        labels: {
          test: `archive-exclude-${uniqueId}`,
          type: "archive-exclude-paths",
        },
        contextSync: [contextSync],
      };

      log("Creating session with Archive mode + archiveExcludePaths...");
      const sessionResult = await agentBay.create(sessionParams);

      expect(sessionResult.success).toBe(true);
      expect(sessionResult.session).toBeDefined();

      const session = sessionResult.session!;

      const fileSystem = new FileSystem(session);

      let dirResult = await fileSystem.createDirectory(`${syncPath}/important`);
      expect(dirResult.success).toBe(true);
      dirResult = await fileSystem.createDirectory(`${syncPath}/regular`);
      expect(dirResult.success).toBe(true);

      let writeResult = await fileSystem.writeFile(
        `${syncPath}/important/data.txt`,
        "This file should be stored individually (excluded from archive)",
        "overwrite"
      );
      expect(writeResult.success).toBe(true);

      writeResult = await fileSystem.writeFile(
        `${syncPath}/config.json`,
        '{"key": "value", "setting": true}',
        "overwrite"
      );
      expect(writeResult.success).toBe(true);

      writeResult = await fileSystem.writeFile(
        `${syncPath}/regular/data.txt`,
        "This file should be archived with the rest",
        "overwrite"
      );
      expect(writeResult.success).toBe(true);

      log("All files written; deleting session with sync...");

      const deleteResult = await agentBay.delete(session, true);
      expect(deleteResult.success).toBe(true);

      let listResult = await agentBay.context.listFiles(
        contextResult.contextId,
        syncPath,
        1,
        20
      );

      for (
        let attempt = 0;
        attempt < 20 &&
        (!listResult.success || listResult.entries.length === 0);
        attempt++
      ) {
        await sleep(2000);
        listResult = await agentBay.context.listFiles(
          contextResult.contextId,
          syncPath,
          1,
          20
        );
      }

      expect(listResult.success).toBe(true);
      expect(listResult.entries.length).toBeGreaterThan(0);

      const filePaths = listResult.entries.map((e) => e.filePath);
      const fileNames = listResult.entries.map((e) => e.fileName ?? "");

      const hasImportant = filePaths.some((p) => p.includes("important"));
      const hasConfig = fileNames.some((n) => n.includes("config.json"));

      log(
        `Excluded paths present individually — important: ${hasImportant}, config.json: ${hasConfig}`
      );
      log(`Files found: ${fileNames.join(", ")}`);

      expect(hasImportant).toBe(true);
      expect(hasConfig).toBe(true);

      // Check for download URL on excluded files (passive check from entry properties)
      for (const entry of listResult.entries) {
        const isExcluded =
          entry.filePath.includes("important") ||
          (entry.fileName?.includes("config.json") ?? false);
        if (!isExcluded) {
          continue;
        }
        const presignedUrl = (entry as any).presignedUrl || (entry as any).downloadUrl;
        if (presignedUrl) {
          log(
            `Excluded file '${entry.fileName}' has Presigned URL: ${presignedUrl.substring(0, 80)}...`
          );
        }
      }

      log("✅ Archive mode with archiveExcludePaths integration test completed");
    }
  );
});
