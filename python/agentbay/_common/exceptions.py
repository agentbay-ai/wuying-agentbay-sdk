class AgentBayError(Exception):
    """Base exception for all AgentBay SDK errors."""

    def __init__(self, message=None, *args, **kwargs):
        if message is None:
            message = self.__class__.__name__
        super().__init__(message, *args)
        self.extra = kwargs


class WsCancelledError(AgentBayError):
    """Raised when a WS stream is cancelled by the caller."""


class AuthenticationError(AgentBayError):
    """Raised when there is an authentication error."""

    def __init__(self, message="Authentication failed", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class APIError(AgentBayError):
    """Raised when there is an error with the API."""

    def __init__(self, message="API error", status_code=None, *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.status_code = status_code


class FileError(AgentBayError):
    """Raised for errors related to file operations."""

    def __init__(self, message="File operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class CommandError(AgentBayError):
    """Raised for errors related to command execution."""

    def __init__(self, message="Command execution error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class SessionError(AgentBayError):
    """Raised for errors related to session operations."""

    def __init__(self, message="Session error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class OssError(AgentBayError):
    """Raised for errors related to OSS operations."""

    def __init__(self, message="OSS operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class BrowserError(AgentBayError):
    """Raised when there is an error with the browser."""

    def __init__(self, message="Browser error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class AgentError(AgentBayError):
    """Raised for errors related to Agent actions."""

    def __init__(self, message="Agent action error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class ClearanceTimeoutError(AgentBayError):
    """Raised when context clearing operation times out."""

    def __init__(self, message="Context clearing operation timed out", *args, **kwargs):
        super().__init__(message, *args, **kwargs)

class GitError(AgentBayError):
    """
    Base exception for all git operations.

    Attributes:
        exit_code: The exit code returned by the git command.
        stderr: The stderr output from the git command.
    """
    def __init__(self, message="Git operation error", exit_code=1, stderr="", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
        self.exit_code = exit_code
        self.stderr = stderr

class GitAuthError(GitError):
    """
    Raised when git authentication fails.

    Common causes include invalid credentials, missing access tokens,
    or insufficient repository permissions.
    """
    def __init__(self, message="Git authentication error", exit_code=1, stderr="", *args, **kwargs):
        super().__init__(message, exit_code, stderr, *args, **kwargs)

class GitNotFoundError(GitError):
    """
    Raised when git is not installed or not found on the remote environment.
    """
    def __init__(self, message="Git not found", exit_code=127, stderr="", *args, **kwargs):
        super().__init__(message, exit_code, stderr, *args, **kwargs)

class GitConflictError(GitError):
    """
    Raised when a git merge or rebase conflict occurs.
    """
    def __init__(self, message="Git merge conflict", exit_code=1, stderr="", *args, **kwargs):
        super().__init__(message, exit_code, stderr, *args, **kwargs)

class GitNotARepoError(GitError):
    """
    Raised when the target directory is not a git repository.
    """
    def __init__(self, message="Not a git repository", exit_code=128, stderr="", *args, **kwargs):
        super().__init__(message, exit_code, stderr, *args, **kwargs)


class PtyError(AgentBayError):
    """Base exception for all PTY operations."""

    def __init__(self, message="PTY operation error", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class PtySessionNotFoundError(PtyError):
    """Raised when a PTY session does not exist or has been terminated."""

    def __init__(self, message="PTY session not found", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class PtyNotConnectedError(PtyError):
    """Raised when attempting to use a PTY handle that is not connected."""

    def __init__(self, message="PTY handle is not connected", *args, **kwargs):
        super().__init__(message, *args, **kwargs)