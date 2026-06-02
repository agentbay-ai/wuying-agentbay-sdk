// This file is auto-generated, don't edit it. Thanks.
package client

import (
	"github.com/alibabacloud-go/tea/dara"
)

type iListSessionRequest interface {
	dara.Model
	String() string
	GoString() string
	SetAuthorization(v string) *ListSessionRequest
	GetAuthorization() *string
	SetImageId(v string) *ListSessionRequest
	GetImageId() *string
	SetLabels(v string) *ListSessionRequest
	GetLabels() *string
	SetMaxResults(v int32) *ListSessionRequest
	GetMaxResults() *int32
	SetNextToken(v string) *ListSessionRequest
	GetNextToken() *string
	SetStatus(v string) *ListSessionRequest
	GetStatus() *string
}

type ListSessionRequest struct {
	Authorization *string `json:"Authorization,omitempty" xml:"Authorization,omitempty"`
	ImageId       *string `json:"ImageId,omitempty" xml:"ImageId,omitempty"`
	Labels        *string `json:"Labels,omitempty" xml:"Labels,omitempty"`
	MaxResults    *int32  `json:"MaxResults,omitempty" xml:"MaxResults,omitempty"`
	NextToken     *string `json:"NextToken,omitempty" xml:"NextToken,omitempty"`
	Status        *string `json:"Status,omitempty" xml:"Status,omitempty"`
}

func (s ListSessionRequest) String() string {
	return dara.Prettify(s)
}

func (s ListSessionRequest) GoString() string {
	return s.String()
}

func (s *ListSessionRequest) GetAuthorization() *string {
	return s.Authorization
}

func (s *ListSessionRequest) GetImageId() *string {
	return s.ImageId
}

func (s *ListSessionRequest) GetLabels() *string {
	return s.Labels
}

func (s *ListSessionRequest) GetMaxResults() *int32 {
	return s.MaxResults
}

func (s *ListSessionRequest) GetNextToken() *string {
	return s.NextToken
}

func (s *ListSessionRequest) GetStatus() *string {
	return s.Status
}

func (s *ListSessionRequest) SetAuthorization(v string) *ListSessionRequest {
	s.Authorization = &v
	return s
}

func (s *ListSessionRequest) SetImageId(v string) *ListSessionRequest {
	s.ImageId = &v
	return s
}

func (s *ListSessionRequest) SetLabels(v string) *ListSessionRequest {
	s.Labels = &v
	return s
}

func (s *ListSessionRequest) SetMaxResults(v int32) *ListSessionRequest {
	s.MaxResults = &v
	return s
}

func (s *ListSessionRequest) SetNextToken(v string) *ListSessionRequest {
	s.NextToken = &v
	return s
}

func (s *ListSessionRequest) SetStatus(v string) *ListSessionRequest {
	s.Status = &v
	return s
}

func (s *ListSessionRequest) Validate() error {
	return dara.Validate(s)
}
