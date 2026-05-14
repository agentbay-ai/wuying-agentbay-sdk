// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class BindContextsRequestPersistenceDataList extends $dara.Model {
  contextId?: string;
  path?: string;
  policy?: string;
  type?: string;
  mountConfig?: string;
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
      mountConfig: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

export class BindContextsRequest extends $dara.Model {
  authorization?: string;
  persistenceDataList?: BindContextsRequestPersistenceDataList[];
  sessionId?: string;
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      persistenceDataList: 'PersistenceDataList',
      sessionId: 'SessionId',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      persistenceDataList: { 'type': 'array', 'itemType': BindContextsRequestPersistenceDataList },
      sessionId: 'string',
    };
  }

  validate() {
    if(Array.isArray(this.persistenceDataList)) {
      $dara.Model.validateArray(this.persistenceDataList);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

