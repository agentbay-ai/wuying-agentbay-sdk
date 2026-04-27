package git

import (
	"testing"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
	"github.com/stretchr/testify/assert"
)

// ==================== classifyError Tests ====================

func TestClassifyError_AuthenticationFailed(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: Authentication failed for 'https://github.com/user/repo.git'",
	}
	err := classifyError("push", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_PermissionDenied(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "Permission denied (publickey).",
	}
	err := classifyError("push", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_CouldNotReadUsername(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: could not read Username for 'https://github.com': terminal prompts disabled",
	}
	err := classifyError("clone", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_NotAGitRepo(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: not a git repository (or any of the parent directories): .git",
	}
	err := classifyError("status", result)
	_, ok := err.(*GitNotARepoError)
	assert.True(t, ok, "expected GitNotARepoError, got %T", err)
}

func TestClassifyError_DoesNotAppearToBeGitRepo(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: 'origin' does not appear to be a git repository",
	}
	err := classifyError("push", result)
	_, ok := err.(*GitNotARepoError)
	assert.True(t, ok, "expected GitNotARepoError, got %T", err)
}

func TestClassifyError_ConflictUpperCase(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 1,
		Stderr:   "CONFLICT (content): Merge conflict in file.txt",
	}
	err := classifyError("merge", result)
	_, ok := err.(*GitConflictError)
	assert.True(t, ok, "expected GitConflictError, got %T", err)
}

func TestClassifyError_MergeConflict(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 1,
		Stderr:   "Merge conflict in file.txt",
	}
	err := classifyError("pull", result)
	_, ok := err.(*GitConflictError)
	assert.True(t, ok, "expected GitConflictError, got %T", err)
}

func TestClassifyError_AutomaticMergeFailed(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 1,
		Stderr:   "Automatic merge failed; fix conflicts and then commit the result.",
	}
	err := classifyError("merge", result)
	_, ok := err.(*GitConflictError)
	assert.True(t, ok, "expected GitConflictError, got %T", err)
}

func TestClassifyError_GitNotFound_ExitCode127(t *testing.T) {
	// exit code 127 = "command not found" in shell, now correctly classified as GitNotFoundError
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 127,
		Stderr:   "sh: git: command not found",
	}
	err := classifyError("status", result)
	_, ok := err.(*GitNotFoundError)
	assert.True(t, ok, "expected GitNotFoundError, got %T", err)
}

func TestClassifyError_GitNotFound_CommandNotFound(t *testing.T) {
	// "command not found" message → GitNotFoundError
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 1,
		Stderr:   "bash: git: command not found",
	}
	err := classifyError("status", result)
	_, ok := err.(*GitNotFoundError)
	assert.True(t, ok, "expected GitNotFoundError, got %T", err)
}

func TestClassifyError_AuthorizationFailed(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: Authorization failed for 'https://github.com/user/repo.git'",
	}
	err := classifyError("push", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_AccessDenied(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "ERROR: access denied or repository not exported: /user/repo.git",
	}
	err := classifyError("clone", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_HTTP403(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 128,
		Stderr:   "fatal: repository 'https://github.com/user/repo.git/' not found\nerror: 403",
	}
	err := classifyError("push", result)
	_, ok := err.(*GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestClassifyError_GenericError(t *testing.T) {
	result := &command.CommandResult{
		Success:  false,
		ExitCode: 1,
		Stderr:   "error: pathspec 'nonexistent' did not match any file(s) known to git",
	}
	err := classifyError("checkout", result)
	_, ok := err.(*GitError)
	assert.True(t, ok, "expected GitError, got %T", err)
	// Should NOT be a specialized error type
	_, isAuth := err.(*GitAuthError)
	_, isNotRepo := err.(*GitNotARepoError)
	_, isConflict := err.(*GitConflictError)
	_, isNotFound := err.(*GitNotFoundError)
	assert.False(t, isAuth)
	assert.False(t, isNotRepo)
	assert.False(t, isConflict)
	assert.False(t, isNotFound)
}

func TestClassifyError_Success(t *testing.T) {
	result := &command.CommandResult{
		Success:  true,
		ExitCode: 0,
		Stdout:   "On branch main",
	}
	err := classifyError("status", result)
	assert.Nil(t, err)
}

// ==================== GitError Interface Tests ====================

func TestGitError_Error(t *testing.T) {
	err := &GitError{
		Message:  "git push failed",
		ExitCode: 128,
		Stderr:   "fatal: error",
	}
	assert.Equal(t, "git push failed (exit code 128)", err.Error())
}

func TestGitAuthError_Error(t *testing.T) {
	err := &GitAuthError{
		GitError: GitError{
			Message:  "authentication failed",
			ExitCode: 128,
			Stderr:   "fatal: Authentication failed",
		},
	}
	assert.Contains(t, err.Error(), "authentication failed")
}

// ==================== GitStatusResult Convenience Methods Tests ====================

func TestGitStatusResult_IsClean(t *testing.T) {
	result := &GitStatusResult{Files: []GitFileStatus{}}
	assert.True(t, result.IsClean())
	assert.False(t, result.HasChanges())
}

func TestGitStatusResult_HasChanges(t *testing.T) {
	result := &GitStatusResult{
		Files: []GitFileStatus{
			{Path: "file.txt", Status: "modified", Staged: true},
		},
	}
	assert.False(t, result.IsClean())
	assert.True(t, result.HasChanges())
}

func TestGitStatusResult_HasStaged(t *testing.T) {
	result := &GitStatusResult{
		Files: []GitFileStatus{
			{Path: "file.txt", Status: "modified", Staged: true},
		},
	}
	assert.True(t, result.HasStaged())
	assert.Equal(t, 1, result.StagedCount())
}

func TestGitStatusResult_HasUntracked(t *testing.T) {
	result := &GitStatusResult{
		Files: []GitFileStatus{
			{Path: "new.txt", Status: "untracked", Staged: false},
		},
	}
	assert.True(t, result.HasUntracked())
	assert.Equal(t, 1, result.UntrackedCount())
}

func TestGitStatusResult_HasConflicts(t *testing.T) {
	result := &GitStatusResult{
		Files: []GitFileStatus{
			{Path: "conflict.txt", Status: "conflict", Staged: false},
		},
	}
	assert.True(t, result.HasConflicts())
	assert.Equal(t, 1, result.ConflictCount())
}

func TestGitStatusResult_Counts(t *testing.T) {
	result := &GitStatusResult{
		Files: []GitFileStatus{
			{Path: "staged.txt", Status: "modified", Staged: true},
			{Path: "unstaged.txt", Status: "modified", Staged: false},
			{Path: "untracked.txt", Status: "untracked", Staged: false},
			{Path: "conflict.txt", Status: "conflict", Staged: false},
			{Path: "added.txt", Status: "added", Staged: true},
		},
	}
	assert.Equal(t, 5, result.TotalCount())
	assert.Equal(t, 2, result.StagedCount())    // staged.txt + added.txt
	assert.Equal(t, 2, result.UnstagedCount())  // unstaged.txt + conflict.txt (not untracked)
	assert.Equal(t, 1, result.UntrackedCount()) // untracked.txt
	assert.Equal(t, 1, result.ConflictCount())  // conflict.txt
}
