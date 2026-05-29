// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.NameInMap;
import com.aliyun.tea.TeaModel;

public class BindContextsRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("PersistenceDataList")
    public java.util.List<BindContextsRequestPersistenceDataList> persistenceDataList;

    @NameInMap("SessionId")
    public String sessionId;

    public static BindContextsRequest build(java.util.Map<String, ?> map) throws Exception {
        BindContextsRequest self = new BindContextsRequest();
        return TeaModel.build(map, self);
    }

    public BindContextsRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public BindContextsRequest setPersistenceDataList(java.util.List<BindContextsRequestPersistenceDataList> persistenceDataList) {
        this.persistenceDataList = persistenceDataList;
        return this;
    }
    public java.util.List<BindContextsRequestPersistenceDataList> getPersistenceDataList() {
        return this.persistenceDataList;
    }

    public BindContextsRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

    public static class BindContextsRequestPersistenceDataListMountConfig extends TeaModel {
        @NameInMap("AccessMode")
        public String accessMode;

        @NameInMap("StorageMode")
        public String storageMode;

        @NameInMap("ObjectKey")
        public String objectKey;

        @NameInMap("SourcePath")
        public String sourcePath;

        public static BindContextsRequestPersistenceDataListMountConfig build(java.util.Map<String, ?> map) throws Exception {
            BindContextsRequestPersistenceDataListMountConfig self = new BindContextsRequestPersistenceDataListMountConfig();
            return TeaModel.build(map, self);
        }

        public BindContextsRequestPersistenceDataListMountConfig setAccessMode(String accessMode) {
            this.accessMode = accessMode;
            return this;
        }
        public String getAccessMode() {
            return this.accessMode;
        }

        public BindContextsRequestPersistenceDataListMountConfig setStorageMode(String storageMode) {
            this.storageMode = storageMode;
            return this;
        }
        public String getStorageMode() {
            return this.storageMode;
        }

        public BindContextsRequestPersistenceDataListMountConfig setObjectKey(String objectKey) {
            this.objectKey = objectKey;
            return this;
        }
        public String getObjectKey() {
            return this.objectKey;
        }

        public BindContextsRequestPersistenceDataListMountConfig setSourcePath(String sourcePath) {
            this.sourcePath = sourcePath;
            return this;
        }
        public String getSourcePath() {
            return this.sourcePath;
        }
    }

    public static class BindContextsRequestPersistenceDataList extends TeaModel {
        @NameInMap("ContextId")
        public String contextId;

        @NameInMap("Path")
        public String path;

        @NameInMap("Policy")
        public String policy;

        @NameInMap("Type")
        public String type;

        @NameInMap("MountConfig")
        public BindContextsRequestPersistenceDataListMountConfig mountConfig;

        public static BindContextsRequestPersistenceDataList build(java.util.Map<String, ?> map) throws Exception {
            BindContextsRequestPersistenceDataList self = new BindContextsRequestPersistenceDataList();
            return TeaModel.build(map, self);
        }

        public BindContextsRequestPersistenceDataList setContextId(String contextId) {
            this.contextId = contextId;
            return this;
        }
        public String getContextId() {
            return this.contextId;
        }

        public BindContextsRequestPersistenceDataList setPath(String path) {
            this.path = path;
            return this;
        }
        public String getPath() {
            return this.path;
        }

        public BindContextsRequestPersistenceDataList setPolicy(String policy) {
            this.policy = policy;
            return this;
        }
        public String getPolicy() {
            return this.policy;
        }

        public BindContextsRequestPersistenceDataList setType(String type) {
            this.type = type;
            return this;
        }
        public String getType() {
            return this.type;
        }

        public BindContextsRequestPersistenceDataList setMountConfig(BindContextsRequestPersistenceDataListMountConfig mountConfig) {
            this.mountConfig = mountConfig;
            return this;
        }
        public BindContextsRequestPersistenceDataListMountConfig getMountConfig() {
            return this.mountConfig;
        }
    }

}
