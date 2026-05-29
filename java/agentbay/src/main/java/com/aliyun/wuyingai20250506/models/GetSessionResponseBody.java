// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class GetSessionResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public GetSessionResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static GetSessionResponseBody build(java.util.Map<String, ?> map) throws Exception {
        GetSessionResponseBody self = new GetSessionResponseBody();
        return TeaModel.build(map, self);
    }

    public GetSessionResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public GetSessionResponseBody setData(GetSessionResponseBodyData data) {
        this.data = data;
        return this;
    }
    public GetSessionResponseBodyData getData() {
        return this.data;
    }

    public GetSessionResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public GetSessionResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public GetSessionResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public GetSessionResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class GetSessionResponseBodyDataToolList extends TeaModel {
        @NameInMap("Description")
        public String description;

        @NameInMap("InputSchema")
        public String inputSchema;

        @NameInMap("IsMcpAvailable")
        public String isMcpAvailable;

        @NameInMap("Name")
        public String name;

        @NameInMap("Server")
        public String server;

        @NameInMap("Tool")
        public String tool;

        public static GetSessionResponseBodyDataToolList build(java.util.Map<String, ?> map) throws Exception {
            GetSessionResponseBodyDataToolList self = new GetSessionResponseBodyDataToolList();
            return TeaModel.build(map, self);
        }

        public GetSessionResponseBodyDataToolList setDescription(String description) {
            this.description = description;
            return this;
        }
        public String getDescription() {
            return this.description;
        }

        public GetSessionResponseBodyDataToolList setInputSchema(String inputSchema) {
            this.inputSchema = inputSchema;
            return this;
        }
        public String getInputSchema() {
            return this.inputSchema;
        }

        public GetSessionResponseBodyDataToolList setIsMcpAvailable(String isMcpAvailable) {
            this.isMcpAvailable = isMcpAvailable;
            return this;
        }
        public String getIsMcpAvailable() {
            return this.isMcpAvailable;
        }

        public GetSessionResponseBodyDataToolList setName(String name) {
            this.name = name;
            return this;
        }
        public String getName() {
            return this.name;
        }

        public GetSessionResponseBodyDataToolList setServer(String server) {
            this.server = server;
            return this;
        }
        public String getServer() {
            return this.server;
        }

        public GetSessionResponseBodyDataToolList setTool(String tool) {
            this.tool = tool;
            return this;
        }
        public String getTool() {
            return this.tool;
        }

    }

    public static class GetSessionResponseBodyDataContexts extends TeaModel {
        @NameInMap("id")
        public String id;

        @NameInMap("name")
        public String name;

        public static GetSessionResponseBodyDataContexts build(java.util.Map<String, ?> map) throws Exception {
            GetSessionResponseBodyDataContexts self = new GetSessionResponseBodyDataContexts();
            return TeaModel.build(map, self);
        }

        public GetSessionResponseBodyDataContexts setId(String id) {
            this.id = id;
            return this;
        }
        public String getId() {
            return this.id;
        }

        public GetSessionResponseBodyDataContexts setName(String name) {
            this.name = name;
            return this;
        }
        public String getName() {
            return this.name;
        }

    }

    public static class GetSessionResponseBodyData extends TeaModel {
        @NameInMap("AppInstanceId")
        public String appInstanceId;

        @NameInMap("HttpPort")
        public String httpPort;

        @NameInMap("LinkUrl")
        public String linkUrl;

        @NameInMap("NetworkInterfaceIp")
        public String networkInterfaceIp;

        @NameInMap("ResourceId")
        public String resourceId;

        @NameInMap("ResourceUrl")
        public String resourceUrl;

        @NameInMap("SessionId")
        public String sessionId;

        @NameInMap("Status")
        public String status;

        @NameInMap("Token")
        public String token;

        @NameInMap("ToolList")
        public java.util.List<GetSessionResponseBodyDataToolList> toolList;

        @NameInMap("VpcResource")
        public Boolean vpcResource;

        @NameInMap("WsUrl")
        public String wsUrl;

        @NameInMap("contexts")
        public java.util.List<GetSessionResponseBodyDataContexts> contexts;

        public static GetSessionResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            GetSessionResponseBodyData self = new GetSessionResponseBodyData();
            return TeaModel.build(map, self);
        }

        public GetSessionResponseBodyData setAppInstanceId(String appInstanceId) {
            this.appInstanceId = appInstanceId;
            return this;
        }
        public String getAppInstanceId() {
            return this.appInstanceId;
        }

        public GetSessionResponseBodyData setHttpPort(String httpPort) {
            this.httpPort = httpPort;
            return this;
        }
        public String getHttpPort() {
            return this.httpPort;
        }

        public GetSessionResponseBodyData setLinkUrl(String linkUrl) {
            this.linkUrl = linkUrl;
            return this;
        }
        public String getLinkUrl() {
            return this.linkUrl;
        }

        public GetSessionResponseBodyData setNetworkInterfaceIp(String networkInterfaceIp) {
            this.networkInterfaceIp = networkInterfaceIp;
            return this;
        }
        public String getNetworkInterfaceIp() {
            return this.networkInterfaceIp;
        }

        public GetSessionResponseBodyData setResourceId(String resourceId) {
            this.resourceId = resourceId;
            return this;
        }
        public String getResourceId() {
            return this.resourceId;
        }

        public GetSessionResponseBodyData setResourceUrl(String resourceUrl) {
            this.resourceUrl = resourceUrl;
            return this;
        }
        public String getResourceUrl() {
            return this.resourceUrl;
        }

        public GetSessionResponseBodyData setSessionId(String sessionId) {
            this.sessionId = sessionId;
            return this;
        }
        public String getSessionId() {
            return this.sessionId;
        }

        public GetSessionResponseBodyData setStatus(String status) {
            this.status = status;
            return this;
        }
        public String getStatus() {
            return this.status;
        }

        public GetSessionResponseBodyData setToken(String token) {
            this.token = token;
            return this;
        }
        public String getToken() {
            return this.token;
        }

        public GetSessionResponseBodyData setToolList(java.util.List<GetSessionResponseBodyDataToolList> toolList) {
            this.toolList = toolList;
            return this;
        }
        public java.util.List<GetSessionResponseBodyDataToolList> getToolList() {
            return this.toolList;
        }

        public GetSessionResponseBodyData setVpcResource(Boolean vpcResource) {
            this.vpcResource = vpcResource;
            return this;
        }
        public Boolean getVpcResource() {
            return this.vpcResource;
        }

        public GetSessionResponseBodyData setWsUrl(String wsUrl) {
            this.wsUrl = wsUrl;
            return this;
        }
        public String getWsUrl() {
            return this.wsUrl;
        }

        public GetSessionResponseBodyData setContexts(java.util.List<GetSessionResponseBodyDataContexts> contexts) {
            this.contexts = contexts;
            return this;
        }
        public java.util.List<GetSessionResponseBodyDataContexts> getContexts() {
            return this.contexts;
        }

    }

}
