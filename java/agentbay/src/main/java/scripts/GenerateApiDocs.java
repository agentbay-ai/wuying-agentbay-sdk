package scripts;

import com.github.javaparser.JavaParser;
import com.github.javaparser.ParseResult;
import com.github.javaparser.ast.CompilationUnit;
import com.github.javaparser.ast.body.*;
import com.github.javaparser.ast.comments.JavadocComment;
import com.github.javaparser.javadoc.Javadoc;
import com.github.javaparser.javadoc.JavadocBlockTag;
import com.github.javaparser.javadoc.description.JavadocDescription;
import com.github.javaparser.symbolsolver.JavaSymbolSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.CombinedTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.ReflectionTypeSolver;
import com.github.javaparser.symbolsolver.resolution.typesolvers.JavaParserTypeSolver;
import org.yaml.snakeyaml.Yaml;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.regex.*;
import java.util.stream.Collectors;

/**
 * Generate API reference documentation for Java SDK using JavaParser + custom Markdown conversion
 * 
 * This script:
 * 1. Uses JavaParser to directly parse Java source files and extract AST information
 * 2. Converts AST data to custom Markdown format
 * 3. Organizes documentation by modules similar to Python/TypeScript/Golang SDKs
 * 
 * Usage: java -cp ".:target/classes" scripts.GenerateApiDocs
 */
public class GenerateApiDocs {
    
    // Get current working directory
    private static final String CURRENT_DIR = System.getProperty("user.dir");
    // If running in agentbay directory, JAVA_ROOT should be its parent directory
    private static final String JAVA_ROOT = CURRENT_DIR.endsWith("agentbay") ? 
        Paths.get(CURRENT_DIR).getParent().toString() : CURRENT_DIR;
    // Project root: the directory containing docs and scripts
    // Since JAVA_ROOT is the java directory (e.g., D:/innerIntenet/current/wuying-agentbay-sdk/java),
    // PROJECT_ROOT should be its parent (e.g., D:/innerIntenet/current/wuying-agentbay-sdk)
    private static final String PROJECT_ROOT = Paths.get(JAVA_ROOT).getParent().toString();
    // Documentation output directory: java/docs/api
    private static final String DOCS_ROOT = JAVA_ROOT + "/docs/api";
    // Source code directory: java/agentbay/src/main/java/com/aliyun/agentbay
    private static final String SRC_ROOT = JAVA_ROOT + "/agentbay/src/main/java/";
    // Metadata file path: scripts/doc-metadata.yaml under project root
    private static final String METADATA_PATH = PROJECT_ROOT + "/scripts/doc-metadata.yaml";
    
    // JavaParser instance with symbol solver
    private JavaParser javaParser;
    
    // Documentation metadata loaded from YAML
    private DocumentationMetadata metadata;
    private List<DocMapping> docMappings;
    
    public static void main(String[] args) {
        try {
            GenerateApiDocs generator = new GenerateApiDocs();
            
            // Parse command line arguments
            boolean validateLinks = false;
            boolean validateOnly = false;
            
            for (String arg : args) {
                if ("--validate-links".equals(arg)) {
                    validateLinks = true;
                } else if ("--validate-only".equals(arg)) {
                    validateOnly = true;
                    validateLinks = true;
                }
            }
            
            if (validateOnly) {
                // Only run validation without generating docs
                System.out.println("🔍 Running documentation validation only...");
                boolean validationPassed = generator.validateDocumentation();
                if (validationPassed) {
                    System.out.println("Documentation validation passed!");
                    System.exit(0);
                } else {
                    System.out.println("Documentation validation failed!");
                    System.exit(1);
                }
            } else {
                // Generate documentation
                generator.generateDocumentation();
                
                // Optionally validate generated documentation
                if (validateLinks) {
                    System.out.println("\n🔍 Validating generated documentation...");
                    boolean validationPassed = generator.validateDocumentation();
                    if (!validationPassed) {
                        System.out.println("⚠️ Documentation generated but validation found issues!");
                        System.exit(1);
                    }
                }
                
                System.out.println("Java API documentation generated successfully!");
            }
        } catch (Exception e) {
            System.err.println("Failed to generate Java API documentation: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    public void generateDocumentation() throws Exception {
        System.out.println("Starting Java API documentation generation with JavaParser...");
        
        // Step 1: Initialize JavaParser with symbol solver
        initializeJavaParser();
        
        // Step 2: Load metadata configuration
        loadMetadata();
        
        // Step 3: Generate documentation mappings from metadata
        generateDocMappings();
        
        // Step 4: Clean and prepare output directory
        cleanDocsDirectory();
        
        // Step 5: Parse Java source files and generate Markdown documentation
        parseSourceFilesAndGenerateMarkdown();

        // Step 6: Write API README entry point
        System.out.println("Step 6: Writing API README...");
        writeApiReadme();
        System.out.println("Step 6 completed: API README written");
        
        System.out.println("Java API documentation generation completed!");
    }
    
    /**
     * Initialize JavaParser with symbol solver for better type resolution
     */
    private void initializeJavaParser() {
        System.out.println("Initializing JavaParser with symbol solver...");
        
        // Set up type solvers
        CombinedTypeSolver combinedTypeSolver = new CombinedTypeSolver();
        combinedTypeSolver.add(new ReflectionTypeSolver());
        
        // Add source directory to type solver
        Path srcPath = Paths.get(SRC_ROOT);
        if (Files.exists(srcPath)) {
            combinedTypeSolver.add(new JavaParserTypeSolver(srcPath));
        } else {
            System.err.println("Warning: Source directory not found: " + srcPath);
        }
        
        // Create JavaSymbolSolver
        JavaSymbolSolver symbolSolver = new JavaSymbolSolver(combinedTypeSolver);
        
        // Configure JavaParser
        this.javaParser = new JavaParser();
        this.javaParser.getParserConfiguration().setSymbolResolver(symbolSolver);
        
        System.out.println("JavaParser initialized successfully");
    }
    
    /**
     * Parse Java source files and generate Markdown documentation using JavaParser
     */
    private void parseSourceFilesAndGenerateMarkdown() throws Exception {
        System.out.println("Parsing Java source files and generating Markdown documentation...");
        
        for (DocMapping mapping : docMappings) {
            try {
                generateMarkdownForMappingWithJavaParser(mapping);
                System.out.println("  Generated: " + mapping.target);
            } catch (Exception e) {
                System.err.println("  Failed to generate " + mapping.target + ": " + e.getMessage());
                // Continue with other mappings
            }
        }
    }
    
    /**
     * Generate Markdown documentation for a mapping using JavaParser
     */
    private void generateMarkdownForMappingWithJavaParser(DocMapping mapping) throws Exception {
        StringBuilder markdown = new StringBuilder();
        
        // Add title with emoji if available - format as "ClassName API Reference"
        String baseTitle = mapping.title + " API Reference";
        String title = mapping.config != null && mapping.config.emoji != null 
            ? mapping.config.emoji + " " + baseTitle 
            : baseTitle;
        markdown.append("# ").append(title).append("\n\n");
        
        // Add overview - either from config or generate default
        markdown.append("## Overview\n\n");
        if (mapping.config != null && mapping.config.overview != null && !mapping.config.overview.trim().isEmpty()) {
            markdown.append(mapping.config.overview).append("\n\n");
        } else {
            // Generate default overview based on module name and classes
            String defaultOverview = generateDefaultOverview(mapping);
            markdown.append(defaultOverview).append("\n\n");
        }
        
        // Add tutorial link if available
        if (mapping.config != null && mapping.config.tutorial != null) {
            markdown.append("## 📚 Tutorial\n\n");
            markdown.append("[").append(mapping.config.tutorial.text).append("](")
                    .append(mapping.config.tutorial.url).append(")\n\n");
            if (mapping.config.tutorial.description != null) {
                markdown.append(mapping.config.tutorial.description).append("\n\n");
            }
        }
        
        // Add requirements if available
        if (mapping.config != null && mapping.config.requirements != null && !mapping.config.requirements.isEmpty()) {
            markdown.append("## 📋 Requirements\n\n");
            for (String requirement : mapping.config.requirements) {
                markdown.append("- ").append(requirement).append("\n");
            }
            markdown.append("\n");
        }
        
        // Process each class in the mapping using JavaParser
        for (String className : mapping.classNames) {
            try {
                String classMarkdown = generateMarkdownForClassWithJavaParser(className, mapping.config);
                if (!classMarkdown.isEmpty()) {
                    markdown.append(classMarkdown).append("\n\n");
                }
            } catch (Exception e) {
                System.err.println("    Failed to process class " + className + ": " + e.getMessage());
            }
        }
        
        // Add best practices if available
        if (mapping.config != null && mapping.config.bestPractices != null && !mapping.config.bestPractices.isEmpty()) {
            markdown.append("## 💡 Best Practices\n\n");
            for (String practice : mapping.config.bestPractices) {
                markdown.append("- ").append(practice).append("\n");
            }
            markdown.append("\n");
        }
        
        // Add related resources if available
        if (mapping.config != null && mapping.config.relatedResources != null && !mapping.config.relatedResources.isEmpty()) {
            markdown.append("## 🔗 Related Resources\n\n");
            for (RelatedResource resource : mapping.config.relatedResources) {
                String resourcePath = resource.category != null 
                    ? generateRelativePathForResource(mapping.target, resource.category, resource.module)
                    : generateRelativePathForResource(mapping.target, null, resource.module);
                markdown.append("- [").append(resource.name).append("](").append(resourcePath).append(")\n");
            }
            markdown.append("\n");
        }
        
        // Write to file with UTF-8 encoding
        Path targetPath = Paths.get(DOCS_ROOT, mapping.target);
        Files.createDirectories(targetPath.getParent());
        Files.write(targetPath, markdown.toString().getBytes("UTF-8"));
    }
    
      /**
     * Generate relative path for a resource based on the current document path
     * 
     * @param currentDocumentPath The path of the current document (relative path from docs/api)
     * @param category The category of the resource (can be null)
     * @param module The module name of the resource
     * @return The relative path to the resource
     */
    private String generateRelativePathForResource(String currentDocumentPath, String category, String module) {
        // Get the absolute path of the current document
        Path currentDocAbsolutePath = Paths.get(DOCS_ROOT, currentDocumentPath);
        
        // Find the docs directory by traversing up from the current document
        Path docsDir = findDocsDirectory(currentDocAbsolutePath);
        
        if (docsDir == null) {
            // Fallback: if docs directory not found, use current logic
            String normalizedPath = currentDocumentPath.replace('\\', '/');
            String[] pathSegments = normalizedPath.split("/");
            int depth = pathSegments.length - 1;
            StringBuilder relativePrefix = new StringBuilder();
            for (int i = 0; i < depth; i++) {
                relativePrefix.append("../");
            }
            if (category != null) {
                return relativePrefix.toString() + category + "/" + module + ".md";
            } else {
                return relativePrefix.toString() + module + ".md";
            }
        }
        
        // Calculate the number of "../" needed to go from current document to docs directory
        int levelsToDocs = calculateLevelsUp(currentDocAbsolutePath, docsDir);
        
        // Build the relative path prefix with the correct number of "../"
        StringBuilder relativePrefix = new StringBuilder();
        for (int i = 0; i < levelsToDocs; i++) {
            relativePrefix.append("../");
        }
        
        // Construct the full resource path starting from docs directory
        // The target path should be: docs/api/{category}/{module}.md
        // But since we're already at docs level, we need to go into api directory
        if (category != null) {
            return relativePrefix.toString() + "api/" + category + "/" + module + ".md";
        } else {
            return relativePrefix.toString() + "api/" + module + ".md";
        }
    }
    
    /**
     * Find the docs directory by traversing up from the current document path
     */
    private Path findDocsDirectory(Path currentPath) {
        Path path = currentPath.getParent();
        int maxLevels = 10; // Prevent infinite loops
        int levels = 0;
        
        while (path != null && levels < maxLevels) {
            if (path.getFileName() != null && path.getFileName().toString().equals("docs")) {
                return path;
            }
            path = path.getParent();
            levels++;
        }
        
        return null;
    }
    
    /**
     * Calculate the number of levels up from current path to target path
     */
    private int calculateLevelsUp(Path currentPath, Path targetPath) {
        Path current = currentPath.getParent();
        int levels = 0;
        int maxLevels = 10; // Prevent infinite loops
        
        while (current != null && !current.equals(targetPath) && levels < maxLevels) {
            current = current.getParent();
            levels++;
        }
        
        return levels;
    }
    
    /**
     * Generate Markdown documentation for a class using JavaParser
     */
    private String generateMarkdownForClassWithJavaParser(String className, ModuleConfig config) throws Exception {
        // Convert class name to file path
        String filePath = className.replace(".", "/") + ".java";
        Path sourceFile = Paths.get(SRC_ROOT, filePath);
        
        if (!Files.exists(sourceFile)) {
            System.err.println("    Source file not found for class: " + className + " at " + sourceFile);
            return "";
        }
        
        // Parse the Java file
        ParseResult<CompilationUnit> parseResult = javaParser.parse(sourceFile);
        if (!parseResult.isSuccessful()) {
            System.err.println("    Failed to parse source file: " + sourceFile);
            return "";
        }
        
        CompilationUnit cu = parseResult.getResult().get();
        StringBuilder markdown = new StringBuilder();
        
        // Find the main class in the compilation unit
        Optional<ClassOrInterfaceDeclaration> classDecl = cu.findFirst(ClassOrInterfaceDeclaration.class, 
            cls -> cls.getNameAsString().equals(className.substring(className.lastIndexOf('.') + 1)));
        
        if (classDecl.isPresent()) {
            ClassOrInterfaceDeclaration cls = classDecl.get();
            markdown.append(generateMarkdownForSingleClass(cls, config));

            // Also process inner classes (e.g., Agent.Computer, Agent.Browser, Agent.Mobile)
            List<ClassOrInterfaceDeclaration> innerClasses = cls.getMembers().stream()
                .filter(m -> m instanceof ClassOrInterfaceDeclaration)
                .map(m -> (ClassOrInterfaceDeclaration) m)
                .filter(ClassOrInterfaceDeclaration::isPublic)
                .collect(Collectors.toList());

            for (ClassOrInterfaceDeclaration inner : innerClasses) {
                markdown.append(generateMarkdownForSingleClass(inner, config));
            }
        }
        
        return markdown.toString();
    }
    
    /**
     * Generate Markdown documentation for a single class declaration (top-level or inner).
     */
    private String generateMarkdownForSingleClass(ClassOrInterfaceDeclaration cls, ModuleConfig config) {
        StringBuilder markdown = new StringBuilder();
        String simpleClassName = cls.getNameAsString();

        markdown.append("## ").append(simpleClassName).append("\n\n");

        if (cls.getJavadocComment().isPresent()) {
            JavadocComment javadocComment = cls.getJavadocComment().get();
            Javadoc javadoc = javadocComment.parse();
            String description = extractJavadocDescription(javadoc);
            if (!description.isEmpty()) {
                markdown.append(description).append("\n\n");
            }
        }

        List<ConstructorDeclaration> constructors = cls.getConstructors().stream()
            .filter(constructor -> shouldIncludeConstructor(constructor, config))
            .collect(Collectors.toList());

        if (!constructors.isEmpty()) {
            markdown.append("### Constructor\n\n");
            for (ConstructorDeclaration constructor : constructors) {
                markdown.append(generateConstructorMarkdown(constructor));
            }
        }

        List<MethodDeclaration> allMethods = cls.getMethods();
        List<MethodDeclaration> publicMethods = allMethods.stream()
            .filter(MethodDeclaration::isPublic)
            .collect(Collectors.toList());

        List<MethodDeclaration> methods = publicMethods.stream()
            .filter(method -> !shouldSkipMethod(method.getNameAsString(), config))
            .collect(Collectors.toList());

        if (!methods.isEmpty()) {
            Map<String, List<MethodDeclaration>> methodGroups = groupMethods(methods);

            for (Map.Entry<String, List<MethodDeclaration>> group : methodGroups.entrySet()) {
                markdown.append("### ").append(group.getKey()).append("\n\n");

                Map<String, List<MethodDeclaration>> methodsByName = group.getValue().stream()
                    .collect(Collectors.groupingBy(MethodDeclaration::getNameAsString, LinkedHashMap::new, Collectors.toList()));

                for (Map.Entry<String, List<MethodDeclaration>> methodGroup : methodsByName.entrySet()) {
                    markdown.append(generateMethodGroupMarkdown(methodGroup.getValue()));
                }
            }
        }

        return markdown.toString();
    }

    /**
     * Generate default overview for a module when no overview is provided in config
     */
    private String generateDefaultOverview(DocMapping mapping) {
        StringBuilder overview = new StringBuilder();
        
        String moduleName = mapping.title;
        
        // Generate overview based on module type
        if (moduleName.toLowerCase().contains("session")) {
            overview.append("The Session class represents an active cloud environment instance in AgentBay. ");
            overview.append("It provides access to all service modules (filesystem, command, browser, code, etc.) ");
            overview.append("and manages the lifecycle of the cloud environment.");
        } else if (moduleName.toLowerCase().contains("browser")) {
            overview.append("The Browser module provides browser automation capabilities using Playwright integration. ");
            overview.append("It enables web scraping, automated testing, form filling, and other browser-based automation tasks in a cloud environment.");
        } else if (moduleName.toLowerCase().contains("agentbay")) {
            overview.append("The AgentBay class is the main entry point for the AgentBay Java SDK. ");
            overview.append("It provides methods to create and manage cloud sessions, configure authentication, and access various cloud services.");
        } else if (moduleName.toLowerCase().contains("code")) {
            overview.append("The Code module provides capabilities for executing Python, JavaScript, R, and Java code in isolated cloud environments. ");
            overview.append("This is useful for running untrusted code, data processing, testing, and automation tasks.");
        } else if (moduleName.toLowerCase().contains("file")) {
            overview.append("The FileSystem module provides comprehensive file and directory operations in the cloud environment. ");
            overview.append("It supports reading, writing, uploading, downloading, and managing files and directories.");
        } else if (moduleName.toLowerCase().contains("command")) {
            overview.append("The Command module enables execution of shell commands and scripts in the cloud environment. ");
            overview.append("It provides both synchronous and asynchronous execution capabilities with timeout and output handling.");
        } else {
            // Generic overview
            overview.append("The ").append(moduleName).append(" module provides specialized functionality for the AgentBay cloud platform. ");
            overview.append("It includes various methods and utilities to interact with cloud services and manage resources.");
        }
        
        return overview.toString();
    }
    
    /**
     * Capitalize the first letter of a string
     */
    private String capitalizeFirstLetter(String str) {
        if (str == null || str.isEmpty()) {
            return str;
        }
        return str.substring(0, 1).toUpperCase() + str.substring(1);
    }
    
    /**
     * Group methods by category for better organization
     */
    private Map<String, List<MethodDeclaration>> groupMethods(List<MethodDeclaration> methods) {
        Map<String, List<MethodDeclaration>> groups = new LinkedHashMap<>();
        
        for (MethodDeclaration method : methods) {
            String methodName = method.getNameAsString();
            String category = categorizeMethod(methodName, method);
            
            groups.computeIfAbsent(category, k -> new ArrayList<>()).add(method);
        }
        
        return groups;
    }
    
    /**
     * Categorize a method based on its name and characteristics
     * All methods that pass the YAML filtering are considered Key Methods
     */
    private String categorizeMethod(String methodName, MethodDeclaration method) {
        // All scanned APIs are Key Methods - filtering is handled by YAML configuration
        return "Methods";
    }
    
    /**
     * Extract description from Javadoc
     */
    private String extractJavadocDescription(Javadoc javadoc) {
        JavadocDescription description = javadoc.getDescription();
        return description.toText().trim();
    }
    
    /**
     * Generate Markdown for a constructor
     */
    private String generateConstructorMarkdown(ConstructorDeclaration constructor) {
        StringBuilder markdown = new StringBuilder();
        
        // Constructor signature in code block with full modifiers
        String signature = constructor.getDeclarationAsString(true, true, true);
        markdown.append("```java\n").append(signature).append("\n```\n\n");
        
        // Constructor description from Javadoc
        if (constructor.getJavadocComment().isPresent()) {
            JavadocComment javadocComment = constructor.getJavadocComment().get();
            Javadoc javadoc = javadocComment.parse();
            String description = extractJavadocDescription(javadoc);
            if (!description.isEmpty()) {
                markdown.append(description).append("\n\n");
            }
            
            // Add parameter descriptions
            List<JavadocBlockTag> paramTags = javadoc.getBlockTags().stream()
                .filter(tag -> tag.getType() == JavadocBlockTag.Type.PARAM)
                .collect(Collectors.toList());
            
            if (!paramTags.isEmpty()) {
                markdown.append("**Parameters:**\n");
                for (JavadocBlockTag paramTag : paramTags) {
                    String paramName = paramTag.getName().orElse("");
                    String paramDesc = paramTag.getContent().toText();
                    String paramType = getConstructorParameterType(constructor, paramName);
                    markdown.append("- `").append(paramName).append("` (").append(paramType).append("): ").append(paramDesc).append("\n");
                }
                markdown.append("\n");
            }
        }
        
        return markdown.toString();
    }
    
    /**
     * Get parameter type for a constructor parameter
     */
    private String getConstructorParameterType(ConstructorDeclaration constructor, String paramName) {
        return constructor.getParameters().stream()
            .filter(param -> param.getNameAsString().equals(paramName))
            .map(param -> param.getType().asString())
            .findFirst()
            .orElse("Object");
    }
    
    /**
     * Generate Markdown for a group of overloaded methods with the same name
     */
    private String generateMethodGroupMarkdown(List<MethodDeclaration> methods) {
        if (methods.isEmpty()) {
            return "";
        }
        
        StringBuilder markdown = new StringBuilder();
        String methodName = methods.get(0).getNameAsString();
        
        // Method header with name only (once for all overloads)
        markdown.append("### ").append(methodName).append("\n\n");
        
        // Show all method signatures together
        for (MethodDeclaration method : methods) {
            String signature = method.getDeclarationAsString(true, true, true);
            markdown.append("```java\n").append(signature).append("\n```\n\n");
        }
        
        // Find the primary method (most complex) for detailed documentation
        MethodDeclaration primaryMethod = findPrimaryMethod(methods);
        
        // Add method description from primary method's Javadoc
        if (primaryMethod.getJavadocComment().isPresent()) {
            JavadocComment javadocComment = primaryMethod.getJavadocComment().get();
            Javadoc javadoc = javadocComment.parse();
            String description = extractJavadocDescription(javadoc);
            if (!description.isEmpty()) {
                markdown.append(description).append("\n\n");
            }
            
            // Add parameter descriptions from primary method
            List<JavadocBlockTag> paramTags = javadoc.getBlockTags().stream()
                .filter(tag -> tag.getType() == JavadocBlockTag.Type.PARAM)
                .collect(Collectors.toList());
            
            if (!paramTags.isEmpty()) {
                markdown.append("**Parameters:**\n");
                for (JavadocBlockTag paramTag : paramTags) {
                    String paramName = paramTag.getName().orElse("");
                    String paramDesc = paramTag.getContent().toText();
                    markdown.append("- `").append(paramName).append("` (").append(getParameterType(primaryMethod, paramName)).append("): ").append(paramDesc).append("\n");
                }
                markdown.append("\n");
            }
            
            // Add return description
            Optional<JavadocBlockTag> returnTag = javadoc.getBlockTags().stream()
                .filter(tag -> tag.getType() == JavadocBlockTag.Type.RETURN)
                .findFirst();
            
            if (returnTag.isPresent()) {
                String returnDesc = returnTag.get().getContent().toText();
                String returnType = primaryMethod.getType().asString();
                markdown.append("**Returns:**\n- `").append(returnType).append("`: ").append(returnDesc).append("\n\n");
            }
            
            // Add throws descriptions
            List<JavadocBlockTag> throwsTags = javadoc.getBlockTags().stream()
                .filter(tag -> tag.getType() == JavadocBlockTag.Type.THROWS)
                .collect(Collectors.toList());
            
            if (!throwsTags.isEmpty()) {
                markdown.append("**Throws:**\n");
                for (JavadocBlockTag throwsTag : throwsTags) {
                    String exceptionName = throwsTag.getName().orElse("");
                    String exceptionDesc = throwsTag.getContent().toText();
                    markdown.append("- `").append(exceptionName).append("`: ").append(exceptionDesc).append("\n");
                }
                markdown.append("\n");
            }
        }
        
        
        return markdown.toString();
    }
    
    /**
     * Find the primary method among overloads (most parameters and complexity)
     */
    private MethodDeclaration findPrimaryMethod(List<MethodDeclaration> methods) {
        return methods.stream()
            .max(Comparator.comparingInt((MethodDeclaration m) -> m.getParameters().size())
                 .thenComparingInt(this::calculateParameterComplexity))
            .orElse(methods.get(0));
    }

    
    /**
     * Get parameter type for a given parameter name
     */
    private String getParameterType(MethodDeclaration method, String paramName) {
        return method.getParameters().stream()
            .filter(param -> param.getNameAsString().equals(paramName))
            .map(param -> param.getType().asString())
            .findFirst()
            .orElse("Object");
    }
    
    
    
    
    /**
     * Calculate parameter complexity score for overload prioritization
     */
    private int calculateParameterComplexity(MethodDeclaration method) {
        int complexity = 0;
        for (Parameter param : method.getParameters()) {
            String typeName = param.getType().asString();
            if (typeName.contains("Map") || typeName.contains("List")) {
                complexity += 3;
            } else if (typeName.contains("Config") || typeName.contains("Params")) {
                complexity += 2;
            } else if (!typeName.equals("String") && !typeName.equals("int") && !typeName.equals("boolean")) {
                complexity += 1;
            }
        }
        return complexity;
    }
    
    /**
     * Check if a constructor should be included in documentation
     */
    private boolean shouldIncludeConstructor(ConstructorDeclaration constructor, ModuleConfig config) {
        // Include all public constructors by default
        return constructor.isPublic();
    }
    
    /**
     * Check if a method should be excluded from documentation
     */
    private boolean shouldSkipMethod(String methodName, ModuleConfig config) {
        // Java-specific exclusions from global YAML configuration
        if (metadata.global != null && metadata.global.javaConfig != null) {
            JavaConfig javaConfig = metadata.global.javaConfig;

            if (javaConfig.excludeObjectMethods != null && javaConfig.excludeObjectMethods.contains(methodName)) {
                return true;
            }

            if (javaConfig.excludeBeanMethods != null && javaConfig.excludeBeanMethods.contains(methodName)) {
                return true;
            }

            if (javaConfig.excludeSerializationMethods != null && javaConfig.excludeSerializationMethods.contains(methodName)) {
                return true;
            }

            if (javaConfig.excludeUtilityMethods != null && javaConfig.excludeUtilityMethods.contains(methodName)) {
                return true;
            }
        }
        
        // Enhanced smart filtering rules (inspired by Python version)
        boolean shouldExclude = shouldExcludeMethodSmart(methodName);
        if (shouldExclude) {
            System.out.println("    -> Skipped by smart filtering: " + methodName);
        } else {
            System.out.println("    -> Method will be included: " + methodName);
        }
        return shouldExclude;
    }
    
    /**
     * Smart method exclusion rules inspired by Python version
     */
    private boolean shouldExcludeMethodSmart(String methodName) {
        // Debug: Log method being checked
        System.out.println("    Checking method for exclusion: " + methodName);
        
        // Rule 1: Simple getter methods (no parameters, starts with 'get')
        if (methodName.startsWith("get") && methodName.length() > 3) {
            // Common simple getters to exclude
            String[] simpleGetters = {
                "getId", "getName", "getType", "getStatus", "getUrl", "getPath",
                "getHost", "getPort", "getTimeout", "getRetries", "getDelay"
            };
            for (String getter : simpleGetters) {
                if (methodName.equals(getter)) {
                    System.out.println("      -> Excluded by Rule 1 (simple getter): " + methodName);
                    return true;
                }
            }
        }
        
        // Rule 2: Validation methods
        if (methodName.startsWith("validate") || methodName.endsWith("Validate") ||
            methodName.startsWith("check") || methodName.endsWith("Check")) {
            System.out.println("      -> Excluded by Rule 2 (validation method): " + methodName);
            return true;
        }
        
        // Rule 3: Internal helper methods
        if (methodName.startsWith("_") || methodName.contains("Internal") || 
            methodName.contains("Helper")) {
            System.out.println("      -> Excluded by Rule 3 (internal helper): " + methodName);
            return true;
        }
        
        // Rule 4: Serialization methods
        String[] serializationMethods = {
            "toMap", "fromMap", "toDict", "fromDict", "toJson", "fromJson",
            "serialize", "deserialize", "marshal", "unmarshal"
        };
        for (String method : serializationMethods) {
            if (methodName.equals(method) || methodName.endsWith(method)) {
                System.out.println("      -> Excluded by Rule 4 (serialization): " + methodName);
                return true;
            }
        }
        
        // Rule 5: Object methods that are typically not useful in documentation
        String[] objectMethods = {
            "equals", "hashCode", "toString", "clone", "finalize",
            "notify", "notifyAll", "getClass"
        };
        for (String method : objectMethods) {
            if (methodName.equals(method)) {
                System.out.println("      -> Excluded by Rule 5 (object method): " + methodName);
                return true;
            }
        }
        
        // Rule 6: Bean/POJO methods
        if (methodName.startsWith("set") && methodName.length() > 3) {
            // Common simple setters to exclude
            String[] simpleSetters = {
                "setId", "setName", "setType", "setStatus", "setUrl", "setPath",
                "setHost", "setPort", "setTimeout", "setRetries", "setDelay"
            };
            for (String setter : simpleSetters) {
                if (methodName.equals(setter)) {
                    System.out.println("      -> Excluded by Rule 6 (simple setter): " + methodName);
                    return true;
                }
            }
        }
        
        System.out.println("      -> Method included: " + methodName);
        return false;
    }
    
    /**
     * Validate generated documentation for link and anchor issues
     * @return true if validation passes, false otherwise
     */
    public boolean validateDocumentation() {
        try {
            System.out.println("🔍 Starting documentation validation...");
            
            List<ValidationError> errors = new ArrayList<>();
            
            // Validate internal links
            errors.addAll(validateInternalLinks());
            
            // Validate anchors
            errors.addAll(validateAnchors());
            
            // Validate cross-references
            errors.addAll(validateCrossReferences());
            
            if (errors.isEmpty()) {
                System.out.println("All documentation validation checks passed!");
                return true;
            } else {
                System.out.println("Found " + errors.size() + " validation issues:");
                for (ValidationError error : errors) {
                    System.out.println("  - " + error.toString());
                }
                return false;
            }
            
        } catch (Exception e) {
            System.err.println("Documentation validation failed: " + e.getMessage());
            e.printStackTrace();
            return false;
        }
    }
    
    /**
     * Validate internal links in generated documentation
     */
    private List<ValidationError> validateInternalLinks() throws IOException {
        List<ValidationError> errors = new ArrayList<>();
        System.out.println("📋 Validating internal links...");
        
        List<Path> markdownFiles = findMarkdownFiles(Paths.get(DOCS_ROOT));
        
        for (Path file : markdownFiles) {
            String content = new String(Files.readAllBytes(file));
            List<MarkdownLink> links = extractLinks(content);
            
            for (MarkdownLink link : links) {
                if (isInternalLink(link.url)) {
                    Path targetPath = resolveInternalLink(file, link.url);
                    
                    if (!Files.exists(targetPath)) {
                        String relativePath = Paths.get(DOCS_ROOT).relativize(file).toString();
                        errors.add(new ValidationError(
                            ValidationError.Type.BROKEN_LINK,
                            relativePath,
                            "Link does not exist: [" + link.text + "](" + link.url + ") -> " + targetPath
                        ));
                    }
                }
            }
        }
        
        System.out.println("  Checked " + markdownFiles.size() + " files for internal links");
        return errors;
    }
    
    /**
     * Validate anchor links in documentation
     */
    private List<ValidationError> validateAnchors() throws IOException {
        List<ValidationError> errors = new ArrayList<>();
        System.out.println("📋 Validating anchor links...");
        
        List<Path> markdownFiles = findMarkdownFiles(Paths.get(DOCS_ROOT));
        Map<Path, Set<String>> fileAnchors = new HashMap<>();
        
        // First pass: collect all anchors in each file
        for (Path file : markdownFiles) {
            String content = new String(Files.readAllBytes(file));
            Set<String> anchors = extractAnchors(content);
            fileAnchors.put(file, anchors);
        }
        
        // Second pass: validate anchor references
        for (Path file : markdownFiles) {
            String content = new String(Files.readAllBytes(file));
            List<MarkdownLink> links = extractLinks(content);
            
            for (MarkdownLink link : links) {
                if (link.url.contains("#")) {
                    String[] parts = link.url.split("#", 2);
                    String filePart = parts[0];
                    String anchor = parts[1];
                    
                    Path targetFile = filePart.isEmpty() ? file : resolveInternalLink(file, filePart);
                    
                    if (Files.exists(targetFile)) {
                        Set<String> targetAnchors = fileAnchors.get(targetFile);
                        if (targetAnchors != null && !targetAnchors.contains(anchor)) {
                            String relativePath = Paths.get(DOCS_ROOT).relativize(file).toString();
                            errors.add(new ValidationError(
                                ValidationError.Type.BROKEN_ANCHOR,
                                relativePath,
                                "Anchor does not exist: [" + link.text + "](" + link.url + ") - anchor '#" + anchor + "' not found"
                            ));
                        }
                    }
                }
            }
        }
        
        System.out.println("  Validated anchors in " + markdownFiles.size() + " files");
        return errors;
    }
    
    /**
     * Validate cross-references between modules
     */
    private List<ValidationError> validateCrossReferences() throws IOException {
        List<ValidationError> errors = new ArrayList<>();
        System.out.println("📋 Validating cross-references...");
        
        // Check if related resources actually exist
        if (metadata != null && metadata.modules != null) {
            for (Map.Entry<String, ModuleConfig> entry : metadata.modules.entrySet()) {
                String moduleName = entry.getKey();
                ModuleConfig config = entry.getValue();
                
                if (config.relatedResources != null) {
                    for (RelatedResource resource : config.relatedResources) {
                        String resourcePath = resource.category != null 
                            ? resource.category + "/" + resource.module + ".md"
                            : resource.module + ".md";
                        
                        Path targetPath = Paths.get(DOCS_ROOT, resourcePath);
                        if (!Files.exists(targetPath)) {
                            errors.add(new ValidationError(
                                ValidationError.Type.BROKEN_CROSS_REFERENCE,
                                moduleName,
                                "Related resource does not exist: " + resource.name + " -> " + resourcePath
                            ));
                        }
                    }
                }
            }
        }
        
        System.out.println("  Validated cross-references");
        return errors;
    }
    
    /**
     * Find all markdown files in a directory
     */
    private List<Path> findMarkdownFiles(Path baseDir) throws IOException {
        if (!Files.exists(baseDir)) {
            return new ArrayList<>();
        }
        
        try (java.util.stream.Stream<Path> stream = Files.walk(baseDir)) {
            return stream
                .filter(Files::isRegularFile)
                .filter(path -> path.toString().endsWith(".md"))
                .collect(Collectors.toList());
        }
    }
    
    /**
     * Extract all markdown links from content
     */
    private List<MarkdownLink> extractLinks(String content) {
        List<MarkdownLink> links = new ArrayList<>();
        Pattern linkPattern = Pattern.compile("\\[([^\\]]*)\\]\\(([^)]+)\\)");
        Matcher matcher = linkPattern.matcher(content);
        
        while (matcher.find()) {
            String text = matcher.group(1);
            String url = matcher.group(2);
            links.add(new MarkdownLink(text, url));
        }
        
        return links;
    }
    
    /**
     * Extract all anchors (headings) from markdown content
     */
    private Set<String> extractAnchors(String content) {
        Set<String> anchors = new HashSet<>();
        Pattern headingPattern = Pattern.compile("^#+\\s+(.+)$", Pattern.MULTILINE);
        Matcher matcher = headingPattern.matcher(content);
        
        while (matcher.find()) {
            String heading = matcher.group(1);
            String anchor = generateAnchor(heading);
            anchors.add(anchor);
        }
        
        return anchors;
    }
    
    /**
     * Generate anchor from heading text (GitHub-style)
     */
    private String generateAnchor(String heading) {
        return heading.toLowerCase()
                     .replaceAll("[^a-z0-9\\s-]", "")
                     .replaceAll("\\s+", "-")
                     .replaceAll("-+", "-")
                     .replaceAll("^-|-$", "");
    }
    
    /**
     * Check if a link is internal (not external URL)
     */
    private boolean isInternalLink(String link) {
        return !link.startsWith("http://") && 
               !link.startsWith("https://") && 
               !link.startsWith("mailto:") &&
               !link.startsWith("#");
    }
    
    /**
     * Resolve internal link to absolute path
     */
    private Path resolveInternalLink(Path baseFile, String link) {
        Path baseDir = baseFile.getParent();
        
        // Remove anchor part
        if (link.contains("#")) {
            link = link.split("#")[0];
        }
        
        // Handle empty link (pure anchor)
        if (link.isEmpty()) {
            return baseFile;
        }
        
        Path targetPath;
        if (link.startsWith("/")) {
            // Absolute path (relative to docs root)
            targetPath = Paths.get(DOCS_ROOT, link.substring(1));
        } else if (link.startsWith("../")) {
            // Handle links that go up from current location
            // These links are relative to the current file location
            String normalizedLink = link.replace("\\", "/");
            targetPath = baseDir.resolve(normalizedLink);
        } else {
            // Relative path - fix potential double separator issue
            // Normalize the link first to handle any mixed separators
            String normalizedLink = link.replace("\\", "/");
            targetPath = baseDir.resolve(normalizedLink);
        }
        
        // Normalize path and convert to absolute path
        targetPath = targetPath.normalize().toAbsolutePath();
        
        // If the resolved path doesn't exist, try alternative resolution
        // This handles cases where relative paths go outside the DOCS_ROOT
        if (!Files.exists(targetPath)) {
            // Try resolving from project root
            Path projectRootPath = Paths.get(PROJECT_ROOT).toAbsolutePath().normalize();
            Path altPath = projectRootPath.resolve(link.replace("\\", "/")).normalize();
            if (Files.exists(altPath)) {
                return altPath;
            }
            
            // Try resolving from docs root
            Path docsRootPath = Paths.get(DOCS_ROOT).toAbsolutePath().normalize();
            altPath = docsRootPath.resolve(link.replace("\\", "/")).normalize();
            if (Files.exists(altPath)) {
                return altPath;
            }
        }
        
        // If it's a directory, try to find README.md
        if (Files.isDirectory(targetPath)) {
            Path readmePath = targetPath.resolve("README.md");
            if (Files.exists(readmePath)) {
                return readmePath;
            }
        }
        
        // Special case: check if the resolved path exists
        // Sometimes normalization can cause issues with paths that do exist
        if (!Files.exists(targetPath)) {
            // Try alternative resolution approach for edge cases
            Path altPath = Paths.get(DOCS_ROOT).resolve(link.replace("\\", "/")).normalize();
            if (Files.exists(altPath)) {
                return altPath;
            }
        }
        
        return targetPath;
    }
    
    private void cleanDocsDirectory() throws IOException {
        Path docsPath = Paths.get(DOCS_ROOT);
        if (Files.exists(docsPath)) {
            deleteDirectory(docsPath);
        }
        Files.createDirectories(docsPath);
        System.out.println("Cleaned and created docs directory: " + DOCS_ROOT);
    }
    
    private void deleteDirectory(Path path) throws IOException {
        if (Files.isDirectory(path)) {
            try (java.util.stream.Stream<Path> stream = Files.list(path)) {
                // Convert to list to avoid issues with concurrent modification
                List<Path> children = stream.collect(Collectors.toList());
                for (Path child : children) {
                    deleteDirectory(child);
                }
            }
        }
        // Use Files.delete instead of deleteIfExists for better error reporting
        if (Files.exists(path)) {
            try {
                Files.delete(path);
            } catch (IOException e) {
                // On Windows, sometimes files are locked, retry after a short delay
                try {
                    Thread.sleep(100);
                    Files.delete(path);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new IOException("Interrupted while deleting: " + path, ie);
                } catch (IOException retryException) {
                    System.err.println("Warning: Failed to delete " + path + ": " + retryException.getMessage());
                    // Continue without throwing exception to avoid blocking the entire process
                }
            }
        }
    }
    
    private void loadMetadata() throws Exception {
        System.out.println("Loading documentation metadata from: " + METADATA_PATH);
        System.out.println("PROJECT_ROOT: " + PROJECT_ROOT);
        
        // Check if metadata file exists
        Path metadataFilePath = Paths.get(METADATA_PATH);
        if (!Files.exists(metadataFilePath)) {
            System.err.println("Metadata file does not exist: " + METADATA_PATH);
            System.err.println("Using fallback configuration");
            this.metadata = createFallbackMetadata();
            return;
        }
        
        Yaml yaml = new Yaml();
        try (FileInputStream fis = new FileInputStream(METADATA_PATH)) {
            Map<String, Object> data = yaml.load(fis);
            
            // Debug: print loaded data structure
            if (data == null) {
                System.err.println("YAML file is empty or null");
                this.metadata = createFallbackMetadata();
                return;
            }
            
            System.out.println("YAML data loaded, keys: " + data.keySet());
            
            this.metadata = new DocumentationMetadata(data);
            System.out.println("Metadata loaded successfully");
        } catch (Exception e) {
            System.err.println("Failed to load metadata, using fallback configuration: " + e.getMessage());
            this.metadata = createFallbackMetadata();
        }
    }
    
    private void generateDocMappings() {
        System.out.println("Generating documentation mappings from metadata...");
        
        this.docMappings = new ArrayList<>();
        
        // Generate mappings based on metadata modules
        for (Map.Entry<String, ModuleConfig> entry : metadata.modules.entrySet()) {
            String moduleName = entry.getKey();
            ModuleConfig config = entry.getValue();
            
            // Generate target path based on category and module name
            String targetPath = generateTargetPath(config.category, moduleName);
            
            // Generate Java class names for this module
            List<String> classNames = generateJavaClassNames(moduleName);
            
            if (!classNames.isEmpty()) {
                // Use module name as title (capitalize first letter)
                String title = capitalizeFirstLetter(moduleName);
                DocMapping mapping = new DocMapping(targetPath, title, classNames, config);
                this.docMappings.add(mapping);
                System.out.println("  " + moduleName + " -> " + targetPath);
            }
        }
        
        System.out.println("Generated " + this.docMappings.size() + " documentation mappings");
    }
    
    private String generateTargetPath(String category, String moduleName) {
        if (category == null || category.isEmpty()) {
            category = "common";
        }
        return category + "/" + moduleName + ".md";
    }
    
    private List<String> generateJavaClassNames(String moduleName) {
        // Comprehensive mapping of module names to Java class names (inspired by Python version)
        Map<String, List<String>> moduleToClasses = new HashMap<>();
        
        // Core modules
        moduleToClasses.put("agentbay", Arrays.asList(
            "com.aliyun.agentbay.AgentBay", 
            "com.aliyun.agentbay.Config"
        ));
        moduleToClasses.put("session", Arrays.asList(
            "com.aliyun.agentbay.session.Session"
        ));
        moduleToClasses.put("session-params", Arrays.asList(
            "com.aliyun.agentbay.session.CreateSessionParams"
        ));
        
        // Basic modules
        moduleToClasses.put("command", Arrays.asList(
            "com.aliyun.agentbay.command.Command"
        ));
        moduleToClasses.put("filesystem", Arrays.asList(
            "com.aliyun.agentbay.filesystem.FileSystem"
        ));
        moduleToClasses.put("context", Arrays.asList(
            "com.aliyun.agentbay.context.ContextService"
        ));
        moduleToClasses.put("context-manager", Arrays.asList(
            "com.aliyun.agentbay.context.ContextManager"
        ));
        moduleToClasses.put("context-sync", Arrays.asList(
            "com.aliyun.agentbay.context.ContextSync",
            "com.aliyun.agentbay.context.SyncPolicy",
            "com.aliyun.agentbay.context.UploadPolicy",
            "com.aliyun.agentbay.context.DownloadPolicy",
            "com.aliyun.agentbay.context.DeletePolicy",
            "com.aliyun.agentbay.context.ExtractPolicy",
            "com.aliyun.agentbay.context.RecyclePolicy",
            "com.aliyun.agentbay.context.WhiteList",
            "com.aliyun.agentbay.context.BWList",
            "com.aliyun.agentbay.context.UploadMode",
            "com.aliyun.agentbay.context.Lifecycle",
            "com.aliyun.agentbay.context.UploadStrategy"
        ));
        
        // Advanced modules
        moduleToClasses.put("browser", Arrays.asList(
            "com.aliyun.agentbay.browser.Browser",
            "com.aliyun.agentbay.browser.BrowserOperator"
        ));
        moduleToClasses.put("code", Arrays.asList(
            "com.aliyun.agentbay.code.Code"
        ));
        moduleToClasses.put("oss", Arrays.asList(
            "com.aliyun.agentbay.oss.OSS"
        ));
        moduleToClasses.put("computer", Arrays.asList(
            "com.aliyun.agentbay.computer.Computer"
        ));
        moduleToClasses.put("mobile", Arrays.asList(
            "com.aliyun.agentbay.mobile.Mobile"
        ));
        moduleToClasses.put("mobile-simulate", Arrays.asList(
            "com.aliyun.agentbay.mobile.MobileSimulate"
        ));
        moduleToClasses.put("agent", Arrays.asList(
            "com.aliyun.agentbay.agent.Agent",
            "com.aliyun.agentbay.agent.AgentEvent",
            "com.aliyun.agentbay.agent.StreamOptions",
            "com.aliyun.agentbay.agent.MobileTaskOptions",
            "com.aliyun.agentbay.agent.TaskExecution"
        ));
        moduleToClasses.put("network", Arrays.asList(
            "com.aliyun.agentbay.network.BetaNetworkService"
        ));
        moduleToClasses.put("git", Arrays.asList(
            "com.aliyun.agentbay.git.Git",
            "com.aliyun.agentbay.git.GitCloneResult",
            "com.aliyun.agentbay.git.GitInitResult",
            "com.aliyun.agentbay.git.GitCommitResult",
            "com.aliyun.agentbay.git.GitStatusResult",
            "com.aliyun.agentbay.git.GitFileStatus",
            "com.aliyun.agentbay.git.GitLogResult",
            "com.aliyun.agentbay.git.GitLogEntry",
            "com.aliyun.agentbay.git.GitBranchListResult",
            "com.aliyun.agentbay.git.GitBranchInfo",
            "com.aliyun.agentbay.git.GitError",
            "com.aliyun.agentbay.git.GitAuthError",
            "com.aliyun.agentbay.git.GitConflictError",
            "com.aliyun.agentbay.git.GitNotARepoError",
            "com.aliyun.agentbay.git.GitNotFoundError"
        ));
        moduleToClasses.put("pty", Arrays.asList(
            "com.aliyun.agentbay.pty.Pty",
            "com.aliyun.agentbay.pty.PtyHandle",
            "com.aliyun.agentbay.pty.PtySession"
        ));
        
        return moduleToClasses.getOrDefault(moduleName, new ArrayList<>());
    }

    private void writeApiReadme() throws IOException {
        Path readmePath = Paths.get(DOCS_ROOT, "README.md");
        List<String> targets = new ArrayList<>();
        if (docMappings != null) {
            for (DocMapping mapping : docMappings) {
                if (mapping != null && mapping.target != null && !mapping.target.trim().isEmpty()) {
                    targets.add(mapping.target);
                }
            }
        }
        targets.sort(String::compareTo);

        StringBuilder sb = new StringBuilder();
        sb.append("# Java SDK API Reference\n\n");
        sb.append("This directory is generated. Run `mvn exec:java` in `java/agentbay` to refresh it.\n\n");
        sb.append("## Index\n\n");
        for (String target : targets) {
            sb.append("- [").append(target).append("](").append(target.replace("\\\\", "/")).append(")\n");
        }
        sb.append('\n');

        Files.write(readmePath, sb.toString().getBytes(StandardCharsets.UTF_8));
        System.out.println("Wrote API README: " + readmePath);
    }
    
    private DocumentationMetadata createFallbackMetadata() {
        // Create comprehensive fallback metadata if YAML loading fails
        Map<String, Object> fallbackData = new HashMap<>();
        Map<String, Object> modules = new HashMap<>();
        
        // Add comprehensive module mappings (inspired by Python version)
        modules.put("agentbay", createModuleConfig("AgentBay", "common-features/basics", "\\uD83D\\uDE80", 
            "The AgentBay class is the main entry point for the AgentBay Java SDK. It provides methods to create and manage cloud sessions, configure authentication, and access various cloud services."));
        modules.put("session", createModuleConfig("Session", "common-features/basics", "\\uD83D\\uDCCB", 
            "The Session class represents an active cloud environment instance in AgentBay. It provides access to all service modules and manages the lifecycle of the cloud environment."));
        modules.put("command", createModuleConfig("Command", "common-features/basics", "\\u26A1", 
            "The Command module enables execution of shell commands and scripts in the cloud environment with timeout and output handling."));
        modules.put("filesystem", createModuleConfig("FileSystem", "common-features/basics", "\\uD83D\\uDCC1", 
            "The FileSystem module provides comprehensive file and directory operations in the cloud environment."));
        modules.put("browser", createModuleConfig("Browser", "common-features/advanced", "\\uD83C\\uDF10", 
            "The Browser module provides browser automation capabilities using Playwright integration for web scraping and testing."));
        modules.put("code", createModuleConfig("Code", "common-features/advanced", "\\uD83D\\uDCBB", 
            "The Code module provides capabilities for executing Python, JavaScript, R, and Java code in isolated cloud environments."));
        modules.put("oss", createModuleConfig("OSS", "common-features/advanced", "\\u2601\\uFE0F", 
            "The OSS module provides object storage service integration for file upload, download, and management."));
        modules.put("computer", createModuleConfig("Computer", "common-features/advanced", "\\uD83D\\uDDA5\\uFE0F", 
            "The Computer module provides desktop automation capabilities including screen capture and interaction."));
        modules.put("mobile", createModuleConfig("Mobile", "common-features/advanced", "\\uD83D\\uDCF1", 
            "The Mobile module provides mobile device automation and testing capabilities."));
        modules.put("pty", createModuleConfig("PTY", "common-features/basics", "\\uD83D\\uDCBB",
            "The PTY module provides interactive terminal sessions in cloud sandbox environments with real-time streaming, resize, and session lifecycle management."));
        
        fallbackData.put("modules", modules);
        
        // Add comprehensive global configuration
        Map<String, Object> globalConfig = new HashMap<>();
        
        Map<String, Object> javaConfig = new HashMap<>();
        javaConfig.put("exclude_object_methods", Arrays.asList("equals", "hashCode", "toString", "clone"));
        javaConfig.put("exclude_bean_methods", Arrays.asList("setId", "setName", "setType", "setStatus"));
        globalConfig.put("java", javaConfig);
        
        fallbackData.put("global", globalConfig);
        
        return new DocumentationMetadata(fallbackData);
    }
    
    private Map<String, Object> createModuleConfig(String title, String category, String emoji, String overview) {
        Map<String, Object> config = new HashMap<>();
        config.put("category", category);
        config.put("emoji", emoji);
        config.put("overview", overview);
        
        // Add tutorial configuration
        Map<String, Object> tutorial = new HashMap<>();
        tutorial.put("url", "../../../../../docs/guides/" + category + "/" + title.toLowerCase() + "-guide.md");
        tutorial.put("text", title + " Guide");
        tutorial.put("description", "Detailed tutorial on " + title.toLowerCase() + " usage and best practices");
        config.put("tutorial", tutorial);
        
        return config;
    }
    
    // Helper classes
    static class DocumentationMetadata {
        public Map<String, ModuleConfig> modules;
        public GlobalConfig global;
        
        @SuppressWarnings("unchecked")
        public DocumentationMetadata(Map<String, Object> data) {
            this.modules = new HashMap<>();
            this.global = new GlobalConfig();
            
            if (data.containsKey("modules")) {
                Map<String, Object> modulesData = (Map<String, Object>) data.get("modules");
                if (modulesData != null) {
                    for (Map.Entry<String, Object> entry : modulesData.entrySet()) {
                        this.modules.put(entry.getKey(), new ModuleConfig((Map<String, Object>) entry.getValue()));
                    }
                }
            }
            
            if (data.containsKey("global")) {
                this.global = new GlobalConfig((Map<String, Object>) data.get("global"));
            }
        }
    }
    
    static class ModuleConfig {
        public String category;
        public String emoji;
        public String overview;
        public TutorialConfig tutorial;
        public List<String> requirements;
        public List<String> bestPractices;
        public List<RelatedResource> relatedResources;
        
        public ModuleConfig() {}
        
        @SuppressWarnings("unchecked")
        public ModuleConfig(Map<String, Object> data) {
            this.category = (String) data.get("category");
            this.emoji = (String) data.get("emoji");
            this.overview = (String) data.get("overview");
            
            if (data.containsKey("tutorial")) {
                this.tutorial = new TutorialConfig((Map<String, Object>) data.get("tutorial"));
            }
            
            if (data.containsKey("requirements")) {
                this.requirements = (List<String>) data.get("requirements");
            }
            
            if (data.containsKey("best_practices")) {
                this.bestPractices = (List<String>) data.get("best_practices");
            }
            
            if (data.containsKey("related_resources")) {
                this.relatedResources = new ArrayList<>();
                List<Map<String, Object>> resources = (List<Map<String, Object>>) data.get("related_resources");
                if (resources != null) {
                    for (Map<String, Object> resource : resources) {
                        this.relatedResources.add(new RelatedResource(resource));
                    }
                }
            }
        }
        
        public String getDisplayName() {
            // This method is no longer used for title generation
            // Title is now derived from module name directly
            if (category != null) {
                return category.replace("-", " ").replace("/", " ");
            }
            return "API";
        }
    }
    
    static class GlobalConfig {
        public JavaConfig javaConfig;
        
        public GlobalConfig() {}
        
        @SuppressWarnings("unchecked")
        public GlobalConfig(Map<String, Object> data) {
            if (data != null) {
                if (data.containsKey("java")) {
                    this.javaConfig = new JavaConfig((Map<String, Object>) data.get("java"));
                }
            }
        }
    }
    
    
    static class JavaConfig {
        public List<String> excludeObjectMethods;
        public List<String> excludeBeanMethods;
        public List<String> excludeSerializationMethods;
        public List<String> excludeUtilityMethods;
        
        @SuppressWarnings("unchecked")
        public JavaConfig(Map<String, Object> data) {
            this.excludeObjectMethods = (List<String>) data.get("exclude_object_methods");
            this.excludeBeanMethods = (List<String>) data.get("exclude_bean_methods");
            this.excludeSerializationMethods = (List<String>) data.get("exclude_serialization_methods");
            this.excludeUtilityMethods = (List<String>) data.get("exclude_utility_methods");
        }
    }
    
    static class TutorialConfig {
        public String url;
        public String text;
        public String description;
        
        public TutorialConfig(Map<String, Object> data) {
            this.url = (String) data.get("url");
            this.text = (String) data.get("text");
            this.description = (String) data.get("description");
        }
    }
    
    static class RelatedResource {
        public String name;
        public String module;
        public String category;
        
        public RelatedResource(Map<String, Object> data) {
            this.name = (String) data.get("name");
            this.module = (String) data.get("module");
            this.category = (String) data.get("category");
        }
    }
    
    static class DocMapping {
        public String target;
        public String title;
        public List<String> classNames;
        public ModuleConfig config;
        
        public DocMapping(String target, String title, List<String> classNames, ModuleConfig config) {
            this.target = target;
            this.title = title;
            this.classNames = classNames;
            this.config = config;
        }
    }
    
    static class ValidationError {
        public enum Type {
            BROKEN_LINK,
            BROKEN_ANCHOR,
            BROKEN_CROSS_REFERENCE
        }
        
        public Type type;
        public String file;
        public String message;
        
        public ValidationError(Type type, String file, String message) {
            this.type = type;
            this.file = file;
            this.message = message;
        }
        
        @Override
        public String toString() {
            return "[" + type + "] " + file + ": " + message;
        }
    }
    
    static class MarkdownLink {
        public String text;
        public String url;
        
        public MarkdownLink(String text, String url) {
            this.text = text;
            this.url = url;
        }
    }
}
