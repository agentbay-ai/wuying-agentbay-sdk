import { loadConfig } from "../../src/config";

describe("ConfigOptions", () => {
  it("should allow partial fields and fill defaults", () => {
    const config = loadConfig({ region_id: "ap-southeast-1" });
    expect(config.endpoint).toBe("agentbay.ap-southeast-1.aliyuncs.com");
    expect(config.timeout_ms).toBe(60000);
    expect(config.region_id).toBe("ap-southeast-1");
  });
});
