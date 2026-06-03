# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List, Optional

from darabonba.model import DaraModel


class ListSkillMetaDataRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        skill_id_list: Optional[List[str]] = None,
    ):
        self.authorization = authorization
        self.skill_id_list = skill_id_list

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization
        if self.skill_id_list is not None:
            result["SkillIdList"] = self.skill_id_list
        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Authorization") is not None:
            self.authorization = m.get("Authorization")
        if m.get("SkillIdList") is not None:
            self.skill_id_list = m.get("SkillIdList")
        return self

