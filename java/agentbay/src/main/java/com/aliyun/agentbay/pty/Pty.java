package com.aliyun.agentbay.pty;

import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.exception.PtyException;
import com.aliyun.agentbay.session.Session;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.util.ArrayList;
import java.util.Base64;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * PTY module entry point – accessed as session.getPty().
 */
public class Pty {
    private static final Logger logger = LoggerFactory.getLogger(Pty.class);
    private static final String PTY_TARGET = "PTY_SERVER";
    private static final int MAX_TERMINAL_SIZE = 500;

    private static final Map<String, String> DEFAULT_ENVS = new HashMap<>();
    static {
        DEFAULT_ENVS.put("TERM", "xterm-256color");
        DEFAULT_ENVS.put("LANG", "en_US.UTF-8");
    }

    private final Session session;
    private volatile WsClient wsClient;
    private final ConcurrentHashMap<String, PtyHandle> handles = new ConcurrentHashMap<>();
    private volatile boolean callbackRegistered;

    public Pty(Session session) {
        this.session = session;
    }

    WsClient getWsClient() {
        if (wsClient == null) {
            wsClient = session.getWsClient();
        }
        return wsClient;
    }

    private void ensureCallback() {
        if (callbackRegistered) return;
        synchronized (this) {
            if (callbackRegistered) return;
            WsClient ws = getWsClient();
            ws.connect();
            ws.registerCallback(PTY_TARGET, this::pushCallback);
            callbackRegistered = true;
        }
    }

    @SuppressWarnings("unchecked")
    private void pushCallback(Map<String, Object> payload) {
        Object dataObj = payload.get("data");
        if (!(dataObj instanceof Map)) return;
        Map<String, Object> data = (Map<String, Object>) dataObj;

        String eventType = data.get("eventType") instanceof String ? (String) data.get("eventType") : "";
        String ptySessionId = data.get("ptySessionId") instanceof String ? (String) data.get("ptySessionId") : "";

        PtyHandle handle = handles.get(ptySessionId);
        if (handle == null) return;

        switch (eventType) {
            case "pty.output": {
                String encoding = data.get("encoding") instanceof String ? (String) data.get("encoding") : "utf8";
                String raw = data.get("data") instanceof String ? (String) data.get("data") : "";
                byte[] dataBytes;
                if ("base64".equals(encoding)) {
                    dataBytes = Base64.getDecoder().decode(raw);
                } else {
                    dataBytes = raw.getBytes(java.nio.charset.StandardCharsets.UTF_8);
                }
                handle.handleOutput(dataBytes);
                break;
            }
            case "pty.exit": {
                int exitCode = -1;
                Object ecObj = data.get("exitCode");
                if (ecObj instanceof Number) {
                    exitCode = ((Number) ecObj).intValue();
                }
                handle.handleExit(exitCode);
                break;
            }
            case "pty.error": {
                String errMsg = data.get("error") instanceof String ? (String) data.get("error") : "Unknown PTY error";
                handle.handleError(errMsg);
                break;
            }
            default:
                break;
        }
    }

    void unregisterHandle(String ptySessionId) {
        handles.remove(ptySessionId);
    }

    /**
     * Create a new PTY session.
     *
     * @param cols      Terminal columns (default 80)
     * @param rows      Terminal rows (default 24)
     * @param cwd       Working directory (null for default)
     * @param envs      Extra environment variables (null for default)
     * @param shell     Shell program (null for default)
     * @param onData    Callback for output data (may be null)
     * @param timeoutMs Timeout in milliseconds (0 defaults to 30 000)
     * @return A PtyHandle connected to the new session
     * @throws PtyException if the terminal size is invalid
     * @throws Exception    on communication failure
     */
    @SuppressWarnings("unchecked")
    public PtyHandle create(int cols, int rows, String cwd,
                            Map<String, String> envs, String shell,
                            Consumer<byte[]> onData, long timeoutMs) throws Exception {
        if (cols <= 0) cols = 80;
        if (rows <= 0) rows = 24;
        if (timeoutMs <= 0) timeoutMs = 30000;

        if (cols > MAX_TERMINAL_SIZE || rows > MAX_TERMINAL_SIZE) {
            throw new PtyException(
                "Invalid terminal size: cols=" + cols + ", rows=" + rows + " (must be 1-" + MAX_TERMINAL_SIZE + ")"
            );
        }

        ensureCallback();
        WsClient ws = getWsClient();

        Map<String, Object> params = new HashMap<>();
        params.put("cols", cols);
        params.put("rows", rows);
        if (cwd != null) params.put("cwd", cwd);
        Map<String, String> mergedEnvs = new HashMap<>(DEFAULT_ENVS);
        if (envs != null) mergedEnvs.putAll(envs);
        params.put("envs", mergedEnvs);
        if (shell != null) params.put("shell", shell);

        Map<String, Object> reqData = new HashMap<>();
        reqData.put("method", "pty.create");
        reqData.put("params", params);

        Map<String, Object> response = ws.call(PTY_TARGET, reqData, timeoutMs);

        Map<String, Object> result = response.get("result") instanceof Map
            ? (Map<String, Object>) response.get("result") : new HashMap<>();
        String ptySessionId = result.get("ptySessionId") instanceof String
            ? (String) result.get("ptySessionId") : null;
        if (ptySessionId == null || ptySessionId.isEmpty()) {
            throw new PtyException("pty.create did not return ptySessionId: " + response);
        }

        PtyHandle handle = new PtyHandle(ptySessionId, this, onData);
        handles.put(ptySessionId, handle);
        return handle;
    }

    /**
     * Create a new PTY session with default settings.
     */
    public PtyHandle create() throws Exception {
        return create(80, 24, null, null, null, null, 30000);
    }

    /**
     * Create a new PTY session with size and callback.
     */
    public PtyHandle create(int cols, int rows, Consumer<byte[]> onData) throws Exception {
        return create(cols, rows, null, null, null, onData, 30000);
    }

    /**
     * List all active PTY sessions.
     */
    @SuppressWarnings("unchecked")
    public List<PtySession> list() throws Exception {
        ensureCallback();
        WsClient ws = getWsClient();

        Map<String, Object> reqData = new HashMap<>();
        reqData.put("method", "pty.list");
        reqData.put("params", new HashMap<>());

        Map<String, Object> response = ws.call(PTY_TARGET, reqData, 30000);

        Map<String, Object> result = response.get("result") instanceof Map
            ? (Map<String, Object>) response.get("result") : new HashMap<>();
        List<?> idsRaw = result.get("ptySessionIds") instanceof List
            ? (List<?>) result.get("ptySessionIds") : new ArrayList<>();

        List<PtySession> sessions = new ArrayList<>();
        for (Object idObj : idsRaw) {
            String sid = idObj instanceof String ? (String) idObj : null;
            if (sid == null || sid.isEmpty()) continue;

            String status = "running";
            Integer exitCode = null;
            PtyHandle h = handles.get(sid);
            if (h != null && h.getExitCode() != null) {
                status = "exited";
                exitCode = h.getExitCode();
            }
            sessions.add(new PtySession(sid, 0, 0, status, exitCode));
        }
        return sessions;
    }

    /**
     * Reconnect to an existing PTY session.
     */
    @SuppressWarnings("unchecked")
    public PtyHandle connect(String ptySessionId, Consumer<byte[]> onData) throws Exception {
        ensureCallback();
        WsClient ws = getWsClient();

        Map<String, Object> params = new HashMap<>();
        params.put("ptySessionId", ptySessionId);

        Map<String, Object> reqData = new HashMap<>();
        reqData.put("method", "pty.connect");
        reqData.put("params", params);

        Map<String, Object> response = ws.call(PTY_TARGET, reqData, 30000);

        Map<String, Object> result = response.get("result") instanceof Map
            ? (Map<String, Object>) response.get("result") : new HashMap<>();
        String returnedId = result.get("ptySessionId") instanceof String
            ? (String) result.get("ptySessionId") : ptySessionId;

        PtyHandle handle = new PtyHandle(returnedId, this, onData);
        handles.put(returnedId, handle);
        return handle;
    }

    /**
     * Kill a PTY session by ID.
     */
    public void kill(String ptySessionId) throws Exception {
        ensureCallback();
        WsClient ws = getWsClient();

        Map<String, Object> params = new HashMap<>();
        params.put("ptySessionId", ptySessionId);

        Map<String, Object> reqData = new HashMap<>();
        reqData.put("method", "pty.kill");
        reqData.put("params", params);

        ws.call(PTY_TARGET, reqData, 30000);

        PtyHandle h = handles.remove(ptySessionId);
        if (h != null) {
            h.handleExit(-9);
        }
    }
}
