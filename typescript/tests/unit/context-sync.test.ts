import {
  ContextSync,
  SyncPolicy,
  newSyncPolicy,
  newUploadPolicy,
  newDownloadPolicy,
  newDeletePolicy,
  newRecyclePolicy,
  newExtractPolicy,
  RecyclePolicy,
  UploadStrategy,
  DownloadStrategy,
  Lifecycle,
  MappingPolicy,
  newMappingPolicy,
  SyncPolicyImpl,
} from "../../src/context-sync";
import { log } from "../../src/utils/logger";

describe("ContextSync Unit Tests", () => {
  describe("SyncPolicy Default Construction", () => {
    it("should create default SyncPolicy with correct values", () => {
      const policy = newSyncPolicy();

      // Verify the policy is not null
      expect(policy).toBeDefined();

      // Verify uploadPolicy
      expect(policy.uploadPolicy).toBeDefined();
      if (policy.uploadPolicy) {
        expect(policy.uploadPolicy.autoUpload).toBe(true);
        expect(policy.uploadPolicy.uploadStrategy).toBe(
          UploadStrategy.UploadBeforeResourceRelease
        );
      }

      // Verify downloadPolicy
      expect(policy.downloadPolicy).toBeDefined();
      if (policy.downloadPolicy) {
        expect(policy.downloadPolicy.autoDownload).toBe(true);
        expect(policy.downloadPolicy.downloadStrategy).toBe(
          DownloadStrategy.DownloadAsync
        );
      }

      // Verify deletePolicy
      expect(policy.deletePolicy).toBeDefined();
      if (policy.deletePolicy) {
        expect(policy.deletePolicy.syncLocalFile).toBe(true);
      }

      // Verify recyclePolicy
      expect(policy.recyclePolicy).toBeDefined();
      if (policy.recyclePolicy) {
        expect(policy.recyclePolicy.lifecycle).toBe(
          Lifecycle.Lifecycle_Forever
        );
        expect(policy.recyclePolicy.paths).toBeDefined();
        expect(policy.recyclePolicy.paths).toHaveLength(1);
        expect(policy.recyclePolicy.paths[0]).toBe("");
      }

      // Verify bwList
      expect(policy.bwList).toBeDefined();
      if (policy.bwList && policy.bwList.whiteLists) {
        expect(policy.bwList.whiteLists).toBeDefined();
        expect(policy.bwList.whiteLists).toHaveLength(1);

        const firstWhiteList = policy.bwList.whiteLists[0];
        expect(firstWhiteList.path).toBe("");
        expect(firstWhiteList.excludePaths).toBeDefined();
        if (firstWhiteList.excludePaths) {
          expect(firstWhiteList.excludePaths).toHaveLength(0);
        }
      }
    });

    it("should create default SyncPolicy that matches JSON requirements", () => {
      const policy = newSyncPolicy();

      // Convert to JSON and verify structure
      const jsonString = JSON.stringify(policy);
      const jsonObject = JSON.parse(jsonString);

      // Verify uploadPolicy in JSON
      expect(jsonObject.uploadPolicy).toBeDefined();
      expect(jsonObject.uploadPolicy.autoUpload).toBe(true);
      expect(jsonObject.uploadPolicy.uploadStrategy).toBe(
        "UploadBeforeResourceRelease"
      );

      // Verify downloadPolicy in JSON
      expect(jsonObject.downloadPolicy).toBeDefined();
      expect(jsonObject.downloadPolicy.autoDownload).toBe(true);
      expect(jsonObject.downloadPolicy.downloadStrategy).toBe("DownloadAsync");

      // Verify deletePolicy in JSON
      expect(jsonObject.deletePolicy).toBeDefined();
      expect(jsonObject.deletePolicy.syncLocalFile).toBe(true);

      // Verify recyclePolicy in JSON
      expect(jsonObject.recyclePolicy).toBeDefined();
      expect(jsonObject.recyclePolicy.lifecycle).toBe("Lifecycle_Forever");
      expect(jsonObject.recyclePolicy.paths).toBeDefined();
      expect(jsonObject.recyclePolicy.paths).toHaveLength(1);
      expect(jsonObject.recyclePolicy.paths[0]).toBe("");

      // Verify bwList in JSON
      expect(jsonObject.bwList).toBeDefined();
      expect(jsonObject.bwList.whiteLists).toBeDefined();
      expect(jsonObject.bwList.whiteLists).toHaveLength(1);
      expect(jsonObject.bwList.whiteLists[0].path).toBe("");
      // excludePaths should be present in JSON since it's an empty array
      expect(jsonObject.bwList.whiteLists[0].excludePaths).toBeDefined();
      expect(jsonObject.bwList.whiteLists[0].excludePaths).toHaveLength(0);

      // Verify syncPaths should not exist in JSON
      expect(jsonObject.syncPaths).toBeUndefined();

      // Log the generated JSON for verification
      log("Generated JSON:", jsonString);
    });

    it("should create individual policy components with correct defaults", () => {
      // Test UploadPolicy defaults
      const uploadPolicy = newUploadPolicy();
      expect(uploadPolicy.autoUpload).toBe(true);
      expect(uploadPolicy.uploadStrategy).toBe(
        UploadStrategy.UploadBeforeResourceRelease
      );

      // Test DownloadPolicy defaults
      const downloadPolicy = newDownloadPolicy();
      expect(downloadPolicy.autoDownload).toBe(true);
      expect(downloadPolicy.downloadStrategy).toBe(
        DownloadStrategy.DownloadAsync
      );

      // Test DeletePolicy defaults
      const deletePolicy = newDeletePolicy();
      expect(deletePolicy.syncLocalFile).toBe(true);
    });

    it("should create ContextSync with default policy", () => {
      const contextId = "test-context-123";
      const path = "/test/path";
      const policy = newSyncPolicy();

      const contextSync = new ContextSync(contextId, path, policy);

      expect(contextSync.contextId).toBe(contextId);
      expect(contextSync.path).toBe(path);
      expect(contextSync.policy).toBe(policy);
    });

    it("should allow chaining with withPolicy method", () => {
      const contextSync = new ContextSync("test-context", "/test/path");
      const policy = newSyncPolicy();

      const result = contextSync.withPolicy(policy);

      expect(result).toBe(contextSync);
      expect(contextSync.policy).toBe(policy);
    });

    it("should create RecyclePolicy with Lifecycle_1Day", () => {
      // Create a custom recycle policy with Lifecycle_1Day
      const customRecyclePolicy: RecyclePolicy = {
        lifecycle: Lifecycle.Lifecycle_1Day,
        paths: ["/custom/path"],
      };

      // Create a sync policy with the custom recycle policy
      const syncPolicy: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        downloadPolicy: newDownloadPolicy(),
        deletePolicy: newDeletePolicy(),
        extractPolicy: newExtractPolicy(),
        recyclePolicy: customRecyclePolicy,
        bwList: {
          whiteLists: [
            {
              path: "",
              excludePaths: [],
            },
          ],
        },
      };

      // Verify the recycle policy
      expect(syncPolicy.recyclePolicy).toBeDefined();
      if (syncPolicy.recyclePolicy) {
        expect(syncPolicy.recyclePolicy.lifecycle).toBe(
          Lifecycle.Lifecycle_1Day
        );
        expect(syncPolicy.recyclePolicy.paths).toBeDefined();
        expect(syncPolicy.recyclePolicy.paths).toHaveLength(1);
        expect(syncPolicy.recyclePolicy.paths[0]).toBe("/custom/path");
      }

      // Test JSON serialization
      const jsonString = JSON.stringify(syncPolicy);
      const jsonObject = JSON.parse(jsonString);

      expect(jsonObject.recyclePolicy).toBeDefined();
      expect(jsonObject.recyclePolicy.lifecycle).toBe("Lifecycle_1Day");
      expect(jsonObject.recyclePolicy.paths).toHaveLength(1);
      expect(jsonObject.recyclePolicy.paths[0]).toBe("/custom/path");
    });

    it("should throw error when recyclePolicy path contains wildcard patterns", () => {
      // Create a recycle policy with invalid wildcard path
      const invalidRecyclePolicy: RecyclePolicy = {
        lifecycle: Lifecycle.Lifecycle_1Day,
        paths: ["/path/with/*"],
      };

      const syncPolicyWithInvalidPath: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        downloadPolicy: newDownloadPolicy(),
        deletePolicy: newDeletePolicy(),
        extractPolicy: newExtractPolicy(),
        recyclePolicy: invalidRecyclePolicy,
        bwList: {
          whiteLists: [
            {
              path: "",
              excludePaths: [],
            },
          ],
        },
      };

      // Test that ContextSync constructor throws an error for invalid path
      expect(() => {
        new ContextSync(
          "test-context",
          "/test/path",
          syncPolicyWithInvalidPath
        );
      }).toThrow(
        "Wildcard patterns are not supported in path when isPathRegex=false. Got: /path/with/*. Please use exact directory paths or set isPathRegex=true for regex matching."
      );
    });

    it("should throw error when SyncPolicy contains unknown properties (e.g. bwlist typo)", () => {
      expect(() => {
        new SyncPolicyImpl({
          bwlist: { whiteLists: [] },
        } as any);
      }).toThrow("Unknown property in SyncPolicy: 'bwlist'.");

      expect(() => {
        new ContextSync("test-context", "/test/path", {
          bwlist: { whiteLists: [] },
        } as any);
      }).toThrow("Unknown property in SyncPolicy: 'bwlist'.");
    });
  });

  describe("MappingPolicy Tests", () => {
    it("should create default MappingPolicy", () => {
      const mappingPolicy = newMappingPolicy();

      expect(mappingPolicy).toBeDefined();
      expect(mappingPolicy.path).toBe("");
    });

    it("should create MappingPolicy with Windows path", () => {
      const windowsPath = "c:\\Users\\Administrator\\Downloads";
      const mappingPolicy: MappingPolicy = {
        path: windowsPath,
      };

      expect(mappingPolicy).toBeDefined();
      expect(mappingPolicy.path).toBe(windowsPath);
    });

    it("should serialize MappingPolicy correctly", () => {
      const windowsPath = "c:\\Users\\Administrator\\Downloads";
      const mappingPolicy: MappingPolicy = {
        path: windowsPath,
      };

      const jsonString = JSON.stringify(mappingPolicy);
      const jsonObject = JSON.parse(jsonString);

      expect(jsonObject.path).toBe(windowsPath);
    });
  });

  describe("SyncPolicy with MappingPolicy Tests", () => {
    it("should create SyncPolicy with MappingPolicy", () => {
      const windowsPath = "c:\\Users\\Administrator\\Downloads";
      const mappingPolicy: MappingPolicy = {
        path: windowsPath,
      };

      const syncPolicy: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        downloadPolicy: newDownloadPolicy(),
        deletePolicy: newDeletePolicy(),
        extractPolicy: newExtractPolicy(),
        mappingPolicy: mappingPolicy,
      };

      expect(syncPolicy).toBeDefined();
      expect(syncPolicy.mappingPolicy).toBeDefined();
      expect(syncPolicy.mappingPolicy?.path).toBe(windowsPath);
    });

    it("should serialize SyncPolicy with MappingPolicy correctly", () => {
      const windowsPath = "c:\\Users\\Administrator\\Downloads";
      const mappingPolicy: MappingPolicy = {
        path: windowsPath,
      };

      const syncPolicy: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        mappingPolicy: mappingPolicy,
      };

      const jsonString = JSON.stringify(syncPolicy);
      const jsonObject = JSON.parse(jsonString);

      expect(jsonObject.mappingPolicy).toBeDefined();
      expect(jsonObject.mappingPolicy.path).toBe(windowsPath);
    });
  });

  describe("ContextSync with MappingPolicy Tests", () => {
    it("should create ContextSync with MappingPolicy", () => {
      const contextId = "ctx-12345";
      const linuxPath = "/home/wuying/下载";
      const windowsPath = "c:\\Users\\Administrator\\Downloads";

      const mappingPolicy: MappingPolicy = {
        path: windowsPath,
      };

      const syncPolicy: SyncPolicy = {
        uploadPolicy: newUploadPolicy(),
        downloadPolicy: newDownloadPolicy(),
        deletePolicy: newDeletePolicy(),
        extractPolicy: newExtractPolicy(),
        mappingPolicy: mappingPolicy,
      };

      const contextSync = new ContextSync(contextId, linuxPath, syncPolicy);

      expect(contextSync).toBeDefined();
      expect(contextSync.contextId).toBe(contextId);
      expect(contextSync.path).toBe(linuxPath);
      expect(contextSync.policy).toBeDefined();
      expect(contextSync.policy?.mappingPolicy).toBeDefined();
      expect(contextSync.policy?.mappingPolicy?.path).toBe(windowsPath);
    });
  });

  describe("WhiteList Regex Path and Exclude Tests", () => {
    it("should support combined isPathRegex and isExcludeRegex mode", () => {
      // ── Construction: both regex flags enabled ────────────────────────────
      const wl = {
        path: "project-.*",
        isPathRegex: true,
        excludePaths: ["cache.*", "下载.*"],
        isExcludeRegex: true,
      };
      expect(wl.path).toBe("project-.*");
      expect(wl.isPathRegex).toBe(true);
      expect(wl.excludePaths).toEqual(["cache.*", "下载.*"]);
      expect(wl.isExcludeRegex).toBe(true);

      // ── Serialization ────────────────────────────────────────────────────
      const json = JSON.parse(JSON.stringify(wl));
      expect(json.path).toBe("project-.*");
      expect(json.isPathRegex).toBe(true);
      expect(json.excludePaths).toEqual(["cache.*", "下载.*"]);
      expect(json.isExcludeRegex).toBe(true);

      // ── Wildcard in regex path is allowed ─────────────────────────────────
      expect(() => {
        new ContextSync("ctx", "/base", {
          bwList: { whiteLists: [{ path: "/home/wuying/.*", isPathRegex: true }] },
        });
      }).not.toThrow();

      // ── Wildcard in regex excludePaths is allowed ────────────────────────
      expect(() => {
        new ContextSync("ctx", "/base", {
          bwList: {
            whiteLists: [
              { path: "/home/wuying", excludePaths: ["record.*"], isExcludeRegex: true },
            ],
          },
        });
      }).not.toThrow();

      // ── Wildcard in path raises when isPathRegex=false ──────────────────
      expect(() => {
        new ContextSync("ctx", "/base", {
          bwList: { whiteLists: [{ path: "/home/wuying/*" }] },
        });
      }).toThrow("isPathRegex=false");

      // ── Wildcard in excludePaths raises when isExcludeRegex=false ──────
      expect(() => {
        new ContextSync("ctx", "/base", {
          bwList: {
            whiteLists: [{ path: "/home/wuying", excludePaths: ["/invalid/*"] }],
          },
        });
      }).toThrow("isExcludeRegex=false");

      // ── Integration in SyncPolicy ─────────────────────────────────────────
      const syncPolicy: SyncPolicy = {
        bwList: {
          whiteLists: [
            {
              path: "project-.*",
              isPathRegex: true,
              excludePaths: ["cache.*"],
              isExcludeRegex: true,
            },
          ],
        },
      };
      const wlEntry = syncPolicy.bwList!.whiteLists![0];
      expect(wlEntry.path).toBe("project-.*");
      expect(wlEntry.isPathRegex).toBe(true);
      expect(wlEntry.excludePaths).toEqual(["cache.*"]);
      expect(wlEntry.isExcludeRegex).toBe(true);

      const policyJson = JSON.parse(JSON.stringify(syncPolicy));
      const wlJson = policyJson.bwList.whiteLists[0];
      expect(wlJson.path).toBe("project-.*");
      expect(wlJson.isPathRegex).toBe(true);
      expect(wlJson.excludePaths).toEqual(["cache.*"]);
      expect(wlJson.isExcludeRegex).toBe(true);
    });
  });
});
