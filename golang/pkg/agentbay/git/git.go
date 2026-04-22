package git

import (
	"fmt"
	neturl "net/url"
	"regexp"
	"strconv"
	"strings"
	"sync"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
)

var defaultGitEnv = map[string]string{
	"GIT_TERMINAL_PROMPT": "0",
	"LC_ALL":              "C",
}

// Pre-compiled regex patterns (avoid recompiling on each call)
var (
	branchInfoPattern = regexp.MustCompile(`## ([^\s.]+)(?:\.\.\.([^\s]+))?(?: \[(.+)\])?`)
	aheadPattern      = regexp.MustCompile(`ahead (\d+)`)
	behindPattern     = regexp.MustCompile(`behind (\d+)`)
	commitHashPattern = regexp.MustCompile(`\[[\w/.-]+(?:\s+\([^)]+\))?\s+([a-f0-9]+)\]`)
)

const (
	// defaultGitTimeoutMs is the default timeout for git operations (30 seconds)
	defaultGitTimeoutMs = 30000
	// defaultCloneTimeoutMs is the default timeout for clone operations (5 minutes, as clone may download large repos)
	defaultCloneTimeoutMs = 300000
	// defaultPullTimeoutMs is the default timeout for pull/push operations (2 minutes, as network operations may be slow)
	defaultPullTimeoutMs = 120000
)

// Git handles git operations in the AgentBay cloud environment.
//
// This struct provides methods for common git operations such as clone, init,
// add, commit, push, pull, branch management, and more. It executes git commands
// in the remote session environment and handles errors appropriately.
type Git struct {
	command  *command.Command
	gitOnce  sync.Once
	gitError error
}

// NewGit creates a new Git instance.
//
// Parameters:
//   - cmd: The command executor to use for running git commands
//
// Returns:
//   - *Git: A new Git instance ready to perform git operations
func NewGit(cmd *command.Command) *Git {
	return &Git{command: cmd}
}

// ==================== Private Helper Methods ====================

// shellEscape escapes a shell argument using single quotes (safest for shell).
func shellEscape(arg string) string {
	return "'" + strings.ReplaceAll(arg, "'", "'\\''") + "'"
}

// buildGitCommand builds a git command string.
func buildGitCommand(args []string, repoPath string) string {
	cmdParts := []string{"git"}
	if repoPath != "" {
		cmdParts = append(cmdParts, "-C", shellEscape(repoPath))
	}
	for _, arg := range args {
		cmdParts = append(cmdParts, shellEscape(arg))
	}
	return strings.Join(cmdParts, " ")
}

// runGit executes a git command.
func (g *Git) runGit(args []string, repoPath string, timeoutMs int) (*command.CommandResult, error) {
	cmd := buildGitCommand(args, repoPath)
	return g.runShell(cmd, timeoutMs)
}

// runShell executes a shell command.
func (g *Git) runShell(cmd string, timeoutMs int) (*command.CommandResult, error) {
	if timeoutMs <= 0 {
		timeoutMs = defaultGitTimeoutMs
	}
	return g.command.ExecuteCommand(cmd, command.WithTimeoutMs(timeoutMs), command.WithEnvs(defaultGitEnv))
}

// ensureGitAvailable checks if git is installed (thread-safe via sync.Once).
func (g *Git) ensureGitAvailable() error {
	g.gitOnce.Do(func() {
		result, err := g.runShell("git --version", 5000)
		if err != nil {
			g.gitError = err
			return
		}

		if !result.Success {
			g.gitError = &GitNotFoundError{
				GitError: GitError{
					Message:  "git is not installed or not available in PATH",
					ExitCode: result.ExitCode,
					Stderr:   result.Stderr,
				},
			}
		}
	})
	return g.gitError
}

// classifyError classifies git errors based on exit code and stderr.
func classifyError(operation string, result *command.CommandResult) error {
	if result.Success {
		return nil
	}

	stderr := strings.ToLower(result.Stderr)

	// Check for git not found (exit code 127 = command not found)
	if result.ExitCode == 127 ||
		strings.Contains(stderr, "command not found") ||
		strings.Contains(stderr, "git: not found") {
		return &GitNotFoundError{
			GitError: GitError{
				Message:  fmt.Sprintf("git is not installed or not found in PATH during %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}

	// Check for authentication errors
	if strings.Contains(stderr, "authentication") ||
		strings.Contains(stderr, "permission denied") ||
		strings.Contains(stderr, "could not read username") ||
		strings.Contains(stderr, "invalid credentials") ||
		strings.Contains(stderr, "authorization failed") ||
		strings.Contains(stderr, "access denied") ||
		strings.Contains(stderr, "403") {
		return &GitAuthError{
			GitError: GitError{
				Message:  fmt.Sprintf("git authentication failed for %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}

	// Check for not a repository errors
	stdout := strings.ToLower(result.Stdout)
	if strings.Contains(stderr, "not a git repository") ||
		strings.Contains(stderr, "does not appear to be a git repository") ||
		strings.Contains(stdout, "not a git repository") {
		return &GitNotARepoError{
			GitError: GitError{
				Message:  fmt.Sprintf("not a git repository for %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}

	// Check for conflict errors (use original case stderr for precise matching)
	if strings.Contains(result.Stderr, "CONFLICT") ||
		strings.Contains(result.Stderr, "Merge conflict") ||
		strings.Contains(stderr, "automatic merge failed") {
		return &GitConflictError{
			GitError: GitError{
				Message:  fmt.Sprintf("merge/rebase conflict during %s", operation),
				ExitCode: result.ExitCode,
				Stderr:   result.Stderr,
			},
		}
	}

	return &GitError{
		Message:  fmt.Sprintf("git %s failed", operation),
		ExitCode: result.ExitCode,
		Stderr:   result.Stderr,
	}
}

// deriveRepoDirFromURL extracts repository directory name from URL.
func deriveRepoDirFromURL(rawURL string) string {
	rawURL = strings.TrimSuffix(rawURL, "/")
	rawURL = strings.TrimSuffix(rawURL, ".git")
	// Handle URL-encoded characters (e.g., %20)
	if decoded, err := neturl.PathUnescape(rawURL); err == nil {
		rawURL = decoded
	}
	// Handle both / and : separators (SSH URLs use git@host:user/repo format)
	lastSlash := strings.LastIndex(rawURL, "/")
	lastColon := strings.LastIndex(rawURL, ":")
	sep := lastSlash
	if lastColon > sep {
		sep = lastColon
	}
	if sep >= 0 && sep < len(rawURL)-1 {
		return rawURL[sep+1:]
	}
	return "repo"
}

// deriveStatus derives combined status from index and worktree status.
func deriveStatus(indexStatus, workTreeStatus string) string {
	switch {
	case indexStatus == "?" && workTreeStatus == "?":
		return "untracked"
	case indexStatus == "U" || workTreeStatus == "U" || (indexStatus == "A" && workTreeStatus == "A"):
		return "conflict"
	case indexStatus == "R":
		return "renamed"
	case indexStatus == "C":
		return "copied"
	case indexStatus == "A":
		return "added"
	case indexStatus == "D" || workTreeStatus == "D":
		return "deleted"
	case indexStatus == "T" || workTreeStatus == "T":
		return "typechange"
	case indexStatus == "M" || workTreeStatus == "M":
		return "modified"
	default:
		return "unknown"
	}
}

// parseGitStatus parses git status --porcelain -b output.
// The first line starting with "## " contains branch info.
func parseGitStatus(output string) *GitStatusResult {
	result := &GitStatusResult{
		Files: []GitFileStatus{},
	}

	lines := strings.Split(strings.TrimSpace(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}

		// Parse branch info line (## branch...upstream [ahead N, behind M])
		if strings.HasPrefix(line, "## ") {
			// Handle "## No commits yet on <branch>" format
			if strings.HasPrefix(line, "## No commits yet on ") {
				result.CurrentBranch = strings.TrimPrefix(line, "## No commits yet on ")
				continue
			}
			// Handle "## Initial commit on <branch>" format (older Git versions)
			if strings.HasPrefix(line, "## Initial commit on ") {
				result.CurrentBranch = strings.TrimPrefix(line, "## Initial commit on ")
				continue
			}
			matches := branchInfoPattern.FindStringSubmatch(line)
			if len(matches) > 1 {
				result.CurrentBranch = matches[1]
				if len(matches) > 2 && matches[2] != "" {
					result.Upstream = matches[2]
				}
				if len(matches) > 3 && matches[3] != "" {
					trackingInfo := matches[3]
					aheadMatches := aheadPattern.FindStringSubmatch(trackingInfo)
					if len(aheadMatches) > 1 {
						result.Ahead, _ = strconv.Atoi(aheadMatches[1])
					}
					behindMatches := behindPattern.FindStringSubmatch(trackingInfo)
					if len(behindMatches) > 1 {
						result.Behind, _ = strconv.Atoi(behindMatches[1])
					}
				}
				result.Detached = matches[1] == "HEAD"
			}
			continue
		}

		if len(line) < 4 {
			continue
		}

		indexStatus := string(line[0])
		workTreeStatus := string(line[1])
		path := strings.TrimSpace(line[3:])

		status := deriveStatus(indexStatus, workTreeStatus)
		staged := indexStatus != " " && indexStatus != "?"

		renamedFrom := ""
		if indexStatus == "R" {
			parts := strings.SplitN(path, " -> ", 2)
			if len(parts) == 2 {
				renamedFrom = parts[0]
				path = parts[1]
			}
		}

		result.Files = append(result.Files, GitFileStatus{
			Path:           path,
			Status:         status,
			IndexStatus:    indexStatus,
			WorkTreeStatus: workTreeStatus,
			Staged:         staged,
			RenamedFrom:    renamedFrom,
		})
	}

	return result
}

// parseGitLog parses git log output using \x00/\x01 separator format.
// Expected format: %H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00
func parseGitLog(output string) *GitLogResult {
	result := &GitLogResult{
		Entries: []GitLogEntry{},
	}

	output = strings.TrimSpace(output)
	if output == "" {
		return result
	}

	// Split entries by \x00 (null byte)
	entries := strings.Split(output, "\x00")
	for _, entry := range entries {
		entry = strings.TrimSpace(entry)
		if entry == "" {
			continue
		}

		// Split fields by \x01 (SOH byte)
		fields := strings.Split(entry, "\x01")
		if len(fields) < 6 {
			continue
		}

		hash := strings.TrimSpace(fields[0])
		shortHash := strings.TrimSpace(fields[1])
		if shortHash == "" && len(hash) >= 7 {
			shortHash = hash[:7]
		}

		result.Entries = append(result.Entries, GitLogEntry{
			Hash:        hash,
			ShortHash:   shortHash,
			AuthorName:  strings.TrimSpace(fields[2]),
			AuthorEmail: strings.TrimSpace(fields[3]),
			Date:        strings.TrimSpace(fields[4]),
			Message:     strings.TrimSpace(fields[5]),
		})
	}

	return result
}

// parseGitBranches parses git branch --format=%(refname:short)\t%(HEAD) output.
// Each line is: branch_name\t* (current) or branch_name\t  (other).
func parseGitBranches(output string) *GitBranchListResult {
	result := &GitBranchListResult{
		Branches: []GitBranchInfo{},
	}

	lines := strings.Split(strings.TrimSpace(output), "\n")
	for _, line := range lines {
		if line == "" {
			continue
		}

		parts := strings.SplitN(line, "\t", 2)
		name := strings.TrimSpace(parts[0])
		if name == "" {
			continue
		}

		isCurrent := len(parts) > 1 && strings.TrimSpace(parts[1]) == "*"
		if isCurrent {
			result.Current = name
		}

		result.Branches = append(result.Branches, GitBranchInfo{
			Name:      name,
			IsCurrent: isCurrent,
		})
	}

	return result
}

// ==================== Functional Options for Clone ====================

type cloneOptions struct {
	path      string
	branch    string
	depth     int
	timeoutMs int
}

// CloneOption configures the Clone operation.
type CloneOption func(*cloneOptions)

// WithClonePath sets the destination path for clone.
func WithClonePath(path string) CloneOption {
	return func(opts *cloneOptions) {
		opts.path = path
	}
}

// WithCloneBranch sets the branch to clone.
func WithCloneBranch(branch string) CloneOption {
	return func(opts *cloneOptions) {
		opts.branch = branch
	}
}

// WithCloneDepth sets the depth for shallow clone.
func WithCloneDepth(depth int) CloneOption {
	return func(opts *cloneOptions) {
		opts.depth = depth
	}
}

// WithCloneTimeout sets the timeout for clone operation.
func WithCloneTimeout(timeoutMs int) CloneOption {
	return func(opts *cloneOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Clone clones a git repository.
func (g *Git) Clone(url string, opts ...CloneOption) (*GitCloneResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &cloneOptions{
		timeoutMs: defaultCloneTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"clone"}
	if options.branch != "" {
		args = append(args, "--branch", options.branch, "--single-branch")
	}
	if options.depth > 0 {
		args = append(args, "--depth", strconv.Itoa(options.depth))
	}
	args = append(args, url)

	if options.path != "" {
		args = append(args, options.path)
	}

	result, err := g.runGit(args, "", options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("clone", result)
	}

	path := options.path
	if path == "" {
		path = deriveRepoDirFromURL(url)
	}

	return &GitCloneResult{Path: path}, nil
}

// ==================== Functional Options for Init ====================

type initOptions struct {
	initialBranch string
	bare          bool
	timeoutMs     int
}

// InitOption configures the Init operation.
type InitOption func(*initOptions)

// WithInitBranch sets the initial branch name.
func WithInitBranch(branch string) InitOption {
	return func(opts *initOptions) {
		opts.initialBranch = branch
	}
}

// WithInitBare creates a bare repository.
func WithInitBare() InitOption {
	return func(opts *initOptions) {
		opts.bare = true
	}
}

// WithInitTimeout sets the timeout for init operation.
func WithInitTimeout(timeoutMs int) InitOption {
	return func(opts *initOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Init initializes a new git repository.
func (g *Git) Init(path string, opts ...InitOption) (*GitInitResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &initOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"init"}
	if options.initialBranch != "" {
		args = append(args, "--initial-branch", options.initialBranch)
	}
	if options.bare {
		args = append(args, "--bare")
	}

	args = append(args, path)
	result, err := g.runGit(args, "", options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("init", result)
	}

	return &GitInitResult{Path: path}, nil
}

// ==================== Functional Options for Add ====================

type addOptions struct {
	paths     []string
	all       bool
	timeoutMs int
}

// AddOption configures the Add operation.
//
// Parameters:
//   - opts: pointer to addOptions struct to configure
type AddOption func(*addOptions)

// WithAddPaths sets the paths to add.
//
// Parameters:
//   - paths: list of file paths to stage
//
// Returns:
//   - AddOption: functional option to configure Add operation
func WithAddPaths(paths []string) AddOption {
	return func(opts *addOptions) {
		opts.paths = paths
	}
}

// WithAddAll adds all files.
//
// Returns:
//   - AddOption: functional option to configure Add operation
func WithAddAll() AddOption {
	return func(opts *addOptions) {
		opts.all = true
	}
}

// WithAddTimeout sets the timeout for add operation.
//
// Parameters:
//   - timeoutMs: timeout in milliseconds
//
// Returns:
//   - AddOption: functional option to configure Add operation
func WithAddTimeout(timeoutMs int) AddOption {
	return func(opts *addOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Add adds files to the staging area.
//
// Parameters:
//   - repoPath: absolute path to the git repository
//   - opts: optional configuration functions for the Add operation
//
// Returns:
//   - error: returns an error if the operation fails, nil otherwise
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.Add("/home/user/my-project")
func (g *Git) Add(repoPath string, opts ...AddOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &addOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"add"}
	if len(options.paths) > 0 {
		// Specific files take priority (matches TypeScript behavior)
		args = append(args, "--")
		args = append(args, options.paths...)
	} else if options.all {
		args = append(args, "--all")
	} else {
		// Default: stage all changes (matches TypeScript/E2B behavior)
		args = append(args, "-A")
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("add", result)
	}

	return nil
}

// ==================== Functional Options for Commit ====================

type commitOptions struct {
	message     string
	authorName  string
	authorEmail string
	allowEmpty  bool
	timeoutMs   int
}

// CommitOption configures the Commit operation.
//
// Parameters:
//   - opts: pointer to commitOptions struct to configure
type CommitOption func(*commitOptions)

// WithCommitAllowEmpty allows empty commits.
//
// Returns:
//   - CommitOption: functional option to configure Commit operation
func WithCommitAllowEmpty() CommitOption {
	return func(opts *commitOptions) {
		opts.allowEmpty = true
	}
}

// WithCommitAuthorName sets the author name for the commit (via git -c user.name=...).
//
// Parameters:
//   - name: author name for the commit
//
// Returns:
//   - CommitOption: functional option to configure Commit operation
func WithCommitAuthorName(name string) CommitOption {
	return func(opts *commitOptions) {
		opts.authorName = name
	}
}

// WithCommitAuthorEmail sets the author email for the commit (via git -c user.email=...).
//
// Parameters:
//   - email: author email for the commit
//
// Returns:
//   - CommitOption: functional option to configure Commit operation
func WithCommitAuthorEmail(email string) CommitOption {
	return func(opts *commitOptions) {
		opts.authorEmail = email
	}
}

// WithCommitTimeout sets the timeout for commit operation.
//
// Parameters:
//   - timeoutMs: timeout in milliseconds
//
// Returns:
//   - CommitOption: functional option to configure Commit operation
func WithCommitTimeout(timeoutMs int) CommitOption {
	return func(opts *commitOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Commit creates a new commit.
//
// Parameters:
//   - repoPath: absolute path to the git repository
//   - message: commit message
//   - opts: optional configuration functions for the Commit operation
//
// Returns:
//   - *GitCommitResult: result containing the commit hash
//   - error: returns an error if the operation fails, nil otherwise
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	commitResult, _ := result.Session.Git.Commit("/home/user/my-project", "Initial commit")
func (g *Git) Commit(repoPath string, message string, opts ...CommitOption) (*GitCommitResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &commitOptions{
		message:   message,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	// Build command manually to support -c global args before the "commit" subcommand.
	// Command format: git -C <path> [-c user.name=xxx] [-c user.email=xxx] commit -m "msg" [flags]
	cmdParts := []string{"git"}
	if repoPath != "" {
		cmdParts = append(cmdParts, "-C", shellEscape(repoPath))
	}
	// -c parameters must come BEFORE the 'commit' subcommand (git requirement)
	if options.authorName != "" {
		cmdParts = append(cmdParts, "-c", shellEscape(fmt.Sprintf("user.name=%s", options.authorName)))
	}
	if options.authorEmail != "" {
		cmdParts = append(cmdParts, "-c", shellEscape(fmt.Sprintf("user.email=%s", options.authorEmail)))
	}

	subArgs := []string{"commit"}
	if options.allowEmpty {
		subArgs = append(subArgs, "--allow-empty")
	}
	subArgs = append(subArgs, "-m", options.message)
	for _, arg := range subArgs {
		cmdParts = append(cmdParts, shellEscape(arg))
	}

	cmd := strings.Join(cmdParts, " ")
	result, err := g.runShell(cmd, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("commit", result)
	}

	// Extract commit hash from output
	matches := commitHashPattern.FindStringSubmatch(result.Stdout)
	if len(matches) > 1 {
		return &GitCommitResult{CommitHash: matches[1]}, nil
	}

	// Fallback: get the latest commit hash (this should rarely happen)
	hashResult, err := g.runGit([]string{"rev-parse", "HEAD"}, repoPath, 5000)
	if err == nil && hashResult.Success {
		return &GitCommitResult{CommitHash: strings.TrimSpace(hashResult.Stdout)}, nil
	}

	return &GitCommitResult{CommitHash: ""}, nil
}

// ==================== Functional Options for Status ====================

type statusOptions struct {
	timeoutMs int
}

// StatusOption configures the Status operation.
//
// Parameters:
//   - opts: pointer to statusOptions struct to configure
type StatusOption func(*statusOptions)

// WithStatusTimeout sets the timeout for status operation.
//
// Parameters:
//   - timeoutMs: timeout in milliseconds
//
// Returns:
//   - StatusOption: functional option to configure Status operation
func WithStatusTimeout(timeoutMs int) StatusOption {
	return func(opts *statusOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Status shows the working tree status.
//
// Parameters:
//   - repoPath: absolute path to the git repository
//   - opts: optional configuration functions for the Status operation
//
// Returns:
//   - *GitStatusResult: result containing branch, staged, unstaged, and untracked files
//   - error: returns an error if the operation fails, nil otherwise
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	statusResult, _ := result.Session.Git.Status("/home/user/my-project")
func (g *Git) Status(repoPath string, opts ...StatusOption) (*GitStatusResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &statusOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	// Get porcelain status with branch info in a single command
	result, err := g.runGit([]string{"status", "--porcelain=1", "-b"}, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("status", result)
	}

	return parseGitStatus(result.Stdout), nil
}

// ==================== Functional Options for Log ====================

type logOptions struct {
	maxCount  int
	timeoutMs int
}

// LogOption configures the Log operation.
//
// Parameters:
//   - opts: pointer to logOptions struct to configure
type LogOption func(*logOptions)

// WithLogMaxCount sets the maximum number of commits.
//
// Parameters:
//   - count: maximum number of commits to return
//
// Returns:
//   - LogOption: functional option to configure Log operation
func WithLogMaxCount(count int) LogOption {
	return func(opts *logOptions) {
		opts.maxCount = count
	}
}

// WithLogTimeout sets the timeout for log operation.
//
// Parameters:
//   - timeoutMs: timeout in milliseconds
//
// Returns:
//   - LogOption: functional option to configure Log operation
func WithLogTimeout(timeoutMs int) LogOption {
	return func(opts *logOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Log shows the commit log.
//
// Parameters:
//   - repoPath: absolute path to the git repository
//   - opts: optional configuration functions for the Log operation
//
// Returns:
//   - *GitLogResult: result containing list of commits with hash, author, date, and message
//   - error: returns an error if the operation fails, nil otherwise
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	logResult, _ := result.Session.Git.Log("/home/user/my-project", git.WithLogMaxCount(10))
func (g *Git) Log(repoPath string, opts ...LogOption) (*GitLogResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &logOptions{
		maxCount:  0,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"log"}
	if options.maxCount > 0 {
		args = append(args, "-n", strconv.Itoa(options.maxCount))
	}
	args = append(args, "--format=%H%x01%h%x01%an%x01%ae%x01%aI%x01%s%x00")

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("log", result)
	}

	return parseGitLog(result.Stdout), nil
}

// ==================== Functional Options for ListBranches ====================

type branchListOptions struct {
	remote    bool
	timeoutMs int
}

// BranchListOption configures the ListBranches operation.
type BranchListOption func(*branchListOptions)

// WithBranchListRemote lists remote branches.
func WithBranchListRemote() BranchListOption {
	return func(opts *branchListOptions) {
		opts.remote = true
	}
}

// WithBranchListTimeout sets the timeout for list branches operation.
func WithBranchListTimeout(timeoutMs int) BranchListOption {
	return func(opts *branchListOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// ListBranches lists all branches in the repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - opts: optional configuration functions
//
// Returns:
//   - *GitBranchListResult: list of branches with HEAD indicator
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	branches, _ := result.Session.Git.ListBranches("/home/user/my-project")
func (g *Git) ListBranches(repoPath string, opts ...BranchListOption) (*GitBranchListResult, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return nil, err
	}

	options := &branchListOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	// Use structured format output for reliable parsing (matches TS/Python)
	args := []string{"branch", "--format=%(refname:short)\t%(HEAD)"}
	if options.remote {
		args = append(args, "-r")
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return nil, err
	}

	if !result.Success {
		return nil, classifyError("branch", result)
	}

	return parseGitBranches(result.Stdout), nil
}

// ==================== Functional Options for CreateBranch ====================

type branchCreateOptions struct {
	checkout  bool
	timeoutMs int
}

// BranchCreateOption configures the CreateBranch operation.
type BranchCreateOption func(*branchCreateOptions)

// WithBranchCreateCheckout sets whether to checkout the new branch after creation.
// Default is true (creates and switches to the new branch using "checkout -b").
// Set to false to only create the branch without switching (using "branch").
func WithBranchCreateCheckout(checkout bool) BranchCreateOption {
	return func(opts *branchCreateOptions) {
		opts.checkout = checkout
	}
}

// WithBranchCreateTimeout sets the timeout for create branch operation.
func WithBranchCreateTimeout(timeoutMs int) BranchCreateOption {
	return func(opts *branchCreateOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// CreateBranch creates a new branch in the repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - branch: name of the branch to create
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.CreateBranch("/home/user/my-project", "feature/new")
func (g *Git) CreateBranch(repoPath string, branch string, opts ...BranchCreateOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &branchCreateOptions{
		checkout:  true,
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	var args []string
	if options.checkout {
		// Create and switch to the new branch (default behavior, matches TS/Python)
		args = []string{"checkout", "-b", branch}
	} else {
		// Only create the branch without switching
		args = []string{"branch", branch}
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("branch", result)
	}

	return nil
}

// ==================== Functional Options for Checkout ====================

type checkoutOptions struct {
	timeoutMs int
}

// CheckoutOption configures the Checkout operation.
type CheckoutOption func(*checkoutOptions)

// WithCheckoutTimeout sets the timeout for checkout operation.
func WithCheckoutTimeout(timeoutMs int) CheckoutOption {
	return func(opts *checkoutOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// CheckoutBranch switches to the specified branch.
//
// Parameters:
//   - repoPath: path to the git repository
//   - branch: name of the branch to switch to
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.CheckoutBranch("/home/user/my-project", "main")
func (g *Git) CheckoutBranch(repoPath string, branch string, opts ...CheckoutOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &checkoutOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"checkout", branch}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("checkout", result)
	}

	return nil
}

// ==================== Functional Options for DeleteBranch ====================

type branchDeleteOptions struct {
	force     bool
	timeoutMs int
}

// BranchDeleteOption configures the DeleteBranch operation.
type BranchDeleteOption func(*branchDeleteOptions)

// WithBranchDeleteForce forces branch deletion even if unmerged.
func WithBranchDeleteForce() BranchDeleteOption {
	return func(opts *branchDeleteOptions) {
		opts.force = true
	}
}

// WithBranchDeleteTimeout sets the timeout for delete branch operation.
func WithBranchDeleteTimeout(timeoutMs int) BranchDeleteOption {
	return func(opts *branchDeleteOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// DeleteBranch deletes a branch from the repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - branch: name of the branch to delete
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.DeleteBranch("/home/user/my-project", "feature/old")
func (g *Git) DeleteBranch(repoPath string, branch string, opts ...BranchDeleteOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &branchDeleteOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"branch"}
	if options.force {
		args = append(args, "-D")
	} else {
		args = append(args, "-d")
	}
	args = append(args, branch)

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("branch", result)
	}

	return nil
}

// ==================== Functional Options for RemoteAdd ====================

type remoteAddOptions struct {
	fetch     bool
	overwrite bool
	timeoutMs int
}

// RemoteAddOption configures the RemoteAdd operation.
type RemoteAddOption func(*remoteAddOptions)

// WithRemoteAddFetch fetches from the remote after adding it.
// Note: git remote add -f means "fetch after adding", not "force".
func WithRemoteAddFetch() RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.fetch = true
	}
}

// WithRemoteAddOverwrite enables idempotent mode: if remote already exists, update its URL.
// Uses "git remote add ... || git remote set-url ..." pattern.
func WithRemoteAddOverwrite() RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.overwrite = true
	}
}

// WithRemoteAddTimeout sets the timeout for remote add operation.
func WithRemoteAddTimeout(timeoutMs int) RemoteAddOption {
	return func(opts *remoteAddOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// RemoteAdd adds a remote repository to the local repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - name: name of the remote (e.g., "origin")
//   - url: URL of the remote repository
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.RemoteAdd("/home/user/my-project", "origin", "https://github.com/user/repo.git")
func (g *Git) RemoteAdd(repoPath string, name string, url string, opts ...RemoteAddOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &remoteAddOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	addArgs := []string{"remote", "add"}
	if options.fetch {
		addArgs = append(addArgs, "-f")
	}
	addArgs = append(addArgs, name, url)

	if !options.overwrite {
		// Simple mode: direct git remote add
		result, err := g.runGit(addArgs, repoPath, options.timeoutMs)
		if err != nil {
			return err
		}
		if !result.Success {
			return classifyError("remote", result)
		}
	} else {
		// Idempotent mode: add fails, fallback to set-url
		addCmd := buildGitCommand(addArgs, repoPath)
		setUrlCmd := buildGitCommand([]string{"remote", "set-url", name, url}, repoPath)
		cmd := addCmd + " || " + setUrlCmd
		if options.fetch {
			fetchCmd := buildGitCommand([]string{"fetch", name}, repoPath)
			cmd = "(" + cmd + ") && " + fetchCmd
		}
		result, err := g.runShell(cmd, options.timeoutMs)
		if err != nil {
			return err
		}
		if !result.Success {
			return classifyError("remote", result)
		}
	}

	return nil
}

// ==================== Functional Options for RemoteGet ====================

type remoteGetOptions struct {
	timeoutMs int
}

// RemoteGetOption configures the RemoteGet operation.
type RemoteGetOption func(*remoteGetOptions)

// WithRemoteGetTimeout sets the timeout for remote get operation.
func WithRemoteGetTimeout(timeoutMs int) RemoteGetOption {
	return func(opts *remoteGetOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// RemoteGet gets the URL of a remote repository.
// Returns empty string (not error) if the remote does not exist.
// Other errors (e.g. not a git repository) are returned as-is.
//
// Parameters:
//   - repoPath: path to the git repository
//   - name: name of the remote
//   - opts: optional configuration functions
//
// Returns:
//   - string: URL of the remote repository, or empty string if not found
//   - error: error if the operation fails (excluding "not found" case)
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	url, _ := result.Session.Git.RemoteGet("/home/user/my-project", "origin")
func (g *Git) RemoteGet(repoPath string, name string, opts ...RemoteGetOption) (string, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return "", err
	}

	options := &remoteGetOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"remote", "get-url", name}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return "", err
	}

	if !result.Success {
		stderr := strings.ToLower(result.Stderr)
		if strings.Contains(stderr, "no such remote") {
			return "", nil
		}
		return "", classifyError("remote_get", result)
	}

	return strings.TrimSpace(result.Stdout), nil
}

// ==================== Functional Options for Reset ====================

type resetOptions struct {
	mode      string // soft, mixed, hard
	commit    string
	paths     []string
	timeoutMs int
}

// ResetOption configures the Reset operation.
type ResetOption func(*resetOptions)

// WithResetSoft performs a soft reset (keeps changes staged).
func WithResetSoft() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "soft"
	}
}

// WithResetMixed performs a mixed reset (default, unstages changes).
func WithResetMixed() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "mixed"
	}
}

// WithResetHard performs a hard reset (discards all changes).
func WithResetHard() ResetOption {
	return func(opts *resetOptions) {
		opts.mode = "hard"
	}
}

// WithResetCommit sets the commit to reset to.
func WithResetCommit(commit string) ResetOption {
	return func(opts *resetOptions) {
		opts.commit = commit
	}
}

// WithResetPaths sets the paths to reset (for path-specific reset).
func WithResetPaths(paths []string) ResetOption {
	return func(opts *resetOptions) {
		opts.paths = paths
	}
}

// WithResetTimeout sets the timeout for reset operation.
func WithResetTimeout(timeoutMs int) ResetOption {
	return func(opts *resetOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Reset resets the current HEAD to the specified state.
//
// Parameters:
//   - repoPath: path to the git repository
//   - opts: optional configuration functions (must specify at least one mode or paths)
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.Reset("/home/user/my-project", git.WithResetHard())
func (g *Git) Reset(repoPath string, opts ...ResetOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &resetOptions{
		mode:      "",
		commit:    "",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"reset"}
	if len(options.paths) > 0 {
		// Pathspec mode: git reset [<commit>] -- <paths>
		// Mode flags (--soft/--mixed/--hard) are NOT allowed with pathspec.
		if options.commit != "" {
			args = append(args, options.commit)
		}
		args = append(args, "--")
		args = append(args, options.paths...)
	} else {
		// Tree-ish mode: git reset [--<mode>] [<commit>]
		mode := options.mode
		if mode == "" {
			mode = "mixed"
		}
		args = append(args, "--"+mode)
		commit := options.commit
		if commit == "" {
			commit = "HEAD"
		}
		args = append(args, commit)
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("reset", result)
	}

	return nil
}

// ==================== Functional Options for Restore ====================

type restoreOptions struct {
	staged    bool
	worktree  bool
	source    string
	timeoutMs int
}

// RestoreOption configures the Restore operation.
type RestoreOption func(*restoreOptions)

// WithRestoreStaged restores staged files to their original state.
func WithRestoreStaged() RestoreOption {
	return func(opts *restoreOptions) {
		opts.staged = true
	}
}

// WithRestoreWorktree restores working tree files (explicit flag).
func WithRestoreWorktree() RestoreOption {
	return func(opts *restoreOptions) {
		opts.worktree = true
	}
}

// WithRestoreSource sets the source tree to restore from.
func WithRestoreSource(source string) RestoreOption {
	return func(opts *restoreOptions) {
		opts.source = source
	}
}

// WithRestoreTimeout sets the timeout for restore operation.
func WithRestoreTimeout(timeoutMs int) RestoreOption {
	return func(opts *restoreOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Restore restores working tree files to their original state.
//
// Parameters:
//   - repoPath: path to the git repository
//   - paths: list of file paths to restore (at least one required)
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.Restore("/home/user/my-project", []string{"file.txt"})
func (g *Git) Restore(repoPath string, paths []string, opts ...RestoreOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &restoreOptions{
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	// Validate: at least one path must be specified
	if len(paths) == 0 {
		return fmt.Errorf("git restore requires at least one path")
	}

	// Default worktree logic: when neither staged nor worktree is set, default to --worktree
	resolvedStaged := options.staged
	resolvedWorktree := options.worktree
	if !resolvedStaged && !resolvedWorktree {
		resolvedWorktree = true
	}

	args := []string{"restore"}
	if resolvedWorktree {
		args = append(args, "--worktree")
	}
	if resolvedStaged {
		args = append(args, "--staged")
	}
	if options.source != "" {
		args = append(args, "--source", options.source)
	}
	args = append(args, "--")
	args = append(args, paths...)

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("restore", result)
	}

	return nil
}

// ==================== Functional Options for Pull ====================

type pullOptions struct {
	remote    string
	branch    string
	timeoutMs int
}

// PullOption configures the Pull operation.
type PullOption func(*pullOptions)

// WithPullRemote sets the remote to pull from.
func WithPullRemote(remote string) PullOption {
	return func(opts *pullOptions) {
		opts.remote = remote
	}
}

// WithPullBranch sets the branch to pull.
func WithPullBranch(branch string) PullOption {
	return func(opts *pullOptions) {
		opts.branch = branch
	}
}

// WithPullTimeout sets the timeout for pull operation.
func WithPullTimeout(timeoutMs int) PullOption {
	return func(opts *pullOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// Pull fetches from and integrates with another repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.Pull("/home/user/my-project")
func (g *Git) Pull(repoPath string, opts ...PullOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &pullOptions{
		timeoutMs: defaultPullTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"pull"}
	if options.remote != "" {
		args = append(args, options.remote)
		if options.branch != "" {
			args = append(args, options.branch)
		}
	}

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("pull", result)
	}

	return nil
}

// ==================== Functional Options for Config ====================

type configOptions struct {
	scope     string // local, global
	timeoutMs int
}

// ConfigOption configures the Config operation.
type ConfigOption func(*configOptions)

// WithConfigLocal sets configuration scope to local (repository-specific).
func WithConfigLocal() ConfigOption {
	return func(opts *configOptions) {
		opts.scope = "local"
	}
}

// WithConfigGlobal sets configuration scope to global (user-specific).
func WithConfigGlobal() ConfigOption {
	return func(opts *configOptions) {
		opts.scope = "global"
	}
}

// WithConfigTimeout sets the timeout for config operation.
func WithConfigTimeout(timeoutMs int) ConfigOption {
	return func(opts *configOptions) {
		opts.timeoutMs = timeoutMs
	}
}

// ConfigureUser configures user name and email for the repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - name: user name to configure
//   - email: user email to configure
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.ConfigureUser("/home/user/my-project", "Agent", "agent@example.com")
func (g *Git) ConfigureUser(repoPath string, name string, email string, opts ...ConfigOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	// Set user name
	nameArgs := []string{"config"}
	if options.scope != "" {
		nameArgs = append(nameArgs, "--"+options.scope)
	}
	nameArgs = append(nameArgs, "user.name", name)

	nameResult, err := g.runGit(nameArgs, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	if !nameResult.Success {
		return classifyError("config", nameResult)
	}

	// Set user email
	emailArgs := []string{"config"}
	if options.scope != "" {
		emailArgs = append(emailArgs, "--"+options.scope)
	}
	emailArgs = append(emailArgs, "user.email", email)

	emailResult, err := g.runGit(emailArgs, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}
	if !emailResult.Success {
		return classifyError("config", emailResult)
	}

	return nil
}

// SetConfig sets a configuration value in the repository.
//
// Parameters:
//   - repoPath: path to the git repository
//   - key: configuration key (e.g., "user.name", "core.autocrlf")
//   - value: configuration value
//   - opts: optional configuration functions
//
// Returns:
//   - error: error if the operation fails
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	_ = result.Session.Git.SetConfig("/home/user/my-project", "core.autocrlf", "true")
func (g *Git) SetConfig(repoPath string, key string, value string, opts ...ConfigOption) error {
	if err := g.ensureGitAvailable(); err != nil {
		return err
	}

	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"config"}
	if options.scope != "" {
		args = append(args, "--"+options.scope)
	}
	args = append(args, key, value)

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return err
	}

	if !result.Success {
		return classifyError("config", result)
	}

	return nil
}

// GetConfig gets a configuration value from the repository.
// Returns empty string (not error) if the key does not exist (exit code 1, empty stderr).
// Other errors (e.g. not a git repository) are returned as-is.
//
// Parameters:
//   - repoPath: path to the git repository
//   - key: configuration key to retrieve
//   - opts: optional configuration functions
//
// Returns:
//   - string: configuration value, or empty string if not found
//   - error: error if the operation fails (excluding "not found" case)
//
// Example:
//
//	client, _ := agentbay.NewAgentBay(os.Getenv("AGENTBAY_API_KEY"), nil)
//	result, _ := client.Create(nil)
//	defer result.Session.Delete()
//	value, _ := result.Session.Git.GetConfig("/home/user/my-project", "user.name")
func (g *Git) GetConfig(repoPath string, key string, opts ...ConfigOption) (string, error) {
	if err := g.ensureGitAvailable(); err != nil {
		return "", err
	}

	options := &configOptions{
		scope:     "global",
		timeoutMs: defaultGitTimeoutMs,
	}
	for _, opt := range opts {
		opt(options)
	}

	args := []string{"config"}
	if options.scope != "" {
		args = append(args, "--"+options.scope)
	}
	args = append(args, "--get", key)

	result, err := g.runGit(args, repoPath, options.timeoutMs)
	if err != nil {
		return "", err
	}

	if !result.Success {
		stderr := strings.TrimSpace(strings.ToLower(result.Stderr))
		if result.ExitCode == 1 && (stderr == "" || strings.Contains(stderr, "key does not contain")) {
			return "", nil
		}
		return "", classifyError("get_config", result)
	}

	return strings.TrimSpace(result.Stdout), nil
}
