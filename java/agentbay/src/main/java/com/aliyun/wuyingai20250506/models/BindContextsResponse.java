// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class BindContextsResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public BindContextsResponseBody body;

    public static BindContextsResponse build(java.util.Map<String, ?> map) throws Exception {
        BindContextsResponse self = new BindContextsResponse();
        return TeaModel.build(map, self);
    }

    public BindContextsResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public BindContextsResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public BindContextsResponse setBody(BindContextsResponseBody body) {
        this.body = body;
        return this;
    }
    public BindContextsResponseBody getBody() {
        return this.body;
    }

}
