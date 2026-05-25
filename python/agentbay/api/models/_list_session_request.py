# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from darabonba.model import DaraModel


class ListSessionRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        image_id: str = None,
        labels: str = None,
        max_results: int = None,
        next_token: str = None,
        status: str = None,
    ):
        self.authorization = authorization
        self.image_id = image_id
        self.labels = labels
        self.max_results = max_results
        self.next_token = next_token
        self.status = status

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization

        if self.image_id is not None:
            result["ImageId"] = self.image_id

        if self.labels is not None:
            result["Labels"] = self.labels

        if self.max_results is not None:
            result["MaxResults"] = self.max_results

        if self.next_token is not None:
            result["NextToken"] = self.next_token

        if self.status is not None:
            result["Status"] = self.status

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Authorization") is not None:
            self.authorization = m.get("Authorization")

        if m.get("ImageId") is not None:
            self.image_id = m.get("ImageId")

        if m.get("Labels") is not None:
            self.labels = m.get("Labels")

        if m.get("MaxResults") is not None:
            self.max_results = m.get("MaxResults")

        if m.get("NextToken") is not None:
            self.next_token = m.get("NextToken")

        if m.get("Status") is not None:
            self.status = m.get("Status")

        return self
