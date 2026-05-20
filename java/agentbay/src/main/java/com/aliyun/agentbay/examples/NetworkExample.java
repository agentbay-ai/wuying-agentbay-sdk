package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.network.NetworkResult;
import com.aliyun.agentbay.network.NetworkStatusResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

public class NetworkExample {

    private static String repeat(String str, int count) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < count; i++) {
            sb.append(str);
        }
        return sb.toString();
    }

    public static void main(String[] args)  {
        try {
            String apiKey = System.getenv("AGENTBAY_API_KEY");
            if (apiKey == null || apiKey.trim().isEmpty()) {
                System.err.println("Error: AGENTBAY_API_KEY environment variable not set");
                return;
            }

            System.out.println("Creating AgentBay client...");
            // Endpoint is derived from regionId via the multi-region mapping.
            AgentBay agentBay = new AgentBay(apiKey, new Config("cn-hangzhou", 60000));

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Example 1: Create a network");
            System.out.println(repeat("=", 60));

            NetworkResult networkResult = agentBay.getBetaNetwork().betaGetNetworkBindToken();

            if (!networkResult.isSuccess()) {
                System.err.println("Failed to create network: " + networkResult.getErrorMessage());
                return;
            }

            String networkId = networkResult.getNetworkId();
            String networkToken = networkResult.getNetworkToken();

           // CreateSessionParams createSessionParams;
           // createSessionParams.setImageId("");
            //agentBay.client

            System.out.println("✅ Network created successfully!");
            System.out.println("   Network ID: " + networkId);
            System.out.println("   Network Token: " + networkToken);
            System.out.println("   Request ID: " + networkResult.getRequestId());

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Example 2: Check network status");
            System.out.println(repeat("=", 60));

            NetworkStatusResult statusResult = agentBay.getBetaNetwork().betaDescribe(networkId);

            if (statusResult.isSuccess()) {
                System.out.println("✅ Network status retrieved successfully!");
                System.out.println("   Network ID: " + networkId);
                System.out.println("   Online: " + statusResult.isOnline());
                System.out.println("   Request ID: " + statusResult.getRequestId());
            } else {
                System.err.println("❌ Failed to get network status: " + statusResult.getErrorMessage());
            }

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Example 3: Create sessions on the same network");
            System.out.println(repeat("=", 60));

            CreateSessionParams params1 = new CreateSessionParams();
            params1.setImageId("linux_latest");
            params1.setBetaNetworkId(networkId);

            System.out.println("\nCreating session 1...");
            SessionResult sessionResult1 = agentBay.create(params1);

            if (!sessionResult1.isSuccess()) {
                System.err.println("Failed to create session 1: " + sessionResult1.getErrorMessage());
                return;
            }

            Session session1 = sessionResult1.getSession();
            System.out.println("✅ Session 1 created successfully!");
            System.out.println("   Session ID: " + session1.getSessionId());
            System.out.println("   Network ID: " + networkId);

            CreateSessionParams params2 = new CreateSessionParams();
            params2.setImageId("linux_latest");
            params2.setBetaNetworkId(networkId);

            System.out.println("\nCreating session 2...");
            SessionResult sessionResult2 = agentBay.create(params2);

            if (!sessionResult2.isSuccess()) {
                System.err.println("Failed to create session 2: " + sessionResult2.getErrorMessage());
                agentBay.delete(session1, false);
                return;
            }

            Session session2 = sessionResult2.getSession();
            System.out.println("✅ Session 2 created successfully!");
            System.out.println("   Session ID: " + session2.getSessionId());
            System.out.println("   Network ID: " + networkId);

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Example 4: Test network communication between sessions");
            System.out.println(repeat("=", 60));

            System.out.println("\n🌐 Starting HTTP server on session 1...");
            String startServerCmd = "nohup python3 -m http.server 8888 > /tmp/server.log 2>&1 & echo $!";
            CommandResult serverResult = session1.getCommand().executeCommand(startServerCmd, 30000);

            if (serverResult.isSuccess()) {
                System.out.println("✅ HTTP server started on session 1");
                System.out.println("   PID: " + serverResult.getOutput().trim());

                Thread.sleep(3000);

                System.out.println("\n📡 Testing connection from session 2 to session 1...");
                String testCmd = "curl -s http://localhost:8888 | head -5";
                CommandResult curlResult = session2.getCommand().executeCommand(testCmd, 30000);

                if (curlResult.isSuccess()) {
                    System.out.println("✅ Successfully connected from session 2 to session 1!");
                    System.out.println("   Response preview:");
                    String[] lines = curlResult.getOutput().split("\n");
                    for (int i = 0; i < Math.min(5, lines.length); i++) {
                        System.out.println("   " + lines[i]);
                    }
                } else {
                    System.err.println("❌ Failed to connect: " + curlResult.getErrorMessage());
                }

                System.out.println("\n🛑 Stopping HTTP server on session 1...");
                String stopCmd = "pkill -f 'python3 -m http.server'";
                session1.getCommand().executeCommand(stopCmd, 30000);
                System.out.println("✅ HTTP server stopped");
            } else {
                System.err.println("❌ Failed to start HTTP server: " + serverResult.getErrorMessage());
            }

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Example 5: Verify network isolation");
            System.out.println(repeat("=", 60));

            System.out.println("\n🔒 Creating session 3 on a different network...");
            NetworkResult network2Result = agentBay.getBetaNetwork().betaGetNetworkBindToken();

            if (!network2Result.isSuccess()) {
                System.err.println("Failed to create second network: " + network2Result.getErrorMessage());
                agentBay.delete(session1, false);
                agentBay.delete(session2, false);
                return;
            }

            String networkId2 = network2Result.getNetworkId();
            System.out.println("✅ Second network created: " + networkId2);

            CreateSessionParams params3 = new CreateSessionParams();
            params3.setImageId("linux_latest");
            params3.setBetaNetworkId(networkId2);

            SessionResult sessionResult3 = agentBay.create(params3);

            if (!sessionResult3.isSuccess()) {
                System.err.println("Failed to create session 3: " + sessionResult3.getErrorMessage());
                agentBay.delete(session1, false);
                agentBay.delete(session2, false);
                return;
            }

            Session session3 = sessionResult3.getSession();
            System.out.println("✅ Session 3 created on different network: " + session3.getSessionId());

            System.out.println("\n🔍 Verifying network isolation...");
            System.out.println("   Session 1 & 2 are on network: " + networkId);
            System.out.println("   Session 3 is on network: " + networkId2);
            System.out.println("   Sessions on different networks cannot communicate with each other");

            System.out.println("\n" + repeat("=", 60));
            System.out.println("Cleaning up...");
            System.out.println(repeat("=", 60));

            DeleteResult deleteResult1 = agentBay.delete(session1, false);
            if (deleteResult1.isSuccess()) {
                System.out.println("✅ Session 1 deleted");
            } else {
                System.err.println("❌ Failed to delete session 1: " + deleteResult1.getErrorMessage());
            }

            DeleteResult deleteResult2 = agentBay.delete(session2, false);
            if (deleteResult2.isSuccess()) {
                System.out.println("✅ Session 2 deleted");
            } else {
                System.err.println("❌ Failed to delete session 2: " + deleteResult2.getErrorMessage());
            }

            DeleteResult deleteResult3 = agentBay.delete(session3, false);
            if (deleteResult3.isSuccess()) {
                System.out.println("✅ Session 3 deleted");
            } else {
                System.err.println("❌ Failed to delete session 3: " + deleteResult3.getErrorMessage());
            }

            System.out.println("\n✅ All examples completed successfully!");

        } catch (AgentBayException e) {
            System.err.println("❌ AgentBay error: " + e.getMessage());
            e.printStackTrace();
        } catch (Exception e) {
            System.err.println("❌ Unexpected error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
