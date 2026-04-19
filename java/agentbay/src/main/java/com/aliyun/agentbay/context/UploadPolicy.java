package com.aliyun.agentbay.context;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Defines the upload policy for context synchronization
 * 
 * Attributes:
 *     autoUpload: Enables automatic upload
 *     uploadStrategy: Defines the upload strategy
 *     uploadMode: Defines the upload mode (UploadMode.FILE or UploadMode.ARCHIVE)
 *     period: Upload period in seconds (default: 30)
 *     archiveExcludePaths: When uploadMode is ARCHIVE, paths to upload as individual files
 */
public class UploadPolicy {
    private boolean autoUpload = true;
    private UploadStrategy uploadStrategy = UploadStrategy.UPLOAD_BEFORE_RESOURCE_RELEASE;
    private UploadMode uploadMode = UploadMode.FILE;
    private Integer period = 30;
    private List<String> archiveExcludePaths;

    public UploadPolicy() {
    }

    public UploadPolicy(boolean autoUpload, UploadStrategy uploadStrategy, Integer period) {
        this.autoUpload = autoUpload;
        this.uploadStrategy = uploadStrategy;
        this.period = period;
        this.uploadMode = UploadMode.FILE;
    }

    public UploadPolicy(boolean autoUpload, UploadStrategy uploadStrategy, UploadMode uploadMode, Integer period) {
        this.autoUpload = autoUpload;
        this.uploadStrategy = uploadStrategy;
        this.uploadMode = uploadMode;
        this.period = period;
    }

    public static UploadPolicy defaultPolicy() {
        return new UploadPolicy();
    }

    public boolean isAutoUpload() {
        return autoUpload;
    }

    public void setAutoUpload(boolean autoUpload) {
        this.autoUpload = autoUpload;
    }

    public UploadStrategy getUploadStrategy() {
        return uploadStrategy;
    }

    public void setUploadStrategy(UploadStrategy uploadStrategy) {
        this.uploadStrategy = uploadStrategy;
    }

    public Integer getPeriod() {
        return period;
    }

    public void setPeriod(Integer period) {
        this.period = period;
    }

    public UploadMode getUploadMode() {
        return uploadMode;
    }

    public void setUploadMode(UploadMode uploadMode) {
        this.uploadMode = uploadMode;
    }

    public List<String> getArchiveExcludePaths() {
        return archiveExcludePaths;
    }

    public void setArchiveExcludePaths(List<String> archiveExcludePaths) {
        this.archiveExcludePaths = archiveExcludePaths;
    }

    public Map<String, Object> toMap() {
        Map<String, Object> map = new HashMap<>();
        map.put("autoUpload", autoUpload);
        map.put("uploadStrategy", uploadStrategy != null ? uploadStrategy.getValue() : null);
        map.put("uploadMode", uploadMode != null ? uploadMode.getValue() : null);
        map.put("period", period);
        if (archiveExcludePaths != null && !archiveExcludePaths.isEmpty()
                && uploadMode == UploadMode.ARCHIVE) {
            map.put("archiveExcludePaths", archiveExcludePaths);
        }
        return map;
    }
}