package com.aliyun.agentbay.exception;

/**
 * Exception for PTY operation errors.
 */
public class PtyException extends AgentBayException {

    public PtyException(String message) {
        super(message);
    }

    public PtyException(String message, Throwable cause) {
        super(message, cause);
    }
}
