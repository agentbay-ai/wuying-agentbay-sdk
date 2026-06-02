// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class ListSessionResponseBodyData extends $dara.Model {
  appInstanceId?: string;
  imageId?: string;
  sessionId?: string;
  sessionStatus?: string;
  static names(): { [key: string]: string } {
    return {
      appInstanceId: 'AppInstanceId',
      imageId: 'ImageId',
      sessionId: 'SessionId',
      sessionStatus: 'SessionStatus',
    };
  }

  static types(): { [key: string]: any } {
    return {
      appInstanceId: 'string',
      imageId: 'string',
      sessionId: 'string',
      sessionStatus: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

