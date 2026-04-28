# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import Optional

from darabonba.model import DaraModel


class CreateMcpSessionShrinkRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        context_id: Optional[str] = None,
        external_user_id: Optional[str] = None,
        image_id: Optional[str] = None,
        timeout: Optional[int] = None,
        max_runtime: Optional[int] = None,
        manual_release: Optional[bool] = None,
        labels: Optional[str] = None,
        load_skill: Optional[bool] = None,
        mcp_policy_id: Optional[str] = None,
        network_id: Optional[str] = None,
        persistence_data_list_shrink: Optional[str] = None,
        session_id: Optional[str] = None,
        skills_shrink: Optional[str] = None,
        vpc_resource: Optional[bool] = None,
        extra_configs: Optional[str] = None,
        sdk_stats: Optional[str] = None,
        login_region_id: Optional[str] = None,
    ):
        self.authorization = authorization
        self.context_id = context_id
        self.external_user_id = external_user_id
        self.image_id = image_id
        self.timeout = timeout
        self.max_runtime = max_runtime
        self.manual_release = manual_release
        self.labels = labels
        self.load_skill = load_skill
        self.mcp_policy_id = mcp_policy_id
        self.network_id = network_id
        self.persistence_data_list_shrink = persistence_data_list_shrink
        self.session_id = session_id
        self.skills_shrink = skills_shrink
        self.vpc_resource = vpc_resource
        self.extra_configs = extra_configs
        self.sdk_stats = sdk_stats
        self.login_region_id = login_region_id

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization

        if self.context_id is not None:
            result["ContextId"] = self.context_id

        if self.external_user_id is not None:
            result["ExternalUserId"] = self.external_user_id

        if self.image_id is not None:
            result["ImageId"] = self.image_id

        if self.timeout is not None:
            result["Timeout"] = self.timeout

        if self.manual_release is not None:
            result["ManualRelease"] = self.manual_release

        if self.max_runtime is not None:
            result["MaxRuntime"] = self.max_runtime

        if self.labels is not None:
            result["Labels"] = self.labels

        if self.load_skill is not None:
            result["LoadSkill"] = self.load_skill

        if self.mcp_policy_id is not None:
            result["McpPolicyId"] = self.mcp_policy_id

        if self.network_id is not None:
            result["NetworkId"] = self.network_id

        if self.persistence_data_list_shrink is not None:
            result["PersistenceDataList"] = self.persistence_data_list_shrink

        if self.session_id is not None:
            result["SessionId"] = self.session_id

        if self.skills_shrink is not None:
            result["Skills"] = self.skills_shrink

        if self.vpc_resource is not None:
            result["VpcResource"] = self.vpc_resource

        if self.extra_configs is not None:
            result["ExtraConfigs"] = self.extra_configs

        if self.sdk_stats is not None:
            result["SdkStats"] = self.sdk_stats

        if self.login_region_id is not None:
            result["LoginRegionId"] = self.login_region_id

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("Authorization") is not None:
            self.authorization = m.get("Authorization")

        if m.get("ContextId") is not None:
            self.context_id = m.get("ContextId")

        if m.get("ExternalUserId") is not None:
            self.external_user_id = m.get("ExternalUserId")

        if m.get("ImageId") is not None:
            self.image_id = m.get("ImageId")

        if m.get("Timeout") is not None:
            self.timeout = m.get("Timeout")

        if m.get("ManualRelease") is not None:
            self.manual_release = m.get("ManualRelease")

        if m.get("MaxRuntime") is not None:
            self.max_runtime = m.get("MaxRuntime")

        if m.get("Labels") is not None:
            self.labels = m.get("Labels")

        if m.get("LoadSkill") is not None:
            self.load_skill = m.get("LoadSkill")

        if m.get("McpPolicyId") is not None:
            self.mcp_policy_id = m.get("McpPolicyId")

        if m.get("NetworkId") is not None:
            self.network_id = m.get("NetworkId")

        if m.get("PersistenceDataList") is not None:
            self.persistence_data_list_shrink = m.get("PersistenceDataList")

        if m.get("SessionId") is not None:
            self.session_id = m.get("SessionId")

        if m.get("Skills") is not None:
            self.skills_shrink = m.get("Skills")

        if m.get("VpcResource") is not None:
            self.vpc_resource = m.get("VpcResource")

        if m.get("ExtraConfigs") is not None:
            self.extra_configs = m.get("ExtraConfigs")

        if m.get("SdkStats") is not None:
            self.sdk_stats = m.get("SdkStats")

        if m.get("LoginRegionId") is not None:
            self.login_region_id = m.get("LoginRegionId")

        return self
