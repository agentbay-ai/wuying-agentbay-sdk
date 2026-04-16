package com.aliyun.agentbay.env;

import com.aliyun.agentbay.mcp.McpTool;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.EnvResult;
import com.aliyun.agentbay.model.OperationResult;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Environment variable management service for AgentBay sessions.
 *
 * <p>Provides methods to set and get global environment variables that persist
 * across all MCP tools (shell, code interpreter, etc.) within a session.</p>
 */
public class Env extends BaseService {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String ENV_SERVER = "wuying_system";
    private static final List<String> ENV_TOOL_NAMES = Arrays.asList("set_env", "get_env");
    private volatile boolean toolsRegistered = false;

    public Env(Session session) {
        super(session);
    }

    private void ensureEnvToolsRegistered() {
        if (toolsRegistered) {
            return;
        }
        toolsRegistered = true;
        for (String toolName : ENV_TOOL_NAMES) {
            if (session.getMcpServerForTool(toolName).isEmpty()) {
                McpTool tool = new McpTool();
                tool.setName(toolName);
                tool.setServer(ENV_SERVER);
                session.getMcpTools().add(tool);
            }
        }
    }

    /**
     * Set or update global environment variables in the session sandbox.
     *
     * @param envs Map of environment variable key-value pairs. Must not be empty.
     * @return BoolResult indicating success or failure
     * @throws IllegalArgumentException if envs is null or empty
     */
    public BoolResult set(Map<String, String> envs) {
        ensureEnvToolsRegistered();
        if (envs == null || envs.isEmpty()) {
            throw new IllegalArgumentException("envs must not be empty");
        }

        List<Map<String, String>> envsArray = new ArrayList<>();
        for (Map.Entry<String, String> entry : envs.entrySet()) {
            Map<String, String> item = new HashMap<>();
            item.put("key", entry.getKey());
            item.put("value", entry.getValue());
            envsArray.add(item);
        }

        Map<String, Object> args = new HashMap<>();
        args.put("envs", envsArray);

        try {
            OperationResult result = callMcpTool("set_env", args);
            if (!result.isSuccess()) {
                return new BoolResult(
                    result.getRequestId(),
                    false,
                    null,
                    result.getErrorMessage()
                );
            }
            return new BoolResult(
                result.getRequestId(),
                true,
                true,
                ""
            );
        } catch (Exception e) {
            return new BoolResult("", false, null,
                "Failed to set environment variables: " + e.getMessage());
        }
    }

    /**
     * Get global environment variables from the session sandbox.
     *
     * @param keys Optional specific variable names to retrieve. If empty or null, returns all.
     * @return EnvResult containing the variable key-value pairs
     */
    public EnvResult get(String... keys) {
        ensureEnvToolsRegistered();
        Map<String, Object> args = new HashMap<>();
        if (keys != null && keys.length > 0) {
            args.put("keys", keys);
        }

        try {
            OperationResult result = callMcpTool("get_env", args);
            Map<String, String> envs = new HashMap<>();

            if (result.isSuccess() && result.getData() != null && !result.getData().isEmpty()) {
                try {
                    envs = objectMapper.readValue(result.getData(), new TypeReference<Map<String, String>>() { });
                } catch (Exception e) {
                    // Return success with empty envs if parsing fails
                }
            }

            return new EnvResult(
                result.getRequestId(),
                result.isSuccess(),
                envs,
                result.getErrorMessage()
            );
        } catch (Exception e) {
            return new EnvResult("", false, new HashMap<>(),
                "Failed to get environment variables: " + e.getMessage());
        }
    }
}
