// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class DescribeSessionContextsResponseBody extends TeaModel {
    @NameInMap("Code")
    public String code;

    @NameInMap("Data")
    public java.util.List<DescribeSessionContextsResponseBodyData> data;

    @NameInMap("HttpStatusCode")
    public Integer httpStatusCode;

    @NameInMap("Message")
    public String message;

    @NameInMap("RequestId")
    public String requestId;

    @NameInMap("Success")
    public Boolean success;

    public static DescribeSessionContextsResponseBody build(java.util.Map<String, ?> map) throws Exception {
        DescribeSessionContextsResponseBody self = new DescribeSessionContextsResponseBody();
        return TeaModel.build(map, self);
    }

    public DescribeSessionContextsResponseBody setCode(String code) {
        this.code = code;
        return this;
    }
    public String getCode() {
        return this.code;
    }

    public DescribeSessionContextsResponseBody setData(java.util.List<DescribeSessionContextsResponseBodyData> data) {
        this.data = data;
        return this;
    }
    public java.util.List<DescribeSessionContextsResponseBodyData> getData() {
        return this.data;
    }

    public DescribeSessionContextsResponseBody setHttpStatusCode(Integer httpStatusCode) {
        this.httpStatusCode = httpStatusCode;
        return this;
    }
    public Integer getHttpStatusCode() {
        return this.httpStatusCode;
    }

    public DescribeSessionContextsResponseBody setMessage(String message) {
        this.message = message;
        return this;
    }
    public String getMessage() {
        return this.message;
    }

    public DescribeSessionContextsResponseBody setRequestId(String requestId) {
        this.requestId = requestId;
        return this;
    }
    public String getRequestId() {
        return this.requestId;
    }

    public DescribeSessionContextsResponseBody setSuccess(Boolean success) {
        this.success = success;
        return this;
    }
    public Boolean getSuccess() {
        return this.success;
    }

    public static class DescribeSessionContextsResponseBodyData extends TeaModel {
        @NameInMap("BindTime")
        public String bindTime;

        @NameInMap("ContextId")
        public String contextId;

        @NameInMap("ContextName")
        public String contextName;

        @NameInMap("Path")
        public String path;

        @NameInMap("Policy")
        public String policy;

        public static DescribeSessionContextsResponseBodyData build(java.util.Map<String, ?> map) throws Exception {
            DescribeSessionContextsResponseBodyData self = new DescribeSessionContextsResponseBodyData();
            return TeaModel.build(map, self);
        }

        public DescribeSessionContextsResponseBodyData setBindTime(String bindTime) {
            this.bindTime = bindTime;
            return this;
        }
        public String getBindTime() {
            return this.bindTime;
        }

        public DescribeSessionContextsResponseBodyData setContextId(String contextId) {
            this.contextId = contextId;
            return this;
        }
        public String getContextId() {
            return this.contextId;
        }

        public DescribeSessionContextsResponseBodyData setContextName(String contextName) {
            this.contextName = contextName;
            return this;
        }
        public String getContextName() {
            return this.contextName;
        }

        public DescribeSessionContextsResponseBodyData setPath(String path) {
            this.path = path;
            return this;
        }
        public String getPath() {
            return this.path;
        }

        public DescribeSessionContextsResponseBodyData setPolicy(String policy) {
            this.policy = policy;
            return this;
        }
        public String getPolicy() {
            return this.policy;
        }

    }

}
