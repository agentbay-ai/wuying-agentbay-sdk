import { Session } from "../session";

export interface EnvResult {
  requestId: string;
  success: boolean;
  envs: Record<string, string>;
  errorMessage?: string;
}

export interface BoolResult {
  requestId: string;
  success: boolean;
  errorMessage?: string;
}

const ENV_SERVER = "wuying_system";
const ENV_TOOLS = ["set_env", "get_env"];

export class Env {
  private session: Session;

  private toolsRegistered = false;

  constructor(session: Session) {
    this.session = session;
  }

  /**
   * Pre-started sandbox instances may not include env tools in their initial
   * ToolList. Register them so the SDK can route through LinkUrl.
   */
  private ensureEnvToolsRegistered(): void {
    if (this.toolsRegistered) return;
    this.toolsRegistered = true;
    for (const toolName of ENV_TOOLS) {
      if (!this.session.getMcpServerForTool(toolName)) {
        this.session.mcpTools.push({
          name: toolName,
          server: ENV_SERVER,
          description: "",
          inputSchema: {},
          tool: toolName,
        });
      }
    }
  }

  async set(envs: Record<string, string>): Promise<BoolResult> {
    this.ensureEnvToolsRegistered();
    if (!envs || Object.keys(envs).length === 0) {
      throw new Error("envs must not be empty");
    }
    for (const [key, value] of Object.entries(envs)) {
      if (typeof key !== "string") {
        throw new Error(`Key must be string, got ${typeof key}`);
      }
      if (typeof value !== "string") {
        throw new Error(
          `Value for key '${key}' must be string, got ${typeof value}`
        );
      }
    }

    const envsArray = Object.entries(envs).map(([key, value]) => ({
      key,
      value,
    }));
    try {
      const result = await this.session.callMcpTool(
        "set_env",
        { envs: envsArray },
        false
      );
      return {
        requestId: result.requestId,
        success: result.success,
        errorMessage: result.errorMessage || undefined,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        errorMessage: `Failed to set environment variables: ${error}`,
      };
    }
  }

  async get(keys?: string[]): Promise<EnvResult> {
    this.ensureEnvToolsRegistered();
    const args: Record<string, unknown> = {};
    if (keys && keys.length > 0) {
      args.keys = keys;
    }
    try {
      const result = await this.session.callMcpTool("get_env", args, false);
      let envs: Record<string, string> = {};
      if (result.success && result.data) {
        try {
          const parsed =
            typeof result.data === "string"
              ? JSON.parse(result.data)
              : result.data;
          if (parsed && typeof parsed === "object") {
            envs = parsed as Record<string, string>;
          }
        } catch {
          // leave envs empty if payload is not valid JSON
        }
      }
      return {
        requestId: result.requestId,
        success: result.success,
        envs,
        errorMessage: result.errorMessage || undefined,
      };
    } catch (error) {
      return {
        requestId: "",
        success: false,
        envs: {},
        errorMessage: `Failed to get environment variables: ${error}`,
      };
    }
  }
}
