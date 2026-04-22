package interfaces

import "github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/git"

//go:generate mockgen -destination=../../../tests/pkg/unit/mock/mock_git.go -package=mock github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/interface GitInterface

// GitInterface defines the interface for git operations
type GitInterface interface {
	// Clone clones a git repository.
	Clone(url string, opts ...git.CloneOption) (*git.GitCloneResult, error)

	// Init initializes a new git repository.
	Init(path string, opts ...git.InitOption) (*git.GitInitResult, error)

	// Add adds files to the staging area.
	Add(repoPath string, opts ...git.AddOption) error

	// Commit creates a new commit.
	Commit(repoPath string, message string, opts ...git.CommitOption) (*git.GitCommitResult, error)

	// Status shows the working tree status.
	Status(repoPath string, opts ...git.StatusOption) (*git.GitStatusResult, error)

	// Log shows the commit log.
	Log(repoPath string, opts ...git.LogOption) (*git.GitLogResult, error)

	// ListBranches lists all branches.
	ListBranches(repoPath string, opts ...git.BranchListOption) (*git.GitBranchListResult, error)

	// CreateBranch creates a new branch.
	CreateBranch(repoPath string, branch string, opts ...git.BranchCreateOption) error

	// CheckoutBranch switches to a branch.
	CheckoutBranch(repoPath string, branch string, opts ...git.CheckoutOption) error

	// DeleteBranch deletes a branch.
	DeleteBranch(repoPath string, branch string, opts ...git.BranchDeleteOption) error

	// RemoteAdd adds a remote repository.
	RemoteAdd(repoPath string, name string, url string, opts ...git.RemoteAddOption) error

	// RemoteGet gets the URL of a remote repository.
	RemoteGet(repoPath string, name string, opts ...git.RemoteGetOption) (string, error)

	// Reset resets the current HEAD to the specified state.
	Reset(repoPath string, opts ...git.ResetOption) error

	// Restore restores working tree files.
	Restore(repoPath string, paths []string, opts ...git.RestoreOption) error

	// Pull fetches from and integrates with another repository.
	Pull(repoPath string, opts ...git.PullOption) error

	// ConfigureUser configures user name and email.
	ConfigureUser(repoPath string, name string, email string, opts ...git.ConfigOption) error

	// SetConfig sets a configuration value.
	SetConfig(repoPath string, key string, value string, opts ...git.ConfigOption) error

	// GetConfig gets a configuration value.
	GetConfig(repoPath string, key string, opts ...git.ConfigOption) (string, error)
}
