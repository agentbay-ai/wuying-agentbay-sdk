export enum BetaContextMountAccessMode {
  ReadWrite = "readWrite",
  ReadOnly = "readOnly",
}

export enum BetaContextMountStrategy {
  Standard = "standard",
  Performance = "performance",
}

/**
 * [Beta] Represents a context mount configuration for direct-mount persistence.
 *
 * IMPORTANT: BetaContextMount requires `imageId: "aio-ubuntu-2404"` on the session.
 * Other images do not provide a real OSS-backed mount — writes are not persisted to
 * the shared context store and are invisible to other sessions even with the same
 * contextId and mount path.
 *
 * Use `withSourcePath()` to mount only a subdirectory of the context. The
 * subdirectory's contents are projected to the mount root.
 */
export class BetaContextMount {
  contextId: string;
  path: string;
  accessMode: BetaContextMountAccessMode;
  strategy: BetaContextMountStrategy;
  sourcePath: string;

  constructor(
    contextId: string,
    path: string,
    accessMode: BetaContextMountAccessMode = BetaContextMountAccessMode.ReadWrite,
    strategy: BetaContextMountStrategy = BetaContextMountStrategy.Standard
  ) {
    this.contextId = contextId;
    this.path = path;
    this.accessMode = accessMode;
    this.strategy = strategy;
    this.sourcePath = "";
  }

  withAccessMode(accessMode: BetaContextMountAccessMode): BetaContextMount {
    this.accessMode = accessMode;
    return this;
  }

  withStrategy(strategy: BetaContextMountStrategy): BetaContextMount {
    this.strategy = strategy;
    return this;
  }

  /**
   * Set the subpath within the context to mount. Empty string (default) mounts
   * the entire context. The selected subdirectory's contents are projected to
   * the mount root.
   */
  withSourcePath(sourcePath: string): BetaContextMount {
    this.sourcePath = sourcePath;
    return this;
  }
}

export function newBetaContextMount(
  contextId: string,
  path: string,
  accessMode?: BetaContextMountAccessMode,
  strategy?: BetaContextMountStrategy
): BetaContextMount {
  return new BetaContextMount(contextId, path, accessMode, strategy);
}
