# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from __future__ import annotations

from typing import List

from darabonba.model import DaraModel

from agentbay.api import models as main_models


class GetSessionResponseBody(DaraModel):
    def __init__(
        self,
        code: str = None,
        data: main_models.GetSessionResponseBodyData = None,
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
            self.data.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.code is not None:
            result["Code"] = self.code

        if self.data is not None:
            result["Data"] = self.data.to_map()

        if self.http_status_code is not None:
            result["HttpStatusCode"] = self.http_status_code

        if self.message is not None:
            result["Message"] = self.message

        if self.request_id is not None:
            result["RequestId"] = self.request_id

        if self.success is not None:
            result["Success"] = self.success

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("Code") is not None:
            self.code = m.get("Code")

        if m.get("Data") is not None:
            temp_model = main_models.GetSessionResponseBodyData()
            self.data = temp_model.from_map(m.get("Data"))

        if m.get("HttpStatusCode") is not None:
            self.http_status_code = m.get("HttpStatusCode")

        if m.get("Message") is not None:
            self.message = m.get("Message")

        if m.get("RequestId") is not None:
            self.request_id = m.get("RequestId")

        if m.get("Success") is not None:
            self.success = m.get("Success")

        return self


class GetSessionResponseBodyData(DaraModel):
    def __init__(
        self,
        app_instance_id: str = None,
        http_port: str = None,
        link_url: str = None,
        network_interface_ip: str = None,
        resource_id: str = None,
        resource_url: str = None,
        session_id: str = None,
        status: str = None,
        token: str = None,
        tool_list: str = None,
        vpc_resource: bool = None,
        vpc_ip: str = None,
        vpc_id: str = None,
        contexts: List[main_models.GetSessionResponseBodyDataContexts] = None,
        ws_url: str = None,
    ):
        self.app_instance_id = app_instance_id
        self.http_port = http_port
        self.link_url = link_url
        self.network_interface_ip = network_interface_ip
        self.resource_id = resource_id
        self.resource_url = resource_url
        self.session_id = session_id
        self.status = status
        self.token = token
        self.tool_list = tool_list
        self.vpc_resource = vpc_resource
        self.vpc_ip = vpc_ip
        self.vpc_id = vpc_id
        self.contexts = contexts
        self.ws_url = ws_url

    def validate(self):
        if self.contexts:
            for v1 in self.contexts:
                if v1:
                    v1.validate()

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.app_instance_id is not None:
            result["AppInstanceId"] = self.app_instance_id

        if self.http_port is not None:
            result["HttpPort"] = self.http_port

        if self.link_url is not None:
            result["LinkUrl"] = self.link_url

        if self.network_interface_ip is not None:
            result["NetworkInterfaceIp"] = self.network_interface_ip

        if self.resource_id is not None:
            result["ResourceId"] = self.resource_id

        if self.resource_url is not None:
            result["ResourceUrl"] = self.resource_url

        if self.session_id is not None:
            result["SessionId"] = self.session_id

        if self.status is not None:
            result["Status"] = self.status

        if self.token is not None:
            result["Token"] = self.token

        if self.tool_list is not None:
            result["ToolList"] = self.tool_list

        if self.vpc_resource is not None:
            result["VpcResource"] = self.vpc_resource

        if self.vpc_ip is not None:
            result["VpcIp"] = self.vpc_ip

        if self.vpc_id is not None:
            result["VpcId"] = self.vpc_id

        if self.ws_url is not None:
            result["WsUrl"] = self.ws_url

        result["contexts"] = []
        if self.contexts is not None:
            for k1 in self.contexts:
                result["contexts"].append(k1.to_map() if k1 else None)

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("AppInstanceId") is not None:
            self.app_instance_id = m.get("AppInstanceId")

        if m.get("HttpPort") is not None:
            self.http_port = m.get("HttpPort")

        if m.get("LinkUrl") is not None:
            self.link_url = m.get("LinkUrl")

        if m.get("NetworkInterfaceIp") is not None:
            self.network_interface_ip = m.get("NetworkInterfaceIp")

        if m.get("ResourceId") is not None:
            self.resource_id = m.get("ResourceId")

        if m.get("ResourceUrl") is not None:
            self.resource_url = m.get("ResourceUrl")

        if m.get("SessionId") is not None:
            self.session_id = m.get("SessionId")

        if m.get("Status") is not None:
            self.status = m.get("Status")

        if m.get("Token") is not None:
            self.token = m.get("Token")

        if m.get("ToolList") is not None:
            self.tool_list = m.get("ToolList")

        if m.get("VpcResource") is not None:
            self.vpc_resource = m.get("VpcResource")

        if m.get("VpcIp") is not None:
            self.vpc_ip = m.get("VpcIp")

        if m.get("VpcId") is not None:
            self.vpc_id = m.get("VpcId")

        if m.get("WsUrl") is not None:
            self.ws_url = m.get("WsUrl")
        elif m.get("wsUrl") is not None:
            self.ws_url = m.get("wsUrl")

        self.contexts = []
        if m.get("contexts") is not None:
            for k1 in m.get("contexts"):
                temp_model = main_models.GetSessionResponseBodyDataContexts()
                self.contexts.append(temp_model.from_map(k1))

        return self


class GetSessionResponseBodyDataContexts(DaraModel):
    def __init__(
        self,
        id: str = None,
        name: str = None,
    ):
        self.id = id
        self.name = name

    def validate(self):
        pass

    def to_map(self):
        result = dict()
        _map = super().to_map()
        if _map is not None:
            result = _map
        if self.id is not None:
            result["id"] = self.id

        if self.name is not None:
            result["name"] = self.name

        return result

    def from_map(self, m: dict = None):
        m = m or dict()
        if m.get("id") is not None:
            self.id = m.get("id")

        if m.get("name") is not None:
            self.name = m.get("name")

        return self
