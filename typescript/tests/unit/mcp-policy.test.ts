import { AgentBay } from "../../src";
import * as sinon from "sinon";

describe("CreateMcpSession policyId", () => {
  let mockClient: any;
  let createMcpSessionStub: sinon.SinonStub;
  let clientConstructorStub: sinon.SinonStub;
  let contextServiceConstructorStub: sinon.SinonStub;

  const mockConfigData = {
    region_id: "cn-hangzhou",
    endpoint: "agentbay.cn-hangzhou.aliyuncs.com",
    timeout_ms: 30000,
  };

  beforeEach(() => {
    mockClient = {
      createMcpSession: sinon.stub(),
    };
    createMcpSessionStub = mockClient.createMcpSession;

    // Set environment variables for config instead of stubbing loadConfig
    process.env.AGENTBAY_REGION_ID = mockConfigData.region_id;
    process.env.AGENTBAY_TIMEOUT_MS = String(mockConfigData.timeout_ms);

    clientConstructorStub = sinon.stub().returns(mockClient);
    sinon
      .stub(require("../../src/api/client"), "Client")
      .callsFake(clientConstructorStub);

    contextServiceConstructorStub = sinon.stub().returns({
      get: sinon.stub().resolves({
        success: false,
        errorMessage: "Context not found",
      }),
    });
    sinon
      .stub(require("../../src/context"), "ContextService")
      .callsFake(contextServiceConstructorStub);
  });

  afterEach(() => {
    sinon.restore();
  });

  it("should pass policyId in CreateMcpSession request", async () => {
    const apiKey = "test-api-key";
    const agentBay = new AgentBay({ apiKey });

    const createMockResponse = {
      statusCode: 200,
      body: {
        data: {
          sessionId: "s-1",
          resourceUrl: "u",
        },
        requestId: "r-1",
      },
    };
    createMcpSessionStub.resolves(createMockResponse);

    const policyId = "policy-xyz";
    const result = await agentBay.create({ policyId });
    expect(result.success).toBe(true);

    expect(createMcpSessionStub.calledOnce).toBe(true);
    const arg0 = createMcpSessionStub.getCall(0).args[0];
    expect(arg0.mcpPolicyId).toBe(policyId);
  });
});
