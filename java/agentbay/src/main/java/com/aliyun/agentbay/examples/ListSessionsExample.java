package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.model.SessionListResult;
import com.aliyun.agentbay.exception.AgentBayException;

import java.util.HashMap;
import java.util.Map;

/**
 * Example demonstrating how to list sessions with filtering and pagination
 */
public class ListSessionsExample {

    public static void main(String[] args) {
        try {
            // Initialize AgentBay client
            AgentBay agentBay = new AgentBay();

            System.out.println("=== Example 1: List all sessions (default parameters) ===");
            SessionListResult result1 = agentBay.list();
            printSessionList(result1);

            System.out.println("\n=== Example 2: List sessions with pagination ===");
            // List first page with 5 sessions per page
            SessionListResult result2 = agentBay.list(null, 1, 5, null, null);
            printSessionList(result2);

            System.out.println("\n=== Example 3: List sessions with labels filter ===");
            Map<String, String> labels = new HashMap<>();
            labels.put("env", "production");
            labels.put("team", "backend");
            SessionListResult result3 = agentBay.list(labels, null, 10, null, null);
            printSessionList(result3);

            System.out.println("\n=== Example 4: List RUNNING sessions only ===");
            SessionListResult result4 = agentBay.list(null, null, 10, "RUNNING", null);
            printSessionList(result4);

            System.out.println("\n=== Example 5: Pagination - Get second page ===");
            SessionListResult result5 = agentBay.list(null, 2, 5, null, null);
            printSessionList(result5);

            System.out.println("\n=== Example 6: List sessions filtered by ImageId ===");
            SessionListResult result6 = agentBay.list(null, null, 10, null, "your-image-id");
            printSessionList(result6);

        } catch (AgentBayException e) {
            System.err.println("Failed to initialize AgentBay: " + e.getMessage());
            e.printStackTrace();
        }
    }

    private static void printSessionList(SessionListResult result) {
        if (result.isSuccess()) {
            System.out.println("✅ Success - Request ID: " + result.getRequestId());
            System.out.println("Total Count: " + result.getTotalCount());
            System.out.println("Returned Count: " + result.getSessionInfos().size());
            System.out.println("Max Results: " + result.getMaxResults());
            System.out.println("Has More Pages: " + (!result.getNextToken().isEmpty()));

            if (!result.getSessionInfos().isEmpty()) {
                System.out.println("\nSessions:");
                for (SessionListResult.SessionInfo sessionInfo : result.getSessionInfos()) {
                    System.out.println("  - Session ID: " + sessionInfo.getSessionId() +
                                     ", Status: " + sessionInfo.getSessionStatus() +
                                     ", AppInstanceId: " + sessionInfo.getAppInstanceId());
                }
            } else {
                System.out.println("No sessions found.");
            }
        } else {
            System.err.println("❌ Failed - " + result.getErrorMessage());
        }
    }
}
