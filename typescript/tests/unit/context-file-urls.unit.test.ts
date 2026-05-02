import { AgentBay } from "../../src";
import { ContextService } from "../../src/context";

function makeAgentBayWithMocks() {
  const agentBay = new AgentBay({ apiKey: "test-api-key" });
  const clientMock = (agentBay as any).getClient
    ? (agentBay as any).getClient()
    : (agentBay as any).client;
  return {
    agentBay,
    context: (agentBay as any).context as ContextService,
    clientMock,
  };
}

describe("Context File URLs - Unit", () => {
  const contextId = "ctx-123";
  const testPath = "/tmp/integration_upload_test.txt";

  test("getFileUploadUrl success", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.getContextFileUploadUrl = jest.fn().mockResolvedValue({
      body: {
        success: true,
        data: { url: "https://oss.example.com/upload-url", expireTime: 3600 },
        requestId: "req-upload-1",
      },
    });

    const res = await context.getFileUploadUrl(contextId, testPath);
    expect(res.success).toBe(true);
    expect(res.url).toBe("https://oss.example.com/upload-url");
    expect(res.expireTime).toBe(3600);
  });

  test("getFileDownloadUrl success", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.getContextFileDownloadUrl = jest.fn().mockResolvedValue({
      body: {
        success: true,
        data: { url: "https://oss.example.com/download-url", expireTime: 7200 },
        requestId: "req-download-1",
      },
    });

    const res = await context.getFileDownloadUrl(contextId, testPath);
    expect(res.success).toBe(true);
    expect(res.url).toBe("https://oss.example.com/download-url");
    expect(res.expireTime).toBe(7200);
  });

  test("getFileDownloadUrl unavailable", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.getContextFileDownloadUrl = jest.fn().mockResolvedValue({
      body: {
        success: false,
        data: null,
        requestId: "req-download-2",
      },
    });

    const res = await context.getFileDownloadUrl(contextId, testPath);
    expect(res.success).toBe(false);
    expect(res.url).toBe("");
    expect(res.expireTime).toBeUndefined();
  });

  test("listFiles with entry", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.describeContextFiles = jest.fn().mockResolvedValue({
      body: {
        success: true,
        count: 1,
        data: [
          {
            fileId: "fid-1",
            fileName: "integration_upload_test.txt",
            filePath: "/tmp/integration_upload_test.txt",
            size: 21,
            status: "ready",
          },
        ],
        requestId: "req-list-1",
      },
    });

    const res = await context.listFiles(contextId, "/tmp", 1, 50);
    expect(res.success).toBe(true);
    expect(res.entries.length).toBe(1);
    expect(res.entries[0].filePath).toBe("/tmp/integration_upload_test.txt");
    expect(res.count).toBe(1);
  });

  test("listFiles empty", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.describeContextFiles = jest.fn().mockResolvedValue({
      body: {
        success: true,
        count: undefined,
        data: [],
        requestId: "req-list-2",
      },
    });

    const res = await context.listFiles(contextId, "/tmp", 1, 50);
    expect(res.success).toBe(true);
    expect(res.entries.length).toBe(0);
    expect(res.count).toBeUndefined();
  });

  test("listFiles uses MaxResults/NextToken and omits page params", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.describeContextFiles = jest.fn().mockResolvedValue({
      body: {
        success: true,
        count: 2,
        nextToken: "token-2",
        data: [],
        requestId: "req-list-token",
      },
    });

    await context.listFiles(contextId, "/", 1, 50, 10, "token-1");
    expect(clientMock.describeContextFiles).toHaveBeenCalledTimes(1);
    const req = clientMock.describeContextFiles.mock.calls[0][0];
    expect(req.maxResults).toBe(10);
    expect(req.nextToken).toBe("token-1");
    expect(req.pageNumber).toBeUndefined();
    expect(req.pageSize).toBeUndefined();

    const res = await context.listFiles(contextId, "/tmp", 1, 50, 10);
    expect(res.nextToken).toBe("token-2");
  });

  test("deleteFile success", async () => {
    const { context, clientMock } = makeAgentBayWithMocks();
    clientMock.deleteContextFile = jest.fn().mockResolvedValue({
      body: {
        success: true,
        requestId: "req-del-1",
      },
    });

    const res = await context.deleteFile(contextId, testPath);
    expect(res.success).toBe(true);
  });
});
