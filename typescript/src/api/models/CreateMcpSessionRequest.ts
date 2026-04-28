// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';
import { CreateMcpSessionRequestPersistenceDataList } from "./CreateMcpSessionRequestPersistenceDataList";


export class CreateMcpSessionRequest extends $dara.Model {
  authorization?: string;
  contextId?: string;
  enableRecord?: boolean;
  externalUserId?: string;
  imageId?: string;
  timeout?: number;
  maxRuntime?: number;
  manualRelease?: boolean;
  labels?: string;
  mcpPolicyId?: string;
  networkId?: string;
  persistenceDataList?: CreateMcpSessionRequestPersistenceDataList[];
  sessionId?: string;
  vpcResource?: boolean;
  extraConfigs?: string;
  sdkStats?: string;
  loginRegionId?: string;
  loadSkill?: boolean;
  skills?: string[];
  static names(): { [key: string]: string } {
    return {
      authorization: 'Authorization',
      contextId: 'ContextId',
      enableRecord: 'EnableRecord',
      externalUserId: 'ExternalUserId',
      imageId: 'ImageId',
      timeout: 'Timeout',
      maxRuntime: 'MaxRuntime',
      manualRelease: 'ManualRelease',
      labels: 'Labels',
      mcpPolicyId: 'McpPolicyId',
      networkId: 'NetworkId',
      persistenceDataList: 'PersistenceDataList',
      sessionId: 'SessionId',
      vpcResource: 'VpcResource',
      extraConfigs: 'ExtraConfigs',
      sdkStats: 'SdkStats',
      loginRegionId: 'LoginRegionId',
      loadSkill: 'LoadSkill',
      skills: 'Skills',
    };
  }

  static types(): { [key: string]: any } {
    return {
      authorization: 'string',
      contextId: 'string',
      enableRecord: 'boolean',
      externalUserId: 'string',
      imageId: 'string',
      timeout: 'number',
      maxRuntime: 'number',
      manualRelease: 'boolean',
      labels: 'string',
      mcpPolicyId: 'string',
      networkId: 'string',
      persistenceDataList: { 'type': 'array', 'itemType': CreateMcpSessionRequestPersistenceDataList },
      sessionId: 'string',
      vpcResource: 'boolean',
      extraConfigs: 'string',
      sdkStats: 'string',
      loginRegionId: 'string',
      loadSkill: 'boolean',
      skills: { 'type': 'array', 'itemType': 'string' },
    };
  }

  validate() {
    if(Array.isArray(this.persistenceDataList)) {
      $dara.Model.validateArray(this.persistenceDataList);
    }
    if(Array.isArray(this.skills)) {
      $dara.Model.validateArray(this.skills);
    }
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

