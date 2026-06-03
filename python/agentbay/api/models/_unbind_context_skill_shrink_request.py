# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import Optional

from darabonba.model import DaraModel


class UnbindContextSkillShrinkRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        context_skill_unbind_items_shrink: Optional[str] = None,
        login_region_id: Optional[str] = None,
    ):
        self.authorization = authorization
        self.context_skill_unbind_items_shrink = context_skill_unbind_items_shrink
        self.login_region_id = login_region_id

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization
        if self.login_region_id is not None:
            result['LoginRegionId'] = self.login_region_id
        if self.context_skill_unbind_items_shrink is not None:
            result['ContextSkillUnbindItems'] = self.context_skill_unbind_items_shrink
        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')
        if m.get('LoginRegionId') is not None:
            self.login_region_id = m.get('LoginRegionId')
        if m.get('ContextSkillUnbindItems') is not None:
            self.context_skill_unbind_items_shrink = m.get('ContextSkillUnbindItems')
        return self
