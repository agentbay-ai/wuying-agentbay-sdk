package com.aliyun.agentbay.test;

import com.aliyun.agentbay.Config;
import com.aliyun.agentbay.browser.BrowserContext;
import com.aliyun.agentbay.browser.BrowserSyncMode;
import com.aliyun.agentbay.browser.ExtensionOption;
import com.aliyun.agentbay.context.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.Test;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

/**
 * Test browser context policy includes BWList with white lists.
 */
public class BrowserContextPolicyTest {

    private final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    public void testDefaultSyncModeIsStandard() throws Exception {
        BrowserContext browserContext = new BrowserContext("test-context", true);
        assertEquals("Default sync mode should be STANDARD",
                     BrowserSyncMode.STANDARD, browserContext.getSyncMode());
    }

    @Test
    public void testExplicitMinimalSyncMode() throws Exception {
        BrowserContext browserContext = new BrowserContext(
            "test-context", true, BrowserSyncMode.MINIMAL, null, null);
        assertEquals("Sync mode should be MINIMAL",
                     BrowserSyncMode.MINIMAL, browserContext.getSyncMode());
    }

    @Test
    public void testBrowserContextStandardModePolicy() throws Exception {
        BrowserContext browserContext = new BrowserContext("test-browser-context", true);

        UploadPolicy uploadPolicy = new UploadPolicy(
            browserContext.isAutoUpload(),
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
            30
        );

        // STANDARD mode whitelist (matching AgentBay.create logic)
        List<WhiteList> whiteLists = new ArrayList<>();
        // Auth core
        whiteLists.add(new WhiteList("/Local State", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Cookies", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Cookies-journal", new ArrayList<>()));
        // Anti-risk-control device fingerprint (localStorage / IndexedDB)
        whiteLists.add(new WhiteList("/Default/Local Storage", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/IndexedDB", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Session Storage", new ArrayList<>()));
        // Saved passwords and form autofill
        whiteLists.add(new WhiteList("/Default/Login Data", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Login Data-journal", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Login Data For Account", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Login Data For Account-journal", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Web Data", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Web Data-journal", new ArrayList<>()));
        // Browser settings and permission consistency
        whiteLists.add(new WhiteList("/Default/Preferences", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Secure Preferences", new ArrayList<>()));
        // Network behavior consistency (HSTS / QUIC)
        whiteLists.add(new WhiteList("/Default/TransportSecurity", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Network Persistent State", new ArrayList<>()));
        // Rendering fingerprint stability
        whiteLists.add(new WhiteList("/Default/GPUCache", new ArrayList<>()));
        // Cross-domain password matching
        whiteLists.add(new WhiteList("/Default/Affiliation Database", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Affiliation Database-journal", new ArrayList<>()));
        BWList bwList = new BWList(whiteLists);

        SyncPolicy syncPolicy = new SyncPolicy(
            uploadPolicy,
            DownloadPolicy.defaultPolicy(),
            DeletePolicy.defaultPolicy(),
            ExtractPolicy.defaultPolicy(),
            bwList
        );

        // Convert to map and serialize to JSON
        Map<String, Object> policyMap = syncPolicy.toMap();

        System.out.println("Generated STANDARD mode policy JSON:");
        System.out.println(objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(policyMap));

        // Verify the policy contains the expected structure
        assertNotNull("Policy map should not be null", policyMap);
        assertTrue("bwList should be present in policy", policyMap.containsKey("bwList"));

        // Check that whiteLists exists in bwList
        @SuppressWarnings("unchecked")
        Map<String, Object> bwListMap = (Map<String, Object>) policyMap.get("bwList");
        assertNotNull("bwList should not be null", bwListMap);
        assertTrue("whiteLists should be present in bwList", bwListMap.containsKey("whiteLists"));

        // Check that we have 3 white lists
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> whiteListsData = (List<Map<String, Object>>) bwListMap.get("whiteLists");
        assertNotNull("whiteLists should not be null", whiteListsData);
        assertEquals("Expected 19 white lists in STANDARD mode", 19, whiteListsData.size());

        // Check the specific paths
        List<String> paths = new ArrayList<>();
        for (Map<String, Object> wl : whiteListsData) {
            paths.add((String) wl.get("path"));
        }

        // Auth core
        assertTrue(paths.contains("/Local State"));
        assertTrue(paths.contains("/Default/Cookies"));
        assertTrue(paths.contains("/Default/Cookies-journal"));
        // Anti-risk-control device fingerprint
        assertTrue(paths.contains("/Default/Local Storage"));
        assertTrue(paths.contains("/Default/IndexedDB"));
        assertTrue(paths.contains("/Default/Session Storage"));
        // Saved passwords and form autofill
        assertTrue(paths.contains("/Default/Login Data"));
        assertTrue(paths.contains("/Default/Login Data-journal"));
        assertTrue(paths.contains("/Default/Login Data For Account"));
        assertTrue(paths.contains("/Default/Login Data For Account-journal"));
        assertTrue(paths.contains("/Default/Web Data"));
        assertTrue(paths.contains("/Default/Web Data-journal"));
        // Browser settings and permission consistency
        assertTrue(paths.contains("/Default/Preferences"));
        assertTrue(paths.contains("/Default/Secure Preferences"));
        // Network behavior consistency
        assertTrue(paths.contains("/Default/TransportSecurity"));
        assertTrue(paths.contains("/Default/Network Persistent State"));
        // Rendering fingerprint stability
        assertTrue(paths.contains("/Default/GPUCache"));
        // Cross-domain password matching
        assertTrue(paths.contains("/Default/Affiliation Database"));
        assertTrue(paths.contains("/Default/Affiliation Database-journal"));
    }

    @Test
    public void testBrowserContextMinimalModePolicy() throws Exception {
        BrowserContext browserContext = new BrowserContext(
            "test-browser-context", true, BrowserSyncMode.MINIMAL, null, null);

        UploadPolicy uploadPolicy = new UploadPolicy(
            browserContext.isAutoUpload(),
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
            30
        );

        // MINIMAL mode whitelist
        List<WhiteList> whiteLists = new ArrayList<>();
        whiteLists.add(new WhiteList("/Local State", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Cookies", new ArrayList<>()));
        whiteLists.add(new WhiteList("/Default/Cookies-journal", new ArrayList<>()));
        BWList bwList = new BWList(whiteLists);

        SyncPolicy syncPolicy = new SyncPolicy(
            uploadPolicy,
            DownloadPolicy.defaultPolicy(),
            DeletePolicy.defaultPolicy(),
            ExtractPolicy.defaultPolicy(),
            bwList
        );

        Map<String, Object> policyMap = syncPolicy.toMap();

        System.out.println("Generated MINIMAL mode policy JSON:");
        System.out.println(objectMapper.writerWithDefaultPrettyPrinter().writeValueAsString(policyMap));

        @SuppressWarnings("unchecked")
        Map<String, Object> bwListMap = (Map<String, Object>) policyMap.get("bwList");

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> whiteListsData = (List<Map<String, Object>>) bwListMap.get("whiteLists");
        assertEquals("Expected 3 white lists in MINIMAL mode", 3, whiteListsData.size());

        List<String> paths = new ArrayList<>();
        for (Map<String, Object> wl : whiteListsData) {
            paths.add((String) wl.get("path"));
        }

        assertTrue(paths.contains("/Local State"));
        assertTrue(paths.contains("/Default/Cookies"));
        assertTrue(paths.contains("/Default/Cookies-journal"));
    }

    @Test
    public void testExtensionContextSyncPolicy() throws Exception {
        ExtensionOption extensionOption = new ExtensionOption(
            "ext-context",
            Arrays.asList("ext1.zip", "ext2.zip")
        );

        BrowserContext browserContext = new BrowserContext(
            "test-context",
            true,
            extensionOption,
            null
        );

        List<ContextSync> extensionSyncs = browserContext.getExtensionContextSyncs();
        assertNotNull("Extension syncs should not be null", extensionSyncs);
        assertFalse("Extension syncs should not be empty", extensionSyncs.isEmpty());

        // Get the first extension sync
        ContextSync extensionSync = extensionSyncs.get(0);
        assertNotNull("Extension sync should not be null", extensionSync);
        assertEquals("ext-context", extensionSync.getContextId());
        assertEquals("/tmp/extensions/", extensionSync.getPath());

        // Check policy
        SyncPolicy policy = extensionSync.getPolicy();
        assertNotNull("Extension sync policy should not be null", policy);

        // Convert to map
        Map<String, Object> policyMap = policy.toMap();
        assertNotNull("Policy map should not be null", policyMap);

        // Check upload policy
        assertTrue("uploadPolicy should be present", policyMap.containsKey("uploadPolicy"));
        @SuppressWarnings("unchecked")
        Map<String, Object> uploadPolicyMap = (Map<String, Object>) policyMap.get("uploadPolicy");
        assertEquals("Extension autoUpload should be false", false, uploadPolicyMap.get("autoUpload"));

        // Check delete policy
        assertTrue("deletePolicy should be present", policyMap.containsKey("deletePolicy"));
        @SuppressWarnings("unchecked")
        Map<String, Object> deletePolicyMap = (Map<String, Object>) policyMap.get("deletePolicy");
        assertEquals("Extension syncLocalFile should be false", false, deletePolicyMap.get("syncLocalFile"));

        // Check extract policy
        assertTrue("extractPolicy should be present", policyMap.containsKey("extractPolicy"));
        @SuppressWarnings("unchecked")
        Map<String, Object> extractPolicyMap = (Map<String, Object>) policyMap.get("extractPolicy");
        assertEquals("Extension extract should be true", true, extractPolicyMap.get("extract"));
        assertEquals("Extension deleteSrcFile should be true", true, extractPolicyMap.get("deleteSrcFile"));

        // Check BWList
        assertTrue("bwList should be present", policyMap.containsKey("bwList"));
        @SuppressWarnings("unchecked")
        Map<String, Object> bwListMap = (Map<String, Object>) policyMap.get("bwList");
        assertTrue("whiteLists should be present", bwListMap.containsKey("whiteLists"));

        @SuppressWarnings("unchecked")
        List<Map<String, Object>> whiteListsData = (List<Map<String, Object>>) bwListMap.get("whiteLists");
        assertEquals("Should have 2 extension whitelists", 2, whiteListsData.size());

        System.out.println("✅ Extension context sync policy is correct!");
    }

    @Test
    public void testFingerprintContextSyncPolicy() throws Exception {
        // Test that fingerprint context sync has correct policy
        com.aliyun.agentbay.browser.BrowserFingerprintContext fingerprintContext =
            new com.aliyun.agentbay.browser.BrowserFingerprintContext("fingerprint-id");

        BrowserContext browserContext = new BrowserContext(
            "test-context",
            true,
            null,
            fingerprintContext
        );

        ContextSync fingerprintSync = browserContext.getFingerprintContextSync();
        assertNotNull("Fingerprint sync should not be null", fingerprintSync);
        assertEquals("fingerprint-id", fingerprintSync.getContextId());
        assertEquals(Config.BROWSER_FINGERPRINT_PERSIST_PATH, fingerprintSync.getPath());

        // Check policy
        SyncPolicy policy = fingerprintSync.getPolicy();
        assertNotNull("Fingerprint sync policy should not be null", policy);

        // Convert to map
        Map<String, Object> policyMap = policy.toMap();
        assertNotNull("Policy map should not be null", policyMap);

        // Check upload policy
        assertTrue("uploadPolicy should be present", policyMap.containsKey("uploadPolicy"));
        @SuppressWarnings("unchecked")
        Map<String, Object> uploadPolicyMap = (Map<String, Object>) policyMap.get("uploadPolicy");
        assertEquals("Fingerprint autoUpload should be false", false, uploadPolicyMap.get("autoUpload"));

        // Check extract policy
        assertTrue("extractPolicy should be present", policyMap.containsKey("extractPolicy"));
        @SuppressWarnings("unchecked")
        Map<String, Object> extractPolicyMap = (Map<String, Object>) policyMap.get("extractPolicy");
        assertEquals("Fingerprint extract should be true", true, extractPolicyMap.get("extract"));
        assertEquals("Fingerprint deleteSrcFile should be true", true, extractPolicyMap.get("deleteSrcFile"));

        System.out.println("✅ Fingerprint context sync policy is correct!");
    }

    @Test
    public void testBrowserContextAutoUploadTrue() throws Exception {
        // Test browser context with auto_upload=true
        BrowserContext browserContext = new BrowserContext("test-context", true);

        assertTrue(browserContext.isAutoUpload());

        // Create upload policy
        UploadPolicy uploadPolicy = new UploadPolicy(
            browserContext.isAutoUpload(),
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
            30
        );

        Map<String, Object> uploadPolicyMap = uploadPolicy.toMap();
        assertEquals("autoUpload should be true", true, uploadPolicyMap.get("autoUpload"));
    }

    @Test
    public void testBrowserContextAutoUploadFalse() throws Exception {
        // Test browser context with auto_upload=false
        BrowserContext browserContext = new BrowserContext("test-context", false);

        assertFalse(browserContext.isAutoUpload());

        // Create upload policy
        UploadPolicy uploadPolicy = new UploadPolicy(
            browserContext.isAutoUpload(),
            UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE,
            30
        );

        Map<String, Object> uploadPolicyMap = uploadPolicy.toMap();
        assertEquals("autoUpload should be false", false, uploadPolicyMap.get("autoUpload"));
    }

    @Test
    public void testUploadPolicyArchiveExcludePaths() {
        UploadPolicy policy = new UploadPolicy();
        policy.setUploadMode(UploadMode.ARCHIVE);
        List<String> excludePaths = Arrays.asList("AGENTS.md", "sessions", "chats.json");
        policy.setArchiveExcludePaths(excludePaths);

        Map<String, Object> map = policy.toMap();
        assertEquals("Archive", map.get("uploadMode"));
        assertEquals(excludePaths, map.get("archiveExcludePaths"));
    }

    @Test
    public void testUploadPolicyArchiveExcludePathsEmpty() {
        UploadPolicy policy = new UploadPolicy();
        policy.setUploadMode(UploadMode.ARCHIVE);

        Map<String, Object> map = policy.toMap();
        assertFalse("archiveExcludePaths should not be present when not set",
                    map.containsKey("archiveExcludePaths"));
    }

    @Test
    public void testUploadPolicyArchiveExcludePathsInSyncPolicy() throws Exception {
        UploadPolicy uploadPolicy = new UploadPolicy();
        uploadPolicy.setUploadMode(UploadMode.ARCHIVE);
        uploadPolicy.setArchiveExcludePaths(Arrays.asList("AGENTS.md", "sessions"));

        SyncPolicy syncPolicy = new SyncPolicy();
        syncPolicy.setUploadPolicy(uploadPolicy);

        Map<String, Object> map = syncPolicy.toMap();
        ObjectMapper objectMapper = new ObjectMapper();
        String json = objectMapper.writeValueAsString(map);

        assertTrue("JSON should contain archiveExcludePaths", json.contains("archiveExcludePaths"));
        assertTrue("JSON should contain AGENTS.md", json.contains("AGENTS.md"));
    }
}

