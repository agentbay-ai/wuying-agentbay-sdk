import {
  AgentBay,
  Session,
  AuthenticationError,
  APIError,
  ListSessionParams,
  LifecyclePolicy,
} from "../../src";
import { log } from "../../src/utils/logger";
import * as sinon from "sinon";

// Define Node.js process if it's not available
declare namespace NodeJS {
  interface ProcessEnv {
    [key: string]: string | undefined;
  }
}

declare var process: {
  env: {
    [key: string]: string | undefined;
  };
};

// Mock data for tests
const mockSessionData = {
  sessionId: "mock-session-123",
  resourceUrl: "mock-resource-url",
};

const mockSessionAData = {
  sessionId: "mock-session-a-456",
  resourceUrl: "mock-resource-url-a",
};

const mockSessionBData = {
  sessionId: "mock-session-b-789",
  resourceUrl: "mock-resource-url-b",
};

// Mock config data
const mockConfigData = {
  region_id: "cn-hangzhou",
  endpoint: "agentbay.cn-hangzhou.aliyuncs.com",
  timeout_ms: 30000,
};

describe("AgentBay", () => {
  let mockClient: any;
  let createMcpSessionStub: sinon.SinonStub;
  let listSessionStub: sinon.SinonStub;
  let deleteSessionAsyncStub: sinon.SinonStub;
  let getSessionStub: sinon.SinonStub;
  let getSessionDetailStub: sinon.SinonStub;
  let clientConstructorStub: sinon.SinonStub;
  let contextServiceConstructorStub: sinon.SinonStub;
  let contextStatusEntries: any[];

  beforeEach(() => {
    // Create mock client
    mockClient = {
      createMcpSession: sinon.stub(),
      listSession: sinon.stub(),
      deleteSessionAsync: sinon.stub(),
      getSession: sinon.stub(),
      getSessionDetail: sinon.stub(),
      getContextInfo: sinon.stub(),
    };

    // Get references to stubs for easier access
    createMcpSessionStub = mockClient.createMcpSession;
    listSessionStub = mockClient.listSession;
    deleteSessionAsyncStub = mockClient.deleteSessionAsync;
    getSessionStub = mockClient.getSession;
    getSessionDetailStub = mockClient.getSessionDetail;

    // Mock getContextInfo used by ContextManager.info().
    // In unit tests, we should not actually wait. We return "Success" statuses immediately
    // when a test sets contextStatusEntries to include the expected context IDs.
    contextStatusEntries = [];
    mockClient.getContextInfo.callsFake(async () => {
      return {
        statusCode: 200,
        body: {
          success: true,
          data: {
            contextStatus: JSON.stringify([
              {
                type: "data",
                data: JSON.stringify(contextStatusEntries),
              },
            ]),
          },
          requestId: "mock-request-id-context-info",
        },
      };
    });

    // Set environment variables for config instead of stubbing loadConfig
    process.env.AGENTBAY_REGION_ID = mockConfigData.region_id;
    process.env.AGENTBAY_TIMEOUT_MS = String(mockConfigData.timeout_ms);

    // Mock Client constructor
    clientConstructorStub = sinon.stub().returns(mockClient);
    sinon
      .stub(require("../../src/api/client"), "Client")
      .callsFake(clientConstructorStub);

    // Mock ContextService constructor
    const mockContextService = {
      get: sinon.stub().resolves({
        success: false,
        errorMessage: "Context not found",
      }),
    };
    contextServiceConstructorStub = sinon.stub().returns(mockContextService);
    sinon
      .stub(require("../../src/context"), "ContextService")
      .callsFake(contextServiceConstructorStub);

    // Mock AgentBay's getClient method to return our mock client
    sinon.stub(AgentBay.prototype, "getClient").returns(mockClient);

    // getAPIKey is now private, no need to mock it

    log("Mock client setup complete");
  });

  afterEach(() => {
    sinon.restore();
  });

  describe("constructor", () => {
    it("should initialize with API key from options", () => {
      const apiKey = "test-api-key";
      const agentBay = new AgentBay({ apiKey });
      log(apiKey);

      expect(agentBay.getAPIKey()).toBe(apiKey);

      // loadConfig is now internal, no need to verify

      // Verify that Client was constructed with correct config
      expect(clientConstructorStub.calledOnce).toBe(true);
      const clientConfig = clientConstructorStub.getCall(0).args[0];
      // Note: OpenAPI client's regionId is hardcoded to "" by design — region info
      // is passed per-request via LoginRegionId, not via the client constructor.
      expect(clientConfig.regionId).toBe("");
      expect(clientConfig.endpoint).toBe(mockConfigData.endpoint);
      expect(clientConfig.readTimeout).toBe(mockConfigData.timeout_ms);
      expect(clientConfig.connectTimeout).toBe(mockConfigData.timeout_ms);

      // Verify that ContextService was constructed
      expect(contextServiceConstructorStub.calledOnce).toBe(true);
    });

    it("should initialize with API key from environment variable", () => {
      const originalEnv = process.env.AGENTBAY_API_KEY;
      process.env.AGENTBAY_API_KEY = "env_api_key";

      try {
        const agentBay = new AgentBay();
        expect(agentBay.getAPIKey()).toBe("env_api_key");

        // Verify dependencies were called
        expect(clientConstructorStub.called).toBe(true);
        expect(contextServiceConstructorStub.called).toBe(true);
      } finally {
        // Restore original environment
        if (originalEnv) {
          process.env.AGENTBAY_API_KEY = originalEnv;
        } else {
          delete process.env.AGENTBAY_API_KEY;
        }
      }
    });

    it("should throw AuthenticationError if no API key is provided", () => {
      const originalEnv = process.env.AGENTBAY_API_KEY;
      delete process.env.AGENTBAY_API_KEY;

      try {
        expect(() => new AgentBay()).toThrow(AuthenticationError);
      } finally {
        // Restore original environment
        if (originalEnv) {
          process.env.AGENTBAY_API_KEY = originalEnv;
        }
      }
    });
  });

  describe("create, list, and delete", () => {
    let agentBay: AgentBay;
    let session: Session;

    beforeEach(() => {
      const apiKey = "test-api-key";
      agentBay = new AgentBay({ apiKey });
    });

    it("should create, list, and delete a session with requestId", async () => {
      // Setup mock response for create session
      const createMockResponse = {
        statusCode: 200,
        body: {
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };

      // Setup mock response for delete session
      const deleteMockResponse = {
        statusCode: 200,
        body: {
          requestId: "mock-request-id-delete",
          success: true,
        },
      };

      createMcpSessionStub.resolves(createMockResponse);
      deleteSessionAsyncStub.resolves(deleteMockResponse);

      // Mock GetSessionDetail to return NotFound error (indicating session is deleted)
      getSessionDetailStub.resolves({
        statusCode: 400,
        body: {
          requestId: "get-session-detail-request-id",
          code: "InvalidMcpSession.NotFound",
          message: "Session not found",
          success: false,
          httpStatusCode: 400,
        },
      });

      // Verify mock setup before test
      log("Verifying mock setup...");
      expect(createMcpSessionStub).toBeDefined();
      expect(deleteSessionAsyncStub).toBeDefined();
      expect(typeof createMcpSessionStub.resolves).toBe("function");

      // Create a session
      log("Creating a new session...");
      const createResponse = await agentBay.create({});
      session = createResponse.session!; // Use session field instead of data
      log(`Session created with ID: ${session?.sessionId || "undefined"}`);
      log(
        `Create Session RequestId: ${createResponse.requestId || "undefined"}`
      );

      // Verify that the mock was called
      expect(createMcpSessionStub.called).toBe(true);
      log(`createMcpSessionStub called: ${createMcpSessionStub.called}`);
      log(`createMcpSessionStub callCount: ${createMcpSessionStub.callCount}`);

      // Verify that the response contains requestId and success
      expect(createResponse.requestId).toBeDefined();
      expect(typeof createResponse.requestId).toBe("string");
      expect(createResponse.requestId).toBe("mock-request-id-create");
      expect(createResponse.success).toBe(true);
      expect(createResponse.session).toBeDefined();

      // Ensure session ID matches mock data
      expect(session.sessionId).toBe(mockSessionData.sessionId);

      // Client is now private, cannot verify directly
      // The session should work correctly if properly initialized

      // Delete the session
      log("Deleting the session...");
      const deleteResponse = await agentBay.delete(session);
      log(
        `Delete Session RequestId: ${deleteResponse.requestId || "undefined"}`
      );

      // Verify that the delete mock was called
      expect(deleteSessionAsyncStub.called).toBe(true);
      log(`deleteSessionAsyncStub called: ${deleteSessionAsyncStub.called}`);
      log(
        `deleteSessionAsyncStub callCount: ${deleteSessionAsyncStub.callCount}`
      );

      // Verify that the delete response contains requestId and success
      expect(deleteResponse.requestId).toBeDefined();
      expect(typeof deleteResponse.requestId).toBe("string");
      expect(deleteResponse.requestId).toBe("mock-request-id-delete");
      expect(deleteResponse.success).toBe(true);

      // Session deletion completed

      // Verify API calls were made with correct parameters
      expect(createMcpSessionStub.calledOnce).toBe(true);
      expect(deleteSessionAsyncStub.calledOnce).toBe(true);

      const createCallArgs = createMcpSessionStub.getCall(0).args[0];
      expect(createCallArgs.authorization).toBe("Bearer test-api-key");
      expect((createCallArgs as any).timeout).toBeUndefined();

      const deleteCallArgs = deleteSessionAsyncStub.getCall(0).args[0];
      expect(deleteCallArgs.sessionId).toBe(mockSessionData.sessionId);
      expect(deleteCallArgs.authorization).toBe("Bearer test-api-key");

      log("All mock verifications passed successfully");
    });
  });

  describe("list", () => {
    let agentBay: AgentBay;

    beforeEach(() => {
      const apiKey = "test-api-key";
      agentBay = new AgentBay({ apiKey });
    });

    it("should list all sessions without labels", async () => {
      const mockResponse = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData, mockSessionBData, mockSessionData],
          maxResults: 10,
          totalCount: 3,
          requestId: "mock-request-id-list-all",
        },
      };

      listSessionStub.resolves(mockResponse);

      const result = await agentBay.list();

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("mock-request-id-list-all");
      expect(result.sessionIds.length).toBe(3);
      expect(result.totalCount).toBe(3);
    });

    it("should list sessions with specific labels", async () => {
      const mockResponse = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData],
          maxResults: 10,
          totalCount: 1,
          requestId: "mock-request-id-list-labeled",
        },
      };

      listSessionStub.resolves(mockResponse);

      const result = await agentBay.list({ env: "prod" });

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("mock-request-id-list-labeled");
      expect(result.sessionIds.length).toBe(1);
      expect(listSessionStub.calledOnce).toBe(true);
      const callArgs = listSessionStub.getCall(0).args[0];
      expect(JSON.parse(callArgs.labels)).toEqual({ env: "prod" });
    });

    it("should list sessions with pagination", async () => {
      // First page response
      const mockResponsePage1 = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData, mockSessionBData],
          maxResults: 2,
          totalCount: 4,
          nextToken: "token-page2",
          requestId: "mock-request-id-page1",
        },
      };

      // Second page response
      const mockResponsePage2 = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionData],
          maxResults: 2,
          totalCount: 4,
          nextToken: "",
          requestId: "mock-request-id-page2",
        },
      };

      listSessionStub.onFirstCall().resolves(mockResponsePage1);
      listSessionStub.onSecondCall().resolves(mockResponsePage2);

      // Request page 2
      const result = await agentBay.list({ env: "prod" }, 2, 2);

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("mock-request-id-page2");
      expect(result.sessionIds.length).toBe(1);
      expect(result.sessionIds[0].sessionId).toBe(mockSessionData.sessionId);
      expect(listSessionStub.calledTwice).toBe(true);
    });

    it("should use default limit of 10 when not specified", async () => {
      const mockResponse = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData],
          maxResults: 10,
          totalCount: 1,
          requestId: "mock-request-id",
        },
      };

      listSessionStub.resolves(mockResponse);

      await agentBay.list();

      const callArgs = listSessionStub.getCall(0).args[0];
      expect(callArgs.maxResults).toBe(10);
    });

    it("should list sessions with specific status", async () => {
      const mockResponse = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData],
          maxResults: 10,
          totalCount: 1,
          requestId: "mock-request-id-list-status",
        },
      };

      listSessionStub.resolves(mockResponse);

      const result = await agentBay.list({}, undefined, 10, "RUNNING");

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("mock-request-id-list-status");
      expect(result.sessionIds.length).toBe(1);
      expect(listSessionStub.calledOnce).toBe(true);
      const callArgs = listSessionStub.getCall(0).args[0];
      expect(callArgs.status).toBe("RUNNING");
    });

    it("should return error for invalid status", async () => {
      const result = await agentBay.list({}, undefined, 10, "INVALID_STATUS");

      expect(result.success).toBe(false);
      expect(result.errorMessage).toContain("Invalid status 'INVALID_STATUS'");
      expect(result.sessionIds.length).toBe(0);
      expect(listSessionStub.called).toBe(false);
    });

    it("should list sessions with labels and status", async () => {
      const mockResponse = {
        statusCode: 200,
        body: {
          success: true,
          data: [mockSessionAData],
          maxResults: 10,
          totalCount: 1,
          requestId: "mock-request-id-list-labels-status",
        },
      };

      listSessionStub.resolves(mockResponse);

      const result = await agentBay.list(
        { env: "prod" },
        undefined,
        10,
        "PAUSED"
      );

      expect(result.success).toBe(true);
      expect(result.requestId).toBe("mock-request-id-list-labels-status");
      expect(result.sessionIds.length).toBe(1);
      expect(listSessionStub.calledOnce).toBe(true);
      const callArgs = listSessionStub.getCall(0).args[0];
      expect(JSON.parse(callArgs.labels)).toEqual({ env: "prod" });
      expect(callArgs.status).toBe("PAUSED");
    });
  });

  describe("policyId passthrough", () => {
    it("should pass policyId to CreateMcpSession request body", async () => {
      const apiKey = "test-api-key";
      const agentBay = new AgentBay({ apiKey });

      const createMockResponse = {
        statusCode: 200,
        body: {
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      const policyId = "policy-xyz";
      await agentBay.create({ policyId });

      expect(createMcpSessionStub.calledOnce).toBe(true);
      const createCallArgs = createMcpSessionStub.getCall(0).args[0];
      expect(createCallArgs.mcpPolicyId).toBe(policyId);
      expect((createCallArgs as any).timeout).toBeUndefined();
    });
  });

  describe("idleReleaseTimeout passthrough", () => {
    it("should pass idleReleaseTimeout to CreateMcpSession request body", async () => {
      const apiKey = "test-api-key";
      const agentBay = new AgentBay({ apiKey });

      const createMockResponse = {
        statusCode: 200,
        body: {
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      await agentBay.create({ idleReleaseTimeout: 123 });

      expect(createMcpSessionStub.calledOnce).toBe(true);
      const createCallArgs = createMcpSessionStub.getCall(0).args[0];
      expect((createCallArgs as any).timeout).toBe(123);
    });
  });

  describe("lifecyclePolicy passthrough", () => {
    it("should pass lifecyclePolicy fields to CreateMcpSession request body", async () => {
      const apiKey = "test-api-key";
      const agentBay = new AgentBay({ apiKey });

      const createMockResponse = {
        statusCode: 200,
        body: {
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      const lp = new LifecyclePolicy({
        idleReleaseTimeout: 10,
        maxRuntime: 120,
      });
      await agentBay.create({ lifecyclePolicy: lp });

      expect(createMcpSessionStub.calledOnce).toBe(true);
      const createCallArgs = createMcpSessionStub.getCall(0).args[0];
      expect((createCallArgs as any).timeout).toBe(10);
      expect((createCallArgs as any).maxRuntime).toBe(120);
      expect((createCallArgs as any).manualRelease).toBeUndefined();
    });

    it("should pass manual release lifecyclePolicy to CreateMcpSession request body", async () => {
      const apiKey = "test-api-key";
      const agentBay = new AgentBay({ apiKey });

      const createMockResponse = {
        statusCode: 200,
        body: {
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      const lp = new LifecyclePolicy({ manualRelease: true });
      await agentBay.create({ lifecyclePolicy: lp });

      expect(createMcpSessionStub.calledOnce).toBe(true);
      const createCallArgs = createMcpSessionStub.getCall(0).args[0];
      expect((createCallArgs as any).timeout).toBeUndefined();
      expect((createCallArgs as any).maxRuntime).toBeUndefined();
      expect((createCallArgs as any).manualRelease).toBe(true);
    });
  });

  describe("create does not modify params", () => {
    let agentBay: AgentBay;

    beforeEach(() => {
      const apiKey = "test-api-key";
      agentBay = new AgentBay({ apiKey });
    });

    it("should not modify original params object when creating session with contextSync", async () => {
      const createMockResponse = {
        body: {
          success: true,
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      const { ContextSync } = require("../../src/context-sync");
      const originalContextSyncs = [
        new ContextSync("ctx-1", "/path1"),
        new ContextSync("ctx-2", "/path2"),
      ];
      const params: any = {
        labels: { env: "test" },
        contextSync: originalContextSyncs,
      };

      // Store original values
      const originalLabels = { ...params.labels };
      const originalContextSyncsList = [...params.contextSync];
      const originalLabelsRef = params.labels;
      const originalContextSyncsRef = params.contextSync;

      // Make the first GetContextInfo call report all contexts as completed.
      contextStatusEntries = originalContextSyncs.map((cs: any) => {
        return {
          contextId: cs.contextId,
          path: cs.path,
          errorMessage: "",
          status: "Success",
          startTime: 0,
          finishTime: 0,
          taskType: "download",
        };
      });

      await agentBay.create(params);

      // Ensure we didn't sleep/retry: create() should break on the first status check.
      expect(mockClient.getContextInfo.calledOnce).toBe(true);

      // Verify the original params object was not modified
      expect(params.labels).toEqual(originalLabels);
      expect(params.labels).toBe(originalLabelsRef); // Should be the same object reference
      expect(params.contextSync).toBe(originalContextSyncsRef); // Should be the same array reference
      expect(params.contextSync.length).toBe(originalContextSyncsList.length);
      for (let i = 0; i < originalContextSyncsList.length; i++) {
        expect(params.contextSync[i].contextId).toBe(
          originalContextSyncsList[i].contextId
        );
        expect(params.contextSync[i].path).toBe(
          originalContextSyncsList[i].path
        );
      }
    });

    it("should not modify original params object when creating session with mobile simulate config", async () => {
      const createMockResponse = {
        body: {
          success: true,
          data: mockSessionData,
          requestId: "mock-request-id-create",
        },
      };
      createMcpSessionStub.resolves(createMockResponse);

      const params: any = {
        labels: { env: "test" },
        extraConfigs: {
          mobile: {
            simulateConfig: {
              simulatedContextId: "mobile-sim-ctx-123",
              simulate: false,
            },
          },
        },
      };

      // Store original values
      const originalLabels = { ...params.labels };
      const originalContextSync = params.contextSync;
      const originalLabelsRef = params.labels;
      const originalContextSyncRef = params.contextSync;

      // Make GetContextInfo report the simulated context as completed immediately.
      contextStatusEntries = [
        {
          contextId: "mobile-sim-ctx-123",
          path: "/data/agentbay_mobile_info",
          errorMessage: "",
          status: "Success",
          startTime: 0,
          finishTime: 0,
          taskType: "download",
        },
      ];

      await agentBay.create(params);

      // Ensure we didn't sleep/retry: create() should break on the first status check.
      expect(mockClient.getContextInfo.calledOnce).toBe(true);

      // Verify the original params object was not modified
      expect(params.labels).toEqual(originalLabels);
      expect(params.labels).toBe(originalLabelsRef); // Should be the same object reference
      // If contextSync was undefined, it should remain undefined
      // If it was an array, it should remain the same array reference
      if (originalContextSync === undefined) {
        expect(params.contextSync).toBeUndefined();
      } else {
        expect(params.contextSync).toBe(originalContextSyncRef);
      }
    });
  });
});
