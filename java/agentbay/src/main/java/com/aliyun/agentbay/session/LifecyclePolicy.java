package com.aliyun.agentbay.session;

/**
 * Lifecycle policy for session management.
 *
 * Controls how and when a session is automatically released.
 * When used, SDK takes full control of lifecycle - console defaults are overridden.
 * All time values are in MINUTES.
 */
public class LifecyclePolicy {

    private int idleReleaseTimeout;
    private int maxRuntime;
    private boolean manualRelease;

    /**
     * Default constructor: idle=5min, max=30min, manual=false
     */
    public LifecyclePolicy() {
        this.idleReleaseTimeout = 5;
        this.maxRuntime = 30;
        this.manualRelease = false;
    }

    /**
     * Custom timeouts constructor.
     *
     * @param idleReleaseTimeout idle timeout in minutes (must be positive)
     * @param maxRuntime maximum runtime in minutes (must be positive)
     */
    public LifecyclePolicy(int idleReleaseTimeout, int maxRuntime) {
        if (idleReleaseTimeout <= 0) {
            throw new IllegalArgumentException("idleReleaseTimeout must be a positive integer (minutes)");
        }
        if (maxRuntime <= 0) {
            throw new IllegalArgumentException("maxRuntime must be a positive integer (minutes)");
        }
        this.idleReleaseTimeout = idleReleaseTimeout;
        this.maxRuntime = maxRuntime;
        this.manualRelease = false;
    }

    /**
     * Full constructor with manual release validation.
     *
     * @param idleReleaseTimeout idle timeout in minutes
     * @param maxRuntime maximum runtime in minutes
     * @param manualRelease when true, idle and max cannot be non-zero defaults
     */
    public LifecyclePolicy(int idleReleaseTimeout, int maxRuntime, boolean manualRelease) {
        if (manualRelease) {
            if (idleReleaseTimeout != 0 || maxRuntime != 0) {
                throw new IllegalArgumentException(
                    "idleReleaseTimeout and maxRuntime cannot be set when manualRelease=true");
            }
            this.idleReleaseTimeout = 0;
            this.maxRuntime = 0;
            this.manualRelease = true;
            return;
        }
        if (idleReleaseTimeout <= 0) {
            throw new IllegalArgumentException("idleReleaseTimeout must be a positive integer (minutes)");
        }
        if (maxRuntime <= 0) {
            throw new IllegalArgumentException("maxRuntime must be a positive integer (minutes)");
        }
        this.idleReleaseTimeout = idleReleaseTimeout;
        this.maxRuntime = maxRuntime;
        this.manualRelease = false;
    }

    /**
     * Factory method for manual release mode.
     *
     * @return policy with manual release only (no automatic idle/max limits)
     */
    public static LifecyclePolicy manualRelease() {
        LifecyclePolicy lp = new LifecyclePolicy();
        lp.idleReleaseTimeout = 0;
        lp.maxRuntime = 0;
        lp.manualRelease = true;
        return lp;
    }

    public int getIdleReleaseTimeout() {
        return idleReleaseTimeout;
    }

    public int getMaxRuntime() {
        return maxRuntime;
    }

    public boolean isManualRelease() {
        return manualRelease;
    }
}
