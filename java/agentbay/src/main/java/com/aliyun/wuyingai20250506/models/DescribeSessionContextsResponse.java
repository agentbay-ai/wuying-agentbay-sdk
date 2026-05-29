// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class DescribeSessionContextsResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public DescribeSessionContextsResponseBody body;

    public static DescribeSessionContextsResponse build(java.util.Map<String, ?> map) throws Exception {
        DescribeSessionContextsResponse self = new DescribeSessionContextsResponse();
        return TeaModel.build(map, self);
    }

    public DescribeSessionContextsResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public DescribeSessionContextsResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public DescribeSessionContextsResponse setBody(DescribeSessionContextsResponseBody body) {
        this.body = body;
        return this;
    }
    public DescribeSessionContextsResponseBody getBody() {
        return this.body;
    }

}
