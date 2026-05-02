# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

import json
from typing import Dict

from alibabacloud_tea_openapi import utils_models as open_api_util_models
from alibabacloud_tea_openapi.client import Client as OpenApiClient
from alibabacloud_tea_openapi.utils import Utils
from darabonba.core import DaraCore as DaraCore
from darabonba.runtime import RuntimeOptions

from agentbay.api import models as main_models

"""
"""


class Client(OpenApiClient):

    def __init__(
        self,
        config: open_api_util_models.Config,
    ):
        super().__init__(config)
        self._signature_algorithm = "v2"
        self._endpoint_rule = ""
        self._signature_algorithm = "v2"
        self._endpoint_rule = ""
        self.check_config(config)
        self._endpoint = self.get_endpoint(
            "wuyingai",
            "",
            self._endpoint_rule,
            self._network,
            self._suffix,
            self._endpoint_map,
            self._endpoint,
        )

    def get_endpoint(
        self,
        product_id: str,
        region_id: str,
        endpoint_rule: str,
        network: str,
        suffix: str,
        endpoint_map: Dict[str, str],
        endpoint: str,
    ) -> str:
        if not DaraCore.is_null(endpoint):
            return endpoint
        if not DaraCore.is_null(endpoint_map) and not DaraCore.is_null(
            endpoint_map.get(region_id)
        ):
            return endpoint_map.get(region_id)
        return Utils.get_endpoint_rules(
            product_id, region_id, endpoint_rule, network, suffix
        )

    def call_mcp_tool_with_options(
        self,
        request: main_models.CallMcpToolRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CallMcpToolResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.args):
            body["Args"] = request.args
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.auto_gen_session):
            body["AutoGenSession"] = request.auto_gen_session
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.server):
            body["Server"] = request.server
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.tool):
            body["Tool"] = request.tool
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CallMcpTool",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CallMcpToolResponse(), self.call_api(params, req, runtime)
        )

    async def call_mcp_tool_with_options_async(
        self,
        request: main_models.CallMcpToolRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CallMcpToolResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.args):
            body["Args"] = request.args
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.auto_gen_session):
            body["AutoGenSession"] = request.auto_gen_session
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.server):
            body["Server"] = request.server
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.tool):
            body["Tool"] = request.tool
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CallMcpTool",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CallMcpToolResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def call_mcp_tool(
        self,
        request: main_models.CallMcpToolRequest,
        read_timeout: int = None,
        connect_timeout: int = None,
    ) -> main_models.CallMcpToolResponse:
        runtime = RuntimeOptions(
            read_timeout=read_timeout, connect_timeout=connect_timeout
        )
        return self.call_mcp_tool_with_options(request, runtime)

    async def call_mcp_tool_async(
        self,
        request: main_models.CallMcpToolRequest,
        read_timeout: int = None,
        connect_timeout: int = None,
    ) -> main_models.CallMcpToolResponse:
        runtime = RuntimeOptions(
            read_timeout=read_timeout, connect_timeout=connect_timeout
        )
        return await self.call_mcp_tool_with_options_async(request, runtime)

    def clear_context_with_options(
        self,
        request: main_models.ClearContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ClearContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ClearContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ClearContextResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def clear_context_with_options_async(
        self,
        request: main_models.ClearContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ClearContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ClearContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ClearContextResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def clear_context(
        self,
        request: main_models.ClearContextRequest,
    ) -> main_models.ClearContextResponse:
        runtime = RuntimeOptions()
        return self.clear_context_with_options(request, runtime)

    async def clear_context_async(
        self,
        request: main_models.ClearContextRequest,
    ) -> main_models.ClearContextResponse:
        runtime = RuntimeOptions()
        return await self.clear_context_with_options_async(request, runtime)

    def create_mcp_session_with_options(
        self,
        tmp_req: main_models.CreateMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateMcpSessionResponse:
        tmp_req.validate()
        request = main_models.CreateMcpSessionShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.persistence_data_list):
            request.persistence_data_list_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.persistence_data_list, "PersistenceDataList", "json"
                )
            )
        if not DaraCore.is_null(tmp_req.skills):
            request.skills_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.skills, "Skills", "json"
                )
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.timeout):
            body["Timeout"] = request.timeout
        if not DaraCore.is_null(request.max_runtime):
            body["MaxRuntime"] = request.max_runtime
        if not DaraCore.is_null(request.manual_release):
            body["ManualRelease"] = request.manual_release
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.load_skill):
            body["LoadSkill"] = request.load_skill
        if not DaraCore.is_null(request.mcp_policy_id):
            body["McpPolicyId"] = request.mcp_policy_id
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        if not DaraCore.is_null(request.persistence_data_list_shrink):
            body["PersistenceDataList"] = request.persistence_data_list_shrink
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.skills_shrink):
            body["Skills"] = request.skills_shrink
        if not DaraCore.is_null(request.vpc_resource):
            body["VpcResource"] = request.vpc_resource
        if not DaraCore.is_null(request.extra_configs):
            body["ExtraConfigs"] = request.extra_configs
        if not DaraCore.is_null(request.sdk_stats):
            body["SdkStats"] = request.sdk_stats
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        # Add EnableRecord field from tmp_req (not in CreateMcpSessionShrinkRequest)
        if tmp_req.enable_record is not None:
            body["EnableRecord"] = tmp_req.enable_record
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateMcpSessionResponse(), self.call_api(params, req, runtime)
        )

    async def create_mcp_session_with_options_async(
        self,
        tmp_req: main_models.CreateMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateMcpSessionResponse:
        tmp_req.validate()
        request = main_models.CreateMcpSessionShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.persistence_data_list):
            request.persistence_data_list_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.persistence_data_list, "PersistenceDataList", "json"
                )
            )
        if not DaraCore.is_null(tmp_req.skills):
            request.skills_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.skills, "Skills", "json"
                )
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.external_user_id):
            body["ExternalUserId"] = request.external_user_id
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.timeout):
            body["Timeout"] = request.timeout
        if not DaraCore.is_null(request.max_runtime):
            body["MaxRuntime"] = request.max_runtime
        if not DaraCore.is_null(request.manual_release):
            body["ManualRelease"] = request.manual_release
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.load_skill):
            body["LoadSkill"] = request.load_skill
        if not DaraCore.is_null(request.mcp_policy_id):
            body["McpPolicyId"] = request.mcp_policy_id
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        if not DaraCore.is_null(request.persistence_data_list_shrink):
            body["PersistenceDataList"] = request.persistence_data_list_shrink
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.skills_shrink):
            body["Skills"] = request.skills_shrink
        if not DaraCore.is_null(request.vpc_resource):
            body["VpcResource"] = request.vpc_resource
        if not DaraCore.is_null(request.extra_configs):
            body["ExtraConfigs"] = request.extra_configs
        if not DaraCore.is_null(request.sdk_stats):
            body["SdkStats"] = request.sdk_stats
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        # Add EnableRecord field from tmp_req (not in CreateMcpSessionShrinkRequest)
        if tmp_req.enable_record is not None:
            body["EnableRecord"] = tmp_req.enable_record
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateMcpSessionResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def create_mcp_session(
        self,
        request: main_models.CreateMcpSessionRequest,
    ) -> main_models.CreateMcpSessionResponse:
        runtime = RuntimeOptions()
        return self.create_mcp_session_with_options(request, runtime)

    async def create_mcp_session_async(
        self,
        request: main_models.CreateMcpSessionRequest,
    ) -> main_models.CreateMcpSessionResponse:
        runtime = RuntimeOptions()
        return await self.create_mcp_session_with_options_async(request, runtime)

    def create_network_with_options(
        self,
        request: main_models.CreateNetworkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateNetworkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateNetwork",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateNetworkResponse(), self.call_api(params, req, runtime)
        )

    async def create_network_with_options_async(
        self,
        request: main_models.CreateNetworkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.CreateNetworkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="CreateNetwork",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.CreateNetworkResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def create_network(
        self,
        request: main_models.CreateNetworkRequest,
    ) -> main_models.CreateNetworkResponse:
        runtime = RuntimeOptions()
        return self.create_network_with_options(request, runtime)

    async def create_network_async(
        self,
        request: main_models.CreateNetworkRequest,
    ) -> main_models.CreateNetworkResponse:
        runtime = RuntimeOptions()
        return await self.create_network_with_options_async(request, runtime)

    def describe_network_with_options(
        self,
        request: main_models.DescribeNetworkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeNetworkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DescribeNetwork",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeNetworkResponse(), self.call_api(params, req, runtime)
        )

    async def describe_network_with_options_async(
        self,
        request: main_models.DescribeNetworkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeNetworkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.network_id):
            body["NetworkId"] = request.network_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DescribeNetwork",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeNetworkResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def describe_network(
        self,
        request: main_models.DescribeNetworkRequest,
    ) -> main_models.DescribeNetworkResponse:
        runtime = RuntimeOptions()
        return self.describe_network_with_options(request, runtime)

    async def describe_network_async(
        self,
        request: main_models.DescribeNetworkRequest,
    ) -> main_models.DescribeNetworkResponse:
        runtime = RuntimeOptions()
        return await self.describe_network_with_options_async(request, runtime)

    def delete_context_with_options(
        self,
        request: main_models.DeleteContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DeleteContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DeleteContextResponse(), self.call_api(params, req, runtime)
        )

    async def delete_context_with_options_async(
        self,
        request: main_models.DeleteContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DeleteContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DeleteContextResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def delete_context(
        self,
        request: main_models.DeleteContextRequest,
    ) -> main_models.DeleteContextResponse:
        runtime = RuntimeOptions()
        return self.delete_context_with_options(request, runtime)

    async def delete_context_async(
        self,
        request: main_models.DeleteContextRequest,
    ) -> main_models.DeleteContextResponse:
        runtime = RuntimeOptions()
        return await self.delete_context_with_options_async(request, runtime)

    def delete_session_async_with_options(
        self,
        request: main_models.DeleteSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body['Authorization'] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body['SessionId'] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            body = Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action = 'DeleteSessionAsync',
            version = '2025-05-06',
            protocol = 'HTTPS',
            pathname = '/',
            method = 'POST',
            auth_type = 'Anonymous',
            style = 'RPC',
            req_body_type = 'formData',
            body_type = 'json'
        )
        return DaraCore.from_map(
            main_models.DeleteSessionAsyncResponse(),
            self.do_rpcrequest(params.action, params.version, params.protocol, params.method, params.auth_type, params.body_type, req, runtime)
        )

    async def delete_session_async_with_options_async(
        self,
        request: main_models.DeleteSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body['Authorization'] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body['SessionId'] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            body = Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action = 'DeleteSessionAsync',
            version = '2025-05-06',
            protocol = 'HTTPS',
            pathname = '/',
            method = 'POST',
            auth_type = 'Anonymous',
            style = 'RPC',
            req_body_type = 'formData',
            body_type = 'json'
        )
        return DaraCore.from_map(
            main_models.DeleteSessionAsyncResponse(),
            await self.do_rpcrequest_async(params.action, params.version, params.protocol, params.method, params.auth_type, params.body_type, req, runtime)
        )

    def delete_session_async(
        self,
        request: main_models.DeleteSessionAsyncRequest,
    ) -> main_models.DeleteSessionAsyncResponse:
        runtime = RuntimeOptions()
        return self.delete_session_async_with_options(request, runtime)

    async def delete_session_async_async(
        self,
        request: main_models.DeleteSessionAsyncRequest,
    ) -> main_models.DeleteSessionAsyncResponse:
        runtime = RuntimeOptions()
        return await self.delete_session_async_with_options_async(request, runtime)

    def get_and_load_internal_context_with_options(
        self,
        request: main_models.GetAndLoadInternalContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetAndLoadInternalContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body['Authorization'] = request.authorization
        if not DaraCore.is_null(request.context_types):
            body['ContextTypes'] = request.context_types
        if not DaraCore.is_null(request.session_id):
            body['SessionId'] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            body = Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action = 'GetAndLoadInternalContext',
            version = '2025-05-06',
            protocol = 'HTTPS',
            pathname = '/',
            method = 'POST',
            auth_type = 'Anonymous',
            style = 'RPC',
            req_body_type = 'formData',
            body_type = 'json'
        )
        return DaraCore.from_map(
            main_models.GetAndLoadInternalContextResponse(),
            self.do_rpcrequest(params.action, params.version, params.protocol, params.method, params.auth_type, params.body_type, req, runtime)
        )

    async def get_and_load_internal_context_with_options_async(
        self,
        request: main_models.GetAndLoadInternalContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetAndLoadInternalContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body['Authorization'] = request.authorization
        if not DaraCore.is_null(request.context_types):
            body['ContextTypes'] = request.context_types
        if not DaraCore.is_null(request.session_id):
            body['SessionId'] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            body = Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action = 'GetAndLoadInternalContext',
            version = '2025-05-06',
            protocol = 'HTTPS',
            pathname = '/',
            method = 'POST',
            auth_type = 'Anonymous',
            style = 'RPC',
            req_body_type = 'formData',
            body_type = 'json'
        )
        return DaraCore.from_map(
            main_models.GetAndLoadInternalContextResponse(),
            await self.do_rpcrequest_async(params.action, params.version, params.protocol, params.method, params.auth_type, params.body_type, req, runtime)
        )

    def get_and_load_internal_context(
        self,
        request: main_models.GetAndLoadInternalContextRequest,
    ) -> main_models.GetAndLoadInternalContextResponse:
        runtime = RuntimeOptions()
        return self.get_and_load_internal_context_with_options(request, runtime)

    async def get_and_load_internal_context_async(
        self,
        request: main_models.GetAndLoadInternalContextRequest,
    ) -> main_models.GetAndLoadInternalContextResponse:
        runtime = RuntimeOptions()
        return await self.get_and_load_internal_context_with_options_async(request, runtime)

    def get_context_with_options(
        self,
        request: main_models.GetContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.allow_create):
            body["AllowCreate"] = request.allow_create
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextResponse(), self.call_api(params, req, runtime)
        )

    async def get_context_with_options_async(
        self,
        request: main_models.GetContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.allow_create):
            body["AllowCreate"] = request.allow_create
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        if not DaraCore.is_null(request.login_region_id):
            body["LoginRegionId"] = request.login_region_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_context(
        self,
        request: main_models.GetContextRequest,
    ) -> main_models.GetContextResponse:
        runtime = RuntimeOptions()
        return self.get_context_with_options(request, runtime)

    async def get_context_async(
        self,
        request: main_models.GetContextRequest,
    ) -> main_models.GetContextResponse:
        runtime = RuntimeOptions()
        return await self.get_context_with_options_async(request, runtime)

    def get_context_info_with_options(
        self,
        request: main_models.GetContextInfoRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextInfoResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.path):
            body["Path"] = request.path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.task_type):
            body["TaskType"] = request.task_type
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextInfo",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextInfoResponse(), self.call_api(params, req, runtime)
        )

    async def get_context_info_with_options_async(
        self,
        request: main_models.GetContextInfoRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextInfoResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.path):
            body["Path"] = request.path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.task_type):
            body["TaskType"] = request.task_type
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextInfo",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextInfoResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_context_info(
        self,
        request: main_models.GetContextInfoRequest,
    ) -> main_models.GetContextInfoResponse:
        runtime = RuntimeOptions()
        return self.get_context_info_with_options(request, runtime)

    async def get_context_info_async(
        self,
        request: main_models.GetContextInfoRequest,
    ) -> main_models.GetContextInfoResponse:
        runtime = RuntimeOptions()
        return await self.get_context_info_with_options_async(request, runtime)

    def get_label_with_options(
        self,
        request: main_models.GetLabelRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetLabelResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetLabel",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetLabelResponse(), self.call_api(params, req, runtime)
        )

    async def get_label_with_options_async(
        self,
        request: main_models.GetLabelRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetLabelResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetLabel",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetLabelResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_label(
        self,
        request: main_models.GetLabelRequest,
    ) -> main_models.GetLabelResponse:
        runtime = RuntimeOptions()
        return self.get_label_with_options(request, runtime)

    async def get_label_async(
        self,
        request: main_models.GetLabelRequest,
    ) -> main_models.GetLabelResponse:
        runtime = RuntimeOptions()
        return await self.get_label_with_options_async(request, runtime)

    def get_session_with_options(
        self,
        request: main_models.GetSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSessionResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def get_session_with_options_async(
        self,
        request: main_models.GetSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSessionResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def get_session(
        self,
        request: main_models.GetSessionRequest,
    ) -> main_models.GetSessionResponse:
        runtime = RuntimeOptions()
        return self.get_session_with_options(request, runtime)

    async def get_session_async(
        self,
        request: main_models.GetSessionRequest,
    ) -> main_models.GetSessionResponse:
        runtime = RuntimeOptions()
        return await self.get_session_with_options_async(request, runtime)

    def get_session_detail_with_options(
        self,
        request: main_models.GetSessionDetailRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSessionDetailResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.session_id):
            query["SessionId"] = request.session_id
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="GetSessionDetail",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSessionDetailResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def get_session_detail_with_options_async(
        self,
        request: main_models.GetSessionDetailRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSessionDetailResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.session_id):
            query["SessionId"] = request.session_id
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="GetSessionDetail",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSessionDetailResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def get_session_detail(
        self,
        request: main_models.GetSessionDetailRequest,
    ) -> main_models.GetSessionDetailResponse:
        runtime = RuntimeOptions()
        return self.get_session_detail_with_options(request, runtime)

    async def get_session_detail_async(
        self,
        request: main_models.GetSessionDetailRequest,
    ) -> main_models.GetSessionDetailResponse:
        runtime = RuntimeOptions()
        return await self.get_session_detail_with_options_async(request, runtime)

    def get_link_with_options(
        self,
        request: main_models.GetLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.port):
            body["Port"] = request.port
        if not DaraCore.is_null(request.protocol_type):
            body["ProtocolType"] = request.protocol_type
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.options):
            body["Option"] = request.options
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetLinkResponse(), self.call_api(params, req, runtime)
        )

    async def get_link_with_options_async(
        self,
        request: main_models.GetLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.port):
            body["Port"] = request.port
        if not DaraCore.is_null(request.protocol_type):
            body["ProtocolType"] = request.protocol_type
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.options):
            body["Option"] = request.options
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetLinkResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_link(
        self,
        request: main_models.GetLinkRequest,
    ) -> main_models.GetLinkResponse:
        runtime = RuntimeOptions()
        return self.get_link_with_options(request, runtime)

    async def get_link_async(
        self,
        request: main_models.GetLinkRequest,
    ) -> main_models.GetLinkResponse:
        runtime = RuntimeOptions()
        return await self.get_link_with_options_async(request, runtime)

    def pause_session_async_with_options(
        self,
        request: main_models.PauseSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.PauseSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="PauseSessionAsync",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.PauseSessionAsyncResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def pause_session_async_with_options_async(
        self,
        request: main_models.PauseSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.PauseSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="PauseSessionAsync",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.PauseSessionAsyncResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def pause_session_async(
        self,
        request: main_models.PauseSessionAsyncRequest,
    ) -> main_models.PauseSessionAsyncResponse:
        runtime = RuntimeOptions()
        return self.pause_session_async_with_options(request, runtime)

    async def pause_session_async_async(
        self,
        request: main_models.PauseSessionAsyncRequest,
    ) -> main_models.PauseSessionAsyncResponse:
        runtime = RuntimeOptions()
        return await self.pause_session_async_with_options_async(request, runtime)

    def refresh_session_idle_time_with_options(
        self,
        request: main_models.RefreshSessionIdleTimeRequest,
        runtime: RuntimeOptions,
    ) -> main_models.RefreshSessionIdleTimeResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="RefreshSessionIdleTime",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.RefreshSessionIdleTimeResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def refresh_session_idle_time_with_options_async(
        self,
        request: main_models.RefreshSessionIdleTimeRequest,
        runtime: RuntimeOptions,
    ) -> main_models.RefreshSessionIdleTimeResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="RefreshSessionIdleTime",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.RefreshSessionIdleTimeResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def refresh_session_idle_time(
        self,
        request: main_models.RefreshSessionIdleTimeRequest,
    ) -> main_models.RefreshSessionIdleTimeResponse:
        runtime = RuntimeOptions()
        return self.refresh_session_idle_time_with_options(request, runtime)

    async def refresh_session_idle_time_async(
        self,
        request: main_models.RefreshSessionIdleTimeRequest,
    ) -> main_models.RefreshSessionIdleTimeResponse:
        runtime = RuntimeOptions()
        return await self.refresh_session_idle_time_with_options_async(request, runtime)

    def resume_session_async_with_options(
        self,
        request: main_models.ResumeSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ResumeSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ResumeSessionAsync",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ResumeSessionAsyncResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def resume_session_async_with_options_async(
        self,
        request: main_models.ResumeSessionAsyncRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ResumeSessionAsyncResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ResumeSessionAsync",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ResumeSessionAsyncResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def resume_session_async(
        self,
        request: main_models.ResumeSessionAsyncRequest,
    ) -> main_models.ResumeSessionAsyncResponse:
        runtime = RuntimeOptions()
        return self.resume_session_async_with_options(request, runtime)

    async def resume_session_async_async(
        self,
        request: main_models.ResumeSessionAsyncRequest,
    ) -> main_models.ResumeSessionAsyncResponse:
        runtime = RuntimeOptions()
        return await self.resume_session_async_with_options_async(request, runtime)

    def get_mcp_resource_with_options(
        self,
        request: main_models.GetMcpResourceRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetMcpResourceResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetMcpResource",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetMcpResourceResponse(), self.call_api(params, req, runtime)
        )

    async def get_mcp_resource_with_options_async(
        self,
        request: main_models.GetMcpResourceRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetMcpResourceResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetMcpResource",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetMcpResourceResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_mcp_resource(
        self,
        request: main_models.GetMcpResourceRequest,
    ) -> main_models.GetMcpResourceResponse:
        runtime = RuntimeOptions()
        return self.get_mcp_resource_with_options(request, runtime)

    async def get_mcp_resource_async(
        self,
        request: main_models.GetMcpResourceRequest,
    ) -> main_models.GetMcpResourceResponse:
        runtime = RuntimeOptions()
        return await self.get_mcp_resource_with_options_async(request, runtime)

    def init_browser_with_options(
        self,
        request: main_models.InitBrowserRequest,
        runtime: RuntimeOptions,
    ) -> main_models.InitBrowserResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.persistent_path):
            body["PersistentPath"] = request.persistent_path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.browser_option):
            body["BrowserOption"] = json.dumps(request.browser_option)
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="InitBrowser",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.InitBrowserResponse(), self.call_api(params, req, runtime)
        )

    async def init_browser_with_options_async(
        self,
        request: main_models.InitBrowserRequest,
        runtime: RuntimeOptions,
    ) -> main_models.InitBrowserResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.persistent_path):
            body["PersistentPath"] = request.persistent_path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.browser_option):
            body["BrowserOption"] = json.dumps(request.browser_option)
        body_map = Utils.parse_to_map(body)
        req = open_api_util_models.OpenApiRequest(body=body_map)
        params = open_api_util_models.Params(
            action="InitBrowser",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.InitBrowserResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def init_browser(
        self,
        request: main_models.InitBrowserRequest,
    ) -> main_models.InitBrowserResponse:
        runtime = RuntimeOptions()
        return self.init_browser_with_options(request, runtime)

    async def init_browser_async(
        self,
        request: main_models.InitBrowserRequest,
    ) -> main_models.InitBrowserResponse:
        runtime = RuntimeOptions()
        return await self.init_browser_with_options_async(request, runtime)

    def list_contexts_with_options(
        self,
        request: main_models.ListContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListContextsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.type):
            body["ContextType"] = request.type
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListContextsResponse(), self.call_api(params, req, runtime)
        )

    async def list_contexts_with_options_async(
        self,
        request: main_models.ListContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListContextsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        if not DaraCore.is_null(request.type):
            body["ContextType"] = request.type
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListContextsResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def list_contexts(
        self,
        request: main_models.ListContextsRequest,
    ) -> main_models.ListContextsResponse:
        runtime = RuntimeOptions()
        return self.list_contexts_with_options(request, runtime)

    async def list_contexts_async(
        self,
        request: main_models.ListContextsRequest,
    ) -> main_models.ListContextsResponse:
        runtime = RuntimeOptions()
        return await self.list_contexts_with_options_async(request, runtime)

    def list_mcp_tools_with_options(
        self,
        request: main_models.ListMcpToolsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListMcpToolsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListMcpTools",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListMcpToolsResponse(), self.call_api(params, req, runtime)
        )

    async def list_mcp_tools_with_options_async(
        self,
        request: main_models.ListMcpToolsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListMcpToolsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListMcpTools",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListMcpToolsResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def list_mcp_tools(
        self,
        request: main_models.ListMcpToolsRequest,
    ) -> main_models.ListMcpToolsResponse:
        runtime = RuntimeOptions()
        return self.list_mcp_tools_with_options(request, runtime)

    async def list_mcp_tools_async(
        self,
        request: main_models.ListMcpToolsRequest,
    ) -> main_models.ListMcpToolsResponse:
        runtime = RuntimeOptions()
        return await self.list_mcp_tools_with_options_async(request, runtime)

    def list_session_with_options(
        self,
        request: main_models.ListSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.status):
            body["Status"] = request.status
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListSessionResponse(), self.call_api(params, req, runtime)
        )

    async def list_session_with_options_async(
        self,
        request: main_models.ListSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.max_results):
            body["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            body["NextToken"] = request.next_token
        if not DaraCore.is_null(request.status):
            body["Status"] = request.status
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListSessionResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def list_session(
        self,
        request: main_models.ListSessionRequest,
    ) -> main_models.ListSessionResponse:
        runtime = RuntimeOptions()
        return self.list_session_with_options(request, runtime)

    async def list_session_async(
        self,
        request: main_models.ListSessionRequest,
    ) -> main_models.ListSessionResponse:
        runtime = RuntimeOptions()
        return await self.list_session_with_options_async(request, runtime)

    def list_skill_meta_data_with_options(
        self,
        request: main_models.ListSkillMetaDataRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListSkillMetaDataResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListSkillMetaData",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListSkillMetaDataResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def list_skill_meta_data_with_options_async(
        self,
        request: main_models.ListSkillMetaDataRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ListSkillMetaDataResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ListSkillMetaData",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ListSkillMetaDataResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def list_skill_meta_data(
        self,
        request: main_models.ListSkillMetaDataRequest,
    ) -> main_models.ListSkillMetaDataResponse:
        runtime = RuntimeOptions()
        return self.list_skill_meta_data_with_options(request, runtime)

    async def list_skill_meta_data_async(
        self,
        request: main_models.ListSkillMetaDataRequest,
    ) -> main_models.ListSkillMetaDataResponse:
        runtime = RuntimeOptions()
        return await self.list_skill_meta_data_with_options_async(request, runtime)

    def get_skill_meta_data_with_options(
        self,
        tmp_req: main_models.GetSkillMetaDataRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSkillMetaDataResponse:
        tmp_req.validate()
        request = main_models.GetSkillMetaDataShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.skill_group_ids):
            request.skill_group_ids_shrink = Utils.array_to_string_with_specified_style(
                tmp_req.skill_group_ids, "SkillGroupIds", "json"
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.skill_group_ids_shrink):
            body["SkillGroupIds"] = request.skill_group_ids_shrink
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetSkillMetaData",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSkillMetaDataResponse(),
            self.call_api(params, req, runtime),
        )

    async def get_skill_meta_data_with_options_async(
        self,
        tmp_req: main_models.GetSkillMetaDataRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetSkillMetaDataResponse:
        tmp_req.validate()
        request = main_models.GetSkillMetaDataShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.skill_group_ids):
            request.skill_group_ids_shrink = Utils.array_to_string_with_specified_style(
                tmp_req.skill_group_ids, "SkillGroupIds", "json"
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.image_id):
            body["ImageId"] = request.image_id
        if not DaraCore.is_null(request.skill_group_ids_shrink):
            body["SkillGroupIds"] = request.skill_group_ids_shrink
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetSkillMetaData",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetSkillMetaDataResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_skill_meta_data(
        self,
        request: main_models.GetSkillMetaDataRequest,
    ) -> main_models.GetSkillMetaDataResponse:
        runtime = RuntimeOptions()
        return self.get_skill_meta_data_with_options(request, runtime)

    async def get_skill_meta_data_async(
        self,
        request: main_models.GetSkillMetaDataRequest,
    ) -> main_models.GetSkillMetaDataResponse:
        runtime = RuntimeOptions()
        return await self.get_skill_meta_data_with_options_async(request, runtime)

    def modify_context_with_options(
        self,
        request: main_models.ModifyContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ModifyContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ModifyContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ModifyContextResponse(), self.call_api(params, req, runtime)
        )

    async def modify_context_with_options_async(
        self,
        request: main_models.ModifyContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ModifyContextResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.id):
            body["Id"] = request.id
        if not DaraCore.is_null(request.name):
            body["Name"] = request.name
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ModifyContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ModifyContextResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def modify_context(
        self,
        request: main_models.ModifyContextRequest,
    ) -> main_models.ModifyContextResponse:
        runtime = RuntimeOptions()
        return self.modify_context_with_options(request, runtime)

    async def modify_context_async(
        self,
        request: main_models.ModifyContextRequest,
    ) -> main_models.ModifyContextResponse:
        runtime = RuntimeOptions()
        return await self.modify_context_with_options_async(request, runtime)

    def release_mcp_session_with_options(
        self,
        request: main_models.ReleaseMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ReleaseMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ReleaseMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ReleaseMcpSessionResponse(), self.call_api(params, req, runtime)
        )

    async def release_mcp_session_with_options_async(
        self,
        request: main_models.ReleaseMcpSessionRequest,
        runtime: RuntimeOptions,
    ) -> main_models.ReleaseMcpSessionResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="ReleaseMcpSession",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.ReleaseMcpSessionResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def release_mcp_session(
        self,
        request: main_models.ReleaseMcpSessionRequest,
    ) -> main_models.ReleaseMcpSessionResponse:
        runtime = RuntimeOptions()
        return self.release_mcp_session_with_options(request, runtime)

    async def release_mcp_session_async(
        self,
        request: main_models.ReleaseMcpSessionRequest,
    ) -> main_models.ReleaseMcpSessionResponse:
        runtime = RuntimeOptions()
        return await self.release_mcp_session_with_options_async(request, runtime)

    def set_label_with_options(
        self,
        request: main_models.SetLabelRequest,
        runtime: RuntimeOptions,
    ) -> main_models.SetLabelResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="SetLabel",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.SetLabelResponse(), self.call_api(params, req, runtime)
        )

    async def set_label_with_options_async(
        self,
        request: main_models.SetLabelRequest,
        runtime: RuntimeOptions,
    ) -> main_models.SetLabelResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.labels):
            body["Labels"] = request.labels
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="SetLabel",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.SetLabelResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def set_label(
        self,
        request: main_models.SetLabelRequest,
    ) -> main_models.SetLabelResponse:
        runtime = RuntimeOptions()
        return self.set_label_with_options(request, runtime)

    async def set_label_async(
        self,
        request: main_models.SetLabelRequest,
    ) -> main_models.SetLabelResponse:
        runtime = RuntimeOptions()
        return await self.set_label_with_options_async(request, runtime)

    def sync_context_with_options(
        self,
        request: main_models.SyncContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.SyncContextResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.authorization):
            query["Authorization"] = request.authorization
        body = {}
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.mode):
            body["Mode"] = request.mode
        if not DaraCore.is_null(request.path):
            body["Path"] = request.path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="SyncContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.SyncContextResponse(), self.call_api(params, req, runtime)
        )

    async def sync_context_with_options_async(
        self,
        request: main_models.SyncContextRequest,
        runtime: RuntimeOptions,
    ) -> main_models.SyncContextResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.authorization):
            query["Authorization"] = request.authorization
        body = {}
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.mode):
            body["Mode"] = request.mode
        if not DaraCore.is_null(request.path):
            body["Path"] = request.path
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="SyncContext",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.SyncContextResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def sync_context(
        self,
        request: main_models.SyncContextRequest,
    ) -> main_models.SyncContextResponse:
        runtime = RuntimeOptions()
        return self.sync_context_with_options(request, runtime)

    async def sync_context_async(
        self,
        request: main_models.SyncContextRequest,
    ) -> main_models.SyncContextResponse:
        runtime = RuntimeOptions()
        return await self.sync_context_with_options_async(request, runtime)

    def delete_context_file_with_options(
        self,
        request: main_models.DeleteContextFileRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteContextFileResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DeleteContextFile",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DeleteContextFileResponse(), self.call_api(params, req, runtime)
        )

    async def delete_context_file_with_options_async(
        self,
        request: main_models.DeleteContextFileRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DeleteContextFileResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DeleteContextFile",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DeleteContextFileResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def delete_context_file(
        self,
        request: main_models.DeleteContextFileRequest,
    ) -> main_models.DeleteContextFileResponse:
        runtime = RuntimeOptions()
        return self.delete_context_file_with_options(request, runtime)

    async def delete_context_file_async(
        self,
        request: main_models.DeleteContextFileRequest,
    ) -> main_models.DeleteContextFileResponse:
        runtime = RuntimeOptions()
        return await self.delete_context_file_with_options_async(request, runtime)

    def describe_context_files_with_options(
        self,
        request: main_models.DescribeContextFilesRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeContextFilesResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.max_results):
            query["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            query["NextToken"] = request.next_token
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.page_number):
            body["PageNumber"] = request.page_number
        if not DaraCore.is_null(request.page_size):
            body["PageSize"] = request.page_size
        if not DaraCore.is_null(request.parent_folder_path):
            body["ParentFolderPath"] = request.parent_folder_path
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="DescribeContextFiles",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeContextFilesResponse(),
            self.call_api(params, req, runtime),
        )

    async def describe_context_files_with_options_async(
        self,
        request: main_models.DescribeContextFilesRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeContextFilesResponse:
        request.validate()
        query = {}
        if not DaraCore.is_null(request.max_results):
            query["MaxResults"] = request.max_results
        if not DaraCore.is_null(request.next_token):
            query["NextToken"] = request.next_token
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.page_number):
            body["PageNumber"] = request.page_number
        if not DaraCore.is_null(request.page_size):
            body["PageSize"] = request.page_size
        if not DaraCore.is_null(request.parent_folder_path):
            body["ParentFolderPath"] = request.parent_folder_path
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        req = open_api_util_models.OpenApiRequest(
            query=Utils.query(query), body=Utils.parse_to_map(body)
        )
        params = open_api_util_models.Params(
            action="DescribeContextFiles",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeContextFilesResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def describe_context_files(
        self,
        request: main_models.DescribeContextFilesRequest,
    ) -> main_models.DescribeContextFilesResponse:
        runtime = RuntimeOptions()
        return self.describe_context_files_with_options(request, runtime)

    async def describe_context_files_async(
        self,
        request: main_models.DescribeContextFilesRequest,
    ) -> main_models.DescribeContextFilesResponse:
        runtime = RuntimeOptions()
        return await self.describe_context_files_with_options_async(request, runtime)

    def get_context_file_download_url_with_options(
        self,
        request: main_models.GetContextFileDownloadUrlRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextFileDownloadUrlResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextFileDownloadUrl",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextFileDownloadUrlResponse(),
            self.call_api(params, req, runtime),
        )

    async def get_context_file_download_url_with_options_async(
        self,
        request: main_models.GetContextFileDownloadUrlRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextFileDownloadUrlResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextFileDownloadUrl",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextFileDownloadUrlResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_context_file_download_url(
        self,
        request: main_models.GetContextFileDownloadUrlRequest,
    ) -> main_models.GetContextFileDownloadUrlResponse:
        runtime = RuntimeOptions()
        return self.get_context_file_download_url_with_options(request, runtime)

    async def get_context_file_download_url_async(
        self,
        request: main_models.GetContextFileDownloadUrlRequest,
    ) -> main_models.GetContextFileDownloadUrlResponse:
        runtime = RuntimeOptions()
        return await self.get_context_file_download_url_with_options_async(
            request, runtime
        )

    def get_context_file_upload_url_with_options(
        self,
        request: main_models.GetContextFileUploadUrlRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextFileUploadUrlResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextFileUploadUrl",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextFileUploadUrlResponse(),
            self.call_api(params, req, runtime),
        )

    async def get_context_file_upload_url_with_options_async(
        self,
        request: main_models.GetContextFileUploadUrlRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetContextFileUploadUrlResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.context_id):
            body["ContextId"] = request.context_id
        if not DaraCore.is_null(request.file_path):
            body["FilePath"] = request.file_path
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetContextFileUploadUrl",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetContextFileUploadUrlResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def get_context_file_upload_url(
        self,
        request: main_models.GetContextFileUploadUrlRequest,
    ) -> main_models.GetContextFileUploadUrlResponse:
        runtime = RuntimeOptions()
        return self.get_context_file_upload_url_with_options(request, runtime)

    async def get_context_file_upload_url_async(
        self,
        request: main_models.GetContextFileUploadUrlRequest,
    ) -> main_models.GetContextFileUploadUrlResponse:
        runtime = RuntimeOptions()
        return await self.get_context_file_upload_url_with_options_async(
            request, runtime
        )

    def get_cdp_link_with_options(
        self,
        request: main_models.GetCdpLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetCdpLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetCdpLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetCdpLinkResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def get_cdp_link_with_options_async(
        self,
        request: main_models.GetCdpLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetCdpLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetCdpLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetCdpLinkResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def get_cdp_link(
        self,
        request: main_models.GetCdpLinkRequest,
    ) -> main_models.GetCdpLinkResponse:
        runtime = RuntimeOptions()
        return self.get_cdp_link_with_options(request, runtime)

    async def get_cdp_link_async(
        self,
        request: main_models.GetCdpLinkRequest,
    ) -> main_models.GetCdpLinkResponse:
        runtime = RuntimeOptions()
        return await self.get_cdp_link_with_options_async(request, runtime)

    def get_adb_link_with_options(
        self,
        request: main_models.GetAdbLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetAdbLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.option):
            body["Option"] = request.option
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetAdbLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetAdbLinkResponse(),
            self.do_rpcrequest(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    async def get_adb_link_with_options_async(
        self,
        request: main_models.GetAdbLinkRequest,
        runtime: RuntimeOptions,
    ) -> main_models.GetAdbLinkResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.option):
            body["Option"] = request.option
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="GetAdbLink",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.GetAdbLinkResponse(),
            await self.do_rpcrequest_async(
                params.action,
                params.version,
                params.protocol,
                params.method,
                params.auth_type,
                params.body_type,
                req,
                runtime,
            ),
        )

    def get_adb_link(
        self,
        request: main_models.GetAdbLinkRequest,
    ) -> main_models.GetAdbLinkResponse:
        runtime = RuntimeOptions()
        return self.get_adb_link_with_options(request, runtime)

    async def get_adb_link_async(
        self,
        request: main_models.GetAdbLinkRequest,
    ) -> main_models.GetAdbLinkResponse:
        runtime = RuntimeOptions()
        return await self.get_adb_link_with_options_async(request, runtime)

    def bind_contexts_with_options(
        self,
        tmp_req: main_models.BindContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.BindContextsResponse:
        tmp_req.validate()
        request = main_models.BindContextsShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.persistence_data_list):
            request.persistence_data_list_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.persistence_data_list, "PersistenceDataList", "json"
                )
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.persistence_data_list_shrink):
            body["PersistenceDataList"] = request.persistence_data_list_shrink
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="BindContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.BindContextsResponse(), self.call_api(params, req, runtime)
        )

    async def bind_contexts_with_options_async(
        self,
        tmp_req: main_models.BindContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.BindContextsResponse:
        tmp_req.validate()
        request = main_models.BindContextsShrinkRequest()
        Utils.convert(tmp_req, request)
        if not DaraCore.is_null(tmp_req.persistence_data_list):
            request.persistence_data_list_shrink = (
                Utils.array_to_string_with_specified_style(
                    tmp_req.persistence_data_list, "PersistenceDataList", "json"
                )
            )
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.persistence_data_list_shrink):
            body["PersistenceDataList"] = request.persistence_data_list_shrink
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="BindContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.BindContextsResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def bind_contexts(
        self,
        request: main_models.BindContextsRequest,
    ) -> main_models.BindContextsResponse:
        runtime = RuntimeOptions()
        return self.bind_contexts_with_options(request, runtime)

    async def bind_contexts_async(
        self,
        request: main_models.BindContextsRequest,
    ) -> main_models.BindContextsResponse:
        runtime = RuntimeOptions()
        return await self.bind_contexts_with_options_async(request, runtime)

    def describe_session_contexts_with_options(
        self,
        request: main_models.DescribeSessionContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeSessionContextsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DescribeSessionContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeSessionContextsResponse(),
            self.call_api(params, req, runtime),
        )

    async def describe_session_contexts_with_options_async(
        self,
        request: main_models.DescribeSessionContextsRequest,
        runtime: RuntimeOptions,
    ) -> main_models.DescribeSessionContextsResponse:
        request.validate()
        body = {}
        if not DaraCore.is_null(request.authorization):
            body["Authorization"] = request.authorization
        if not DaraCore.is_null(request.session_id):
            body["SessionId"] = request.session_id
        req = open_api_util_models.OpenApiRequest(body=Utils.parse_to_map(body))
        params = open_api_util_models.Params(
            action="DescribeSessionContexts",
            version="2025-05-06",
            protocol="HTTPS",
            pathname="/",
            method="POST",
            auth_type="Anonymous",
            style="RPC",
            req_body_type="formData",
            body_type="json",
        )
        return DaraCore.from_map(
            main_models.DescribeSessionContextsResponse(),
            await self.call_api_async(params, req, runtime),
        )

    def describe_session_contexts(
        self,
        request: main_models.DescribeSessionContextsRequest,
    ) -> main_models.DescribeSessionContextsResponse:
        runtime = RuntimeOptions()
        return self.describe_session_contexts_with_options(request, runtime)

    async def describe_session_contexts_async(
        self,
        request: main_models.DescribeSessionContextsRequest,
    ) -> main_models.DescribeSessionContextsResponse:
        runtime = RuntimeOptions()
        return await self.describe_session_contexts_with_options_async(request, runtime)
