// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class CreateMcpSessionRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("ContextId")
    public String contextId;

    @NameInMap("DirectLink")
    public Boolean directLink;

    /**
     * <strong>if can be null:</strong>
     * <p>false</p>
     */
    @NameInMap("EnableRecord")
    public Boolean enableRecord;

    @NameInMap("ExternalUserId")
    public String externalUserId;

    @NameInMap("ImageId")
    public String imageId;

    @NameInMap("Labels")
    public String labels;

    @NameInMap("LoadSkill")
    public Boolean loadSkill;

    @NameInMap("LoginRegionId")
    public String loginRegionId;

    @NameInMap("ManualRelease")
    public Boolean manualRelease;

    @NameInMap("MaxRuntime")
    public Integer maxRuntime;

    @NameInMap("McpPolicyId")
    public String mcpPolicyId;

    @NameInMap("NetworkId")
    public String networkId;

    @NameInMap("PersistenceDataList")
    public java.util.List<CreateMcpSessionRequestPersistenceDataList> persistenceDataList;

    @NameInMap("SdkStats")
    public String sdkStats;

    @NameInMap("SessionId")
    public String sessionId;

    @NameInMap("Skills")
    public java.util.List<String> skills;

    @NameInMap("Timeout")
    public Integer timeout;

    @NameInMap("VpcResource")
    public Boolean vpcResource;

    public static CreateMcpSessionRequest build(java.util.Map<String, ?> map) throws Exception {
        CreateMcpSessionRequest self = new CreateMcpSessionRequest();
        return TeaModel.build(map, self);
    }

    public CreateMcpSessionRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public CreateMcpSessionRequest setContextId(String contextId) {
        this.contextId = contextId;
        return this;
    }
    public String getContextId() {
        return this.contextId;
    }

    public CreateMcpSessionRequest setDirectLink(Boolean directLink) {
        this.directLink = directLink;
        return this;
    }
    public Boolean getDirectLink() {
        return this.directLink;
    }

    public CreateMcpSessionRequest setEnableRecord(Boolean enableRecord) {
        this.enableRecord = enableRecord;
        return this;
    }
    public Boolean getEnableRecord() {
        return this.enableRecord;
    }

    public CreateMcpSessionRequest setExternalUserId(String externalUserId) {
        this.externalUserId = externalUserId;
        return this;
    }
    public String getExternalUserId() {
        return this.externalUserId;
    }

    public CreateMcpSessionRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public CreateMcpSessionRequest setLabels(String labels) {
        this.labels = labels;
        return this;
    }
    public String getLabels() {
        return this.labels;
    }

    public CreateMcpSessionRequest setLoadSkill(Boolean loadSkill) {
        this.loadSkill = loadSkill;
        return this;
    }
    public Boolean getLoadSkill() {
        return this.loadSkill;
    }

    public CreateMcpSessionRequest setLoginRegionId(String loginRegionId) {
        this.loginRegionId = loginRegionId;
        return this;
    }
    public String getLoginRegionId() {
        return this.loginRegionId;
    }

    public CreateMcpSessionRequest setManualRelease(Boolean manualRelease) {
        this.manualRelease = manualRelease;
        return this;
    }
    public Boolean getManualRelease() {
        return this.manualRelease;
    }

    public CreateMcpSessionRequest setMaxRuntime(Integer maxRuntime) {
        this.maxRuntime = maxRuntime;
        return this;
    }
    public Integer getMaxRuntime() {
        return this.maxRuntime;
    }

    public CreateMcpSessionRequest setMcpPolicyId(String mcpPolicyId) {
        this.mcpPolicyId = mcpPolicyId;
        return this;
    }
    public String getMcpPolicyId() {
        return this.mcpPolicyId;
    }

    public CreateMcpSessionRequest setNetworkId(String networkId) {
        this.networkId = networkId;
        return this;
    }
    public String getNetworkId() {
        return this.networkId;
    }

    public CreateMcpSessionRequest setPersistenceDataList(java.util.List<CreateMcpSessionRequestPersistenceDataList> persistenceDataList) {
        this.persistenceDataList = persistenceDataList;
        return this;
    }
    public java.util.List<CreateMcpSessionRequestPersistenceDataList> getPersistenceDataList() {
        return this.persistenceDataList;
    }

    public CreateMcpSessionRequest setSdkStats(String sdkStats) {
        this.sdkStats = sdkStats;
        return this;
    }
    public String getSdkStats() {
        return this.sdkStats;
    }

    public CreateMcpSessionRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

    public CreateMcpSessionRequest setSkills(java.util.List<String> skills) {
        this.skills = skills;
        return this;
    }
    public java.util.List<String> getSkills() {
        return this.skills;
    }

    public CreateMcpSessionRequest setTimeout(Integer timeout) {
        this.timeout = timeout;
        return this;
    }
    public Integer getTimeout() {
        return this.timeout;
    }

    public CreateMcpSessionRequest setVpcResource(Boolean vpcResource) {
        this.vpcResource = vpcResource;
        return this;
    }
    public Boolean getVpcResource() {
        return this.vpcResource;
    }

    public static class CreateMcpSessionRequestPersistenceDataListMountConfig extends TeaModel {
        @NameInMap("AccessMode")
        public String accessMode;

        @NameInMap("StorageMode")
        public String storageMode;

        @NameInMap("ObjectKey")
        public String objectKey;

        @NameInMap("SourcePath")
        public String sourcePath;

        public static CreateMcpSessionRequestPersistenceDataListMountConfig build(java.util.Map<String, ?> map) throws Exception {
            CreateMcpSessionRequestPersistenceDataListMountConfig self = new CreateMcpSessionRequestPersistenceDataListMountConfig();
            return TeaModel.build(map, self);
        }

        public CreateMcpSessionRequestPersistenceDataListMountConfig setAccessMode(String accessMode) {
            this.accessMode = accessMode;
            return this;
        }
        public String getAccessMode() {
            return this.accessMode;
        }

        public CreateMcpSessionRequestPersistenceDataListMountConfig setStorageMode(String storageMode) {
            this.storageMode = storageMode;
            return this;
        }
        public String getStorageMode() {
            return this.storageMode;
        }

        public CreateMcpSessionRequestPersistenceDataListMountConfig setObjectKey(String objectKey) {
            this.objectKey = objectKey;
            return this;
        }
        public String getObjectKey() {
            return this.objectKey;
        }

        public CreateMcpSessionRequestPersistenceDataListMountConfig setSourcePath(String sourcePath) {
            this.sourcePath = sourcePath;
            return this;
        }
        public String getSourcePath() {
            return this.sourcePath;
        }
    }

    public static class CreateMcpSessionRequestPersistenceDataList extends TeaModel {
        @NameInMap("ContextId")
        public String contextId;

        @NameInMap("Path")
        public String path;

        @NameInMap("Policy")
        public String policy;

        @NameInMap("Type")
        public String type;

        @NameInMap("MountConfig")
        public CreateMcpSessionRequestPersistenceDataListMountConfig mountConfig;

        public static CreateMcpSessionRequestPersistenceDataList build(java.util.Map<String, ?> map) throws Exception {
            CreateMcpSessionRequestPersistenceDataList self = new CreateMcpSessionRequestPersistenceDataList();
            return TeaModel.build(map, self);
        }

        public CreateMcpSessionRequestPersistenceDataList setContextId(String contextId) {
            this.contextId = contextId;
            return this;
        }
        public String getContextId() {
            return this.contextId;
        }

        public CreateMcpSessionRequestPersistenceDataList setPath(String path) {
            this.path = path;
            return this;
        }
        public String getPath() {
            return this.path;
        }

        public CreateMcpSessionRequestPersistenceDataList setPolicy(String policy) {
            this.policy = policy;
            return this;
        }
        public String getPolicy() {
            return this.policy;
        }

        public CreateMcpSessionRequestPersistenceDataList setType(String type) {
            this.type = type;
            return this;
        }
        public String getType() {
            return this.type;
        }

        public CreateMcpSessionRequestPersistenceDataList setMountConfig(CreateMcpSessionRequestPersistenceDataListMountConfig mountConfig) {
            this.mountConfig = mountConfig;
            return this;
        }
        public CreateMcpSessionRequestPersistenceDataListMountConfig getMountConfig() {
            return this.mountConfig;
        }

    }

}
