export enum ContextMountAccessMode {
  ReadWrite = "readWrite",
  ReadOnly = "readOnly",
}

export enum ContextMountStrategy {
  Standard = "standard",
  Performance = "performance",
}

export class ContextMount {
  contextId: string;
  path: string;
  accessMode: ContextMountAccessMode;
  strategy: ContextMountStrategy;

  constructor(
    contextId: string,
    path: string,
    accessMode: ContextMountAccessMode = ContextMountAccessMode.ReadWrite,
    strategy: ContextMountStrategy = ContextMountStrategy.Standard
  ) {
    this.contextId = contextId;
    this.path = path;
    this.accessMode = accessMode;
    this.strategy = strategy;
  }

  withAccessMode(accessMode: ContextMountAccessMode): ContextMount {
    this.accessMode = accessMode;
    return this;
  }

  withStrategy(strategy: ContextMountStrategy): ContextMount {
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

export function newContextMount(
  contextId: string,
  path: string,
  accessMode?: ContextMountAccessMode,
  strategy?: ContextMountStrategy
): ContextMount {
  return new ContextMount(contextId, path, accessMode, strategy);
}
