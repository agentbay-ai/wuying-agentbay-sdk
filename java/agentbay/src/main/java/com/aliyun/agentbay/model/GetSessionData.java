package com.aliyun.agentbay.model;

/**
 * Data returned by GetSession API
 */
public class GetSessionData {
    private String sessionId;
    private String appInstanceId;
    private String resourceId;
    private String resourceUrl;
    private boolean vpcResource;
    private String networkInterfaceIp;
    private String vpcIp;
    private String vpcId;
    private String httpPort;
    private String token;
    private String linkUrl;
    private String wsUrl;
    private String status;
    private String code;
    private String toolList;
    private boolean success;

    public GetSessionData() {
    }

    public GetSessionData(String sessionId, String appInstanceId, String resourceId,
                         String resourceUrl, boolean vpcResource, String networkInterfaceIp,
                         String httpPort, String token, String linkUrl, String wsUrl,
                         String code, String toolList, boolean success, String status) {
        this(sessionId, appInstanceId, resourceId, resourceUrl, vpcResource,
             networkInterfaceIp, httpPort, token, linkUrl, wsUrl, code, toolList,
             success, status, null, null);
    }

    public GetSessionData(String sessionId, String appInstanceId, String resourceId,
                         String resourceUrl, boolean vpcResource, String networkInterfaceIp,
                         String httpPort, String token, String linkUrl, String wsUrl,
                         String code, String toolList, boolean success, String status,
                         String vpcIp, String vpcId) {
        this.sessionId = sessionId;
        this.appInstanceId = appInstanceId;
        this.resourceId = resourceId;
        this.resourceUrl = resourceUrl;
        this.vpcResource = vpcResource;
        this.networkInterfaceIp = networkInterfaceIp;
        this.httpPort = httpPort;
        this.token = token;
        this.linkUrl = linkUrl;
        this.wsUrl = wsUrl;
        this.code = code;
        this.toolList = toolList;
        this.success = success;
        this.status = status;
        this.vpcIp = vpcIp;
        this.vpcId = vpcId;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getAppInstanceId() {
        return appInstanceId;
    }

    public void setAppInstanceId(String appInstanceId) {
        this.appInstanceId = appInstanceId;
    }

    public String getResourceId() {
        return resourceId;
    }

    public void setResourceId(String resourceId) {
        this.resourceId = resourceId;
    }

    public String getResourceUrl() {
        return resourceUrl;
    }

    public void setResourceUrl(String resourceUrl) {
        this.resourceUrl = resourceUrl;
    }

    public boolean isVpcResource() {
        return vpcResource;
    }

    public void setVpcResource(boolean vpcResource) {
        this.vpcResource = vpcResource;
    }

    public String getNetworkInterfaceIp() {
        return networkInterfaceIp;
    }

    public void setNetworkInterfaceIp(String networkInterfaceIp) {
        this.networkInterfaceIp = networkInterfaceIp;
    }

    public String getVpcIp() {
        return vpcIp;
    }

    public void setVpcIp(String vpcIp) {
        this.vpcIp = vpcIp;
    }

    public String getVpcId() {
        return vpcId;
    }

    public void setVpcId(String vpcId) {
        this.vpcId = vpcId;
    }

    public String getHttpPort() {
        return httpPort;
    }

    public void setHttpPort(String httpPort) {
        this.httpPort = httpPort;
    }

    public String getToken() {
        return token;
    }

    public void setToken(String token) {
        this.token = token;
    }

    public String getLinkUrl() {
        return linkUrl;
    }

    public void setLinkUrl(String linkUrl) {
        this.linkUrl = linkUrl;
    }

    public String getWsUrl() {
        return wsUrl;
    }

    public void setWsUrl(String wsUrl) {
        this.wsUrl = wsUrl;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getToolList() {
        return toolList;
    }

    public void setToolList(String toolList) {
        this.toolList = toolList;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }
}

