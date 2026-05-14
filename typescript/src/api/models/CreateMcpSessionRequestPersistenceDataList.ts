// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class CreateMcpSessionRequestPersistenceDataList extends $dara.Model {
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

