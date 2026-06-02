package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

/**
 * Example to verify file system and process persistence after session pause/resume.
 *
 * This example:
 * 1. Creates a session
 * 2. Writes test files to the file system
 * 3. Starts a background process that continuously writes to a file
 * 4. Pauses the session
 * 5. Resumes the session
 * 6. Verifies:
 *    - Files persist after pause/resume
 *    - Background process is still running
 *    - Process continues writing to file
 */
public class PauseResumePersistenceVerificationExample {

    private static final String SEPARATOR = "============================================================";

    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            System.err.println("Please set AGENTBAY_API_KEY environment variable");
            return;
        }

        String imageId = System.getenv("AGENTBAY_IMAGE_ID");
        if (imageId == null || imageId.trim().isEmpty()) {
            imageId = "imgc-0ab5ta4nvas4kvko7";
        }

        Session session = null;
        try {
            AgentBay agentBay = new AgentBay();

            // ========== Step 1: Create session ==========
            System.out.println(SEPARATOR);
            System.out.println("Step 1: Creating session...");
            System.out.println(SEPARATOR);

            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("AIO_ubuntu2404");

            long createStart = System.currentTimeMillis();
            SessionResult createResult = agentBay.create(params);
            long createElapsed = System.currentTimeMillis() - createStart;

            if (!createResult.isSuccess() || createResult.getSession() == null) {
                System.err.println("Failed to create session: " + createResult.getErrorMessage());
                return;
            }
            session = createResult.getSession();
            System.out.printf("  Session created: %s (%.2fs)%n", session.getSessionId(), createElapsed / 1000.0);

            // ========== Step 2: Write test files ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 2: Writing test files...");
            System.out.println(SEPARATOR);

            // Write a text file
            String testContent = "hello from before pause! timestamp=" + System.currentTimeMillis();
            BoolResult writeResult = session.getFileSystem().writeFile("/tmp/test_persist.txt", testContent);
            if (!writeResult.isSuccess()) {
                System.err.println("Failed to write test file: " + writeResult.getErrorMessage());
                return;
            }
            System.out.println("  Text file written: /tmp/test_persist.txt");
            System.out.println("  Content: " + testContent);

            // Write a binary file (256 bytes: 0-255)
            byte[] binaryContent = new byte[256];
            for (int i = 0; i < 256; i++) {
                binaryContent[i] = (byte) i;
            }
            UploadResult binaryWriteResult = session.getFileSystem().uploadFileBytes(binaryContent, "/tmp/test_binary.bin");
            if (!binaryWriteResult.isSuccess()) {
                System.err.println("Failed to write binary file: " + binaryWriteResult.getErrorMessage());
                return;
            }
            System.out.println("  Binary file written: /tmp/test_binary.bin (256 bytes)");

            // ========== Step 3: Start background process ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 3: Starting background process...");
            System.out.println(SEPARATOR);

            // Create a background worker script
            String workerScript = 
                "#!/bin/bash\n" +
                "counter=0\n" +
                "while true; do\n" +
                "    counter=$((counter + 1))\n" +
                "    echo \"counter=$counter, pid=$$, time=$(date +%s)\" > /tmp/proc_counter.txt\n" +
                "    sleep 1\n" +
                "done";
            
            session.getFileSystem().writeFile("/tmp/background_worker.sh", workerScript);
            
            // Start the background process
            CommandResult startResult = session.getCommand().execute("chmod +x /tmp/background_worker.sh && nohup /tmp/background_worker.sh >/dev/null 2>&1 &");
            if (!startResult.isSuccess()) {
                System.err.println("Failed to start background process: " + startResult.getErrorMessage());
                return;
            }
            System.out.println("  Background process started");

            // Wait for background process to run
            System.out.println("\n  Waiting 3 seconds for background process...");
            Thread.sleep(3000);

            // Verify pre-pause state
            System.out.println("\n  Verifying pre-pause state...");
            CommandResult checkBeforeResult = session.getCommand().execute("cat /tmp/proc_counter.txt");
            if (checkBeforeResult.isSuccess()) {
                System.out.println("  Counter file: " + checkBeforeResult.getStdout().trim());
            }

            // ========== Step 4: Pause session ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 4: Pausing session...");
            System.out.println(SEPARATOR);

            long pauseStart = System.currentTimeMillis();
            SessionPauseResult pauseResult = session.betaPause(600, 2.0);
            long pauseElapsed = System.currentTimeMillis() - pauseStart;

            if (!pauseResult.isSuccess()) {
                System.err.println("Pause failed: " + pauseResult.getErrorMessage());
                return;
            }
            System.out.printf("  Session paused (%.2fs)%n", pauseElapsed / 1000.0);
            System.out.println("  Status: " + pauseResult.getStatus());

            // ========== Step 5: Resume session ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 5: Resuming session...");
            System.out.println(SEPARATOR);

            long resumeStart = System.currentTimeMillis();
            SessionResumeResult resumeResult = session.betaResume(600, 2.0);
            long resumeElapsed = System.currentTimeMillis() - resumeStart;

            if (!resumeResult.isSuccess()) {
                System.err.println("Resume failed: " + resumeResult.getErrorMessage());
                return;
            }
            System.out.printf("  Session resumed (%.2fs)%n", resumeElapsed / 1000.0);
            System.out.println("  Status: " + resumeResult.getStatus());

            // Wait a moment for services to stabilize
            Thread.sleep(2000);

            // ========== Step 6: Verify file persistence ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 6: Verifying file persistence...");
            System.out.println(SEPARATOR);

            // Check text file
            FileContentResult textFileResult = session.getFileSystem().readFile("/tmp/test_persist.txt");
            if (textFileResult.isSuccess()) {
                System.out.println("  Text file exists: /tmp/test_persist.txt");
                System.out.println("  Content: " + textFileResult.getContent());
            } else {
                System.err.println("  Text file NOT found!");
            }

            // Check binary file
            DownloadResult binaryFileResult = session.getFileSystem().downloadFileBytes("/tmp/test_binary.bin");
            if (binaryFileResult.isSuccess() && binaryFileResult.getContent() != null) {
                boolean contentCorrect = binaryFileResult.getContent().length == 256;
                System.out.printf("  Binary file exists: /tmp/test_binary.bin (%d bytes, content correct: %s)%n", 
                    binaryFileResult.getContent().length, contentCorrect);
            } else {
                System.err.println("  Binary file NOT found!");
            }

            // ========== Step 7: Verify process persistence ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 7: Verifying process persistence...");
            System.out.println(SEPARATOR);

            // Check if background process is still running
            CommandResult checkProcResult = session.getCommand().execute("ps aux | grep background_worker | grep -v grep");
            if (checkProcResult.isSuccess() && !checkProcResult.getStdout().trim().isEmpty()) {
                System.out.println("  Background process is running:");
                System.out.println("  " + checkProcResult.getStdout().replace("\n", "\n  "));
            } else {
                System.err.println("  Background process NOT found!");
            }

            // Check counter file
            CommandResult checkCounterResult = session.getCommand().execute("cat /tmp/proc_counter.txt");
            if (checkCounterResult.isSuccess()) {
                System.out.println("  Counter file: " + checkCounterResult.getStdout().trim());
            }

            // Wait 2 seconds and check again to verify process is still updating
            System.out.println("\n  Waiting 2 seconds to verify process is still active...");
            Thread.sleep(2000);
            
            CommandResult checkCounterAfterResult = session.getCommand().execute("cat /tmp/proc_counter.txt");
            if (checkCounterAfterResult.isSuccess()) {
                System.out.println("  Counter file after 2s: " + checkCounterAfterResult.getStdout().trim());
            }

            // ========== Summary ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("SUMMARY");
            System.out.println(SEPARATOR);
            System.out.printf("  Create session: %.2fs%n", createElapsed / 1000.0);
            System.out.printf("  Pause session:  %.2fs%n", pauseElapsed / 1000.0);
            System.out.printf("  Resume session: %.2fs%n", resumeElapsed / 1000.0);
            System.out.println("\n  Verification items:");
            System.out.println("    1. Text file persistence (/tmp/test_persist.txt)");
            System.out.println("    2. Binary file persistence (/tmp/test_binary.bin)");
            System.out.println("    3. Background process survival (background_worker.sh)");
            System.out.println("    4. Process-written counter file (/tmp/proc_counter.txt)");
            System.out.println(SEPARATOR);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (session != null) {
                try {
                    System.out.println("\nCleaning up: deleting session...");
                    session.delete(false);
                    System.out.println("  Session deleted");
                } catch (Exception ignored) {
                }
            }
        }
    }
}
