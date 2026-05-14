import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.BetaContextMount;
import com.aliyun.agentbay.context.Context;
import com.aliyun.agentbay.context.ContextBindResult;
import com.aliyun.agentbay.context.ContextResult;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.FileContentResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.Arrays;

/**
 * AgentBay SDK - Context Mount Example
 *
 * Demonstrates the Context Mount (direct-mount persistence) feature:
 * - Mounting a context at session creation time
 * - Write-through persistence (no manual sync needed)
 * - Cross-session data persistence via mount
 * - Dynamic mounting using bind()
 */
public class ContextMountExample {

    public static void main(String[] args) {
        System.out.println("📌 AgentBay Context Mount Example");

        AgentBay agentBay;
        try {
            agentBay = new AgentBay();
        } catch (AgentBayException e) {
            System.err.println("Failed to create AgentBay client: " + e.getMessage());
            return;
        }

        try {
            contextMountDemo(agentBay);
        } catch (Exception e) {
            System.err.println("❌ Example execution failed: " + e.getMessage());
            e.printStackTrace();
        }

        System.out.println("✅ Context mount example completed");
    }

    private static void contextMountDemo(AgentBay agentBay) throws Exception {
        System.out.println("\n🔄 === Context Mount Demonstration ===");

        // Step 1: Create a context for persistent storage
        System.out.println("\n📦 Step 1: Creating context for persistent storage...");
        String contextName = "mount-demo-" + System.currentTimeMillis();
        ContextResult contextResult = agentBay.getContext().get(contextName, true);

        if (!contextResult.isSuccess() || contextResult.getContext() == null) {
            throw new RuntimeException("Context creation failed: " + contextResult.getErrorMessage());
        }

        Context context = contextResult.getContext();
        System.out.println("✅ Context created: " + context.getId() + " (name: " + context.getName() + ")");

        // Step 2: Create first session with context mount
        System.out.println("\n🔧 Step 2: Creating first session with context mount...");
        BetaContextMount contextMount = new BetaContextMount(context.getId(), "/tmp/mounted_data");

        CreateSessionParams params1 = new CreateSessionParams();
        params1.setBetaContextMounts(Arrays.asList(contextMount));

        SessionResult session1Result = agentBay.create(params1);
        if (!session1Result.isSuccess() || session1Result.getSession() == null) {
            throw new RuntimeException("First session creation failed: " + session1Result.getErrorMessage());
        }

        Session session1 = session1Result.getSession();
        System.out.println("✅ First session created: " + session1.getSessionId());
        String session1Id = session1.getSessionId();

        try {
            // Step 3: Write data — persisted immediately via write-through
            System.out.println("\n💾 Step 3: Writing data (write-through persistence)...");

            session1.getCommand().executeCommand("mkdir -p /tmp/mounted_data/config", 5000);

            String configContent = "{\"app\": \"mount-demo\", \"version\": \"1.0\", \"session\": \"" + session1.getSessionId() + "\"}";
            BoolResult configWriteResult = session1.getFileSystem().writeFile(
                    "/tmp/mounted_data/config/app.json", configContent, "overwrite");
            if (configWriteResult.isSuccess()) {
                System.out.println("✅ Config file written (persisted immediately)");
            } else {
                System.out.println("❌ Failed to write config: " + configWriteResult.getErrorMessage());
            }

            BoolResult dataWriteResult = session1.getFileSystem().writeFile(
                    "/tmp/mounted_data/notes.txt",
                    "This data is persisted via Context Mount.\nNo manual sync() call needed!",
                    "overwrite");
            if (dataWriteResult.isSuccess()) {
                System.out.println("✅ Data file written (persisted immediately)");
            } else {
                System.out.println("❌ Failed to write data: " + dataWriteResult.getErrorMessage());
            }

            // List files
            System.out.println("\n📋 Files in mounted path:");
            CommandResult listResult = session1.getCommand().executeCommand("find /tmp/mounted_data -type f -ls", 5000);
            if (listResult.isSuccess()) {
                System.out.println(listResult.getOutput());
            }

        } finally {
            // No sync needed — data is already persisted
            System.out.println("\n🧹 Deleting first session (no sync needed for mount)...");
            DeleteResult deleteResult1 = agentBay.delete(session1);
            if (deleteResult1.isSuccess()) {
                System.out.println("✅ First session deleted");
            } else {
                System.out.println("❌ First session deletion failed: " + deleteResult1.getErrorMessage());
            }
        }

        // Step 4: Create second session to verify cross-session persistence
        System.out.println("\n🔧 Step 4: Creating second session to verify persistence...");

        CreateSessionParams params2 = new CreateSessionParams();
        params2.setBetaContextMounts(Arrays.asList(contextMount));

        SessionResult session2Result = agentBay.create(params2);
        if (!session2Result.isSuccess() || session2Result.getSession() == null) {
            throw new RuntimeException("Second session creation failed: " + session2Result.getErrorMessage());
        }

        Session session2 = session2Result.getSession();
        System.out.println("✅ Second session created: " + session2.getSessionId());

        try {
            System.out.println("\n🔍 Step 5: Verifying persisted data in second session...");

            String[] filesToCheck = {
                    "/tmp/mounted_data/config/app.json",
                    "/tmp/mounted_data/notes.txt",
            };

            int filesFound = 0;
            for (String filePath : filesToCheck) {
                System.out.println("\n🔍 Checking: " + filePath);
                FileContentResult readResult = session2.getFileSystem().readFile(filePath);

                if (readResult.isSuccess()) {
                    System.out.println("✅ File found!");
                    String content = readResult.getContent();
                    String preview = content.length() > 120 ? content.substring(0, 120) : content;
                    System.out.println("   📄 Content: " + preview);
                    filesFound++;
                } else {
                    System.out.println("❌ Not found: " + readResult.getErrorMessage());
                }
            }

            // Step 6: Dynamic mount demo (bind)
            System.out.println("\n🔧 Step 6: Dynamic mount using bind()...");
            ContextResult dynamicCtxResult = agentBay.getContext().get(
                    "dynamic-mount-" + System.currentTimeMillis(), true);
            if (dynamicCtxResult.isSuccess() && dynamicCtxResult.getContext() != null) {
                BetaContextMount dynamicMount = new BetaContextMount(
                        dynamicCtxResult.getContext().getId(), "/tmp/dynamic_mount");
                ContextBindResult bindResult = session2.getContext().bind(dynamicMount);
                if (bindResult.isSuccess()) {
                    System.out.println("✅ Dynamic mount bound successfully");
                    BoolResult writeResult = session2.getFileSystem().writeFile(
                            "/tmp/dynamic_mount/dynamic.txt", "Dynamically mounted data!", "overwrite");
                    if (writeResult.isSuccess()) {
                        System.out.println("✅ Wrote to dynamically mounted path");
                    }
                } else {
                    System.out.println("❌ Dynamic bind failed: " + bindResult.getErrorMessage());
                }

                // Clean up dynamic context
                agentBay.getContext().delete(dynamicCtxResult.getContext());
            }

            // Summary
            System.out.println("\n📊 === Persistence Summary ===");
            System.out.println("✅ Context ID: " + context.getId());
            System.out.println("✅ Session 1: " + session1Id + " (deleted)");
            System.out.println("✅ Session 2: " + session2.getSessionId() + " (active)");
            System.out.println("✅ Files found: " + filesFound + "/" + filesToCheck.length);

            if (filesFound == filesToCheck.length) {
                System.out.println("🎉 Context Mount persistence verification SUCCESSFUL!");
            } else {
                System.out.println("⚠️  Some files not found — mount may still be initializing");
            }

        } finally {
            System.out.println("\n🧹 Cleaning up second session...");
            DeleteResult deleteResult2 = agentBay.delete(session2);
            if (deleteResult2.isSuccess()) {
                System.out.println("✅ Second session deleted");
            }
        }

        // Clean up context
        System.out.println("\n🧹 Cleaning up context...");
        agentBay.getContext().delete(context);
        System.out.println("✅ Context deleted");
    }
}
