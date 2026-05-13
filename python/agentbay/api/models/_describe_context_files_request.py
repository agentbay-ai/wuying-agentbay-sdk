# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from darabonba.model import DaraModel


class DescribeContextFilesRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        page_number: int = None,
        page_size: int = None,
        parent_folder_path: str = None,
        context_id: str = None,
        max_results: int = None,
        next_token: str = None,
    ):
        self.authorization = authorization
        self.page_number = page_number
        self.page_size = page_size
        self.parent_folder_path = parent_folder_path
        self.context_id = context_id
        self.max_results = max_results
        self.next_token = next_token

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization

        if self.page_number is not None:
            result["PageNumber"] = self.page_number

        if self.page_size is not None:
            result["PageSize"] = self.page_size

        if self.parent_folder_path is not None:
            result["ParentFolderPath"] = self.parent_folder_path

        if self.context_id is not None:
            result["ContextId"] = self.context_id

        if self.max_results is not None:
            result["MaxResults"] = self.max_results

        if self.next_token is not None:
            result["NextToken"] = self.next_token

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Authorization") is not None:
            self.authorization = m.get("Authorization")

        if m.get("PageNumber") is not None:
            self.page_number = m.get("PageNumber")

        if m.get("PageSize") is not None:
            self.page_size = m.get("PageSize")

        if m.get("ParentFolderPath") is not None:
            self.parent_folder_path = m.get("ParentFolderPath")

        if m.get("ContextId") is not None:
            self.context_id = m.get("ContextId")

        if m.get("MaxResults") is not None:
            self.max_results = m.get("MaxResults")

        if m.get("NextToken") is not None:
            self.next_token = m.get("NextToken")

        return self
