import * as sinon from "sinon";
import { ContextManager, SessionInterface } from "../../src/context-manager";
import { ContextSync } from "../../src/context-sync";
import { BetaContextMount } from "../../src/beta-context-mount";

describe("ContextManager.bind", () => {
  let contextManager: ContextManager;
  let mockSession: SessionInterface;
  let mockClient: any;
  let sandbox: sinon.SinonSandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockClient = {
      getContextInfo: sandbox.stub(),
      syncContext: sandbox.stub(),
      bindContexts: sandbox.stub(),
      describeSessionContexts: sandbox.stub(),
    };

    mockSession = {
      getAPIKey: sandbox.stub().returns("test-api-key"),
      getClient: sandbox.stub().returns(mockClient),
      getSessionId: sandbox.stub().returns("test-session-id"),
    };

    contextManager = new ContextManager(mockSession);
  });

  afterEach(() => {
    sandbox.restore();
  });

  it("should return error when no contexts provided", async () => {
    const result = await contextManager.bind([]);
    expect(result.success).toBe(false);
    expect(result.errorMessage).toContain("At least one context is required");
  });

  it("should call bindContexts API for a single ContextSync", async () => {
    mockClient.bindContexts.resolves({
      body: { requestId: "req-001", success: true },
      statusCode: 200,
    });

    mockClient.describeSessionContexts.resolves({
      body: {
        requestId: "req-list",
        success: true,
        data: [{ contextId: "ctx-123", path: "/tmp/test" }],
      },
    });

    const infoResponse = {
      body: {
        data: {
          contextStatus:
            '[{"type":"data","data":"[{\\"contextId\\":\\"ctx-123\\",\\"path\\":\\"/tmp/test\\",\\"errorMessage\\":\\"\\",\\"status\\":\\"Success\\",\\"startTime\\":0,\\"finishTime\\":0,\\"taskType\\":\\"download\\"}]"}]',
        },
        requestId: "req-info",
      },
      statusCode: 200,
    };
    mockClient.getContextInfo.resolves(infoResponse);

    const ctx = new ContextSync("ctx-123", "/tmp/test");
    const result = await contextManager.bind(ctx);

    expect(result.success).toBe(true);
    expect(mockClient.bindContexts.calledOnce).toBe(true);

    const callArg = mockClient.bindContexts.firstCall.args[0];
    expect(callArg.sessionId).toBe("test-session-id");
    expect(callArg.authorization).toBe("Bearer test-api-key");
    expect(callArg.persistenceDataList.length).toBe(1);
    expect(callArg.persistenceDataList[0].contextId).toBe("ctx-123");
  });

  it("should handle API failure", async () => {
    mockClient.bindContexts.resolves({
      body: {
        requestId: "req-003",
        success: false,
        code: "PathAlreadyBound",
        message: "Path /tmp/test is already bound",
      },
      statusCode: 200,
    });

    const ctx = new ContextSync("ctx-123", "/tmp/test");
    const result = await contextManager.bind(ctx);

    expect(result.success).toBe(false);
    expect(result.errorMessage).toContain("PathAlreadyBound");
    expect(result.errorMessage).toContain("already bound");
  });

  it("should not poll when waitForCompletion=false", async () => {
    mockClient.bindContexts.resolves({
      body: { requestId: "req-004", success: true },
      statusCode: 200,
    });

    const ctx = new ContextSync("ctx-123", "/tmp/test");
    const result = await contextManager.bind(ctx, false);

    expect(result.success).toBe(true);
    expect(mockClient.describeSessionContexts.called).toBe(false);
    expect(mockClient.getContextInfo.called).toBe(false);
  });
});

describe("ContextManager.bind download polling", () => {
  let contextManager: ContextManager;
  let mockSession: SessionInterface;
  let mockClient: any;
  let sandbox: sinon.SinonSandbox;

  beforeEach(() => {
    sandbox = sinon.createSandbox();

    mockClient = {
      getContextInfo: sandbox.stub(),
      syncContext: sandbox.stub(),
      bindContexts: sandbox.stub(),
      describeSessionContexts: sandbox.stub(),
    };

    mockSession = {
      getAPIKey: sandbox.stub().returns("test-api-key"),
      getClient: sandbox.stub().returns(mockClient),
      getSessionId: sandbox.stub().returns("test-session-id"),
    };

    contextManager = new ContextManager(mockSession);
  });

  afterEach(() => {
    sandbox.restore();
  });

  it("should poll info() until download completes", async () => {
    mockClient.bindContexts.resolves({
      body: { requestId: "req-005", success: true },
      statusCode: 200,
    });

    mockClient.describeSessionContexts.resolves({
      body: {
        requestId: "req-list",
        success: true,
        data: [{ contextId: "ctx-123", path: "/tmp/test" }],
      },
    });

    let infoCallCount = 0;
    mockClient.getContextInfo.callsFake(() => {
      infoCallCount++;
      const status = infoCallCount <= 2 ? "InProgress" : "Success";
      return Promise.resolve({
        body: {
          data: {
            contextStatus: `[{"type":"data","data":"[{\\"contextId\\":\\"ctx-123\\",\\"path\\":\\"/tmp/test\\",\\"errorMessage\\":\\"\\",\\"status\\":\\"${status}\\",\\"startTime\\":0,\\"finishTime\\":0,\\"taskType\\":\\"download\\"}]"}]`,
          },
          requestId: "req-info",
        },
        statusCode: 200,
      });
    });

    const ctx = new ContextSync("ctx-123", "/tmp/test");
    const result = await contextManager.bind(ctx, true);

    expect(result.success).toBe(true);
    expect(infoCallCount).toBeGreaterThanOrEqual(3);
  });

  it("should NOT poll info() for BetaContextMount", async () => {
    mockClient.bindContexts.resolves({
      body: { requestId: "req-006", success: true },
      statusCode: 200,
    });

    const ctx = new BetaContextMount("ctx-456", "/mnt/data");
    const result = await contextManager.bind(ctx, true);

    expect(result.success).toBe(true);
    expect(mockClient.getContextInfo.called).toBe(false);
    expect(mockClient.describeSessionContexts.called).toBe(false);
  });

  it("should return success even if download fails", async () => {
    mockClient.bindContexts.resolves({
      body: { requestId: "req-007", success: true },
      statusCode: 200,
    });

    mockClient.describeSessionContexts.resolves({
      body: {
        requestId: "req-list",
        success: true,
        data: [{ contextId: "ctx-123", path: "/tmp/test" }],
      },
    });

    mockClient.getContextInfo.resolves({
      body: {
        data: {
          contextStatus:
            '[{"type":"data","data":"[{\\"contextId\\":\\"ctx-123\\",\\"path\\":\\"/tmp/test\\",\\"errorMessage\\":\\"Download timeout\\",\\"status\\":\\"Failed\\",\\"startTime\\":0,\\"finishTime\\":0,\\"taskType\\":\\"download\\"}]"}]',
        },
        requestId: "req-info",
      },
      statusCode: 200,
    });

    const ctx = new ContextSync("ctx-123", "/tmp/test");
    const result = await contextManager.bind(ctx, true);

    expect(result.success).toBe(true);
  });
});
