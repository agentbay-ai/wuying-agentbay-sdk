// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';

export class DescribeContextFilesResponseBodyData extends $dara.Model {
  fileId?: string;
  fileName?: string;
  filePath?: string;
  fileType?: string;
  gmtCreate?: string;
  gmtModified?: string;
  size?: number;
  status?: string;
  static names(): { [key: string]: string } {
    return {
      fileId: 'FileId',
      fileName: 'FileName',
      filePath: 'FilePath',
      fileType: 'FileType',
      gmtCreate: 'GmtCreate',
      gmtModified: 'GmtModified',
      size: 'Size',
      status: 'Status',
    };
  }

  static types(): { [key: string]: any } {
    return {
      fileId: 'string',
      fileName: 'string',
      filePath: 'string',
      fileType: 'string',
      gmtCreate: 'string',
      gmtModified: 'string',
      size: 'number',
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

export class DescribeContextFilesResponseBody extends $dara.Model {
  code?: string;
  count?: number;
  data?: DescribeContextFilesResponseBodyData[];
  httpStatusCode?: number;
  message?: string;
  requestId?: string;
  success?: boolean;
  nextToken?: string;
  maxResults?: number;
  static names(): { [key: string]: string } {
    return {
      code: 'Code',
      count: 'Count',
      data: 'Data',
      httpStatusCode: 'HttpStatusCode',
      message: 'Message',
      requestId: 'RequestId',
      success: 'Success',
      nextToken: 'NextToken',
      maxResults: 'MaxResults',
    };
  }

  static types(): { [key: string]: any } {
    return {
      code: 'string',
      count: 'number',
      data: { type: 'array', itemType: DescribeContextFilesResponseBodyData },
      httpStatusCode: 'number',
      message: 'string',
      requestId: 'string',
      success: 'boolean',
      nextToken: 'string',
      maxResults: 'number',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
} 