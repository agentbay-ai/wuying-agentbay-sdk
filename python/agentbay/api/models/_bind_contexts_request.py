# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from agentbay.api import models as main_models
from darabonba.model import DaraModel

class BindContextsRequest(DaraModel):
    def __init__(
        self,
        authorization: str = None,
        persistence_data_list: List[main_models.BindContextsRequestPersistenceDataList] = None,
        session_id: str = None,
    ):
        self.authorization = authorization
        self.persistence_data_list = persistence_data_list
        self.session_id = session_id

    def validate(self):
        if self.persistence_data_list:
            for v1 in self.persistence_data_list:
                 if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result['Authorization'] = self.authorization

        result['PersistenceDataList'] = []
        if self.persistence_data_list is not None:
            for k1 in self.persistence_data_list:
                result['PersistenceDataList'].append(k1.to_map() if k1 else None)

        if self.session_id is not None:
            result['SessionId'] = self.session_id

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('Authorization') is not None:
            self.authorization = m.get('Authorization')

        self.persistence_data_list = []
        if m.get('PersistenceDataList') is not None:
            for k1 in m.get('PersistenceDataList'):
                temp_model = main_models.BindContextsRequestPersistenceDataList()
                self.persistence_data_list.append(temp_model.from_map(k1))

        if m.get('SessionId') is not None:
            self.session_id = m.get('SessionId')

        return self

class BindContextsRequestPersistenceDataListMountConfig(DaraModel):
    def __init__(
        self,
        access_mode: str = None,
        storage_mode: str = None,
        object_key: str = None,
        source_path: str = None,
    ):
        self.access_mode = access_mode
        self.storage_mode = storage_mode
        self.object_key = object_key
        self.source_path = source_path

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.access_mode is not None:
            result['AccessMode'] = self.access_mode

        if self.storage_mode is not None:
            result['StorageMode'] = self.storage_mode

        if self.object_key is not None:
            result['ObjectKey'] = self.object_key

        if self.source_path is not None:
            result['SourcePath'] = self.source_path

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('AccessMode') is not None:
            self.access_mode = m.get('AccessMode')

        if m.get('StorageMode') is not None:
            self.storage_mode = m.get('StorageMode')

        if m.get('ObjectKey') is not None:
            self.object_key = m.get('ObjectKey')

        if m.get('SourcePath') is not None:
            self.source_path = m.get('SourcePath')

        return self


class BindContextsRequestPersistenceDataList(DaraModel):
    def __init__(
        self,
        context_id: str = None,
        path: str = None,
        policy: str = None,
        type: str = None,
        mount_config: BindContextsRequestPersistenceDataListMountConfig = None,
    ):
        self.context_id = context_id
        self.path = path
        self.policy = policy
        self.type = type
        self.mount_config = mount_config

    def validate(self):
        if self.mount_config:
            self.mount_config.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.context_id is not None:
            result['ContextId'] = self.context_id

        if self.path is not None:
            result['Path'] = self.path

        if self.policy is not None:
            result['Policy'] = self.policy

        if self.type is not None:
            result['Type'] = self.type

        if self.mount_config is not None:
            result['MountConfig'] = self.mount_config.to_map()

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get('ContextId') is not None:
            self.context_id = m.get('ContextId')

        if m.get('Path') is not None:
            self.path = m.get('Path')

        if m.get('Policy') is not None:
            self.policy = m.get('Policy')

        if m.get('Type') is not None:
            self.type = m.get('Type')

        if m.get('MountConfig') is not None:
            temp_model = BindContextsRequestPersistenceDataListMountConfig()
            self.mount_config = temp_model.from_map(m.get('MountConfig'))

        return self

