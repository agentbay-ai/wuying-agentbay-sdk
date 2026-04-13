package com.aliyun.agentbay.test;

import com.aliyun.agentbay.context.BWList;
import com.aliyun.agentbay.context.DeletePolicy;
import com.aliyun.agentbay.context.DownloadPolicy;
import com.aliyun.agentbay.context.SyncPolicy;
import com.aliyun.agentbay.context.UploadPolicy;
import com.aliyun.agentbay.context.WhiteList;
import org.junit.Test;

import java.util.Arrays;
import java.util.List;
import java.util.Map;

import static org.junit.Assert.*;

/**
 * Unit tests for WhiteList regex path and exclude pattern validation,
 * aligned with Python test_whitelist_regex_path_and_exclude.
 */
public class contextSyncTest {

    @Test
    public void testWhiteListRegexPathAndExclude() {
        // ── Construction: both regex flags enabled ────────────────────────────
        WhiteList wl = new WhiteList(
            "project-.*",
            Arrays.asList("cache.*", "下载.*"),
            true,
            true
        );
        assertEquals("project-.*", wl.getPath());
        assertTrue(wl.isPathRegex());
        assertEquals(Arrays.asList("cache.*", "下载.*"), wl.getExcludePaths());
        assertTrue(wl.isExcludeRegex());

        // ── Serialization ────────────────────────────────────────────────────
        Map<String, Object> map = wl.toMap();
        assertEquals("project-.*", map.get("path"));
        assertTrue((Boolean) map.get("isPathRegex"));
        assertEquals(Arrays.asList("cache.*", "下载.*"), map.get("excludePaths"));
        assertTrue((Boolean) map.get("isExcludeRegex"));

        // ── Wildcard in regex path is allowed ─────────────────────────────────
        WhiteList wlRegexPath = new WhiteList("/home/wuying/.*", null, true, false);
        assertEquals("/home/wuying/.*", wlRegexPath.getPath());

        // ── Wildcard in regex excludePaths is allowed ────────────────────────
        WhiteList wlRegexExclude = new WhiteList(
            "/home/wuying", Arrays.asList("record.*"), false, true
        );
        assertEquals(Arrays.asList("record.*"), wlRegexExclude.getExcludePaths());

        // ── Wildcard in path raises when isPathRegex=false ──────────────────
        try {
            new WhiteList("/home/wuying/*", null, false, false);
            fail("Expected IllegalArgumentException for wildcard in path with isPathRegex=false");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("isPathRegex=false"));
        }

        // ── Wildcard in excludePaths raises when isExcludeRegex=false ──────
        try {
            new WhiteList("/home/wuying", Arrays.asList("/invalid/*"), false, false);
            fail("Expected IllegalArgumentException for wildcard in excludePaths with isExcludeRegex=false");
        } catch (IllegalArgumentException e) {
            assertTrue(e.getMessage().contains("isExcludeRegex=false"));
        }

        // ── Integration in SyncPolicy ─────────────────────────────────────────
        WhiteList wlForPolicy = new WhiteList(
            "project-.*",
            Arrays.asList("cache.*"),
            true,
            true
        );
        SyncPolicy syncPolicy = new SyncPolicy();
        syncPolicy.setBwList(new BWList(Arrays.asList(wlForPolicy)));

        List<WhiteList> whiteLists = syncPolicy.getBwList().getWhiteLists();
        assertEquals(1, whiteLists.size());
        WhiteList entry = whiteLists.get(0);
        assertEquals("project-.*", entry.getPath());
        assertTrue(entry.isPathRegex());
        assertEquals(Arrays.asList("cache.*"), entry.getExcludePaths());
        assertTrue(entry.isExcludeRegex());

        Map<String, Object> policyMap = syncPolicy.getBwList().toMap();
        @SuppressWarnings("unchecked")
        List<Map<String, Object>> wlMaps = (List<Map<String, Object>>) policyMap.get("whiteLists");
        assertEquals(1, wlMaps.size());
        Map<String, Object> wlMap = wlMaps.get(0);
        assertEquals("project-.*", wlMap.get("path"));
        assertTrue((Boolean) wlMap.get("isPathRegex"));
        assertEquals(Arrays.asList("cache.*"), wlMap.get("excludePaths"));
        assertTrue((Boolean) wlMap.get("isExcludeRegex"));
    }

    @Test
    public void testSyncPolicyWithAllParameters() {
        // Aligned with Python test_sync_policy_with_all_parameters
        UploadPolicy uploadPolicy = new UploadPolicy(false,
            com.aliyun.agentbay.context.UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE, null);
        DownloadPolicy downloadPolicy = new DownloadPolicy(false,
            com.aliyun.agentbay.context.DownloadStrategy.DOWNLOAD_ASYNC);
        DeletePolicy deletePolicy = new DeletePolicy(false);
        BWList bwList = new BWList(Arrays.asList(
            new WhiteList("/test", Arrays.asList("/exclude"))
        ));

        SyncPolicy syncPolicy = new SyncPolicy(uploadPolicy, downloadPolicy, deletePolicy, null, bwList);

        // Verify all policies are set correctly
        assertFalse(syncPolicy.getUploadPolicy().isAutoUpload());
        assertFalse(syncPolicy.getDownloadPolicy().isAutoDownload());
        assertFalse(syncPolicy.getDeletePolicy().isSyncLocalFile());

        List<WhiteList> whiteLists = syncPolicy.getBwList().getWhiteLists();
        assertEquals(1, whiteLists.size());
        assertEquals("/test", whiteLists.get(0).getPath());
        assertEquals(Arrays.asList("/exclude"), whiteLists.get(0).getExcludePaths());
        assertFalse(whiteLists.get(0).isPathRegex());
        assertFalse(whiteLists.get(0).isExcludeRegex());
    }
}
