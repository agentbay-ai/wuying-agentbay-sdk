// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class CreateMcpSessionRequestPersistenceDataListMountConfig extends $dara.Model {
  accessMode?: string;
  storageMode?: string;
  objectKey?: string;
  static names(): { [key: string]: string } {
    return {
      accessMode: 'AccessMode',
      storageMode: 'StorageMode',
      objectKey: 'ObjectKey',
    };
  }

  static types(): { [key: string]: any } {
    return {
      accessMode: 'string',
      storageMode: 'string',
      objectKey: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class CreateMcpSessionRequestPersistenceDataList extends $dara.Model {
  contextId?: string;
  path?: string;
  policy?: string;
  type?: string;
  mountConfig?: CreateMcpSessionRequestPersistenceDataListMountConfig;
  static names(): { [key: string]: string } {
    return {
      contextId: 'ContextId',
      path: 'Path',
      policy: 'Policy',
      type: 'Type',
      mountConfig: 'MountConfig',
    };
  }

  static types(): { [key: string]: any } {
    return {
      contextId: 'string',
      path: 'string',
      policy: 'string',
      type: 'string',
      mountConfig: CreateMcpSessionRequestPersistenceDataListMountConfig,
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

