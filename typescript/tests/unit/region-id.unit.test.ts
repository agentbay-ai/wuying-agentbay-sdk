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

    test("should map known pre regions via the hardcoded table", () => {
      // Different pre regions use different hostname conventions:
      // cn-hangzhou → "agentbay-pre.*", ap-southeast-1 → "wuyingai-pre.*".
      const cases: Array<[string, string, string]> = [
        [
          "pre-cn-hangzhou",
          "cn-hangzhou",
          "agentbay-pre.cn-hangzhou.aliyuncs.com",
        ],
        [
          "pre-ap-southeast-1",
          "ap-southeast-1",
          "wuyingai-pre.ap-southeast-1.aliyuncs.com",
        ],
      ];
      for (const [input, region, endpoint] of cases) {
        const client = new AgentBay({
          apiKey: mockApiKey,
          config: { region_id: input },
        });
        expect(client.getRegionId()).toBe(region);
        expect((client as any).endpoint).toBe(endpoint);
      }
    });

    test("should map known regions by pattern substitution silently", () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
      try {
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
        expect(warnSpy).not.toHaveBeenCalled();
      } finally {
        warnSpy.mockRestore();
      }
    });

    test("should warn and still use pattern for unknown production regions", () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
      try {
        const cases: Array<[string, string]> = [
          ["us-west-1", "agentbay.us-west-1.aliyuncs.com"],
          ["eu-central-1", "agentbay.eu-central-1.aliyuncs.com"],
        ];
        for (const [region, expected] of cases) {
          const client = new AgentBay({
            apiKey: mockApiKey,
            config: { region_id: region },
          });
          expect(client.getRegionId()).toBe(region);
          expect((client as any).endpoint).toBe(expected);
        }
        // The SDK reads the config more than once internally, so the exact
        // call count is an implementation detail. We just assert the warning
        // fired and that every unknown region appears in the messages along
        // with the known list.
        expect(warnSpy).toHaveBeenCalled();
        const message = warnSpy.mock.calls
          .map((args) => String(args[0]))
          .join("\n");
        expect(message).toMatch(/us-west-1/);
        expect(message).toMatch(/eu-central-1/);
        expect(message).toMatch(/cn-hangzhou/);
        expect(message).toMatch(/ap-southeast-1/);
        expect(message).toMatch(/us-east-1/);
      } finally {
        warnSpy.mockRestore();
      }
    });

    test("should warn and fall back to default pattern for unknown pre regions", () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
      try {
        const client = new AgentBay({
          apiKey: mockApiKey,
          config: { region_id: "pre-us-west-1" },
        });
        expect(client.getRegionId()).toBe("us-west-1");
        expect((client as any).endpoint).toBe(
          "agentbay-pre.us-west-1.aliyuncs.com"
        );
        // A warning was emitted naming the unknown region and the known options.
        expect(warnSpy).toHaveBeenCalled();
        const message = warnSpy.mock.calls
          .map((args) => String(args[0]))
          .join("\n");
        expect(message).toMatch(/pre-us-west-1/);
        expect(message).toMatch(/cn-hangzhou/);
        expect(message).toMatch(/ap-southeast-1/);
      } finally {
        warnSpy.mockRestore();
      }
    });

    test("should warn but not throw when deprecated endpoint option is passed", () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
      try {
        const client = new AgentBay({
          apiKey: mockApiKey,
          config: {
            region_id: "ap-southeast-1",
            // Exercising the deprecated `endpoint` option (kept for backwards
            // compatibility, marked @deprecated in ConfigOptions).
            endpoint: "should-be-ignored.example.com",
          },
        });
        // Endpoint comes from region_id, not from the deprecated option.
        expect(client.getRegionId()).toBe("ap-southeast-1");
        expect((client as any).endpoint).toBe(
          "agentbay.ap-southeast-1.aliyuncs.com"
        );
        // And a deprecation warning was emitted (the SDK may read the config
        // more than once internally, so we don't assert exact call count).
        expect(warnSpy).toHaveBeenCalled();
        const message = warnSpy.mock.calls
          .map((args) => String(args[0]))
          .join("\n");
        expect(message).toMatch(/DeprecationWarning/);
        expect(message).toMatch(/should-be-ignored\.example\.com/);
      } finally {
        warnSpy.mockRestore();
      }
    });

    test("should not warn when endpoint option is not passed", () => {
      const warnSpy = jest.spyOn(console, "warn").mockImplementation(() => {});
      try {
        new AgentBay({
          apiKey: mockApiKey,
          config: { region_id: "cn-hangzhou" },
        });
        expect(warnSpy).not.toHaveBeenCalled();
      } finally {
        warnSpy.mockRestore();
      }
    });
  });
});
