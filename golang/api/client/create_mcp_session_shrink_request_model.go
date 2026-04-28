// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iCreateMcpSessionShrinkRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *CreateMcpSessionShrinkRequest
	GetAuthorization() *string
	SetContextId(v string) *CreateMcpSessionShrinkRequest
	GetContextId() *string
	SetEnableRecord(v bool) *CreateMcpSessionShrinkRequest
	GetEnableRecord() *bool
	SetExternalUserId(v string) *CreateMcpSessionShrinkRequest
	GetExternalUserId() *string
	SetImageId(v string) *CreateMcpSessionShrinkRequest
	GetImageId() *string
	SetTimeout(v int32) *CreateMcpSessionShrinkRequest
	GetTimeout() *int32
	SetLabels(v string) *CreateMcpSessionShrinkRequest
	GetLabels() *string
	SetMcpPolicyId(v string) *CreateMcpSessionShrinkRequest
	GetMcpPolicyId() *string
	SetNetworkId(v string) *CreateMcpSessionShrinkRequest
	GetNetworkId() *string
	SetPersistenceDataListShrink(v string) *CreateMcpSessionShrinkRequest
	GetPersistenceDataListShrink() *string
	SetSessionId(v string) *CreateMcpSessionShrinkRequest
	GetSessionId() *string
	SetVpcResource(v bool) *CreateMcpSessionShrinkRequest
	GetVpcResource() *bool
	SetExtraConfigs(v string) *CreateMcpSessionShrinkRequest
	GetExtraConfigs() *string
	SetSdkStats(v string) *CreateMcpSessionShrinkRequest
	GetSdkStats() *string
	SetLoginRegionId(v string) *CreateMcpSessionShrinkRequest
	GetLoginRegionId() *string
	SetManualRelease(v bool) *CreateMcpSessionShrinkRequest
	GetManualRelease() *bool
	SetMaxRuntime(v int32) *CreateMcpSessionShrinkRequest
	GetMaxRuntime() *int32
	SetLoadSkill(v bool) *CreateMcpSessionShrinkRequest
	GetLoadSkill() *bool
	SetSkillsShrink(v string) *CreateMcpSessionShrinkRequest
	GetSkillsShrink() *string
}

type CreateMcpSessionShrinkRequest struct {
	Authorization             *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ContextId                 *string `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	EnableRecord              *bool   `json:"EnableRecord,omitempty" xml:"EnableRecord,omitempty"`
	ExternalUserId            *string `json:"ExternalUserId,omitempty" xml:"ExternalUserId,omitempty"`
	ImageId                   *string `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	Timeout                   *int32  `json:"Timeout,omitempty" xml:"Timeout,omitempty"`
	ManualRelease             *bool   `json:"ManualRelease,omitempty" xml:"ManualRelease,omitempty"`
	MaxRuntime                *int32  `json:"MaxRuntime,omitempty" xml:"MaxRuntime,omitempty"`
	Labels                    *string `json:"Labels,omitempty" xml:"Labels,omitempty"`
	McpPolicyId               *string `json:"McpPolicyId,omitempty" xml:"McpPolicyId,omitempty"`
	NetworkId                 *string `json:"NetworkId,omitempty" xml:"NetworkId,omitempty"`
	PersistenceDataListShrink *string `json:"PersistenceDataList,omitempty" xml:"PersistenceDataList,omitempty"`
	SessionId                 *string `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
	VpcResource               *bool   `json:"VpcResource,omitempty" xml:"VpcResource,omitempty"`
	ExtraConfigs              *string `json:"ExtraConfigs,omitempty" xml:"ExtraConfigs,omitempty"`
	SdkStats                  *string `json:"SdkStats,omitempty" xml:"SdkStats,omitempty"`
	LoginRegionId             *string `json:"LoginRegionId,omitempty" xml:"LoginRegionId,omitempty"`
	LoadSkill                 *bool   `json:"LoadSkill,omitempty" xml:"LoadSkill,omitempty"`
	SkillsShrink              *string `json:"Skills,omitempty" xml:"Skills,omitempty"`
}

func (s CreateMcpSessionShrinkRequest) String() string {
	return dara.Prettify(s)
}

func (s CreateMcpSessionShrinkRequest) GoString() string {
	return s.String()
}

func (s *CreateMcpSessionShrinkRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *CreateMcpSessionShrinkRequest) GetContextId() *string {
	return s.ContextId
}

func (s *CreateMcpSessionShrinkRequest) GetEnableRecord() *bool {
	return s.EnableRecord
}

func (s *CreateMcpSessionShrinkRequest) GetExternalUserId() *string {
	return s.ExternalUserId
}

func (s *CreateMcpSessionShrinkRequest) GetImageId() *string {
	return s.ImageId
}

func (s *CreateMcpSessionShrinkRequest) GetTimeout() *int32 {
	return s.Timeout
}

func (s *CreateMcpSessionShrinkRequest) GetManualRelease() *bool {
	return s.ManualRelease
}

func (s *CreateMcpSessionShrinkRequest) GetMaxRuntime() *int32 {
	return s.MaxRuntime
}

func (s *CreateMcpSessionShrinkRequest) GetLabels() *string {
	return s.Labels
}

func (s *CreateMcpSessionShrinkRequest) GetMcpPolicyId() *string {
	return s.McpPolicyId
}

func (s *CreateMcpSessionShrinkRequest) GetNetworkId() *string {
	return s.NetworkId
}

func (s *CreateMcpSessionShrinkRequest) GetPersistenceDataListShrink() *string {
	return s.PersistenceDataListShrink
}

func (s *CreateMcpSessionShrinkRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *CreateMcpSessionShrinkRequest) GetVpcResource() *bool {
	return s.VpcResource
}

func (s *CreateMcpSessionShrinkRequest) SetAuthorization(v string) *CreateMcpSessionShrinkRequest {
	s.Authorization = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetContextId(v string) *CreateMcpSessionShrinkRequest {
	s.ContextId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetEnableRecord(v bool) *CreateMcpSessionShrinkRequest {
	s.EnableRecord = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetExternalUserId(v string) *CreateMcpSessionShrinkRequest {
	s.ExternalUserId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetImageId(v string) *CreateMcpSessionShrinkRequest {
	s.ImageId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetTimeout(v int32) *CreateMcpSessionShrinkRequest {
	s.Timeout = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetManualRelease(v bool) *CreateMcpSessionShrinkRequest {
	s.ManualRelease = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetMaxRuntime(v int32) *CreateMcpSessionShrinkRequest {
	s.MaxRuntime = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetLabels(v string) *CreateMcpSessionShrinkRequest {
	s.Labels = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetMcpPolicyId(v string) *CreateMcpSessionShrinkRequest {
	s.McpPolicyId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetNetworkId(v string) *CreateMcpSessionShrinkRequest {
	s.NetworkId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetPersistenceDataListShrink(v string) *CreateMcpSessionShrinkRequest {
	s.PersistenceDataListShrink = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetSessionId(v string) *CreateMcpSessionShrinkRequest {
	s.SessionId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetVpcResource(v bool) *CreateMcpSessionShrinkRequest {
	s.VpcResource = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) GetExtraConfigs() *string {
	return s.ExtraConfigs
}

func (s *CreateMcpSessionShrinkRequest) SetExtraConfigs(v string) *CreateMcpSessionShrinkRequest {
	s.ExtraConfigs = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) GetSdkStats() *string {
	return s.SdkStats
}

func (s *CreateMcpSessionShrinkRequest) SetSdkStats(v string) *CreateMcpSessionShrinkRequest {
	s.SdkStats = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) GetLoginRegionId() *string {
	return s.LoginRegionId
}

func (s *CreateMcpSessionShrinkRequest) SetLoginRegionId(v string) *CreateMcpSessionShrinkRequest {
	s.LoginRegionId = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) GetLoadSkill() *bool {
	return s.LoadSkill
}

func (s *CreateMcpSessionShrinkRequest) GetSkillsShrink() *string {
	return s.SkillsShrink
}

func (s *CreateMcpSessionShrinkRequest) SetLoadSkill(v bool) *CreateMcpSessionShrinkRequest {
	s.LoadSkill = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) SetSkillsShrink(v string) *CreateMcpSessionShrinkRequest {
	s.SkillsShrink = &v
	return s
}

func (s *CreateMcpSessionShrinkRequest) Validate() error {
	return dara.Validate(s)
}
