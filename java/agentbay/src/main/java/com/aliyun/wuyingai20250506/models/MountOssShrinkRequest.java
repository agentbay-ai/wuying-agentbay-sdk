// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class MountOssShrinkRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("OssMountConfigs")
    public String ossMountConfigsShrink;

    @NameInMap("SessionId")
    public String sessionId;

    @NameInMap("FsType")
    public String fsType;

    public static MountOssShrinkRequest build(java.util.Map<String, ?> map) throws Exception {
        MountOssShrinkRequest self = new MountOssShrinkRequest();
        return TeaModel.build(map, self);
    }

    public MountOssShrinkRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public MountOssShrinkRequest setOssMountConfigsShrink(String ossMountConfigsShrink) {
        this.ossMountConfigsShrink = ossMountConfigsShrink;
        return this;
    }
    public String getOssMountConfigsShrink() {
        return this.ossMountConfigsShrink;
    }

    public MountOssShrinkRequest setSessionId(String sessionId) {
        this.sessionId = sessionId;
        return this;
    }
    public String getSessionId() {
        return this.sessionId;
    }

    public MountOssShrinkRequest setFsType(String fsType) {
        this.fsType = fsType;
        return this;
    }
    public String getFsType() {
        return this.fsType;
    }

}
