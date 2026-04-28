package main

import (
	"bytes"
	"fmt"
	"go/ast"
	"go/doc"
	"go/parser"
	"go/printer"
	"go/token"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"

	"gopkg.in/yaml.v3"
)

type docMapping struct {
	Target          string
	Title           string
	PackagePath     string
	ModuleName      string // Optional: module name for metadata lookup (defaults to extractModuleName(PackagePath))
	TypeNames       []string
	FuncNames       []string
	ValueNames      []string
	IncludeAllTypes bool
	IncludeAllFuncs bool
	HiddenMethods   []string // Methods to hide from documentation
	PriorityTypes   []string // Types to show first (main types before auxiliary types)
}

type packageDoc struct {
	doc  *doc.Package
	fset *token.FileSet
}

type Metadata struct {
	Global  GlobalConfig            `yaml:"global"`
	Modules map[string]ModuleConfig `yaml:"modules"`
}

type GlobalConfig struct {
	ImageRequirements map[string]string `yaml:"image_requirements"`
	BestPractices     map[string]string `yaml:"best_practices"`
	AutoFilterRules   AutoFilterRules   `yaml:"auto_filter_rules"`
}

type AutoFilterRules struct {
	ExcludeSimpleGetters        []string `yaml:"exclude_simple_getters"`
	ExcludeVpcHelpers           []string `yaml:"exclude_vpc_helpers"`
	ExcludeSerializationMethods []string `yaml:"exclude_serialization_methods"`
	ExcludeMarshalMethods       []string `yaml:"exclude_marshal_methods"`
	ExcludeLowercaseMethods     bool     `yaml:"exclude_lowercase_methods"`
	ExcludeValidationMethods    bool     `yaml:"exclude_validation_methods"`
	ExcludeInternalHelpers      bool     `yaml:"exclude_internal_helpers"`
}

type ModuleConfig struct {
	Tutorial         *TutorialConfig  `yaml:"tutorial"`
	RelatedResources []ResourceConfig `yaml:"related_resources"`
	Overview         string           `yaml:"overview"`
	Requirements     []string         `yaml:"requirements"`
	BestPractices    []string         `yaml:"best_practices"`
	DataTypes        []DataTypeInfo   `yaml:"data_types"`
	ImportantNotes   []string         `yaml:"important_notes"`
	Emoji            string           `yaml:"emoji"`
	Category         string           `yaml:"category"`
}

type TutorialConfig struct {
	URL         string `yaml:"url"`
	Text        string `yaml:"text"`
	Description string `yaml:"description"`
}

type ResourceConfig struct {
	Name     string `yaml:"name"`
	Module   string `yaml:"module"`
	Category string `yaml:"category"`
}

type DataTypeInfo struct {
	Name        string `yaml:"name"`
	Description string `yaml:"description"`
}

var mappings = []docMapping{
	{
		Target:      "common-features/basics/agentbay.md",
		Title:       "AgentBay",
		PackagePath: "pkg/agentbay",
		TypeNames:   []string{"AgentBayConfig", "AgentBay", "Option"},
		FuncNames: []string{
			"NewAgentBay",
			"NewAgentBayWithDefaults",
			"WithConfig",
			"WithEnvFile",
		},
	},
	{
		Target:      "common-features/basics/session.md",
		Title:       "Session",
		PackagePath: "pkg/agentbay",
		ModuleName:  "session", // Use "session" for metadata lookup instead of "agentbay"
		TypeNames: []string{
			// Main types (show first)
			"Session",
			"CreateSessionParams",
			// Result types
			"SessionResult",
			"SessionListResult",
			"InfoResult",
			"LabelResult",
			"LinkResult",
			"DeleteResult",
			"McpToolsResult",
			// MCP and Info types
			"McpTool",
			"SessionInfo",
		},
		PriorityTypes: []string{
			"Session",
			"CreateSessionParams",
		},
		// HiddenMethods now handled by auto-filter rules in metadata.yaml
		// Only need to specify special cases not covered by auto-rules
		HiddenMethods: []string{
			"FindServerForTool",              // Internal MCP tool lookup helper
			"callMcpToolAPI",                 // Internal implementation
			"callMcpToolVPC",                 // Internal implementation
			"extractTextContentFromResponse", // Internal helper
			"GetCommand",                     // Internal accessor
			"GetMcpTools",                    // Internal accessor
			"ensureDefaults",                 // Internal helper
			"CallMcpToolForBrowser",          // Duplicate interface method
			"GetLinkForBrowser",              // Duplicate interface method
			"GetFileUploadUrl",               // Internal interface method
			"GetFileDownloadUrl",             // Internal interface method
			"GetContextService",              // Internal interface method
		},
		FuncNames: []string{
			"NewSession",
			"NewCreateSessionParams",
		},
	},
	{
		Target:          "common-features/basics/command.md",
		Title:           "Command",
		PackagePath:     "pkg/agentbay/command",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/basics/context.md",
		Title:       "Context",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"Context",
			"ContextResult",
			"ContextListResult",
			"ContextCreateResult",
			"ContextModifyResult",
			"ContextDeleteResult",
			"ContextClearResult",
			"ContextService",
			"ContextListParams",
			"ContextFileUrlResult",
			"ContextFileEntry",
			"ContextFileListResult",
			"ContextFileDeleteResult",
		},
		FuncNames: []string{
			"NewContextListParams",
		},
	},
	{
		Target:      "common-features/basics/session-params.md",
		Title:       "Session Params",
		PackagePath: "pkg/agentbay",
		ModuleName:  "session-params",
		TypeNames: []string{
			"CreateSessionParams",
			"ListSessionParams",
		},
		FuncNames: []string{
			"NewCreateSessionParams",
			"NewListSessionParams",
		},
	},
	{
		Target:      "common-features/basics/lifecycle-policy.md",
		Title:       "Lifecycle Policy",
		PackagePath: "pkg/agentbay",
		ModuleName:  "lifecycle-policy",
		TypeNames: []string{
			"LifecyclePolicy",
		},
		FuncNames: []string{
			"NewLifecyclePolicy",
			"NewLifecyclePolicyWithValues",
		},
	},
	{
		Target:      "common-features/basics/context-manager.md",
		Title:       "Context Manager",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"ContextStatusData",
			"ContextStatusItem",
			"ContextInfoResult",
			"ContextSyncResult",
			"ContextManager",
		},
		FuncNames: []string{
			"NewContextManager",
		},
	},
	{
		Target:          "common-features/basics/filesystem.md",
		Title:           "File System",
		PackagePath:     "pkg/agentbay/filesystem",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/basics/context-sync.md",
		Title:       "Context Sync",
		PackagePath: "pkg/agentbay",
		TypeNames: []string{
			"ContextSync",
			"SyncPolicy",
			"UploadPolicy",
			"DownloadPolicy",
			"DeletePolicy",
			"ExtractPolicy",
			"RecyclePolicy",
			"WhiteList",
			"BWList",
			"MappingPolicy",
			"UploadStrategy",
			"DownloadStrategy",
			"UploadMode",
			"Lifecycle",
		},
		FuncNames: []string{
			"NewContextSync",
			"NewSyncPolicy",
			"NewUploadPolicy",
			"NewDownloadPolicy",
			"NewDeletePolicy",
			"NewExtractPolicy",
			"NewRecyclePolicy",
			"NewMappingPolicy",
		},
	},
	{
		Target:      "common-features/basics/logging.md",
		Title:       "Logging",
		PackagePath: "pkg/agentbay",
		TypeNames:   []string{"LoggerConfig"},
		FuncNames: []string{
			"SetLogLevel",
			"GetLogLevel",
			"SetupLogger",
			"LogDebug",
			"LogInfo",
			// Private functions removed: logInfoWithColor, logOperationError, logAPICall,
			// logAPIResponseWithDetails, logCodeExecutionOutput, maskSensitiveData
		},
		ValueNames: []string{"LOG_DEBUG", "LOG_INFO", "LOG_WARN", "LOG_ERROR"},
	},
	{
		Target:          "common-features/advanced/agent.md",
		Title:           "Agent",
		PackagePath:     "pkg/agentbay/agent",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/advanced/oss.md",
		Title:           "OSS",
		PackagePath:     "pkg/agentbay/oss",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:      "common-features/advanced/network.md",
		Title:       "Network",
		PackagePath: "pkg/agentbay",
		ModuleName:  "network",
		TypeNames: []string{
			"BetaNetworkService",
			"BetaNetworkResult",
			"BetaNetworkStatusResult",
		},
	},
	{
		Target:          "browser-use/browser.md",
		Title:           "Browser",
		PackagePath:     "pkg/agentbay/browser",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "codespace/code.md",
		Title:           "Code",
		PackagePath:     "pkg/agentbay/code",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "computer-use/computer.md",
		Title:           "Computer",
		PackagePath:     "pkg/agentbay/computer",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "mobile-use/mobile.md",
		Title:           "Mobile",
		PackagePath:     "pkg/agentbay/mobile",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:      "mobile-use/mobile-simulate.md",
		Title:       "Mobile Simulate",
		PackagePath: "pkg/agentbay",
		ModuleName:  "mobile-simulate",
		TypeNames: []string{
			"MobileSimulateService",
			"MobileSimulateUploadResult",
		},
		FuncNames: []string{
			"NewMobileSimulateService",
		},
	},
	{
		Target:          "common-features/advanced/git.md",
		Title:           "Git",
		PackagePath:     "pkg/agentbay/git",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/basics/pty.md",
		Title:           "PTY Terminal",
		PackagePath:     "pkg/agentbay/pty",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
	{
		Target:          "common-features/basics/env.md",
		Title:           "Env",
		PackagePath:     "pkg/agentbay/env",
		IncludeAllTypes: true,
		IncludeAllFuncs: true,
	},
}

var packageCache = map[string]*packageDoc{}

func loadMetadata(projectRoot string) (*Metadata, error) {
	metadataPath := filepath.Join(filepath.Dir(projectRoot), "scripts", "doc-metadata.yaml")
	data, err := os.ReadFile(metadataPath)
	if err != nil {
		if os.IsNotExist(err) {
			return &Metadata{Modules: make(map[string]ModuleConfig)}, nil
		}
		return nil, err
	}

	var metadata Metadata
	if err := yaml.Unmarshal(data, &metadata); err != nil {
		return nil, err
	}

	return &metadata, nil
}

func extractModuleName(packagePath string) string {
	parts := strings.Split(packagePath, "/")
	return parts[len(parts)-1]
}

func getTutorialSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || config.Tutorial == nil {
		return ""
	}

	emoji := config.Emoji
	if emoji == "" {
		emoji = "📖"
	}

	return fmt.Sprintf("## %s Related Tutorial\n\n- [%s](%s) - %s\n\n",
		emoji,
		config.Tutorial.Text,
		config.Tutorial.URL,
		config.Tutorial.Description)
}

func calculateResourcePath(resource ResourceConfig, moduleConfig ModuleConfig) string {
	targetCategory := resource.Category
	if targetCategory == "" {
		targetCategory = "common-features/basics"
	}

	currentCategory := moduleConfig.Category
	if currentCategory == "" {
		currentCategory = "common-features/basics"
	}

	module := resource.Module

	// If same category, just use module name
	if targetCategory == currentCategory {
		return fmt.Sprintf("%s.md", module)
	}

	// Calculate relative path based on current and target categories
	switch currentCategory {
	case "common-features/basics":
		switch targetCategory {
		case "common-features/advanced":
			return fmt.Sprintf("../advanced/%s.md", module)
		case "browser-use":
			return fmt.Sprintf("../../../browser-use/%s.md", module)
		case "codespace":
			return fmt.Sprintf("../../../codespace/%s.md", module)
		case "computer-use":
			return fmt.Sprintf("../../../computer-use/%s.md", module)
		case "mobile-use":
			return fmt.Sprintf("../../../mobile-use/%s.md", module)
		default:
			return fmt.Sprintf("../../../%s/%s.md", targetCategory, module)
		}
	case "common-features/advanced":
		switch targetCategory {
		case "common-features/basics":
			return fmt.Sprintf("../basics/%s.md", module)
		case "browser-use":
			return fmt.Sprintf("../../../browser-use/%s.md", module)
		case "codespace":
			return fmt.Sprintf("../../../codespace/%s.md", module)
		case "computer-use":
			return fmt.Sprintf("../../../computer-use/%s.md", module)
		case "mobile-use":
			return fmt.Sprintf("../../../mobile-use/%s.md", module)
		default:
			return fmt.Sprintf("../../../%s/%s.md", targetCategory, module)
		}
	case "browser-use", "codespace", "computer-use", "mobile-use":
		switch targetCategory {
		case "common-features/basics":
			return fmt.Sprintf("../common-features/basics/%s.md", module)
		case "common-features/advanced":
			return fmt.Sprintf("../common-features/advanced/%s.md", module)
		case "browser-use":
			return fmt.Sprintf("../%s.md", module)
		case "codespace":
			return fmt.Sprintf("../../codespace/%s.md", module)
		case "computer-use":
			return fmt.Sprintf("../../computer-use/%s.md", module)
		case "mobile-use":
			return fmt.Sprintf("../../mobile-use/%s.md", module)
		default:
			return fmt.Sprintf("../../%s/%s.md", targetCategory, module)
		}
	default:
		// Fallback for unknown categories
		return fmt.Sprintf("../../%s/%s.md", targetCategory, module)
	}
}

func getOverviewSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || config.Overview == "" {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Overview\n\n")
	buf.WriteString(strings.TrimSpace(config.Overview))
	buf.WriteString("\n\n")

	return buf.String()
}

func getRequirementsSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || len(config.Requirements) == 0 {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Requirements\n\n")
	for _, req := range config.Requirements {
		fmt.Fprintf(&buf, "- %s\n", req)
	}
	buf.WriteString("\n")

	return buf.String()
}

func getDataTypesSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || len(config.DataTypes) == 0 {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Data Types\n\n")
	for _, dt := range config.DataTypes {
		fmt.Fprintf(&buf, "### %s\n\n", dt.Name)
		fmt.Fprintf(&buf, "%s\n\n", dt.Description)
	}

	return buf.String()
}

func getImportantNotesSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || len(config.ImportantNotes) == 0 {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Important Notes\n\n")
	for _, note := range config.ImportantNotes {
		fmt.Fprintf(&buf, "- %s\n", note)
	}
	buf.WriteString("\n")

	return buf.String()
}

func getBestPracticesSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || len(config.BestPractices) == 0 {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Best Practices\n\n")
	for i, practice := range config.BestPractices {
		fmt.Fprintf(&buf, "%d. %s\n", i+1, practice)
	}
	buf.WriteString("\n")

	return buf.String()
}

func getRelatedResourcesSection(moduleName string, metadata *Metadata) string {
	config, ok := metadata.Modules[moduleName]
	if !ok || len(config.RelatedResources) == 0 {
		return ""
	}

	var buf bytes.Buffer
	buf.WriteString("## Related Resources\n\n")
	for _, resource := range config.RelatedResources {
		path := calculateResourcePath(resource, config)
		fmt.Fprintf(&buf, "- [%s](%s)\n", resource.Name, path)
	}
	buf.WriteString("\n")

	return buf.String()
}

func main() {
	_, currentFile, _, _ := runtime.Caller(0)
	scriptDir := filepath.Dir(currentFile)
	projectRoot := filepath.Dir(scriptDir)
	docsRoot := filepath.Join(projectRoot, "docs", "api")

	metadata, err := loadMetadata(projectRoot)
	if err != nil {
		panic(err)
	}

	if err := os.RemoveAll(docsRoot); err != nil {
		panic(err)
	}
	if err := os.MkdirAll(docsRoot, 0o755); err != nil {
		panic(err)
	}

	for _, mapping := range mappings {
		if err := generateDoc(projectRoot, docsRoot, mapping, metadata); err != nil {
			panic(err)
		}
	}

	if err := writeReadme(docsRoot); err != nil {
		panic(err)
	}
}

func generateDoc(projectRoot, docsRoot string, mapping docMapping, metadata *Metadata) error {
	pkgDoc, err := loadPackageDoc(projectRoot, mapping.PackagePath)
	if err != nil {
		return err
	}

	var buf bytes.Buffer
	fmt.Fprintf(&buf, "# %s API Reference\n\n", mapping.Title)

	// Determine module name for metadata lookup
	moduleName := mapping.ModuleName
	if moduleName == "" {
		moduleName = extractModuleName(mapping.PackagePath)
	}

	// Add tutorial section
	tutorialSection := getTutorialSection(moduleName, metadata)
	if tutorialSection != "" {
		buf.WriteString(tutorialSection)
	}

	// Add overview section
	overviewSection := getOverviewSection(moduleName, metadata)
	if overviewSection != "" {
		buf.WriteString(overviewSection)
	}

	// Add package comment if exists
	if pkgComment := strings.TrimSpace(pkgDoc.doc.Doc); pkgComment != "" {
		buf.WriteString(pkgComment)
		buf.WriteString("\n\n")
	}

	// Add requirements section
	requirementsSection := getRequirementsSection(moduleName, metadata)
	if requirementsSection != "" {
		buf.WriteString(requirementsSection)
	}

	// Add data types section
	dataTypesSection := getDataTypesSection(moduleName, metadata)
	if dataTypesSection != "" {
		buf.WriteString(dataTypesSection)
	}

	// Add important notes section
	importantNotesSection := getImportantNotesSection(moduleName, metadata)
	if importantNotesSection != "" {
		buf.WriteString(importantNotesSection)
	}

	// Add types from source code
	types, err := selectTypes(pkgDoc.doc, mapping)
	if err != nil {
		return err
	}
	for _, typ := range types {
		writeType(&buf, pkgDoc, typ, mapping, metadata.Global.AutoFilterRules)
	}

	// Add functions from source code
	funcs, err := selectFuncs(pkgDoc.doc, mapping)
	if err != nil {
		return err
	}
	// Filter out hidden functions (apply same rules as methods)
	visibleFuncs := make([]*doc.Func, 0)
	for _, fn := range funcs {
		if !shouldSkipMethod(fn.Name, fn.Doc, mapping.HiddenMethods, metadata.Global.AutoFilterRules) {
			visibleFuncs = append(visibleFuncs, fn)
		}
	}
	if len(visibleFuncs) > 0 {
		buf.WriteString("## Functions\n\n")
		for _, fn := range visibleFuncs {
			writeFunc(&buf, pkgDoc, fn)
		}
	}

	// Add constants and variables from source code
	values, err := selectValues(pkgDoc.doc, mapping.ValueNames)
	if err != nil {
		return err
	}
	if len(values) > 0 {
		buf.WriteString("## Constants and Variables\n\n")
		for _, val := range values {
			writeValue(&buf, pkgDoc, val)
		}
	}

	// Add best practices section
	bestPracticesSection := getBestPracticesSection(moduleName, metadata)
	if bestPracticesSection != "" {
		buf.WriteString(bestPracticesSection)
	}

	// Add related resources section
	resourcesSection := getRelatedResourcesSection(moduleName, metadata)
	if resourcesSection != "" {
		buf.WriteString(resourcesSection)
	}

	buf.WriteString("---\n\n*Documentation generated automatically from Go source code.*\n")

	outputPath := filepath.Join(docsRoot, mapping.Target)
	if err := os.MkdirAll(filepath.Dir(outputPath), 0o755); err != nil {
		return err
	}
	return os.WriteFile(outputPath, buf.Bytes(), 0o644)
}

func loadPackageDoc(projectRoot, relPath string) (*packageDoc, error) {
	if pkg, ok := packageCache[relPath]; ok {
		return pkg, nil
	}

	dir := filepath.Join(projectRoot, relPath)
	fset := token.NewFileSet()
	// Filter out test files (*_test.go) to exclude test functions from documentation
	filter := func(fi os.FileInfo) bool {
		return !strings.HasSuffix(fi.Name(), "_test.go")
	}
	pkgs, err := parser.ParseDir(fset, dir, filter, parser.ParseComments)
	if err != nil {
		return nil, fmt.Errorf("parse package %s: %w", relPath, err)
	}

	var first *ast.Package
	for _, pkg := range pkgs {
		first = pkg
		break
	}
	if first == nil {
		return nil, fmt.Errorf("no Go package found in %s", relPath)
	}

	docPkg := doc.New(first, "./", doc.AllDecls)
	packageCache[relPath] = &packageDoc{doc: docPkg, fset: fset}
	return packageCache[relPath], nil
}

func selectTypes(docPkg *doc.Package, mapping docMapping) ([]*doc.Type, error) {
	if mapping.IncludeAllTypes {
		return docPkg.Types, nil
	}
	if len(mapping.TypeNames) == 0 {
		return nil, nil
	}

	index := make(map[string]*doc.Type)
	for _, typ := range docPkg.Types {
		index[typ.Name] = typ
	}

	selected := make([]*doc.Type, 0, len(mapping.TypeNames))
	for _, name := range mapping.TypeNames {
		typ, ok := index[name]
		if !ok {
			return nil, fmt.Errorf("type %s not found in package %s", name, mapping.PackagePath)
		}
		selected = append(selected, typ)
	}
	return selected, nil
}

func selectFuncs(docPkg *doc.Package, mapping docMapping) ([]*doc.Func, error) {
	if mapping.IncludeAllFuncs {
		return docPkg.Funcs, nil
	}
	if len(mapping.FuncNames) == 0 {
		return nil, nil
	}

	// Build index of all functions (both package-level and type-associated)
	index := make(map[string]*doc.Func)

	// Add package-level functions
	for _, fn := range docPkg.Funcs {
		index[fn.Name] = fn
	}

	// Add type-associated functions (constructors and factory functions)
	for _, typ := range docPkg.Types {
		for _, fn := range typ.Funcs {
			index[fn.Name] = fn
		}
	}

	selected := make([]*doc.Func, 0, len(mapping.FuncNames))
	for _, name := range mapping.FuncNames {
		fn, ok := index[name]
		if !ok {
			return nil, fmt.Errorf("function %s not found in package %s", name, mapping.PackagePath)
		}
		selected = append(selected, fn)
	}
	return selected, nil
}

func selectValues(docPkg *doc.Package, names []string) ([]*doc.Value, error) {
	if len(names) == 0 {
		return nil, nil
	}

	wanted := make(map[string]bool)
	for _, name := range names {
		wanted[name] = true
	}

	var results []*doc.Value
	seen := make(map[*doc.Value]bool)
	search := append(append([]*doc.Value{}, docPkg.Consts...), docPkg.Vars...)

	for _, value := range search {
		for _, identifier := range value.Names {
			if wanted[identifier] {
				if !seen[value] {
					results = append(results, value)
					seen[value] = true
				}
				delete(wanted, identifier)
			}
		}
	}

	if len(wanted) > 0 {
		missing := make([]string, 0, len(wanted))
		for name := range wanted {
			missing = append(missing, name)
		}
		sort.Strings(missing)
		return nil, fmt.Errorf("constants or variables %v not found in package %s", missing, docPkg.Name)
	}

	return results, nil
}

// toCamelCase converts snake_case to CamelCase (e.g., get_api_key -> GetApiKey)
func toCamelCase(s string) string {
	parts := strings.Split(s, "_")
	for i, part := range parts {
		if part != "" {
			parts[i] = strings.ToUpper(part[:1]) + strings.ToLower(part[1:])
		}
	}
	return strings.Join(parts, "")
}

// matchesMethodName checks if a method name matches a pattern (supports snake_case and CamelCase)
func matchesMethodName(methodName, pattern string) bool {
	// Direct case-insensitive match
	if strings.EqualFold(methodName, pattern) {
		return true
	}
	// Convert pattern from snake_case to CamelCase and compare
	camelPattern := toCamelCase(pattern)
	if strings.EqualFold(methodName, camelPattern) {
		return true
	}
	return false
}

// shouldSkipMethod checks if a method should be hidden from documentation
func shouldSkipMethod(methodName string, methodDoc string, hiddenMethods []string, autoRules AutoFilterRules) bool {
	// Convert to lowercase for case-insensitive comparison
	lowerName := strings.ToLower(methodName)

	// Check if method is in the explicit hidden methods list
	for _, hidden := range hiddenMethods {
		if matchesMethodName(methodName, hidden) {
			return true
		}
	}

	// Skip methods starting with underscore (private methods)
	if strings.HasPrefix(methodName, "_") {
		return true
	}

	// Apply auto-filter rules

	// 1. Exclude simple getters
	for _, getter := range autoRules.ExcludeSimpleGetters {
		if matchesMethodName(methodName, getter) {
			return true
		}
	}

	// 2. Exclude VPC helpers
	for _, helper := range autoRules.ExcludeVpcHelpers {
		if matchesMethodName(methodName, helper) {
			return true
		}
	}

	// 3. Exclude serialization methods (ToMap, FromMap, etc.)
	for _, serMethod := range autoRules.ExcludeSerializationMethods {
		if matchesMethodName(methodName, serMethod) {
			return true
		}
	}

	// 4. Exclude marshal/unmarshal methods
	for _, marshalMethod := range autoRules.ExcludeMarshalMethods {
		if matchesMethodName(methodName, marshalMethod) {
			return true
		}
	}

	// 5. Exclude lowercase methods (Go convention: lowercase = package-private)
	if autoRules.ExcludeLowercaseMethods {
		if len(methodName) > 0 && methodName[0] >= 'a' && methodName[0] <= 'z' {
			return true
		}
	}

	// 6. Exclude validation methods (starting with Validate or containing validate)
	if autoRules.ExcludeValidationMethods {
		if strings.HasPrefix(lowerName, "validate") ||
			strings.Contains(lowerName, "_validate") ||
			strings.HasSuffix(lowerName, "validate") {
			return true
		}
	}

	// 7. Exclude internal helpers (check docstring for "internal" or "helper")
	if autoRules.ExcludeInternalHelpers && methodDoc != "" {
		lowerDoc := strings.ToLower(methodDoc)
		if strings.Contains(lowerDoc, "internal") || strings.Contains(lowerDoc, "helper") {
			return true
		}
	}

	return false
}

func writeType(buf *bytes.Buffer, pkg *packageDoc, typ *doc.Type, mapping docMapping, autoRules AutoFilterRules) {
	fmt.Fprintf(buf, "## Type %s\n\n", typ.Name)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, typ.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(typ.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}

	if len(typ.Methods) > 0 {
		// Filter out hidden methods
		visibleMethods := make([]*doc.Func, 0)
		for _, method := range typ.Methods {
			if !shouldSkipMethod(method.Name, method.Doc, mapping.HiddenMethods, autoRules) {
				visibleMethods = append(visibleMethods, method)
			}
		}

		// Only write Methods section if there are visible methods
		if len(visibleMethods) > 0 {
			buf.WriteString("### Methods\n\n")
			for _, method := range visibleMethods {
				fmt.Fprintf(buf, "### %s\n\n", method.Name)
				buf.WriteString("```go\n")
				buf.WriteString(formatNode(pkg.fset, method.Decl))
				buf.WriteString("\n```\n\n")
				if text := formatComment(method.Doc); text != "" {
					buf.WriteString(text)
					buf.WriteString("\n\n")
				}
			}
		}
	}

	if len(typ.Funcs) > 0 {
		// Filter out hidden functions (apply same rules as methods)
		visibleFuncs := make([]*doc.Func, 0)
		for _, fn := range typ.Funcs {
			if !shouldSkipMethod(fn.Name, fn.Doc, mapping.HiddenMethods, autoRules) {
				visibleFuncs = append(visibleFuncs, fn)
			}
		}

		// Only write Related Functions section if there are visible functions
		if len(visibleFuncs) > 0 {
			buf.WriteString("### Related Functions\n\n")
			for _, fn := range visibleFuncs {
				fmt.Fprintf(buf, "### %s\n\n", fn.Name)
				buf.WriteString("```go\n")
				buf.WriteString(formatNode(pkg.fset, fn.Decl))
				buf.WriteString("\n```\n\n")
				if text := formatComment(fn.Doc); text != "" {
					buf.WriteString(text)
					buf.WriteString("\n\n")
				}
			}
		}
	}
}

func writeFunc(buf *bytes.Buffer, pkg *packageDoc, fn *doc.Func) {
	fmt.Fprintf(buf, "### %s\n\n", fn.Name)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, fn.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(fn.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}
}

func writeValue(buf *bytes.Buffer, pkg *packageDoc, val *doc.Value) {
	title := strings.Join(val.Names, ", ")
	fmt.Fprintf(buf, "### %s\n\n", title)
	buf.WriteString("```go\n")
	buf.WriteString(formatNode(pkg.fset, val.Decl))
	buf.WriteString("\n```\n\n")
	if text := formatComment(val.Doc); text != "" {
		buf.WriteString(text)
		buf.WriteString("\n\n")
	}
}

func formatNode(fset *token.FileSet, node ast.Node) string {
	var buf bytes.Buffer
	if err := printer.Fprint(&buf, fset, node); err != nil {
		return ""
	}
	return buf.String()
}

func formatComment(comment string) string {
	comment = strings.TrimSpace(comment)
	if comment == "" {
		return ""
	}
	var buf bytes.Buffer
	doc.ToText(&buf, comment, "", "\n", 100)
	text := strings.TrimSpace(buf.String())

	// Process the text to wrap code examples in markdown code blocks
	return wrapCodeExamples(text)
}

func wrapCodeExamples(text string) string {
	lines := strings.Split(text, "\n")
	var result strings.Builder
	inCodeBlock := false
	var codeLines []string

	for i := 0; i < len(lines); i++ {
		line := lines[i]
		trimmedLine := strings.TrimSpace(line)

		// Detect "Example:" line
		if !inCodeBlock && trimmedLine == "Example:" {
			result.WriteString("**Example:**\n\n")

			// Skip all empty lines after "Example:"
			i++
			for i < len(lines) && strings.TrimSpace(lines[i]) == "" {
				i++
			}

			// Start code block and continue until end of comment
			if i < len(lines) {
				inCodeBlock = true
				codeLines = []string{}
				i-- // Reprocess this line in code block mode
			}
			continue
		}

		if inCodeBlock {
			// Collect all code lines
			codeLines = append(codeLines, line)
		} else {
			result.WriteString(line)
			result.WriteString("\n")
		}
	}

	// Process and write code block if we collected any
	if inCodeBlock && len(codeLines) > 0 {
		result.WriteString("```go\n")

		// Clean up excessive empty lines in code
		// Keep empty lines only between major sections (comments, imports, functions)
		prevEmpty := false
		prevWasComment := false

		for i, line := range codeLines {
			trimmed := strings.TrimSpace(line)
			isEmpty := trimmed == ""
			isComment := strings.HasPrefix(trimmed, "//")

			// Determine if we should keep this empty line
			keepEmptyLine := false
			if isEmpty {
				// Look at next non-empty line
				nextLine := ""
				for j := i + 1; j < len(codeLines); j++ {
					next := strings.TrimSpace(codeLines[j])
					if next != "" {
						nextLine = next
						break
					}
				}

				// Keep empty line before comments or after closing braces
				if strings.HasPrefix(nextLine, "//") || prevWasComment {
					keepEmptyLine = true
				}
			}

			// Skip consecutive empty lines or unnecessary empty lines
			if isEmpty {
				if prevEmpty || !keepEmptyLine {
					prevEmpty = true
					continue
				}
			}

			result.WriteString(line)
			result.WriteString("\n")
			prevEmpty = isEmpty
			prevWasComment = isComment
		}

		// Remove trailing empty lines
		resultStr := result.String()
		for strings.HasSuffix(resultStr, "\n\n") {
			resultStr = strings.TrimSuffix(resultStr, "\n")
		}
		return strings.TrimSpace(resultStr) + "\n```"
	}

	return strings.TrimSpace(result.String())
}

func writeReadme(docsRoot string) error {
	sections := map[string][]docMapping{}
	for _, mapping := range mappings {
		section := strings.Split(mapping.Target, "/")[0]
		sections[section] = append(sections[section], mapping)
	}

	keys := make([]string, 0, len(sections))
	for key := range sections {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	var buf bytes.Buffer
	buf.WriteString("# AgentBay Go SDK API Reference\n\n")
	buf.WriteString("This directory is generated. Run `go run scripts/generate_api_docs.go` to refresh it.\n\n")

	for _, key := range keys {
		buf.WriteString(fmt.Sprintf("## %s\n\n", formatSectionTitle(key)))
		for _, mapping := range sections[key] {
			buf.WriteString(fmt.Sprintf("- `%s` – %s\n", mapping.Target, mapping.Title))
		}
		buf.WriteString("\n")
	}

	readmePath := filepath.Join(docsRoot, "README.md")
	return os.WriteFile(readmePath, buf.Bytes(), 0o644)
}

func formatSectionTitle(segment string) string {
	parts := strings.Split(segment, "-")
	for i, part := range parts {
		if part == "" {
			continue
		}
		parts[i] = strings.ToUpper(part[:1]) + strings.ToLower(part[1:])
	}
	return strings.Join(parts, " ")
}
