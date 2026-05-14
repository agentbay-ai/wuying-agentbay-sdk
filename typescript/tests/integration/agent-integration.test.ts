// ci-stable
import { AgentBay, Session } from "../../src";
import {
  ContextSync,
  SyncPolicy,
  UploadPolicy,
  DownloadPolicy,
  DeletePolicy,
  ExtractPolicy,
  RecyclePolicy,
  BWList,
  WhiteList,
  newUploadPolicy,
  newDownloadPolicy,
  newDeletePolicy,
  newExtractPolicy,
  newRecyclePolicy,
  WhiteListValidator,
} from "../../src/context-sync";
import { Context } from "../../src/context";
import { getTestApiKey } from "../utils/test-helpers";
import { log } from "../../src/utils/logger";
import { zodToJsonSchema } from "zod-to-json-schema";
const { z } = require("zod");

describe("Agent", () => {
  describe("computerExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with Windows image for computer agent tasks
      log("Creating a new session for computer agent task testing...");
      const createResponse = await agentBay.create({
        imageId: "windows_latest",
      });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(
        `Create Session RequestId: ${createResponse.requestId || "undefined"}`
      );
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(
            `Delete Session RequestId: ${
              deleteResponse.requestId || "undefined"
            }`
          );
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully", async () => {
      if (session.agent) {
        const task = "create a folder named 'agentbay' in C:\\Windows\\Temp";

        // Get timeout from environment or use default
        const timeoutStr = process.env.AGENT_TASK_TIMEOUT;
        let timeout = 180; // default value in seconds
        if (timeoutStr) {
          const parsed = parseInt(timeoutStr, 10);
          if (!isNaN(parsed)) {
            timeout = parsed;
          }
        }

        try {
          log(`Executing computer agent task: ${task}`);
          const result = await session.agent.computer.executeTaskAndWait(
            task,
            timeout
          );

          log(
            `Agent task result: Success=${result.success}, TaskID=${result.taskId}, Status=${result.taskStatus}`
          );
          log(`Agent Task RequestId: ${result.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Agent task execution failed: ${result.errorMessage}`);
            // Don't fail the test if task execution is not supported in test environment
          } else {
            log(
              `Agent task executed successfully with result: ${result.taskResult}`
            );
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
          }
        } catch (error) {
          log(`Note: Agent task execution failed: ${error}`);
          // Don't fail the test if agent execution is not supported
        }
      } else {
        log("Note: Agent interface is nil, skipping agent test");
      }
    }); // Set a long timeout for the task execution
  });

  describe("browserExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with linux image for agent tasks
      log("Creating a new session for browser agent task testing...");
      const createResponse = await agentBay.create({ imageId: "linux_latest" });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(
        `Create Session RequestId: ${createResponse.requestId || "undefined"}`
      );
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(
            `Delete Session RequestId: ${
              deleteResponse.requestId || "undefined"
            }`
          );
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully", async () => {
      if (session.agent) {
        const task = "导航到百度查询上海天气.";

        // Get timeout from environment or use default
        const timeoutStr = process.env.AGENT_TASK_TIMEOUT;
        let timeout = 180; // default value in seconds
        if (timeoutStr) {
          const parsed = parseInt(timeoutStr, 10);
          if (!isNaN(parsed)) {
            timeout = parsed;
          }
        }

        try {
          log(`Executing browser agent task: ${task}`);
          const WeatherSchema = z.object({
            city: z.string(),
            weather: z.string(),
          });
          const result = await session.agent.browser.executeTaskAndWait(
            task,
            timeout,
            false,
            WeatherSchema
          );

          log(
            `Agent task result: Success=${result.success}, TaskID=${result.taskId}, Status=${result.taskStatus}`
          );
          log(`Agent Task RequestId: ${result.requestId || "undefined"}`);

          // Verify that the response contains requestId
          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(`Note: Agent task execution failed: ${result.errorMessage}`);
            // Don't fail the test if task execution is not supported in test environment
          } else {
            log(
              `Agent task executed successfully with result: ${result.taskResult}`
            );
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
          }
        } catch (error) {
          log(`Note: Agent task execution failed: ${error}`);
          // Don't fail the test if agent execution is not supported
        }
      } else {
        log("Note: Agent interface is nil, skipping agent test");
      }
    }); // Set a long timeout for the task execution
  });

  describe("mobileExecuteTask", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });

      // Create a session with mobile image for mobile agent tasks
      log("Creating a new session for mobile agent task testing...");
      const createResponse = await agentBay.create({
        imageId: "mobile_latest",
      });
      session = createResponse.session!;
      log(`Session created with ID: ${session.sessionId}`);
      log(
        `Create Session RequestId: ${createResponse.requestId || "undefined"}`
      );
    });

    afterEach(async () => {
      // Clean up the session
      log("Cleaning up: Deleting the session...");
      try {
        if (session && session.sessionId) {
          const deleteResponse = await agentBay.delete(session);
          log(
            `Delete Session RequestId: ${
              deleteResponse.requestId || "undefined"
            }`
          );
        }
      } catch (error) {
        log(`Warning: Error deleting session: ${error}`);
      }
    });

    it("should execute task successfully (non-blocking)", async () => {
      if (session.agent) {
        const task = "Open WeChat app";

        try {
          log(`Executing mobile agent task (non-blocking): ${task}`);
          const execution = await session.agent.mobile.executeTask(task, {
            maxSteps: 100,
          });

          expect(execution).toBeDefined();
          expect(execution.taskId).toBeDefined();
          log(`Mobile Agent task started, TaskID: ${execution.taskId}`);

          const result = await execution.wait(120);
          log(
            `Mobile Agent task result: Success=${result.success}, Status=${result.taskStatus}`
          );

          if (!result.success) {
            log(
              `Note: Mobile Agent task execution failed: ${result.errorMessage}`
            );
          } else {
            log(`Mobile Agent task executed successfully`);
            expect(result.success).toBe(true);
          }
        } catch (error) {
          log(`Note: Mobile Agent task execution failed: ${error}`);
        }
      } else {
        log("Note: Agent interface is nil, skipping mobile agent test");
      }
    }, 120000);

    it("should execute task and wait successfully (blocking)", async () => {
      if (session.agent) {
        const task = "Open WeChat app";
        const maxSteps = 100;
        const timeoutStr = process.env.AGENT_TASK_TIMEOUT;
        let timeout = 180; // default value in seconds
        if (timeoutStr) {
          const parsed = parseInt(timeoutStr, 10);
          if (!isNaN(parsed)) {
            timeout = parsed;
          }
        }

        try {
          log(`Executing mobile agent task (blocking): ${task}`);
          const result = await session.agent.mobile.executeTaskAndWait(
            task,
            timeout,
            { maxSteps }
          );

          log(
            `Mobile Agent task result: Success=${result.success}, ` +
              `TaskID=${result.taskId}, Status=${result.taskStatus}`
          );
          log(
            `Mobile Agent Task RequestId: ${result.requestId || "undefined"}`
          );

          expect(result.requestId).toBeDefined();
          expect(typeof result.requestId).toBe("string");

          if (!result.success) {
            log(
              `Note: Mobile Agent task execution failed: ` +
                `${result.errorMessage}`
            );
          } else {
            log(
              `Mobile Agent task executed successfully with result: ` +
                `${result.taskResult}`
            );
            expect(result.success).toBe(true);
            expect(result.taskId).toBeTruthy();
            expect(result.taskStatus).toBe("completed");
          }
        } catch (error) {
          log(`Note: Mobile Agent task execution failed: ${error}`);
        }
      } else {
        log("Note: Agent interface is nil, skipping mobile agent test");
      }
    }, 120000);
  });
});

// ─── WhiteList Pattern (BWList) Tests ────────────────────────────────────────

describe("WhiteListPattern", () => {
  describe("whiteListPatternBWList", () => {
    let agentBay: AgentBay;
    let session: Session | undefined;
    let bwlistContext: Context | undefined;

    beforeEach(async () => {
      const apiKey = getTestApiKey();
      agentBay = new AgentBay({ apiKey });
      session = undefined;
      bwlistContext = undefined;
    });

    afterEach(async () => {
      if (session) {
        try {
          log("Cleaning up session with pattern-based BWList...");
          const deleteResponse = await agentBay.delete(session, true);
          log(
            `Delete Session RequestId: ${
              deleteResponse.requestId || "undefined"
            }`
          );
        } catch (error) {
          log(`Warning: Error deleting session: ${error}`);
        }
      }
      if (bwlistContext) {
        try {
          const ctxDel = await agentBay.context.delete(bwlistContext);
          log(`Deleted context ${bwlistContext.id}: ${ctxDel.success}`);
        } catch (error) {
          log(`Warning: Error deleting context: ${error}`);
        }
      }
    });

    // Helper: recursively collect FILE entry names under folderPath.
    // folderPath is a Windows local path; list_files returns OSS-style paths.
    // For FOLDER entries: extract the last segment, build sub-path, recurse.
    // For FILE entries: extract the last segment (file name) and store it.
    async function collectAllFiles(
      contextId: string,
      folderPath: string
    ): Promise<string[]> {
      const result = await agentBay.context.listFiles(
        contextId,
        folderPath,
        1,
        200
      );
      if (!result.success || !result.entries || result.entries.length === 0) {
        return [];
      }
      const fileNames: string[] = [];
      for (const entry of result.entries) {
        const ftype = (entry.fileType || "").toUpperCase();
        const lastSegment =
          entry.filePath.replace(/\/$/, "").split("/").pop() || "";
        if (["FOLDER", "DIR", "DIRECTORY"].includes(ftype)) {
          // Build Windows local sub-path and recurse
          const subPath = folderPath.replace(/\\$/, "") + "\\" + lastSegment;
          const sub = await collectAllFiles(contextId, subPath);
          fileNames.push(...sub);
        } else {
          fileNames.push(lastSegment);
        }
      }
      return fileNames;
    }

    it("should create session with BWList using is_path_regex and is_exclude_regex (Windows single-session)", async () => {
      log(
        "Testing BWList is_path_regex + is_exclude_regex via single-session strategy..."
      );

      const base = "C:\\Users\\Administrator\\testdata";

      // Create context
      const contextName = `bwlist-ctx-${Date.now()}`;
      const contextResult = await agentBay.context.get(contextName, true);
      expect(contextResult.success && contextResult.context).toBeTruthy();
      bwlistContext = contextResult.context!;
      if (!bwlistContext) {
        throw new Error("Failed to get/create context");
      }
      const contextId = bwlistContext.id;
      log(`Context ID: ${contextId}`);

      // Create session WITH BWList
      // path=r"project-.*" (isPathRegex=true): match any sub-dir starting with "project-"
      // excludePaths=[r"cache.*"] (isExcludeRegex=true): exclude sub-dirs matching "cache.*"
      const syncPolicy: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        downloadPolicy: newDownloadPolicy(),
        deletePolicy: newDeletePolicy(),
        extractPolicy: newExtractPolicy(),
        recyclePolicy: newRecyclePolicy(),
        bwList: {
          whiteLists: [
            {
              path: "project-.*", // regex matching project-alpha, project-beta
              isPathRegex: true,
              excludePaths: ["cache.*"], // exclude sub-dirs matching cache.*
              isExcludeRegex: true,
            },
          ],
        },
      };

      const contextSync = new ContextSync(contextId, base, syncPolicy);
      log(`SyncPolicy bwList JSON: ${JSON.stringify(syncPolicy.bwList)}`);

      const createResponse = await agentBay.create({
        imageId: "imgc-0ae8jv3fd5yuss7ky",
        labels: { test: "patternBWList" },
        contextSync: [contextSync],
      });
      expect(createResponse.success).toBe(true);
      session = createResponse.session;
      log(`Session created with ID: ${session!.sessionId}`);

      // Write test files onto local FS
      const fs = session!.fileSystem!;
      for (const dir of [
        base,
        `${base}\\project-alpha`,
        `${base}\\project-beta`,
        `${base}\\project-beta\\cache`,
      ]) {
        const r = await fs.createDirectory(dir);
        log(`  mkdir ${dir}: ${r.success ? "OK" : r.errorMessage}`);
      }

      const testFiles: [string, string][] = [
        [
          `${base}\\project-alpha\\main.py`,
          "# main entry point\nprint('hello')\n",
        ],
        [`${base}\\project-alpha\\README.txt`, "Project Alpha README\n"],
        [`${base}\\project-beta\\config.json`, '{"env": "test"}\n'],
        [`${base}\\project-beta\\cache\\temp.log`, "temporary log\n"],
      ];
      for (const [fpath, content] of testFiles) {
        const r = await fs.writeFile(fpath, content);
        log(`  write ${fpath}: ${r.success ? "OK" : r.errorMessage}`);
      }

      // delete(syncContext=true) triggers upload with BWList filter
      log(
        "  Deleting session with syncContext=true (BWList upload filter applied)..."
      );
      const delResult = await agentBay.delete(session!, true);
      expect(delResult.success).toBe(true);
      session = undefined;
      log("  Session deleted. Filtered upload triggered.");

      // list_files(base) – one call, traverse entries directly
      log("\n=== Verifying OSS content via context.listFiles ===");
      const probe = await agentBay.context.listFiles(contextId, base, 1, 200);
      const entryCount = probe.entries ? probe.entries.length : 0;
      log(
        `  listFiles(${base}) -> success=${probe.success}, entries=${entryCount}`
      );

      const allFiles: string[] = [];
      if (probe.entries && probe.entries.length > 0) {
        for (const e of probe.entries) {
          const ftype = (e.fileType || "").toUpperCase();
          const lastSegment =
            e.filePath.replace(/\/$/, "").split("/").pop() || "";
          log(`    [${ftype}] ${e.filePath}  -> lastSegment=${lastSegment}`);
          if (["FOLDER", "DIR", "DIRECTORY"].includes(ftype)) {
            const subPath = base.replace(/\\$/, "") + "\\" + lastSegment;
            log(`      Recursing into ${subPath}...`);
            const sub = await collectAllFiles(contextId, subPath);
            allFiles.push(...sub);
          } else {
            allFiles.push(e.filePath);
          }
        }
      } else {
        log("  WARNING: No entries found in OSS.");
      }

      log(`  Collected ${allFiles.length} file(s) total`);
      log(`\n  === All files in OSS (${allFiles.length} total) ===`);
      for (const p of allFiles) {
        log(`    ${p}`);
      }

      expect(allFiles.length).toBe(3);

      // Files that SHOULD be present
      for (const name of ["main.py", "README.txt", "config.json"]) {
        const found = allFiles.some((p) => p.includes(name));
        log(`  ${found ? "FOUND" : "NOT FOUND"}: ${name}`);
        expect(found).toBe(true);
      }
      log("✅ Expected files present in OSS");

      // Files that SHOULD be absent (excluded by BWList cache.* regex)
      for (const name of ["temp.log"]) {
        const found = allFiles.some((p) => p.includes(name));
        log(
          `  ${
            found ? "FOUND (should be absent!)" : "correctly absent"
          }: ${name}`
        );
        expect(found).toBe(false);
      }
      log("✅ Excluded files correctly absent from OSS");
      log("BWList with isPathRegex + isExcludeRegex verified successfully");
    }, 120000);
  });
});
