import { loadConfig } from "../../src/config";

describe("ConfigOptions", () => {
  it("should allow partial fields and fill defaults", () => {
    const config = loadConfig({ region_id: "ap-southeast-1" });
    expect(config.endpoint).toBe("agentbay.ap-southeast-1.aliyuncs.com");
    expect(config.timeout_ms).toBe(60000);
    expect(config.region_id).toBe("ap-southeast-1");
  });
});

describe("Endpoint fallback path", () => {
  const ENV_KEYS = [
    "AGENTBAY_REGION_ID",
    "AGENTBAY_ENDPOINT",
    "AGENTBAY_TIMEOUT_MS",
  ];

  let warnSpy: jest.SpyInstance;
  let savedEnv: Record<string, string | undefined>;

  beforeEach(() => {
    warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
    savedEnv = {};
    for (const k of ENV_KEYS) {
      savedEnv[k] = process.env[k];
      delete process.env[k];
    }
  });

  afterEach(() => {
    warnSpy.mockRestore();
    for (const k of ENV_KEYS) {
      if (savedEnv[k] === undefined) delete process.env[k];
      else process.env[k] = savedEnv[k];
    }
  });

  it("uses cfg.endpoint as-is when region_id is not set", () => {
    const config = loadConfig({ endpoint: "custom.example.com" });
    expect(config.endpoint).toBe("custom.example.com");
  });

  it("region_id wins when both cfg.region_id and cfg.endpoint are set", () => {
    const config = loadConfig({
      region_id: "ap-southeast-1",
      endpoint: "ignored.example.com",
    });
    expect(config.endpoint).toBe("agentbay.ap-southeast-1.aliyuncs.com");
    expect(config.region_id).toBe("ap-southeast-1");
  });

  it("uses AGENTBAY_ENDPOINT env var as fallback", () => {
    process.env.AGENTBAY_ENDPOINT = "env-endpoint.example.com";
    const config = loadConfig();
    expect(config.endpoint).toBe("env-endpoint.example.com");
  });

  it("AGENTBAY_REGION_ID env wins over AGENTBAY_ENDPOINT env", () => {
    process.env.AGENTBAY_REGION_ID = "us-east-1";
    process.env.AGENTBAY_ENDPOINT = "env-endpoint.example.com";
    const config = loadConfig();
    expect(config.endpoint).toBe("agentbay.us-east-1.aliyuncs.com");
    expect(config.region_id).toBe("us-east-1");
  });

  it("cfg.endpoint (code layer) wins over AGENTBAY_REGION_ID (env layer)", () => {
    process.env.AGENTBAY_REGION_ID = "us-east-1";
    const config = loadConfig({ endpoint: "cfg-endpoint.example.com" });
    expect(config.endpoint).toBe("cfg-endpoint.example.com");
  });

  it("empty region_id with endpoint still uses endpoint", () => {
    const config = loadConfig({
      region_id: "",
      endpoint: "fallback.example.com",
    });
    expect(config.endpoint).toBe("fallback.example.com");
  });
});
