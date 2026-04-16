import crypto from "crypto";
import type { WebSocket as WsType } from "./ws";
import { logDebug, logInfo, logWarn, maskSensitiveData } from "../utils/logger";
import { WsCancelledError } from "../exceptions";

// eslint-disable-next-line @typescript-eslint/no-var-requires
const WebSocketImpl: typeof WsType = require("ws");

export enum WsConnectionState {
  OPEN = "OPEN",
  CLOSED = "CLOSED",
  RECONNECTING = "RECONNECTING",
  ERROR = "ERROR",
}

type ConnectionStateListener = (
  state: WsConnectionState,
  reason: string
) => void;
type OnEvent = (invocationId: string, data: Record<string, any>) => void;
type OnEnd = (invocationId: string, data: Record<string, any>) => void;
type OnError = (invocationId: string, err: Error) => void;
type PushCallback = (payload: {
  requestId: string;
  target: string;
  data: Record<string, any>;
}) => void | Promise<void>;

function newInvocationId(): string {
  return crypto.randomBytes(16).toString("hex");
}

function safeStringify(obj: any): string {
  try {
    return JSON.stringify(obj);
  } catch (e) {
    return String(obj);
  }
}

function truncate(s: string, maxLen: number): string {
  if (s.length <= maxLen) return s;
  return s.slice(0, maxLen) + "...";
}

export class WsClient {
  private wsUrl: string;
  private token: string;
  private ws: any | null = null;
  private connecting: Promise<void> | null = null;
  private closedExplicitly = false;
  private callbacksByTarget = new Map<string, Set<PushCallback>>();
  private stateListeners: ConnectionStateListener[] = [];
  private state: WsConnectionState = WsConnectionState.CLOSED;
  private pendingById = new Map<
    string,
    {
      onEvent?: OnEvent;
      onEnd?: OnEnd;
      onError?: OnError;
      resolveEnd: (data: Record<string, any>) => void;
      rejectEnd: (err: Error) => void;
      isCall?: boolean;
    }
  >();

  private heartbeatIntervalMs: number;
  private heartbeatTimer: ReturnType<typeof setInterval> | null = null;
  private reconnectInitialDelayMs: number;
  private reconnectMaxDelayMs: number;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  private reconnecting = false;

  constructor(
    wsUrl: string,
    token: string,
    options?: {
      heartbeatIntervalMs?: number;
      reconnectInitialDelayMs?: number;
      reconnectMaxDelayMs?: number;
    }
  ) {
    this.wsUrl = wsUrl;
    this.token = token;
    this.heartbeatIntervalMs = options?.heartbeatIntervalMs ?? 20_000;
    this.reconnectInitialDelayMs = options?.reconnectInitialDelayMs ?? 500;
    this.reconnectMaxDelayMs = options?.reconnectMaxDelayMs ?? 5_000;
  }

  getState(): WsConnectionState {
    return this.state;
  }

  onConnectionStateChange(listener: ConnectionStateListener): () => void {
    this.stateListeners.push(listener);
    return () => {
      const idx = this.stateListeners.indexOf(listener);
      if (idx >= 0) this.stateListeners.splice(idx, 1);
    };
  }

  private setState(state: WsConnectionState, reason: string): void {
    this.state = state;
    for (const listener of [...this.stateListeners]) {
      try {
        listener(state, reason);
      } catch (_e) {
        logWarn("ConnectionState listener failed");
      }
    }
  }

  registerCallback(target: string, callback: PushCallback): () => void {
    if (!target || typeof target !== "string") {
      throw new Error("target must be a non-empty string");
    }
    if (typeof callback !== "function") {
      throw new Error("callback must be a function");
    }
    if (!this.callbacksByTarget.has(target)) {
      this.callbacksByTarget.set(target, new Set());
    }
    this.callbacksByTarget.get(target)?.add(callback);
    return () => this.unregisterCallback(target, callback);
  }

  unregisterCallback(target: string, callback?: PushCallback): void {
    if (!target || typeof target !== "string") {
      throw new Error("target must be a non-empty string");
    }
    if (!callback) {
      this.callbacksByTarget.delete(target);
      return;
    }
    const set = this.callbacksByTarget.get(target);
    if (!set) return;
    set.delete(callback);
    if (set.size === 0) {
      this.callbacksByTarget.delete(target);
    }
  }

  private logFrame(direction: ">>" | "<<", payload: any): void {
    const raw = safeStringify(payload);
    const masked = String(maskSensitiveData(raw));
    logDebug(`WS ${direction} ${truncate(masked, 1200)}`);
  }

  async connect(): Promise<void> {
    if (this.ws) return;
    if (this.connecting) return this.connecting;

    this.connecting = this.openConnection();
    return this.connecting;
  }

  private openConnection(): Promise<void> {
    this.setState(WsConnectionState.RECONNECTING, "connecting");
    logInfo(`WS CONNECT url=${this.wsUrl}`);

    return new Promise<void>((resolve, reject) => {
      const ws = new WebSocketImpl(this.wsUrl, {
        headers: {
          "X-Access-Token": this.token,
        },
      });

      ws.on("open", () => {
        this.ws = ws;
        this.connecting = null;
        this.reconnecting = false;
        this.setState(WsConnectionState.OPEN, "connected");
        this.startHeartbeat();
        resolve();
      });

      ws.on("message", (data: any) => {
        this.handleIncoming(data);
      });

      ws.on("error", (err: any) => {
        const e = err instanceof Error ? err : new Error(String(err));
        this.stopHeartbeat();
        this.failAllPending(e);
        this.ws = null;
        this.connecting = null;
        this.setState(WsConnectionState.ERROR, e.message);
        if (!this.reconnecting) {
          reject(e);
        }
        this.scheduleReconnect();
      });

      ws.on("close", () => {
        this.stopHeartbeat();
        this.failAllPending(new Error("WS connection closed"));
        this.ws = null;
        this.connecting = null;
        if (this.state === WsConnectionState.OPEN) {
          this.setState(WsConnectionState.CLOSED, "connection closed");
        }
        this.scheduleReconnect();
      });
    });
  }

  async close(): Promise<void> {
    this.closedExplicitly = true;
    this.stopHeartbeat();
    this.cancelReconnect();
    const ws = this.ws;
    this.ws = null;
    this.connecting = null;
    if (!ws) return;
    try {
      ws.close();
    } catch (_e) {
      return;
    }
    this.setState(WsConnectionState.CLOSED, "explicit close");
  }

  private startHeartbeat(): void {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      if (this.ws) {
        try {
          this.ws.ping();
        } catch (_e) {
          logWarn("Heartbeat ping failed");
        }
      }
    }, this.heartbeatIntervalMs);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  private cancelReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  private scheduleReconnect(): void {
    if (this.closedExplicitly) return;
    if (this.reconnecting) return;
    this.reconnecting = true;
    this.reconnectWithBackoff(this.reconnectInitialDelayMs);
  }

  private reconnectWithBackoff(delay: number): void {
    if (this.closedExplicitly) return;
    const jitter = delay * 0.5 * Math.random();
    const actualDelay = Math.min(delay + jitter, this.reconnectMaxDelayMs);
    logInfo(`WS reconnecting in ${Math.round(actualDelay)}ms`);
    this.setState(WsConnectionState.RECONNECTING, "reconnecting");

    this.reconnectTimer = setTimeout(async () => {
      this.reconnectTimer = null;
      if (this.closedExplicitly) return;
      try {
        this.connecting = this.openConnection();
        await this.connecting;
      } catch (_e) {
        const nextDelay = Math.min(delay * 2, this.reconnectMaxDelayMs);
        this.reconnectWithBackoff(nextDelay);
      }
    }, actualDelay);
  }

  /**
   * Send a message to the target without expecting a response.
   * Used for one-way notifications like browser callback messages.
   *
   * @param target - The target service identifier
   * @param data - The message data to send
   */
  async sendMessage(target: string, data: Record<string, any>): Promise<void> {
    await this.connect();
    const ws = this.ws;
    if (!ws) {
      throw new Error("WS is not connected");
    }

    const invocationId = newInvocationId();
    const payload = {
      invocationId,
      source: "SDK",
      target,
      data,
    };

    this.logFrame(">>", payload);
    ws.send(safeStringify(payload));
  }

  async callStream(params: {
    target: string;
    data: Record<string, any>;
    onEvent?: OnEvent;
    onEnd?: OnEnd;
    onError?: OnError;
  }): Promise<{
    invocationId: string;
    waitEnd: () => Promise<Record<string, any>>;
    cancel: () => Promise<void>;
    write: (data: Record<string, any>) => Promise<void>;
  }> {
    await this.connect();
    const ws = this.ws;
    if (!ws) {
      throw new Error("WS is not connected");
    }

    const invocationId = newInvocationId();
    const payload = {
      invocationId,
      source: "SDK",
      target: params.target,
      data: params.data,
    };

    const endPromise = new Promise<Record<string, any>>((resolve, reject) => {
      this.pendingById.set(invocationId, {
        onEvent: params.onEvent,
        onEnd: params.onEnd,
        onError: params.onError,
        resolveEnd: resolve,
        rejectEnd: reject,
      });
    });

    this.logFrame(">>", payload);
    ws.send(safeStringify(payload));

    const target = params.target;
    return {
      invocationId,
      waitEnd: async () => await endPromise,
      cancel: async () => {
        this.cancelPending(invocationId);
      },
      write: async (data: Record<string, any>) => {
        const ws = this.ws;
        if (!ws) throw new Error("WS not connected");
        const writePayload = {
          invocationId,
          source: "SDK",
          target,
          data,
        };
        this.logFrame(">>", writePayload);
        ws.send(safeStringify(writePayload));
      },
    };
  }

  /**
   * Send a request and wait for a single response (no phase semantics).
   * Used for PTY operations and other simple request-response patterns.
   */
  async call(
    target: string,
    data: Record<string, any>,
    timeoutMs = 30000
  ): Promise<Record<string, any>> {
    await this.connect();
    const ws = this.ws;
    if (!ws) {
      throw new Error("WS is not connected");
    }

    const invocationId = newInvocationId();
    const payload = {
      invocationId,
      source: "SDK",
      target,
      data,
    };

    const endPromise = new Promise<Record<string, any>>((resolve, reject) => {
      this.pendingById.set(invocationId, {
        resolveEnd: resolve,
        rejectEnd: reject,
        isCall: true,
      });

      setTimeout(() => {
        if (this.pendingById.has(invocationId)) {
          this.pendingById.delete(invocationId);
          reject(new Error(`call() timed out after ${timeoutMs}ms`));
        }
      }, timeoutMs);
    });

    this.logFrame(">>", payload);
    ws.send(safeStringify(payload));

    return endPromise;
  }

  private cancelPending(invocationId: string): void {
    const pending = this.pendingById.get(invocationId);
    if (!pending) return;
    const err = new WsCancelledError(
      `Stream ${invocationId} was cancelled by caller`
    );
    try {
      if (pending.onError) pending.onError(invocationId, err);
    } catch (_e) {}
    pending.rejectEnd(err);
    this.pendingById.delete(invocationId);
  }

  private handleIncoming(raw: any): void {
    const text = typeof raw === "string" ? raw : raw?.toString?.() ?? "";
    let msg: any;
    try {
      msg = JSON.parse(text);
    } catch (e) {
      this.failAllPending(new Error(`Invalid JSON message: ${e}`));
      return;
    }

    if (!msg || typeof msg !== "object") return;
    const invocationId = msg.invocationId || msg.requestId;
    if (!invocationId || typeof invocationId !== "string") return;

    const pending = this.pendingById.get(invocationId);
    const source = msg.source;
    const target = msg.target;
    const dataAny = msg.data;

    let data: Record<string, any> | null = null;
    if (dataAny && typeof dataAny === "object") {
      data = dataAny;
    } else if (typeof dataAny === "string") {
      try {
        const parsed = JSON.parse(dataAny);
        if (parsed && typeof parsed === "object") {
          logWarn(
            "WS protocol violation: backend sent data as string; decoded to object"
          );
          data = parsed;
        }
      } catch (_e) {
        data = null;
      }
    }

    if (!pending) {
      const routeTarget =
        target === "SDK" &&
        typeof source === "string" &&
        source &&
        source !== "SDK"
          ? source
          : target;
      if (!routeTarget || typeof routeTarget !== "string") return;
      if (!data) return;
      const callbacks = Array.from(
        this.callbacksByTarget.get(routeTarget) ?? []
      );
      if (callbacks.length === 0) return;
      const payload = { requestId: invocationId, target: routeTarget, data };
      for (const cb of callbacks) {
        try {
          const r = cb(payload);
          if (r && typeof (r as any).then === "function") {
            (r as Promise<void>).catch(() => undefined);
          }
        } catch (_e) {
          continue;
        }
      }
      return;
    }

    if (source === "WEBSOCKET_SERVER") {
      this.logFrame("<<", { invocationId, source, data });
      const errMsg =
        (typeof msg.error === "string" && msg.error) ||
        (data && typeof data === "object" && typeof data.error === "string"
          ? data.error
          : "");
      if (errMsg) {
        const err = new Error(errMsg);
        if (pending.onError) pending.onError(invocationId, err);
        pending.rejectEnd(err);
        this.pendingById.delete(invocationId);
        return;
      }
      const endData = data ?? {};
      if (pending.onEnd) pending.onEnd(invocationId, endData);
      pending.resolveEnd(endData);
      this.pendingById.delete(invocationId);
      return;
    }

    if (!data) return;

    this.logFrame("<<", { invocationId, source, target, data });

    if (typeof data.error === "string" && data.error) {
      const err = new Error(data.error);
      if (pending.onError) pending.onError(invocationId, err);
      pending.rejectEnd(err);
      this.pendingById.delete(invocationId);
      return;
    }

    if (pending.isCall) {
      if (pending.onEnd) pending.onEnd(invocationId, data);
      pending.resolveEnd(data);
      this.pendingById.delete(invocationId);
      return;
    }

    const phase = data.phase;
    if (phase === "event") {
      if (pending.onEvent) pending.onEvent(invocationId, data);
      return;
    }
    if (phase === "end") {
      if (pending.onEnd) pending.onEnd(invocationId, data);
      pending.resolveEnd(data);
      this.pendingById.delete(invocationId);
      return;
    }

    const err = new Error(`Unsupported phase: ${String(phase)}`);
    if (pending.onError) pending.onError(invocationId, err);
    pending.rejectEnd(err);
    this.pendingById.delete(invocationId);
  }

  private failAllPending(err: Error): void {
    for (const [invocationId, pending] of this.pendingById.entries()) {
      if (pending.onError) pending.onError(invocationId, err);
      pending.rejectEnd(err);
    }
    this.pendingById.clear();
  }
}
