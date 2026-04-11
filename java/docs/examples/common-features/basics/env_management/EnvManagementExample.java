import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.EnvResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.HashMap;
import java.util.Map;

/**
 * Example: session-scoped environment variables via the Env module.
 *
 * Demonstrates set, get (all and by keys), overwrite, and shell visibility.
 *
 * <p>Build the SDK module first, then compile this file with the same classpath as the module
 * (see README in this directory).</p>
 */
public class EnvManagementExample {

    private static final String IMAGE_ID = "AIO_ubuntu2404";

    public static void main(String[] args) {
        AgentBay agentBay;
        try {
            agentBay = new AgentBay();
        } catch (AgentBayException e) {
            System.err.println("Failed to create AgentBay client: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        CreateSessionParams params = new CreateSessionParams();
        params.setImageId(IMAGE_ID);

        SessionResult createResult;
        try {
            System.out.println("Creating session...");
            createResult = agentBay.create(params);
        } catch (AgentBayException e) {
            System.err.println("create failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        if (!createResult.isSuccess() || createResult.getSession() == null) {
            System.err.println("Failed to create session: " + createResult.getErrorMessage());
            return;
        }

        Session session = createResult.getSession();
        System.out.println("Session ID: " + session.getSessionId());

        try {
            System.out.println("\n1. Set environment variables");
            Map<String, String> initial = new HashMap<>();
            initial.put("DEMO_APP", "agentbay");
            initial.put("DEMO_STAGE", "dev");
            BoolResult setResult = session.getEnv().set(initial);
            if (!setResult.isSuccess()) {
                throw new IllegalStateException("env.set failed: " + setResult.getErrorMessage());
            }
            System.out.println("set ok (requestId: " + setResult.getRequestId() + ")");

            System.out.println("\n2. Get all environment variables (subset printed)");
            EnvResult all = session.getEnv().get();
            if (!all.isSuccess()) {
                throw new IllegalStateException("env.get() failed: " + all.getErrorMessage());
            }
            Map<String, String> envs = all.getEnvs();
            System.out.println("DEMO_APP=" + envs.get("DEMO_APP") + ", DEMO_STAGE=" + envs.get("DEMO_STAGE"));

            System.out.println("\n3. Get specific keys only");
            EnvResult subset = session.getEnv().get("DEMO_APP");
            if (!subset.isSuccess()) {
                throw new IllegalStateException("env.get(keys) failed: " + subset.getErrorMessage());
            }
            System.out.println("DEMO_APP=" + subset.getEnvs().get("DEMO_APP"));

            System.out.println("\n4. Overwrite an existing variable");
            Map<String, String> overwrite = new HashMap<>();
            overwrite.put("DEMO_STAGE", "prod");
            session.getEnv().set(overwrite);
            EnvResult after = session.getEnv().get("DEMO_STAGE");
            if (!"prod".equals(after.getEnvs().get("DEMO_STAGE"))) {
                throw new IllegalStateException(
                    "expected DEMO_STAGE=prod, got " + after.getEnvs().get("DEMO_STAGE"));
            }
            System.out.println("DEMO_STAGE is now " + after.getEnvs().get("DEMO_STAGE"));

            System.out.println("\n5. Verify variables are visible to shell commands");
            CommandResult cmd = session.getCommand().executeCommand("echo $DEMO_APP", 5000);
            if (!cmd.isSuccess()) {
                throw new IllegalStateException("command failed: " + cmd.getErrorMessage());
            }
            String echoed = cmd.getStdout() != null ? cmd.getStdout().trim() : "";
            if (!"agentbay".equals(echoed)) {
                throw new IllegalStateException("expected shell to echo agentbay, got: " + echoed);
            }
            System.out.println("echo $DEMO_APP -> \"" + echoed + "\"");
        } catch (IllegalStateException e) {
            System.err.println(e.getMessage());
        } finally {
            System.out.println("\nDeleting session...");
            try {
                session.delete();
                System.out.println("Done.");
            } catch (Exception e) {
                System.err.println("delete failed: " + e.getMessage());
            }
        }
    }
}
