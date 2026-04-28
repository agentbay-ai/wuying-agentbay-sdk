export interface LifecyclePolicyOptions {
  idleReleaseTimeout?: number;
  maxRuntime?: number;
  manualRelease?: boolean;
}

export class LifecyclePolicy {
  readonly idleReleaseTimeout: number;
  readonly maxRuntime: number;
  readonly manualRelease: boolean;

  constructor(options?: LifecyclePolicyOptions) {
    const opts = options || {};

    if (opts.manualRelease) {
      if (opts.idleReleaseTimeout !== undefined && opts.idleReleaseTimeout !== null) {
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
      throw new Error("idleReleaseTimeout must be a positive integer (minutes)");
    }
    if (typeof max !== "number" || !Number.isInteger(max) || max <= 0) {
      throw new Error("maxRuntime must be a positive integer (minutes)");
    }

    this.idleReleaseTimeout = idle;
    this.maxRuntime = max;
    this.manualRelease = false;
  }
}
