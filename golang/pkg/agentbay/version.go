package agentbay

import (
	"regexp"
	"runtime/debug"
	"strings"
)

// Version is the current version of the AgentBay SDK
// This can be overridden at build time using:
//
//	go build -ldflags "-X github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay.Version=x.y.z"
//
// If not overridden, it will try to read from Go module info, or fallback to default
var Version = getVersion()

// IsRelease indicates whether this is a release build
// A release build is identified by checking if the module is installed from GitHub
// This can also be overridden at build time using:
//
//	go build -ldflags "-X github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay.IsRelease=false"
var IsRelease = "false"

// getVersion attempts to read version from Go module info
// Returns the version from go.mod or a default fallback
func getVersion() string {
	// Try to read from build info (available in Go 1.18+)
	if info, ok := debug.ReadBuildInfo(); ok {
		// First check if this is the main module
		// This happens when someone is developing the SDK itself
		if info.Main.Path == "github.com/aliyun/wuying-agentbay-sdk/golang" {
			if info.Main.Version != "" && info.Main.Version != "(devel)" {
				return info.Main.Version
			}
		}

		// Look for this module as a dependency
		// This happens when someone is using the SDK in their project
		for _, dep := range info.Deps {
			if dep.Path == "github.com/aliyun/wuying-agentbay-sdk/golang" {
				if dep.Version != "" && dep.Version != "(devel)" {
					return dep.Version
				}
			}
		}
	}

	// Fallback to default version (used in development)
	return "0.19.0"
}

// isReleaseVersion checks if this is a release build
// Returns true only if the SDK is installed from GitHub (github.com/aliyun/wuying-agentbay-sdk/golang)
// Returns false if:
// 1. Developing the SDK locally (main module)
// 2. Installed via go.mod replace from internal source (code.alibaba-inc.com)
// 3. Installed from a pseudo-version
func isReleaseVersion() bool {
	// Check if explicitly set via -ldflags
	if strings.ToLower(IsRelease) == "true" {
		return true
	}

	// Try to read from build info
	if info, ok := debug.ReadBuildInfo(); ok {
		// Case 1: Local development - this is the main module
		if info.Main.Path == "github.com/aliyun/wuying-agentbay-sdk/golang" {
			// If version is "(devel)" or empty, it's local development
			if info.Main.Version == "" || info.Main.Version == "(devel)" {
				return false
			}
		}

		// Case 2: Check if this module is used as a dependency
		for _, dep := range info.Deps {
			if dep.Path == "github.com/aliyun/wuying-agentbay-sdk/golang" {
				// Check if this dependency is replaced (e.g., via go.mod replace)
				if dep.Replace != nil {
					// Check if replaced with internal source
					if strings.Contains(dep.Replace.Path, "code.alibaba-inc.com") {
						return false
					}
					// Other replace directives are also considered non-release
					return false
				}

				// Check if version is a pseudo-version (e.g., v0.0.0-20251030235743-xxxxx)
				// Pseudo-versions contain timestamps and are not official releases
				if matched, _ := regexp.MatchString(`v0\.0\.0-\d{14}-[a-f0-9]+`, dep.Version); matched {
					return false
				}

				// If installed from github.com without replace and not a pseudo-version
				// then it's a release version
				if dep.Version != "" && dep.Version != "(devel)" {
					return true
				}
			}
		}
	}

	// Default to false for unknown cases
	return false
}
