package com.aliyun.agentbay.filesystem;

import com.aliyun.agentbay._internal.WsClient;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.exception.FileException;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.service.BaseService;
import com.aliyun.agentbay.session.Session;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.util.*;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Handles file operations in the AgentBay cloud environment.
 *
 */
public class FileSystem extends BaseService {
    private static final Logger logger = LoggerFactory.getLogger(FileSystem.class);
    private static final ObjectMapper objectMapper = new ObjectMapper();
    private static final String SERVER_FILESYSTEM = "wuying_filesystem";
    private static final String SERVER_SHELL = "wuying_shell";

    private static final int DEFAULT_CHUNK_SIZE = 50 * 1024;

    private FileTransfer fileTransfer;

    /**
     * Initialize FileSystem with FileTransfer capability.
     *
     * @param session The session object for file operations
     */
    public FileSystem(Session session) {
        super(session);
    }

    private OperationResult callFilesystemTool(String toolName, Map<String, Object> args) {
        return callMcpTool(toolName, args);
    }

    private OperationResult callShellTool(Map<String, Object> args) {
        return callMcpTool("shell", args);
    }

    /**
     * Ensure FileTransfer is initialized with the current session.
     *
     * @return The FileTransfer instance
     * @throws RuntimeException if AgentBay instance or session is not available
     */
    private FileTransfer ensureFileTransfer() {
        if (fileTransfer == null) {
            if (session.getAgentBay() == null) {
                throw new RuntimeException("FileTransfer requires an AgentBay instance");
            }
            if (session == null) {
                throw new RuntimeException("FileTransfer requires a session");
            }
            fileTransfer = new FileTransfer(session.getAgentBay(), session);
        }
        return fileTransfer;
    }

    /**
     * Get the context path for file transfer operations.
     *
     * <p>This method ensures the context ID is loaded and returns the associated
     * context path that was retrieved from GetAndLoadInternalContext API.</p>
     *
     * @return The context path if available, null otherwise
     */
    public String getFileTransferContextPath() {
        FileTransfer transfer = ensureFileTransfer();
        return transfer.getContextPath();
    }

    /**
     * Read a file, alias of readFile().
     *
     * @param path The path of the file to read
     * @return File content as string
     * @throws AgentBayException if reading fails
     */
    public String read(String path) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);
        OperationResult result = callFilesystemTool("read_file", args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Write content to a file.
     *
     * @param path The path of the file to write
     * @param content The content to write to the file
     * @return Write result as string
     * @throws AgentBayException if writing fails
     */
    public String write(String path, String content) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);
        args.put("content", content);
        OperationResult result = callFilesystemTool("write_file", args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * List the contents of a directory.
     *
     * @param path The path of the directory to list
     * @return Directory listing as string
     * @throws AgentBayException if listing fails or directory does not exist
     */
    public String list(String path) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);
        OperationResult result = callFilesystemTool("list_directory", args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Check if a file or directory exists.
     *
     * @param path Path to check
     * @return true if exists, false otherwise
     * @throws AgentBayException if check fails
     */
    public boolean exists(String path) throws AgentBayException {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("command", "test -e \"" + path + "\" && echo 'exists' || echo 'not exists'");
            OperationResult result = callShellTool(args);
            return result.isSuccess() && result.getData() != null && (result.getData().trim().contains("exists") && !result.getData().trim().contains("not exists"));
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * Create a directory.
     *
     * @param path Directory path to create
     * @return Creation result as string
     * @throws AgentBayException if creation fails or path is invalid
     */
    public String mkdir(String path) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("command", "mkdir -p \"" + path + "\"");
        OperationResult result = callShellTool(args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Remove a file or directory using shell command.
     *
     * @param path Path to remove
     * @return Removal result
     * @throws AgentBayException if removal fails
     * @deprecated Use deleteFile instead. This method uses shell command which may not work in all environments.
     */
    @Deprecated
    public String removeLegacy(String path) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("command", "rm -rf \"" + path + "\"");
        OperationResult result = callShellTool(args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Copy a file or directory.
     *
     * @param source Source path to copy from
     * @param destination Destination path to copy to
     * @return Copy result as string
     * @throws AgentBayException if copy fails, source does not exist, or destination is invalid
     */
    public String copy(String source, String destination) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("command", "cp -r \"" + source + "\" \"" + destination + "\"");
        OperationResult result = callShellTool(args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Move a file or directory.
     *
     * @param source Source path to move from
     * @param destination Destination path to move to
     * @return Move result as string
     * @throws AgentBayException if move fails, source does not exist, or destination is invalid
     */
    public String move(String source, String destination) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("command", "mv \"" + source + "\" \"" + destination + "\"");
        OperationResult result = callShellTool(args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Get file information.
     *
     * @param path File path to inspect
     * @return File information as string (ls -la output)
     * @throws AgentBayException if getting info fails or file does not exist
     */
    public String getInfo(String path) throws AgentBayException {
        Map<String, Object> args = new HashMap<>();
        args.put("command", "ls -la \"" + path + "\"");
        OperationResult result = callShellTool(args);
        if (result.isSuccess()) {
            return result.getData();
        } else {
            throw new AgentBayException(result.getErrorMessage());
        }
    }

    /**
     * Check if the current session uses LinkUrl (HTTP) channel.
     * When using LinkUrl, chunking is not needed as HTTP has no message size limit.
     */
    private boolean isUsingLinkUrl() {
        return session.getLinkUrl() != null && !session.getLinkUrl().isEmpty()
            && session.getToken() != null && !session.getToken().isEmpty();
    }

    /**
     * Write content to a file.
     * For MQTT channel, automatically handles large files by chunking.
     * For HTTP LinkUrl channel, writes the entire content in a single call without chunking.
     * 
     * <p>Similar to Python's write_file method.</p>
     *
     * @param path File path
     * @param content Content to write
     * @param mode Write mode ("overwrite" or "append")
     * @param createParentDir Whether to create parent directories if they don't exist (default: false)
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult writeFile(String path, String content, String mode, boolean createParentDir) {
        // HTTP (LinkUrl) channel: write entire content in a single call, no chunking needed
        if (isUsingLinkUrl()) {
            return writeFileChunk(path, content, mode, createParentDir);
        }

        int contentLength = content.getBytes().length;
        int chunkSize = DEFAULT_CHUNK_SIZE;
        // If the content length is less than the chunk size, write it directly
        if (contentLength <= chunkSize) {
            return writeFileChunk(path, content, mode, createParentDir);
        }

        try {
            // Write the first chunk (creates or overwrites the file)
            String firstChunk = content.substring(0, Math.min(chunkSize, content.length()));
            BoolResult result = writeFileChunk(path, firstChunk, mode, createParentDir);
            if (!result.isSuccess()) {
                return result;
            }

            // Write the rest in chunks (appending)
            int offset = chunkSize;
            while (offset < content.length()) {
                int end = Math.min(offset + chunkSize, content.length());
                String currentChunk = content.substring(offset, end);
                result = writeFileChunk(path, currentChunk, "append", false);
                if (!result.isSuccess()) {
                    return result;
                }
                offset = end;
            }

            return new BoolResult(result.getRequestId(), true, true, "");

        } catch (Exception e) {
            return new BoolResult("", false, false, "Failed to write file: " + e.getMessage());
        }
    }

    /**
     * Write file content using BoolResult with default "overwrite" mode
     */
    public BoolResult writeFile(String path, String content) {
        return writeFile(path, content, "overwrite", false);
    }

    /**
     * Write file content using BoolResult with specified mode
     */
    public BoolResult writeFile(String path, String content, String mode) {
        return writeFile(path, content, mode, false);
    }

    // Note: The three-parameter version writeFile(path, content, mode) is the main method above

    /**
     * Internal method to write a file chunk. Used for chunked file operations.
     * Similar to Python's _write_file_chunk method.
     *
     * @param path File path
     * @param content Content to write
     * @param mode Write mode ("overwrite" or "append")
     * @param createParentDir Whether to create parent directories if they don't exist
     * @return BoolResult containing success status and error message if any
     */
    private BoolResult writeFileChunk(String path, String content, String mode, boolean createParentDir) {
        if (!"overwrite".equals(mode) && !"append".equals(mode)) {
            return new BoolResult("", false, false,
                "Invalid write mode: " + mode + ". Must be 'overwrite' or 'append'.");
        }

        Map<String, Object> args = new HashMap<>();
        args.put("path", path);
        args.put("content", content);
        args.put("mode", mode);
        args.put("create_parent_dir", createParentDir);

        try {
            OperationResult result = callFilesystemTool("write_file", args);
            if (result.isSuccess()) {
                return new BoolResult(result.getRequestId(), true, true, "");
            } else {
                return new BoolResult(result.getRequestId(), false, false, result.getErrorMessage());
            }

        } catch (Exception e) {
            return new BoolResult("", false, false, "Failed to write file chunk: " + e.getMessage());
        }
    }

    /**
     * Read file content using FileContentResult
     *
     * @param path File path to read
     * @return FileContentResult containing success status, file content, and error message if any
     */
    public FileContentResult readFile(String path) {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);

        try {
            OperationResult result = callFilesystemTool("read_file", args);
            if (result.isSuccess()) {
                return new FileContentResult(result.getRequestId(), true, result.getData(), "");
            } else {
                return new FileContentResult(result.getRequestId(), false, "", result.getErrorMessage());
            }

        } catch (Exception e) {
            return new FileContentResult("", false, "", "Failed to read file: " + e.getMessage());
        }
    }

    /**
     * Search for files matching a pattern
     *
     * @param directory Directory to search in
     * @param pattern File pattern to match (e.g., "*.java", "test*")
     * @return FileSearchResult containing list of matching file paths and error message if any
     */
    public FileSearchResult searchFiles(String directory, String pattern) {
        return searchFiles(directory, pattern, null);
    }
    
    /**
     * Search for files matching a pattern
     *
     * @param directory Directory to search in
     * @param pattern Wildcard pattern to match against file names. Supports * (any characters) and ? (single character). Examples: "*.py", "test_*", "*config*".
     * @param excludePatterns  Optional list of wildcard patterns to exclude from the search.
     * @return FileSearchResult containing list of matching file paths and error message if any
     */
    public FileSearchResult searchFiles(String directory, String pattern, List<String> excludePatterns) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("path", directory);
            args.put("pattern", pattern);
            if (excludePatterns != null && !excludePatterns.isEmpty()) {
                args.put("excludePatterns", excludePatterns);
            }

            OperationResult result = callFilesystemTool("search_files", args);

            if (result.isSuccess()) {
                String[] matchingFiles = result.getData() != null && !result.getData().trim().isEmpty()
                    ? result.getData().trim().split("\n")
                    : new String[0];

                List<String> matches = Arrays.asList(matchingFiles);
                if (matches.size() == 1 && "No matches found".equals(matches.get(0))) {
                    return new FileSearchResult(result.getRequestId(), false, new ArrayList<>(), "No matches found");
                }
                return new FileSearchResult(result.getRequestId(), true, matches, "");
            } else {
                return new FileSearchResult(result.getRequestId(), false, null,
                    result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to search files");
            }
        } catch (Exception e) {
            return new FileSearchResult("", false, null, e.getMessage());
        }
    }

    /**
     * Read multiple files at once
     *
     * @param paths List of file paths to read
     * @return MultipleFileContentResult containing map of file paths to their content and error message if any
     */
    public MultipleFileContentResult readMultipleFiles(List<String> paths) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("paths", paths);

            OperationResult result = callFilesystemTool("read_multiple_files", args);

            if (result.isSuccess()) {
                Map<String, String> filesContent = parseMultipleFilesResponse(result.getData());
                return new MultipleFileContentResult(result.getRequestId(), true, filesContent, "");
            } else {
                return new MultipleFileContentResult(result.getRequestId(), false, null,
                    result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to read multiple files");
            }
        } catch (Exception e) {
            return new MultipleFileContentResult("", false, null, e.getMessage());
        }
    }

    /**
     * Delete a file at the specified path.
     *
     * @param path The path of the file to delete
     * @return BoolResult containing success status and error message if any
     *
     */
    public BoolResult  deleteFile(String path) {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);

        try {
            OperationResult result = callFilesystemTool("delete_file", args);
            if (result.isSuccess()) {
                return new BoolResult(result.getRequestId(), true, true, "");
            } else {
                return new BoolResult(result.getRequestId(), false, false, result.getErrorMessage());
            }

        } catch (Exception e) {
            return new BoolResult("", false, false, "Failed to delete file: " + e.getMessage());
        }
    }

    /**
     * Create a new directory at the specified path.
     *
     * @param path The path of the directory to create
     * @return BoolResult containing success status and error message if any
     *
     */
    public BoolResult createDirectory(String path) {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);

        try {
            OperationResult result = callFilesystemTool("create_directory", args);
            if (result.isSuccess()) {
                return new BoolResult(result.getRequestId(), true, true, "");
            } else {
                return new BoolResult(result.getRequestId(), false, false, result.getErrorMessage());
            }

        } catch (Exception e) {
            return new BoolResult("", false, false, "Failed to create directory: " + e.getMessage());
        }
    }

    /**
     * List the contents of a directory.
     *
     * @param path The path of the directory to list
     * @return DirectoryListResult containing directory entries and error message if any
     *  - success (bool): True if the operation succeeded
     *   - entries (List[Dict[str, Union[str, bool]]]): List of directory entries (if success is True)
     *      Each entry contains:
     *      - name (str): Name of the file or directory
     *     - isDirectory (bool): True if entry is a directory, False if file
     *- requestId (str): Unique identifier for this API request
     *- errorMessage (str): Error description (if success is False)
     */
    public com.aliyun.agentbay.model.DirectoryListResult listDirectory(String path) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("path", path);

            OperationResult result = callFilesystemTool("list_directory", args);

            if (result.isSuccess()) {
                // Parse the directory listing response like Python SDK does
                String directoryResponse = result.getData();
                List<Map<String, Object>> entries = parseDirectoryListing(directoryResponse);

                return new com.aliyun.agentbay.model.DirectoryListResult(result.getRequestId(), true, entries, "");
            } else {
                return new com.aliyun.agentbay.model.DirectoryListResult(result.getRequestId(), false, null, result.getErrorMessage());
            }
        } catch (Exception e) {
            return new com.aliyun.agentbay.model.DirectoryListResult("", false, null, e.getMessage());
        }
    }

    /**
     * Get information about a file or directory.
     *
     * @param path The path of the file or directory to inspect
     * @return FileInfoResult containing file info and error message if any
     *
     */
    public com.aliyun.agentbay.model.FileInfoResult getFileInfo(String path) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("path", path);

            OperationResult result = callFilesystemTool("get_file_info", args);

            if (result.isSuccess()) {
                Map<String, Object> fileInfo = parseFileInfo(result.getData());
                com.aliyun.agentbay.model.FileInfoResult fileInfoResult =
                    new com.aliyun.agentbay.model.FileInfoResult(result.getRequestId(), true, result.getData(), "");
                fileInfoResult.setFileInfo(fileInfo);
                return fileInfoResult;
            } else {
                return new com.aliyun.agentbay.model.FileInfoResult(result.getRequestId(), false, "",
                    result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to get file info");
            }
        } catch (Exception e) {
            return new com.aliyun.agentbay.model.FileInfoResult("", false, null, e.getMessage());
        }
    }

    /**
     * Edit a file by replacing occurrences of oldText with newText.
     *
     * @param path The path of the file to edit
     * @param edits A list of maps specifying oldText and newText for replacements
     * @return BoolResult containing success status and error message if any
     *
     */
    public BoolResult editFile(String path, java.util.List<java.util.Map<String, String>> edits) {
        return editFile(path, edits, false);
    }

    /**
     * Edit a file by replacing occurrences of oldText with newText.
     *
     * @param path The path of the file to edit
     * @param edits A list of maps specifying oldText and newText for replacements
     * @param dryRun If true, preview changes without applying them
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult editFile(String path, java.util.List<java.util.Map<String, String>> edits, boolean dryRun) {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);
        args.put("edits", edits);
        args.put("dryRun", dryRun);

        try {
            OperationResult result = callFilesystemTool("edit_file", args);
            if (result.isSuccess()) {
                return new BoolResult(result.getRequestId(), true, true, "");
            } else {
                return new BoolResult(result.getRequestId(), false, false, result.getErrorMessage());
            }

        } catch (Exception e) {
            return new BoolResult("", false, false, "Failed to edit file: " + e.getMessage());
        }
    }

    /**
     * Move a file from source to destination path.
     *
     * @param source Source file path to move from
     * @param destination Destination file path to move to
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult moveFile(String source, String destination) {
        try {
            Map<String, Object> args = new HashMap<>();
            args.put("source", source);
            args.put("destination", destination);

            OperationResult result = callFilesystemTool("move_file", args);

            if (result.isSuccess()) {
                return new BoolResult(result.getRequestId(), true, true, "");
            } else {
                return new BoolResult(result.getRequestId(), false, false,
                    result.getErrorMessage() != null ? result.getErrorMessage() : "Failed to move file");
            }
        } catch (Exception e) {
            return new BoolResult("", false, false, e.getMessage());
        }
    }

    /**
     * Parse directory listing text into a list of file/directory entries.
     * This mimics the Python SDK's parse_directory_listing function.
     *
     * @param text Directory listing text in format:
     *             [DIR] directory_name
     *             [FILE] file_name
     *             Each entry should be on a new line with [DIR] or [FILE] prefix
     * @return List of maps containing name and isDirectory fields
     */
    private List<Map<String, Object>> parseDirectoryListing(String text) {
        List<Map<String, Object>> result = new ArrayList<>();
        if (text == null || text.trim().isEmpty()) {
            return result;
        }

        String[] lines = text.split("\n");
        for (String line : lines) {
            line = line.trim();
            if (line.isEmpty()) {
                continue;
            }

            Map<String, Object> entryMap = new HashMap<>();
            if (line.startsWith("[DIR]")) {
                entryMap.put("isDirectory", true);
                entryMap.put("isFile", false);
                entryMap.put("name", line.replace("[DIR]", "").trim());
            } else if (line.startsWith("[FILE]")) {
                entryMap.put("isDirectory", false);
                entryMap.put("isFile", true);
                entryMap.put("name", line.replace("[FILE]", "").trim());
            } else {
                // Skip lines that don't match the expected format
                continue;
            }

            result.add(entryMap);
        }

        return result;
    }

    /**
     * Parse file info string into a map.
     * This mimics the Python SDK's parse_file_info function.
     *
     * @param fileInfoStr The file info string to parse
     * @return A map containing the parsed file info
     */
    private Map<String, Object> parseFileInfo(String fileInfoStr) {
        Map<String, Object> result = new HashMap<>();
        if (fileInfoStr == null || fileInfoStr.trim().isEmpty()) {
            return result;
        }

        String[] lines = fileInfoStr.split("\\n");
        for (String line : lines) {
            if (line.contains(":")) {
                String[] parts = line.split(":", 2);
                if (parts.length == 2) {
                    String key = parts[0].trim();
                    String value = parts[1].trim();

                    // Convert boolean values
                    if ("true".equalsIgnoreCase(value)) {
                        result.put(key, true);
                    } else if ("false".equalsIgnoreCase(value)) {
                        result.put(key, false);
                    } else {
                        // Try to convert numeric values
                        try {
                            if (value.contains(".")) {
                                result.put(key, Double.parseDouble(value));
                            } else {
                                result.put(key, Long.parseLong(value));
                            }
                        } catch (NumberFormatException e) {
                            // Keep as string if not numeric
                            result.put(key, value);
                        }
                    }
                }
            }
        }
        return result;
    }
    /**
     * Parse the response from reading multiple files.
     * This mimics the Python SDK's parse_multiple_files_response function.
     *
     * @param text The response string containing file contents in format:
     *             /path/to/file1.txt: Content of file1
     *
     *             ---
     *
     *             /path/to/file2.txt:Content of file2
     * @return A map mapping file paths to their content
     */
    private Map<String, String> parseMultipleFilesResponse(String text) {
        Map<String, String> result = new HashMap<>();
        if (text == null || text.trim().isEmpty()) {
            return result;
        }

        String[] lines = text.split("\\n");
        String currentPath = null;
        List<String> currentContent = new ArrayList<>();

        for (int i = 0; i < lines.length; i++) {
            String line = lines[i];

            // Check if this line contains a file path (ends with a colon)
            if (line.contains(":") && currentPath == null) {
                // Extract path (everything before the first colon)
                int colonIndex = line.indexOf(":");
                String path = line.substring(0, colonIndex).trim();

                // Start collecting content (everything after the colon)
                currentPath = path;

                // If there's content on the same line after the colon, add it
                if (line.length() > colonIndex + 1) {
                    String contentStart = line.substring(colonIndex + 1).trim();
                    if (!contentStart.isEmpty()) {
                        currentContent.add(contentStart);
                    }
                }
            }
            // Check if this is a separator line
            else if ("---".equals(line.trim())) {
                // Save the current file content
                if (currentPath != null) {
                    result.put(currentPath, String.join("\n", currentContent).trim());
                    currentPath = null;
                    currentContent.clear();
                }
            }
            // If we're collecting content for a path, add this line
            else if (currentPath != null) {
                currentContent.add(line);
            }
        }

        // Save the last file content if exists
        if (currentPath != null) {
            result.put(currentPath, String.join("\n", currentContent).trim());
        }

        return result;
    }

    /**
     * Upload a local file to remote path using pre-signed URLs.
     *
     * @param localPath Local file path to upload
     * @param remotePath Remote file path to upload to
     * @param contentType Optional content type for the file (can be null)
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @return UploadResult containing the result of the upload operation
     */
    public UploadResult uploadFile(
        String localPath,
        String remotePath,
        String contentType,
        boolean wait,
        float waitTimeout,
        float pollInterval
    ) {
        return uploadFile(localPath, remotePath, contentType, wait, waitTimeout, pollInterval, null);
    }
    /**
     * Upload a local file to remote path using pre-signed URLs.
     *
     * @param localPath Local file path to upload
     * @param remotePath Remote file path to upload to
     * @param contentType Optional content type for the file (can be null)
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @param progressCallback Callback for upload progress updates
     * @return UploadResult containing the result of the upload operation
     */
    public UploadResult uploadFile(
        String localPath,
        String remotePath,
        String contentType,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        try {
            FileTransfer transfer = ensureFileTransfer();
            UploadResult result = transfer.upload(localPath, remotePath, contentType, wait, waitTimeout, pollInterval, progressCallback);
            return result;
        } catch (Exception e) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Upload failed: " + e.getMessage()
            );
        }
    }

    /**
     * Upload a local file to remote path with default parameters.
     *
     * @param localPath Local file path to upload from
     * @param remotePath Remote file path to upload to
     * @return UploadResult containing the result of the upload operation
     */
    public UploadResult uploadFile(String localPath, String remotePath) {
        return uploadFile(localPath, remotePath, null, true, 30.0f, 1.5f);
    }

    /**
     * Download a file from remote path to local path using pre-signed URLs.
     *
     * @param remotePath Remote file path to download from
     * @param localPath Local file path to download to
     * @param overwrite Whether to overwrite existing local file
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @return DownloadResult containing the result of the download operation
     */
    public DownloadResult downloadFile(
        String remotePath,
        String localPath,
        boolean overwrite,
        boolean wait,
        float waitTimeout,
        float pollInterval
    ) {
        return downloadFile(remotePath, localPath, overwrite, wait, waitTimeout, pollInterval, null);
    }

    /**
     * Download a file from remote path to local path using pre-signed URLs.
     *
     * @param remotePath Remote file path to download from
     * @param localPath Local file path to download to
     * @param overwrite Whether to overwrite existing local file
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @param progressCallback  Callback for download progress updates
     * @return DownloadResult containing the result of the download operation
     */
    public DownloadResult downloadFile(
        String remotePath,
        String localPath,
        boolean overwrite,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        try {
            FileTransfer transfer = ensureFileTransfer();
            DownloadResult result = transfer.download(remotePath, localPath, overwrite, wait, waitTimeout, pollInterval, progressCallback);
            return result;
        } catch (Exception e) {
            return new DownloadResult(
                "", false, null, null, null, 0, remotePath, localPath, null,
                "Download failed: " + e.getMessage()
            );
        }
    }

    /**
     * Download a file from remote path to local path with default parameters.
     *
     * @param remotePath Remote file path to download from
     * @param localPath Local file path to download to
     * @return DownloadResult containing the result of the download operation
     */
    public DownloadResult downloadFile(String remotePath, String localPath) {
        return downloadFile(remotePath, localPath, true, true, 30.0f, 1.5f);
    }

    /**
     * Download a file from remote path with auto-generated local path.
     *
     * @param remotePath Remote file path to download from
     * @return DownloadResult containing the result of the download operation
     */
    public DownloadResult downloadFile(String remotePath) {
        return downloadFile(remotePath, null);
    }

    /**
     * Upload byte array to remote path using pre-signed URLs.
     * This is a Java SDK extension that allows uploading data from memory without writing to disk first.
     *
     * @param content Byte array content to upload
     * @param remotePath Remote file path to upload to
     * @param contentType Optional content type for the file
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @param progressCallback Callback for upload progress updates
     * @return UploadResult containing the result of the upload operation
     */
    public UploadResult uploadFileBytes(
        byte[] content,
        String remotePath,
        String contentType,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        try {
            FileTransfer transfer = ensureFileTransfer();
            UploadResult result = transfer.uploadBytes(content, remotePath, contentType, wait, waitTimeout, pollInterval, progressCallback);
            return result;
        } catch (Exception e) {
            return new UploadResult(
                "", false, null, null, null, null, 0, remotePath,
                "Upload failed: " + e.getMessage()
            );
        }
    }

    /**
     * Upload byte array to remote path with default parameters.
     *
     * @param content Byte array content to upload
     * @param remotePath Remote file path to upload to
     * @return UploadResult containing the result of the upload operation
     */
    public UploadResult uploadFileBytes(byte[] content, String remotePath) {
        return uploadFileBytes(content, remotePath, null, true, 30.0f, 1.5f, null);
    }

    /**
     * Download file from remote path to byte array using pre-signed URLs.
     * This is a Java SDK extension that allows downloading data to memory without writing to disk.
     *
     * @param remotePath Remote file path to download from
     * @param wait Whether to wait for the sync operation to complete
     * @param waitTimeout Timeout for waiting for sync completion (seconds)
     * @param pollInterval Interval between polling for sync completion (seconds)
     * @param progressCallback Callback for download progress updates
     * @return DownloadResult containing the downloaded byte array in the content field
     */
    public DownloadResult downloadFileBytes(
        String remotePath,
        boolean wait,
        float waitTimeout,
        float pollInterval,
        ProgressCallback progressCallback
    ) {
        try {
            FileTransfer transfer = ensureFileTransfer();
            DownloadResult result = transfer.downloadBytes(remotePath, wait, waitTimeout, pollInterval, progressCallback);
            return result;
        } catch (Exception e) {
            return new DownloadResult(
                "", false, null, null, null, 0, remotePath, null, null,
                "Download failed: " + e.getMessage()
            );
        }
    }
    /**
     * Download file from remote path to byte array with default parameters.
     *
     * @param remotePath Remote file path to download from
     * @return DownloadResult containing the downloaded byte array in the content field
     */
    public DownloadResult downloadFileBytes(String remotePath) {
        return downloadFileBytes(remotePath, true, 30.0f, 1.5f, null);
    }

    /**
     * Delete a file at the specified path. Alias for deleteFile().
     *
     * @param path The path of the file to delete
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult delete(String path) {
        return deleteFile(path);
    }

    /**
     * Remove a file at the specified path. Alias for deleteFile().
     *
     * @param path The path of the file to remove
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult remove(String path) {
        return deleteFile(path);
    }

    /**
     * Remove a file at the specified path. Alias for deleteFile().
     *
     * @param path The path of the file to remove
     * @return BoolResult containing success status and error message if any
     */
    public BoolResult rm(String path) {
        return deleteFile(path);
    }

    /**
     * List directory contents. Alias for listDirectory().
     *
     * @param path The path of the directory to list
     * @return DirectoryListResult containing directory entries and error message if any
     */
    public com.aliyun.agentbay.model.DirectoryListResult ls(String path) {
        return listDirectory(path);
    }

    // ── File Change Monitoring ──

    /**
     * Parse raw JSON data from get_file_change into FileChangeEvent list.
     */
    private List<FileChangeEvent> parseFileChangeData(String rawData) {
        List<FileChangeEvent> events = new ArrayList<>();
        if (rawData == null || rawData.isEmpty() || "{}".equals(rawData) || "[]".equals(rawData)) {
            return events;
        }
        try {
            // Try MCP wrapper: {"content":[{"text":"..."}]}
            Map<String, Object> wrapper = objectMapper.readValue(rawData, Map.class);
            Object content = wrapper.get("content");
            if (content instanceof List) {
                List<?> contentList = (List<?>) content;
                if (!contentList.isEmpty()) {
                    Object first = contentList.get(0);
                    if (first instanceof Map) {
                        Object text = ((Map<?, ?>) first).get("text");
                        if (text instanceof String) {
                            return parseFileChangeData((String) text);
                        }
                    }
                }
            }
        } catch (Exception ignored) {
        }

        try {
            // Try array
            List<Map<String, Object>> array = objectMapper.readValue(
                rawData, new TypeReference<List<Map<String, Object>>>() {});
            for (Map<String, Object> dict : array) {
                if (dict != null && !dict.isEmpty()) {
                    FileChangeEvent e = FileChangeEvent.fromDict(dict);
                    if (!e.getEventType().isEmpty() || !e.getPath().isEmpty()) {
                        events.add(e);
                    }
                }
            }
            return events;
        } catch (Exception ignored) {
        }

        try {
            // Try single object
            Map<String, Object> dict = objectMapper.readValue(rawData, Map.class);
            if (dict != null && !dict.isEmpty()) {
                FileChangeEvent e = FileChangeEvent.fromDict(dict);
                if (!e.getEventType().isEmpty() || !e.getPath().isEmpty()) {
                    events.add(e);
                }
            }
            return events;
        } catch (Exception ignored) {
        }

        return events;
    }

    /**
     * Get file change information for the specified directory path.
     *
     * @param path Absolute path to the directory to monitor
     * @return FileChangeResult containing detected file changes
     */
    public FileChangeResult getFileChange(String path) {
        Map<String, Object> args = new HashMap<>();
        args.put("path", path);

        try {
            OperationResult result = callFilesystemTool("get_file_change", args);
            if (result.isSuccess()) {
                List<FileChangeEvent> events = parseFileChangeData(result.getData());
                return new FileChangeResult(result.getRequestId(), true, events, result.getData(), "");
            } else {
                return new FileChangeResult(
                    result.getRequestId(), false, null, result.getData(),
                    result.getErrorMessage() != null ? result.getErrorMessage() : "get_file_change failed");
            }
        } catch (Exception e) {
            return new FileChangeResult("", false, null, "", "Failed to get file change: " + e.getMessage());
        }
    }

    /**
     * Result handle for a running directory watch operation.
     */
    public static class WatchHandle {
        private final Thread thread;
        private final CountDownLatch ready;

        WatchHandle(Thread thread, CountDownLatch ready) {
            this.thread = thread;
            this.ready = ready;
        }

        /**
         * Block until the baseline is established.
         */
        public void awaitReady() throws InterruptedException {
            ready.await();
        }

        /**
         * Block until the baseline is established, with timeout.
         */
        public boolean awaitReady(long timeout, TimeUnit unit) throws InterruptedException {
            return ready.await(timeout, unit);
        }

        /**
         * Block until the monitoring thread finishes.
         */
        public void join() throws InterruptedException {
            thread.join();
        }

        /**
         * Block until the monitoring thread finishes, with timeout.
         */
        public void join(long millis) throws InterruptedException {
            thread.join(millis);
        }
    }

    /**
     * Callback interface for file change events.
     */
    @FunctionalInterface
    public interface FileChangeCallback {
        void onFileChange(List<FileChangeEvent> events);
    }

    /**
     * Watch a directory for file changes.
     *
     * When the session provides a WebSocket connection, uses real-time push
     * notifications for near-instant event delivery. Falls back to HTTP
     * polling when WebSocket is unavailable.
     *
     * @param path     Absolute path to the directory to watch
     * @param callback Called when changes are detected
     * @param intervalMs Polling interval in milliseconds (deprecated in push mode)
     * @param stop     AtomicBoolean; set to true to stop watching
     * @return WatchHandle for waiting on readiness and thread join
     */
    public WatchHandle watchDirectory(
        String path,
        FileChangeCallback callback,
        long intervalMs,
        AtomicBoolean stop
    ) {
        CountDownLatch ready = new CountDownLatch(1);

        boolean useWsPush = false;
        String serverName = "";
        String wsUrl = session.getWsUrl();
        String token = session.getToken();
        serverName = session.getMcpServerForTool("get_file_change");
        if (wsUrl != null && !wsUrl.isEmpty()
            && token != null && !token.isEmpty()
            && serverName != null && !serverName.isEmpty()) {
            useWsPush = true;
        }

        final boolean finalUseWsPush = useWsPush;
        final String finalServerName = serverName;

        Thread thread = new Thread(() -> {
            if (finalUseWsPush) {
                monitorWsPush(path, callback, intervalMs, stop, ready, finalServerName);
            } else {
                monitorPolling(path, callback, intervalMs, stop, ready);
            }
        }, "FileWatch-" + path.replace('/', '_'));
        thread.setDaemon(true);
        thread.start();

        return new WatchHandle(thread, ready);
    }

    /**
     * Watch a directory with default 500ms polling interval.
     */
    public WatchHandle watchDirectory(
        String path,
        FileChangeCallback callback,
        AtomicBoolean stop
    ) {
        return watchDirectory(path, callback, 500, stop);
    }

    private void monitorPolling(
        String path,
        FileChangeCallback callback,
        long intervalMs,
        AtomicBoolean stop,
        CountDownLatch ready
    ) {
        logger.info("Starting polling monitoring for: {}", path);

        // Baseline
        getFileChange(path);
        ready.countDown();

        pollingLoop(path, callback, intervalMs, stop);
    }

    private void pollingLoop(
        String path,
        FileChangeCallback callback,
        long intervalMs,
        AtomicBoolean stop
    ) {
        while (!stop.get()) {
            try {
                Thread.sleep(intervalMs);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
            if (stop.get()) break;

            FileChangeResult result = getFileChange(path);
            if (!result.isSuccess()) {
                String err = result.getErrorMessage();
                if (err != null && err.toLowerCase().contains("session")
                    && (err.toLowerCase().contains("expired") || err.toLowerCase().contains("not found"))) {
                    logger.warn("Session expired, stopping polling for: {}", path);
                    break;
                }
                continue;
            }
            if (!result.getEvents().isEmpty()) {
                logger.info("Detected {} file changes", result.getEvents().size());
                try {
                    callback.onFileChange(result.getEvents());
                } catch (Exception e) {
                    logger.error("Error in watch callback: {}", e.getMessage());
                }
            }
        }
        logger.info("Stopped polling monitoring for: {}", path);
    }

    private void monitorWsPush(
        String path,
        FileChangeCallback callback,
        long intervalMs,
        AtomicBoolean stop,
        CountDownLatch ready,
        String serverName
    ) {
        logger.info("Starting WS push monitoring for: {}", path);

        // Phase 1: HTTP baseline
        getFileChange(path);
        ready.countDown();
        logger.info("WS push: baseline established via HTTP for: {}", path);

        // Phase 2: Attach to session's shared WsClient
        Runnable unsubscribePush = null;
        Runnable unsubscribeState = null;
        final AtomicBoolean subscriptionActive = new AtomicBoolean(false);

        WsClient wsClient;
        try {
            wsClient = session.getWsClient();
            wsClient.connect().get(15, TimeUnit.SECONDS);
        } catch (Exception e) {
            logger.warn("WS push: failed to get WsClient: {}. Falling back to polling.", e.getMessage());
            pollingLoop(path, callback, intervalMs, stop);
            return;
        }

        // Push callback
        WsClient.PushCallback onPush = payload -> {
            Object dataObj = payload.get("data");
            if (!(dataObj instanceof Map)) return;
            Map<String, Object> data = (Map<String, Object>) dataObj;
            if (!"file_change".equals(data.get("eventType"))) return;
            if (!path.equals(data.get("path"))) return;

            Object eventsRaw = data.get("events");
            if (!(eventsRaw instanceof List)) return;
            List<FileChangeEvent> events = new ArrayList<>();
            for (Object item : (List<?>) eventsRaw) {
                if (item instanceof Map) {
                    events.add(FileChangeEvent.fromDict((Map<String, Object>) item));
                }
            }
            if (!events.isEmpty()) {
                logger.info("WS push: {} file changes for {}", events.size(), path);
                try {
                    callback.onFileChange(events);
                } catch (Exception e) {
                    logger.error("Error in watch callback: {}", e.getMessage());
                }
            }
        };

        unsubscribePush = wsClient.registerCallback(serverName, onPush);

        // Reconnection handler
        final WsClient finalWsClient = wsClient;
        unsubscribeState = wsClient.onConnectionStateChange((state, reason) -> {
            if (state != WsClient.ConnectionState.OPEN) return;
            if (!subscriptionActive.get() || stop.get()) return;

            logger.info("WS reconnected, catch-up polling for: {}", path);
            FileChangeResult catchUp = getFileChange(path);
            if (catchUp.isSuccess() && !catchUp.getEvents().isEmpty()) {
                try {
                    callback.onFileChange(catchUp.getEvents());
                } catch (Exception e) {
                    logger.error("Catch-up callback error: {}", e.getMessage());
                }
            }

            // Re-subscribe
            try {
                Map<String, Object> subData = new HashMap<>();
                subData.put("method", "subscribe_file_change");
                Map<String, Object> params = new HashMap<>();
                params.put("path", path);
                subData.put("params", params);

                WsClient.StreamHandle handle = finalWsClient.callStream(
                    serverName, subData, null, null, null
                ).get(10, TimeUnit.SECONDS);
                handle.waitEnd().get(10, TimeUnit.SECONDS);
                logger.info("Resubscribed after reconnect for: {}", path);
            } catch (Exception e) {
                logger.error("Re-subscribe failed: {}", e.getMessage());
            }
        });

        // Subscribe via WsClient
        try {
            Map<String, Object> subData = new HashMap<>();
            subData.put("method", "subscribe_file_change");
            Map<String, Object> params = new HashMap<>();
            params.put("path", path);
            subData.put("params", params);

            WsClient.StreamHandle handle = wsClient.callStream(
                serverName, subData, null, null, null
            ).get(15, TimeUnit.SECONDS);
            handle.waitEnd().get(15, TimeUnit.SECONDS);
            subscriptionActive.set(true);
        } catch (Exception e) {
            logger.warn("WS push subscribe failed: {}. Falling back to polling.", e.getMessage());
            if (unsubscribePush != null) { try { unsubscribePush.run(); } catch (Exception ignored) {} }
            if (unsubscribeState != null) { try { unsubscribeState.run(); } catch (Exception ignored) {} }
            pollingLoop(path, callback, intervalMs, stop);
            return;
        }

        // Catch-up poll: fill gap between baseline and subscribe
        FileChangeResult catchup = getFileChange(path);
        if (catchup.isSuccess() && !catchup.getEvents().isEmpty()) {
            try {
                callback.onFileChange(catchup.getEvents());
            } catch (Exception e) {
                logger.error("Catch-up callback error: {}", e.getMessage());
            }
        }

        logger.info("WS push monitoring active for: {}", path);

        // Wait loop
        while (!stop.get()) {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
                break;
            }
        }

        // Cleanup
        subscriptionActive.set(false);
        if (unsubscribePush != null) { try { unsubscribePush.run(); } catch (Exception ignored) {} }
        if (unsubscribeState != null) { try { unsubscribeState.run(); } catch (Exception ignored) {} }
        try {
            Map<String, Object> unsubData = new HashMap<>();
            unsubData.put("method", "unsubscribe_file_change");
            Map<String, Object> params = new HashMap<>();
            params.put("path", path);
            unsubData.put("params", params);
            wsClient.sendMessage(serverName, unsubData);
        } catch (Exception ignored) {
        }
        logger.info("Stopped WS push monitoring for: {}", path);
    }
}
