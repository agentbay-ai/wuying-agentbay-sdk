# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import Optional

from darabonba.model import DaraModel


class BindContextSkillAsyncShrinkRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        context_skill_bind_items_shrink: Optional[str] = None,
    ):
        self.authorization = authorization
        self.context_skill_bind_items_shrink = context_skill_bind_items_shrink

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization
        if self.context_skill_bind_items_shrink is not None:
            result['ContextSkillBindItems'] = self.context_skill_bind_items_shrink
        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')
        if m.get('ContextSkillBindItems') is not None:
            self.context_skill_bind_items_shrink = m.get('ContextSkillBindItems')
        return self
