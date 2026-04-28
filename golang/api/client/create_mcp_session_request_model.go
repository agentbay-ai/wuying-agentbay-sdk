// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iCreateMcpSessionRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *CreateMcpSessionRequest
	GetAuthorization() *string
	SetContextId(v string) *CreateMcpSessionRequest
	GetContextId() *string
	SetEnableRecord(v bool) *CreateMcpSessionRequest
	GetEnableRecord() *bool
	SetExternalUserId(v string) *CreateMcpSessionRequest
	GetExternalUserId() *string
	SetImageId(v string) *CreateMcpSessionRequest
	GetImageId() *string
	SetTimeout(v int32) *CreateMcpSessionRequest
	GetTimeout() *int32
	SetLabels(v string) *CreateMcpSessionRequest
	GetLabels() *string
	SetMcpPolicyId(v string) *CreateMcpSessionRequest
	GetMcpPolicyId() *string
	SetNetworkId(v string) *CreateMcpSessionRequest
	GetNetworkId() *string
	SetPersistenceDataList(v []*CreateMcpSessionRequestPersistenceDataList) *CreateMcpSessionRequest
	GetPersistenceDataList() []*CreateMcpSessionRequestPersistenceDataList
	SetSessionId(v string) *CreateMcpSessionRequest
	GetSessionId() *string
	SetVpcResource(v bool) *CreateMcpSessionRequest
	GetVpcResource() *bool
	SetExtraConfigs(v string) *CreateMcpSessionRequest
	GetExtraConfigs() *string
	SetSdkStats(v string) *CreateMcpSessionRequest
	GetSdkStats() *string
	SetLoginRegionId(v string) *CreateMcpSessionRequest
	GetLoginRegionId() *string
	SetManualRelease(v bool) *CreateMcpSessionRequest
	GetManualRelease() *bool
	SetMaxRuntime(v int32) *CreateMcpSessionRequest
	GetMaxRuntime() *int32
	SetLoadSkill(v bool) *CreateMcpSessionRequest
	GetLoadSkill() *bool
	SetSkills(v []*string) *CreateMcpSessionRequest
	GetSkills() []*string
}

type CreateMcpSessionRequest struct {
	Authorization       *string                                       `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ContextId           *string                                       `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	EnableRecord        *bool                                         `json:"EnableRecord,omitempty" xml:"EnableRecord,omitempty"`
	ExternalUserId      *string                                       `json:"ExternalUserId,omitempty" xml:"ExternalUserId,omitempty"`
	ImageId             *string                                       `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	Timeout             *int32                                        `json:"Timeout,omitempty" xml:"Timeout,omitempty"`
	ManualRelease       *bool                                         `json:"ManualRelease,omitempty" xml:"ManualRelease,omitempty"`
	MaxRuntime          *int32                                        `json:"MaxRuntime,omitempty" xml:"MaxRuntime,omitempty"`
	Labels              *string                                       `json:"Labels,omitempty" xml:"Labels,omitempty"`
	McpPolicyId         *string                                       `json:"McpPolicyId,omitempty" xml:"McpPolicyId,omitempty"`
	NetworkId           *string                                       `json:"NetworkId,omitempty" xml:"NetworkId,omitempty"`
	PersistenceDataList []*CreateMcpSessionRequestPersistenceDataList `json:"PersistenceDataList,omitempty" xml:"PersistenceDataList,omitempty" type:"Repeated"`
	SessionId           *string                                       `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	VpcResource         *bool                                         `json:"VpcResource,omitempty" xml:"VpcResource,omitempty"`
	ExtraConfigs        *string                                       `json:"ExtraConfigs,omitempty" xml:"ExtraConfigs,omitempty"`
	SdkStats            *string                                       `json:"SdkStats,omitempty" xml:"SdkStats,omitempty"`
	LoginRegionId       *string                                       `json:"LoginRegionId,omitempty" xml:"LoginRegionId,omitempty"`
	LoadSkill           *bool                                         `json:"LoadSkill,omitempty" xml:"LoadSkill,omitempty"`
	Skills              []*string                                     `json:"Skills,omitempty" xml:"Skills,omitempty" type:"Repeated"`
}

func (s CreateMcpSessionRequest) String() string {
	return dara.Prettify(s)
}

func (s CreateMcpSessionRequest) GoString() string {
	return s.String()
}

func (s *CreateMcpSessionRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *CreateMcpSessionRequest) GetContextId() *string {
	return s.ContextId
}

func (s *CreateMcpSessionRequest) GetEnableRecord() *bool {
	return s.EnableRecord
}

func (s *CreateMcpSessionRequest) GetExternalUserId() *string {
	return s.ExternalUserId
}

func (s *CreateMcpSessionRequest) GetImageId() *string {
	return s.ImageId
}

func (s *CreateMcpSessionRequest) GetTimeout() *int32 {
	return s.Timeout
}

func (s *CreateMcpSessionRequest) GetManualRelease() *bool {
	return s.ManualRelease
}

func (s *CreateMcpSessionRequest) GetMaxRuntime() *int32 {
	return s.MaxRuntime
}

func (s *CreateMcpSessionRequest) GetLabels() *string {
	return s.Labels
}

func (s *CreateMcpSessionRequest) GetMcpPolicyId() *string {
	return s.McpPolicyId
}

func (s *CreateMcpSessionRequest) GetNetworkId() *string {
	return s.NetworkId
}

func (s *CreateMcpSessionRequest) GetPersistenceDataList() []*CreateMcpSessionRequestPersistenceDataList {
	return s.PersistenceDataList
}

func (s *CreateMcpSessionRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *CreateMcpSessionRequest) GetVpcResource() *bool {
	return s.VpcResource
}

func (s *CreateMcpSessionRequest) SetAuthorization(v string) *CreateMcpSessionRequest {
	s.Authorization = &v
	return s
}

func (s *CreateMcpSessionRequest) SetContextId(v string) *CreateMcpSessionRequest {
	s.ContextId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetEnableRecord(v bool) *CreateMcpSessionRequest {
	s.EnableRecord = &v
	return s
}

func (s *CreateMcpSessionRequest) SetExternalUserId(v string) *CreateMcpSessionRequest {
	s.ExternalUserId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetImageId(v string) *CreateMcpSessionRequest {
	s.ImageId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetTimeout(v int32) *CreateMcpSessionRequest {
	s.Timeout = &v
	return s
}

func (s *CreateMcpSessionRequest) SetManualRelease(v bool) *CreateMcpSessionRequest {
	s.ManualRelease = &v
	return s
}

func (s *CreateMcpSessionRequest) SetMaxRuntime(v int32) *CreateMcpSessionRequest {
	s.MaxRuntime = &v
	return s
}

func (s *CreateMcpSessionRequest) SetLabels(v string) *CreateMcpSessionRequest {
	s.Labels = &v
	return s
}

func (s *CreateMcpSessionRequest) SetMcpPolicyId(v string) *CreateMcpSessionRequest {
	s.McpPolicyId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetNetworkId(v string) *CreateMcpSessionRequest {
	s.NetworkId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetPersistenceDataList(v []*CreateMcpSessionRequestPersistenceDataList) *CreateMcpSessionRequest {
	s.PersistenceDataList = v
	return s
}

func (s *CreateMcpSessionRequest) SetSessionId(v string) *CreateMcpSessionRequest {
	s.SessionId = &v
	return s
}

func (s *CreateMcpSessionRequest) SetVpcResource(v bool) *CreateMcpSessionRequest {
	s.VpcResource = &v
	return s
}

func (s *CreateMcpSessionRequest) SetExtraConfigs(v string) *CreateMcpSessionRequest {
	s.ExtraConfigs = &v
	return s
}

func (s *CreateMcpSessionRequest) GetExtraConfigs() *string {
	return s.ExtraConfigs
}

func (s *CreateMcpSessionRequest) SetSdkStats(v string) *CreateMcpSessionRequest {
	s.SdkStats = &v
	return s
}

func (s *CreateMcpSessionRequest) GetSdkStats() *string {
	return s.SdkStats
}

func (s *CreateMcpSessionRequest) SetLoginRegionId(v string) *CreateMcpSessionRequest {
	s.LoginRegionId = &v
	return s
}

func (s *CreateMcpSessionRequest) GetLoginRegionId() *string {
	return s.LoginRegionId
}

func (s *CreateMcpSessionRequest) GetLoadSkill() *bool {
	return s.LoadSkill
}

func (s *CreateMcpSessionRequest) GetSkills() []*string {
	return s.Skills
}

func (s *CreateMcpSessionRequest) SetLoadSkill(v bool) *CreateMcpSessionRequest {
	s.LoadSkill = &v
	return s
}

func (s *CreateMcpSessionRequest) SetSkills(v []*string) *CreateMcpSessionRequest {
	s.Skills = v
	return s
}

func (s *CreateMcpSessionRequest) Validate() error {
	return dara.Validate(s)
}

type CreateMcpSessionRequestPersistenceDataList struct {
	ContextId *string `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	Path      *string `json:"Path,omitempty" xml:"Path,omitempty"`
	Policy    *string `json:"Policy,omitempty" xml:"Policy,omitempty"`
}

func (s CreateMcpSessionRequestPersistenceDataList) String() string {
	return dara.Prettify(s)
}

func (s CreateMcpSessionRequestPersistenceDataList) GoString() string {
	return s.String()
}

func (s *CreateMcpSessionRequestPersistenceDataList) GetContextId() *string {
	return s.ContextId
}

func (s *CreateMcpSessionRequestPersistenceDataList) GetPath() *string {
	return s.Path
}

func (s *CreateMcpSessionRequestPersistenceDataList) GetPolicy() *string {
	return s.Policy
}

func (s *CreateMcpSessionRequestPersistenceDataList) SetContextId(v string) *CreateMcpSessionRequestPersistenceDataList {
	s.ContextId = &v
	return s
}

func (s *CreateMcpSessionRequestPersistenceDataList) SetPath(v string) *CreateMcpSessionRequestPersistenceDataList {
	s.Path = &v
	return s
}

func (s *CreateMcpSessionRequestPersistenceDataList) SetPolicy(v string) *CreateMcpSessionRequestPersistenceDataList {
	s.Policy = &v
	return s
}

func (s *CreateMcpSessionRequestPersistenceDataList) Validate() error {
	return dara.Validate(s)
}
