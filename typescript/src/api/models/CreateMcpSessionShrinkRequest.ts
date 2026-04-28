// This file is auto-generated, don't edit it
import * as $dara from '@darabonba/typescript';


export class CreateMcpSessionShrinkRequest extends $dara.Model {
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
  persistenceDataListShrink?: string;
  sessionId?: string;
  vpcResource?: boolean;
  extraConfigs?: string;
  sdkStats?: string;
  loginRegionId?: string;
  loadSkill?: boolean;
  skillsShrink?: string;
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
      persistenceDataListShrink: 'PersistenceDataList',
      sessionId: 'SessionId',
      vpcResource: 'VpcResource',
      extraConfigs: 'ExtraConfigs',
      sdkStats: 'SdkStats',
      loginRegionId: 'LoginRegionId',
      loadSkill: 'LoadSkill',
      skillsShrink: 'Skills',
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
      persistenceDataListShrink: 'string',
      sessionId: 'string',
      vpcResource: 'boolean',
      extraConfigs: 'string',
      sdkStats: 'string',
      loginRegionId: 'string',
      loadSkill: 'boolean',
      skillsShrink: 'string',
    };
  }

  validate() {
    super.validate();
  }

  constructor(map?: { [key: string]: any }) {
    super(map);
  }
}

