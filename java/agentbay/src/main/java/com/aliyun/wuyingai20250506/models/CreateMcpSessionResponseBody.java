// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class CreateMcpSessionResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public CreateMcpSessionResponseBodyData data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static CreateMcpSessionResponseBody build(java.util.Map<String, ?> map) throws Exception {
        CreateMcpSessionResponseBody self = new CreateMcpSessionResponseBody();
        return TeaModel.build(map, self);
    }

    public CreateMcpSessionResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public CreateMcpSessionResponseBody setData(CreateMcpSessionResponseBodyData data) {
        this.data = data;
        return this;
    }
    public CreateMcpSessionResponseBodyData getData() {
        return this.data;
    }

    public CreateMcpSessionResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public CreateMcpSessionResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public CreateMcpSessionResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public CreateMcpSessionResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class CreateMcpSessionResponseBodyData extends TeaModel {
        @NameInMap("AppInstanceId")
        public String appInstanceId;

        @NameInMap("ErrMsg")
        public String errMsg;

        @NameInMap("ErrorCode")
        public String errorCode;

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

        @NameInMap("Success")
        public Boolean success;

        @NameInMap("Token")
        public String token;

        @NameInMap("ToolList")
        public String toolList;

        @NameInMap("VpcResource")
        public Boolean vpcResource;

        @NameInMap("WsUrl")
        public String wsUrl;

        public static CreateMcpSessionResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            CreateMcpSessionResponseBodyData self = new CreateMcpSessionResponseBodyData();
            return TeaModel.build(map, self);
        }

        public CreateMcpSessionResponseBodyData setAppInstanceId(String appInstanceId) {
            this.appInstanceId = appInstanceId;
            return this;
        }
        public String getAppInstanceId() {
            return this.appInstanceId;
        }

        public CreateMcpSessionResponseBodyData setErrMsg(String errMsg) {
            this.errMsg = errMsg;
            return this;
        }
        public String getErrMsg() {
            return this.errMsg;
        }

        public CreateMcpSessionResponseBodyData setErrorCode(String errorCode) {
            this.errorCode = errorCode;
            return this;
        }
        public String getErrorCode() {
            return this.errorCode;
        }

        public CreateMcpSessionResponseBodyData setHttpPort(String httpPort) {
            this.httpPort = httpPort;
            return this;
        }
        public String getHttpPort() {
            return this.httpPort;
        }

        public CreateMcpSessionResponseBodyData setLinkUrl(String linkUrl) {
            this.linkUrl = linkUrl;
            return this;
        }
        public String getLinkUrl() {
            return this.linkUrl;
        }

        public CreateMcpSessionResponseBodyData setNetworkInterfaceIp(String networkInterfaceIp) {
            this.networkInterfaceIp = networkInterfaceIp;
            return this;
        }
        public String getNetworkInterfaceIp() {
            return this.networkInterfaceIp;
        }

        public CreateMcpSessionResponseBodyData setResourceId(String resourceId) {
            this.resourceId = resourceId;
            return this;
        }
        public String getResourceId() {
            return this.resourceId;
        }

        public CreateMcpSessionResponseBodyData setResourceUrl(String resourceUrl) {
            this.resourceUrl = resourceUrl;
            return this;
        }
        public String getResourceUrl() {
            return this.resourceUrl;
        }

        public CreateMcpSessionResponseBodyData setSessionId(String sessionId) {
            this.sessionId = sessionId;
            return this;
        }
        public String getSessionId() {
            return this.sessionId;
        }

        public CreateMcpSessionResponseBodyData setSuccess(Boolean success) {
            this.success = success;
            return this;
        }
        public Boolean getSuccess() {
            return this.success;
        }

        public CreateMcpSessionResponseBodyData setToken(String token) {
            this.token = token;
            return this;
        }
        public String getToken() {
            return this.token;
        }

        public CreateMcpSessionResponseBodyData setToolList(String toolList) {
            this.toolList = toolList;
            return this;
        }
        public String getToolList() {
            return this.toolList;
        }

        public CreateMcpSessionResponseBodyData setVpcResource(Boolean vpcResource) {
            this.vpcResource = vpcResource;
            return this;
        }
        public Boolean getVpcResource() {
            return this.vpcResource;
        }

        public CreateMcpSessionResponseBodyData setWsUrl(String wsUrl) {
            this.wsUrl = wsUrl;
            return this;
        }
        public String getWsUrl() {
            return this.wsUrl;
        }

    }

}
