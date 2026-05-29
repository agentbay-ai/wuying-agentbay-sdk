// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class CreateMcpSessionShrinkRequest extends TeaModel {
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
    public String persistenceDataListShrink;

    @NameInMap("SdkStats")
    public String sdkStats;

    @NameInMap("SessionId")
    public String sessionId;

    @NameInMap("Skills")
    public String skillsShrink;

    @NameInMap("Timeout")
    public Integer timeout;

    @NameInMap("VpcResource")
    public Boolean vpcResource;

    public static CreateMcpSessionShrinkRequest build(java.util.Map<String, ?> map) throws Exception {
        CreateMcpSessionShrinkRequest self = new CreateMcpSessionShrinkRequest();
        return TeaModel.build(map, self);
    }

    public CreateMcpSessionShrinkRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public CreateMcpSessionShrinkRequest setContextId(String contextId) {
        this.contextId = contextId;
        return this;
    }
    public String getContextId() {
        return this.contextId;
    }

    public CreateMcpSessionShrinkRequest setDirectLink(Boolean directLink) {
        this.directLink = directLink;
        return this;
    }
    public Boolean getDirectLink() {
        return this.directLink;
    }

    public CreateMcpSessionShrinkRequest setEnableRecord(Boolean enableRecord) {
        this.enableRecord = enableRecord;
        return this;
    }
    public Boolean getEnableRecord() {
        return this.enableRecord;
    }

    public CreateMcpSessionShrinkRequest setExternalUserId(String externalUserId) {
        this.externalUserId = externalUserId;
        return this;
    }
    public String getExternalUserId() {
        return this.externalUserId;
    }

    public CreateMcpSessionShrinkRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public CreateMcpSessionShrinkRequest setLabels(String labels) {
        this.labels = labels;
        return this;
    }
    public String getLabels() {
        return this.labels;
    }

    public CreateMcpSessionShrinkRequest setLoadSkill(Boolean loadSkill) {
        this.loadSkill = loadSkill;
        return this;
    }
    public Boolean getLoadSkill() {
        return this.loadSkill;
    }

    public CreateMcpSessionShrinkRequest setLoginRegionId(String loginRegionId) {
        this.loginRegionId = loginRegionId;
        return this;
    }
    public String getLoginRegionId() {
        return this.loginRegionId;
    }

    public CreateMcpSessionShrinkRequest setManualRelease(Boolean manualRelease) {
        this.manualRelease = manualRelease;
        return this;
    }
    public Boolean getManualRelease() {
        return this.manualRelease;
    }

    public CreateMcpSessionShrinkRequest setMaxRuntime(Integer maxRuntime) {
        this.maxRuntime = maxRuntime;
        return this;
    }
    public Integer getMaxRuntime() {
        return this.maxRuntime;
    }

    public CreateMcpSessionShrinkRequest setMcpPolicyId(String mcpPolicyId) {
        this.mcpPolicyId = mcpPolicyId;
        return this;
    }
    public String getMcpPolicyId() {
        return this.mcpPolicyId;
    }

    public CreateMcpSessionShrinkRequest setNetworkId(String networkId) {
        this.networkId = networkId;
        return this;
    }
    public String getNetworkId() {
        return this.networkId;
    }

    public CreateMcpSessionShrinkRequest setPersistenceDataListShrink(String persistenceDataListShrink) {
        this.persistenceDataListShrink = persistenceDataListShrink;
        return this;
    }
    public String getPersistenceDataListShrink() {
        return this.persistenceDataListShrink;
    }

    public CreateMcpSessionShrinkRequest setSdkStats(String sdkStats) {
        this.sdkStats = sdkStats;
        return this;
    }
    public String getSdkStats() {
        return this.sdkStats;
    }

    public CreateMcpSessionShrinkRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

    public CreateMcpSessionShrinkRequest setSkillsShrink(String skillsShrink) {
        this.skillsShrink = skillsShrink;
        return this;
    }
    public String getSkillsShrink() {
        return this.skillsShrink;
    }

    public CreateMcpSessionShrinkRequest setTimeout(Integer timeout) {
        this.timeout = timeout;
        return this;
    }
    public Integer getTimeout() {
        return this.timeout;
    }

    public CreateMcpSessionShrinkRequest setVpcResource(Boolean vpcResource) {
        this.vpcResource = vpcResource;
        return this;
    }
    public Boolean getVpcResource() {
        return this.vpcResource;
    }

}
