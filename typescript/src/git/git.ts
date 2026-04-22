import { Session } from "../session";
import { CommandResult } from "../types/api-response";
import {
  GitError,
  GitAuthError,
  GitNotFoundError,
  GitConflictError,
  GitNotARepoError,
} from "./errors";
import {
  GitCloneOpts,
  GitCloneResult,
  GitInitOpts,
  GitInitResult,
  GitAddOpts,
  GitCommitOpts,
  GitCommitResult,
  GitStatusOpts,
  GitFileStatus,
  GitStatusResult,
  GitLogOpts,
  GitLogEntry,
  GitLogResult,
  GitBranchListOpts,
  GitBranchInfo,
  GitBranchListResult,
  GitBranchCreateOpts,
  GitBranchDeleteOpts,
  GitCheckoutOpts,
  GitRemoteAddOpts,
  GitResetOpts,
  GitRestoreOpts,
  GitPullOpts,
  GitConfigOpts,
} from "./types";

/**
 * Default environment variables for all git commands.
 * GIT_TERMINAL_PROMPT=0 prevents git from prompting for credentials interactively,
 * which would cause the command to hang in a non-interactive environment.
 */
const DEFAULT_GIT_ENV: Record<string, string> = {
  GIT_TERMINAL_PROMPT: "0",
  LC_ALL: "C",
};

/**
 * Default timeout for git operations in milliseconds (30 seconds).
 */
const DEFAULT_GIT_TIMEOUT_MS = 30000;

/**
 * Default timeout for git clone operations in milliseconds (5 minutes).
 */
const DEFAULT_CLONE_TIMEOUT_MS = 300000;

/**
 * Default timeout for git pull operations in milliseconds (2 minutes).
 */
const DEFAULT_PULL_TIMEOUT_MS = 120000;

/**
 * Provides high-level git operations in the AgentBay cloud environment.
 *
 * This module wraps git CLI commands and executes them on the remote session
 * via the Command module. All commands run with `GIT_TERMINAL_PROMPT=0` to
 * prevent interactive credential prompts, and `LC_ALL=C` to ensure consistent
 * English output for reliable parsing. Supports repository management, branch
 * operations, staging, committing, and configuration.
 *
 * @example
 * ```typescript
 * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
 * const result = await agentBay.create();
 * if (result.success) {
 *   const cloneResult = await result.session.git.clone('https://github.com/user/repo.git');
 *   console.log('Cloned to:', cloneResult.path);
 *   await result.session.delete();
 * }
 * ```
 */
export class Git {
  private session: Session;
  private gitAvailable: boolean | null = null;

  /**
   * Initialize a Git object.
   *
   * @param session - The Session instance that this Git module belongs to.
   */
  constructor(session: Session) {
    this.session = session;
  }

  // ---------------------------------------------------------------------------
  // Private helpers
  // ---------------------------------------------------------------------------

  /**
   * Escape a string argument for safe use in a Linux shell command.
   * Uses single-quote wrapping with proper escaping of embedded single quotes.
   *
   * @param arg - The argument to escape
   * @returns The shell-escaped argument
   *
   * @example
   * shellEscape("hello") => "'hello'"
   * shellEscape("it's") => "'it'\\''s'"
   * shellEscape("") => "''"
   */
  private shellEscape(arg: string): string {
    return "'" + arg.replace(/'/g, "'\\''") + "'";
  }

  /**
   * Build a complete git command string with optional -C (repo path) prefix.
   * All arguments are shell-escaped for safe execution.
   *
   * @param args - Array of git sub-command arguments (e.g., ['clone', '--depth', '1', url])
   * @param repoPath - Optional repository path; if provided, git -C <path> is prepended
   * @returns The complete shell command string
   */
  private buildGitCommand(args: string[], repoPath?: string): string {
    const parts = ["git"];
    if (repoPath) {
      parts.push("-C", this.shellEscape(repoPath));
    }
    parts.push(...args.map((a) => this.shellEscape(a)));
    return parts.join(" ");
  }

  /**
   * Execute a standard git command via the Command module.
   * Automatically merges DEFAULT_GIT_ENV into the environment.
   *
   * Use this for straightforward git commands (clone, pull, push, etc.).
   * For commands requiring shell pipes or complex shell features, use runShell().
   *
   * @param args - Array of git sub-command arguments
   * @param repoPath - Optional repository path for git -C
   * @param opts - Optional settings (timeoutMs)
   * @returns The CommandResult from executing the git command
   */
  private async runGit(
    args: string[],
    repoPath?: string,
    opts?: { timeoutMs?: number }
  ): Promise<CommandResult> {
    const cmd = this.buildGitCommand(args, repoPath);
    return this.session.command.executeCommand(
      cmd,
      opts?.timeoutMs || DEFAULT_GIT_TIMEOUT_MS,
      undefined, // cwd is handled via git -C
      DEFAULT_GIT_ENV
    );
  }

  /**
   * Execute a raw shell command with git environment variables.
   * Automatically merges DEFAULT_GIT_ENV into the environment.
   *
   * Use this for commands that require shell features like pipes, redirects,
   * or complex command chaining. For standard git commands, prefer runGit().
   *
   * This method is also used internally for operations that need to compose
   * shell commands (e.g., credential helpers in future phases).
   *
   * @param cmd - The raw shell command string
   * @param opts - Optional settings (timeoutMs)
   * @returns The CommandResult from executing the shell command
   */
  private async runShell(
    cmd: string,
    opts?: { timeoutMs?: number }
  ): Promise<CommandResult> {
    return this.session.command.executeCommand(
      cmd,
      opts?.timeoutMs || DEFAULT_GIT_TIMEOUT_MS,
      undefined,
      DEFAULT_GIT_ENV
    );
  }

  /**
   * Check whether git is available on the remote environment.
   * The result is cached after the first successful check.
   *
   * @throws GitNotFoundError if git is not installed
   */
  private async ensureGitAvailable(): Promise<void> {
    if (this.gitAvailable === true) {
      return;
    }

    const result = await this.runGit(["--version"]);

    if (!result.success) {
      this.gitAvailable = false;
      throw new GitNotFoundError(
        "Git is not installed or not available on the remote environment. " +
          "Please ensure git is installed in the session image.",
        result.exitCode || 127,
        result.stderr || result.errorMessage || ""
      );
    }

    this.gitAvailable = true;
  }

  /**
   * Classify a failed git command result into a specific error type
   * based on stderr content and exit code.
   *
   * @param operation - The git operation name (e.g., 'clone', 'pull')
   * @param result - The failed CommandResult
   * @returns A specific GitError subclass instance
   */
  private classifyError(operation: string, result: CommandResult): GitError {
    const stderr = (result.stderr || result.errorMessage || "").toLowerCase();
    const exitCode = result.exitCode || 1;
    const rawStderr = result.stderr || result.errorMessage || "";

    // Authentication errors
    if (
      stderr.includes("authentication failed") ||
      stderr.includes("could not read username") ||
      stderr.includes("invalid credentials") ||
      stderr.includes("authorization failed") ||
      stderr.includes("access denied") ||
      stderr.includes("permission denied") ||
      stderr.includes("403")
    ) {
      return new GitAuthError(
        `Git ${operation} failed: authentication error. ${rawStderr}`,
        exitCode,
        rawStderr
      );
    }

    // Not a git repository
    if (
      stderr.includes("not a git repository") ||
      stderr.includes("does not appear to be a git repository")
    ) {
      return new GitNotARepoError(
        `Git ${operation} failed: not a git repository. ${rawStderr}`,
        exitCode,
        rawStderr
      );
    }

    // Merge/rebase conflicts
    if (
      rawStderr.includes("CONFLICT") ||
      stderr.includes("merge conflict") ||
      stderr.includes("automatic merge failed")
    ) {
      return new GitConflictError(
        `Git ${operation} failed: merge conflict. ${rawStderr}`,
        exitCode,
        rawStderr
      );
    }

    // Git not found (command not found)
    if (
      stderr.includes("command not found") ||
      stderr.includes("not found") ||
      exitCode === 127
    ) {
      return new GitNotFoundError(
        `Git ${operation} failed: git not found. ${rawStderr}`,
        exitCode,
        rawStderr
      );
    }

    // Generic git error
    return new GitError(
      `Git ${operation} failed (exit code ${exitCode}): ${rawStderr}`,
      exitCode,
      rawStderr
    );
  }

  /**
   * Derive the target directory name from a git repository URL.
   *
   * @param url - The git repository URL
   * @returns The derived directory name
   *
   * @example
   * deriveRepoDirFromUrl("https://github.com/user/repo.git") => "repo"
   * deriveRepoDirFromUrl("https://github.com/user/repo") => "repo"
   * deriveRepoDirFromUrl("git@github.com:user/repo.git") => "repo"
   */
  private deriveRepoDirFromUrl(url: string): string {
    // Remove trailing slashes
    let cleaned = url.replace(/\/+$/, "");

    // Remove .git suffix
    cleaned = cleaned.replace(/\.git$/, "");

    // Extract the last path segment
    const lastSlash = cleaned.lastIndexOf("/");
    const lastColon = cleaned.lastIndexOf(":");

    // Use whichever separator comes last (handles both HTTPS and SSH URLs)
    const separatorIndex = Math.max(lastSlash, lastColon);

    if (separatorIndex >= 0 && separatorIndex < cleaned.length - 1) {
      return cleaned.substring(separatorIndex + 1);
    }

    // Fallback: return the whole cleaned string
    return cleaned;
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  /**
   * Clone a git repository into the remote session environment.
   *
   * Clones a repository from the given URL into the remote session. When a
   * branch is specified, `--single-branch` is automatically added to reduce
   * data transfer. The target directory is derived from the URL if not
   * explicitly provided via `opts.path`. Currently supports public
   * repositories only; authentication support will be added in a future phase.
   *
   * @param url - The repository URL to clone (HTTPS or SSH)
   * @param opts - Optional clone settings (path, branch, depth, timeoutMs)
   * @returns Promise resolving to {@link GitCloneResult} with the cloned repository path
   *
   * @throws {GitNotFoundError} When git is not installed on the remote environment
   * @throws {GitAuthError} When authentication fails (e.g., private repo without credentials)
   * @throws {GitError} When the clone operation fails for other reasons
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const cloneResult = await result.session.git.clone('https://github.com/user/repo.git');
   *   console.log('Cloned to:', cloneResult.path);
   *   await result.session.delete();
   * }
   * ```
   */
  async clone(url: string, opts?: GitCloneOpts): Promise<GitCloneResult> {
    await this.ensureGitAvailable();

    const args: string[] = ["clone"];

    // When a branch is specified, add --single-branch to only fetch that branch
    // (reduces data transfer, inspired by E2B's approach)
    if (opts?.branch) {
      args.push("--branch", opts.branch, "--single-branch");
    }

    if (opts?.depth) {
      args.push("--depth", String(opts.depth));
    }

    args.push(url);

    const targetPath = opts?.path || this.deriveRepoDirFromUrl(url);
    args.push(targetPath);

    const result = await this.runGit(args, undefined, {
      timeoutMs: opts?.timeoutMs ?? DEFAULT_CLONE_TIMEOUT_MS,
    });

    if (!result.success) {
      throw this.classifyError("clone", result);
    }

    return { path: targetPath };
  }

  /**
   * Initialize a new git repository in the remote session environment.
   *
   * Creates an empty git repository at the specified path. Optionally sets the
   * initial branch name (requires git >= 2.28) and supports creating bare
   * repositories for server-side use.
   *
   * @param path - The directory path to initialize as a git repository
   * @param opts - Optional init settings (initialBranch, bare, timeoutMs)
   * @returns Promise resolving to {@link GitInitResult} with the initialized repository path
   *
   * @throws {GitNotFoundError} When git is not installed on the remote environment
   * @throws {GitError} When the init operation fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const initResult = await result.session.git.init('/home/user/my-project');
   *   console.log('Initialized at:', initResult.path);
   *   await result.session.delete();
   * }
   * ```
   */
  async init(path: string, opts?: GitInitOpts): Promise<GitInitResult> {
    await this.ensureGitAvailable();

    const args: string[] = ["init"];

    if (opts?.initialBranch) {
      args.push("--initial-branch", opts.initialBranch);
    }

    if (opts?.bare) {
      args.push("--bare");
    }

    args.push(path);

    const result = await this.runGit(args, undefined, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("init", result);
    }

    return { path };
  }

  /**
   * Add files to the git staging area.
   *
   * By default (when no files are specified and `all` is not explicitly false),
   * stages all changes using `git add -A`. Specific files can be staged by
   * providing them in `opts.files`. A `--` separator is automatically inserted
   * before file paths to prevent them from being interpreted as options.
   *
   * @param repoPath - The repository path
   * @param opts - Optional add settings (files, all, timeoutMs)
   *
   * @throws {GitNotFoundError} When git is not installed
   * @throws {GitNotARepoError} When the path is not a git repository
   * @throws {GitError} When the add operation fails
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.add('/home/user/my-project');
   *   await result.session.delete();
   * }
   * ```
   */
  async add(repoPath: string, opts?: GitAddOpts): Promise<void> {
    await this.ensureGitAvailable();

    const args: string[] = ["add"];

    if (opts?.files && opts.files.length > 0) {
      // Use -- separator to prevent filenames from being interpreted as options
      args.push("--", ...opts.files);
    } else if (opts?.all !== false) {
      // Default: stage all changes
      args.push("-A");
    } else {
      // all=false: stage current directory only
      args.push(".");
    }

    const result = await this.runGit(args, repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("add", result);
    }
  }

  /**
   * Create a git commit with the staged changes.
   *
   * Author information can be provided via `authorName` and `authorEmail`,
   * which are applied as temporary `-c` configuration (not persisted to git config).
   *
   * @param repoPath - The repository path
   * @param message - The commit message
   * @param opts - Optional commit settings
   * @returns Promise resolving to GitCommitResult with the commit hash
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const commitResult = await result.session.git.commit('/home/user/my-project', 'Initial commit');
   *   console.log('Commit hash:', commitResult.commitHash);
   *   await result.session.delete();
   * }
   * ```
   */
  async commit(
    repoPath: string,
    message: string,
    opts?: GitCommitOpts
  ): Promise<GitCommitResult> {
    await this.ensureGitAvailable();

    // -c parameters must come BEFORE the 'commit' subcommand (git requirement)
    const args: string[] = [];

    if (opts?.authorName) {
      args.push("-c", `user.name=${opts.authorName}`);
    }
    if (opts?.authorEmail) {
      args.push("-c", `user.email=${opts.authorEmail}`);
    }

    args.push("commit", "-m", message);

    if (opts?.allowEmpty) {
      args.push("--allow-empty");
    }

    const result = await this.runGit(args, repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("commit", result);
    }

    // Try to parse commit hash from stdout or stderr (git outputs commit info to stderr)
    // Normal:      "[main abc1234] Initial commit"
    // Root commit: "[main (root-commit) abc1234] Initial commit"
    const commitOutput = result.stdout || result.output || "";
    const hashMatch = commitOutput.match(
      /\[[\w/.-]+(?:\s+\([^)]+\))?\s+([a-f0-9]+)\]/
    );
    return { commitHash: hashMatch?.[1] };
  }

  /**
   * Get the status of the working tree and staging area.
   *
   * Returns a structured result parsed from `git status --porcelain=1 -b`.
   *
   * @param repoPath - The repository path
   * @param opts - Optional status settings
   * @returns Promise resolving to GitStatusResult with branch info and file statuses
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const status = await result.session.git.status('/home/user/my-project');
   *   console.log('Branch:', status.branch);
   *   console.log('Clean:', status.isClean);
   *   await result.session.delete();
   * }
   * ```
   */
  async status(
    repoPath: string,
    opts?: GitStatusOpts
  ): Promise<GitStatusResult> {
    await this.ensureGitAvailable();

    const result = await this.runGit(
      ["status", "--porcelain=1", "-b"],
      repoPath,
      { timeoutMs: opts?.timeoutMs }
    );

    if (!result.success) {
      throw this.classifyError("status", result);
    }

    return this.parseGitStatus(result.stdout || result.output || "");
  }

  /**
   * Get the commit history of the repository.
   *
   * Returns a structured result with parsed commit entries.
   *
   * @param repoPath - The repository path
   * @param opts - Optional log settings
   * @returns Promise resolving to GitLogResult with commit entries
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const log = await result.session.git.log('/home/user/my-project');
   *   console.log('Total commits:', log.entries.length);
   *   await result.session.delete();
   * }
   * ```
   */
  async log(repoPath: string, opts?: GitLogOpts): Promise<GitLogResult> {
    await this.ensureGitAvailable();

    // Use special delimiters: %x01 between fields, %x00 between records
    const format = "%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00";
    const args: string[] = ["log", `--format=${format}`];

    if (opts?.maxCount) {
      args.push("--max-count", String(opts.maxCount));
    }

    const result = await this.runGit(args, repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("log", result);
    }

    return this.parseGitLog(result.stdout || result.output || "");
  }

  /**
   * List all local branches in the repository.
   *
   * @param repoPath - The repository path
   * @param opts - Optional settings
   * @returns Promise resolving to GitBranchListResult with branch info
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const branches = await result.session.git.listBranches('/home/user/my-project');
   *   console.log('Current branch:', branches.current);
   *   await result.session.delete();
   * }
   * ```
   */
  async listBranches(
    repoPath: string,
    opts?: GitBranchListOpts
  ): Promise<GitBranchListResult> {
    await this.ensureGitAvailable();

    // Use custom format: branch_name<TAB>HEAD_marker
    // %(HEAD) outputs '*' for current branch, ' ' for others
    const result = await this.runGit(
      ["branch", "--format=%(refname:short)\t%(HEAD)"],
      repoPath,
      { timeoutMs: opts?.timeoutMs }
    );

    if (!result.success) {
      throw this.classifyError("listBranches", result);
    }

    return this.parseGitBranches(result.stdout || result.output || "");
  }

  /**
   * Create a new branch in the repository.
   *
   * By default, also checks out the new branch (using `git checkout -b`).
   * Set `opts.checkout = false` to create without switching (using `git branch`).
   *
   * @param repoPath - The repository path
   * @param branch - The name of the new branch
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors (e.g., branch already exists)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.createBranch('/home/user/my-project', 'feature/new-feature');
   *   await result.session.delete();
   * }
   * ```
   */
  async createBranch(
    repoPath: string,
    branch: string,
    opts?: GitBranchCreateOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    let args: string[];

    if (opts?.checkout === false) {
      // Create branch without switching
      args = ["branch", branch];
    } else {
      // Default: create and switch to the new branch
      args = ["checkout", "-b", branch];
    }

    const result = await this.runGit(args, repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("createBranch", result);
    }
  }

  /**
   * Switch to an existing branch.
   *
   * @param repoPath - The repository path
   * @param branch - The branch name to switch to
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors (e.g., branch does not exist)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.checkoutBranch('/home/user/my-project', 'main');
   *   await result.session.delete();
   * }
   * ```
   */
  async checkoutBranch(
    repoPath: string,
    branch: string,
    opts?: GitCheckoutOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    const result = await this.runGit(["checkout", branch], repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("checkoutBranch", result);
    }
  }

  // ---------------------------------------------------------------------------
  // Remote operations
  // ---------------------------------------------------------------------------

  /**
   * Add a remote repository.
   *
   * @param repoPath - The repository path
   * @param name - The remote name (e.g., "origin")
   * @param url - The remote URL
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.remoteAdd('/home/user/my-project', 'origin', 'https://github.com/user/repo.git');
   *   await result.session.delete();
   * }
   * ```
   */
  async remoteAdd(
    repoPath: string,
    name: string,
    url: string,
    opts?: GitRemoteAddOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    const { fetch, overwrite, timeoutMs } = opts ?? {};
    const addArgs: string[] = ["remote", "add"];
    if (fetch) addArgs.push("-f");
    addArgs.push(name, url);

    if (!overwrite) {
      // Simple mode: direct git remote add
      const result = await this.runGit(addArgs, repoPath, { timeoutMs });
      if (!result.success) {
        throw this.classifyError("remoteAdd", result);
      }
    } else {
      // Idempotent mode: add fails, fallback to set-url
      const addCmd = this.buildGitCommand(addArgs, repoPath);
      const setUrlCmd = this.buildGitCommand(
        ["remote", "set-url", name, url],
        repoPath
      );
      let cmd = `${addCmd} || ${setUrlCmd}`;
      if (fetch) {
        const fetchCmd = this.buildGitCommand(["fetch", name], repoPath);
        cmd = `(${cmd}) && ${fetchCmd}`;
      }
      const result = await this.runShell(cmd, { timeoutMs });
      if (!result.success) {
        throw this.classifyError("remoteAdd", result);
      }
    }
  }

  /**
   * Get the URL of a remote repository.
   *
   * @param repoPath - The repository path
   * @param name - The remote name (e.g., "origin")
   * @param opts - Optional settings
   * @returns The remote URL, or undefined if the remote does not exist
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const url = await result.session.git.remoteGet('/home/user/my-project', 'origin');
   *   console.log('Remote URL:', url);
   *   await result.session.delete();
   * }
   * ```
   */
  async remoteGet(
    repoPath: string,
    name: string,
    opts?: { timeoutMs?: number }
  ): Promise<string | undefined> {
    await this.ensureGitAvailable();

    const result = await this.runGit(["remote", "get-url", name], repoPath, {
      timeoutMs: opts?.timeoutMs,
    });
    if (!result.success) {
      const stderr = (result.stderr || "").toLowerCase();
      if (stderr.includes("no such remote")) {
        return undefined;
      }
      throw this.classifyError("remote get", result);
    }
    const trimmed = (result.stdout || "").trim();
    return trimmed.length > 0 ? trimmed : undefined;
  }

  // ---------------------------------------------------------------------------
  // Reset operations
  // ---------------------------------------------------------------------------

  /**
   * Reset the repository to a specific state.
   *
   * @param repoPath - The repository path
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.reset('/home/user/my-project');
   *   await result.session.delete();
   * }
   * ```
   */
  async reset(repoPath: string, opts?: GitResetOpts): Promise<void> {
    await this.ensureGitAvailable();

    const { mode, target, paths, timeoutMs } = opts ?? {};
    const args: string[] = ["reset"];
    if (mode) args.push(`--${mode}`);
    if (target) args.push(target);
    if (paths && paths.length > 0) args.push("--", ...paths);

    const result = await this.runGit(args, repoPath, { timeoutMs });
    if (!result.success) {
      throw this.classifyError("reset", result);
    }
  }

  // ---------------------------------------------------------------------------
  // Restore operations
  // ---------------------------------------------------------------------------

  /**
   * Restore files from the index or working tree.
   *
   * @param repoPath - The repository path
   * @param opts - Restore options including paths (required)
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.restore('/home/user/my-project', { paths: ['src/index.ts'] });
   *   await result.session.delete();
   * }
   * ```
   */
  async restore(repoPath: string, opts: GitRestoreOpts): Promise<void> {
    await this.ensureGitAvailable();

    const { paths, staged, worktree, source, timeoutMs } = opts;
    const resolvedStaged = staged ?? false;
    const resolvedWorktree = worktree ?? !resolvedStaged;

    const args: string[] = ["restore"];
    if (resolvedWorktree) args.push("--worktree");
    if (resolvedStaged) args.push("--staged");
    if (source) args.push("--source", source);
    args.push("--", ...paths);

    const result = await this.runGit(args, repoPath, { timeoutMs });
    if (!result.success) {
      throw this.classifyError("restore", result);
    }
  }

  // ---------------------------------------------------------------------------
  // Pull operations
  // ---------------------------------------------------------------------------

  /**
   * Pull changes from a remote repository.
   *
   * @param repoPath - The repository path
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors (e.g., no upstream configured)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.pull('/home/user/my-project');
   *   await result.session.delete();
   * }
   * ```
   */
  async pull(repoPath: string, opts?: GitPullOpts): Promise<void> {
    await this.ensureGitAvailable();

    const { remote, branch, timeoutMs } = opts ?? {};
    const args: string[] = ["pull"];
    if (remote) args.push(remote);
    if (branch) args.push(branch);

    const result = await this.runGit(args, repoPath, {
      timeoutMs: timeoutMs ?? DEFAULT_PULL_TIMEOUT_MS,
    });
    if (!result.success) {
      throw this.classifyError("pull", result);
    }
  }

  // ---------------------------------------------------------------------------
  // Config operations
  // ---------------------------------------------------------------------------

  /**
   * Configure git user information.
   *
   * @param repoPath - The repository path
   * @param name - The user name
   * @param email - The user email
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.configureUser('/home/user/my-project', 'Agent', 'agent@example.com');
   *   await result.session.delete();
   * }
   * ```
   */
  async configureUser(
    repoPath: string,
    name: string,
    email: string,
    opts?: GitConfigOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    const { scope, timeoutMs } = opts ?? {};
    // Default scope is global (matches E2B behavior)
    const scopeFlag = scope === "local" ? "--local" : "--global";
    const baseArgs = ["config", scopeFlag];

    const nameResult = await this.runGit(
      [...baseArgs, "user.name", name],
      repoPath,
      { timeoutMs }
    );
    if (!nameResult.success) {
      throw this.classifyError("configureUser", nameResult);
    }
    const emailResult = await this.runGit(
      [...baseArgs, "user.email", email],
      repoPath,
      { timeoutMs }
    );
    if (!emailResult.success) {
      throw this.classifyError("configureUser", emailResult);
    }
  }

  /**
   * Set a git configuration value.
   *
   * @param repoPath - The repository path
   * @param key - The configuration key
   * @param value - The configuration value
   * @param opts - Optional settings
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.setConfig('/home/user/my-project', 'pull.rebase', 'true');
   *   await result.session.delete();
   * }
   * ```
   */
  async setConfig(
    repoPath: string,
    key: string,
    value: string,
    opts?: GitConfigOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    const { scope, timeoutMs } = opts ?? {};
    const args: string[] = ["config"];
    // Default scope is global (matches E2B behavior)
    args.push(scope === "local" ? "--local" : "--global");
    args.push(key, value);

    const result = await this.runGit(args, repoPath, { timeoutMs });
    if (!result.success) {
      throw this.classifyError("setConfig", result);
    }
  }

  /**
   * Get a git configuration value.
   *
   * @param repoPath - The repository path
   * @param key - The configuration key
   * @param opts - Optional settings
   * @returns The configuration value, or undefined if not found
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   const name = await result.session.git.getConfig('/home/user/my-project', 'user.name');
   *   console.log('User name:', name);
   *   await result.session.delete();
   * }
   * ```
   */
  async getConfig(
    repoPath: string,
    key: string,
    opts?: GitConfigOpts
  ): Promise<string | undefined> {
    await this.ensureGitAvailable();

    const { scope, timeoutMs } = opts ?? {};
    const args: string[] = ["config"];
    // Default scope is global (matches E2B behavior)
    args.push(scope === "local" ? "--local" : "--global");
    args.push("--get", key);

    const result = await this.runGit(args, repoPath, { timeoutMs });
    if (!result.success) {
      const rawStderr = (result.stderr || "").trim().toLowerCase();
      // exit code 1 with empty/missing stderr means key does not exist
      if (
        result.exitCode === 1 &&
        (rawStderr.length === 0 || rawStderr.includes("key does not contain"))
      ) {
        return undefined;
      }
      throw this.classifyError("get config", result);
    }
    const trimmed = (result.stdout || "").trim();
    return trimmed.length > 0 ? trimmed : undefined;
  }

  /**
   * Delete a local branch.
   *
   * @param repoPath - The repository path
   * @param branch - The branch name to delete
   * @param opts - Optional settings. Use `force: true` for `-D` (force delete)
   *
   * @throws GitNotFoundError if git is not installed
   * @throws GitNotARepoError if the path is not a git repository
   * @throws GitError for other git errors (e.g., branch not fully merged)
   *
   * @example
   * ```typescript
   * const agentBay = new AgentBay({ apiKey: process.env.AGENTBAY_API_KEY });
   * const result = await agentBay.create();
   * if (result.success) {
   *   await result.session.git.deleteBranch('/home/user/my-project', 'feature/old');
   *   await result.session.delete();
   * }
   * ```
   */
  async deleteBranch(
    repoPath: string,
    branch: string,
    opts?: GitBranchDeleteOpts
  ): Promise<void> {
    await this.ensureGitAvailable();

    const deleteFlag = opts?.force ? "-D" : "-d";
    const result = await this.runGit(["branch", deleteFlag, branch], repoPath, {
      timeoutMs: opts?.timeoutMs,
    });

    if (!result.success) {
      throw this.classifyError("deleteBranch", result);
    }
  }

  // ---------------------------------------------------------------------------
  // Output parsers
  // ---------------------------------------------------------------------------

  /**
   * Derive a human-readable status string from porcelain status characters.
   *
   * @param indexStatus - The index status character (first character in porcelain output)
   * @param workTreeStatus - The worktree status character (second character in porcelain output)
   * @returns A human-readable status string
   */
  private deriveStatus(indexStatus: string, workTreeStatus: string): string {
    const combined = indexStatus + workTreeStatus;

    if (combined.includes("U")) {
      return "conflict";
    }
    if (combined.includes("R")) {
      return "renamed";
    }
    if (combined.includes("C")) {
      return "copied";
    }
    if (combined.includes("D")) {
      return "deleted";
    }
    if (combined.includes("A")) {
      return "added";
    }
    if (combined.includes("M")) {
      return "modified";
    }
    if (combined.includes("T")) {
      return "typechange";
    }
    if (combined.includes("?")) {
      return "untracked";
    }

    return "unknown";
  }

  /**
   * Parse the output of `git status --porcelain=1 -b` into a structured result.
   *
   * Format:
   * - First line: `## branch_name` or `## branch_name...remote/branch_name`
   * - Subsequent lines: `XY path` where X=index status, Y=worktree status
   *
   * @param output - Raw stdout from git status
   * @returns Parsed GitStatusResult
   */
  private parseGitStatus(output: string): GitStatusResult {
    const lines = output.split("\n").filter((l) => l.length > 0);
    let currentBranch: string | undefined;
    let upstream: string | undefined;
    let ahead = 0;
    let behind = 0;
    let detached = false;
    const files: GitFileStatus[] = [];

    for (const line of lines) {
      if (line.startsWith("## ")) {
        // Branch line: "## main...origin/main [ahead 1, behind 2]" or similar
        const branchInfo = line.substring(3);

        // Handle "No commits yet on <branch>" format
        const noCommitsMatch = branchInfo.match(/No commits yet on (.+)/);
        if (noCommitsMatch) {
          currentBranch = noCommitsMatch[1].split("...")[0];
        } else {
          // Parse ahead/behind info
          const aheadStart = branchInfo.indexOf(" [");
          const branchPart =
            aheadStart === -1
              ? branchInfo
              : branchInfo.substring(0, aheadStart);

          // Extract branch and upstream
          const parts = branchPart.split("...");
          currentBranch = parts[0];
          upstream = parts[1];

          // Parse ahead/behind from [ahead N, behind M] format
          if (aheadStart !== -1) {
            const aheadPart = branchInfo.substring(
              aheadStart + 2,
              branchInfo.length - 1
            );
            const aheadMatch = aheadPart.match(/ahead (\d+)/);
            const behindMatch = aheadPart.match(/behind (\d+)/);

            if (aheadMatch) {
              ahead = parseInt(aheadMatch[1], 10);
            }
            if (behindMatch) {
              behind = parseInt(behindMatch[1], 10);
            }
          }

          // Detect detached HEAD
          if (
            currentBranch.includes("HEAD (detached") ||
            currentBranch === "HEAD (no branch)"
          ) {
            detached = true;
          }
        }
      } else if (line.length >= 3) {
        const indexStatus = line[0];
        const workTreeStatus = line[1];
        const path = line.substring(3);

        // Handle renamed files (path contains " -> ")
        let renamedFrom: string | undefined;
        let actualPath = path;
        const renameMatch = path.match(/^(.+?) -> (.+)$/);
        if (renameMatch) {
          renamedFrom = renameMatch[1];
          actualPath = renameMatch[2];
        }

        // Determine if staged (index status is not space and not '?')
        const staged = indexStatus !== " " && indexStatus !== "?";

        files.push({
          path: actualPath,
          indexStatus,
          workTreeStatus,
          status: this.deriveStatus(indexStatus, workTreeStatus),
          staged,
          renamedFrom,
        });
      }
    }

    // Calculate statistics
    const totalCount = files.length;
    const stagedCount = files.filter((f) => f.staged).length;
    const untrackedCount = files.filter((f) => f.status === "untracked").length;
    const conflictCount = files.filter((f) => f.status === "conflict").length;
    const unstagedCount = files.filter(
      (f) => !f.staged && f.status !== "untracked"
    ).length;
    const hasChanges = totalCount > 0;
    const hasStaged = stagedCount > 0;
    const hasUntracked = untrackedCount > 0;
    const hasConflicts = conflictCount > 0;
    const isClean = !hasChanges;

    return {
      currentBranch,
      upstream,
      ahead,
      behind,
      detached,
      files,
      isClean,
      hasChanges,
      hasStaged,
      hasUntracked,
      hasConflicts,
      totalCount,
      stagedCount,
      unstagedCount,
      untrackedCount,
      conflictCount,
    };
  }

  /**
   * Parse the output of `git log --format=...` into a structured result.
   *
   * Uses %x00 (NUL) as record separator and %x01 (SOH) as field separator
   * to avoid conflicts with commit messages containing newlines or special chars.
   *
   * @param output - Raw stdout from git log
   * @returns Parsed GitLogResult
   */
  private parseGitLog(output: string): GitLogResult {
    const entries: GitLogEntry[] = [];
    const records = output.split("\x00").filter((r) => r.trim().length > 0);

    for (const record of records) {
      const parts = record.split("\x01");
      if (parts.length >= 6) {
        entries.push({
          hash: parts[0].trim(),
          shortHash: parts[1],
          authorName: parts[2],
          authorEmail: parts[3],
          date: parts[4],
          message: parts[5].trim(),
        });
      }
    }

    return { entries };
  }

  /**
   * Parse the output of `git branch --format=%(refname:short)\t%(HEAD)`.
   *
   * Each line is: `branch_name\t*` (current) or `branch_name\t ` (other).
   *
   * @param output - Raw stdout from git branch
   * @returns Parsed GitBranchListResult
   */
  private parseGitBranches(output: string): GitBranchListResult {
    const lines = output.split("\n").filter((l) => l.length > 0);
    const branches: GitBranchInfo[] = [];
    let current = "";

    for (const line of lines) {
      const parts = line.split("\t");
      const name = parts[0].trim();

      // Skip detached HEAD state (matches E2B behavior)
      if (name.startsWith("(HEAD detached")) {
        continue;
      }

      const isCurrent = parts[1]?.trim() === "*";

      if (name) {
        branches.push({ name, isCurrent });
        if (isCurrent) {
          current = name;
        }
      }
    }

    return { branches, current };
  }
}
