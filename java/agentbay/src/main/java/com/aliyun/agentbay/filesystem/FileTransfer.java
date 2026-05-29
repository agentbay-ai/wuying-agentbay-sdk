package com.aliyun.agentbay.filesystem;

/**
 * Provides pre-signed URL upload/download functionality between local and OSS,
 * with integration to Session Context synchronization.
 * 
 * <p><strong>Prerequisites and Constraints:</strong></p>
 * <ul>
 * <li>Session must be associated with the corresponding context_id and path through
 * CreateSessionParams.context_syncs, and remote_path should fall within that
 * synchronization path (or conform to backend path rules).</li>
 * <li>Requires available AgentBay context service (agent_bay.context) and session context.</li>
 * </ul>
 */

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.context.ContextInfoResult;
import com.aliyun.agentbay.context.ContextService;
import com.aliyun.agentbay.context.ContextStatusData;
import com.aliyun.agentbay.context.ContextSyncResult;
import com.aliyun.agentbay.model.DownloadResult;
import com.aliyun.agentbay.model.FileUrlResult;
import com.aliyun.agentbay.model.UploadResult;
import com.aliyun.agentbay.session.Session;
import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

public class FileTransfer {
    private final AgentBay agentBay;
    private final ContextService contextService;
    private final Session session;
    private final int httpTimeout;
    private final boolean followRedirects;
    private String contextId;
    private String contextPath;

    private static final Set<String> FINISHED_STATES = new HashSet<>();

    static {
        FINISHED_STATES.add("success");
        FINISHED_STATES.add("successful");
        FINISHED_STATES.add("ok");
        FINISHED_STATES.add("finished");
        FINISHED_STATES.add("done");
        FINISHED_STATES.add("completed");
        FINISHED_STATES.add("complete");
    }

    private EnsureContextResult ensureContextId() {
        if (contextId != null) {
            return new EnsureContextResult(true, null);
        }

        try {
            com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextRequest request =
                new com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextRequest();
            request.setAuthorization("Bearer " + agentBay.getApiKey());
            request.setSessionId(session.getSessionId());
            java.util.List<String> contextTypes = new java.util.ArrayList<>();
            contextTypes.add("file_transfer");
            request.setContextTypes(contextTypes);
            com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextResponse response =
                agentBay.getApiClient().getClient().getAndLoadInternalContext(request);

            if (response == null || response.getBody() == null) {
                return new EnsureContextResult(false, "GetAndLoadInternalContext returned null response");
            }

            com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextResponseBody body = response.getBody();
            String requestId = body.getRequestId();
            if (body.getSuccess() == null || !body.getSuccess()) {
                String errorMsg = body.getMessage() != null ? body.getMessage() : "Unknown error";
                return new EnsureContextResult(false, errorMsg);
            }

            java.util.List<com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextResponseBody.GetAndLoadInternalContextResponseBodyData> dataList =
                body.getData();

            if (dataList != null && !dataList.isEmpty()) {
                for (com.aliyun.wuyingai20250506.models.GetAndLoadInternalContextResponseBody.GetAndLoadInternalContextResponseBodyData item : dataList) {
                    String ctxId = item.getContextId();
                    String ctxPath = item.getContextPath();

                    if (ctxId != null && !ctxId.isEmpty() && ctxPath != null && !ctxPath.isEmpty()) {
                        this.contextId = ctxId;
                        this.contextPath = ctxPath;
                        return new EnsureContextResult(true, null);
                    }
                }
            }
            return new EnsureContextResult(false, "Response contains no data");

        } catch (Exception e) {
            return new EnsureContextResult(false, "Failed to call GetAndLoadInternalContext: " + e.getMessage());
        }
    }

    public String getContextPath() {
        if (contextId == null) {
            ensureContextId();
        }
        return contextPath;
    }

    public FileTransfer(AgentBay agentBay, Session session) {
        this(agentBay, session, 60000, true);
    }

    public FileTransfer(AgentBay agentBay, Session session, int httpTimeout, boolean followRedirects) {
        this.agentBay = agentBay;
        this.contextService = agentBay.getContextService();
        this.session = session;
        this.httpTimeout = httpTimeout;
        this.followRedirects = followRedirects;
        this.contextId = null;
        this.contextPath = null;
    }

    public UploadResult upload(
        String localPath,
        String remotePath,
        String contentType,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        File localFile = new File(localPath);
        if (!localFile.isFile()) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Local file not found: " + localPath
            );
        }

        if (contextId == null) {
            EnsureContextResult ensureResult = ensureContextId();
            if (!ensureResult.success) {
                return new UploadResult(
                    "", false, null, null, null, null, 0, remotePath,
                    ensureResult.message
                );
            }
        }

        try {

            FileUrlResult urlResult = contextService.getFileUploadUrl(contextId, remotePath);
            if (!urlResult.isSuccess() || urlResult.getUrl() == null || urlResult.getUrl().isEmpty()) {
                return new UploadResult(
                    "", false, urlResult.getRequestId(), null, null, null, 0, remotePath,
                    "get_file_upload_url failed: " + urlResult.getErrorMessage()
                );
            }

            String uploadUrl = urlResult.getUrl();
            String reqIdUpload = urlResult.getRequestId();
            PutFileResult putResult = putFileSync(uploadUrl, localPath, contentType, progressCallback);
            if (putResult.statusCode != 200 && putResult.statusCode != 201 && putResult.statusCode != 204) {
                return new UploadResult(
                    "", false, reqIdUpload, null, putResult.statusCode, putResult.etag,
                    putResult.bytesSent, remotePath,
                    "Upload failed with HTTP " + putResult.statusCode
                );
            }
            String reqIdSync = awaitSync("download", remotePath, contextId);
            if (wait) {
                WaitResult waitResult = waitForTask(contextId, remotePath, "download", waitTimeout, pollInterval);
                if (!waitResult.success) {
                    return new UploadResult(
                        "", false, reqIdUpload, reqIdSync, putResult.statusCode, putResult.etag,
                        putResult.bytesSent, remotePath,
                        "Upload sync not finished: " + (waitResult.error != null ? waitResult.error : "timeout or unknown")
                    );
                }
            }
            return new UploadResult(
                "", true, reqIdUpload, reqIdSync, putResult.statusCode, putResult.etag,
                putResult.bytesSent, remotePath, null
            );

        } catch (Exception e) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Upload exception: " + e.getMessage()
            );
        }
    }

    public DownloadResult download(
        String remotePath,
        String localPath,
        boolean overwrite,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        if (contextId == null) {
            EnsureContextResult ensureResult = ensureContextId();
            if (!ensureResult.success) {
                return new DownloadResult(
                    "", false, null, null, null, 0, remotePath, localPath, null,
                    ensureResult.message
                );
            }
        }

        try {

            String reqIdSync = awaitSync("upload", remotePath, contextId);
            if (wait) {
                WaitResult waitResult = waitForTask(contextId, remotePath, "upload", waitTimeout, pollInterval);
                if (!waitResult.success) {
                    return new DownloadResult(
                        "", false, null, reqIdSync, null, 0, remotePath, localPath, null,
                        "Download sync not finished: " + (waitResult.error != null ? waitResult.error : "timeout or unknown")
                    );
                }
            }
            FileUrlResult urlResult = contextService.getFileDownloadUrl(contextId, remotePath);
            if (!urlResult.isSuccess() || urlResult.getUrl() == null || urlResult.getUrl().isEmpty()) {
                return new DownloadResult(
                    "", false, urlResult.getRequestId(), reqIdSync, null, 0, remotePath, localPath, null,
                    "get_file_download_url failed: " + urlResult.getErrorMessage()
                );
            }

            String downloadUrl = urlResult.getUrl();
            String reqIdDownload = urlResult.getRequestId();
            GetFileResult getResult = getFileSync(downloadUrl, localPath, progressCallback);
            if (getResult.statusCode != 200) {
                return new DownloadResult(
                    "", false, reqIdDownload, reqIdSync, getResult.statusCode,
                    getResult.bytesReceived, remotePath, localPath, null,
                    "Download failed with HTTP " + getResult.statusCode
                );
            }

            long actualFileSize = 0;
            if (localPath != null && !localPath.isEmpty()) {
                File downloadedFile = new File(localPath);
                actualFileSize = downloadedFile.exists() ? downloadedFile.length() : 0;
            }
            return new DownloadResult(
                "", true, reqIdDownload, reqIdSync, 200,
                actualFileSize, remotePath, localPath, null, null
            );

        } catch (Exception e) {
            return new DownloadResult(
                "", false, null, null, null, 0, remotePath, localPath, null,
                "Download exception: " + e.getMessage()
            );
        }
    }

    public UploadResult uploadBytes(
        byte[] content,
        String remotePath,
        String contentType,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        if (content == null) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Content cannot be null"
            );
        }

        if (contextId == null) {
            EnsureContextResult ensureResult = ensureContextId();
            if (!ensureResult.success) {
                return new UploadResult(
                    "", false, null, null, null, null, 0, remotePath,
                    ensureResult.message
                );
            }
        }

        try {

            FileUrlResult urlResult = contextService.getFileUploadUrl(contextId, remotePath);
            if (!urlResult.isSuccess() || urlResult.getUrl() == null || urlResult.getUrl().isEmpty()) {
                return new UploadResult(
                    "", false, urlResult.getRequestId(), null, null, null, 0, remotePath,
                    "get_file_upload_url failed: " + urlResult.getErrorMessage()
                );
            }

            String uploadUrl = urlResult.getUrl();
            String reqIdUpload = urlResult.getRequestId();
            PutFileBytesResult putResult = putFileBytesSync(uploadUrl, content, contentType, progressCallback);
            if (putResult.statusCode != 200 && putResult.statusCode != 201 && putResult.statusCode != 204) {
                return new UploadResult(
                    "", false, reqIdUpload, null, putResult.statusCode, putResult.etag,
                    putResult.bytesSent, remotePath,
                    "Upload failed with HTTP " + putResult.statusCode
                );
            }
            String reqIdSync = awaitSync("download", remotePath, contextId);
            if (wait) {
                WaitResult waitResult = waitForTask(contextId, remotePath, "download", waitTimeout, pollInterval);
                if (!waitResult.success) {
                    return new UploadResult(
                        "", false, reqIdUpload, reqIdSync, putResult.statusCode, putResult.etag,
                        putResult.bytesSent, remotePath,
                        "Upload sync not finished: " + (waitResult.error != null ? waitResult.error : "timeout or unknown")
                    );
                }
            }
            return new UploadResult(
                "", true, reqIdUpload, reqIdSync, putResult.statusCode, putResult.etag,
                putResult.bytesSent, remotePath, null
            );

        } catch (Exception e) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Upload exception: " + e.getMessage()
            );
        }
    }

    public DownloadResult downloadBytes(
        String remotePath,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        if (contextId == null) {
            EnsureContextResult ensureResult = ensureContextId();
            if (!ensureResult.success) {
                return new DownloadResult(
                    "", false, null, null, null, 0, remotePath, null, null,
                    ensureResult.message
                );
            }
        }

        try {

            String reqIdSync = awaitSync("upload", remotePath, contextId);
            if (wait) {
                WaitResult waitResult = waitForTask(contextId, remotePath, "upload", waitTimeout, pollInterval);
                if (!waitResult.success) {
                    return new DownloadResult(
                        "", false, null, reqIdSync, null, 0, remotePath, null, null,
                        "Download sync not finished: " + (waitResult.error != null ? waitResult.error : "timeout or unknown")
                    );
                }
            }
            FileUrlResult urlResult = contextService.getFileDownloadUrl(contextId, remotePath);
            if (!urlResult.isSuccess() || urlResult.getUrl() == null || urlResult.getUrl().isEmpty()) {
                return new DownloadResult(
                    "", false, urlResult.getRequestId(), reqIdSync, null, 0, remotePath, null, null,
                    "get_file_download_url failed: " + urlResult.getErrorMessage()
                );
            }

            String downloadUrl = urlResult.getUrl();
            String reqIdDownload = urlResult.getRequestId();
            GetFileBytesResult getResult = getFileBytesSync(downloadUrl, progressCallback);
            if (getResult.statusCode != 200) {
                return new DownloadResult(
                    "", false, reqIdDownload, reqIdSync, getResult.statusCode,
                    getResult.bytesReceived, remotePath, null, null,
                    "Download failed with HTTP " + getResult.statusCode
                );
            }
            return new DownloadResult(
                "", true, reqIdDownload, reqIdSync, 200,
                getResult.bytesReceived, remotePath, null, getResult.data, null
            );

        } catch (Exception e) {
            return new DownloadResult(
                "", false, null, null, null, 0, remotePath, null, null,
                "Download exception: " + e.getMessage()
            );
        }
    }

    private String awaitSync(String mode, String remotePath, String contextId) {
        ContextSyncResult result = session.getContext().sync(contextId, remotePath, mode);
        return result.getRequestId();
    }

    private String getDirectoryPath(String remotePath) {
        if (remotePath == null || remotePath.isEmpty()) {
            return "/";
        }
        int lastSlashIndex = remotePath.lastIndexOf('/');
        if (lastSlashIndex <= 0) {
            return "/";
        }
        return remotePath.substring(0, lastSlashIndex + 1);
    }

    private WaitResult waitForTask(
        String contextId,
        String remotePath,
        String taskType,
        float timeout,
        float interval
    ) {
        long deadline = System.currentTimeMillis() + (long) (timeout * 1000);
        String lastErr = null;

        while (System.currentTimeMillis() < deadline) {
            try {
                ContextInfoResult res = session.getContext().info(contextId, remotePath, taskType);
                List<ContextStatusData> statusList = res.getContextStatusData();

                for (ContextStatusData item : statusList) {
                    String cid = item.getContextId();
                    String path = item.getPath();
                    String ttype = item.getTaskType();
                    String status = item.getStatus();
                    String err = item.getErrorMessage();

                    if (contextId.equals(cid) && remotePath.equals(path) &&
                        (taskType == null || taskType.equals(ttype))) {
                        if (err != null && !err.isEmpty()) {
                            return new WaitResult(false, "Task error: " + err);
                        }
                        if (status != null && FINISHED_STATES.contains(status.toLowerCase())) {
                            return new WaitResult(true, null);
                        }
                    }
                }

                lastErr = "task not finished";
            } catch (Exception e) {
                lastErr = "info error: " + e.getMessage();
            }

            try {
                Thread.sleep((long) (interval * 1000));
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                return new WaitResult(false, "Interrupted");
            }
        }

        return new WaitResult(false, lastErr != null ? lastErr : "timeout");
    }

    private PutFileResult putFileSync(String url, String filePath, String contentType, ProgressCallback progressCallback) throws IOException {
        File file = new File(filePath);
        long fileSize = file.length();

        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("PUT");
        conn.setDoOutput(true);
        conn.setConnectTimeout(httpTimeout);
        conn.setReadTimeout(httpTimeout);
        conn.setInstanceFollowRedirects(followRedirects);

        if (contentType != null && !contentType.isEmpty()) {
            conn.setRequestProperty("Content-Type", contentType);
        }

        long bytesSent = 0;
        try (FileInputStream fis = new FileInputStream(file);
             OutputStream os = conn.getOutputStream()) {
            byte[] buffer = new byte[8192];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                os.write(buffer, 0, bytesRead);
                bytesSent += bytesRead;
                if (progressCallback != null) {
                    try {
                        progressCallback.onProgress(bytesSent);
                    } catch (Exception e) {
                    }
                }
            }
        }

        int statusCode = conn.getResponseCode();
        String etag = conn.getHeaderField("ETag");

        conn.disconnect();
        return new PutFileResult(statusCode, etag, fileSize);
    }

    private GetFileResult getFileSync(String url, String destPath, ProgressCallback progressCallback) throws IOException {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(httpTimeout);
        conn.setReadTimeout(httpTimeout);
        conn.setInstanceFollowRedirects(followRedirects);

        int statusCode = conn.getResponseCode();
        long bytesReceived = 0;

        if (statusCode == 200) {
            if (destPath != null && !destPath.isEmpty()) {
                File destFile = new File(destPath);
                File parentDir = destFile.getParentFile();
                if (parentDir != null && !parentDir.exists()) {
                    parentDir.mkdirs();
                }

                try (InputStream is = conn.getInputStream();
                     BufferedOutputStream bos = new BufferedOutputStream(new FileOutputStream(destPath))) {
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = is.read(buffer)) != -1) {
                        bos.write(buffer, 0, bytesRead);
                        bytesReceived += bytesRead;
                        if (progressCallback != null) {
                            try {
                                progressCallback.onProgress(bytesReceived);
                            } catch (Exception e) {
                            }
                        }
                    }
                }
            } else {
                try (InputStream is = conn.getInputStream()) {
                    byte[] buffer = new byte[8192];
                    int bytesRead;
                    while ((bytesRead = is.read(buffer)) != -1) {
                        bytesReceived += bytesRead;
                    }
                }
            }
        }

        conn.disconnect();
        return new GetFileResult(statusCode, bytesReceived);
    }

    private PutFileBytesResult putFileBytesSync(String url, byte[] content, String contentType, ProgressCallback progressCallback) throws IOException {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("PUT");
        conn.setDoOutput(true);
        conn.setConnectTimeout(httpTimeout);
        conn.setReadTimeout(httpTimeout);
        conn.setInstanceFollowRedirects(followRedirects);

        if (contentType != null && !contentType.isEmpty()) {
            conn.setRequestProperty("Content-Type", contentType);
        }

        long bytesSent = 0;
        try (OutputStream os = conn.getOutputStream()) {
            os.write(content);
            bytesSent = content.length;
            if (progressCallback != null) {
                try {
                    progressCallback.onProgress(bytesSent);
                } catch (Exception e) {
                }
            }
        }

        int statusCode = conn.getResponseCode();
        String etag = conn.getHeaderField("ETag");

        conn.disconnect();
        return new PutFileBytesResult(statusCode, etag, bytesSent);
    }

    private GetFileBytesResult getFileBytesSync(String url, ProgressCallback progressCallback) throws IOException {
        HttpURLConnection conn = (HttpURLConnection) new URL(url).openConnection();
        conn.setRequestMethod("GET");
        conn.setConnectTimeout(httpTimeout);
        conn.setReadTimeout(httpTimeout);
        conn.setInstanceFollowRedirects(followRedirects);

        int statusCode = conn.getResponseCode();
        byte[] data = null;
        long bytesReceived = 0;

        if (statusCode == 200) {
            try (InputStream is = conn.getInputStream();
                 ByteArrayOutputStream baos = new ByteArrayOutputStream()) {
                byte[] buffer = new byte[8192];
                int bytesRead;
                while ((bytesRead = is.read(buffer)) != -1) {
                    baos.write(buffer, 0, bytesRead);
                    bytesReceived += bytesRead;
                    if (progressCallback != null) {
                        try {
                            progressCallback.onProgress(bytesReceived);
                        } catch (Exception e) {
                        }
                    }
                }
                data = baos.toByteArray();
            }
        }

        conn.disconnect();
        return new GetFileBytesResult(statusCode, bytesReceived, data);
    }

    private static class PutFileResult {
        int statusCode;
        String etag;
        long bytesSent;

        PutFileResult(int statusCode, String etag, long bytesSent) {
            this.statusCode = statusCode;
            this.etag = etag;
            this.bytesSent = bytesSent;
        }
    }

    private static class GetFileResult {
        int statusCode;
        long bytesReceived;

        GetFileResult(int statusCode, long bytesReceived) {
            this.statusCode = statusCode;
            this.bytesReceived = bytesReceived;
        }
    }

    private static class EnsureContextResult {
        boolean success;
        String message;

        EnsureContextResult(boolean success, String message) {
            this.success = success;
            this.message = message;
        }
    }

    private static class WaitResult {
        boolean success;
        String error;

        WaitResult(boolean success, String error) {
            this.success = success;
            this.error = error;
        }
    }

    private static class PutFileBytesResult {
        int statusCode;
        String etag;
        long bytesSent;

        PutFileBytesResult(int statusCode, String etag, long bytesSent) {
            this.statusCode = statusCode;
            this.etag = etag;
            this.bytesSent = bytesSent;
        }
    }

    private static class GetFileBytesResult {
        int statusCode;
        long bytesReceived;
        byte[] data;

        GetFileBytesResult(int statusCode, long bytesReceived, byte[] data) {
            this.statusCode = statusCode;
            this.bytesReceived = bytesReceived;
            this.data = data;
        }
    }
}
