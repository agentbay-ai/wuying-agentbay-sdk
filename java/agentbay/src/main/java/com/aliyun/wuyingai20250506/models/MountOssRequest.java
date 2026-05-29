// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class MountOssRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("OssMountConfigs")
    public java.util.List<MountOssRequestOssMountConfigs> ossMountConfigs;

    @NameInMap("SessionId")
    public String sessionId;

    @NameInMap("FsType")
    public String fsType;

    public static MountOssRequest build(java.util.Map<String, ?> map) throws Exception {
        MountOssRequest self = new MountOssRequest();
        return TeaModel.build(map, self);
    }

    public MountOssRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public MountOssRequest setOssMountConfigs(java.util.List<MountOssRequestOssMountConfigs> ossMountConfigs) {
        this.ossMountConfigs = ossMountConfigs;
        return this;
    }
    public java.util.List<MountOssRequestOssMountConfigs> getOssMountConfigs() {
        return this.ossMountConfigs;
    }

    public MountOssRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

    public MountOssRequest setFsType(String fsType) {
        this.fsType = fsType;
        return this;
    }
    public String getFsType() {
        return this.fsType;
    }

    public static class MountOssRequestOssMountConfigs extends TeaModel {
        @NameInMap("Bucket")
        public String bucket;

        @NameInMap("Endpoint")
        public String endpoint;

        @NameInMap("ObjectKey")
        public String objectKey;

        @NameInMap("OtherOpts")
        public String otherOpts;

        @NameInMap("ReadOnly")
        public Boolean readOnly;

        @NameInMap("TargetPath")
        public String targetPath;

        public static MountOssRequestOssMountConfigs build(java.util.Map<String, ?> map) throws Exception {
            MountOssRequestOssMountConfigs self = new MountOssRequestOssMountConfigs();
            return TeaModel.build(map, self);
        }

        public MountOssRequestOssMountConfigs setBucket(String bucket) {
            this.bucket = bucket;
            return this;
        }
        public String getBucket() {
            return this.bucket;
        }

        public MountOssRequestOssMountConfigs setEndpoint(String endpoint) {
            this.endpoint = endpoint;
            return this;
        }
        public String getEndpoint() {
            return this.endpoint;
        }

        public MountOssRequestOssMountConfigs setObjectKey(String objectKey) {
            this.objectKey = objectKey;
            return this;
        }
        public String getObjectKey() {
            return this.objectKey;
        }

        public MountOssRequestOssMountConfigs setOtherOpts(String otherOpts) {
            this.otherOpts = otherOpts;
            return this;
        }
        public String getOtherOpts() {
            return this.otherOpts;
        }

        public MountOssRequestOssMountConfigs setReadOnly(Boolean readOnly) {
            this.readOnly = readOnly;
            return this;
        }
        public Boolean getReadOnly() {
            return this.readOnly;
        }

        public MountOssRequestOssMountConfigs setTargetPath(String targetPath) {
            this.targetPath = targetPath;
            return this;
        }
        public String getTargetPath() {
            return this.targetPath;
        }

    }

}
