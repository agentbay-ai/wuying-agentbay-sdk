// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class ListSessionRequest extends $dara.Model {
  authorization?: string;
  imageId?: string;
  labels?: string;
  maxResults?: number;
  nextToken?: string;
  status?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      imageId: 'ImageId',
      labels: 'Labels',
      maxResults: 'MaxResults',
      nextToken: 'NextToken',
      status: 'Status',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      imageId: 'string',
      labels: 'string',
      maxResults: 'number',
      nextToken: 'string',
      status: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

