// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class MountOssResponse extends TeaModel {
    @NameInMap("headers")
    public java.util.Map<String, String> headers;

    @NameInMap("statusCode")
    public Integer statusCode;

    @NameInMap("body")
    public MountOssResponseBody body;

    public static MountOssResponse build(java.util.Map<String, ?> map) throws Exception {
        MountOssResponse self = new MountOssResponse();
        return TeaModel.build(map, self);
    }

    public MountOssResponse setHeaders(java.util.Map<String, String> headers) {
        this.headers = headers;
        return this;
    }
    public java.util.Map<String, String> getHeaders() {
        return this.headers;
    }

    public MountOssResponse setStatusCode(Integer statusCode) {
        this.statusCode = statusCode;
        return this;
    }
    public Integer getStatusCode() {
        return this.statusCode;
    }

    public MountOssResponse setBody(MountOssResponseBody body) {
        this.body = body;
        return this;
    }
    public MountOssResponseBody getBody() {
        return this.body;
    }

}
