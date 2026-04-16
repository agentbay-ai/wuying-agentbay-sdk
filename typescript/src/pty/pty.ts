/**
 * PTY (Pseudo Terminal) module for interactive terminal sessions
 * in cloud sandbox environments.
 */

import type { WsClient } from "../_internal/ws-client";

const PTY_TARGET = "PTY_SERVER";

const DEFAULT_ENVS: Record<string, string> = {
  TERM: "xterm-256color",
  LANG: "en_US.UTF-8",
};

const MAX_TERMINAL_SIZE = 500;

export interface PtySession {
  ptySessionId: string;
  cols: number;
  rows: number;
  status: string;
  exitCode?: number;
}

export interface PtyCreateOptions {
  cols?: number;
  rows?: number;
  cwd?: string;
  envs?: Record<string, string>;
  shell?: string;
  onData?: (data: Uint8Array) => void;
  timeoutMs?: number;
}

export class PtyError extends Error {
  constructor(message = "PTY operation error") {
    super(message);
    this.name = "PtyError";
  }
}

export class PtyNotConnectedError extends PtyError {
  constructor(message = "PTY handle is not connected") {
    super(message);
    this.name = "PtyNotConnectedError";
  }
}

export class PtyHandle {
  private _ptySessionId: string;
  private _ptyModule: Pty;
  private _onData?: (data: Uint8Array) => void;
  private _connected = true;
  private _exitCode: number | undefined = undefined;
  private _errorMsg: string | undefined = undefined;

  constructor(
    ptySessionId: string,
    ptyModule: Pty,
    onData?: (data: Uint8Array) => void
  ) {
    this._ptySessionId = ptySessionId;
    this._ptyModule = ptyModule;
    this._onData = onData;
  }

  get ptySessionId(): string {
    return this._ptySessionId;
  }

  get isConnected(): boolean {
    return this._connected;
  }

  get exitCode(): number | undefined {
    return this._exitCode;
  }

  async sendInput(data: Uint8Array): Promise<void> {
    if (!this._connected) throw new PtyNotConnectedError();
    let text: string;
    let encoding: string;
    try {
      text = new TextDecoder("utf-8", { fatal: true }).decode(data);
      encoding = "utf8";
    } catch {
      text = Buffer.from(data).toString("base64");
      encoding = "base64";
    }
    const wsClient = await this._ptyModule.getWsClient();
    await wsClient.sendMessage(PTY_TARGET, {
      method: "pty.input",
      params: {
        ptySessionId: this._ptySessionId,
        encoding,
        data: text,
      },
    });
  }

  async resize(cols: number, rows: number): Promise<void> {
    if (!this._connected) throw new PtyNotConnectedError();
    if (cols < 1 || cols > MAX_TERMINAL_SIZE || rows < 1 || rows > MAX_TERMINAL_SIZE) {
      throw new PtyError(
        `Invalid terminal size: cols=${cols}, rows=${rows} (must be 1-${MAX_TERMINAL_SIZE})`
      );
    }
    const wsClient = await this._ptyModule.getWsClient();
    await wsClient.sendMessage(PTY_TARGET, {
      method: "pty.resize",
      params: {
        ptySessionId: this._ptySessionId,
        cols,
        rows,
      },
    });
  }

  async kill(): Promise<void> {
    if (!this._connected) throw new PtyNotConnectedError();
    const wsClient = await this._ptyModule.getWsClient();
    await wsClient.call(PTY_TARGET, {
      method: "pty.kill",
      params: { ptySessionId: this._ptySessionId },
    });
  }

  async wait(timeoutMs?: number): Promise<number> {
    const deadline = timeoutMs ? Date.now() + timeoutMs : undefined;
    while (this._exitCode === undefined && this._errorMsg === undefined) {
      if (deadline !== undefined && Date.now() >= deadline) {
        throw new PtyError(`PTY wait timed out after ${timeoutMs}ms`);
      }
      await new Promise((r) => setTimeout(r, 100));
    }
    if (this._errorMsg !== undefined) {
      throw new PtyError(this._errorMsg);
    }
    return this._exitCode!;
  }

  disconnect(): void {
    if (!this._connected) return;
    this._connected = false;
    this._ptyModule.unregisterHandle(this._ptySessionId);
  }

  /** @internal */
  _handleOutput(dataBytes: Uint8Array): void {
    if (this._onData) {
      try {
        this._onData(dataBytes);
      } catch (e) {
        console.error("on_data callback raised an exception", e);
      }
    }
  }

  /** @internal */
  _handleExit(exitCode: number): void {
    this._exitCode = exitCode;
    this._connected = false;
  }

  /** @internal */
  _handleError(errorMsg: string): void {
    this._errorMsg = errorMsg;
    this._connected = false;
  }
}

export class Pty {
  private session: any;
  private wsClient: WsClient | null = null;
  private handles = new Map<string, PtyHandle>();
  private callbackRegistered = false;

  constructor(session: any) {
    this.session = session;
  }

  /** @internal */
  async getWsClient(): Promise<WsClient> {
    if (!this.wsClient) {
      this.wsClient = await this.session.getWsClient();
    }
    return this.wsClient!;
  }

  private async ensureCallback(): Promise<void> {
    if (this.callbackRegistered) return;
    const wsClient = await this.getWsClient();
    await wsClient.connect();
    wsClient.registerCallback(PTY_TARGET, (payload) => {
      this.pushCallback(payload);
    });
    this.callbackRegistered = true;
  }

  private pushCallback(payload: {
    requestId: string;
    target: string;
    data: Record<string, any>;
  }): void {
    const data = payload.data ?? {};
    const eventType = data.eventType ?? "";
    const ptySessionId = data.ptySessionId ?? "";

    if (eventType === "pty.output") {
      const handle = this.handles.get(ptySessionId);
      if (!handle) return;
      const encoding = data.encoding ?? "utf8";
      const raw = data.data ?? "";
      let dataBytes: Uint8Array;
      if (encoding === "base64") {
        dataBytes = Buffer.from(raw, "base64");
      } else {
        dataBytes =
          typeof raw === "string"
            ? new TextEncoder().encode(raw)
            : new Uint8Array(raw);
      }
      handle._handleOutput(dataBytes);
    } else if (eventType === "pty.exit") {
      const handle = this.handles.get(ptySessionId);
      if (!handle) return;
      const exitCode = typeof data.exitCode === "number" ? data.exitCode : -1;
      handle._handleExit(exitCode);
    } else if (eventType === "pty.error") {
      const handle = this.handles.get(ptySessionId);
      if (!handle) return;
      const errorMsg =
        typeof data.error === "string" ? data.error : "Unknown PTY error";
      handle._handleError(errorMsg);
    }
  }

  /** @internal */
  unregisterHandle(ptySessionId: string): void {
    this.handles.delete(ptySessionId);
  }

  async create(options: PtyCreateOptions = {}): Promise<PtyHandle> {
    const cols = options.cols ?? 80;
    const rows = options.rows ?? 24;

    if (cols < 1 || cols > MAX_TERMINAL_SIZE || rows < 1 || rows > MAX_TERMINAL_SIZE) {
      throw new PtyError(
        `Invalid terminal size: cols=${cols}, rows=${rows} (must be 1-${MAX_TERMINAL_SIZE})`
      );
    }

    await this.ensureCallback();
    const wsClient = await this.getWsClient();

    const params: Record<string, any> = { cols, rows };
    if (options.cwd !== undefined) params.cwd = options.cwd;
    const mergedEnvs = { ...DEFAULT_ENVS, ...(options.envs ?? {}) };
    params.envs = mergedEnvs;
    if (options.shell !== undefined) params.shell = options.shell;

    const timeoutMs = options.timeoutMs ?? 30000;
    const response = await wsClient.call(
      PTY_TARGET,
      { method: "pty.create", params },
      timeoutMs
    );

    const result = (response.result as Record<string, any>) ?? {};
    const ptySessionId = result.ptySessionId as string;
    if (!ptySessionId) {
      throw new PtyError(
        `pty.create did not return ptySessionId: ${JSON.stringify(response)}`
      );
    }

    const handle = new PtyHandle(ptySessionId, this, options.onData);
    this.handles.set(ptySessionId, handle);
    return handle;
  }

  async list(): Promise<PtySession[]> {
    await this.ensureCallback();
    const wsClient = await this.getWsClient();

    const response = await wsClient.call(PTY_TARGET, {
      method: "pty.list",
      params: {},
    });

    const result = (response.result as Record<string, any>) ?? {};
    const ptySessionIds = (result.ptySessionIds as string[]) ?? [];
    const sessions: PtySession[] = [];
    for (const sid of ptySessionIds) {
      const handle = this.handles.get(sid);
      let status = "running";
      let exitCode: number | undefined;
      if (handle && handle.exitCode !== undefined) {
        status = "exited";
        exitCode = handle.exitCode;
      }
      sessions.push({
        ptySessionId: sid,
        cols: 0,
        rows: 0,
        status,
        exitCode,
      });
    }
    return sessions;
  }

  async connect(
    ptySessionId: string,
    onData?: (data: Uint8Array) => void
  ): Promise<PtyHandle> {
    await this.ensureCallback();
    const wsClient = await this.getWsClient();

    const response = await wsClient.call(PTY_TARGET, {
      method: "pty.connect",
      params: { ptySessionId },
    });

    const result = (response.result as Record<string, any>) ?? {};
    const returnedId = (result.ptySessionId as string) || ptySessionId;

    const handle = new PtyHandle(returnedId, this, onData);
    this.handles.set(returnedId, handle);
    return handle;
  }

  async kill(ptySessionId: string): Promise<void> {
    await this.ensureCallback();
    const wsClient = await this.getWsClient();

    await wsClient.call(PTY_TARGET, {
      method: "pty.kill",
      params: { ptySessionId },
    });

    const handle = this.handles.get(ptySessionId);
    if (handle) {
      (handle as any)._connected = false;
      this.handles.delete(ptySessionId);
    }
  }
}
