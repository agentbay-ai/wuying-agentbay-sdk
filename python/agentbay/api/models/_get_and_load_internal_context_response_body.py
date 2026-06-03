# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from agentbay.api import models as main_models
from darabonba.model import DaraModel

class GetAndLoadInternalContextResponseBody(DaraModel):
    def __init__(
        self,
        code: str = None,
        data: List[main_models.GetAndLoadInternalContextResponseBodyData] = None,
        http_status_code: int = None,
        message: str = None,
        request_id: str = None,
        success: bool = None,
    ):
        self.code = code
        self.data = data
        self.http_status_code = http_status_code
        self.message = message
        self.request_id = request_id
        self.success = success

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
            result['Code'] = self.code

        result['Data'] = []
        if self.data is not None:
            for k1 in self.data:
                result['Data'].append(k1.to_map() if k1 else None)

        if self.http_status_code is not None:
            result['HttpStatusCode'] = self.http_status_code

        if self.message is not None:
            result['Message'] = self.message

        if self.request_id is not None:
            result['RequestId'] = self.request_id

        if self.success is not None:
            result['Success'] = self.success

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Code') is not None:
            self.code = m.get('Code')

        self.data = []
        if m.get('Data') is not None:
            for k1 in m.get('Data'):
                temp_model = main_models.GetAndLoadInternalContextResponseBodyData()
                self.data.append(temp_model.from_map(k1))

        if m.get('HttpStatusCode') is not None:
            self.http_status_code = m.get('HttpStatusCode')

        if m.get('Message') is not None:
            self.message = m.get('Message')

        if m.get('RequestId') is not None:
            self.request_id = m.get('RequestId')

        if m.get('Success') is not None:
            self.success = m.get('Success')

        return self

class GetAndLoadInternalContextResponseBodyData(DaraModel):
    def __init__(
        self,
        context_id: str = None,
        context_path: str = None,
        context_type: str = None,
    ):
        self.context_id = context_id
        self.context_path = context_path
        self.context_type = context_type

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.context_id is not None:
            result['ContextId'] = self.context_id

        if self.context_path is not None:
            result['ContextPath'] = self.context_path

        if self.context_type is not None:
            result['ContextType'] = self.context_type

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ContextId') is not None:
            self.context_id = m.get('ContextId')

        if m.get('ContextPath') is not None:
            self.context_path = m.get('ContextPath')

        if m.get('ContextType') is not None:
            self.context_type = m.get('ContextType')

        return self

