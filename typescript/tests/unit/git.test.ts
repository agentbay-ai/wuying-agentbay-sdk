import { Git } from "../../src/git/git";
import {
  GitError,
  GitAuthError,
  GitNotFoundError,
  GitConflictError,
  GitNotARepoError,
} from "../../src/git/errors";
import { CommandResult } from "../../src/types/api-response";

// ---------------------------------------------------------------------------
// Mock Session with a mock Command module
// ---------------------------------------------------------------------------

function createMockSession() {
  const executeCommandMock = jest.fn<Promise<CommandResult>, any[]>();
  const session = {
    command: {
      executeCommand: executeCommandMock,
    },
  } as any;
  return { session, executeCommandMock };
}

function successResult(overrides: Partial<CommandResult> = {}): CommandResult {
  return {
    requestId: "req-1",
    success: true,
    output: "",
    exitCode: 0,
    stdout: "",
    stderr: "",
    errorMessage: "",
    ...overrides,
  };
}

function failureResult(overrides: Partial<CommandResult> = {}): CommandResult {
  return {
    requestId: "req-1",
    success: false,
    output: "",
    exitCode: 1,
    stdout: "",
    stderr: "",
    errorMessage: "",
    ...overrides,
  };
}

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------

describe("Git module", () => {
  // -------------------------------------------------------------------------
  // shellEscape (tested indirectly through command construction)
  // -------------------------------------------------------------------------
  describe("shellEscape (via clone command construction)", () => {
    it("should escape normal strings with single quotes", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      // First call: ensureGitAvailable (git --version)
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      // Second call: clone
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      // Verify the clone command was constructed with shell-escaped arguments
      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe("git 'clone' 'https://github.com/user/repo.git' 'repo'");
    });

    it("should escape strings containing single quotes", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      // Path with a single quote
      await git.clone("https://github.com/user/repo.git", {
        path: "/home/user/it's-a-test",
      });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toContain("'/home/user/it'\\''s-a-test'");
    });

    it("should fallback to derived path when path is empty string", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      // Empty string is falsy in JS, so it falls back to deriveRepoDirFromUrl
      await git.clone("https://github.com/user/repo.git", { path: "" });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe("git 'clone' 'https://github.com/user/repo.git' 'repo'");
    });
  });

  // -------------------------------------------------------------------------
  // ensureGitAvailable
  // -------------------------------------------------------------------------
  describe("ensureGitAvailable", () => {
    it("should pass when git is available", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      // Should not throw
      await git.clone("https://github.com/user/repo.git");

      // First call should be git --version
      const versionCall = executeCommandMock.mock.calls[0];
      const cmd = versionCall[0] as string;
      expect(cmd).toBe("git '--version'");
    });

    it("should throw GitNotFoundError when git is not available", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 127,
          stderr: "bash: git: command not found",
          errorMessage: "bash: git: command not found",
        })
      );

      await expect(
        git.clone("https://github.com/user/repo.git")
      ).rejects.toThrow(GitNotFoundError);
    });

    it("should cache git availability after first successful check", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      // First clone: git --version + clone
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      // Second clone: should NOT call git --version again
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/another-repo.git");

      // Total calls: git --version (1) + clone (1) + clone (1) = 3
      expect(executeCommandMock).toHaveBeenCalledTimes(3);

      // Verify the third call is a clone, not git --version
      const thirdCall = executeCommandMock.mock.calls[2];
      const cmd = thirdCall[0] as string;
      expect(cmd).toContain("'clone'");
      expect(cmd).not.toContain("'--version'");
    });
  });

  // -------------------------------------------------------------------------
  // clone command construction
  // -------------------------------------------------------------------------
  describe("clone command construction", () => {
    let session: any;
    let executeCommandMock: jest.Mock;
    let git: Git;

    beforeEach(() => {
      const mock = createMockSession();
      session = mock.session;
      executeCommandMock = mock.executeCommandMock;
      git = new Git(session);

      // Always succeed git --version
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
    });

    it("should construct basic clone command", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe("git 'clone' 'https://github.com/user/repo.git' 'repo'");
    });

    it("should add --branch and --single-branch when branch is specified", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git", {
        branch: "develop",
      });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe(
        "git 'clone' '--branch' 'develop' '--single-branch' 'https://github.com/user/repo.git' 'repo'"
      );
    });

    it("should add --depth when depth is specified", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git", { depth: 1 });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe(
        "git 'clone' '--depth' '1' 'https://github.com/user/repo.git' 'repo'"
      );
    });

    it("should use custom path when specified", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git", {
        path: "/home/user/my-project",
      });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe(
        "git 'clone' 'https://github.com/user/repo.git' '/home/user/my-project'"
      );
    });

    it("should combine branch, depth, and path options", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git", {
        branch: "main",
        depth: 5,
        path: "/tmp/repo",
      });

      const cloneCall = executeCommandMock.mock.calls[1];
      const cmd = cloneCall[0] as string;
      expect(cmd).toBe(
        "git 'clone' '--branch' 'main' '--single-branch' '--depth' '5' 'https://github.com/user/repo.git' '/tmp/repo'"
      );
    });

    it("should use custom timeout when specified", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git", {
        timeoutMs: 60000,
      });

      const cloneCall = executeCommandMock.mock.calls[1];
      const timeoutArg = cloneCall[1] as number;
      expect(timeoutArg).toBe(60000);
    });

    it("should use default clone timeout (300000ms) when not specified", async () => {
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      const cloneCall = executeCommandMock.mock.calls[1];
      const timeoutArg = cloneCall[1] as number;
      expect(timeoutArg).toBe(300000);
    });
  });

  // -------------------------------------------------------------------------
  // deriveRepoDirFromUrl (tested via clone)
  // -------------------------------------------------------------------------
  describe("deriveRepoDirFromUrl (via clone)", () => {
    let session: any;
    let executeCommandMock: jest.Mock;
    let git: Git;

    beforeEach(() => {
      const mock = createMockSession();
      session = mock.session;
      executeCommandMock = mock.executeCommandMock;
      git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
    });

    const testCases = [
      {
        url: "https://github.com/user/repo.git",
        expected: "repo",
        desc: "HTTPS URL with .git suffix",
      },
      {
        url: "https://github.com/user/repo",
        expected: "repo",
        desc: "HTTPS URL without .git suffix",
      },
      {
        url: "https://github.com/user/repo/",
        expected: "repo",
        desc: "HTTPS URL with trailing slash",
      },
      {
        url: "https://github.com/user/repo.git/",
        expected: "repo",
        desc: "HTTPS URL with .git and trailing slash",
      },
      {
        url: "git@github.com:user/repo.git",
        expected: "repo",
        desc: "SSH URL with .git suffix",
      },
      {
        url: "git@github.com:user/repo",
        expected: "repo",
        desc: "SSH URL without .git suffix",
      },
      {
        url: "https://github.com/user/my-awesome-project.git",
        expected: "my-awesome-project",
        desc: "URL with hyphens in repo name",
      },
    ];

    for (const tc of testCases) {
      it(`should derive "${tc.expected}" from ${tc.desc}`, async () => {
        executeCommandMock.mockResolvedValueOnce(successResult());

        const result = await git.clone(tc.url);

        expect(result.path).toBe(tc.expected);

        // Verify the derived path is used in the command
        const cloneCall = executeCommandMock.mock.calls[1];
        const cmd = cloneCall[0] as string;
        expect(cmd).toContain(`'${tc.expected}'`);
      });
    }
  });

  // -------------------------------------------------------------------------
  // GIT_TERMINAL_PROMPT environment variable
  // -------------------------------------------------------------------------
  describe("GIT_TERMINAL_PROMPT environment variable", () => {
    it("should pass GIT_TERMINAL_PROMPT=0 for git --version", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      // Check git --version call
      const versionCall = executeCommandMock.mock.calls[0];
      const envs = versionCall[3] as Record<string, string>;
      expect(envs).toEqual({ GIT_TERMINAL_PROMPT: "0", LC_ALL: "C" });
    });

    it("should pass GIT_TERMINAL_PROMPT=0 for clone command", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.clone("https://github.com/user/repo.git");

      // Check clone call
      const cloneCall = executeCommandMock.mock.calls[1];
      const envs = cloneCall[3] as Record<string, string>;
      expect(envs).toEqual({ GIT_TERMINAL_PROMPT: "0", LC_ALL: "C" });
    });
  });

  // -------------------------------------------------------------------------
  // Error classification
  // -------------------------------------------------------------------------
  describe("error classification", () => {
    let session: any;
    let executeCommandMock: jest.Mock;
    let git: Git;

    beforeEach(() => {
      const mock = createMockSession();
      session = mock.session;
      executeCommandMock = mock.executeCommandMock;
      git = new Git(session);

      // Always succeed git --version
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
    });

    it("should throw GitAuthError for authentication failures", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: Authentication failed for 'https://github.com/user/private-repo.git'",
        })
      );

      await expect(
        git.clone("https://github.com/user/private-repo.git")
      ).rejects.toThrow(GitAuthError);
    });

    it("should throw GitAuthError for 'could not read username'", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: could not read Username for 'https://github.com': terminal prompts disabled",
        })
      );

      await expect(
        git.clone("https://github.com/user/private-repo.git")
      ).rejects.toThrow(GitAuthError);
    });

    it("should throw GitNotARepoError for 'not a git repository'", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: 'https://example.com/not-a-repo' does not appear to be a git repository",
        })
      );

      await expect(git.clone("https://example.com/not-a-repo")).rejects.toThrow(
        GitNotARepoError
      );
    });

    it("should throw GitNotFoundError for 'command not found'", async () => {
      // Reset git availability cache by creating a new Git instance
      const { session: newSession, executeCommandMock: newMock } =
        createMockSession();
      const newGit = new Git(newSession);

      // git --version succeeds
      newMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      // clone fails with command not found (unlikely but tests the classifier)
      newMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 127,
          stderr: "bash: git: command not found",
        })
      );

      await expect(
        newGit.clone("https://github.com/user/repo.git")
      ).rejects.toThrow(GitNotFoundError);
    });

    it("should throw GitConflictError for merge conflicts", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 1,
          stderr: "CONFLICT (content): Merge conflict in file.txt",
        })
      );

      await expect(
        git.clone("https://github.com/user/repo.git")
      ).rejects.toThrow(GitConflictError);
    });

    it("should throw generic GitError for unknown errors", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 1,
          stderr: "fatal: some unknown error occurred",
        })
      );

      const error = await git
        .clone("https://github.com/user/repo.git")
        .catch((e) => e);

      expect(error).toBeInstanceOf(GitError);
      // Should NOT be a more specific subclass
      expect(error).not.toBeInstanceOf(GitAuthError);
      expect(error).not.toBeInstanceOf(GitNotFoundError);
      expect(error).not.toBeInstanceOf(GitConflictError);
      expect(error).not.toBeInstanceOf(GitNotARepoError);
    });

    it("should include exit code and stderr in error", async () => {
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: Authentication failed for 'https://github.com/user/repo.git'",
        })
      );

      try {
        await git.clone("https://github.com/user/repo.git");
        fail("Expected GitAuthError to be thrown");
      } catch (error) {
        expect(error).toBeInstanceOf(GitAuthError);
        const gitError = error as GitAuthError;
        expect(gitError.exitCode).toBe(128);
        expect(gitError.stderr).toContain("Authentication failed");
      }
    });
  });

  // -------------------------------------------------------------------------
  // clone return value
  // -------------------------------------------------------------------------
  describe("clone return value", () => {
    it("should return GitCloneResult with derived path", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      const result = await git.clone("https://github.com/user/repo.git");

      expect(result).toEqual({ path: "repo" });
    });

    it("should return GitCloneResult with custom path", async () => {
      const { session, executeCommandMock } = createMockSession();
      const git = new Git(session);

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "git version 2.39.0" })
      );
      executeCommandMock.mockResolvedValueOnce(successResult());

      const result = await git.clone("https://github.com/user/repo.git", {
        path: "/home/user/my-project",
      });

      expect(result).toEqual({ path: "/home/user/my-project" });
    });
  });

  // -------------------------------------------------------------------------
  // Error inheritance
  // -------------------------------------------------------------------------
  describe("error inheritance", () => {
    it("GitError should be an instance of Error", () => {
      const error = new GitError("test", 1, "stderr");
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GitError);
    });

    it("GitAuthError should be an instance of GitError", () => {
      const error = new GitAuthError("test", 128, "stderr");
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GitError);
      expect(error).toBeInstanceOf(GitAuthError);
    });

    it("GitNotFoundError should be an instance of GitError", () => {
      const error = new GitNotFoundError("test", 127, "stderr");
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GitError);
      expect(error).toBeInstanceOf(GitNotFoundError);
    });

    it("GitConflictError should be an instance of GitError", () => {
      const error = new GitConflictError("test", 1, "stderr");
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GitError);
      expect(error).toBeInstanceOf(GitConflictError);
    });

    it("GitNotARepoError should be an instance of GitError", () => {
      const error = new GitNotARepoError("test", 128, "stderr");
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(GitError);
      expect(error).toBeInstanceOf(GitNotARepoError);
    });

    it("error properties should be accessible", () => {
      const error = new GitAuthError("auth failed", 128, "fatal: auth error");
      expect(error.message).toBe("auth failed");
      expect(error.exitCode).toBe(128);
      expect(error.stderr).toBe("fatal: auth error");
      expect(error.name).toBe("GitAuthError");
    });
  });

  // =========================================================================
  // Phase 2: init / add / commit / status / log / branch
  // =========================================================================

  // Helper: create a Git instance with git --version already cached
  function createGitWithVersion() {
    const { session, executeCommandMock } = createMockSession();
    const git = new Git(session);
    // Pre-cache git availability
    executeCommandMock.mockResolvedValueOnce(
      successResult({ stdout: "git version 2.39.0" })
    );
    return { git, executeCommandMock };
  }

  // -------------------------------------------------------------------------
  // init
  // -------------------------------------------------------------------------
  describe("init", () => {
    it("should construct basic init command", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.init("/home/user/my-project");

      // calls[0] = git --version, calls[1] = init
      const initCall = executeCommandMock.mock.calls[1];
      const cmd = initCall[0] as string;
      expect(cmd).toBe("git 'init' '/home/user/my-project'");
    });

    it("should add --initial-branch when specified", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.init("/home/user/my-project", { initialBranch: "main" });

      const initCall = executeCommandMock.mock.calls[1];
      const cmd = initCall[0] as string;
      expect(cmd).toBe(
        "git 'init' '--initial-branch' 'main' '/home/user/my-project'"
      );
    });

    it("should add --bare when specified", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.init("/home/user/my-project.git", { bare: true });

      const initCall = executeCommandMock.mock.calls[1];
      const cmd = initCall[0] as string;
      expect(cmd).toBe("git 'init' '--bare' '/home/user/my-project.git'");
    });

    it("should combine initialBranch and bare", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.init("/tmp/repo", { initialBranch: "main", bare: true });

      const initCall = executeCommandMock.mock.calls[1];
      const cmd = initCall[0] as string;
      expect(cmd).toBe(
        "git 'init' '--initial-branch' 'main' '--bare' '/tmp/repo'"
      );
    });

    it("should return GitInitResult with path", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      const result = await git.init("/home/user/my-project");
      expect(result).toEqual({ path: "/home/user/my-project" });
    });
  });

  // -------------------------------------------------------------------------
  // add
  // -------------------------------------------------------------------------
  describe("add", () => {
    it("should default to -A when no files specified", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.add("/home/user/repo");

      const addCall = executeCommandMock.mock.calls[1];
      const cmd = addCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'add' '-A'");
    });

    it("should use -A when all=true explicitly", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.add("/home/user/repo", { all: true });

      const addCall = executeCommandMock.mock.calls[1];
      const cmd = addCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'add' '-A'");
    });

    it("should use . when all=false", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.add("/home/user/repo", { all: false });

      const addCall = executeCommandMock.mock.calls[1];
      const cmd = addCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'add' '.'");
    });

    it("should add specific files with -- separator", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.add("/home/user/repo", {
        files: ["src/index.ts", "README.md"],
      });

      const addCall = executeCommandMock.mock.calls[1];
      const cmd = addCall[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'add' '--' 'src/index.ts' 'README.md'"
      );
    });

    it("should use -A when files is empty array", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.add("/home/user/repo", { files: [] });

      const addCall = executeCommandMock.mock.calls[1];
      const cmd = addCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'add' '-A'");
    });
  });

  // -------------------------------------------------------------------------
  // commit
  // -------------------------------------------------------------------------
  describe("commit", () => {
    it("should construct basic commit command", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "[main abc1234] Initial commit" })
      );

      await git.commit("/home/user/repo", "Initial commit");

      const commitCall = executeCommandMock.mock.calls[1];
      const cmd = commitCall[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'commit' '-m' 'Initial commit'"
      );
    });

    it("should place -c user.name before commit subcommand", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "[main abc1234] test" })
      );

      await git.commit("/home/user/repo", "test", {
        authorName: "Agent",
        authorEmail: "agent@example.com",
      });

      const commitCall = executeCommandMock.mock.calls[1];
      const cmd = commitCall[0] as string;
      // -c params must come BEFORE 'commit'
      expect(cmd).toBe(
        "git -C '/home/user/repo' '-c' 'user.name=Agent' '-c' 'user.email=agent@example.com' 'commit' '-m' 'test'"
      );
    });

    it("should add --allow-empty when specified", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "[main abc1234] empty" })
      );

      await git.commit("/home/user/repo", "empty", { allowEmpty: true });

      const commitCall = executeCommandMock.mock.calls[1];
      const cmd = commitCall[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'commit' '-m' 'empty' '--allow-empty'"
      );
    });

    it("should parse commit hash from stdout", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "[main abc1234] Initial commit\n 1 file changed",
        })
      );

      const result = await git.commit("/home/user/repo", "Initial commit");
      expect(result.commitHash).toBe("abc1234");
    });

    it("should return undefined commitHash when parsing fails", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "some unexpected output" })
      );

      const result = await git.commit("/home/user/repo", "test");
      expect(result.commitHash).toBeUndefined();
    });
  });

  // -------------------------------------------------------------------------
  // status
  // -------------------------------------------------------------------------
  describe("status", () => {
    it("should construct status command with --porcelain=1 -b", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "## main\n" })
      );

      await git.status("/home/user/repo");

      const statusCall = executeCommandMock.mock.calls[1];
      const cmd = statusCall[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'status' '--porcelain=1' '-b'"
      );
    });

    it("should parse branch name from porcelain output", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "## main\n" })
      );

      const result = await git.status("/home/user/repo");
      expect(result.currentBranch).toBe("main");
      expect(result.isClean).toBe(true);
      expect(result.files).toEqual([]);
    });

    it("should parse branch with remote tracking", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "## main...origin/main\n" })
      );

      const result = await git.status("/home/user/repo");
      expect(result.currentBranch).toBe("main");
    });

    it("should parse file statuses", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      const porcelainOutput = [
        "## develop",
        "M  src/index.ts",
        "A  README.md",
        "?? new-file.txt",
        " M modified-unstaged.ts",
      ].join("\n");

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: porcelainOutput })
      );

      const result = await git.status("/home/user/repo");
      expect(result.currentBranch).toBe("develop");
      expect(result.isClean).toBe(false);
      expect(result.files).toHaveLength(4);

      expect(result.files[0]).toEqual({
        path: "src/index.ts",
        indexStatus: "M",
        workTreeStatus: " ",
        status: "modified",
        staged: true,
        renamedFrom: undefined,
      });
      expect(result.files[1]).toEqual({
        path: "README.md",
        indexStatus: "A",
        workTreeStatus: " ",
        status: "added",
        staged: true,
        renamedFrom: undefined,
      });
      expect(result.files[2]).toEqual({
        path: "new-file.txt",
        indexStatus: "?",
        workTreeStatus: "?",
        status: "untracked",
        staged: false,
        renamedFrom: undefined,
      });
      expect(result.files[3]).toEqual({
        path: "modified-unstaged.ts",
        indexStatus: " ",
        workTreeStatus: "M",
        status: "modified",
        staged: false,
        renamedFrom: undefined,
      });
    });

    it("should handle 'No commits yet' branch format", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "## No commits yet on main\nA  file.txt\n" })
      );

      const result = await git.status("/home/user/repo");
      expect(result.currentBranch).toBe("main");
      expect(result.files).toHaveLength(1);
    });

    it("should report isClean=true when no files changed", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "## main\n" })
      );

      const result = await git.status("/home/user/repo");
      expect(result.isClean).toBe(true);
    });
  });

  // -------------------------------------------------------------------------
  // log
  // -------------------------------------------------------------------------
  describe("log", () => {
    it("should construct log command with custom format", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult({ stdout: "" }));

      await git.log("/home/user/repo");

      const logCall = executeCommandMock.mock.calls[1];
      const cmd = logCall[0] as string;
      expect(cmd).toContain("'log'");
      expect(cmd).toContain(
        "'--format=%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00'"
      );
    });

    it("should add --max-count when specified", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult({ stdout: "" }));

      await git.log("/home/user/repo", { maxCount: 5 });

      const logCall = executeCommandMock.mock.calls[1];
      const cmd = logCall[0] as string;
      expect(cmd).toContain("'--max-count' '5'");
    });

    it("should parse log entries", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      const logOutput = [
        "abc123def456abc123def456abc123def456abc123\x01abc123d\x01John Doe\x01john@example.com\x012024-01-15T10:30:00+08:00\x01Initial commit",
        "\x00",
        "def456abc123def456abc123def456abc123def456\x01def456a\x01Jane Smith\x01jane@example.com\x012024-01-14T09:00:00+08:00\x01Add README",
        "\x00",
      ].join("");

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: logOutput })
      );

      const result = await git.log("/home/user/repo");
      expect(result.entries).toHaveLength(2);

      expect(result.entries[0]).toEqual({
        hash: "abc123def456abc123def456abc123def456abc123",
        shortHash: "abc123d",
        authorName: "John Doe",
        authorEmail: "john@example.com",
        date: "2024-01-15T10:30:00+08:00",
        message: "Initial commit",
      });

      expect(result.entries[1]).toEqual({
        hash: "def456abc123def456abc123def456abc123def456",
        shortHash: "def456a",
        authorName: "Jane Smith",
        authorEmail: "jane@example.com",
        date: "2024-01-14T09:00:00+08:00",
        message: "Add README",
      });
    });

    it("should return empty entries for empty output", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult({ stdout: "" }));

      const result = await git.log("/home/user/repo");
      expect(result.entries).toEqual([]);
    });
  });

  // -------------------------------------------------------------------------
  // listBranches
  // -------------------------------------------------------------------------
  describe("listBranches", () => {
    it("should construct branch list command with format", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "main\t*\n" })
      );

      await git.listBranches("/home/user/repo");

      const branchCall = executeCommandMock.mock.calls[1];
      const cmd = branchCall[0] as string;
      expect(cmd).toContain("'branch'");
      expect(cmd).toContain("'--format=%(refname:short)\t%(HEAD)'");
    });

    it("should parse branch list with current branch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      const branchOutput = "main\t*\ndevelop\t \nfeature/test\t \n";

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: branchOutput })
      );

      const result = await git.listBranches("/home/user/repo");
      expect(result.current).toBe("main");
      expect(result.branches).toHaveLength(3);

      expect(result.branches[0]).toEqual({ name: "main", isCurrent: true });
      expect(result.branches[1]).toEqual({ name: "develop", isCurrent: false });
      expect(result.branches[2]).toEqual({
        name: "feature/test",
        isCurrent: false,
      });
    });

    it("should handle single branch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: "main\t*\n" })
      );

      const result = await git.listBranches("/home/user/repo");
      expect(result.current).toBe("main");
      expect(result.branches).toHaveLength(1);
      expect(result.branches[0]).toEqual({ name: "main", isCurrent: true });
    });

    it("should handle empty output", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult({ stdout: "" }));

      const result = await git.listBranches("/home/user/repo");
      expect(result.current).toBe("");
      expect(result.branches).toEqual([]);
    });
  });

  // -------------------------------------------------------------------------
  // createBranch
  // -------------------------------------------------------------------------
  describe("createBranch", () => {
    it("should default to checkout -b (create and switch)", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.createBranch("/home/user/repo", "feature/new");

      const branchCall = executeCommandMock.mock.calls[1];
      const cmd = branchCall[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'checkout' '-b' 'feature/new'"
      );
    });

    it("should use git branch when checkout=false", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.createBranch("/home/user/repo", "feature/new", {
        checkout: false,
      });

      const branchCall = executeCommandMock.mock.calls[1];
      const cmd = branchCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'branch' 'feature/new'");
    });
  });

  // -------------------------------------------------------------------------
  // checkoutBranch
  // -------------------------------------------------------------------------
  describe("checkoutBranch", () => {
    it("should construct checkout command", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.checkoutBranch("/home/user/repo", "develop");

      const checkoutCall = executeCommandMock.mock.calls[1];
      const cmd = checkoutCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'checkout' 'develop'");
    });
  });

  // -------------------------------------------------------------------------
  // deleteBranch
  // -------------------------------------------------------------------------
  describe("deleteBranch", () => {
    it("should use -d for safe delete by default", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.deleteBranch("/home/user/repo", "feature/old");

      const deleteCall = executeCommandMock.mock.calls[1];
      const cmd = deleteCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'branch' '-d' 'feature/old'");
    });

    it("should use -D for force delete", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.deleteBranch("/home/user/repo", "feature/old", {
        force: true,
      });

      const deleteCall = executeCommandMock.mock.calls[1];
      const cmd = deleteCall[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'branch' '-D' 'feature/old'");
    });
  });

  // -------------------------------------------------------------------------
  // remoteAdd
  // -------------------------------------------------------------------------
  describe("remoteAdd", () => {
    it("should add remote without fetch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteAdd(
        "/home/user/repo",
        "origin",
        "https://github.com/user/repo.git"
      );

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'remote' 'add' 'origin' 'https://github.com/user/repo.git'"
      );
    });

    it("should add remote with fetch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteAdd(
        "/home/user/repo",
        "origin",
        "https://github.com/user/repo.git",
        { fetch: true }
      );

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'remote' 'add' '-f' 'origin' 'https://github.com/user/repo.git'"
      );
    });

    it("should use runShell for overwrite mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteAdd(
        "/home/user/repo",
        "origin",
        "https://github.com/user/repo.git",
        { overwrite: true }
      );

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toContain(
        "git -C '/home/user/repo' 'remote' 'add' 'origin' 'https://github.com/user/repo.git'"
      );
      expect(cmd).toContain("||");
      expect(cmd).toContain(
        "git -C '/home/user/repo' 'remote' 'set-url' 'origin' 'https://github.com/user/repo.git'"
      );
    });

    it("should use runShell for overwrite+fetch mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteAdd(
        "/home/user/repo",
        "origin",
        "https://github.com/user/repo.git",
        { overwrite: true, fetch: true }
      );

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toContain(
        "git -C '/home/user/repo' 'remote' 'add' '-f' 'origin' 'https://github.com/user/repo.git'"
      );
      expect(cmd).toContain("||");
      expect(cmd).toContain(
        "git -C '/home/user/repo' 'remote' 'set-url' 'origin' 'https://github.com/user/repo.git'"
      );
      expect(cmd).toContain("git -C '/home/user/repo' 'fetch' 'origin'");
    });

    it("should use runGit for non-overwrite mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteAdd(
        "/home/user/repo",
        "origin",
        "https://github.com/user/repo.git"
      );

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).not.toContain("||");
    });

    it("should throw error on failure", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({ stderr: "error" })
      );

      await expect(
        git.remoteAdd(
          "/home/user/repo",
          "origin",
          "https://github.com/user/repo.git"
        )
      ).rejects.toThrow();
    });
  });

  // -------------------------------------------------------------------------
  // remoteGet
  // -------------------------------------------------------------------------
  describe("remoteGet", () => {
    it("should construct remote get-url command", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteGet("/home/user/repo", "origin");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'remote' 'get-url' 'origin'");
    });

    it("should return URL when remote exists", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "https://github.com/user/repo.git\n",
        })
      );

      const url = await git.remoteGet("/home/user/repo", "origin");
      expect(url).toBe("https://github.com/user/repo.git");
    });

    it("should return undefined when remote does not exist", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({ stderr: "fatal: No such remote 'nonexistent'" })
      );

      const url = await git.remoteGet("/home/user/repo", "nonexistent");
      expect(url).toBeUndefined();
    });

    it("should use runGit (not runShell) for remoteGet", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.remoteGet("/home/user/repo", "origin");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).not.toContain("|| true");
    });

    it("should throw on non-remote errors", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({ stderr: "fatal: not a git repository" })
      );

      await expect(
        git.remoteGet("/home/user/repo", "origin")
      ).rejects.toThrow();
    });
  });

  // -------------------------------------------------------------------------
  // reset
  // -------------------------------------------------------------------------
  describe("reset", () => {
    it("should reset with default mixed mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset'");
    });

    it("should reset with soft mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { mode: "soft" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset' '--soft'");
    });

    it("should reset with hard mode", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { mode: "hard" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset' '--hard'");
    });

    it("should reset to specific target", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { target: "HEAD~1" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset' 'HEAD~1'");
    });

    it("should reset specific paths", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { paths: ["src/index.ts"] });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset' '--' 'src/index.ts'");
    });

    it("should combine mode, target, and paths", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", {
        mode: "soft",
        target: "HEAD~1",
        paths: ["src/index.ts"],
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'reset' '--soft' 'HEAD~1' '--' 'src/index.ts'"
      );
    });
  });

  // -------------------------------------------------------------------------
  // restore
  // -------------------------------------------------------------------------
  describe("restore", () => {
    it("should restore working tree by default", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", { paths: ["src/index.ts"] });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--worktree' '--' 'src/index.ts'"
      );
    });

    it("should restore staged files", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", {
        paths: ["src/index.ts"],
        staged: true,
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--staged' '--' 'src/index.ts'"
      );
    });

    it("should restore both staged and worktree", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", {
        paths: ["src/index.ts"],
        staged: true,
        worktree: true,
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--worktree' '--staged' '--' 'src/index.ts'"
      );
    });

    it("should restore from specific source", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", {
        paths: ["src/index.ts"],
        source: "HEAD~1",
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--worktree' '--source' 'HEAD~1' '--' 'src/index.ts'"
      );
    });

    it("should restore multiple files", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", {
        paths: ["src/index.ts", "src/utils.ts"],
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--worktree' '--' 'src/index.ts' 'src/utils.ts'"
      );
    });

    it("should restore all files with dot", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.restore("/home/user/repo", { paths: ["."] });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'restore' '--worktree' '--' '.'"
      );
    });
  });

  // -------------------------------------------------------------------------
  // pull
  // -------------------------------------------------------------------------
  describe("pull", () => {
    it("should pull from default upstream", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.pull("/home/user/repo");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'pull'");
    });

    it("should pull from specific remote", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.pull("/home/user/repo", { remote: "origin" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'pull' 'origin'");
    });

    it("should pull specific branch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.pull("/home/user/repo", { branch: "main" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'pull' 'main'");
    });

    it("should pull from remote and branch", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.pull("/home/user/repo", { remote: "origin", branch: "main" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'pull' 'origin' 'main'");
    });
  });

  // -------------------------------------------------------------------------
  // configureUser
  // -------------------------------------------------------------------------
  describe("configureUser", () => {
    it("should set global user config by default", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.configureUser("/home/user/repo", "Agent", "agent@example.com");

      const nameCall = executeCommandMock.mock.calls[1];
      const emailCall = executeCommandMock.mock.calls[2];
      const nameCmd = nameCall[0] as string;
      const emailCmd = emailCall[0] as string;

      expect(nameCmd).toBe(
        "git -C '/home/user/repo' 'config' '--global' 'user.name' 'Agent'"
      );
      expect(emailCmd).toBe(
        "git -C '/home/user/repo' 'config' '--global' 'user.email' 'agent@example.com'"
      );
    });

    it("should set local user config when scope is local", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.configureUser("/home/user/repo", "Agent", "agent@example.com", {
        scope: "local",
      });

      const nameCall = executeCommandMock.mock.calls[1];
      const emailCall = executeCommandMock.mock.calls[2];
      const nameCmd = nameCall[0] as string;
      const emailCmd = emailCall[0] as string;

      expect(nameCmd).toBe(
        "git -C '/home/user/repo' 'config' '--local' 'user.name' 'Agent'"
      );
      expect(emailCmd).toBe(
        "git -C '/home/user/repo' 'config' '--local' 'user.email' 'agent@example.com'"
      );
    });

    it("should set both name and email", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.configureUser("/home/user/repo", "Agent", "agent@example.com");

      expect(executeCommandMock.mock.calls.length).toBe(3); // version + name + email
    });
  });

  // -------------------------------------------------------------------------
  // setConfig
  // -------------------------------------------------------------------------
  describe("setConfig", () => {
    it("should set global config by default", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.setConfig("/home/user/repo", "pull.rebase", "true");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'config' '--global' 'pull.rebase' 'true'"
      );
    });

    it("should set local config when scope is local", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.setConfig("/home/user/repo", "core.autocrlf", "true", {
        scope: "local",
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'config' '--local' 'core.autocrlf' 'true'"
      );
    });

    it("should handle special values", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.setConfig("/home/user/repo", "user.name", "John Doe");

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'config' '--global' 'user.name' 'John Doe'"
      );
    });
  });

  // -------------------------------------------------------------------------
  // listBranches - detached HEAD handling (E2B alignment)
  // -------------------------------------------------------------------------
  describe("listBranches - detached HEAD", () => {
    it("should skip detached HEAD state in branch list", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      // Simulate detached HEAD output
      const branchOutput =
        "(HEAD detached at abc1234)\t*\nmain\t \nfeature\t \n";

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: branchOutput })
      );

      const result = await git.listBranches("/home/user/repo");

      // Should NOT include detached HEAD as a branch
      expect(result.current).toBe(""); // No valid current branch
      expect(result.branches).toHaveLength(2);
      expect(result.branches.map((b) => b.name)).not.toContain(
        "(HEAD detached at abc1234)"
      );
      expect(result.branches.map((b) => b.name)).toContain("main");
      expect(result.branches.map((b) => b.name)).toContain("feature");
    });

    it("should handle detached HEAD with other branches", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      const branchOutput =
        "main\t*\n(HEAD detached at def5678)\t \nfeature\t \n";

      executeCommandMock.mockResolvedValueOnce(
        successResult({ stdout: branchOutput })
      );

      const result = await git.listBranches("/home/user/repo");

      expect(result.current).toBe("main");
      expect(result.branches).toHaveLength(2);
      expect(result.branches[0]).toEqual({ name: "main", isCurrent: true });
      expect(result.branches[1]).toEqual({ name: "feature", isCurrent: false });
    });
  });

  // -------------------------------------------------------------------------
  // reset - parameter validation (E2B alignment: no validation, let git handle it)
  // -------------------------------------------------------------------------
  describe("reset - parameter combinations", () => {
    it("should allow both target and paths (git will validate)", async () => {
      // E2B does NOT validate parameter conflicts - it passes through to git
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", {
        mode: "mixed",
        target: "HEAD~1",
        paths: ["src/index.ts"],
      });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      // Command is constructed as-is, git will error if invalid
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'reset' '--mixed' 'HEAD~1' '--' 'src/index.ts'"
      );
    });

    it("should handle reset with only target", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { target: "HEAD~2" });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe("git -C '/home/user/repo' 'reset' 'HEAD~2'");
    });

    it("should handle reset with only paths (unstages files)", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.reset("/home/user/repo", { paths: ["file1.txt", "file2.txt"] });

      const call = executeCommandMock.mock.calls[1];
      const cmd = call[0] as string;
      expect(cmd).toBe(
        "git -C '/home/user/repo' 'reset' '--' 'file1.txt' 'file2.txt'"
      );
    });
  });

  // -------------------------------------------------------------------------
  // configureUser - scope validation
  // -------------------------------------------------------------------------
  describe("configureUser - scope handling", () => {
    it("should use global scope when scope is undefined", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.configureUser("/home/user/repo", "Agent", "agent@example.com");

      const nameCall = executeCommandMock.mock.calls[1];
      const nameCmd = nameCall[0] as string;
      // Default is global (no --local flag)
      expect(nameCmd).toContain("'config'");
      expect(nameCmd).not.toContain("'--local'");
    });

    it("should use global scope when scope is 'global'", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(successResult());
      executeCommandMock.mockResolvedValueOnce(successResult());

      await git.configureUser("/home/user/repo", "Agent", "agent@example.com", {
        scope: "global",
      });

      const nameCall = executeCommandMock.mock.calls[1];
      const nameCmd = nameCall[0] as string;
      // Explicit global also has no --local flag
      expect(nameCmd).not.toContain("'--local'");
    });
  });

  // -------------------------------------------------------------------------
  // getConfig - edge cases
  // -------------------------------------------------------------------------
  describe("getConfig - edge cases", () => {
    it("should trim whitespace from config value", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "  Agent  \n",
        })
      );

      const value = await git.getConfig("/home/user/repo", "user.name");
      expect(value).toBe("Agent");
    });

    it("should return full trimmed output for multi-line stdout", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "Agent\nSome other output\n",
        })
      );

      const value = await git.getConfig("/home/user/repo", "user.name");
      expect(value).toBe("Agent\nSome other output");
    });
  });

  // -------------------------------------------------------------------------
  // remoteGet - edge cases
  // -------------------------------------------------------------------------
  describe("remoteGet - edge cases", () => {
    it("should trim whitespace from URL", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "  https://github.com/user/repo.git  \n",
        })
      );

      const url = await git.remoteGet("/home/user/repo", "origin");
      expect(url).toBe("https://github.com/user/repo.git");
    });

    it("should handle multiple URLs (return first)", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout:
            "https://github.com/user/repo.git\nhttps://github.com/user/repo2.git\n",
        })
      );

      const url = await git.remoteGet("/home/user/repo", "origin");
      // Returns all output trimmed
      expect(url).toContain("https://github.com/user/repo.git");
    });
  });

  // -------------------------------------------------------------------------
  // Error classification - additional cases (E2B alignment)
  // -------------------------------------------------------------------------
  describe("error classification - additional cases", () => {
    it("should throw GitAuthError for 403 errors", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: unable to access 'https://github.com/user/repo.git': The requested URL returned error: 403",
        })
      );

      await expect(
        git.clone("https://github.com/user/repo.git")
      ).rejects.toThrow(GitAuthError);
    });

    it("should throw GitAuthError for 'access denied'", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr: "fatal: access denied",
        })
      );

      await expect(
        git.clone("https://github.com/user/repo.git")
      ).rejects.toThrow(GitAuthError);
    });

    it("should throw GitNotARepoError for 'does not appear to be a git repository'", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        failureResult({
          exitCode: 128,
          stderr:
            "fatal: '/tmp/not-a-repo' does not appear to be a git repository",
        })
      );

      await expect(git.status("/tmp/not-a-repo")).rejects.toThrow(
        GitNotARepoError
      );
    });
  });

  // -------------------------------------------------------------------------
  // commit - root commit parsing
  // -------------------------------------------------------------------------
  describe("commit - root commit parsing", () => {
    it("should parse commit hash from root commit output", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "[main (root-commit) abc1234] Initial commit\n",
        })
      );

      const result = await git.commit("/home/user/repo", "Initial commit");
      expect(result.commitHash).toBe("abc1234");
    });

    it("should parse commit hash with branch containing slashes", async () => {
      const { git, executeCommandMock } = createGitWithVersion();
      executeCommandMock.mockResolvedValueOnce(
        successResult({
          stdout: "[feature/new-branch def5678] Add feature\n",
        })
      );

      const result = await git.commit("/home/user/repo", "Add feature");
      expect(result.commitHash).toBe("def5678");
    });
  });
});
