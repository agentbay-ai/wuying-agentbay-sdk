package com.aliyun.agentbay.exception;

/**
 * Thrown when an operation is attempted on a disconnected PTY handle.
 */
public class PtyNotConnectedException extends PtyException {

    public PtyNotConnectedException() {
        super("PTY handle is not connected");
    }

    public PtyNotConnectedException(String message) {
        super(message);
    }
}
