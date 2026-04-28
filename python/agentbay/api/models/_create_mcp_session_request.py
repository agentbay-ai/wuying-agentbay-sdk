# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List, Optional
from enum import Enum

from darabonba.model import DaraModel

from agentbay.api import models as main_models


class CreateMcpSessionRequest(DaraModel):
    def __init__(
        self,
        authorization: Optional[str] = None,
        context_id: Optional[str] = None,
        enable_record: Optional[bool] = None,
        external_user_id: Optional[str] = None,
        image_id: Optional[str] = None,
        timeout: Optional[int] = None,
        max_runtime: Optional[int] = None,
        manual_release: Optional[bool] = None,
        labels: Optional[str] = None,
        load_skill: Optional[bool] = None,
        mcp_policy_id: Optional[str] = None,
        network_id: Optional[str] = None,
        persistence_data_list: Optional[
            List[main_models.CreateMcpSessionRequestPersistenceDataList]
        ] = None,
        session_id: Optional[str] = None,
        skills: Optional[List[str]] = None,
        vpc_resource: Optional[bool] = None,
        extra_configs: Optional[main_models.ExtraConfigs] = None,
        sdk_stats: Optional[str] = None,
        login_region_id: Optional[str] = None,
    ):
        self.authorization = authorization
        self.context_id = context_id
        self.enable_record = enable_record
        self.external_user_id = external_user_id
        self.image_id = image_id
        self.timeout = timeout
        self.max_runtime = max_runtime
        self.manual_release = manual_release
        self.labels = labels
        self.load_skill = load_skill
        self.mcp_policy_id = mcp_policy_id
        self.network_id = network_id
        self.persistence_data_list = persistence_data_list
        self.session_id = session_id
        self.skills = skills
        self.vpc_resource = vpc_resource
        self.extra_configs = extra_configs
        self.sdk_stats = sdk_stats
        self.login_region_id = login_region_id

    def validate(self):
        if self.persistence_data_list:
            for v1 in self.persistence_data_list:
                if v1:
                    v1.validate()
        if self.extra_configs:
            self.extra_configs.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.authorization is not None:
            result["Authorization"] = self.authorization

        if self.context_id is not None:
            result["ContextId"] = self.context_id

        if self.enable_record is not None:
            result['EnableRecord'] = self.enable_record

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

        result["PersistenceDataList"] = []
        if self.persistence_data_list is not None:
            for k1 in self.persistence_data_list:
                result["PersistenceDataList"].append(k1.to_map() if k1 else None)

        if self.session_id is not None:
            result["SessionId"] = self.session_id

        if self.skills is not None:
            result["Skills"] = self.skills

        if self.vpc_resource is not None:
            result["VpcResource"] = self.vpc_resource

        if self.extra_configs is not None:
            result["ExtraConfigs"] = self.extra_configs.to_map()

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

        if m.get('EnableRecord') is not None:
            self.enable_record = m.get('EnableRecord')

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

        self.persistence_data_list = []
        if m.get("PersistenceDataList") is not None:
            for k1 in m.get("PersistenceDataList", []):
                temp_model = main_models.CreateMcpSessionRequestPersistenceDataList()
                self.persistence_data_list.append(temp_model.from_map(k1))

        if m.get("SessionId") is not None:
            self.session_id = m.get("SessionId")

        if m.get("Skills") is not None:
            self.skills = m.get("Skills")

        if m.get("VpcResource") is not None:
            self.vpc_resource = m.get("VpcResource")

        if m.get("ExtraConfigs") is not None:
            temp_model = main_models.ExtraConfigs()
            self.extra_configs = temp_model.from_map(m.get("ExtraConfigs"))

        if m.get("SdkStats") is not None:
            self.sdk_stats = m.get("SdkStats")

        if m.get("LoginRegionId") is not None:
            self.login_region_id = m.get("LoginRegionId")

        return self


class CreateMcpSessionRequestPersistenceDataList(DaraModel):
    def __init__(
        self,
        context_id: Optional[str] = None,
        path: Optional[str] = None,
        policy: Optional[str] = None,
    ):
        self.context_id = context_id
        self.path = path
        self.policy = policy

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.context_id is not None:
            result["ContextId"] = self.context_id

        if self.path is not None:
            result["Path"] = self.path

        if self.policy is not None:
            result["Policy"] = self.policy

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("ContextId") is not None:
            self.context_id = m.get("ContextId")

        if m.get("Path") is not None:
            self.path = m.get("Path")

        if m.get("Policy") is not None:
            self.policy = m.get("Policy")

        return self


class AppManagerRule(DaraModel):
    def __init__(
        self,
        rule_type: Optional[str] = None,
        app_package_name_list: Optional[List[str]] = None,
    ):
        self.rule_type = rule_type
        self.app_package_name_list = app_package_name_list

    def validate(self):
        if self.app_package_name_list:
            for v1 in self.app_package_name_list:
                if v1 and not isinstance(v1, str):
                    raise ValueError("app_package_name_list items must be strings")

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map

        if self.rule_type is not None:
            result["RuleType"] = self.rule_type

        result["AppPackageNameList"] = []
        if self.app_package_name_list is not None:
            result["AppPackageNameList"] = self.app_package_name_list

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("RuleType") is not None:
            self.rule_type = m.get("RuleType")

        if m.get("AppPackageNameList") is not None:
            self.app_package_name_list = m.get("AppPackageNameList", [])

        return self


class MobileSimulateMode(Enum):
    PROPERTIES_ONLY = "PropertiesOnly"
    SENSORS_ONLY = "SensorsOnly"
    PACKAGES_ONLY = "PackagesOnly"
    SERVICES_ONLY = "ServicesOnly"
    ALL = "All"


class MobileSimulateConfig(DaraModel):
    def __init__(
        self,
        simulate: bool = False,
        simulate_path: str = None,
        simulate_mode: Optional[MobileSimulateMode] = None,
        simulated_context_id: Optional[str] = None,
    ):
        self.simulate = simulate
        self.simulate_path = simulate_path
        self.simulate_mode = simulate_mode
        self.simulated_context_id = simulated_context_id

    def validate(self):
        if not self.simulate_path:
            raise ValueError("simulate_path is required")

class MobileExtraConfig(DaraModel):
    def __init__(
        self,
        lock_resolution: Optional[bool] = None,
        app_manager_rule: Optional[AppManagerRule] = None,
        hide_navigation_bar: Optional[bool] = None,
        uninstall_blacklist: Optional[List[str]] = None,
        simulate_config: Optional[MobileSimulateConfig] = None,
    ):
        self.lock_resolution = lock_resolution
        self.app_manager_rule = app_manager_rule
        self.hide_navigation_bar = hide_navigation_bar
        self.uninstall_blacklist = uninstall_blacklist
        self.simulate_config = simulate_config

    def validate(self):
        if self.app_manager_rule:
            self.app_manager_rule.validate()
        if self.uninstall_blacklist:
            for v1 in self.uninstall_blacklist:
                if v1 and not isinstance(v1, str):
                    raise ValueError("uninstall_blacklist items must be strings")
        if self.simulate_config:
            self.simulate_config.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map

        if self.lock_resolution is not None:
            result["LockResolution"] = self.lock_resolution

        if self.app_manager_rule is not None:
            result["AppManagerRule"] = self.app_manager_rule.to_map()

        if self.hide_navigation_bar is not None:
            result["HideNavigationBar"] = self.hide_navigation_bar

        if self.uninstall_blacklist is not None:
            result["UninstallBlacklist"] = self.uninstall_blacklist

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("LockResolution") is not None:
            self.lock_resolution = m.get("LockResolution")

        if m.get("AppManagerRule") is not None:
            temp_model = AppManagerRule()
            self.app_manager_rule = temp_model.from_map(m.get("AppManagerRule"))

        if m.get("HideNavigationBar") is not None:
            self.hide_navigation_bar = m.get("HideNavigationBar")

        if m.get("UninstallBlacklist") is not None:
            self.uninstall_blacklist = m.get("UninstallBlacklist", [])

        return self


class ExtraConfigs(DaraModel):
    def __init__(
        self,
        mobile: Optional[MobileExtraConfig] = None,
    ):
        self.mobile = mobile

    def validate(self):
        if self.mobile:
            self.mobile.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map

        if self.mobile is not None:
            result["Mobile"] = self.mobile.to_map()

        return result

    def from_map(self, m: Optional[dict] = None):
        m = m or dict()
        if m.get("Mobile") is not None:
            temp_model = MobileExtraConfig()
            self.mobile = temp_model.from_map(m.get("Mobile"))

        return self
