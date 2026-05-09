/**
 * Example: session-scoped environment variables via the Env module.
 *
 * Demonstrates set, get (all and by keys), overwrite, and shell visibility.
 */

// Resolve SDK source when running from the repo (avoids stale dist/ without session.env).
import { AgentBay } from "../../../../../src";

const IMAGE_ID = "linux_latest";

async function main() {
  const apiKey = process.env.AGENTBAY_API_KEY;
  if (!apiKey) {
    throw new Error("AGENTBAY_API_KEY environment variable is not set");
  }

  const agentBay = new AgentBay({ apiKey });
  console.log("Creating session...");
  const { session, success, errorMessage } = await agentBay.create({
    imageId: IMAGE_ID,
  });
  if (!success || !session) {
    throw new Error(`Failed to create session: ${errorMessage ?? "unknown error"}`);
  }
  console.log(`Session ID: ${session.sessionId}`);

  try {
    console.log("\n1. Set environment variables");
    const setResult = await session.env.set({
      DEMO_APP: "agentbay",
      DEMO_STAGE: "dev",
    });
    if (!setResult.success) {
      throw new Error(`env.set failed: ${setResult.errorMessage}`);
    }
    console.log(`set ok (requestId: ${setResult.requestId})`);

    console.log("\n2. Get all environment variables (subset printed)");
    const all = await session.env.get();
    if (!all.success || !all.envs) {
      throw new Error(`env.get() failed: ${all.errorMessage}`);
    }
    console.log(`DEMO_APP=${all.envs["DEMO_APP"]}, DEMO_STAGE=${all.envs["DEMO_STAGE"]}`);

    console.log("\n3. Get specific keys only");
    const subset = await session.env.get(["DEMO_APP"]);
    if (!subset.success || !subset.envs) {
      throw new Error(`env.get(keys) failed: ${subset.errorMessage}`);
    }
    console.log(`DEMO_APP=${subset.envs["DEMO_APP"]}`);

    console.log("\n4. Overwrite an existing variable");
    await session.env.set({ DEMO_STAGE: "prod" });
    const afterOverwrite = await session.env.get(["DEMO_STAGE"]);
    if (afterOverwrite.envs?.["DEMO_STAGE"] !== "prod") {
      throw new Error(
        `expected DEMO_STAGE=prod, got ${afterOverwrite.envs?.["DEMO_STAGE"]}`
      );
    }
    console.log(`DEMO_STAGE is now ${afterOverwrite.envs["DEMO_STAGE"]}`);

    console.log("\n5. Verify variables are visible to shell commands");
    const cmd = await session.command.executeCommand("echo $DEMO_APP", 5000);
    if (!cmd.success) {
      throw new Error(`command failed: ${cmd.errorMessage}`);
    }
    const echoed = (cmd.stdout ?? "").trim();
    if (echoed !== "agentbay") {
      throw new Error(`expected shell to echo agentbay, got: ${JSON.stringify(echoed)}`);
    }
    console.log(`echo $DEMO_APP -> ${JSON.stringify(echoed)}`);
  } finally {
    console.log("\nDeleting session...");
    await agentBay.delete(session);
    console.log("Done.");
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
