// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iBindContextsRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *BindContextsRequest
	GetAuthorization() *string
	SetPersistenceDataList(v []*BindContextsRequestPersistenceDataList) *BindContextsRequest
	GetPersistenceDataList() []*BindContextsRequestPersistenceDataList
	SetSessionId(v string) *BindContextsRequest
	GetSessionId() *string
}

type BindContextsRequest struct {
	Authorization       *string                                   `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	PersistenceDataList []*BindContextsRequestPersistenceDataList `json:"PersistenceDataList,omitempty" xml:"PersistenceDataList,omitempty" type:"Repeated"`
	SessionId           *string                                   `json:"SessionId,omitempty" xml:"SessionId,omitempty"`
}

func (s BindContextsRequest) String() string {
	return dara.Prettify(s)
}

func (s BindContextsRequest) GoString() string {
	return s.String()
}

func (s *BindContextsRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *BindContextsRequest) GetPersistenceDataList() []*BindContextsRequestPersistenceDataList {
	return s.PersistenceDataList
}

func (s *BindContextsRequest) GetSessionId() *string {
	return s.SessionId
}

func (s *BindContextsRequest) SetAuthorization(v string) *BindContextsRequest {
	s.Authorization = &v
	return s
}

func (s *BindContextsRequest) SetPersistenceDataList(v []*BindContextsRequestPersistenceDataList) *BindContextsRequest {
	s.PersistenceDataList = v
	return s
}

func (s *BindContextsRequest) SetSessionId(v string) *BindContextsRequest {
	s.SessionId = &v
	return s
}

func (s *BindContextsRequest) Validate() error {
	if s.PersistenceDataList != nil {
		for _, item := range s.PersistenceDataList {
			if item != nil {
				if err := item.Validate(); err != nil {
					return err
				}
			}
		}
	}
	return nil
}

type BindContextsRequestPersistenceDataList struct {
	ContextId   *string `json:"ContextId,omitempty" xml:"ContextId,omitempty"`
	Path        *string `json:"Path,omitempty" xml:"Path,omitempty"`
	Policy      *string `json:"Policy,omitempty" xml:"Policy,omitempty"`
	Type        *string `json:"Type,omitempty" xml:"Type,omitempty"`
	MountConfig *string `json:"MountConfig,omitempty" xml:"MountConfig,omitempty"`
}

func (s BindContextsRequestPersistenceDataList) String() string {
	return dara.Prettify(s)
}

func (s BindContextsRequestPersistenceDataList) GoString() string {
	return s.String()
}

func (s *BindContextsRequestPersistenceDataList) GetContextId() *string {
	return s.ContextId
}

func (s *BindContextsRequestPersistenceDataList) GetPath() *string {
	return s.Path
}

func (s *BindContextsRequestPersistenceDataList) GetPolicy() *string {
	return s.Policy
}

func (s *BindContextsRequestPersistenceDataList) GetType() *string {
	return s.Type
}

func (s *BindContextsRequestPersistenceDataList) GetMountConfig() *string {
	return s.MountConfig
}

func (s *BindContextsRequestPersistenceDataList) SetContextId(v string) *BindContextsRequestPersistenceDataList {
	s.ContextId = &v
	return s
}

func (s *BindContextsRequestPersistenceDataList) SetPath(v string) *BindContextsRequestPersistenceDataList {
	s.Path = &v
	return s
}

func (s *BindContextsRequestPersistenceDataList) SetPolicy(v string) *BindContextsRequestPersistenceDataList {
	s.Policy = &v
	return s
}

func (s *BindContextsRequestPersistenceDataList) SetType(v string) *BindContextsRequestPersistenceDataList {
	s.Type = &v
	return s
}

func (s *BindContextsRequestPersistenceDataList) SetMountConfig(v string) *BindContextsRequestPersistenceDataList {
	s.MountConfig = &v
	return s
}

func (s *BindContextsRequestPersistenceDataList) Validate() error {
	return dara.Validate(s)
}
