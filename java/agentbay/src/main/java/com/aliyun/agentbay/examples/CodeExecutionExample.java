package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.filesystem.FileSystem;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.SessionException;
import com.aliyun.agentbay.model.code.EnhancedCodeExecutionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;;

/**
 * Example demonstrating code execution functionality in AgentBay Java SDK
 */
public class CodeExecutionExample {

    public static void main(String[] args) {
        try {
            // Get API Key from environment variable
            String apiKey = System.getenv("AGENTBAY_API_KEY");
            if (apiKey == null || apiKey.trim().isEmpty()) {
                System.err.println("Error: AGENTBAY_API_KEY environment variable not set");
                return;
            }

            // Get configuration from environment variables or use defaults.
            // Endpoint is derived from region; not configurable directly.
            String region = getEnvOrDefault("AGENTBAY_REGION_ID", "us-east-1");
            int timeout = Integer.parseInt(getEnvOrDefault("AGENTBAY_TIMEOUT_MS", "60000"));
            String imageId = System.getenv("AGENTBAY_IMAGE_ID");

            Config cfg = new Config(region, timeout);

            // Print configuration
            System.out.println("========== Configuration ==========");
            System.out.println("Region: " + cfg.getRegionId());
            System.out.println("Endpoint: " + cfg.getEndpoint() + " (derived)");
            System.out.println("Timeout: " + cfg.getTimeoutMs() + "ms");
            System.out.println("Image ID: " + imageId);
            System.out.println("===================================\n");

            // Create AgentBay client
            System.out.println("Creating AgentBay client...");
            AgentBay agentBay = new AgentBay(apiKey, cfg);


            // Create a session
            System.out.println("Creating session...");
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId(imageId);
            long startTime = System.currentTimeMillis();
            SessionResult sessionResult = agentBay.create(params);
            long duration = System.currentTimeMillis() - startTime;
            System.out.println("⏱️  Create session finished in " + duration + "ms");

            if (!sessionResult.isSuccess()) {
                System.err.println("Failed to create session: " + sessionResult.getErrorMessage());
                return;
            }

            Session session = sessionResult.getSession();

            System.out.println("✅ Session created successfully!");
            System.out.println("   Session ID: " + session.getSessionId());
            System.out.println("   Request ID: " + sessionResult.getRequestId());

            FileSystem fs = session.getFileSystem();
//
//            // ===== BASIC FILE OPERATIONS =====
//            System.out.println("\n===== BASIC FILE OPERATIONS =====");
//
            // Example 1: Write a simple file
            System.out.println("\nExample 1: Writing a simple file...");
            String testContent = "This is a test file content.\nIt has multiple lines.\nThis is the third line.";
            String testFilePath = "/tmp/test_file.txt";

            long writeStartTime = System.currentTimeMillis();
            BoolResult result1 = fs.writeFile(testFilePath, testContent, "overwrite");
            long writeDuration = System.currentTimeMillis() - writeStartTime;
            System.out.println("File write successful: " + result1.isSuccess());
            System.out.println("⏱️  Write file finished in " + writeDuration + "ms");
            if (!result1.isSuccess()) {
                System.out.println("Error: " + result1.getErrorMessage());
            }
            System.out.println("Request ID: " + result1.getRequestId());


            // Example 1: Execute Python code
            System.out.println("\n🐍 Executing Python code...");
            String pythonCode = "print(\"hello world\")";
            long pythonStartTime = System.currentTimeMillis();
            EnhancedCodeExecutionResult pythonResult = session.getCode().runCode(pythonCode, "python");
            long pythonDuration = System.currentTimeMillis() - pythonStartTime;

            if (pythonResult.isSuccess()) {
                System.out.println("✅ Python code executed successfully!");
                System.out.println("⏱️  Python execution finished in " + pythonDuration + "ms");
                System.out.println("   Output: " + pythonResult.getResult());
                System.out.println("   Request ID: " + pythonResult.getRequestId());
            } else {
                System.err.println("❌ Failed to execute Python code: " + pythonResult.getErrorMessage());
                System.out.println("⏱️  Python execution finished in " + pythonDuration + "ms");
            }

            // Example 2: Execute JavaScript code
            System.out.println("\n🟨 Executing JavaScript code...");
            String jsCode = "console.log('Hello from JavaScript!');\nconst result = 5 * 4;\nconsole.log(`5 * 4 = ${result}`);";
            long jsStartTime = System.currentTimeMillis();
            EnhancedCodeExecutionResult jsResult = session.getCode().runCode(jsCode, "javascript");
            long jsDuration = System.currentTimeMillis() - jsStartTime;

            if (jsResult.isSuccess()) {
                System.out.println("✅ JavaScript code executed successfully!");
                System.out.println("⏱️  JavaScript execution finished in " + jsDuration + "ms");
                System.out.println("   Output: " + jsResult.getResult());
                System.out.println("   Request ID: " + jsResult.getRequestId());
            } else {
                System.err.println("❌ Failed to execute JavaScript code: " + jsResult.getErrorMessage());
                System.out.println("⏱️  JavaScript execution finished in " + jsDuration + "ms");
            }

            // Clean up - delete the session
            DeleteResult deleteResult = session.delete();
            if (!deleteResult.isSuccess()) {
                System.err.println("Failed to delete session: " + deleteResult.getErrorMessage());
            }
            System.out.println("   Session deleted successfully!");


        } catch (SessionException e) {
            System.err.println("❌ Session error: " + e.getMessage());
            e.printStackTrace();
        } catch (AgentBayException e) {
            System.err.println("❌ AgentBay error: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("❌ Unexpected error: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * Helper method to get environment variable or default value
     */
    private static String getEnvOrDefault(String envName, String defaultValue) {
        String value = System.getenv(envName);
        return (value != null && !value.trim().isEmpty()) ? value : defaultValue;
    }
}