import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.ContextFileListResult;
import com.aliyun.agentbay.context.ContextInfoResult;
import com.aliyun.agentbay.context.ContextResult;
import com.aliyun.agentbay.context.ContextSync;
import com.aliyun.agentbay.context.ContextSyncResult;
import com.aliyun.agentbay.context.FileInfo;
import com.aliyun.agentbay.context.SyncPolicy;
import com.aliyun.agentbay.context.UploadMode;
import com.aliyun.agentbay.context.UploadPolicy;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.model.BoolResult;
import com.aliyun.agentbay.model.DeleteResult;
import com.aliyun.agentbay.model.SessionResult;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.Arrays;
import java.util.HashMap;
import java.util.Map;

/**
 * Examples for {@link UploadMode#ARCHIVE}: standard archive upload and hybrid storage using
 * {@code archiveExcludePaths} (some paths uploaded as individual files while the rest are archived).
 *
 * <p>Build the {@code agentbay} module first, then compile this file with the module classpath
 * (see README in this directory).</p>
 */
public class ArchiveUploadModeExample {

    public static void main(String[] args) {
        AgentBay agentBay;
        try {
            agentBay = new AgentBay();
        } catch (AgentBayException e) {
            System.err.println("Failed to create AgentBay client: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        String uniqueId = String.valueOf(System.currentTimeMillis());
        System.out.println("🚀 AgentBay Archive Upload Mode Examples");
        System.out.println("============================================================");

        demonstrateBasicArchiveUpload(agentBay, uniqueId);
        demonstrateArchiveExcludePaths(agentBay, uniqueId);

        System.out.println("\n✅ Archive upload mode examples completed");
    }

    private static void demonstrateBasicArchiveUpload(AgentBay agentBay, String uniqueId) {
        System.out.println("\n📦 === Basic Archive Upload Mode ===");
        Session session = null;
        String contextId = null;
        String syncPath = "/tmp/archive-mode-java-" + uniqueId;

        try {
            String contextName = "archive-mode-context-java-" + uniqueId;
            ContextResult ctxRes = agentBay.getContext().get(contextName, true);
            if (!ctxRes.isSuccess()) {
                System.err.println("Context error: " + ctxRes.getErrorMessage());
                return;
            }
            contextId = ctxRes.getContextId();
            System.out.println("✅ Context ID: " + contextId);

            UploadPolicy uploadPolicy = new UploadPolicy();
            uploadPolicy.setUploadMode(UploadMode.ARCHIVE);
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            syncPolicy.setUploadPolicy(uploadPolicy);

            CreateSessionParams params = new CreateSessionParams();
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "archive-mode-java-" + uniqueId);
            labels.put("type", "archive-upload-demo");
            labels.put("uploadMode", "Archive");
            params.setLabels(labels);
            params.setContextSyncs(Arrays.asList(ContextSync.create(contextId, syncPath, syncPolicy)));

            SessionResult createResult = agentBay.create(params);
            if (!createResult.isSuccess() || createResult.getSession() == null) {
                System.err.println("create failed: " + createResult.getErrorMessage());
                return;
            }
            session = createResult.getSession();
            System.out.println("✅ Session ID: " + session.getSessionId());

            int contentSize = 5 * 1024;
            String base = "Archive mode test successful! This is a test file created in the session path. ";
            StringBuilder sb = new StringBuilder();
            while (sb.length() < contentSize) {
                sb.append(base);
            }
            String fileContent = sb.substring(0, contentSize);
            String filePath = syncPath + "/test-file-5kb.txt";

            BoolResult write = session.getFileSystem().writeFile(filePath, fileContent, "overwrite");
            if (!write.isSuccess()) {
                throw new IllegalStateException("write failed: " + write.getErrorMessage());
            }
            System.out.println("✅ Wrote " + filePath + " (" + contentSize + " bytes)");

            ContextSyncResult syncResult = session.getContext().sync();
            if (!syncResult.isSuccess()) {
                throw new IllegalStateException("sync failed: " + syncResult.getErrorMessage());
            }
            System.out.println("✅ Context sync requestId: " + syncResult.getRequestId());

            ContextInfoResult infoResult = session.getContext().info();
            if (!infoResult.isSuccess()) {
                throw new IllegalStateException("info failed: " + infoResult.getErrorMessage());
            }
            System.out.println("✅ Context info entries: " + infoResult.getContextStatusData().size());

            ContextFileListResult listResult =
                agentBay.getContext().listFiles(contextId, syncPath, 10, null);
            if (!listResult.isSuccess()) {
                throw new IllegalStateException("listFiles failed: " + listResult.getErrorMessage());
            }
            System.out.println("✅ Listed " + listResult.getEntries().size() + " entries");
            if (listResult.getNextToken() != null && !listResult.getNextToken().isEmpty()) {
                System.out.println("   nextToken present for further pages");
            }
            for (int i = 0; i < listResult.getEntries().size(); i++) {
                FileInfo e = listResult.getEntries().get(i);
                System.out.println(
                    "   [" + i + "] " + e.getFilePath() + " (" + e.getFileName() + ", " + e.getSize() + " bytes)");
            }

            System.out.println("\n🎉 Basic archive upload demo finished.");
        } catch (IllegalStateException e) {
            System.err.println(e.getMessage());
        } catch (AgentBayException e) {
            System.err.println("AgentBay error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (session != null) {
                System.out.println("\n🧹 Deleting session (basic demo)...");
                try {
                    DeleteResult del = agentBay.delete(session, true);
                    System.out.println("delete success=" + del.isSuccess() + ", requestId=" + del.getRequestId());
                } catch (Exception e) {
                    System.err.println("delete failed: " + e.getMessage());
                }
            }
        }
    }

    private static void demonstrateArchiveExcludePaths(AgentBay agentBay, String uniqueId) {
        System.out.println("\n📂 === Archive Mode with archiveExcludePaths (hybrid storage) ===");
        Session session = null;
        String contextId = null;
        String syncPath = "/tmp/archive-exclude-java-" + uniqueId;

        try {
            String contextName = "archive-exclude-context-java-" + uniqueId;
            ContextResult ctxRes = agentBay.getContext().get(contextName, true);
            if (!ctxRes.isSuccess()) {
                System.err.println("Context error: " + ctxRes.getErrorMessage());
                return;
            }
            contextId = ctxRes.getContextId();
            System.out.println("✅ Context ID: " + contextId);

            UploadPolicy uploadPolicy = new UploadPolicy();
            uploadPolicy.setUploadMode(UploadMode.ARCHIVE);
            uploadPolicy.setArchiveExcludePaths(Arrays.asList("important/", "config.json"));
            SyncPolicy syncPolicy = SyncPolicy.defaultPolicy();
            syncPolicy.setUploadPolicy(uploadPolicy);

            System.out.println("✅ archiveExcludePaths: " + uploadPolicy.getArchiveExcludePaths());

            CreateSessionParams params = new CreateSessionParams();
            Map<String, String> labels = new HashMap<>();
            labels.put("example", "archive-exclude-java-" + uniqueId);
            labels.put("type", "archive-exclude-demo");
            labels.put("uploadMode", "Archive");
            params.setLabels(labels);
            params.setContextSyncs(Arrays.asList(ContextSync.create(contextId, syncPath, syncPolicy)));

            SessionResult createResult = agentBay.create(params);
            if (!createResult.isSuccess() || createResult.getSession() == null) {
                System.err.println("create failed: " + createResult.getErrorMessage());
                return;
            }
            session = createResult.getSession();
            System.out.println("✅ Session ID: " + session.getSessionId());

            BoolResult d1 = session.getFileSystem().createDirectory(syncPath + "/important");
            if (!d1.isSuccess()) {
                throw new IllegalStateException("mkdir important: " + d1.getErrorMessage());
            }
            BoolResult d2 = session.getFileSystem().createDirectory(syncPath + "/regular");
            if (!d2.isSuccess()) {
                throw new IllegalStateException("mkdir regular: " + d2.getErrorMessage());
            }

            BoolResult w1 = session.getFileSystem().writeFile(
                syncPath + "/important/data.txt",
                "Excluded path: stored individually when possible."
            );
            if (!w1.isSuccess()) {
                throw new IllegalStateException("write important/data.txt: " + w1.getErrorMessage());
            }

            BoolResult w2 = session.getFileSystem().writeFile(
                syncPath + "/config.json",
                "{\"key\":\"value\"}"
            );
            if (!w2.isSuccess()) {
                throw new IllegalStateException("write config.json: " + w2.getErrorMessage());
            }

            BoolResult w3 = session.getFileSystem().writeFile(
                syncPath + "/regular/data.txt",
                "Regular path: eligible for bulk archive packaging."
            );
            if (!w3.isSuccess()) {
                throw new IllegalStateException("write regular/data.txt: " + w3.getErrorMessage());
            }

            ContextSyncResult syncResult = session.getContext().sync();
            if (!syncResult.isSuccess()) {
                throw new IllegalStateException("sync failed: " + syncResult.getErrorMessage());
            }
            System.out.println("✅ Context sync requestId: " + syncResult.getRequestId());

            ContextFileListResult listResult =
                agentBay.getContext().listFiles(contextId, syncPath, 20, null);
            if (!listResult.isSuccess()) {
                throw new IllegalStateException("listFiles failed: " + listResult.getErrorMessage());
            }
            System.out.println("✅ Listed " + listResult.getEntries().size() + " entries");
            for (int i = 0; i < listResult.getEntries().size(); i++) {
                FileInfo e = listResult.getEntries().get(i);
                System.out.println(
                    "   [" + i + "] " + e.getFilePath() + " (" + e.getFileName() + ", " + e.getSize() + " bytes)");
            }

            System.out.println("\n🎉 archiveExcludePaths demo finished.");
        } catch (IllegalStateException e) {
            System.err.println(e.getMessage());
        } catch (AgentBayException e) {
            System.err.println("AgentBay error: " + e.getMessage());
            e.printStackTrace();
        } finally {
            if (session != null) {
                System.out.println("\n🧹 Deleting session (exclude-paths demo)...");
                try {
                    DeleteResult del = agentBay.delete(session, true);
                    System.out.println("delete success=" + del.isSuccess() + ", requestId=" + del.getRequestId());
                } catch (Exception e) {
                    System.err.println("delete failed: " + e.getMessage());
                }
            }
        }
    }
}
