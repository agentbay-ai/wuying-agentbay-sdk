/**
 * Options for creating a LifecyclePolicy.
 */
export interface LifecyclePolicyOptions {
  /** Idle release timeout in minutes (default: 5). Must be a positive integer. */
  idleReleaseTimeout?: number;
  /** Maximum session runtime in minutes from creation (default: 30). Must be a positive integer. */
  maxRuntime?: number;
  /** When true, disables all auto-release; the session only ends via delete(). */
  manualRelease?: boolean;
}

/**
 * Lifecycle policy for session management.
 *
 * Controls how and when a session is automatically released.
 * When used, SDK takes full control of lifecycle — console defaults are overridden.
 * All time values are in MINUTES.
 *
 * Three control dimensions:
 * - **idleReleaseTimeout**: Minutes of inactivity before auto-release (default: 5)
 * - **maxRuntime**: Absolute maximum session duration from creation (default: 30)
 * - **manualRelease**: Disable all auto-release; session only ends via `delete()`
 */
export class LifecyclePolicy {
  /** Minutes of inactivity before auto-release (default: 5). */
  readonly idleReleaseTimeout: number;
  /** Maximum session runtime in minutes from creation (default: 30). */
  readonly maxRuntime: number;
  /** When true, disables all auto-release; session only ends via delete(). */
  readonly manualRelease: boolean;

  constructor(options?: LifecyclePolicyOptions) {
    const opts = options || {};

    if (opts.manualRelease) {
      if (
        opts.idleReleaseTimeout !== undefined &&
        opts.idleReleaseTimeout !== null
      ) {
        throw new Error(
          "idleReleaseTimeout cannot be set when manualRelease=true. " +
            "In manual release mode, the session is only released via delete()."
        );
      }
      if (opts.maxRuntime !== undefined && opts.maxRuntime !== null) {
        throw new Error(
          "maxRuntime cannot be set when manualRelease=true. " +
            "In manual release mode, the session is only released via delete()."
        );
      }
      this.idleReleaseTimeout = 0;
      this.maxRuntime = 0;
      this.manualRelease = true;
      return;
    }

    const idle =
      opts.idleReleaseTimeout !== undefined && opts.idleReleaseTimeout !== null
        ? opts.idleReleaseTimeout
        : 5;
    const max =
      opts.maxRuntime !== undefined && opts.maxRuntime !== null
        ? opts.maxRuntime
        : 30;

    if (typeof idle !== "number" || !Number.isInteger(idle) || idle <= 0) {
      throw new Error(
        "idleReleaseTimeout must be a positive integer (minutes)"
      );
    }
    if (typeof max !== "number" || !Number.isInteger(max) || max <= 0) {
      throw new Error("maxRuntime must be a positive integer (minutes)");
    }

    this.idleReleaseTimeout = idle;
    this.maxRuntime = max;
    this.manualRelease = false;
  }
}
