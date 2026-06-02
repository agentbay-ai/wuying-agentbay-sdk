// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iGetSessionResponseBody interface {
	dara.Model
	String() string
	GoString() string
	SetCode(v string) *GetSessionResponseBody
	GetCode() *string
	SetData(v *GetSessionResponseBodyData) *GetSessionResponseBody
	GetData() *GetSessionResponseBodyData
	SetHttpStatusCode(v int32) *GetSessionResponseBody
	GetHttpStatusCode() *int32
	SetMessage(v string) *GetSessionResponseBody
	GetMessage() *string
	SetRequestId(v string) *GetSessionResponseBody
	GetRequestId() *string
	SetSuccess(v bool) *GetSessionResponseBody
	GetSuccess() *bool
}

type GetSessionResponseBody struct {
	Code           *string                     `json:"Code,omitempty" xml:"Code,omitempty"`
	Data           *GetSessionResponseBodyData `json:"Data,omitempty" xml:"Data,omitempty" type:"Struct"`
	HttpStatusCode *int32                      `json:"HttpStatusCode,omitempty" xml:"HttpStatusCode,omitempty"`
	Message        *string                     `json:"Message,omitempty" xml:"Message,omitempty"`
	RequestId      *string                     `json:"RequestId,omitempty" xml:"RequestId,omitempty"`
	Success        *bool                       `json:"Success,omitempty" xml:"Success,omitempty"`
}

func (s GetSessionResponseBody) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBody) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBody) GetCode() *string {
	return s.Code
}

func (s *GetSessionResponseBody) GetData() *GetSessionResponseBodyData {
	return s.Data
}

func (s *GetSessionResponseBody) GetHttpStatusCode() *int32 {
	return s.HttpStatusCode
}

func (s *GetSessionResponseBody) GetMessage() *string {
	return s.Message
}

func (s *GetSessionResponseBody) GetRequestId() *string {
	return s.RequestId
}

func (s *GetSessionResponseBody) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionResponseBody) SetCode(v string) *GetSessionResponseBody {
	s.Code = &v
	return s
}

func (s *GetSessionResponseBody) SetData(v *GetSessionResponseBodyData) *GetSessionResponseBody {
	s.Data = v
	return s
}

func (s *GetSessionResponseBody) SetHttpStatusCode(v int32) *GetSessionResponseBody {
	s.HttpStatusCode = &v
	return s
}

func (s *GetSessionResponseBody) SetMessage(v string) *GetSessionResponseBody {
	s.Message = &v
	return s
}

func (s *GetSessionResponseBody) SetRequestId(v string) *GetSessionResponseBody {
	s.RequestId = &v
	return s
}

func (s *GetSessionResponseBody) SetSuccess(v bool) *GetSessionResponseBody {
	s.Success = &v
	return s
}

func (s *GetSessionResponseBody) Validate() error {
	if s.Data != nil {
		if err := s.Data.Validate(); err != nil {
			return err
		}
	}
	return nil
}

type GetSessionResponseBodyData struct {
	AppInstanceId      *string                               `json:"AppInstanceId,omitempty" xml:"AppInstanceId,omitempty"`
	HttpPort           *string                               `json:"HttpPort,omitempty" xml:"HttpPort,omitempty"`
	LinkUrl            *string                               `json:"LinkUrl,omitempty" xml:"LinkUrl,omitempty"`
	NetworkInterfaceIp *string                               `json:"NetworkInterfaceIp,omitempty" xml:"NetworkInterfaceIp,omitempty"`
	ResourceId         *string                               `json:"ResourceId,omitempty" xml:"ResourceId,omitempty"`
	ResourceUrl        *string                               `json:"ResourceUrl,omitempty" xml:"ResourceUrl,omitempty"`
	SessionId          *string                               `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	Status             *string                               `json:"Status,omitempty" xml:"Status,omitempty"`
	Success            *bool                                 `json:"Success,omitempty" xml:"Success,omitempty"`
	Token              *string                               `json:"Token,omitempty" xml:"Token,omitempty"`
	ToolList           interface{}                            `json:"ToolList,omitempty" xml:"ToolList,omitempty"`
	WsUrl              *string                               `json:"WsUrl,omitempty" xml:"WsUrl,omitempty"`
	VpcResource        *bool                                 `json:"VpcResource,omitempty" xml:"VpcResource,omitempty"`
	VpcIp              *string                               `json:"VpcIp,omitempty" xml:"VpcIp,omitempty"`
	VpcId              *string                               `json:"VpcId,omitempty" xml:"VpcId,omitempty"`
	Contexts           []*GetSessionResponseBodyDataContexts `json:"contexts,omitempty" xml:"contexts,omitempty" type:"Repeated"`
}

func (s GetSessionResponseBodyData) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBodyData) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBodyData) GetAppInstanceId() *string {
	return s.AppInstanceId
}

func (s *GetSessionResponseBodyData) GetHttpPort() *string {
	return s.HttpPort
}

func (s *GetSessionResponseBodyData) GetLinkUrl() *string {
	return s.LinkUrl
}

func (s *GetSessionResponseBodyData) GetNetworkInterfaceIp() *string {
	return s.NetworkInterfaceIp
}

func (s *GetSessionResponseBodyData) GetResourceId() *string {
	return s.ResourceId
}

func (s *GetSessionResponseBodyData) GetResourceUrl() *string {
	return s.ResourceUrl
}

func (s *GetSessionResponseBodyData) GetSessionId() *string {
	return s.SessionId
}

func (s *GetSessionResponseBodyData) GetStatus() *string {
	return s.Status
}

func (s *GetSessionResponseBodyData) GetSuccess() *bool {
	return s.Success
}

func (s *GetSessionResponseBodyData) GetToken() *string {
	return s.Token
}

func (s *GetSessionResponseBodyData) GetToolList() interface{} {
	return s.ToolList
}

func (s *GetSessionResponseBodyData) GetWsUrl() *string {
	return s.WsUrl
}

func (s *GetSessionResponseBodyData) GetVpcResource() *bool {
	return s.VpcResource
}

func (s *GetSessionResponseBodyData) GetVpcIp() *string {
	return s.VpcIp
}

func (s *GetSessionResponseBodyData) GetVpcId() *string {
	return s.VpcId
}

func (s *GetSessionResponseBodyData) GetContexts() []*GetSessionResponseBodyDataContexts {
	return s.Contexts
}

func (s *GetSessionResponseBodyData) SetAppInstanceId(v string) *GetSessionResponseBodyData {
	s.AppInstanceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetHttpPort(v string) *GetSessionResponseBodyData {
	s.HttpPort = &v
	return s
}

func (s *GetSessionResponseBodyData) SetLinkUrl(v string) *GetSessionResponseBodyData {
	s.LinkUrl = &v
	return s
}

func (s *GetSessionResponseBodyData) SetNetworkInterfaceIp(v string) *GetSessionResponseBodyData {
	s.NetworkInterfaceIp = &v
	return s
}

func (s *GetSessionResponseBodyData) SetResourceId(v string) *GetSessionResponseBodyData {
	s.ResourceId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetResourceUrl(v string) *GetSessionResponseBodyData {
	s.ResourceUrl = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSessionId(v string) *GetSessionResponseBodyData {
	s.SessionId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetStatus(v string) *GetSessionResponseBodyData {
	s.Status = &v
	return s
}

func (s *GetSessionResponseBodyData) SetSuccess(v bool) *GetSessionResponseBodyData {
	s.Success = &v
	return s
}

func (s *GetSessionResponseBodyData) SetToken(v string) *GetSessionResponseBodyData {
	s.Token = &v
	return s
}

func (s *GetSessionResponseBodyData) SetToolList(v interface{}) *GetSessionResponseBodyData {
	s.ToolList = v
	return s
}

func (s *GetSessionResponseBodyData) SetWsUrl(v string) *GetSessionResponseBodyData {
	s.WsUrl = &v
	return s
}

func (s *GetSessionResponseBodyData) SetVpcResource(v bool) *GetSessionResponseBodyData {
	s.VpcResource = &v
	return s
}

func (s *GetSessionResponseBodyData) SetVpcIp(v string) *GetSessionResponseBodyData {
	s.VpcIp = &v
	return s
}

func (s *GetSessionResponseBodyData) SetVpcId(v string) *GetSessionResponseBodyData {
	s.VpcId = &v
	return s
}

func (s *GetSessionResponseBodyData) SetContexts(v []*GetSessionResponseBodyDataContexts) *GetSessionResponseBodyData {
	s.Contexts = v
	return s
}

func (s *GetSessionResponseBodyData) Validate() error {
	if s.Contexts != nil {
		for _, item := range s.Contexts {
			if item != nil {
				if err := item.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type GetSessionResponseBodyDataContexts struct {
	Id   *string `json:"id,omitempty" xml:"id,omitempty"`
	Name *string `json:"name,omitempty" xml:"name,omitempty"`
}

func (s GetSessionResponseBodyDataContexts) String() string {
	return dara.Prettify(s)
}

func (s GetSessionResponseBodyDataContexts) GoString() string {
	return s.String()
}

func (s *GetSessionResponseBodyDataContexts) GetId() *string {
	return s.Id
}

func (s *GetSessionResponseBodyDataContexts) GetName() *string {
	return s.Name
}

func (s *GetSessionResponseBodyDataContexts) SetId(v string) *GetSessionResponseBodyDataContexts {
	s.Id = &v
	return s
}

func (s *GetSessionResponseBodyDataContexts) SetName(v string) *GetSessionResponseBodyDataContexts {
	s.Name = &v
	return s
}

func (s *GetSessionResponseBodyDataContexts) Validate() error {
	return dara.Validate(s)
}
