import re
from typing import Dict, List, Optional
from urllib.parse import unquote

from ..base_service import AsyncBaseService
from ..._common.exceptions import (
    GitAuthError,
    GitConflictError,
    GitError,
    GitNotARepoError,
    GitNotFoundError,
)
from ..._common.logger import get_logger
from ..._common.models.command import CommandResult
from ..._common.models.git import (
    GitBranchInfo,
    GitBranchListResult,
    GitCloneResult,
    GitCommitResult,
    GitFileStatus,
    GitInitResult,
    GitLogEntry,
    GitLogResult,
    GitStatusResult,
)

# Initialize logger for this module
_logger = get_logger("git")

# Default environment variables for all git commands.
# GIT_TERMINAL_PROMPT=0 prevents git from prompting for credentials interactively,
# which would cause the command to hang in a non-interactive environment.
_DEFAULT_GIT_ENV: Dict[str, str] = {
    "GIT_TERMINAL_PROMPT": "0",
    "LC_ALL": "C",
}

# Default timeout for git operations in milliseconds (30 seconds).
_DEFAULT_GIT_TIMEOUT_MS = 30000

# Default timeout for git clone operations in milliseconds (5 minutes).
_DEFAULT_CLONE_TIMEOUT_MS = 300000

# Default timeout for git pull operations in milliseconds (2 minutes).
_DEFAULT_PULL_TIMEOUT_MS = 120000

# Valid reset modes for parameter validation.
_VALID_RESET_MODES = {"soft", "mixed", "hard", "merge", "keep"}


class AsyncGit(AsyncBaseService):
    """
    Manage git operations in the AgentBay cloud environment.

    Provides a high-level interface for common git workflows (clone, commit,
    branch, config, etc.) by executing git commands on the remote session via
    the Command module. All commands run with ``GIT_TERMINAL_PROMPT=0`` to
    prevent interactive credential prompts.

    Example:
        agent_bay = AsyncAgentBay(api_key="your_api_key")
        result = await agent_bay.create()
        session = result.session

        clone_result = await session.git.clone(
            "https://github.com/user/repo.git",
            branch="main",
            depth=1,
        )
        print("Cloned to:", clone_result.path)
    """

    def __init__(self, session):
        super().__init__(session)
        self._git_available = None

    # -------------------------------------------------------------------------
    # Private helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _shell_escape(arg: str) -> str:
        """
        Escape a string for safe use in a shell command.

        Wraps the argument in single quotes and escapes any embedded
        single quotes.

        Args:
            arg: The argument to escape.

        Returns:
            The shell-escaped argument string.
        """
        return "'" + arg.replace("'", "'\\''") + "'"

    def _build_git_command(
        self, args: List[str], repo_path: Optional[str] = None
    ) -> str:
        """
        Build a complete git command string.

        All arguments are shell-escaped for safe execution. When *repo_path*
        is given, ``git -C <path>`` is prepended.

        Args:
            args: Git sub-command arguments.
            repo_path: Optional repository path (adds ``-C`` prefix).

        Returns:
            The complete shell command string.
        """
        parts = ["git"]
        if repo_path:
            parts.extend(["-C", self._shell_escape(repo_path)])
        parts.extend(self._shell_escape(a) for a in args)
        return " ".join(parts)

    @staticmethod
    def _get_stdout(result: CommandResult) -> str:
        """
        Extract stdout content from a CommandResult.

        Args:
            result: The CommandResult to extract from.

        Returns:
            The stdout string (empty string if absent).
        """
        return result.stdout or result.output or ""

    @staticmethod
    def _get_stderr(result: CommandResult) -> str:
        """
        Extract stderr content from a CommandResult.

        Args:
            result: The CommandResult to extract from.

        Returns:
            The stderr string (empty string if absent).
        """
        return result.stderr or result.error_message or ""

    async def _run_git(
        self,
        args: List[str],
        repo_path: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> CommandResult:
        """
        Execute a standard git command via the Command module.

        Automatically merges ``_DEFAULT_GIT_ENV`` into the environment.

        Args:
            args: Git sub-command arguments.
            repo_path: Optional repository path for ``git -C``.
            timeout_ms: Optional timeout in milliseconds.

        Returns:
            The CommandResult from executing the git command.
        """
        cmd = self._build_git_command(args, repo_path)
        _logger.debug("Executing git command: %s", cmd)
        result = await self.session.command.execute_command(
            cmd,
            timeout_ms=timeout_ms or _DEFAULT_GIT_TIMEOUT_MS,
            envs=_DEFAULT_GIT_ENV,
        )
        if not result.success:
            _logger.debug(
                "Git command failed: cmd=%s, exit_code=%s, stderr=%s",
                cmd, result.exit_code, self._get_stderr(result)[:500],
            )
        return result

    async def _run_shell(self, cmd: str, timeout_ms: Optional[int] = None) -> CommandResult:
        """
        Execute a raw shell command with git environment variables.

        Args:
            cmd: The raw shell command string.
            timeout_ms: Optional timeout in milliseconds.

        Returns:
            The CommandResult from executing the shell command.
        """
        return await self.session.command.execute_command(
            cmd,
            timeout_ms=timeout_ms or _DEFAULT_GIT_TIMEOUT_MS,
            envs=_DEFAULT_GIT_ENV,
        )

    async def _ensure_git_available(self) -> None:
        """
        Check whether git is available on the remote environment.

        The result is cached after the first successful check.

        Raises:
            GitNotFoundError: If git is not installed or not reachable.
        """
        if self._git_available is True:
            return

        result = await self._run_git(["--version"])

        if not result.success:
            self._git_available = False
            _logger.warning("Git is not available on the remote environment")
            raise GitNotFoundError(
                "Git is not installed or not available on the remote environment. "
                "Please ensure git is installed in the session image.",
                exit_code=result.exit_code or 127,
                stderr=self._get_stderr(result),
            )

        self._git_available = True
        _logger.info("Git is available on the remote environment")

    def _classify_error(self, operation: str, result: CommandResult) -> GitError:
        """
        Classify a failed git command result into a specific error type.

        Args:
            operation: The git operation name (e.g., ``'clone'``, ``'pull'``).
            result: The failed CommandResult.

        Returns:
            A specific GitError subclass instance.
        """
        raw_stderr = self._get_stderr(result)
        stderr = raw_stderr.lower()
        exit_code = result.exit_code or 1

        # Authentication errors
        auth_keywords = [
            "authentication failed",
            "could not read username",
            "invalid credentials",
            "authorization failed",
            "access denied",
            "permission denied",
            "403",
        ]
        if any(kw in stderr for kw in auth_keywords):
            _logger.warning("Git %s failed: authentication error", operation)
            return GitAuthError(
                f"Git {operation} failed: authentication error. {raw_stderr}",
                exit_code=exit_code,
                stderr=raw_stderr,
            )

        # Not a git repository
        if "not a git repository" in stderr or "does not appear to be a git repository" in stderr:
            _logger.warning("Git %s failed: not a git repository", operation)
            return GitNotARepoError(
                f"Git {operation} failed: not a git repository. {raw_stderr}",
                exit_code=exit_code,
                stderr=raw_stderr,
            )

        # Merge/rebase conflicts
        if "CONFLICT" in raw_stderr or "merge conflict" in stderr or "automatic merge failed" in stderr:
            _logger.warning("Git %s failed: merge conflict", operation)
            return GitConflictError(
                f"Git {operation} failed: merge conflict. {raw_stderr}",
                exit_code=exit_code,
                stderr=raw_stderr,
            )

        # Git not found
        if "command not found" in stderr or "git: not found" in stderr or exit_code == 127:
            _logger.warning("Git %s failed: git not found", operation)
            return GitNotFoundError(
                f"Git {operation} failed: git not found. {raw_stderr}",
                exit_code=exit_code,
                stderr=raw_stderr,
            )

        # Generic git error
        _logger.warning("Git %s failed (exit code %d)", operation, exit_code)
        return GitError(
            f"Git {operation} failed (exit code {exit_code}): {raw_stderr}",
            exit_code=exit_code,
            stderr=raw_stderr,
        )

    @staticmethod
    def _derive_repo_dir_from_url(url: str) -> str:
        """
        Derive the target directory name from a git repository URL.

        Args:
            url: The git repository URL.

        Returns:
            The derived directory name.
        """
        # Remove trailing slashes
        cleaned = url.rstrip("/")
        # Remove .git suffix
        if cleaned.endswith(".git"):
            cleaned = cleaned[:-4]
        # Handle URL-encoded characters (e.g., %20)
        cleaned = unquote(cleaned)
        # Extract the last path segment
        last_slash = cleaned.rfind("/")
        last_colon = cleaned.rfind(":")
        separator_index = max(last_slash, last_colon)
        if separator_index >= 0 and separator_index < len(cleaned) - 1:
            return cleaned[separator_index + 1 :]
        return cleaned

    @staticmethod
    def _derive_status(index_status: str, work_tree_status: str) -> str:
        """
        Derive a normalized status label from porcelain status characters.

        Args:
            index_status: Index status character.
            work_tree_status: Working tree status character.

        Returns:
            Normalized status label (e.g., ``'modified'``, ``'added'``).
        """
        combined = index_status + work_tree_status
        if "U" in combined:
            return "conflict"
        if "R" in combined:
            return "renamed"
        if "C" in combined:
            return "copied"
        if "D" in combined:
            return "deleted"
        if "A" in combined:
            return "added"
        if "M" in combined:
            return "modified"
        if "T" in combined:
            return "typechange"
        if "?" in combined:
            return "untracked"
        return "unknown"

    @staticmethod
    def _parse_git_status(output: str) -> GitStatusResult:
        """
        Parse ``git status --porcelain=1 -b`` output into a structured result.

        Args:
            output: Raw stdout from ``git status``.

        Returns:
            Parsed GitStatusResult with branch info and file statuses.
        """
        lines = [line for line in output.split("\n") if line.strip()]
        current_branch: Optional[str] = None
        upstream: Optional[str] = None
        ahead = 0
        behind = 0
        detached = False
        file_status: List[GitFileStatus] = []

        if not lines:
            return GitStatusResult()

        branch_line = lines[0]
        if branch_line.startswith("## "):
            branch_info = branch_line[3:]

            # Handle "No commits yet on <branch>" format
            no_commits_match = re.match(r"No commits yet on (.+)", branch_info)
            if no_commits_match:
                current_branch = no_commits_match.group(1).split("...")[0]
            else:
                # Parse ahead/behind info: "## main...origin/main [ahead 1, behind 2]"
                ahead_start = branch_info.find(" [")
                branch_part = branch_info if ahead_start == -1 else branch_info[:ahead_start]
                ahead_part = None if ahead_start == -1 else branch_info[ahead_start + 2 : -1]

                # Detect detached HEAD
                if branch_part.startswith("HEAD (detached") or "detached" in branch_part:
                    detached = True
                elif branch_part == "HEAD (no branch)":
                    detached = True
                elif "..." in branch_part:
                    parts = branch_part.split("...")
                    current_branch = parts[0] or None
                    upstream = parts[1] if len(parts) > 1 else None
                else:
                    current_branch = branch_part or None

                # Parse ahead/behind
                if ahead_part:
                    ahead_match = re.search(r"ahead (\d+)", ahead_part)
                    behind_match = re.search(r"behind (\d+)", ahead_part)
                    if ahead_match:
                        ahead = int(ahead_match.group(1))
                    if behind_match:
                        behind = int(behind_match.group(1))

        for line in lines[1:]:
            if line.startswith("?? "):
                name = line[3:]
                file_status.append(
                    GitFileStatus(
                        path=name,
                        status="untracked",
                        index_status="?",
                        work_tree_status="?",
                        staged=False,
                    )
                )
                continue

            if len(line) < 3:
                continue

            index_s = line[0]
            work_tree_s = line[1]
            path = line[3:]

            # Handle renamed files (path contains " -> ")
            renamed_from: Optional[str] = None
            actual_path = path
            if " -> " in path:
                parts = path.split(" -> ", 1)
                renamed_from = parts[0]
                actual_path = parts[1]

            staged = index_s not in (" ", "?")

            file_status.append(
                GitFileStatus(
                    path=actual_path,
                    status=AsyncGit._derive_status(index_s, work_tree_s),
                    index_status=index_s,
                    work_tree_status=work_tree_s,
                    staged=staged,
                    renamed_from=renamed_from,
                )
            )

        return GitStatusResult(
            current_branch=current_branch,
            upstream=upstream,
            ahead=ahead,
            behind=behind,
            detached=detached,
            files=file_status,
        )

    @staticmethod
    def _parse_git_log(output: str) -> GitLogResult:
        """
        Parse ``git log --format=...`` output into a structured result.

        Uses ``\\x00`` (NUL) as record separator and ``\\x01`` (SOH) as
        field separator.

        Args:
            output: Raw stdout from ``git log``.

        Returns:
            Parsed GitLogResult containing commit entries.
        """
        entries: List[GitLogEntry] = []
        records = [r for r in output.split("\x00") if r.strip()]

        for record in records:
            parts = record.split("\x01")
            if len(parts) >= 6:
                entries.append(
                    GitLogEntry(
                        hash=parts[0].strip(),
                        short_hash=parts[1],
                        author_name=parts[2],
                        author_email=parts[3],
                        date=parts[4],
                        message=parts[5].strip(),
                    )
                )

        return GitLogResult(entries=entries)

    @staticmethod
    def _parse_git_branches(output: str) -> GitBranchListResult:
        """
        Parse ``git branch --format=...`` output into a structured result.

        Args:
            output: Raw stdout from ``git branch``.

        Returns:
            Parsed GitBranchListResult with branch info.
        """
        lines = [line for line in output.split("\n") if line.strip()]
        branches: List[GitBranchInfo] = []
        current = ""

        for line in lines:
            parts = line.split("\t")
            name = parts[0].strip()

            # Skip detached HEAD state
            if name.startswith("(HEAD detached"):
                continue

            is_current = len(parts) > 1 and parts[1].strip() == "*"

            if name:
                branches.append(GitBranchInfo(name=name, is_current=is_current))
                if is_current:
                    current = name

        return GitBranchListResult(branches=branches, current=current)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------

    async def clone(
        self,
        url: str,
        *,
        path: Optional[str] = None,
        branch: Optional[str] = None,
        depth: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> GitCloneResult:
        """
        Clone a git repository into the remote session environment.

        Supports public repositories. When *branch* is specified,
        ``--single-branch`` is automatically added.

        Args:
            url: The repository URL to clone (HTTPS or SSH).
            path: Target directory path. If omitted, derived from the URL.
            branch: Branch to clone (adds ``--single-branch``).
            depth: Create a shallow clone with the given number of commits.
            timeout_ms: Timeout in milliseconds (default: 300 000, i.e. 5 min).

        Returns:
            GitCloneResult with the cloned repository path.

        Raises:
            GitNotFoundError: If git is not installed.
            GitAuthError: If authentication fails.
            GitError: For other git errors.

        Example:
            result = await session.git.clone(
                "https://github.com/user/repo.git",
                branch="main",
                depth=1,
            )
            print(result.path)
        """
        await self._ensure_git_available()

        _logger.info(
            "Cloning repository: url=%s, branch=%s, depth=%s, path=%s",
            url, branch, depth, path,
        )

        args: List[str] = ["clone"]

        if branch:
            args.extend(["--branch", branch, "--single-branch"])

        if depth:
            args.extend(["--depth", str(depth)])

        args.append(url)

        target_path = path or self._derive_repo_dir_from_url(url)
        args.append(target_path)

        effective_timeout = timeout_ms or _DEFAULT_CLONE_TIMEOUT_MS
        _logger.debug("Clone timeout: %d ms", effective_timeout)

        result = await self._run_git(args, timeout_ms=effective_timeout)

        if not result.success:
            stderr = self._get_stderr(result)
            stdout = self._get_stdout(result)
            _logger.error(
                "Clone failed: url=%s, exit_code=%s, stderr=%s, stdout=%s",
                url, result.exit_code, stderr[:1000], stdout[:500],
            )
            raise self._classify_error("clone", result)

        _logger.info("Clone succeeded: url=%s -> %s", url, target_path)
        return GitCloneResult(path=target_path)

    async def init(
        self,
        path: str,
        *,
        initial_branch: Optional[str] = None,
        bare: bool = False,
        timeout_ms: Optional[int] = None,
    ) -> GitInitResult:
        """
        Initialize a new git repository in the remote session environment.

        Args:
            path: Directory path to initialize as a git repository.
            initial_branch: Name of the initial branch (e.g., ``"main"``).
            bare: If True, create a bare repository.
            timeout_ms: Timeout in milliseconds.

        Returns:
            GitInitResult with the initialized repository path.

        Raises:
            GitNotFoundError: If git is not installed.
            GitError: For other git errors.

        Example:
            result = await session.git.init("/home/user/project", initial_branch="main")
            print(result.path)
        """
        await self._ensure_git_available()

        args: List[str] = ["init"]

        if initial_branch:
            args.extend(["--initial-branch", initial_branch])

        if bare:
            args.append("--bare")

        args.append(path)

        result = await self._run_git(args, timeout_ms=timeout_ms)

        if not result.success:
            _logger.error("Init failed: path=%s, exit_code=%s", path, result.exit_code)
            raise self._classify_error("init", result)

        _logger.debug("Initialized repository at %s", path)
        return GitInitResult(path=path)

    async def add(
        self,
        repo_path: str,
        *,
        files: Optional[List[str]] = None,
        stage_all: bool = True,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Add files to the git staging area.

        By default (no *files* specified and *stage_all* is ``True``), stages
        all changes using ``git add -A``.

        Args:
            repo_path: The repository path.
            files: Specific files to add. Overrides *stage_all*.
            stage_all: Use ``git add -A`` when no files specified (default: True).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.add("/home/user/project")
            await session.git.add("/home/user/project", files=["README.md"])
        """
        await self._ensure_git_available()

        args: List[str] = ["add"]

        if files and len(files) > 0:
            args.extend(["--", *files])
        elif stage_all:
            args.append("-A")
        else:
            args.append(".")

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)

        if not result.success:
            _logger.error("Add failed: repo=%s, files=%s, exit_code=%s", repo_path, files, result.exit_code)
            raise self._classify_error("add", result)

    async def commit(
        self,
        repo_path: str,
        message: str,
        *,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        allow_empty: bool = False,
        timeout_ms: Optional[int] = None,
    ) -> GitCommitResult:
        """
        Create a git commit with the staged changes.

        Author information, when provided, is applied as temporary ``-c``
        configuration and is **not** persisted to git config.

        Args:
            repo_path: The repository path.
            message: The commit message.
            author_name: Author name (temporary, not persisted).
            author_email: Author email (temporary, not persisted).
            allow_empty: Allow creating a commit with no changes.
            timeout_ms: Timeout in milliseconds.

        Returns:
            GitCommitResult containing the commit hash.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.add("/home/user/project")
            result = await session.git.commit("/home/user/project", "Initial commit")
            print(result.commit_hash)
        """
        await self._ensure_git_available()

        # -c parameters must come BEFORE the 'commit' subcommand
        args: List[str] = []

        if author_name:
            args.extend(["-c", f"user.name={author_name}"])
        if author_email:
            args.extend(["-c", f"user.email={author_email}"])

        args.extend(["commit", "-m", message])

        if allow_empty:
            args.append("--allow-empty")

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)

        if not result.success:
            _logger.error("Commit failed: repo=%s, exit_code=%s", repo_path, result.exit_code)
            raise self._classify_error("commit", result)

        # Parse commit hash from output
        commit_output = self._get_stdout(result)
        hash_match = re.search(
            r"\[[\w/.-]+(?:\s+\([^)]+\))?\s+([a-f0-9]+)\]", commit_output
        )
        return GitCommitResult(commit_hash=hash_match.group(1) if hash_match else None)

    async def status(
        self,
        repo_path: str,
        *,
        timeout_ms: Optional[int] = None,
    ) -> GitStatusResult:
        """
        Get the status of the working tree and staging area.

        Returns a structured result parsed from
        ``git status --porcelain=1 -b``.

        Args:
            repo_path: The repository path.
            timeout_ms: Timeout in milliseconds.

        Returns:
            GitStatusResult with branch info and file statuses.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            status = await session.git.status("/home/user/project")
            print(status.current_branch, status.is_clean)
        """
        await self._ensure_git_available()

        result = await self._run_git(
            ["status", "--porcelain=1", "-b"], repo_path, timeout_ms=timeout_ms
        )

        if not result.success:
            raise self._classify_error("status", result)

        return self._parse_git_status(
            self._get_stdout(result)
        )

    async def log(
        self,
        repo_path: str,
        *,
        max_count: Optional[int] = None,
        timeout_ms: Optional[int] = None,
    ) -> GitLogResult:
        """
        Get the commit history of the repository.

        Args:
            repo_path: The repository path.
            max_count: Maximum number of log entries to return.
            timeout_ms: Timeout in milliseconds.

        Returns:
            GitLogResult with structured commit entries.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            log = await session.git.log("/home/user/project", max_count=5)
            for entry in log.entries:
                print(entry.short_hash, entry.message)
        """
        await self._ensure_git_available()

        fmt = "%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00"
        args: List[str] = ["log", f"--format={fmt}"]

        if max_count:
            args.extend(["--max-count", str(max_count)])

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)

        if not result.success:
            raise self._classify_error("log", result)

        return self._parse_git_log(
            self._get_stdout(result)
        )

    async def list_branches(
        self,
        repo_path: str,
        *,
        timeout_ms: Optional[int] = None,
    ) -> GitBranchListResult:
        """
        List all local branches in the repository.

        Args:
            repo_path: The repository path.
            timeout_ms: Timeout in milliseconds.

        Returns:
            GitBranchListResult with branch info and current branch.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            branches = await session.git.list_branches("/home/user/project")
            print(branches.current)
        """
        await self._ensure_git_available()

        result = await self._run_git(
            ["branch", "--format=%(refname:short)\t%(HEAD)"],
            repo_path,
            timeout_ms=timeout_ms,
        )

        if not result.success:
            raise self._classify_error("list_branches", result)

        return self._parse_git_branches(
            self._get_stdout(result)
        )

    async def create_branch(
        self,
        repo_path: str,
        branch: str,
        *,
        checkout: bool = True,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Create a new branch in the repository.

        By default the new branch is also checked out (``git checkout -b``).
        Set *checkout* to ``False`` to create without switching.

        Args:
            repo_path: The repository path.
            branch: The name of the new branch.
            checkout: Whether to checkout the new branch (default: True).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.create_branch("/home/user/project", "feature-x")
        """
        await self._ensure_git_available()

        if checkout:
            args = ["checkout", "-b", branch]
        else:
            args = ["branch", branch]

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)

        if not result.success:
            raise self._classify_error("create_branch", result)

    async def checkout_branch(
        self,
        repo_path: str,
        branch: str,
        *,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Switch to an existing branch.

        Args:
            repo_path: The repository path.
            branch: The branch name to switch to.
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.checkout_branch("/home/user/project", "main")
        """
        await self._ensure_git_available()

        result = await self._run_git(
            ["checkout", branch], repo_path, timeout_ms=timeout_ms
        )

        if not result.success:
            raise self._classify_error("checkout_branch", result)

    async def delete_branch(
        self,
        repo_path: str,
        branch: str,
        *,
        force: bool = False,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Delete a local branch.

        Args:
            repo_path: The repository path.
            branch: The branch name to delete.
            force: Force delete (``-D`` instead of ``-d``).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.delete_branch("/home/user/project", "old-branch")
        """
        await self._ensure_git_available()

        delete_flag = "-D" if force else "-d"
        result = await self._run_git(
            ["branch", delete_flag, branch], repo_path, timeout_ms=timeout_ms
        )

        if not result.success:
            raise self._classify_error("delete_branch", result)

    async def remote_add(
        self,
        repo_path: str,
        name: str,
        url: str,
        *,
        fetch: bool = False,
        overwrite: bool = False,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Add a remote repository.

        When *overwrite* is ``True``, the remote URL is updated if the remote
        already exists (idempotent behaviour).

        Args:
            repo_path: The repository path.
            name: The remote name (e.g., ``"origin"``).
            url: The remote URL.
            fetch: Fetch from the remote immediately after adding.
            overwrite: Update the URL if the remote already exists.
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.remote_add(
                "/home/user/project", "origin",
                "https://github.com/user/repo.git",
            )
        """
        await self._ensure_git_available()

        add_args: List[str] = ["remote", "add"]
        if fetch:
            add_args.append("-f")
        add_args.extend([name, url])

        if not overwrite:
            result = await self._run_git(add_args, repo_path, timeout_ms=timeout_ms)
            if not result.success:
                raise self._classify_error("remote_add", result)
        else:
            # Idempotent mode: add fails, fallback to set-url
            add_cmd = self._build_git_command(add_args, repo_path)
            set_url_cmd = self._build_git_command(
                ["remote", "set-url", name, url], repo_path
            )
            cmd = f"{add_cmd} || {set_url_cmd}"
            if fetch:
                fetch_cmd = self._build_git_command(["fetch", name], repo_path)
                cmd = f"({cmd}) && {fetch_cmd}"
            result = await self._run_shell(cmd, timeout_ms=timeout_ms)
            if not result.success:
                raise self._classify_error("remote_add", result)

    async def remote_get(
        self,
        repo_path: str,
        name: str,
        *,
        timeout_ms: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get the URL of a remote repository.

        Args:
            repo_path: The repository path.
            name: The remote name (e.g., ``"origin"``).
            timeout_ms: Timeout in milliseconds.

        Returns:
            The remote URL, or ``None`` if the remote does not exist.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.

        Example:
            url = await session.git.remote_get("/home/user/project", "origin")
            print(url)
        """
        await self._ensure_git_available()

        result = await self._run_git(
            ["remote", "get-url", name], repo_path, timeout_ms=timeout_ms
        )
        if not result.success:
            stderr = self._get_stderr(result).lower()
            # Remote does not exist -> return None (handle both English and Chinese locales)
            if "no such remote" in stderr or "没有此远程" in stderr:
                return None
            raise self._classify_error("remote_get", result)
        return self._get_stdout(result).strip() or None

    async def reset(
        self,
        repo_path: str,
        *,
        mode: Optional[str] = None,
        target: Optional[str] = None,
        paths: Optional[List[str]] = None,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Reset the repository to a specific state.

        Args:
            repo_path: The repository path.
            mode: Reset mode (``"soft"``, ``"mixed"``, ``"hard"``,
                ``"merge"``, or ``"keep"``).
            target: Target commit / branch / ref (defaults to HEAD).
            paths: Specific file paths to reset.
            timeout_ms: Timeout in milliseconds.

        Raises:
            ValueError: If *mode* is not a valid reset mode.
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.reset("/home/user/project", mode="hard", target="HEAD~1")
        """
        if mode and mode not in _VALID_RESET_MODES:
            raise ValueError(
                f"Invalid reset mode: '{mode}'. Must be one of {sorted(_VALID_RESET_MODES)}"
            )

        await self._ensure_git_available()

        args: List[str] = ["reset"]
        if mode:
            args.append(f"--{mode}")
        if target:
            args.append(target)
        if paths and len(paths) > 0:
            args.extend(["--", *paths])

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)
        if not result.success:
            raise self._classify_error("reset", result)

    async def restore(
        self,
        repo_path: str,
        paths: List[str],
        *,
        staged: bool = False,
        worktree: Optional[bool] = None,
        source: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Restore files from the index or working tree.

        Args:
            repo_path: The repository path.
            paths: File paths to restore. Use ``["."]`` to restore all files.
            staged: Restore the index / staging area (``--staged``).
            worktree: Restore the working tree (``--worktree``).
                Defaults to ``True`` when *staged* is ``False``.
            source: Restore from a specific commit / branch / ref
                (``--source``).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.restore("/home/user/project", ["file.txt"])
        """
        await self._ensure_git_available()

        resolved_staged = staged
        resolved_worktree = worktree if worktree is not None else (not resolved_staged)

        args: List[str] = ["restore"]
        if resolved_worktree:
            args.append("--worktree")
        if resolved_staged:
            args.append("--staged")
        if source:
            args.extend(["--source", source])
        args.extend(["--", *paths])

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)
        if not result.success:
            raise self._classify_error("restore", result)

    async def pull(
        self,
        repo_path: str,
        *,
        remote: Optional[str] = None,
        branch: Optional[str] = None,
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Pull changes from a remote repository.

        Args:
            repo_path: The repository path.
            remote: Remote name (e.g., ``"origin"``).
            branch: Branch name to pull.
            timeout_ms: Timeout in milliseconds (default: 120 000, i.e. 2 min).

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.
            GitError: For other git errors.

        Example:
            await session.git.pull("/home/user/project", remote="origin", branch="main")
        """
        await self._ensure_git_available()

        _logger.info(
            "Pulling from remote: repo=%s, remote=%s, branch=%s",
            repo_path, remote, branch,
        )

        args: List[str] = ["pull"]
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)

        result = await self._run_git(
            args, repo_path, timeout_ms=timeout_ms or _DEFAULT_PULL_TIMEOUT_MS
        )
        if not result.success:
            stderr = self._get_stderr(result)
            _logger.error(
                "Pull failed: repo=%s, remote=%s, branch=%s, exit_code=%s, stderr=%s",
                repo_path, remote, branch, result.exit_code, stderr[:1000],
            )
            raise self._classify_error("pull", result)

    async def configure_user(
        self,
        repo_path: str,
        name: str,
        email: str,
        *,
        scope: str = "global",
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Configure git user name and email.

        Args:
            repo_path: The repository path.
            name: The user name.
            email: The user email.
            scope: Configuration scope (``"global"`` or ``"local"``,
                default: ``"global"``).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.

        Example:
            await session.git.configure_user(
                "/home/user/project", "Alice", "alice@example.com",
            )
        """
        await self._ensure_git_available()

        scope_flag = "--local" if scope == "local" else "--global"
        base_args = ["config", scope_flag]

        name_result = await self._run_git(
            [*base_args, "user.name", name], repo_path, timeout_ms=timeout_ms
        )
        if not name_result.success:
            raise self._classify_error("configure_user", name_result)

        email_result = await self._run_git(
            [*base_args, "user.email", email], repo_path, timeout_ms=timeout_ms
        )
        if not email_result.success:
            raise self._classify_error("configure_user", email_result)

    async def set_config(
        self,
        repo_path: str,
        key: str,
        value: str,
        *,
        scope: str = "global",
        timeout_ms: Optional[int] = None,
    ) -> None:
        """
        Set a git configuration value.

        Args:
            repo_path: The repository path.
            key: The configuration key (e.g., ``"core.autocrlf"``).
            value: The configuration value.
            scope: Configuration scope (``"global"`` or ``"local"``,
                default: ``"global"``).
            timeout_ms: Timeout in milliseconds.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.

        Example:
            await session.git.set_config("/home/user/project", "core.autocrlf", "false")
        """
        await self._ensure_git_available()

        scope_flag = "--local" if scope == "local" else "--global"
        args = ["config", scope_flag, key, value]

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)
        if not result.success:
            raise self._classify_error("set_config", result)

    async def get_config(
        self,
        repo_path: str,
        key: str,
        *,
        scope: str = "global",
        timeout_ms: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get a git configuration value.

        Args:
            repo_path: The repository path.
            key: The configuration key (e.g., ``"user.name"``).
            scope: Configuration scope (``"global"`` or ``"local"``,
                default: ``"global"``).
            timeout_ms: Timeout in milliseconds.

        Returns:
            The configuration value, or ``None`` if the key is not found.

        Raises:
            GitNotFoundError: If git is not installed.
            GitNotARepoError: If the path is not a git repository.

        Example:
            name = await session.git.get_config("/home/user/project", "user.name")
            print(name)
        """
        await self._ensure_git_available()

        scope_flag = "--local" if scope == "local" else "--global"
        args = ["config", scope_flag, "--get", key]

        result = await self._run_git(args, repo_path, timeout_ms=timeout_ms)
        if not result.success:
            # git config --get exits with code 1 when the key is not found.
            # Use result.stderr directly (not _get_stderr) to avoid picking up
            # error_message which may contain unrelated transport-level info.
            raw_stderr = (result.stderr or "").strip().lower()
            if result.exit_code == 1 and (not raw_stderr or "key does not contain" in raw_stderr):
                return None
            raise self._classify_error("get_config", result)
        return self._get_stdout(result).strip() or None
