# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List, Optional

from agentbay.api import models as main_models
from darabonba.model import DaraModel


class UnbindContextSkillRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        context_skill_unbind_items: Optional[List["UnbindContextSkillRequestContextSkillUnbindItems"]] = None,
    ):
        self.authorization = authorization
        self.context_skill_unbind_items = context_skill_unbind_items

    def validate(self):
        if self.context_skill_unbind_items:
            for v1 in self.context_skill_unbind_items:
                if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization
        result['ContextSkillUnbindItems'] = []
        if self.context_skill_unbind_items is not None:
            for k1 in self.context_skill_unbind_items:
                result['ContextSkillUnbindItems'].append(k1.to_map() if k1 else None)
        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')
        self.context_skill_unbind_items = []
        if m.get('ContextSkillUnbindItems') is not None:
            for k1 in m.get('ContextSkillUnbindItems'):
                temp_model = UnbindContextSkillRequestContextSkillUnbindItems()
                self.context_skill_unbind_items.append(temp_model.from_map(k1))
        return self


class UnbindContextSkillRequestContextSkillUnbindItems(DaraModel):
    def __init__(
        self,
        context_id: Optional[str] = None,
        skill_ids: Optional[List[str]] = None,
    ):
        self.context_id = context_id
        self.skill_ids = skill_ids

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.context_id is not None:
            result['ContextId'] = self.context_id
        if self.skill_ids is not None:
            result['SkillIds'] = self.skill_ids
        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('ContextId') is not None:
            self.context_id = m.get('ContextId')
        if m.get('SkillIds') is not None:
            self.skill_ids = m.get('SkillIds')
        return self
