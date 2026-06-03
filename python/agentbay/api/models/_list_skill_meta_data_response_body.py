# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from darabonba.model import DaraModel


class ListSkillMetaDataResponseBody(DaraModel):
    def __init__(
        self,
        code: str = None,
        data: List["ListSkillMetaDataResponseBodyData"] = None,
        http_status_code: int = None,
        message: str = None,
        request_id: str = None,
        success: bool = None,
        total_count: int = None,
    ):
        self.code = code
        self.data = data
        self.http_status_code = http_status_code
        self.message = message
        self.request_id = request_id
        self.success = success
        self.total_count = total_count

    def validate(self):
        if self.data:
            for v1 in self.data:
                if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.code is not None:
            result["Code"] = self.code
        result["Data"] = []
        if self.data is not None:
            for k1 in self.data:
                result["Data"].append(k1.to_map() if k1 else None)
        if self.http_status_code is not None:
            result["HttpStatusCode"] = self.http_status_code
        if self.message is not None:
            result["Message"] = self.message
        if self.request_id is not None:
            result["RequestId"] = self.request_id
        if self.success is not None:
            result["Success"] = self.success
        if self.total_count is not None:
            result["TotalCount"] = self.total_count
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Code") is not None:
            self.code = m.get("Code")
        self.data = []
        if m.get("Data") is not None:
            for k1 in m.get("Data"):
                temp_model = ListSkillMetaDataResponseBodyData()
                self.data.append(temp_model.from_map(k1))
        if m.get("HttpStatusCode") is not None:
            self.http_status_code = m.get("HttpStatusCode")
        if m.get("Message") is not None:
            self.message = m.get("Message")
        if m.get("RequestId") is not None:
            self.request_id = m.get("RequestId")
        if m.get("Success") is not None:
            self.success = m.get("Success")
        if m.get("TotalCount") is not None:
            self.total_count = m.get("TotalCount")
        return self


class ListSkillMetaDataResponseBodyData(DaraModel):
    def __init__(
        self,
        description: str = None,
        name: str = None,
        skill_id: str = None,
    ):
        self.description = description
        self.name = name
        self.skill_id = skill_id

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.description is not None:
            result["Description"] = self.description
        if self.name is not None:
            result["Name"] = self.name
        if self.skill_id is not None:
            result["SkillId"] = self.skill_id
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Description") is not None:
            self.description = m.get("Description")
        if m.get("Name") is not None:
            self.name = m.get("Name")
        if m.get("SkillId") is not None:
            self.skill_id = m.get("SkillId")
        return self

