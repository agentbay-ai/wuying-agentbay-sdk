import { Session } from "../session";
import { CommandResult } from "../types/api-response";

/**
 * Parsed result from a shell-tool MCP response payload.
 */
interface ParsedShellPayload {
  stdout: string;
  stderr: string;
  exitCode: number;
  traceId: string;
}

/**
 * Conservatively determines whether a parsed JSON object looks like the
 * shell-tool wrapped envelope `{exit_code, stdout, stderr}`.
 *
 * Different sandbox images return data in different shapes:
 * - **Wrapped** (code_latest): `{"exit_code":0,"stdout":"...","stderr":"..."}`
 * - **Raw** (imgc-* / openclaw): the command's stdout returned verbatim
 *
 * We require strong signals to avoid mistaking user command JSON output
 * for the wrapper:
 * 1. Integer `exit_code` + at least one string `stdout`/`stderr`, OR
 * 2. Both string `stdout` and `stderr` present.
 */
function looksLikeWrappedShellPayload(obj: any): boolean {
  if (obj == null || typeof obj !== "object" || Array.isArray(obj)) {
    return false;
  }
  const hasIntExitCode =
    typeof obj.exit_code === "number" && Number.isInteger(obj.exit_code);
  const hasStdout = typeof obj.stdout === "string";
  const hasStderr = typeof obj.stderr === "string";
  if (hasIntExitCode && (hasStdout || hasStderr)) {
    return true;
  }
  return hasStdout && hasStderr;
}

/**
 * Parses a shell-tool MCP response payload into a structured result.
 * Detects the wrapped format conservatively; anything else is treated
 * as raw command output returned verbatim.
 */
function parseShellPayload(rawData: string): ParsedShellPayload {
  if (!rawData) {
    return { stdout: "", stderr: "", exitCode: 0, traceId: "" };
  }
  try {
    const parsed = JSON.parse(rawData);
    if (looksLikeWrappedShellPayload(parsed)) {
      return {
        stdout: parsed.stdout || "",
        stderr: parsed.stderr || "",
        exitCode: typeof parsed.exit_code === "number" ? parsed.exit_code : 0,
        traceId: parsed.traceId || "",
      };
    }
  } catch {
    // Not valid JSON — fall through to raw treatment.
  }
  return { stdout: rawData, stderr: "", exitCode: 0, traceId: "" };
}

/**
 * Handles command execution operations in the AgentBay cloud environment.
 */
export class Command {
  private session: Session;

  /**
   * Initialize a Command object.
   *
   * @param session - The Session instance that this Command belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Sanitizes error messages to remove sensitive information like API keys.
   *
   * @param error - The error to sanitize
   * @returns The sanitized error
   */
  private sanitizeError(error: any): any {
    if (!error) {
      return error;
    }

    const errorString = String(error);
    return errorString.replace(/Bearer\s+[^\s]+/g, "Bearer [REDACTED]");
  }

  /**
   * Execute a shell command with optional working directory and environment variables.
   *
   * Executes a shell command in the session environment with configurable timeout,
   * working directory, and environment variables. The command runs with session
   * user permissions in a Linux shell environment.
   *
   * @param command - The shell command to execute
   * @param timeoutMs - Timeout in milliseconds (default: 50000ms/50s).
   * @param cwd - The working directory for command execution. If not specified,
   *              the command runs in the default session directory
   * @param envs - Environment variables as a dictionary of key-value pairs.
   *              These variables are set for the command execution only
   *
   * @returns Promise resolving to CommandResult containing:
   *          - success: Whether the command executed successfully (exitCode === 0)
   *          - output: Command output for backward compatibility (stdout + stderr)
   *          - exitCode: The exit code of the command execution (0 for success)
   *          - stdout: Standard output from the command execution
   *          - stderr: Standard error from the command execution
   *          - traceId: Trace ID for error tracking (only present when exitCode !== 0)
   *          - requestId: Unique identifier for this API request
   *          - errorMessage: Error description if execution failed
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const cmdResult = await result.session.command.executeCommand('echo "Hello"', 5000);
   *   console.log('Command output:', cmdResult.output);
   *   console.log('Exit code:', cmdResult.exitCode);
   *   console.log('Stdout:', cmdResult.stdout);
   *   await result.session.delete();
   * }
   * ```
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: 'your_api_key' });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const cmdResult = await result.session.command.executeCommand(
   *     'pwd',
   *     5000,
   *     '/tmp',
   *     { TEST_VAR: 'test_value' }
   *   );
   *   console.log('Working directory:', cmdResult.stdout);
   *   await result.session.delete();
   * }
   * ```
   */
  async executeCommand(
    command: string,
    timeoutMs = 1000,
    cwd?: string,
    envs?: Record<string, string>
  ): Promise<CommandResult> {
    // Validate environment variables - strict type checking (before try block to allow Error to propagate)
    if (envs !== undefined) {
      const invalidVars: string[] = [];
      for (const [key, value] of Object.entries(envs)) {
        if (typeof key !== "string") {
          invalidVars.push(`key '${key}' (type: ${typeof key})`);
        }
        if (typeof value !== "string") {
          invalidVars.push(`value for key '${key}' (type: ${typeof value})`);
        }
      }

      if (invalidVars.length > 0) {
        throw new Error(
          `Invalid environment variables: all keys and values must be strings. ` +
            `Found invalid entries: ${invalidVars.join(", ")}`
        );
      }
    }

    try {
      // Build request arguments
      const args: Record<string, any> = {
        command,
        timeout_ms: timeoutMs,
      };
      if (cwd !== undefined) {
        args.cwd = cwd;
      }
      if (envs !== undefined) {
        args.envs = envs;
      }

      const result = await this.session.callMcpTool("shell", args, false);

      if (result.success) {
        const rawData =
          result.data == null
            ? ""
            : typeof result.data === "string"
            ? result.data
            : String(result.data);
        const parsed = parseShellPayload(rawData);
        return {
          requestId: result.requestId,
          success: parsed.exitCode === 0,
          output: parsed.stdout + parsed.stderr,
          exitCode: parsed.exitCode,
          stdout: parsed.stdout,
          stderr: parsed.stderr,
          traceId: parsed.traceId || undefined,
          errorMessage: result.errorMessage,
        };
      } else {
        const rawErr = result.errorMessage || "";
        const parsed = parseShellPayload(rawErr);
        const effectiveExitCode = parsed.exitCode !== 0 ? parsed.exitCode : 1;
        const effectiveError =
          parsed.stderr || rawErr || "Failed to execute command";
        return {
          requestId: result.requestId,
          success: false,
          output: parsed.stdout + parsed.stderr,
          exitCode: effectiveExitCode,
          stdout: parsed.stdout,
          stderr: parsed.stderr,
          traceId: parsed.traceId || undefined,
          errorMessage: effectiveError,
        };
      }
    } catch (error) {
      return {
        requestId: "",
        success: false,
        output: "",
        errorMessage: `Failed to execute command: ${error}`,
      };
    }
  }

  /**
   * Alias of executeCommand().
   */
  async run(
    command: string,
    timeoutMs = 1000,
    cwd?: string,
    envs?: Record<string, string>
  ): Promise<CommandResult> {
    return await this.executeCommand(command, timeoutMs, cwd, envs);
  }

  /**
   * Alias of executeCommand().
   */
  async exec(
    command: string,
    timeoutMs = 1000,
    cwd?: string,
    envs?: Record<string, string>
  ): Promise<CommandResult> {
    return await this.executeCommand(command, timeoutMs, cwd, envs);
  }
}
