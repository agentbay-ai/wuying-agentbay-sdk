// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class BindContextsShrinkRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("PersistenceDataList")
    public String persistenceDataListShrink;

    @NameInMap("SessionId")
    public String sessionId;

    public static BindContextsShrinkRequest build(java.util.Map<String, ?> map) throws Exception {
        BindContextsShrinkRequest self = new BindContextsShrinkRequest();
        return TeaModel.build(map, self);
    }

    public BindContextsShrinkRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public BindContextsShrinkRequest setPersistenceDataListShrink(String persistenceDataListShrink) {
        this.persistenceDataListShrink = persistenceDataListShrink;
        return this;
    }
    public String getPersistenceDataListShrink() {
        return this.persistenceDataListShrink;
    }

    public BindContextsShrinkRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

}
