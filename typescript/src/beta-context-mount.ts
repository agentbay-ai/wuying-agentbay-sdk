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
 */
export class BetaContextMount {
  contextId: string;
  path: string;
  accessMode: BetaContextMountAccessMode;
  strategy: BetaContextMountStrategy;

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
  }

  withAccessMode(accessMode: BetaContextMountAccessMode): BetaContextMount {
    this.accessMode = accessMode;
    return this;
  }

  withStrategy(strategy: BetaContextMountStrategy): BetaContextMount {
    this.strategy = strategy;
    return this;
  }

  toMountConfigJSON(): string {
    return JSON.stringify({
      accessMode: this.accessMode,
      storageMode: this.strategy,
    });
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
