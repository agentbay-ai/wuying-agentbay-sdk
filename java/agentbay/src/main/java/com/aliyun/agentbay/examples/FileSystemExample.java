package com.aliyun.agentbay.examples;

import com.aliyun.agentbay.AgentBay;
import com.aliyun.agentbay.exception.AgentBayException;
import com.aliyun.agentbay.filesystem.*;
import com.aliyun.agentbay.model.*;
import com.aliyun.agentbay.session.CreateSessionParams;
import com.aliyun.agentbay.session.Session;

import java.util.*;

/**
 * FileSystem Example - Java equivalent of Python filesystem management
 * 
 * This example demonstrates how to:
 * 1. Basic file reading and writing
 * 2. Directory operations
 * 3. File information retrieval
 * 4. File editing
 * 5. File searching
 * 6. Multiple file reading
 * 7. Large file operations
 */
public class FileSystemExample {
    
    public static void main(String[] args) {
        String apiKey = System.getenv("AGENTBAY_API_KEY");
        if (apiKey == null || apiKey.trim().isEmpty()) {
            System.err.println("Error: AGENTBAY_API_KEY environment variable not set");
            return;
        }

        // Initialize the AgentBay client
        Session session = null;
        
        try {
            System.out.println("Initializing AgentBay client...");
            AgentBay agentBay = new AgentBay();
            
            // Create a session
            System.out.println("Creating a new session...");
            CreateSessionParams params = new CreateSessionParams();
            params.setImageId("linux_latest");

            SessionResult sessionResult = agentBay.create(params);
            session = sessionResult.getSession();
            System.out.println("Session created with ID: " + session.getSessionId());
            System.out.println("Request ID: " + sessionResult.getRequestId());
            
            // Get the FileSystem interface
            FileSystem fs = session.getFileSystem();
            
            // ===== BASIC FILE OPERATIONS =====
            System.out.println("\n===== BASIC FILE OPERATIONS =====");
            
            // Example 1: Write a simple file
            System.out.println("\nExample 1: Writing a simple file...");
            String testContent = "This is a test file content.\nIt has multiple lines.\nThis is the third line.";
            String testFilePath = "/tmp/test_file.txt";
            
            BoolResult result = fs.writeFile(testFilePath, testContent, "overwrite");
            System.out.println("File write successful: " + result.isSuccess());
            if (!result.isSuccess()) {
                System.out.println("Error: " + result.getErrorMessage());
            }
            System.out.println("Request ID: " + result.getRequestId());
            
            // Example 2: Read the file
            System.out.println("\nExample 2: Reading the file...");
            FileContentResult readResult = fs.readFile(testFilePath);
            if (readResult.isSuccess()) {
                String content = readResult.getContent();
                System.out.println("File content (" + content.length() + " bytes):");
                System.out.println(content);
                System.out.println("Content matches original: " + content.equals(testContent));
            } else {
                System.out.println("Error reading file: " + readResult.getErrorMessage());
            }
            System.out.println("Request ID: " + readResult.getRequestId());
            
            // Example 3: Append to the file
            System.out.println("\nExample 3: Appending to the file...");
            String appendContent = "\nThis is an appended line.";
            BoolResult appendResult = fs.writeFile(testFilePath, appendContent, "append");
            System.out.println("File append successful: " + appendResult.isSuccess());
            if (!appendResult.isSuccess()) {
                System.out.println("Error: " + appendResult.getErrorMessage());
            }
            System.out.println("Request ID: " + appendResult.getRequestId());
            
            // Read the file again to verify append
            FileContentResult updatedReadResult = fs.readFile(testFilePath);
            if (updatedReadResult.isSuccess()) {
                String updatedContent = updatedReadResult.getContent();
                System.out.println("Updated file content (" + updatedContent.length() + " bytes):");
                System.out.println(updatedContent);
                System.out.println("Content matches: " + updatedContent.equals(testContent + appendContent));
            } else {
                System.out.println("Error reading updated file: " + updatedReadResult.getErrorMessage());
            }
            System.out.println("Request ID: " + updatedReadResult.getRequestId());
            
            // ===== DIRECTORY OPERATIONS =====
            System.out.println("\n===== DIRECTORY OPERATIONS =====");
            
            // Example 4: Create a directory
            System.out.println("\nExample 4: Creating a directory...");
            String testDirPath = "/tmp/test_directory";
            BoolResult dirResult = fs.createDirectory(testDirPath);
            System.out.println("Directory creation successful: " + dirResult.isSuccess());
            if (!dirResult.isSuccess()) {
                System.out.println("Error: " + dirResult.getErrorMessage());
            }
            System.out.println("Request ID: " + dirResult.getRequestId());
            
            // Example 5: List directory contents
            System.out.println("\nExample 5: Listing directory contents...");
            DirectoryListResult listResult = fs.listDirectory("/tmp");
            if (listResult.isSuccess()) {
                List<com.aliyun.agentbay.model.DirectoryEntry> entries = listResult.getEntries();
                System.out.println("Found " + entries.size() + " entries in /tmp:");
                for (com.aliyun.agentbay.model.DirectoryEntry entry : entries) {
                    String entryType = entry.isDirectory() ? "Directory" : "File";
                    System.out.println("  - " + entry.getName() + " (" + entryType + ")");
                }
            } else {
                System.out.println("Error listing directory: " + listResult.getErrorMessage());
            }
            System.out.println("Request ID: " + listResult.getRequestId());
            
            // ===== FILE INFORMATION =====
            System.out.println("\n===== FILE INFORMATION =====");
            
            // Example 6: Get file information
            System.out.println("\nExample 6: Getting file information...");
            FileInfoResult infoResult = fs.getFileInfo(testFilePath);
            if (infoResult.isSuccess()) {
                Map<String, Object> fileInfo = infoResult.getFileInfo();
                System.out.println("File information for " + testFilePath + ":");
                for (Map.Entry<String, Object> entry : fileInfo.entrySet()) {
                    System.out.println("  - " + entry.getKey() + ": " + entry.getValue());
                }
            } else {
                System.out.println("Error getting file info: " + infoResult.getErrorMessage());
            }
            System.out.println("Request ID: " + infoResult.getRequestId());
            
            // ===== FILE EDITING =====
            System.out.println("\n===== FILE EDITING =====");
            
            // Example 7: Edit a file
            System.out.println("\nExample 7: Editing a file...");
            List<Map<String, String>> edits = new ArrayList<>();
            Map<String, String> edit = new HashMap<>();
            edit.put("oldText", "This is the third line.");
            edit.put("newText", "This line has been edited.");
            edits.add(edit);
            
            BoolResult editResult = fs.editFile(testFilePath, edits);
            System.out.println("File edit successful: " + editResult.isSuccess());
            if (!editResult.isSuccess()) {
                System.out.println("Error: " + editResult.getErrorMessage());
            }
            System.out.println("Request ID: " + editResult.getRequestId());
            
            // Read the file again to verify edit
            FileContentResult editedReadResult = fs.readFile(testFilePath);
            if (editedReadResult.isSuccess()) {
                String editedContent = editedReadResult.getContent();
                System.out.println("Edited file content (" + editedContent.length() + " bytes):");
                System.out.println(editedContent);
            } else {
                System.out.println("Error reading edited file: " + editedReadResult.getErrorMessage());
            }
            System.out.println("Request ID: " + editedReadResult.getRequestId());
            
            // ===== FILE MOVING =====
            System.out.println("\n===== FILE MOVING =====");
            
            // Example 8: Move a file
            System.out.println("\nExample 8: Moving a file...");
            String sourcePath = "/tmp/test_file.txt";
            String destPath = "/tmp/test_directory/moved_file.txt";
            BoolResult moveResult = fs.moveFile(sourcePath, destPath);
            System.out.println("File move successful: " + moveResult.isSuccess());
            if (!moveResult.isSuccess()) {
                System.out.println("Error: " + moveResult.getErrorMessage());
            }
            System.out.println("Request ID: " + moveResult.getRequestId());
            
            // Verify the file was moved
            FileContentResult movedReadResult = fs.readFile(destPath);
            if (movedReadResult.isSuccess()) {
                String movedContent = movedReadResult.getContent();
                System.out.println("Moved file content length: " + movedContent.length() + " bytes");
                System.out.println("Content preserved after move: " + movedContent.equals(editedReadResult.getContent()));
            } else {
                System.out.println("Error reading moved file: " + movedReadResult.getErrorMessage());
            }
            System.out.println("Request ID: " + movedReadResult.getRequestId());
            
            // ===== FILE SEARCHING =====
            System.out.println("\n===== FILE SEARCHING =====");
            
            // Create some files for searching
            fs.writeFile("/tmp/test_directory/file1.txt", "This file contains the word SEARCHABLE", "overwrite");
            fs.writeFile("/tmp/test_directory/file2.txt", "This file does not contain the keyword", "overwrite");
            fs.writeFile("/tmp/test_directory/file3.txt", "This file also contains SEARCHABLE term", "overwrite");
            
            // Example 9: Search for files
            System.out.println("\nExample 9: Searching for files...");
            FileSearchResult searchResult = fs.searchFiles("/tmp/test_directory", "SEARCHABLE");
            if (searchResult.isSuccess()) {
                List<String> searchMatches = searchResult.getMatches();
                System.out.println("Found " + searchMatches.size() + " files matching the search pattern:");
                for (String resultFile : searchMatches) {
                    System.out.println("  - " + resultFile);
                }
            } else {
                System.out.println("Error searching files: " + searchResult.getErrorMessage());
            }
            System.out.println("Request ID: " + searchResult.getRequestId());
            
            // ===== MULTIPLE FILE READING =====
            System.out.println("\n===== MULTIPLE FILE READING =====");
            
            // Example 10: Read multiple files
            System.out.println("\nExample 10: Reading multiple files...");
            List<String> filePaths = Arrays.asList(
                "/tmp/test_directory/file1.txt",
                "/tmp/test_directory/file2.txt",
                "/tmp/test_directory/file3.txt"
            );
            
            MultipleFileContentResult multiReadResult = fs.readMultipleFiles(filePaths);
            if (multiReadResult.isSuccess()) {
                Map<String, String> multiFileContents = multiReadResult.getContent();
                System.out.println("Read " + multiFileContents.size() + " files:");
                for (Map.Entry<String, String> entry : multiFileContents.entrySet()) {
                    System.out.println("  - " + entry.getKey() + ": " + entry.getValue().length() + " bytes");
                    System.out.println("    Content: " + entry.getValue());
                }
            } else {
                System.out.println("Error reading multiple files: " + multiReadResult.getErrorMessage());
            }
            System.out.println("Request ID: " + multiReadResult.getRequestId());
            
            // ===== CREATE PARENT DIRECTORY TEST =====
            System.out.println("\n===== CREATE PARENT DIRECTORY TEST =====");

            // Example 11: Test create_parent_dir parameter
            System.out.println("\nExample 11: Testing create_parent_dir parameter...");

            // Test 1: Write file without creating parent directory (should fail)
            String nestedFilePath = "/tmp/non_existent_dir/subdir/test.txt";
            String nestedContent = "This is a test file in nested directories.";

            System.out.println("Test 1: Writing to nested path WITHOUT creating parent directories...");
            BoolResult writeWithoutParent = fs.writeFile(nestedFilePath, nestedContent, "overwrite", false);
            System.out.println("Success (should be false): " + writeWithoutParent.isSuccess());
            if (!writeWithoutParent.isSuccess()) {
                System.out.println("Expected error: " + writeWithoutParent.getErrorMessage());
            }

            // Test 2: Write file with creating parent directory (should succeed)
            System.out.println("\nTest 2: Writing to nested path WITH creating parent directories...");
            BoolResult writeWithParent = fs.writeFile(nestedFilePath, nestedContent, "overwrite", true);
            System.out.println("Success (should be true): " + writeWithParent.isSuccess());
            if (!writeWithParent.isSuccess()) {
                System.out.println("Error: " + writeWithParent.getErrorMessage());
            } else {
                System.out.println("File successfully written to: " + nestedFilePath);

                // Verify the file content
                FileContentResult verifyResult = fs.readFile(nestedFilePath);
                if (verifyResult.isSuccess()) {
                    System.out.println("File content verified: " + verifyResult.getContent().equals(nestedContent));
                    System.out.println("Content: " + verifyResult.getContent());
                }
            }

            // ===== LARGE FILE OPERATIONS =====
            System.out.println("\n===== LARGE FILE OPERATIONS =====");

            // Example 12: Write a large file
            System.out.println("\nExample 12: Writing a large file...");
            
            // Generate approximately 1MB of test content
            StringBuilder largeContentBuilder = new StringBuilder();
            String lineContent = "This is a line of test content for large file testing. ";
            for (int i = 0; i < 20; i++) {
                largeContentBuilder.append(lineContent);
            }
            String singleLine = largeContentBuilder.toString();
            
            largeContentBuilder = new StringBuilder();
            for (int i = 0; i < 50; i++) {
                largeContentBuilder.append(singleLine).append("\n");
            }
            String largeContent = largeContentBuilder.toString();
            String largeFilePath = "/tmp/large_file.txt";
            
            System.out.println("Generated test content size: " + largeContent.length() + " bytes");
            
            long startTime = System.currentTimeMillis();
            BoolResult largeWriteResult = fs.writeFile(largeFilePath, largeContent);
            long writeTime = System.currentTimeMillis() - startTime;
            
            System.out.println("Write operation completed in " + (writeTime / 1000.0) + " seconds");
            System.out.println("Success: " + largeWriteResult.isSuccess());
            if (!largeWriteResult.isSuccess()) {
                System.out.println("Error: " + largeWriteResult.getErrorMessage());
            }
            System.out.println("Request ID: " + largeWriteResult.getRequestId());
            
            // Example 13: Read the large file
            System.out.println("\nExample 13: Reading the large file...");
            
            startTime = System.currentTimeMillis();
            FileContentResult largeReadResult = fs.readFile(largeFilePath);
            long readTime = System.currentTimeMillis() - startTime;
            
            if (largeReadResult.isSuccess()) {
                String readContent = largeReadResult.getContent();
                System.out.println("Read operation completed in " + (readTime / 1000.0) + " seconds");
                System.out.println("Content length: " + readContent.length() + " bytes");
                System.out.println("Content matches original: " + readContent.equals(largeContent));
            } else {
                System.out.println("Error reading large file: " + largeReadResult.getErrorMessage());
            }
            System.out.println("Request ID: " + largeReadResult.getRequestId());
        } catch (AgentBayException e) {
            System.err.println("AgentBay error: " + e.getMessage());
        } catch (Exception e) {
            System.err.println("Unexpected error: " + e.getMessage());
        } finally {
            // Clean up: Delete the session
            if (session != null) {
                try {
                    System.out.println("\nCleaning up: Deleting the session...");
                    DeleteResult deleteResult = session.delete();
                    System.out.println("Session deleted successfully. Request ID: " + deleteResult.getRequestId());
                } catch (Exception e) {
                    System.err.println("Error deleting session: " + e.getMessage());
                }
            }
        }
    }
}