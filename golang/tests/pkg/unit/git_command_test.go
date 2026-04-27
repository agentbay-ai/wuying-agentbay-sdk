package agentbay_test

import (
	"encoding/json"
	"strings"
	"testing"

	mcp "github.com/aliyun/wuying-agentbay-sdk/golang/api/client"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/command"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/git"
	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay/models"
	"github.com/stretchr/testify/assert"
)

// GitTestMockSession is a mock implementation of the Session interface for testing Git command building
type GitTestMockSession struct {
	callMcpToolFunc func(toolName string, args interface{}) (*models.McpToolResult, error)
}

func (m *GitTestMockSession) GetAPIKey() string {
	return "test-api-key"
}

func (m *GitTestMockSession) GetClient() *mcp.Client {
	return nil
}

func (m *GitTestMockSession) GetSessionId() string {
	return "test-session-id"
}

func (m *GitTestMockSession) IsVpc() bool {
	return false
}

func (m *GitTestMockSession) NetworkInterfaceIp() string {
	return ""
}

func (m *GitTestMockSession) HttpPort() string {
	return ""
}

func (m *GitTestMockSession) CallMcpTool(toolName string, args interface{}) (*models.McpToolResult, error) {
	if m.callMcpToolFunc != nil {
		return m.callMcpToolFunc(toolName, args)
	}
	return nil, nil
}

// createMockGit creates a mock Git instance with a command validator callback.
// The callback is called for each command execution (after the initial git --version check).
// For commit commands, the mock returns a stdout containing a commit hash to avoid
// the rev-parse HEAD fallback path.
func createMockGit(t *testing.T, validator func(cmd string)) *git.Git {
	callCount := 0
	mockSession := &GitTestMockSession{
		callMcpToolFunc: func(toolName string, args interface{}) (*models.McpToolResult, error) {
			assert.Equal(t, "shell", toolName)

			argsMap := args.(map[string]interface{})
			cmd := argsMap["command"].(string)

			// First call is always git --version for ensureGitAvailable
			if callCount == 0 {
				callCount++
				// Return success for git --version
				jsonData := map[string]interface{}{
					"stdout":    "git version 2.39.0",
					"stderr":    "",
					"exit_code": 0,
				}
				jsonBytes, _ := json.Marshal(jsonData)
				return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
			}

			// Subsequent calls go through the validator
			if validator != nil {
				validator(cmd)
			}

			// Determine appropriate stdout based on command type
			stdout := ""
			if strings.Contains(cmd, "'commit'") {
				// Return commit-like output so Commit() can parse the hash
				// and avoid falling back to rev-parse HEAD
				stdout = "[main abc1234] test commit\n 1 file changed, 1 insertion(+)"
			} else if strings.Contains(cmd, "'status'") {
				stdout = "## main"
			} else if strings.Contains(cmd, "'log'") {
				stdout = ""
			} else if strings.Contains(cmd, "'branch'") && strings.Contains(cmd, "'--format") {
				stdout = "main\t*"
			}

			// Return success for subsequent calls
			jsonData := map[string]interface{}{
				"stdout":    stdout,
				"stderr":    "",
				"exit_code": 0,
			}
			jsonBytes, _ := json.Marshal(jsonData)
			return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
		},
	}

	cmd := command.NewCommand(mockSession)
	return git.NewGit(cmd)
}

// ============================================================================
// Clone Command Tests (5 tests)
// ============================================================================

func TestGit_Clone_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Clone("https://github.com/user/repo.git")

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "'clone'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
	assert.Equal(t, "repo", result.Path)
}

func TestGit_Clone_WithBranch(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Clone("https://github.com/user/repo.git", git.WithCloneBranch("main"))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "'clone'")
	assert.Contains(t, capturedCmd, "'--branch'")
	assert.Contains(t, capturedCmd, "'main'")
	assert.Contains(t, capturedCmd, "'--single-branch'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

func TestGit_Clone_WithDepth(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Clone("https://github.com/user/repo.git", git.WithCloneDepth(1))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "'clone'")
	assert.Contains(t, capturedCmd, "'--depth'")
	assert.Contains(t, capturedCmd, "'1'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

func TestGit_Clone_WithPath(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Clone("https://github.com/user/repo.git", git.WithClonePath("/tmp/myrepo"))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "'clone'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
	assert.Contains(t, capturedCmd, "'/tmp/myrepo'")
	assert.Equal(t, "/tmp/myrepo", result.Path)
}

func TestGit_Clone_WithBranchAndDepth(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Clone("https://github.com/user/repo.git",
		git.WithCloneBranch("develop"),
		git.WithCloneDepth(5))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "'clone'")
	assert.Contains(t, capturedCmd, "'--branch'")
	assert.Contains(t, capturedCmd, "'develop'")
	assert.Contains(t, capturedCmd, "'--single-branch'")
	assert.Contains(t, capturedCmd, "'--depth'")
	assert.Contains(t, capturedCmd, "'5'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

// ============================================================================
// Init Command Tests (3 tests)
// ============================================================================

func TestGit_Init_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Init("/tmp/testrepo")

	assert.NoError(t, err)
	assert.NotNil(t, result)
	// Path should be an argument to init, NOT used with -C
	assert.NotContains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'init'")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Equal(t, "/tmp/testrepo", result.Path)
}

func TestGit_Init_WithBranch(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Init("/tmp/testrepo", git.WithInitBranch("main"))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.NotContains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'init'")
	assert.Contains(t, capturedCmd, "'--initial-branch'")
	assert.Contains(t, capturedCmd, "'main'")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
}

func TestGit_Init_WithBare(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Init("/tmp/testrepo", git.WithInitBare())

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.NotContains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'init'")
	assert.Contains(t, capturedCmd, "'--bare'")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
}

// ============================================================================
// Add Command Tests (3 tests)
// ============================================================================

func TestGit_Add_WithPaths(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Add("/tmp/testrepo", git.WithAddPaths([]string{"file1.txt", "file2.txt"}))

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "'--'")
	assert.Contains(t, capturedCmd, "'file1.txt'")
	assert.Contains(t, capturedCmd, "'file2.txt'")
}

func TestGit_Add_WithAll(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Add("/tmp/testrepo", git.WithAddAll())

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "'--all'")
}

func TestGit_Add_NoPaths_DefaultStageAll(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Add("/tmp/testrepo")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "'-A'")
}

// ============================================================================
// Commit Command Tests (3 tests)
// ============================================================================

func TestGit_Commit_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Commit("/tmp/testrepo", "Initial commit")

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'commit'")
	assert.Contains(t, capturedCmd, "'-m'")
	assert.Contains(t, capturedCmd, "'Initial commit'")
}

func TestGit_Commit_WithAllowEmpty(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Commit("/tmp/testrepo", "Empty commit", git.WithCommitAllowEmpty())

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'commit'")
	assert.Contains(t, capturedCmd, "'--allow-empty'")
	assert.Contains(t, capturedCmd, "'-m'")
	assert.Contains(t, capturedCmd, "'Empty commit'")
}

func TestGit_Commit_WithAuthorNameAndEmail(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Commit("/tmp/testrepo", "Test commit",
		git.WithCommitAuthorName("Test User"),
		git.WithCommitAuthorEmail("test@example.com"))

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	// -c parameters must come BEFORE the 'commit' subcommand
	// Note: -c is not shell-escaped (it's a git global flag added manually)
	assert.Contains(t, capturedCmd, "-c")
	assert.Contains(t, capturedCmd, "'user.name=Test User'")
	assert.Contains(t, capturedCmd, "'user.email=test@example.com'")
	assert.Contains(t, capturedCmd, "'commit'")
	assert.Contains(t, capturedCmd, "'-m'")
	assert.Contains(t, capturedCmd, "'Test commit'")
}

// ============================================================================
// Status Command Tests (1 test)
// ============================================================================

func TestGit_Status_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	result, err := g.Status("/tmp/testrepo")

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'status'")
	assert.Contains(t, capturedCmd, "'--porcelain=1'")
	assert.Contains(t, capturedCmd, "'-b'")
}

// ============================================================================
// Branch Command Tests (4 tests)
// ============================================================================

func TestGit_CreateBranch_Default(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.CreateBranch("/tmp/testrepo", "feature")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'checkout'")
	assert.Contains(t, capturedCmd, "'-b'")
	assert.Contains(t, capturedCmd, "'feature'")
}

func TestGit_CreateBranch_NoCheckout(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.CreateBranch("/tmp/testrepo", "feature", git.WithBranchCreateCheckout(false))

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'branch'")
	assert.Contains(t, capturedCmd, "'feature'")
	assert.NotContains(t, capturedCmd, "'checkout'")
}

func TestGit_DeleteBranch_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.DeleteBranch("/tmp/testrepo", "feature")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'branch'")
	assert.Contains(t, capturedCmd, "'-d'")
	assert.Contains(t, capturedCmd, "'feature'")
}

func TestGit_DeleteBranch_WithForce(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.DeleteBranch("/tmp/testrepo", "feature", git.WithBranchDeleteForce())

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'branch'")
	assert.Contains(t, capturedCmd, "'-D'")
	assert.Contains(t, capturedCmd, "'feature'")
}

// ============================================================================
// Config Command Tests (2 tests)
// ============================================================================

func TestGit_ConfigureUser_DefaultGlobal(t *testing.T) {
	var capturedCmds []string
	g := createMockGit(t, func(cmd string) {
		capturedCmds = append(capturedCmds, cmd)
	})

	err := g.ConfigureUser("/tmp/testrepo", "Test User", "test@example.com")

	assert.NoError(t, err)
	assert.Len(t, capturedCmds, 2)

	// First command: set user name
	assert.Contains(t, capturedCmds[0], "-C")
	assert.Contains(t, capturedCmds[0], "'/tmp/testrepo'")
	assert.Contains(t, capturedCmds[0], "'config'")
	assert.Contains(t, capturedCmds[0], "'--global'")
	assert.Contains(t, capturedCmds[0], "'user.name'")
	assert.Contains(t, capturedCmds[0], "'Test User'")

	// Second command: set user email
	assert.Contains(t, capturedCmds[1], "-C")
	assert.Contains(t, capturedCmds[1], "'/tmp/testrepo'")
	assert.Contains(t, capturedCmds[1], "'config'")
	assert.Contains(t, capturedCmds[1], "'--global'")
	assert.Contains(t, capturedCmds[1], "'user.email'")
	assert.Contains(t, capturedCmds[1], "'test@example.com'")
}

func TestGit_SetConfig_DefaultGlobal(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.SetConfig("/tmp/testrepo", "core.autocrlf", "true")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'config'")
	assert.Contains(t, capturedCmd, "'--global'")
	assert.Contains(t, capturedCmd, "'core.autocrlf'")
	assert.Contains(t, capturedCmd, "'true'")
}

// ============================================================================
// Reset Command Tests (2 tests)
// ============================================================================

func TestGit_Reset_Default(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Reset("/tmp/testrepo")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'reset'")
	assert.Contains(t, capturedCmd, "'--mixed'")
	assert.Contains(t, capturedCmd, "'HEAD'")
}

func TestGit_Reset_Hard(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Reset("/tmp/testrepo", git.WithResetHard())

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'reset'")
	assert.Contains(t, capturedCmd, "'--hard'")
	assert.Contains(t, capturedCmd, "'HEAD'")
}

// ============================================================================
// Pull Command Tests (2 tests)
// ============================================================================

func TestGit_Pull_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Pull("/tmp/testrepo")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'pull'")
}

// ============================================================================
// RemoteAdd Command Tests (2 tests)
// ============================================================================

func TestGit_RemoteAdd_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.RemoteAdd("/tmp/testrepo", "origin", "https://github.com/user/repo.git")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'remote'")
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "'origin'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

func TestGit_RemoteAdd_WithFetch(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.RemoteAdd("/tmp/testrepo", "origin", "https://github.com/user/repo.git", git.WithRemoteAddFetch())

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'remote'")
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "'-f'")
	assert.Contains(t, capturedCmd, "'origin'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

func TestGit_RemoteAdd_WithOverwrite(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.RemoteAdd("/tmp/testrepo", "origin", "https://github.com/user/repo.git", git.WithRemoteAddOverwrite())

	assert.NoError(t, err)
	// Idempotent mode uses "add ... || set-url ..." pattern
	assert.Contains(t, capturedCmd, "'remote'")
	assert.Contains(t, capturedCmd, "'add'")
	assert.Contains(t, capturedCmd, "||") // fallback pattern
	assert.Contains(t, capturedCmd, "'set-url'")
	assert.Contains(t, capturedCmd, "'origin'")
	assert.Contains(t, capturedCmd, "'https://github.com/user/repo.git'")
}

// ==================== Checkout Tests ====================

func TestGit_Checkout_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.CheckoutBranch("/tmp/testrepo", "main")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'checkout'")
	assert.Contains(t, capturedCmd, "'main'")
}

// ==================== Log Tests ======================================

func TestGit_Log_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	_, err := g.Log("/tmp/testrepo")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'log'")
	assert.Contains(t, capturedCmd, "'--format=%H")
}

func TestGit_Log_WithMaxCount(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	_, err := g.Log("/tmp/testrepo", git.WithLogMaxCount(5))

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'log'")
	assert.Contains(t, capturedCmd, "'-n'")
	assert.Contains(t, capturedCmd, "'5'")
}

// ==================== Restore Tests ====================

func TestGit_Restore_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Restore("/tmp/testrepo", []string{"file.txt"})

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "-C")
	assert.Contains(t, capturedCmd, "'/tmp/testrepo'")
	assert.Contains(t, capturedCmd, "'restore'")
	// Default: should have --worktree when neither staged nor worktree is set
	assert.Contains(t, capturedCmd, "'--worktree'")
	assert.Contains(t, capturedCmd, "'--'")
	assert.Contains(t, capturedCmd, "'file.txt'")
}

func TestGit_Restore_Staged(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Restore("/tmp/testrepo", []string{"file.txt"}, git.WithRestoreStaged())

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'restore'")
	assert.Contains(t, capturedCmd, "'--staged'")
	assert.Contains(t, capturedCmd, "'--'")
	assert.Contains(t, capturedCmd, "'file.txt'")
	// When staged is set, --worktree should NOT be present
	assert.NotContains(t, capturedCmd, "'--worktree'")
}

func TestGit_Restore_NoPaths_Error(t *testing.T) {
	g := createMockGit(t, func(cmd string) {
		t.Error("Should not call command when no paths provided")
	})

	err := g.Restore("/tmp/testrepo", []string{})

	assert.Error(t, err)
	assert.Contains(t, err.Error(), "requires at least one path")
}

// ==================== RemoteGet Tests ====================

func TestGit_RemoteGet_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	_, err := g.RemoteGet("/tmp/testrepo", "origin")

	assert.NoError(t, err)
	// Uses direct runGit (no || true)
	assert.Contains(t, capturedCmd, "'remote'")
	assert.Contains(t, capturedCmd, "'get-url'")
	assert.Contains(t, capturedCmd, "'origin'")
	assert.NotContains(t, capturedCmd, "|| true")
}

// ==================== GetConfig Tests ====================

func TestGit_GetConfig_Basic(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	_, err := g.GetConfig("/tmp/testrepo", "user.name")

	assert.NoError(t, err)
	// Uses direct runGit (no || true)
	assert.Contains(t, capturedCmd, "'config'")
	assert.Contains(t, capturedCmd, "'--global'")
	assert.Contains(t, capturedCmd, "'--get'")
	assert.Contains(t, capturedCmd, "'user.name'")
	assert.NotContains(t, capturedCmd, "|| true")
}

// ==================== CreateBranch Force+Checkout Tests ====================

func TestGit_CreateBranch_DefaultUsesSmallB(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.CreateBranch("/tmp/testrepo", "feature")

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'checkout'")
	assert.Contains(t, capturedCmd, "'-b'")
	assert.Contains(t, capturedCmd, "'feature'")
	// Should NOT contain -B (force) since WithBranchCreateForce is removed
	assert.NotContains(t, capturedCmd, "'-B'")
}

func TestGit_Reset_WithPaths(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Reset("/tmp/testrepo", git.WithResetPaths([]string{"file1.txt", "file2.txt"}))

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'reset'")
	assert.Contains(t, capturedCmd, "'--'")
	assert.Contains(t, capturedCmd, "'file1.txt'")
	assert.Contains(t, capturedCmd, "'file2.txt'")
}

func TestGit_Restore_DefaultWorktree(t *testing.T) {
	var capturedCmd string
	g := createMockGit(t, func(cmd string) {
		capturedCmd = cmd
	})

	err := g.Restore("/tmp/testrepo", []string{"file.txt"})

	assert.NoError(t, err)
	assert.Contains(t, capturedCmd, "'restore'")
	assert.Contains(t, capturedCmd, "'--worktree'")
	assert.Contains(t, capturedCmd, "'--'")
	assert.Contains(t, capturedCmd, "'file.txt'")
}

// ==================== Error Path Tests ====================

// createMockGitWithError creates a mock Git instance that returns an error response
// for git operations (after the initial git --version check).
func createMockGitWithError(t *testing.T, exitCode int, stderr string) *git.Git {
	callCount := 0
	mockSession := &GitTestMockSession{
		callMcpToolFunc: func(toolName string, args interface{}) (*models.McpToolResult, error) {
			assert.Equal(t, "shell", toolName)

			// First call is always git --version for ensureGitAvailable
			if callCount == 0 {
				callCount++
				jsonData := map[string]interface{}{
					"stdout":    "git version 2.39.0",
					"stderr":    "",
					"exit_code": 0,
				}
				jsonBytes, _ := json.Marshal(jsonData)
				return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
			}

			// Subsequent calls return error
			jsonData := map[string]interface{}{
				"stdout":    "",
				"stderr":    stderr,
				"exit_code": exitCode,
			}
			jsonBytes, _ := json.Marshal(jsonData)
			return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
		},
	}

	cmd := command.NewCommand(mockSession)
	return git.NewGit(cmd)
}

func TestGit_Clone_AuthError(t *testing.T) {
	g := createMockGitWithError(t, 128, "fatal: Authentication failed for 'https://github.com/user/repo.git'")

	_, err := g.Clone("https://github.com/user/repo.git")

	assert.Error(t, err)
	_, ok := err.(*git.GitAuthError)
	assert.True(t, ok, "expected GitAuthError, got %T", err)
}

func TestGit_Status_NotARepoError(t *testing.T) {
	g := createMockGitWithError(t, 128, "fatal: not a git repository (or any of the parent directories): .git")

	_, err := g.Status("/tmp/not-a-repo")

	assert.Error(t, err)
	_, ok := err.(*git.GitNotARepoError)
	assert.True(t, ok, "expected GitNotARepoError, got %T", err)
}

// ==================== Commit Hash Fallback Tests ====================

func TestGit_Commit_HashFallback(t *testing.T) {
	// Test the fallback path: commit output doesn't contain a parseable hash,
	// so it falls back to rev-parse HEAD
	callCount := 0
	mockSession := &GitTestMockSession{
		callMcpToolFunc: func(toolName string, args interface{}) (*models.McpToolResult, error) {
			assert.Equal(t, "shell", toolName)

			argsMap := args.(map[string]interface{})
			cmd := argsMap["command"].(string)

			// First call: git --version
			if callCount == 0 {
				callCount++
				jsonData := map[string]interface{}{
					"stdout":    "git version 2.39.0",
					"stderr":    "",
					"exit_code": 0,
				}
				jsonBytes, _ := json.Marshal(jsonData)
				return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
			}

			callCount++
			var stdout string
			if strings.Contains(cmd, "'commit'") {
				// Return commit output WITHOUT a parseable hash
				stdout = "Your branch is up to date.\n1 file changed, 1 insertion(+)"
			} else if strings.Contains(cmd, "'rev-parse'") {
				// Fallback: return full commit hash
				stdout = "deadbeef1234567890abcdef1234567890abcdef"
			}

			jsonData := map[string]interface{}{
				"stdout":    stdout,
				"stderr":    "",
				"exit_code": 0,
			}
			jsonBytes, _ := json.Marshal(jsonData)
			return &models.McpToolResult{Success: true, Data: string(jsonBytes)}, nil
		},
	}

	cmd := command.NewCommand(mockSession)
	g := git.NewGit(cmd)

	result, err := g.Commit("/tmp/testrepo", "Test commit")

	assert.NoError(t, err)
	assert.NotNil(t, result)
	// Should get the hash from rev-parse HEAD fallback
	assert.Equal(t, "deadbeef1234567890abcdef1234567890abcdef", result.CommitHash)
}
