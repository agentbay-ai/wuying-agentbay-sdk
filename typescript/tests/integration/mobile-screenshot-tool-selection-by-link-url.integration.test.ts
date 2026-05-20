import { AgentBay } from "../../src";

// After the multi-region refactor, endpoints are derived from region_id.
// Both pre-release endpoints map to the "pre-cn-hangzhou" region.
const LINK_URL_REGION = "pre-cn-hangzhou";
const LINK_URL_IMAGE_ID = "mobile-use-android-12-gw";

const NO_LINK_URL_REGION = "pre-cn-hangzhou";
const NO_LINK_URL_IMAGE_ID = "mobile_latest";

describe("Mobile screenshot tool selection by linkUrl", () => {
  test("linkUrl present requires betaTakeScreenshot", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({
      apiKey,
      config: {
        timeout_ms: 60000,
        region_id: process.env.AGENTBAY_REGION_ID || LINK_URL_REGION,
      },
    });

    const createResult = await client.create({ imageId: LINK_URL_IMAGE_ID });
    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    if (!createResult.session) {
      return;
    }
    const session = createResult.session;

    try {
      expect(session.getLinkUrl()).not.toBe("");

      const r = await session.mobile.screenshot();
      expect(r.success).toBe(false);
      expect(r.errorMessage || "").toContain("does not support `screenshot()`");
      expect(r.errorMessage || "").toContain("beta_take_screenshot");

      const beta = await session.mobile.betaTakeScreenshot();
      expect(beta.success).toBe(true);
      expect(beta.type).toBe("image");
      expect(beta.mimeType).toBe("image/png");
      expect(typeof beta.width).toBe("number");
      expect(typeof beta.height).toBe("number");
      expect((beta.width || 0) > 0).toBe(true);
      expect((beta.height || 0) > 0).toBe(true);
      expect(beta.data instanceof Uint8Array).toBe(true);
      expect(beta.data.length).toBeGreaterThan(0);
      expect(Array.from(beta.data.slice(0, 8))).toEqual([
        0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
      ]);
    } finally {
      await session.delete();
    }
  });

  test("linkUrl absent requires screenshot", async () => {
    const apiKey = process.env.AGENTBAY_API_KEY;
    if (!apiKey) {
      return;
    }

    const client = new AgentBay({
      apiKey,
      config: {
        timeout_ms: 60000,
        region_id: process.env.AGENTBAY_REGION_ID || NO_LINK_URL_REGION,
      },
    });

    const createResult = await client.create({ imageId: NO_LINK_URL_IMAGE_ID });
    expect(createResult.success).toBe(true);
    expect(createResult.session).toBeDefined();
    if (!createResult.session) {
      return;
    }
    const session = createResult.session;

    try {
      expect(session.getLinkUrl()).toBe("");

      const r = await session.mobile.screenshot();
      expect(r.success).toBe(true);
      expect(typeof r.data).toBe("string");
      expect(String(r.data || "").trim()).not.toBe("");

      const beta = await session.mobile.betaTakeScreenshot();
      expect(beta.success).toBe(false);
      expect(beta.errorMessage || "").toContain(
        "does not support `beta_take_screenshot()`"
      );
    } finally {
      await session.delete();
    }
  });
});
