package com.aliyun.agentbay.command;

import com.aliyun.agentbay.model.CommandResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.HashMap;
import java.util.Map;

/**
 * Async command execution service for session shells in the AgentBay cloud environment.
 * 
 * <p>Use this class for non-blocking command execution; for blocking/synchronous usage,
 * refer to the Command service in the sync API.
 */
public class Command extends BaseService {
    private static final String SERVER_SHELL = "wuying_shell";

    public Command(Session session) {
        super(session);
    }

    /**
     * Execute a shell command with default timeout (50000ms).
     *
     * @param command The shell command to execute
     * @return CommandResult Result object containing execution details
     */
    public CommandResult execute(String command) {
        return executeCommand(command, 50000);
    }

    /**
     * Execute a shell command with default timeout (50000ms).
     * Note: The input parameter is currently not used in the implementation.
     *
     * @param command The shell command to execute
     * @param input Input parameter (currently unused)
     * @return CommandResult Result object containing execution details
     */
    public CommandResult execute(String command, String input) {
        return executeCommand(command, 50000);
    }

    /**
     * Execute a shell command with specified timeout.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     */
    public CommandResult executeCommand(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs, null, null);
    }

    /**
     * Execute a shell command with optional working directory and environment variables.
     *
     * <p>Executes a shell command in the session environment with configurable timeout,
     * working directory, and environment variables. The command runs with session
     * user permissions in a Linux shell environment.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds (default: 50000ms/50s).
     * @param cwd The working directory for command execution. If not specified,
     *            the command runs in the default session directory
     * @param envs Environment variables as a map of key-value pairs.
     *             These variables are set for the command execution only
     * @return CommandResult Result object containing:
     *         <ul>
     *           <li>success: Whether the command executed successfully (exit_code == 0)</li>
     *           <li>output: Command output for backward compatibility (stdout + stderr)</li>
     *           <li>exitCode: The exit code of the command execution (0 for success)</li>
     *           <li>stdout: Standard output from the command execution</li>
     *           <li>stderr: Standard error from the command execution</li>
     *           <li>traceId: Trace ID for error tracking (only present when exit_code != 0)</li>
     *           <li>requestId: Unique identifier for this API request</li>
     *           <li>errorMessage: Error description if execution failed</li>
     *         </ul>
     * @throws IllegalArgumentException If environment variables contain non-string keys or values
     *
     */
    public CommandResult executeCommand(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        if (envs != null) {
            java.util.List<String> invalidVars = new java.util.ArrayList<>();
            for (Map.Entry<String, String> entry : envs.entrySet()) {
                Object key = entry.getKey();
                Object value = entry.getValue();

                if (!(key instanceof String)) {
                    invalidVars.add(String.format("key '%s' (type: %s)", key, key.getClass().getSimpleName()));
                }
                if (!(value instanceof String)) {
                    invalidVars.add(String.format("value for key '%s' (type: %s)", key, value.getClass().getSimpleName()));
                }
            }

            if (!invalidVars.isEmpty()) {
                throw new IllegalArgumentException(
                    "Invalid environment variables: all keys and values must be strings. " +
                    "Found invalid entries: " + String.join(", ", invalidVars)
                );
            }
        }

        try {
            Map<String, Object> args = new HashMap<>();
            args.put("command", command);
            args.put("timeout_ms", timeoutMs);

            if (cwd != null) {
                args.put("cwd", cwd);
            }

            if (envs != null) {
                args.put("envs", envs);
            }

            OperationResult result = callMcpTool("shell", args);

            if (result.isSuccess()) {
                String rawData = result.getData() == null ? "" : result.getData();
                ParsedShellPayload parsed = parseShellPayload(rawData);
                return new CommandResult(result.getRequestId(),
                        parsed.exitCode == 0,
                        parsed.stdout + parsed.stderr,
                        "",
                        parsed.exitCode,
                        parsed.stdout,
                        parsed.stderr,
                        parsed.traceId);
            } else {
                String rawErr = result.getErrorMessage() == null ? "" : result.getErrorMessage();
                ParsedShellPayload parsed = parseShellPayload(rawErr);
                String errorMessage = !parsed.stderr.isEmpty() ? parsed.stderr
                        : (rawErr.isEmpty() ? "Failed to execute command" : rawErr);
                int exitCode = parsed.exitCode != 0 ? parsed.exitCode : 1;
                return new CommandResult(result.getRequestId(), false,
                        parsed.stdout + parsed.stderr, errorMessage, exitCode,
                        parsed.stdout, parsed.stderr, parsed.traceId);
            }

        } catch (Exception e) {
            return new CommandResult("", false, "", "Failed to execute command: " + e.getMessage(), 1,
                    "", "", "");
        }
    }

    /**
     * Parsed payload from a shell-tool MCP response.
     *
     * <p>The MCP server's shell tool can return data in different shapes depending on the
     * sandbox image. The two known shapes are:
     * <ol>
     *   <li><b>Wrapped</b>: {@code {"exit_code":0,"stdout":"...","stderr":"...","traceId":"..."}}
     *       — used by code_latest and similar images.</li>
     *   <li><b>Raw</b>: the command's stdout returned verbatim with no JSON wrapping
     *       — used by openclaw / imgc-* and similar custom images.</li>
     * </ol>
     *
     * <p>This method detects the wrapped shape conservatively (requires both an integer
     * {@code exit_code} field <b>and</b> at least one of {@code stdout}/{@code stderr}, OR
     * both {@code stdout} and {@code stderr} together). Anything else — including JSON
     * objects/arrays/scalars and plain text — is treated as raw command output.
     */
    private static class ParsedShellPayload {
        final String stdout;
        final String stderr;
        final int exitCode;
        final String traceId;

        ParsedShellPayload(String stdout, String stderr, int exitCode, String traceId) {
            this.stdout = stdout;
            this.stderr = stderr;
            this.exitCode = exitCode;
            this.traceId = traceId;
        }
    }

    private static ParsedShellPayload parseShellPayload(String rawData) {
        if (rawData == null || rawData.isEmpty()) {
            return new ParsedShellPayload("", "", 0, "");
        }
        try {
            ObjectMapper mapper = new ObjectMapper();
            JsonNode node = mapper.readTree(rawData);
            if (looksLikeWrappedShellPayload(node)) {
                String stdout = node.has("stdout") ? node.get("stdout").asText() : "";
                String stderr = node.has("stderr") ? node.get("stderr").asText() : "";
                int exitCode = node.has("exit_code") ? node.get("exit_code").asInt() : 0;
                String traceId = node.has("traceId") ? node.get("traceId").asText() : "";
                return new ParsedShellPayload(stdout, stderr, exitCode, traceId);
            }
        } catch (Exception ignored) {
            // Not valid JSON — fall through to raw treatment.
        }
        // Raw stdout: return the entire payload verbatim.
        return new ParsedShellPayload(rawData, "", 0, "");
    }

    /**
     * Conservatively determines whether a JSON node looks like the shell-tool wrapped
     * envelope. We require strong signals to avoid mistaking a user command's JSON output
     * for the wrapper.
     */
    private static boolean looksLikeWrappedShellPayload(JsonNode node) {
        if (node == null || !node.isObject()) {
            return false;
        }
        boolean hasIntExitCode = node.has("exit_code") && node.get("exit_code").isInt();
        boolean hasStdout = node.has("stdout") && node.get("stdout").isTextual();
        boolean hasStderr = node.has("stderr") && node.get("stderr").isTextual();
        // Strong signal #1: integer exit_code + at least one textual stdout/stderr.
        if (hasIntExitCode && (hasStdout || hasStderr)) {
            return true;
        }
        // Strong signal #2: both textual stdout and stderr present (exit_code may default to 0).
        return hasStdout && hasStderr;
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     * @see #executeCommand(String, int, String, Map)
     */
    public CommandResult run(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @param cwd The working directory for command execution
     * @param envs Environment variables as a map of key-value pairs
     * @return CommandResult Result object containing execution details
     */
    public CommandResult run(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @return CommandResult Result object containing execution details
     */
    public CommandResult exec(String command, int timeoutMs) {
        return executeCommand(command, timeoutMs);
    }

    /**
     * Alias of executeCommand() for better ergonomics and LLM friendliness.
     *
     * @param command The shell command to execute
     * @param timeoutMs Timeout in milliseconds
     * @param cwd The working directory for command execution
     * @param envs Environment variables as a map of key-value pairs
     * @return CommandResult Result object containing execution details
     */
    public CommandResult exec(String command, int timeoutMs, String cwd, Map<String, String> envs) {
        return executeCommand(command, timeoutMs, cwd, envs);
    }

}