package com.aliyun.agentbay.pty;

import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.exception.PtyException;
import com.aliyun.agentbay.exception.PtyNotConnectedException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.nio.charset.CharacterCodingException;
import java.nio.charset.CharsetDecoder;
import java.nio.charset.CodingErrorAction;
import java.nio.charset.StandardCharsets;
import java.nio.ByteBuffer;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

/**
 * An active connection to a PTY session.
 */
public class PtyHandle {
    private static final Logger logger = LoggerFactory.getLogger(PtyHandle.class);
    private static final String PTY_TARGET = "PTY_SERVER";
    private static final int MAX_TERMINAL_SIZE = 500;

    private final String ptySessionId;
    private final Pty ptyModule;
    private final Consumer<byte[]> onData;
    private volatile boolean connected;
    private volatile Integer exitCode;
    private volatile String errorMsg;

    PtyHandle(String ptySessionId, Pty ptyModule, Consumer<byte[]> onData) {
        this.ptySessionId = ptySessionId;
        this.ptyModule = ptyModule;
        this.onData = onData;
        this.connected = true;
    }

    public String getPtySessionId() {
        return ptySessionId;
    }

    public boolean isConnected() {
        return connected;
    }

    public Integer getExitCode() {
        return exitCode;
    }

    /**
     * Send input bytes to the PTY.
     */
    public void sendInput(byte[] data) throws PtyNotConnectedException {
        if (!connected) throw new PtyNotConnectedException();

        String text;
        String encoding;
        if (isValidUtf8(data)) {
            text = new String(data, StandardCharsets.UTF_8);
            encoding = "utf8";
        } else {
            text = Base64.getEncoder().encodeToString(data);
            encoding = "base64";
        }

        WsClient wsClient = ptyModule.getWsClient();
        Map<String, Object> params = new HashMap<>();
        params.put("ptySessionId", ptySessionId);
        params.put("encoding", encoding);
        params.put("data", text);

        Map<String, Object> msg = new HashMap<>();
        msg.put("method", "pty.input");
        msg.put("params", params);
        wsClient.sendMessage(PTY_TARGET, msg);
    }

    /**
     * Resize the terminal.
     */
    public void resize(int cols, int rows) throws PtyNotConnectedException, PtyException {
        if (!connected) throw new PtyNotConnectedException();
        if (cols < 1 || cols > MAX_TERMINAL_SIZE || rows < 1 || rows > MAX_TERMINAL_SIZE) {
            throw new PtyException(
                "Invalid terminal size: cols=" + cols + ", rows=" + rows + " (must be 1-" + MAX_TERMINAL_SIZE + ")"
            );
        }

        WsClient wsClient = ptyModule.getWsClient();
        Map<String, Object> params = new HashMap<>();
        params.put("ptySessionId", ptySessionId);
        params.put("cols", cols);
        params.put("rows", rows);

        Map<String, Object> msg = new HashMap<>();
        msg.put("method", "pty.resize");
        msg.put("params", params);
        wsClient.sendMessage(PTY_TARGET, msg);
    }

    /**
     * Kill the PTY process.
     */
    public void kill() throws Exception {
        if (!connected) throw new PtyNotConnectedException();

        WsClient wsClient = ptyModule.getWsClient();
        Map<String, Object> params = new HashMap<>();
        params.put("ptySessionId", ptySessionId);

        Map<String, Object> msg = new HashMap<>();
        msg.put("method", "pty.kill");
        msg.put("params", params);
        wsClient.call(PTY_TARGET, msg, 30000);
    }

    /**
     * Wait for the PTY process to exit and return its exit code.
     *
     * @param timeoutMs Timeout in milliseconds (0 for no timeout)
     * @return The exit code of the PTY process
     * @throws PtyException on error or timeout
     */
    public int wait(int timeoutMs) throws PtyException {
        long deadline = timeoutMs > 0 ? System.currentTimeMillis() + timeoutMs : 0;

        while (exitCode == null && errorMsg == null) {
            if (deadline > 0 && System.currentTimeMillis() >= deadline) {
                throw new PtyException("PTY wait timed out after " + timeoutMs + "ms");
            }
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                throw new PtyException("PTY wait interrupted");
            }
        }
        if (errorMsg != null) {
            throw new PtyException(errorMsg);
        }
        return exitCode;
    }

    /**
     * Disconnect from the PTY (process continues on server).
     */
    public void disconnect() {
        if (!connected) return;
        connected = false;
        ptyModule.unregisterHandle(ptySessionId);
    }

    void handleOutput(byte[] data) {
        if (onData != null) {
            try {
                onData.accept(data);
            } catch (Exception e) {
                logger.warn("on_data callback raised an exception", e);
            }
        }
    }

    void handleExit(int code) {
        this.exitCode = code;
        this.connected = false;
    }

    void handleError(String msg) {
        this.errorMsg = msg;
        this.connected = false;
    }

    private static boolean isValidUtf8(byte[] data) {
        CharsetDecoder decoder = StandardCharsets.UTF_8.newDecoder()
            .onMalformedInput(CodingErrorAction.REPORT)
            .onUnmappableCharacter(CodingErrorAction.REPORT);
        try {
            decoder.decode(ByteBuffer.wrap(data));
            return true;
        } catch (CharacterCodingException e) {
            return false;
        }
    }
}
