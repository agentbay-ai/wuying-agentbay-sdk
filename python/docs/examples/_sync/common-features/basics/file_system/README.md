# FileSystem Examples

This directory contains comprehensive examples demonstrating the FileSystem functionality in the AgentBay SDK for Python. It covers both basic file operations and advanced features like file monitoring and transfers.

## Examples

### Basic Operations Example ([basic_file_operations_example.py](./basic_file_operations_example.py))

Demonstrates fundamental file system operations:

- Basic file reading and writing
- Directory creation and listing
- File information retrieval
- File editing and moving
- File searching
- Multiple file reading
- Large file operations with automatic chunking

### Watch Directory Example ([watch_directory_example.py](./watch_directory_example.py))

Demonstrates how to monitor file changes in a directory:

- Creating directories for monitoring
- Setting up file change monitoring with callbacks
- Performing file operations to trigger events
- Processing different types of file events (create, modify, delete)
- Proper resource cleanup

### File Transfer Example ([file_transfer_example.py](./file_transfer_example.py))

Demonstrates file upload and download operations:

- Creating contexts and sessions with file transfer capabilities
- Using the simplified FileSystem API for file transfers
- Uploading files from local storage to the cloud
- Downloading files from the cloud to local storage
- Tracking file transfer progress with callbacks
- Verifying file content integrity after transfers
- Proper resource cleanup

## Features Demonstrated

### Basic File Operations
- **File Writing**: Create new files with content
- **File Reading**: Read file contents
- **File Appending**: Add content to existing files

### Directory Operations
- **Directory Creation**: Create new directories
- **Directory Listing**: List contents of directories

### File Information
- **File Info Retrieval**: Get detailed information about files (size, permissions, etc.)

### File Manipulation
- **File Editing**: Edit specific parts of file content
- **File Moving**: Move files between directories

### Search Operations
- **File Searching**: Search for files containing specific patterns

### Multiple File Operations
- **Multiple File Reading**: Read multiple files in a single operation

### Large File Operations
- **Large File Writing**: Write files larger than the default API size limits using automatic chunking
- **Large File Reading**: Read large files using automatic chunking
- **Custom Chunk Size**: Specify custom chunk sizes for both reading and writing operations
- **Performance Measurement**: Measure and compare operation times with different chunk sizes

### Advanced Features
- **Real-time File Monitoring**: Monitor directory changes with event callbacks
- **File Transfer Operations**: Upload and download files with progress tracking
- **Context Synchronization**: Use contexts for persistent file operations

## Prerequisites

- Python 3.10 or later
- Wuying AgentBay SDK installed:
  ```bash
  pip install wuying-agentbay-sdk
  ```

## Running the Examples

1. Make sure you have set the `AGENTBAY_API_KEY` environment variable:

```bash
export AGENTBAY_API_KEY=your_api_key_here
```

2. Run any of the examples:

```bash
# Basic file operations
python basic_file_operations_example.py

# Directory monitoring
python watch_directory_example.py

# File transfers
python file_transfer_example.py
```

## Code Explanation

### Basic Operations Example (basic_file_operations_example.py)

The basic operations example demonstrates the following workflow:

1. **Session Creation**: Creates a new session with the specified image ID
2. **Basic File Operations**: Demonstrates writing, reading, and appending to files
3. **Directory Operations**: Shows how to create directories and list their contents
4. **File Information**: Retrieves and displays detailed file information
5. **File Editing**: Demonstrates how to edit specific parts of a file
6. **File Moving**: Shows how to move files between directories
7. **File Searching**: Searches for files containing specific patterns
8. **Multiple File Reading**: Reads multiple files in a single operation
9. **Large File Operations**: Demonstrates reading and writing large files with both default and custom chunk sizes
10. **Content Verification**: Verifies that file operations maintain content integrity
11. **Performance Comparison**: Measures and reports the time taken for large file operations

### Watch Directory Example

The watch directory example demonstrates real-time file monitoring capabilities:

1. Initialize the AgentBay client with an API key
2. Create a session with a suitable image
3. Create a test directory to monitor
4. Set up monitoring with a callback function to handle file events
5. Perform various file operations to trigger events
6. Process and display the detected file changes
7. Clean up resources properly

### File Transfer Example

The file transfer example demonstrates uploading and downloading files:

1. Initialize the AgentBay client with an API key
2. Create a context for file operations
3. Create a browser session with context synchronization
4. Create test files for upload
5. Upload files to the cloud using the simplified API
6. Download files from the cloud to local storage
7. Track progress during transfers
8. Verify file content integrity
9. Clean up resources properly

Each section of the examples is clearly marked and includes verification steps to ensure operations are working correctly.

## API Reference

For more detailed information on the FileSystem API methods, refer to the SDK documentation.