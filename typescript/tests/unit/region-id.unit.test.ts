import { AgentBay } from "../../src";

describe("Region ID Unit Tests", () => {
  const mockApiKey = "test-api-key-12345";

  describe("AgentBay initialization", () => {
    test("should create AgentBay client with region_id", () => {
      const config = {
        timeout_ms: 60000,
        region_id: "cn-hangzhou",
      };
      const client = new AgentBay({
        apiKey: "test-api-key",
        config: config,
      });
      expect(client.getRegionId()).toBe("cn-hangzhou");
    });

    test("should fill defaults and derive endpoint when only region_id is provided", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        config: {
          region_id: "cn-hangzhou",
        },
      });

      expect(client.getRegionId()).toBe("cn-hangzhou");
      expect((client as any).endpoint).toBe("agentbay.cn-hangzhou.aliyuncs.com");
      expect((client as any).config.timeout_ms).toBe(60000);
    });

    test("should default to cn-hangzhou when no region_id is provided", () => {
      // Clear environment variable to ensure clean test
      const originalRegionId = process.env.AGENTBAY_REGION_ID;
      delete process.env.AGENTBAY_REGION_ID;

      try {
        const client = new AgentBay({
          apiKey: mockApiKey,
        });

        expect(client.getRegionId()).toBe("cn-hangzhou");
      } finally {
        // Restore original environment variable
        if (originalRegionId !== undefined) {
          process.env.AGENTBAY_REGION_ID = originalRegionId;
        }
      }
    });

    test("should fall back to default when region_id is empty string", () => {
      const client = new AgentBay({
        apiKey: "test-api-key",
        config: {
          timeout_ms: 60000,
          region_id: "",
        },
      });
      // Empty string is treated as "not provided" → default cn-hangzhou
      expect(client.getRegionId()).toBe("cn-hangzhou");
    });

    test("should normalize pre- prefix and use the pre-release endpoint", () => {
      const client = new AgentBay({
        apiKey: mockApiKey,
        config: {
          region_id: "pre-cn-hangzhou",
        },
      });
      expect(client.getRegionId()).toBe("cn-hangzhou");
      expect((client as any).endpoint).toBe(
        "agentbay-pre.cn-hangzhou.aliyuncs.com"
      );
    });

    test("should map each supported region to its unit endpoint", () => {
      const cases: Array<[string, string]> = [
        ["cn-hangzhou", "agentbay.cn-hangzhou.aliyuncs.com"],
        ["ap-southeast-1", "agentbay.ap-southeast-1.aliyuncs.com"],
        ["us-east-1", "agentbay.us-east-1.aliyuncs.com"],
      ];
      for (const [region, expected] of cases) {
        const client = new AgentBay({
          apiKey: mockApiKey,
          config: { region_id: region },
        });
        expect(client.getRegionId()).toBe(region);
        expect((client as any).endpoint).toBe(expected);
      }
    });

    test("should throw on invalid region_id", () => {
      expect(
        () =>
          new AgentBay({
            apiKey: mockApiKey,
            config: { region_id: "us-west-1" },
          })
      ).toThrow(/Invalid region_id 'us-west-1'/);
    });
  });
});
