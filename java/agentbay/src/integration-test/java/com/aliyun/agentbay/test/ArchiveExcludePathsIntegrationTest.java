package com.aliyun.agentbay.test;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.*;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.FileUrlResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;
import org.junit.BeforeClass;
import org.junit.Test;

import java.util.Arrays;

import static org.junit.Assert.*;

/**
 * Integration test for Archive upload mode with archiveExcludePaths (hybrid storage).
 */
public class ArchiveExcludePathsIntegrationTest {

    private static AgentBay agentBay;

    @BeforeClass
    public static void setUpClass() throws AgentBayException {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        String ci = System.getenv("CI");
        if (apiKey == null || apiKey.trim().isEmpty() || "true".equals(ci)) {
            throw new IllegalStateException(
                "Skipping integration test: No API key available or running in CI"
            );
        }
        agentBay = new AgentBay();
    }

    @Test
    public void testArchiveModeWithExcludePaths() throws Exception {
        String contextName = "archive-exclude-java-" + System.currentTimeMillis();
        ContextResult contextResult = agentBay.getContext().get(contextName, true);
        assertTrue("Error getting/creating context", contextResult.isSuccess());
        assertNotNull("Context should not be null", contextResult.getContext());

        Context context = contextResult.getContext();
        String contextId = context.getId();
        Session session = null;

        try {
            long timestamp = System.currentTimeMillis();
            String syncPath = "/home/wuying/archive-exclude-java-" + timestamp;

            UploadPolicy uploadPolicy = new UploadPolicy();
            uploadPolicy.setUploadMode(UploadMode.ARCHIVE);
            uploadPolicy.setArchiveExcludePaths(Arrays.asList("important/", "config.json"));

            SyncPolicy syncPolicy = new SyncPolicy(
                uploadPolicy,
                DownloadPolicy.defaultPolicy(),
                DeletePolicy.defaultPolicy(),
                ExtractPolicy.defaultPolicy(),
                null,
                null
            );

            CreateSessionParams sessionParams = new CreateSessionParams();
            ContextSync contextSync = ContextSync.create(contextId, syncPath, syncPolicy);
            sessionParams.setContextSyncs(Arrays.asList(contextSync));
            sessionParams.setImageId("linux_latest");

            SessionResult sessionResult = agentBay.create(sessionParams);
            assertTrue("Error creating session", sessionResult.isSuccess());
            assertNotNull("Session should not be null", sessionResult.getSession());
            session = sessionResult.getSession();

            BoolResult dirImportant = session.getFileSystem().createDirectory(syncPath + "/important");
            assertTrue("Error creating important directory", dirImportant.isSuccess());
            BoolResult dirRegular = session.getFileSystem().createDirectory(syncPath + "/regular");
            assertTrue("Error creating regular directory", dirRegular.isSuccess());

            BoolResult writeImportant = session.getFileSystem().writeFile(
                syncPath + "/important/data.txt",
                "This file should be stored individually via FILE mode"
            );
            assertTrue("Error writing important/data.txt", writeImportant.isSuccess());

            BoolResult writeConfig = session.getFileSystem().writeFile(
                syncPath + "/config.json",
                "{\"key\": \"value\", \"setting\": true}"
            );
            assertTrue("Error writing config.json", writeConfig.isSuccess());

            BoolResult writeRegular = session.getFileSystem().writeFile(
                syncPath + "/regular/data.txt",
                "This file should be archived with the rest"
            );
            assertTrue("Error writing regular/data.txt", writeRegular.isSuccess());

            DeleteResult deleteResult = agentBay.delete(session, true);
            assertTrue("Error deleting session with sync", deleteResult.isSuccess());
            session = null;

            ContextFileListResult listResult = agentBay.getContext().listFiles(
                contextId,
                syncPath,
                1,
                20
            );
            assertTrue("listFiles should succeed", listResult.isSuccess());
            assertNotNull("listFiles entries should not be null", listResult.getEntries());
            assertFalse("Should have files after sync", listResult.getEntries().isEmpty());

            System.out.println("Total files listed: " + listResult.getEntries().size());
            for (FileInfo entry : listResult.getEntries()) {
                System.out.println(
                    "  "
                        + entry.getFilePath()
                        + " | "
                        + entry.getFileName()
                        + " ("
                        + entry.getFileType()
                        + ", "
                        + entry.getSize()
                        + " bytes)"
                );
            }

            boolean hasImportant = false;
            boolean hasConfig = false;
            for (FileInfo entry : listResult.getEntries()) {
                String fp = entry.getFilePath();
                String fn = entry.getFileName();
                if (fp != null && fp.contains("important")) {
                    hasImportant = true;
                }
                if (fn != null && fn.contains("config.json")) {
                    hasConfig = true;
                }
                if (fp != null && fp.contains("config.json")) {
                    hasConfig = true;
                }
            }

            System.out.println("Has excluded 'important/' files individually: " + hasImportant);
            System.out.println("Has excluded 'config.json' individually: " + hasConfig);

            assertTrue("Expected entries referencing important/ as individual files (archiveExcludePaths)", hasImportant);
            assertTrue("Expected config.json as individual file in listing (archiveExcludePaths)", hasConfig);

            for (FileInfo entry : listResult.getEntries()) {
                String fp = entry.getFilePath();
                String fn = entry.getFileName();
                boolean excluded = (fp != null && fp.contains("important"))
                    || (fn != null && "config.json".equals(fn))
                    || (fp != null && fp.contains("config.json"));
                if (!excluded) {
                    continue;
                }
                try {
                    FileUrlResult urlResult = agentBay.getContext().getFileDownloadUrl(
                        contextId,
                        entry.getFilePath()
                    );
                    if (urlResult.isSuccess() && urlResult.getUrl() != null && !urlResult.getUrl().isEmpty()) {
                        String url = urlResult.getUrl();
                        int max = Math.min(url.length(), 80);
                        System.out.println(
                            "  Excluded file '"
                                + entry.getFileName()
                                + "' download URL (truncated): "
                                + url.substring(0, max)
                                + (url.length() > max ? "..." : "")
                        );
                    } else {
                        System.out.println(
                            "  Excluded file '"
                                + entry.getFileName()
                                + "' — no download URL from API ("
                                + urlResult.getErrorMessage()
                                + ")"
                        );
                    }
                } catch (AgentBayException e) {
                    System.out.println(
                        "  getFileDownloadUrl failed for '"
                            + entry.getFileName()
                            + "': "
                            + e.getMessage()
                    );
                }
            }
        } finally {
            if (session != null) {
                try {
                    agentBay.delete(session, true);
                } catch (Exception e) {
                }
            }
            try {
                agentBay.getContext().delete(context);
            } catch (Exception e) {
            }
        }
    }
}
