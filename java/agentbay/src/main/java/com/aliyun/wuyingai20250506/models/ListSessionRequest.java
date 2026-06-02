// This file is auto-generated, don't edit it. Thanks.
package com.aliyun.wuyingai20250506.models;

import com.aliyun.tea.*;

public class ListSessionRequest extends TeaModel {
    @NameInMap("Authorization")
    public String authorization;

    @NameInMap("IsAll")
    public Boolean isAll;

    @NameInMap("Labels")
    public String labels;

    @NameInMap("MaxResults")
    public Integer maxResults;

    @NameInMap("NextToken")
    public String nextToken;

    @NameInMap("ImageId")
    public String imageId;

    @NameInMap("Status")
    public String status;

    public static ListSessionRequest build(java.util.Map<String, ?> map) throws Exception {
        ListSessionRequest self = new ListSessionRequest();
        return TeaModel.build(map, self);
    }

    public ListSessionRequest setAuthorization(String authorization) {
        this.authorization = authorization;
        return this;
    }
    public String getAuthorization() {
        return this.authorization;
    }

    public ListSessionRequest setImageId(String imageId) {
        this.imageId = imageId;
        return this;
    }
    public String getImageId() {
        return this.imageId;
    }

    public ListSessionRequest setIsAll(Boolean isAll) {
        this.isAll = isAll;
        return this;
    }
    public Boolean getIsAll() {
        return this.isAll;
    }

    public ListSessionRequest setLabels(String labels) {
        this.labels = labels;
        return this;
    }
    public String getLabels() {
        return this.labels;
    }

    public ListSessionRequest setMaxResults(Integer maxResults) {
        this.maxResults = maxResults;
        return this;
    }
    public Integer getMaxResults() {
        return this.maxResults;
    }

    public ListSessionRequest setNextToken(String nextToken) {
        this.nextToken = nextToken;
        return this;
    }
    public String getNextToken() {
        return this.nextToken;
    }

    public ListSessionRequest setStatus(String status) {
        this.status = status;
        return this;
    }
    public String getStatus() {
        return this.status;
    }

}
