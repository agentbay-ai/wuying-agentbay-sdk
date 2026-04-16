package git

// GitCloneResult represents the result of a git clone operation.
type GitCloneResult struct {
	Path string
}

// GitInitResult represents the result of a git init operation.
type GitInitResult struct {
	Path string
}

// GitCommitResult represents the result of a git commit operation.
type GitCommitResult struct {
	CommitHash string
}

// GitFileStatus represents the status of a single file in the working tree.
type GitFileStatus struct {
	Path           string
	Status         string // Combined status: "added", "modified", "deleted", "renamed", "copied", "typechange", "untracked", "conflict", "unknown"
	IndexStatus    string // X in porcelain status output (' '=unmodified, M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked)
	WorkTreeStatus string // Y in porcelain status output (' '=unmodified, M=modified, A=added, D=deleted, R=renamed, C=copied, U=unmerged, ?=untracked)
	Staged         bool
	RenamedFrom    string
}

// GitStatusResult represents the result of a git status operation.
type GitStatusResult struct {
	CurrentBranch string
	Upstream      string
	Ahead         int
	Behind        int
	Detached      bool
	Files         []GitFileStatus
}

// IsClean returns true if there are no changes in the working tree.
func (s *GitStatusResult) IsClean() bool {
	return len(s.Files) == 0
}

// HasChanges returns true if there are any changes (staged or unstaged).
func (s *GitStatusResult) HasChanges() bool {
	return len(s.Files) > 0
}

// HasStaged returns true if there are staged changes.
func (s *GitStatusResult) HasStaged() bool {
	return s.StagedCount() > 0
}

// HasUntracked returns true if there are untracked files.
func (s *GitStatusResult) HasUntracked() bool {
	return s.UntrackedCount() > 0
}

// HasConflicts returns true if there are merge/rebase conflicts.
func (s *GitStatusResult) HasConflicts() bool {
	return s.ConflictCount() > 0
}

// TotalCount returns the total number of changed files.
func (s *GitStatusResult) TotalCount() int {
	return len(s.Files)
}

// StagedCount returns the number of staged files.
func (s *GitStatusResult) StagedCount() int {
	count := 0
	for _, file := range s.Files {
		if file.Staged {
			count++
		}
	}
	return count
}

// UnstagedCount returns the number of unstaged files.
func (s *GitStatusResult) UnstagedCount() int {
	count := 0
	for _, file := range s.Files {
		if !file.Staged && file.Status != "untracked" {
			count++
		}
	}
	return count
}

// UntrackedCount returns the number of untracked files.
func (s *GitStatusResult) UntrackedCount() int {
	count := 0
	for _, file := range s.Files {
		if file.Status == "untracked" {
			count++
		}
	}
	return count
}

// ConflictCount returns the number of files with conflicts.
func (s *GitStatusResult) ConflictCount() int {
	count := 0
	for _, file := range s.Files {
		if file.Status == "conflict" {
			count++
		}
	}
	return count
}

// GitLogEntry represents a single commit in the git log.
type GitLogEntry struct {
	Hash        string
	ShortHash   string
	AuthorName  string
	AuthorEmail string
	Date        string // ISO 8601 format: 2006-01-02T15:04:05Z07:00
	Message     string
}

// GitLogResult represents the result of a git log operation.
type GitLogResult struct {
	Entries []GitLogEntry
}

// GitBranchInfo represents information about a git branch.
type GitBranchInfo struct {
	Name      string
	IsCurrent bool
}

// GitBranchListResult represents the result of a git branch list operation.
type GitBranchListResult struct {
	Branches []GitBranchInfo
	Current  string
}
