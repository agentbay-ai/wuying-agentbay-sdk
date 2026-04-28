import { LifecyclePolicy } from "../../src/lifecycle-policy";

describe("LifecyclePolicy", () => {
  describe("default values", () => {
    it("should use default idle_release_timeout=5 and max_runtime=30", () => {
      const policy = new LifecyclePolicy();
      expect(policy.idleReleaseTimeout).toBe(5);
      expect(policy.maxRuntime).toBe(30);
      expect(policy.manualRelease).toBe(false);
    });
  });

  describe("custom values", () => {
    it("should accept custom idleReleaseTimeout and maxRuntime", () => {
      const policy = new LifecyclePolicy({
        idleReleaseTimeout: 10,
        maxRuntime: 120,
      });
      expect(policy.idleReleaseTimeout).toBe(10);
      expect(policy.maxRuntime).toBe(120);
    });

    it("should use default max_runtime when only idle is set", () => {
      const policy = new LifecyclePolicy({ idleReleaseTimeout: 10 });
      expect(policy.idleReleaseTimeout).toBe(10);
      expect(policy.maxRuntime).toBe(30);
    });

    it("should use default idle when only max_runtime is set", () => {
      const policy = new LifecyclePolicy({ maxRuntime: 60 });
      expect(policy.idleReleaseTimeout).toBe(5);
      expect(policy.maxRuntime).toBe(60);
    });
  });

  describe("manual release", () => {
    it("should support manual release mode", () => {
      const policy = new LifecyclePolicy({ manualRelease: true });
      expect(policy.manualRelease).toBe(true);
      expect(policy.idleReleaseTimeout).toBe(0);
      expect(policy.maxRuntime).toBe(0);
    });

    it("should reject idleReleaseTimeout with manual release", () => {
      expect(() =>
        new LifecyclePolicy({ manualRelease: true, idleReleaseTimeout: 10 })
      ).toThrow();
    });

    it("should reject maxRuntime with manual release", () => {
      expect(() =>
        new LifecyclePolicy({ manualRelease: true, maxRuntime: 60 })
      ).toThrow();
    });
  });

  describe("validation", () => {
    it("should reject non-positive idleReleaseTimeout", () => {
      expect(() => new LifecyclePolicy({ idleReleaseTimeout: 0 })).toThrow();
      expect(() => new LifecyclePolicy({ idleReleaseTimeout: -1 })).toThrow();
    });

    it("should reject non-integer idleReleaseTimeout", () => {
      expect(() => new LifecyclePolicy({ idleReleaseTimeout: 1.5 })).toThrow();
    });

    it("should reject non-positive maxRuntime", () => {
      expect(() => new LifecyclePolicy({ maxRuntime: 0 })).toThrow();
      expect(() => new LifecyclePolicy({ maxRuntime: -1 })).toThrow();
    });

    it("should reject non-integer maxRuntime", () => {
      expect(() => new LifecyclePolicy({ maxRuntime: 1.5 })).toThrow();
    });
  });
});
