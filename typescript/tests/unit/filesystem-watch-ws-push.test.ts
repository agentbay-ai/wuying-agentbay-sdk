import { FileSystem, FileChangeEvent } from "../../src/filesystem/filesystem";
import * as sinon from "sinon";

function makeMockController() {
  const ctrl: any = {
    signal: {
      aborted: false,
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
      onabort: null,
    } as any,
    abort: jest.fn(),
  };
  ctrl.abort.mockImplementation(() => {
    ctrl.signal.aborted = true;
    // Invoke all registered abort listeners
    for (const call of ctrl.signal.addEventListener.mock.calls) {
      if (call[0] === "abort" && typeof call[1] === "function") {
        try {
          call[1]();
        } catch (_e) {
          /* */
        }
      }
    }
  });
  return ctrl;
}

function makeMockSession(opts?: {
  wsUrl?: string;
  token?: string;
  serverName?: string | null;
}) {
  const sandbox = sinon.createSandbox();
  const session: any = {
    getAPIKey: sandbox.stub().returns("test-key"),
    getSessionId: sandbox.stub().returns("test-session"),
    callMcpTool: sandbox.stub().resolves({
      success: true,
      requestId: "r1",
      data: JSON.stringify([]),
      errorMessage: "",
    }),
    wsUrl: opts?.wsUrl ?? "wss://example.com/ws",
    token: opts?.token ?? "test-token",
    linkUrl: "",
    mcpTools: [],
    getMcpServerForTool: sandbox
      .stub()
      .returns(
        opts?.serverName === undefined ? "wuying_filesystem" : opts.serverName
      ),
    _isExpired: sandbox.stub().returns(false),
    getWsClient: sandbox.stub(),
  };
  return { session, sandbox };
}

function makeMockWsClient() {
  const registered: { target: string; callback: Function }[] = [];
  const stateListeners: Function[] = [];

  const ws: any = {
    registerCallback: jest.fn((target: string, cb: Function) => {
      registered.push({ target, callback: cb });
      return () => {
        const idx = registered.findIndex((r) => r.callback === cb);
        if (idx >= 0) registered.splice(idx, 1);
      };
    }),
    onConnectionStateChange: jest.fn((listener: Function) => {
      stateListeners.push(listener);
      return () => {
        const idx = stateListeners.indexOf(listener);
        if (idx >= 0) stateListeners.splice(idx, 1);
      };
    }),
    callStream: jest.fn().mockResolvedValue({
      invocationId: "inv-1",
      waitEnd: jest.fn().mockResolvedValue({ phase: "end" }),
      cancel: jest.fn(),
      write: jest.fn(),
    }),
    sendMessage: jest.fn().mockResolvedValue(undefined),
    connect: jest.fn().mockResolvedValue(undefined),
    _registered: registered,
    _stateListeners: stateListeners,
  };
  return ws;
}

describe("FileSystem watchDirectory WS Push Tests", () => {
  describe("Mode Selection", () => {
    it("should select WS push when all prerequisites met", () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      controller.abort();
      sandbox.restore();
    });

    it("should fall back to polling when no wsUrl", async () => {
      const { session, sandbox } = makeMockSession({ wsUrl: "" });
      const fs = new FileSystem(session);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        50,
        controller.signal
      );
      await ready;
      controller.abort();
      await monitoring;

      expect(session.getWsClient.called).toBe(false);
      sandbox.restore();
    });

    it("should fall back to polling when no server name", async () => {
      const { session, sandbox } = makeMockSession({ serverName: null });
      const fs = new FileSystem(session);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        50,
        controller.signal
      );
      await ready;
      controller.abort();
      await monitoring;

      expect(session.getWsClient.called).toBe(false);
      sandbox.restore();
    });
  });

  describe("Subscription", () => {
    it("should call subscribe_file_change via callStream", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/home/user/project",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));
      controller.abort();
      await monitoring;

      expect(mockWs.callStream).toHaveBeenCalled();
      const callArgs = mockWs.callStream.mock.calls[0][0];
      expect(callArgs.target).toBe("wuying_filesystem");
      expect(callArgs.data.method).toBe("subscribe_file_change");
      expect(callArgs.data.params.path).toBe("/home/user/project");
      sandbox.restore();
    });

    it("should register callback with server name", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));
      controller.abort();
      await monitoring;

      expect(mockWs.registerCallback).toHaveBeenCalled();
      const regArgs = mockWs.registerCallback.mock.calls[0];
      expect(regArgs[0]).toBe("wuying_filesystem");
      expect(typeof regArgs[1]).toBe("function");
      sandbox.restore();
    });

    it("should register connection state change listener", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));
      controller.abort();
      await monitoring;

      expect(mockWs.onConnectionStateChange).toHaveBeenCalled();
      const stateArgs = mockWs.onConnectionStateChange.mock.calls[0];
      expect(typeof stateArgs[0]).toBe("function");
      sandbox.restore();
    });
  });

  describe("Push Event Dispatch", () => {
    it("should dispatch push events to user callback", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const received: FileChangeEvent[] = [];
      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        (events) => received.push(...events),
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));

      const pushHandler = mockWs._registered[0]?.callback;
      expect(pushHandler).toBeDefined();

      pushHandler({
        data: {
          eventType: "file_change",
          path: "/watch",
          events: [
            { eventType: "create", path: "/watch/new.txt", pathType: "file" },
            { eventType: "modify", path: "/watch/old.py", pathType: "file" },
          ],
        },
      });

      expect(received).toHaveLength(2);
      expect(received[0].eventType).toBe("create");
      expect(received[0].path).toBe("/watch/new.txt");
      expect(received[1].eventType).toBe("modify");

      controller.abort();
      await monitoring;
      sandbox.restore();
    });

    it("should ignore push events for different path", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const received: FileChangeEvent[] = [];
      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        (events) => received.push(...events),
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));

      const pushHandler = mockWs._registered[0]?.callback;
      pushHandler({
        data: {
          eventType: "file_change",
          path: "/other",
          events: [
            { eventType: "create", path: "/other/x.txt", pathType: "file" },
          ],
        },
      });

      expect(received).toHaveLength(0);

      controller.abort();
      await monitoring;
      sandbox.restore();
    });

    it("should ignore push events with wrong eventType", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const received: FileChangeEvent[] = [];
      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        (events) => received.push(...events),
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));

      const pushHandler = mockWs._registered[0]?.callback;
      pushHandler({
        data: {
          eventType: "other_type",
          path: "/watch",
          events: [
            { eventType: "create", path: "/watch/x.txt", pathType: "file" },
          ],
        },
      });

      expect(received).toHaveLength(0);

      controller.abort();
      await monitoring;
      sandbox.restore();
    });
  });

  describe("Unsubscribe on Stop", () => {
    it("should send unsubscribe_file_change on stop", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));
      controller.abort();
      await monitoring;

      expect(mockWs.sendMessage).toHaveBeenCalledWith("wuying_filesystem", {
        method: "unsubscribe_file_change",
        params: { path: "/watch" },
      });
      sandbox.restore();
    });

    it("should unregister push callback on stop", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));

      expect(mockWs._registered).toHaveLength(1);

      controller.abort();
      await monitoring;

      expect(mockWs._registered).toHaveLength(0);
      sandbox.restore();
    });

    it("should unregister state listener on stop", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      session.getWsClient.resolves(mockWs);

      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        () => {},
        500,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));

      expect(mockWs._stateListeners).toHaveLength(1);

      controller.abort();
      await monitoring;

      expect(mockWs._stateListeners).toHaveLength(0);
      sandbox.restore();
    });
  });

  describe("Fallback to Polling", () => {
    it("should fall back to polling when subscribe fails", async () => {
      const { session, sandbox } = makeMockSession();
      const fs = new FileSystem(session);
      const mockWs = makeMockWsClient();
      mockWs.callStream.mockRejectedValue(new Error("subscribe failed"));
      session.getWsClient.resolves(mockWs);

      let pollCount = 0;
      session.callMcpTool.callsFake(() => {
        pollCount++;
        if (pollCount > 3) {
          return Promise.resolve({
            success: true,
            requestId: "r",
            data: JSON.stringify([
              { eventType: "create", path: "/watch/new.txt", pathType: "file" },
            ]),
            errorMessage: "",
          });
        }
        return Promise.resolve({
          success: true,
          requestId: "r",
          data: JSON.stringify([]),
          errorMessage: "",
        });
      });

      const received: FileChangeEvent[] = [];
      const controller = makeMockController();
      const { monitoring, ready } = fs.watchDirectory(
        "/watch",
        (events) => received.push(...events),
        50,
        controller.signal
      );
      await ready;
      await new Promise((r) => setTimeout(r, 500));
      controller.abort();
      await monitoring;

      expect(pollCount).toBeGreaterThan(3);
      expect(received.length).toBeGreaterThan(0);
      sandbox.restore();
    });
  });
});
