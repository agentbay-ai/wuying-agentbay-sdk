// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class CreateNetworkRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("LoginRegionId")
    public String loginRegionId;

    @NameInMap("NetworkId")
    public String networkId;

    public static CreateNetworkRequest build(java.util.Map<String, ?> map) throws Exception {
        CreateNetworkRequest self = new CreateNetworkRequest();
        return TeaModel.build(map, self);
    }

    public CreateNetworkRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public CreateNetworkRequest setLoginRegionId(String loginRegionId) {
        this.loginRegionId = loginRegionId;
        return this;
    }
    public String getLoginRegionId() {
        return this.loginRegionId;
    }

    public CreateNetworkRequest setNetworkId(String networkId) {
        this.networkId = networkId;
        return this;
    }
    public String getNetworkId() {
        return this.networkId;
    }

}
