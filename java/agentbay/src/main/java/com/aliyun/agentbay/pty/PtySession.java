package com.aliyun.agentbay.pty;

/**
 * Read-only snapshot of a PTY session.
 */
public class PtySession {
    private final String ptySessionId;
    private final int cols;
    private final int rows;
    private final String status;
    private final Integer exitCode;

    public PtySession(String ptySessionId, int cols, int rows, String status, Integer exitCode) {
        this.ptySessionId = ptySessionId;
        this.cols = cols;
        this.rows = rows;
        this.status = status;
        this.exitCode = exitCode;
    }

    public String getPtySessionId() {
        return ptySessionId;
    }

    public int getCols() {
        return cols;
    }

    public int getRows() {
        return rows;
    }

    public String getStatus() {
        return status;
    }

    public Integer getExitCode() {
        return exitCode;
    }
}
