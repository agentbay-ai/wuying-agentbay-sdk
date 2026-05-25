// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"encoding/json"

	openapi "github.com/alibabacloud-go/darabonba-openapi/v2/client"
	openapiutil "github.com/alibabacloud-go/darabonba-openapi/v2/utils"
	"github.com/alibabacloud-go/tea/dara"
)

type Client struct {
	openapi.Client
	DisableSDKError *bool
}

func NewClient(config *openapiutil.Config) (*Client, error) {
	client := new(Client)
	err := client.Init(config)
	return client, err
}

func (client *Client) Init(config *openapiutil.Config) (_err error) {
	_err = client.Client.Init(config)
	if _err != nil {
		return _err
	}
	client.SignatureAlgorithm = dara.String("v2")
	client.EndpointRule = dara.String("")
	_err = client.CheckConfig(config)
	if _err != nil {
		return _err
	}
	client.Endpoint, _err = client.GetEndpoint(dara.String("wuyingai"), client.RegionId, client.EndpointRule, client.Network, client.Suffix, client.EndpointMap, client.Endpoint)
	if _err != nil {
		return _err
	}

	return nil
}

func (client *Client) GetEndpoint(productId *string, regionId *string, endpointRule *string, network *string, suffix *string, endpointMap map[string]*string, endpoint *string) (_result *string, _err error) {
	if !dara.IsNil(endpoint) {
		_result = endpoint
		return _result, _err
	}

	if !dara.IsNil(endpointMap) && !dara.IsNil(endpointMap[dara.StringValue(regionId)]) {
		_result = endpointMap[dara.StringValue(regionId)]
		return _result, _err
	}

	_body, _err := openapiutil.GetEndpointRules(productId, regionId, endpointRule, network, suffix)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Call MCP tool
//
// @param request - CallMcpToolRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return CallMcpToolResponse
func (client *Client) CallMcpToolWithOptions(request *CallMcpToolRequest, runtime *dara.RuntimeOptions) (_result *CallMcpToolResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Args) {
		body["Args"] = request.Args
	}

	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.AutoGenSession) {
		body["AutoGenSession"] = request.AutoGenSession
	}

	if !dara.IsNil(request.ExternalUserId) {
		body["ExternalUserId"] = request.ExternalUserId
	}

	if !dara.IsNil(request.ImageId) {
		body["ImageId"] = request.ImageId
	}

	if !dara.IsNil(request.Name) {
		body["Name"] = request.Name
	}

	if !dara.IsNil(request.Server) {
		body["Server"] = request.Server
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.Tool) {
		body["Tool"] = request.Tool
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("CallMcpTool"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &CallMcpToolResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Call MCP tool
//
// @param request - CallMcpToolRequest
//
// @return CallMcpToolResponse
func (client *Client) CallMcpTool(request *CallMcpToolRequest) (_result *CallMcpToolResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &CallMcpToolResponse{}
	_body, _err := client.CallMcpToolWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Delete Persistent Context
//
// @param request - ClearContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ClearContextResponse
func (client *Client) ClearContextWithOptions(request *ClearContextRequest, runtime *dara.RuntimeOptions) (_result *ClearContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Id) {
		body["Id"] = request.Id
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ClearContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ClearContextResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Delete Persistent Context
//
// @param request - ClearContextRequest
//
// @return ClearContextResponse
func (client *Client) ClearContext(request *ClearContextRequest) (_result *ClearContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ClearContextResponse{}
	_body, _err := client.ClearContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// 创建 mcp session
//
// @param tmpReq - CreateMcpSessionRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return CreateMcpSessionResponse
func (client *Client) CreateMcpSessionWithOptions(tmpReq *CreateMcpSessionRequest, runtime *dara.RuntimeOptions) (_result *CreateMcpSessionResponse, _err error) {
	_err = tmpReq.Validate()
	if _err != nil {
		return _result, _err
	}
	request := &CreateMcpSessionShrinkRequest{}
	openapiutil.Convert(tmpReq, request)
	if !dara.IsNil(tmpReq.PersistenceDataList) {
		request.PersistenceDataListShrink = openapiutil.ArrayToStringWithSpecifiedStyle(tmpReq.PersistenceDataList, dara.String("PersistenceDataList"), dara.String("json"))
	}
	if !dara.IsNil(tmpReq.Skills) {
		request.SkillsShrink = openapiutil.ArrayToStringWithSpecifiedStyle(tmpReq.Skills, dara.String("Skills"), dara.String("json"))
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.EnableRecord) {
		body["EnableRecord"] = request.EnableRecord
	}

	if !dara.IsNil(request.ExternalUserId) {
		body["ExternalUserId"] = request.ExternalUserId
	}

	if !dara.IsNil(request.ImageId) {
		body["ImageId"] = request.ImageId
	}

	if !dara.IsNil(request.Timeout) {
		body["Timeout"] = request.Timeout
	}

	if !dara.IsNil(request.MaxRuntime) {
		body["MaxRuntime"] = request.MaxRuntime
	}

	if !dara.IsNil(request.ManualRelease) {
		body["ManualRelease"] = request.ManualRelease
	}

	if !dara.IsNil(request.Labels) {
		body["Labels"] = request.Labels
	}

	if !dara.IsNil(request.McpPolicyId) {
		body["McpPolicyId"] = request.McpPolicyId
	}

	if !dara.IsNil(request.NetworkId) {
		body["NetworkId"] = request.NetworkId
	}

	if !dara.IsNil(request.PersistenceDataListShrink) {
		body["PersistenceDataList"] = request.PersistenceDataListShrink
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.VpcResource) {
		body["VpcResource"] = request.VpcResource
	}

	if !dara.IsNil(request.ExtraConfigs) {
		body["ExtraConfigs"] = request.ExtraConfigs
	}

	if !dara.IsNil(request.SdkStats) {
		body["SdkStats"] = request.SdkStats
	}

	if !dara.IsNil(request.LoginRegionId) {
		body["LoginRegionId"] = request.LoginRegionId
	}

	if !dara.IsNil(request.LoadSkill) {
		body["LoadSkill"] = request.LoadSkill
	}

	if !dara.IsNil(request.SkillsShrink) {
		body["Skills"] = request.SkillsShrink
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("CreateMcpSession"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &CreateMcpSessionResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Create MCP session
//
// @param request - CreateMcpSessionRequest
//
// @return CreateMcpSessionResponse
func (client *Client) CreateMcpSession(request *CreateMcpSessionRequest) (_result *CreateMcpSessionResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &CreateMcpSessionResponse{}
	_body, _err := client.CreateMcpSessionWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Create network
//
// @param request - CreateNetworkRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return CreateNetworkResponse
func (client *Client) CreateNetworkWithOptions(request *CreateNetworkRequest, runtime *dara.RuntimeOptions) (_result *CreateNetworkResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.LoginRegionId) {
		body["LoginRegionId"] = request.LoginRegionId
	}
	if !dara.IsNil(request.NetworkId) {
		body["NetworkId"] = request.NetworkId
	}
	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("CreateNetwork"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &CreateNetworkResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Create network
//
// @param request - CreateNetworkRequest
//
// @return CreateNetworkResponse
func (client *Client) CreateNetwork(request *CreateNetworkRequest) (_result *CreateNetworkResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &CreateNetworkResponse{}
	_body, _err := client.CreateNetworkWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Describe network
//
// @param request - DescribeNetworkRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return DescribeNetworkResponse
func (client *Client) DescribeNetworkWithOptions(request *DescribeNetworkRequest, runtime *dara.RuntimeOptions) (_result *DescribeNetworkResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.NetworkId) {
		body["NetworkId"] = request.NetworkId
	}
	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DescribeNetwork"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DescribeNetworkResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Describe network
//
// @param request - DescribeNetworkRequest
//
// @return DescribeNetworkResponse
func (client *Client) DescribeNetwork(request *DescribeNetworkRequest) (_result *DescribeNetworkResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DescribeNetworkResponse{}
	_body, _err := client.DescribeNetworkWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Delete persistent context
//
// @param request - DeleteContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return DeleteContextResponse
func (client *Client) DeleteContextWithOptions(request *DeleteContextRequest, runtime *dara.RuntimeOptions) (_result *DeleteContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Id) {
		body["Id"] = request.Id
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DeleteContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DeleteContextResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Delete persistent context
//
// @param request - DeleteContextRequest
//
// @return DeleteContextResponse
func (client *Client) DeleteContext(request *DeleteContextRequest) (_result *DeleteContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DeleteContextResponse{}
	_body, _err := client.DeleteContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - DeleteContextFileRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return DeleteContextFileResponse
func (client *Client) DeleteContextFileWithOptions(request *DeleteContextFileRequest, runtime *dara.RuntimeOptions) (_result *DeleteContextFileResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.FilePath) {
		body["FilePath"] = request.FilePath
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DeleteContextFile"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DeleteContextFileResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - DeleteContextFileRequest
//
// @return DeleteContextFileResponse
func (client *Client) DeleteContextFile(request *DeleteContextFileRequest) (_result *DeleteContextFileResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DeleteContextFileResponse{}
	_body, _err := client.DeleteContextFileWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Delete session async
//
// @param request - DeleteSessionAsyncRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return DeleteSessionAsyncResponse
func (client *Client) DeleteSessionAsyncWithOptions(request *DeleteSessionAsyncRequest, runtime *dara.RuntimeOptions) (_result *DeleteSessionAsyncResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DeleteSessionAsync"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DeleteSessionAsyncResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Delete session async
//
// @param request - DeleteSessionAsyncRequest
//
// @return DeleteSessionAsyncResponse
func (client *Client) DeleteSessionAsync(request *DeleteSessionAsyncRequest) (_result *DeleteSessionAsyncResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DeleteSessionAsyncResponse{}
	_body, _err := client.DeleteSessionAsyncWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Query context specific directory files
//
// @param request - DescribeContextFilesRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return DescribeContextFilesResponse
func (client *Client) DescribeContextFilesWithOptions(request *DescribeContextFilesRequest, runtime *dara.RuntimeOptions) (_result *DescribeContextFilesResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	query := map[string]interface{}{}
	if !dara.IsNil(request.MaxResults) {
		query["MaxResults"] = request.MaxResults
	}

	if !dara.IsNil(request.NextToken) {
		query["NextToken"] = request.NextToken
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.PageNumber) {
		body["PageNumber"] = request.PageNumber
	}

	if !dara.IsNil(request.PageSize) {
		body["PageSize"] = request.PageSize
	}

	if !dara.IsNil(request.ParentFolderPath) {
		body["ParentFolderPath"] = request.ParentFolderPath
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	req := &openapiutil.OpenApiRequest{
		Query: openapiutil.Query(query),
		Body:  openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DescribeContextFiles"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DescribeContextFilesResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Query context specific directory files
//
// @param request - DescribeContextFilesRequest
//
// @return DescribeContextFilesResponse
func (client *Client) DescribeContextFiles(request *DescribeContextFilesRequest) (_result *DescribeContextFilesResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DescribeContextFilesResponse{}
	_body, _err := client.DescribeContextFilesWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context
//
// @param request - GetContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetContextResponse
func (client *Client) GetContextWithOptions(request *GetContextRequest, runtime *dara.RuntimeOptions) (_result *GetContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.AllowCreate) {
		body["AllowCreate"] = request.AllowCreate
	}

	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.Name) {
		body["Name"] = request.Name
	}

	if !dara.IsNil(request.LoginRegionId) {
		body["LoginRegionId"] = request.LoginRegionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetContextResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context
//
// @param request - GetContextRequest
//
// @return GetContextResponse
func (client *Client) GetContext(request *GetContextRequest) (_result *GetContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetContextResponse{}
	_body, _err := client.GetContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context information
//
// @param request - GetContextInfoRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetContextInfoResponse
func (client *Client) GetContextInfoWithOptions(request *GetContextInfoRequest, runtime *dara.RuntimeOptions) (_result *GetContextInfoResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.Path) {
		body["Path"] = request.Path
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.TaskType) {
		body["TaskType"] = request.TaskType
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetContextInfo"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetContextInfoResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context information
//
// @param request - GetContextInfoRequest
//
// @return GetContextInfoResponse
func (client *Client) GetContextInfo(request *GetContextInfoRequest) (_result *GetContextInfoResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetContextInfoResponse{}
	_body, _err := client.GetContextInfoWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get labels
//
// @param request - GetLabelRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetLabelResponse
func (client *Client) GetLabelWithOptions(request *GetLabelRequest, runtime *dara.RuntimeOptions) (_result *GetLabelResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.MaxResults) {
		body["MaxResults"] = request.MaxResults
	}

	if !dara.IsNil(request.NextToken) {
		body["NextToken"] = request.NextToken
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetLabel"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetLabelResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get labels
//
// @param request - GetLabelRequest
//
// @return GetLabelResponse
func (client *Client) GetLabel(request *GetLabelRequest) (_result *GetLabelResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetLabelResponse{}
	_body, _err := client.GetLabelWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get session information
//
// @param request - GetSessionRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetSessionResponse
func (client *Client) GetSessionWithOptions(request *GetSessionRequest, runtime *dara.RuntimeOptions) (_result *GetSessionResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetSession"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetSessionResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get session information
//
// @param request - GetSessionRequest
//
// @return GetSessionResponse
func (client *Client) GetSession(request *GetSessionRequest) (_result *GetSessionResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetSessionResponse{}
	_body, _err := client.GetSessionWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get basic session information by session ID
//
// @param request - GetSessionDetailRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetSessionDetailResponse
func (client *Client) GetSessionDetailWithOptions(request *GetSessionDetailRequest, runtime *dara.RuntimeOptions) (_result *GetSessionDetailResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	query := map[string]interface{}{}
	if !dara.IsNil(request.SessionId) {
		query["SessionId"] = request.SessionId
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	req := &openapiutil.OpenApiRequest{
		Query: openapiutil.Query(query),
		Body:  openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetSessionDetail"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetSessionDetailResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get basic session information by session ID
//
// @param request - GetSessionDetailRequest
//
// @return GetSessionDetailResponse
func (client *Client) GetSessionDetail(request *GetSessionDetailRequest) (_result *GetSessionDetailResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetSessionDetailResponse{}
	_body, _err := client.GetSessionDetailWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get forwarding link for specific port
//
// @param request - GetLinkRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetLinkResponse
func (client *Client) GetLinkWithOptions(request *GetLinkRequest, runtime *dara.RuntimeOptions) (_result *GetLinkResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Port) {
		body["Port"] = request.Port
	}

	if !dara.IsNil(request.ProtocolType) {
		body["ProtocolType"] = request.ProtocolType
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.Option) {
		body["Option"] = request.Option
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetLink"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetLinkResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get forwarding link for specific port
//
// @param request - GetLinkRequest
//
// @return GetLinkResponse
func (client *Client) GetLink(request *GetLinkRequest) (_result *GetLinkResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetLinkResponse{}
	_body, _err := client.GetLinkWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get MCP resource information
//
// @param request - GetMcpResourceRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetMcpResourceResponse
func (client *Client) GetMcpResourceWithOptions(request *GetMcpResourceRequest, runtime *dara.RuntimeOptions) (_result *GetMcpResourceResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetMcpResource"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetMcpResourceResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get MCP resource information
//
// @param request - GetMcpResourceRequest
//
// @return GetMcpResourceResponse
func (client *Client) GetMcpResource(request *GetMcpResourceRequest) (_result *GetMcpResourceResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetMcpResourceResponse{}
	_body, _err := client.GetMcpResourceWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - GetContextFileDownloadUrlRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetContextFileDownloadUrlResponse
func (client *Client) GetContextFileDownloadUrlWithOptions(request *GetContextFileDownloadUrlRequest, runtime *dara.RuntimeOptions) (_result *GetContextFileDownloadUrlResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.FilePath) {
		body["FilePath"] = request.FilePath
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetContextFileDownloadUrl"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetContextFileDownloadUrlResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - GetContextFileDownloadUrlRequest
//
// @return GetContextFileDownloadUrlResponse
func (client *Client) GetContextFileDownloadUrl(request *GetContextFileDownloadUrlRequest) (_result *GetContextFileDownloadUrlResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetContextFileDownloadUrlResponse{}
	_body, _err := client.GetContextFileDownloadUrlWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - GetContextFileUploadUrlRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetContextFileUploadUrlResponse
func (client *Client) GetContextFileUploadUrlWithOptions(request *GetContextFileUploadUrlRequest, runtime *dara.RuntimeOptions) (_result *GetContextFileUploadUrlResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.FilePath) {
		body["FilePath"] = request.FilePath
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetContextFileUploadUrl"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetContextFileUploadUrlResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context file upload URL
//
// @param request - GetContextFileUploadUrlRequest
//
// @return GetContextFileUploadUrlResponse
func (client *Client) GetContextFileUploadUrl(request *GetContextFileUploadUrlRequest) (_result *GetContextFileUploadUrlResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetContextFileUploadUrlResponse{}
	_body, _err := client.GetContextFileUploadUrlWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get context list
//
// @param request - ListContextsRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ListContextsResponse
func (client *Client) ListContextsWithOptions(request *ListContextsRequest, runtime *dara.RuntimeOptions) (_result *ListContextsResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.MaxResults) {
		body["MaxResults"] = request.MaxResults
	}

	if !dara.IsNil(request.NextToken) {
		body["NextToken"] = request.NextToken
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.Type) {
		body["ContextType"] = request.Type
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ListContexts"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ListContextsResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get context list
//
// @param request - ListContextsRequest
//
// @return ListContextsResponse
func (client *Client) ListContexts(request *ListContextsRequest) (_result *ListContextsResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ListContextsResponse{}
	_body, _err := client.ListContextsWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # ListMcpTools
//
// @param request - ListMcpToolsRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ListMcpToolsResponse
func (client *Client) ListMcpToolsWithOptions(request *ListMcpToolsRequest, runtime *dara.RuntimeOptions) (_result *ListMcpToolsResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ImageId) {
		body["ImageId"] = request.ImageId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ListMcpTools"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ListMcpToolsResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # ListMcpTools
//
// @param request - ListMcpToolsRequest
//
// @return ListMcpToolsResponse
func (client *Client) ListMcpTools(request *ListMcpToolsRequest) (_result *ListMcpToolsResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ListMcpToolsResponse{}
	_body, _err := client.ListMcpToolsWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Query session list by label
//
// @param request - ListSessionRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ListSessionResponse
func (client *Client) ListSessionWithOptions(request *ListSessionRequest, runtime *dara.RuntimeOptions) (_result *ListSessionResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Labels) {
		body["Labels"] = request.Labels
	}

	if !dara.IsNil(request.MaxResults) {
		body["MaxResults"] = request.MaxResults
	}

	if !dara.IsNil(request.NextToken) {
		body["NextToken"] = request.NextToken
	}

	if !dara.IsNil(request.Status) {
		body["Status"] = request.Status
	}

	if !dara.IsNil(request.ImageId) {
		body["ImageId"] = request.ImageId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ListSession"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ListSessionResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Query session list by label
//
// @param request - ListSessionRequest
//
// @return ListSessionResponse
func (client *Client) ListSession(request *ListSessionRequest) (_result *ListSessionResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ListSessionResponse{}
	_body, _err := client.ListSessionWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # List official skills metadata
//
// @param request - ListSkillMetaDataRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ListSkillMetaDataResponse
func (client *Client) ListSkillMetaDataWithOptions(request *ListSkillMetaDataRequest, runtime *dara.RuntimeOptions) (_result *ListSkillMetaDataResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ListSkillMetaData"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ListSkillMetaDataResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # List official skills metadata
//
// @param request - ListSkillMetaDataRequest
//
// @return ListSkillMetaDataResponse
func (client *Client) ListSkillMetaData(request *ListSkillMetaDataRequest) (_result *ListSkillMetaDataResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ListSkillMetaDataResponse{}
	_body, _err := client.ListSkillMetaDataWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # GetSkillMetaData
//
// @param tmpReq - GetSkillMetaDataRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetSkillMetaDataResponse
func (client *Client) GetSkillMetaDataWithOptions(tmpReq *GetSkillMetaDataRequest, runtime *dara.RuntimeOptions) (_result *GetSkillMetaDataResponse, _err error) {
	_err = tmpReq.Validate()
	if _err != nil {
		return _result, _err
	}
	request := &GetSkillMetaDataShrinkRequest{}
	openapiutil.Convert(tmpReq, request)
	if !dara.IsNil(tmpReq.SkillGroupIds) {
		request.SkillGroupIdsShrink = openapiutil.ArrayToStringWithSpecifiedStyle(tmpReq.SkillGroupIds, dara.String("SkillGroupIds"), dara.String("json"))
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.ImageId) {
		body["ImageId"] = request.ImageId
	}
	if !dara.IsNil(request.SkillGroupIdsShrink) {
		body["SkillGroupIds"] = request.SkillGroupIdsShrink
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetSkillMetaData"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetSkillMetaDataResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # GetSkillMetaData
//
// @param request - GetSkillMetaDataRequest
//
// @return GetSkillMetaDataResponse
func (client *Client) GetSkillMetaData(request *GetSkillMetaDataRequest) (_result *GetSkillMetaDataResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetSkillMetaDataResponse{}
	_body, _err := client.GetSkillMetaDataWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Modify context
//
// @param request - ModifyContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ModifyContextResponse
func (client *Client) ModifyContextWithOptions(request *ModifyContextRequest, runtime *dara.RuntimeOptions) (_result *ModifyContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Id) {
		body["Id"] = request.Id
	}

	if !dara.IsNil(request.Name) {
		body["Name"] = request.Name
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ModifyContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ModifyContextResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Modify context
//
// @param request - ModifyContextRequest
//
// @return ModifyContextResponse
func (client *Client) ModifyContext(request *ModifyContextRequest) (_result *ModifyContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ModifyContextResponse{}
	_body, _err := client.ModifyContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Refresh session idle timer
//
// @param request - RefreshSessionIdleTimeRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return RefreshSessionIdleTimeResponse
func (client *Client) RefreshSessionIdleTimeWithOptions(request *RefreshSessionIdleTimeRequest, runtime *dara.RuntimeOptions) (_result *RefreshSessionIdleTimeResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}
	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("RefreshSessionIdleTime"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &RefreshSessionIdleTimeResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Refresh session idle timer
//
// @param request - RefreshSessionIdleTimeRequest
//
// @return RefreshSessionIdleTimeResponse
func (client *Client) RefreshSessionIdleTime(request *RefreshSessionIdleTimeRequest) (_result *RefreshSessionIdleTimeResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &RefreshSessionIdleTimeResponse{}
	_body, _err := client.RefreshSessionIdleTimeWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Release MCP session
//
// @param request - ReleaseMcpSessionRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ReleaseMcpSessionResponse
func (client *Client) ReleaseMcpSessionWithOptions(request *ReleaseMcpSessionRequest, runtime *dara.RuntimeOptions) (_result *ReleaseMcpSessionResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ReleaseMcpSession"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ReleaseMcpSessionResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Release MCP session
//
// @param request - ReleaseMcpSessionRequest
//
// @return ReleaseMcpSessionResponse
func (client *Client) ReleaseMcpSession(request *ReleaseMcpSessionRequest) (_result *ReleaseMcpSessionResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ReleaseMcpSessionResponse{}
	_body, _err := client.ReleaseMcpSessionWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Set labels
//
// @param request - SetLabelRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return SetLabelResponse
func (client *Client) SetLabelWithOptions(request *SetLabelRequest, runtime *dara.RuntimeOptions) (_result *SetLabelResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Labels) {
		body["Labels"] = request.Labels
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("SetLabel"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &SetLabelResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Set labels
//
// @param request - SetLabelRequest
//
// @return SetLabelResponse
func (client *Client) SetLabel(request *SetLabelRequest) (_result *SetLabelResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &SetLabelResponse{}
	_body, _err := client.SetLabelWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Sync context
//
// @param request - SyncContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return SyncContextResponse
func (client *Client) SyncContextWithOptions(request *SyncContextRequest, runtime *dara.RuntimeOptions) (_result *SyncContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	query := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		query["Authorization"] = request.Authorization
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.ContextId) {
		body["ContextId"] = request.ContextId
	}

	if !dara.IsNil(request.Mode) {
		body["Mode"] = request.Mode
	}

	if !dara.IsNil(request.Path) {
		body["Path"] = request.Path
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Query: openapiutil.Query(query),
		Body:  openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("SyncContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &SyncContextResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Sync context
//
// @param request - SyncContextRequest
//
// @return SyncContextResponse
func (client *Client) SyncContext(request *SyncContextRequest) (_result *SyncContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &SyncContextResponse{}
	_body, _err := client.SyncContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Initialize Browser
//
// @param request - InitBrowserRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return InitBrowserResponse
func (client *Client) InitBrowserWithOptions(request *InitBrowserRequest, runtime *dara.RuntimeOptions) (_result *InitBrowserResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	if !dara.IsNil(request.PersistentPath) {
		body["PersistentPath"] = request.PersistentPath
	}

	if !dara.IsNil(request.BrowserOption) {
		browserOptionJSON, err := json.Marshal(request.BrowserOption)
		if err != nil {
			return _result, err
		}
		body["BrowserOption"] = string(browserOptionJSON)
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("InitBrowser"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &InitBrowserResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Initialize Browser
//
// @param request - InitBrowserRequest
//
// @return InitBrowserResponse
func (client *Client) InitBrowser(request *InitBrowserRequest) (_result *InitBrowserResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &InitBrowserResponse{}
	_body, _err := client.InitBrowserWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Pause Session Async
//
// @param request - PauseSessionAsyncRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return PauseSessionAsyncResponse
func (client *Client) PauseSessionAsyncWithOptions(request *PauseSessionAsyncRequest, runtime *dara.RuntimeOptions) (_result *PauseSessionAsyncResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	query := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		query["Authorization"] = request.Authorization
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Query: openapiutil.Query(query),
		Body:  openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("PauseSessionAsync"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &PauseSessionAsyncResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Pause Session Async
//
// @param request - PauseSessionAsyncRequest
//
// @return PauseSessionAsyncResponse
func (client *Client) PauseSessionAsync(request *PauseSessionAsyncRequest) (_result *PauseSessionAsyncResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &PauseSessionAsyncResponse{}
	_body, _err := client.PauseSessionAsyncWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Resume Session Async
//
// @param request - ResumeSessionAsyncRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return ResumeSessionAsyncResponse
func (client *Client) ResumeSessionAsyncWithOptions(request *ResumeSessionAsyncRequest, runtime *dara.RuntimeOptions) (_result *ResumeSessionAsyncResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	query := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		query["Authorization"] = request.Authorization
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Query: openapiutil.Query(query),
		Body:  openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("ResumeSessionAsync"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &ResumeSessionAsyncResponse{}
	_body, _err := client.CallApi(params, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Resume Session Async
//
// @param request - ResumeSessionAsyncRequest
//
// @return ResumeSessionAsyncResponse
func (client *Client) ResumeSessionAsync(request *ResumeSessionAsyncRequest) (_result *ResumeSessionAsyncResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &ResumeSessionAsyncResponse{}
	_body, _err := client.ResumeSessionAsyncWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get ADB Link
//
// @param request - GetAdbLinkRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetAdbLinkResponse
func (client *Client) GetAdbLinkWithOptions(request *GetAdbLinkRequest, runtime *dara.RuntimeOptions) (_result *GetAdbLinkResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.Option) {
		body["Option"] = request.Option
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetAdbLink"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetAdbLinkResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get ADB Link
//
// @param request - GetAdbLinkRequest
//
// @return GetAdbLinkResponse
func (client *Client) GetAdbLink(request *GetAdbLinkRequest) (_result *GetAdbLinkResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetAdbLinkResponse{}
	_body, _err := client.GetAdbLinkWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get CDP Link
//
// @param request - GetCdpLinkRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetCdpLinkResponse
func (client *Client) GetCdpLinkWithOptions(request *GetCdpLinkRequest, runtime *dara.RuntimeOptions) (_result *GetCdpLinkResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetCdpLink"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetCdpLinkResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get CDP Link
//
// @param request - GetCdpLinkRequest
//
// @return GetCdpLinkResponse
func (client *Client) GetCdpLink(request *GetCdpLinkRequest) (_result *GetCdpLinkResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetCdpLinkResponse{}
	_body, _err := client.GetCdpLinkWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

// Summary:
//
// # Get Internal Context
//
// @param request - GetAndLoadInternalContextRequest
//
// @param runtime - runtime options for this request RuntimeOptions
//
// @return GetAndLoadInternalContextResponse
func (client *Client) GetAndLoadInternalContextWithOptions(request *GetAndLoadInternalContextRequest, runtime *dara.RuntimeOptions) (_result *GetAndLoadInternalContextResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}

	if !dara.IsNil(request.ContextTypes) {
		body["ContextTypes"] = request.ContextTypes
	}

	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("GetAndLoadInternalContext"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &GetAndLoadInternalContextResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

// Summary:
//
// # Get Internal Context
//
// @param request - GetAndLoadInternalContextRequest
//
// @return GetAndLoadInternalContextResponse
func (client *Client) GetAndLoadInternalContext(request *GetAndLoadInternalContextRequest) (_result *GetAndLoadInternalContextResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &GetAndLoadInternalContextResponse{}
	_body, _err := client.GetAndLoadInternalContextWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

func (client *Client) BindContextsWithOptions(tmpReq *BindContextsRequest, runtime *dara.RuntimeOptions) (_result *BindContextsResponse, _err error) {
	_err = tmpReq.Validate()
	if _err != nil {
		return _result, _err
	}
	request := &BindContextsShrinkRequest{}
	openapiutil.Convert(tmpReq, request)
	if !dara.IsNil(tmpReq.PersistenceDataList) {
		request.PersistenceDataListShrink = openapiutil.ArrayToStringWithSpecifiedStyle(tmpReq.PersistenceDataList, dara.String("PersistenceDataList"), dara.String("json"))
	}

	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.PersistenceDataListShrink) {
		body["PersistenceDataList"] = request.PersistenceDataListShrink
	}
	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("BindContexts"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &BindContextsResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

func (client *Client) BindContexts(request *BindContextsRequest) (_result *BindContextsResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &BindContextsResponse{}
	_body, _err := client.BindContextsWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}

func (client *Client) DescribeSessionContextsWithOptions(request *DescribeSessionContextsRequest, runtime *dara.RuntimeOptions) (_result *DescribeSessionContextsResponse, _err error) {
	_err = request.Validate()
	if _err != nil {
		return _result, _err
	}
	body := map[string]interface{}{}
	if !dara.IsNil(request.Authorization) {
		body["Authorization"] = request.Authorization
	}
	if !dara.IsNil(request.SessionId) {
		body["SessionId"] = request.SessionId
	}

	req := &openapiutil.OpenApiRequest{
		Body: openapiutil.ParseToMap(body),
	}
	params := &openapiutil.Params{
		Action:      dara.String("DescribeSessionContexts"),
		Version:     dara.String("2025-05-06"),
		Protocol:    dara.String("HTTPS"),
		Pathname:    dara.String("/"),
		Method:      dara.String("POST"),
		AuthType:    dara.String("Anonymous"),
		Style:       dara.String("RPC"),
		ReqBodyType: dara.String("formData"),
		BodyType:    dara.String("json"),
	}
	_result = &DescribeSessionContextsResponse{}
	_body, _err := client.DoRPCRequest(params.Action, params.Version, params.Protocol, params.Method, params.AuthType, params.BodyType, req, runtime)
	if _err != nil {
		return _result, _err
	}
	_err = dara.Convert(_body, &_result)
	return _result, _err
}

func (client *Client) DescribeSessionContexts(request *DescribeSessionContextsRequest) (_result *DescribeSessionContextsResponse, _err error) {
	runtime := &dara.RuntimeOptions{}
	_result = &DescribeSessionContextsResponse{}
	_body, _err := client.DescribeSessionContextsWithOptions(request, runtime)
	if _err != nil {
		return _result, _err
	}
	_result = _body
	return _result, _err
}
