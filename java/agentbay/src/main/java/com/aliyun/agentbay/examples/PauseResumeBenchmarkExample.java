package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.ArrayList;
import java.util.List;

/**
 * Example to batch test session pause/resume with file persistence verification.
 *
 * This example:
 * 1. Creates N sessions sequentially
 * 2. Each session writes a unique test file
 * 3. Pauses all sessions
 * 4. Sleeps for 16 minutes
 * 5. Resumes each session sequentially and measures resume time
 * 6. Verifies each session's test file still exists
 * 7. Prints a summary of all timings and verification results
 */
public class PauseResumeBenchmarkExample {

    private static final int NUM_SESSIONS = 10;
    private static final int SLEEP_MINUTES = 16;
    private static final String SEPARATOR = "============================================================";

    // Holds info about each session for tracking
    static class SessionInfo {
        final int index;
        Session session;
        String testFilePath;
        String testFileContent;
        long createElapsed;
        long pauseElapsed;
        long resumeElapsed;
        boolean fileExists;
        String fileContent;
        String errorMessage;

        SessionInfo(int index) {
            this.index = index;
            this.fileExists = false;
        }
    }

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

        AgentBay agentBay;
        try {
            agentBay = new AgentBay();
        } catch (Exception e) {
            System.err.println("Failed to create AgentBay client: " + e.getMessage());
            return;
        }
        List<SessionInfo> sessions = new ArrayList<>();

        try {
            // ========== Step 1: Create N sessions ==========
            System.out.println(SEPARATOR);
            System.out.println("Step 1: Creating " + NUM_SESSIONS + " sessions...");
            System.out.println(SEPARATOR);

            for (int i = 0; i < NUM_SESSIONS; i++) {
                SessionInfo info = new SessionInfo(i + 1);
                sessions.add(info);

                System.out.printf("%n  Creating session %d/%d...%n", i + 1, NUM_SESSIONS);
                CreateSessionParams params = new CreateSessionParams();
                params.setImageId("AIO_ubuntu2404");

                long createStart = System.currentTimeMillis();
                SessionResult createResult = agentBay.create(params);
                long createElapsed = System.currentTimeMillis() - createStart;
                info.createElapsed = createElapsed;

                if (!createResult.isSuccess() || createResult.getSession() == null) {
                    info.errorMessage = "Failed to create: " + createResult.getErrorMessage();
                    System.err.printf("  ✗ Session %d creation failed: %s%n", i + 1, info.errorMessage);
                    continue;
                }

                info.session = createResult.getSession();
                System.out.printf("  ✓ Session %d created: %s (%.2fs)%n",
                        info.index, info.session.getSessionId(), createElapsed / 1000.0);

                // Write a unique test file for each session
                String testFilePath = "/tmp/test_session_" + info.index + ".txt";
                String timestamp = String.valueOf(System.currentTimeMillis());
                String testContent = "Session " + info.index + " created at timestamp=" + timestamp;

                BoolResult writeResult = info.session.getFileSystem().writeFile(testFilePath, testContent);
                if (!writeResult.isSuccess()) {
                    info.errorMessage = "Failed to write test file: " + writeResult.getErrorMessage();
                    System.err.printf("  ✗ Session %d failed to write file: %s%n", i + 1, info.errorMessage);
                    continue;
                }

                info.testFilePath = testFilePath;
                info.testFileContent = testContent;
                System.out.printf("    Test file written: %s%n", testFilePath);
            }

            // Filter out sessions that failed to create
            sessions.removeIf(info -> info.session == null);

            if (sessions.isEmpty()) {
                System.err.println("No sessions created successfully. Exiting.");
                return;
            }

            System.out.printf("%n  Successfully created %d/%d sessions%n", sessions.size(), NUM_SESSIONS);

            // ========== Step 2: Pause all sessions ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 2: Pausing all sessions...");
            System.out.println(SEPARATOR);

            for (SessionInfo info : sessions) {
                System.out.printf("%n  Pausing session %d (%s)...%n", info.index, info.session.getSessionId());
                long pauseStart = System.currentTimeMillis();
                SessionPauseResult pauseResult = info.session.betaPause(600, 2.0);
                long pauseElapsed = System.currentTimeMillis() - pauseStart;
                info.pauseElapsed = pauseElapsed;

                if (!pauseResult.isSuccess()) {
                    info.errorMessage = "Pause failed: " + pauseResult.getErrorMessage();
                    System.err.printf("  ✗ Session %d pause failed: %s%n", info.index, info.errorMessage);
                } else {
                    System.out.printf("  ✓ Session %d paused (%.2fs)%n", info.index, pauseElapsed / 1000.0);
                }
            }

            // ========== Step 3: Sleep ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 3: Sleeping for " + SLEEP_MINUTES + " minutes...");
            System.out.println(SEPARATOR);
            System.out.println("  Start time: " + java.time.LocalDateTime.now());

            long sleepMs = SLEEP_MINUTES * 60 * 1000L;
            long sleepStart = System.currentTimeMillis();

            // Print progress every minute
            while (System.currentTimeMillis() - sleepStart < sleepMs) {
                long elapsed = System.currentTimeMillis() - sleepStart;
                long remaining = sleepMs - elapsed;
                if (remaining > 60000) {
                    Thread.sleep(60000);
                } else {
                    Thread.sleep(remaining);
                }
            }

            System.out.println("  Wake up time: " + java.time.LocalDateTime.now());
            System.out.printf("  Sleep completed (%d minutes)%n", SLEEP_MINUTES);

            // ========== Step 4: Resume sessions sequentially and verify ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Step 4: Resuming sessions and verifying file persistence...");
            System.out.println(SEPARATOR);

            for (SessionInfo info : sessions) {
                System.out.printf("%n  --- Session %d (%s) ---%n", info.index, info.session.getSessionId());

                // Resume
                System.out.println("  Resuming...");
                long resumeStart = System.currentTimeMillis();
                try {
                    SessionResumeResult resumeResult = info.session.betaResume(600, 2.0);
                    long resumeElapsed = System.currentTimeMillis() - resumeStart;
                    info.resumeElapsed = resumeElapsed;

                    if (!resumeResult.isSuccess()) {
                        info.errorMessage = "Resume failed: " + resumeResult.getErrorMessage();
                        System.err.printf("  ✗ Resume failed: %s (%.2fs)%n", info.errorMessage, resumeElapsed / 1000.0);
                        continue;
                    }
                    System.out.printf("  ✓ Resumed (%.2fs)%n", resumeElapsed / 1000.0);

                    // Wait for services to stabilize
                    Thread.sleep(2000);
                } catch (Exception e) {
                    info.resumeElapsed = System.currentTimeMillis() - resumeStart;
                    info.errorMessage = "Resume exception: " + e.getMessage();
                    System.err.printf("  ✗ Resume exception: %s (%.2fs)%n", e.getMessage(), info.resumeElapsed / 1000.0);
                    continue;
                }

                // Verify file exists
                System.out.printf("  Verifying file: %s%n", info.testFilePath);
                try {
                    FileContentResult fileResult = info.session.getFileSystem().readFile(info.testFilePath);
                    if (fileResult.isSuccess()) {
                        info.fileExists = true;
                        info.fileContent = fileResult.getContent();
                        boolean contentMatches = info.testFileContent.equals(fileResult.getContent());
                        System.out.printf("  ✓ File exists! Content matches: %s%n", contentMatches);
                        if (!contentMatches) {
                            System.out.printf("    Expected: %s%n", info.testFileContent);
                            System.out.printf("    Got: %s%n", fileResult.getContent());
                        }
                    } else {
                        System.err.printf("  ✗ File NOT found: %s%n", fileResult.getErrorMessage());
                    }
                } catch (Exception e) {
                    System.err.printf("  ✗ File verification failed: %s%n", e.getMessage());
                }
            }

            // ========== Step 5: Print summary ==========
            printSummary(sessions);

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            // ========== Cleanup: delete all sessions ==========
            System.out.println("\n" + SEPARATOR);
            System.out.println("Cleaning up: deleting all sessions...");
            System.out.println(SEPARATOR);

            for (SessionInfo info : sessions) {
                if (info.session != null) {
                    try {
                        System.out.printf("  Deleting session %d (%s)...%n", info.index, info.session.getSessionId());
                        info.session.delete(false);
                        System.out.printf("  ✓ Session %d deleted%n", info.index);
                    } catch (Exception e) {
                        System.err.printf("  ✗ Failed to delete session %d: %s%n", info.index, e.getMessage());
                    }
                }
            }
            System.out.println("  All sessions cleaned up");
        }
    }

    private static void printSummary(List<SessionInfo> sessions) {
        System.out.println("\n" + SEPARATOR);
        System.out.println("BENCHMARK SUMMARY");
        System.out.println(SEPARATOR);

        System.out.printf("%n  Total sessions: %d%n", sessions.size());

        System.out.printf("%n  Session details:%n");
        System.out.printf("  %-8s | %-12s | %-12s | %-12s | %-10s | %s%n",
                "Session", "Create(s)", "Pause(s)", "Resume(s)", "File", "ID");
        System.out.println("  " + repeatChar('-', 100));

        long totalCreate = 0, totalPause = 0, totalResume = 0;
        int fileExistsCount = 0;
        long minResume = Long.MAX_VALUE, maxResume = Long.MIN_VALUE;

        for (SessionInfo info : sessions) {
            totalCreate += info.createElapsed;
            totalPause += info.pauseElapsed;
            if (info.resumeElapsed > 0) {
                totalResume += info.resumeElapsed;
                minResume = Math.min(minResume, info.resumeElapsed);
                maxResume = Math.max(maxResume, info.resumeElapsed);
            }
            if (info.fileExists) {
                fileExistsCount++;
            }

            String fileStatus = info.fileExists ? "✓" : "✗";
            String sessionId = info.session != null ? info.session.getSessionId() : "N/A";
            String resumeStr = info.resumeElapsed > 0 ? String.format("%.2f", info.resumeElapsed / 1000.0) : "N/A";

            System.out.printf("  %-8d | %-12.2f | %-12.2f | %-12s | %-10s | %s%n",
                    info.index,
                    info.createElapsed / 1000.0,
                    info.pauseElapsed / 1000.0,
                    resumeStr,
                    fileStatus,
                    sessionId.length() > 20 ? sessionId.substring(0, 20) + "..." : sessionId);

            if (info.errorMessage != null) {
                System.out.printf("           Error: %s%n", info.errorMessage);
            }
        }

        int resumeCount = (int) sessions.stream().filter(info -> info.resumeElapsed > 0).count();

        System.out.println("  " + repeatChar('-', 100));
        System.out.printf("%n  Averages (over %d resumed sessions):%n", resumeCount);
        System.out.printf("    Avg create:  %.2fs%n", (totalCreate / (double) sessions.size()));
        System.out.printf("    Avg pause:   %.2fs%n", (totalPause / (double) sessions.size()));
        if (resumeCount > 0) {
            System.out.printf("    Avg resume:  %.2fs%n", (totalResume / (double) resumeCount));
            System.out.printf("    Min resume:  %.2fs%n", (minResume / 1000.0));
            System.out.printf("    Max resume:  %.2fs%n", (maxResume / 1000.0));
        }

        System.out.printf("%n  File persistence: %d/%d files survived%n", fileExistsCount, sessions.size());
        System.out.println(SEPARATOR);
    }

    private static String repeatChar(char c, int count) {
        StringBuilder sb = new StringBuilder(count);
        for (int i = 0; i < count; i++) {
            sb.append(c);
        }
        return sb.toString();
    }
}
