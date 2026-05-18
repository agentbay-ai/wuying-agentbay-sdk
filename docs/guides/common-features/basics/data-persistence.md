# Complete Data Persistence Guide

This guide covers AgentBay SDK's data persistence features, including context concepts, context management, and data synchronization strategies for maintaining state across sessions. Both synchronous and asynchronous APIs are supported.

> **Multi-language support:** Code examples use Python. Data persistence APIs are available in all SDKs with similar patterns. See: [Python](../../../../python/README.md) | [TypeScript](../../../../typescript/README.md) | [Golang](../../../../golang/README.md) | [Java](../../../../java/README.md)

## 📋 Table of Contents

- [Core Concepts](#core-concepts)
- [Context Management](#context-management)
- [Dynamic Context Binding](#dynamic-context-binding)
- [Data Synchronization Strategies](#data-synchronization-strategies)
- [Context Mount (Direct-Mount Persistence) [Beta]](#context-mount-direct-mount-persistence-beta)

<a id="core-concepts"></a>
## 🎯 Core Concepts

### Understanding Context - A Simple Example

Before diving into complex features, let's understand what Context and ContextId represent with the simplest possible example:

```python
from agentbay import AgentBay

# Initialize client
agent_bay = AgentBay()

# Create a context - think of it as a "named storage box"
context_result = agent_bay.context.get("my-storage-box", create=True)
context = context_result.context

print(f"Context Name: {context.name}")        # Output: "my-storage-box"
print(f"Context ID: {context.id}")           # Output: "SdkCtx-123abc456def" (unique identifier)
```

**What is a Context?**
- A **Context** is like a persistent storage container that survives beyond individual sessions
- The **Context Name** (like "my-storage-box") is what you use to reference it
- The **Context ID** (like "SdkCtx-123abc456def") is the system's unique identifier for that storage container

**What is a ContextId?**
- Every Context has a unique ID assigned by the system
- You use this ID to mount the context's data into sessions
- Think of it as the "address" where your persistent data lives

### The Persistence Problem

In AgentBay, **sessions are temporary** - when a session ends, all its data disappears:

```python
# Without Context: Data is LOST when session ends
session1 = agent_bay.create().session
session1.file_system.write_file("/tmp/data.txt", "Important data")
agent_bay.delete(session1)
# Session ends -> data.txt is GONE forever!

# With Context: Data is SAVED permanently
from agentbay import ContextSync, CreateSessionParams

context = agent_bay.context.get("my-storage", create=True).context
context_sync = ContextSync.new(context.id, "/tmp/persistent")  # Mount context at /tmp/persistent

session2 = agent_bay.create(CreateSessionParams(context_syncs=[context_sync])).session
session2.file_system.write_file("/tmp/persistent/data.txt", "Important data")
agent_bay.delete(session2, sync_context=True)  # Ensure data syncs before continuing

# Later, in a new session, you can access the same data:
session3 = agent_bay.create(CreateSessionParams(context_syncs=[context_sync])).session
content = session3.file_system.read_file("/tmp/persistent/data.txt")
print(content.content)  # Output: "Important data"
agent_bay.delete(session3)
```

### Implementation Principle - How Context Works Under the Hood

Understanding the technical implementation helps you better use the Context system:

**Context Storage Architecture:**
```
ContextId (e.g., "SdkCtx-123abc456def")
    ↓
OSS Directory (/contexts/SdkCtx-123abc456def/)
    ├── file1.txt
    ├── data/
    │   └── config.json
    └── logs/
        └── app.log
```

**What happens when you create a Context:**
1. **OSS Directory Creation**: AgentBay creates a dedicated OSS (Object Storage Service) directory
2. **Unique Mapping**: Each ContextId maps to a specific OSS path like `/contexts/{SdkCtx-123abc456def}/`
3. **Persistent Storage**: All files in this OSS directory persist beyond session lifecycles

**What happens when you bind Context to Session:**
```python
# This line tells the session: "Download OSS files to /tmp/persistent"
context_sync = ContextSync.new(context.id, "/tmp/persistent")
session = agent_bay.create(CreateSessionParams(context_syncs=[context_sync])).session
```

**Session Lifecycle with Context:**
1. **Session Start**: Downloads all files from OSS directory to `/tmp/persistent`
2. **Session Runtime**: You work with files in `/tmp/persistent` as normal local files  
3. **Session End**: Uploads all changes from `/tmp/persistent` back to OSS directory

### Beta: Skip waiting for non-critical contexts during session creation

By default, when you create a session with `ContextSync`, the SDK will wait until the context download finishes before returning the session object. This is the safest default because your files are guaranteed to be present at the mount path.

For latency-sensitive workloads, you may want to start the session as soon as possible and let large, non-critical contexts download in the background. You can do this by setting the beta flag on specific `ContextSync` entries:

```python
from agentbay import AgentBay, ContextSync, CreateSessionParams, SyncPolicy

agent_bay = AgentBay()
ctx = agent_bay.context.get("my-big-context", create=True).context

# Do not block create() on this context download (beta)
cs = ContextSync.new(ctx.id, "/tmp/persistent", SyncPolicy.default(), beta_wait_for_completion=False)
session = agent_bay.create(CreateSessionParams(context_syncs=[cs])).session
```

**Visual Flow:**
```
OSS Storage          Session Environment          OSS Storage After Upload
┌─────────────┐      ┌──────────────────┐      ┌──────────────────┐
│             │ ───► │ /tmp/persistent/ │ ───► │                  │
│ SdkCtx-123/ │      │   ├── file1      │      │ SdkCtx-123/      │
│ ├── file1   │      │   ├── data       │      │ ├── file1        │
│ └── data    │      │   └── output.log │      │ ├── data         │
└─────────────┘      │   (new file)     │      │ └── output.log   │
   Download          └──────────────────┘      └──────────────────┘
   on Start                                       Upload on End
```

**What this diagram shows:**
- **Left**: Initial OSS directory with existing files (`file1`, `data`) 
- **Middle**: Session workspace with downloaded files + new files you create (`output.log`)
- **Right**: Final OSS directory with ALL changes uploaded back (modified/original files + new files)

**Key Benefits of this Architecture:**
- **Scalability**: OSS handles large files and directories efficiently
- **Reliability**: Cloud storage ensures data durability and availability
- **Performance**: Local file operations during session for fast I/O
- **Sharing**: Multiple sessions can mount the same OSS directory

### Dynamic Context Binding

In addition to binding contexts at session creation time, AgentBay supports **dynamic context binding** — mounting contexts to a running session on demand. This is useful when:

- You don't know which contexts will be needed until runtime
- An AI agent discovers it needs additional data mid-task
- You want to progressively load data as requirements emerge

#### Binding Contexts After Session Creation

```python
from agentbay import AgentBay, ContextSync, SyncPolicy, CreateSessionParams

agent_bay = AgentBay()

# Create a session WITHOUT any initial context
session = agent_bay.create(CreateSessionParams()).session

# Later, dynamically bind a context
context = agent_bay.context.get("project-data", create=True).context
context_sync = ContextSync.new(context.id, "/tmp/project-data", SyncPolicy.default())

bind_result = session.context.bind(context_sync)
if bind_result.success:
    print("Context bound successfully!")
    # Files from 'project-data' context are now available at /tmp/project-data
    content = session.file_system.read_file("/tmp/project-data/config.json")
```

#### Binding Multiple Contexts at Once

```python
# Create two contexts
ctx_a = agent_bay.context.get("dataset-a", create=True).context
ctx_b = agent_bay.context.get("dataset-b", create=True).context

policy = SyncPolicy.default()
cs_a = ContextSync.new(ctx_a.id, "/tmp/dataset-a", policy)
cs_b = ContextSync.new(ctx_b.id, "/tmp/dataset-b", policy)

# Bind both at once
bind_result = session.context.bind(cs_a, cs_b)
if bind_result.success:
    print("Both contexts bound!")
```

#### Listing Current Bindings

```python
bindings_result = session.context.list_bindings()
if bindings_result.success:
    for binding in bindings_result.bindings:
        print(f"  Context: {binding.context_name} -> {binding.path}")
```

#### Key Differences: Creation-Time vs Dynamic Binding

| Aspect | Creation-Time Binding | Dynamic Binding |
|--------|----------------------|-----------------|
| **When** | At `create()` call | Any time during session |
| **How** | `CreateSessionParams(context_syncs=[...])` | `session.context.bind(...)` |
| **Wait for download** | SDK waits by default | SDK polls until binding confirmed |
| **Use case** | Known data requirements | Discovered at runtime |

> **Note:** Each path can only be bound once per session. Attempting to bind a different context to an already-bound path will result in a `PathAlreadyBound` error. Paths under `/tmp/` are recommended for dynamic binding.

### Context vs Session

| Feature | Session | Context |
|---------|---------|---------|
| Lifecycle | Temporary, destroyed when session ends | Persistent, destroyed only when manually deleted |
| Data Storage | Not saved | Permanently saved in OSS |
| Sharing | Independent, not shared | Can be shared across multiple sessions |
| Use Case | Execute temporary tasks | Store project data, configurations, etc. |
| Implementation | Local filesystem only | OSS directory + local filesystem sync |

### Persistence Options: Built-in Context vs Custom OSS

In addition to Context, AgentBay also supports integrating your own Object Storage Service (OSS) for data persistence. Here's how they compare:

| Feature | Built-in Context | Custom OSS Integration |
|---------|------------------|------------------------|
| **Underlying Storage** | AgentBay-managed OSS | User-managed OSS (e.g., Alibaba Cloud OSS) |
| **Mechanism** | Automatic synchronization (Context Sync) | Manual atomic operations (Upload/Download APIs) |
| **Setup** | Zero configuration (just use Context ID) | Requires configuring credentials (STS) & buckets |
| **Cost** | Storage fees charged by AgentBay | Storage fees paid directly to cloud provider |
| **Use Case** | Seamless session state persistence, ease of use | Integration with existing data pipelines, fine-grained control |
| **Data Sync** | Automatic sync on session start/end | Manual API calls required |

**Context (Recommended for most users):**
- Based on AgentBay's internal OSS implementation.
- Provides a robust data synchronization mechanism (automatic download on start, upload on stop).
- Storage costs are included in AgentBay's billing.
- Best for persisting workspace state, configuration, and project files between sessions effortlessly.

**Custom OSS (For advanced integration):**
- Allows you to use your own OSS buckets for data persistence.
- AgentBay provides atomic APIs for file operations (upload, download).
- You manage the storage costs and credentials directly with the provider.
- Best when you need to access existing data lakes, share data with external systems, or have specific compliance requirements.

See the [OSS Integration Guide](../advanced/oss-integration.md) for details on using your own OSS.

<a id="context-management"></a>
## 📦 Context Management

### Creating and Getting Contexts

```python
from agentbay import AgentBay

# Initialize AgentBay client (requires valid API key)
#api_key from your os env
agent_bay = AgentBay(api_key=api_key)

 # Initialize AgentBay client (requires valid API key)
agent_bay = AgentBay()

# Get or create context
context_result = agent_bay.context.get("my-project", create=True)
if context_result.success:
    context = context_result.context
    print(f"Context ID: {context.id}")
    print(f"Context Name: {context.name}")
    print(f"Created At: {context.created_at}")
else:
    print(f"Context operation failed: {context_result.success}")

# Get existing context only
existing_context_result = agent_bay.context.get("my-project", create=False)
if not existing_context_result.success:
    print("Context does not exist")
else:
context = existing_context_result.context
print(f"Found context: {context.name}")
```


### Listing and Deleting Contexts

```python
# List all contexts (default pagination)
contexts_result = agent_bay.context.list()
if contexts_result.success:
    print(f"Total contexts: {contexts_result.total_count}")
    for context in contexts_result.contexts:
        print(f"Context: {context.name} (ID: {context.id})")
else:
    print(f"Failed to list contexts: {contexts_result.error_message}")

# List contexts with pagination
from agentbay import ContextListParams

params = ContextListParams(max_results=20)
result = agent_bay.context.list(params)

if result.success:
    print(f"Total contexts: {result.total_count}")
    print(f"Current page: {len(result.contexts)} contexts")
    
    # Iterate through all pages
    while result.next_token:
        params = ContextListParams(max_results=20, next_token=result.next_token)
        result = agent_bay.context.list(params)
        if result.success:
            print(f"Next page: {len(result.contexts)} contexts")
        else:
            print(f"Failed to fetch next page: {result.error_message}")
            break

# Get context by name
context_result = agent_bay.context.get(name="my-project", create=False)
if context_result.success:
    print(f"Found context: {context_result.context.name}")
else:
    print(f"Context not found: {context_result.error_message}")

# Get context by ID
context_result = agent_bay.context.get(context_id="SdkCtx-123abc456def")
if context_result.success:
    print(f"Found context: {context_result.context.name} (ID: {context_result.context.id})")
else:
    print(f"Context not found: {context_result.error_message}")

# Update context name
context_result = agent_bay.context.get(name="old-name", create=False)
if context_result.success:
    context = context_result.context
    context.name = "new-name"
    update_result = agent_bay.context.update(context)
    if update_result.success:
        print("Context name updated successfully")
    else:
        print(f"Failed to update context: {update_result.error_message}")

# Delete context
context_to_delete = agent_bay.context.get("my-project", create=False).context
if context_to_delete:
    delete_result = agent_bay.context.delete(context_to_delete)
    if delete_result.success:
        print("Context deleted successfully")
    else:
        print(f"Failed to delete context: {delete_result.error_message}")
```

## 📁 Context File Operations

Context file operations provide direct access to files stored in a context's OSS directory. These operations are useful when you need to manage files without creating a session, or when you want to integrate context data with external systems.

### When to Use Direct File Operations

**Use direct file operations when:**
- You need to access files without creating a session
- You want to integrate with external systems (webhooks, APIs)
- You need to download/upload large files directly
- You want to inspect context contents programmatically

**Use session sync when:**
- You need to work with files during session execution
- You want automatic bidirectional synchronization
- You're running code that expects local filesystem access

### Getting Presigned URLs

Presigned URLs allow you to upload or download files directly to/from the context's OSS storage without going through a session.

**Note:** The presigned URL expires in 1 hour by default.

```python
from agentbay import AgentBay
import requests

agent_bay = AgentBay()

# Create or get context
context = agent_bay.context.get("my-project", create=True).context

# Get upload URL
upload_result = agent_bay.context.get_file_upload_url(
    context_id=context.id,
    file_path="/data/report.txt"
)

if upload_result.success:
    print(f"Upload URL: {upload_result.url}")
    print(f"URL expires at: {upload_result.expire_time}")
    
    # Upload file using requests library
    file_content = "This is my report content"
    response = requests.put(upload_result.url, data=file_content.encode('utf-8'))
    
    if response.status_code == 200:
        print("File uploaded successfully")
    else:
        print(f"Upload failed: {response.status_code}")
else:
    print(f"Failed to get upload URL: {upload_result.error_message}")

# Get download URL
download_result = agent_bay.context.get_file_download_url(
    context_id=context.id,
    file_path="/data/report.txt"
)

if download_result.success:
    print(f"Download URL: {download_result.url}")
    
    # Download file using requests library
    response = requests.get(download_result.url)
    
    if response.status_code == 200:
        content = response.text
        print(f"File content: {content}")
    else:
        print(f"Download failed: {response.status_code}")
else:
    print(f"Failed to get download URL: {download_result.error_message}")
```

### Listing Files

List files in a context with pagination support:

```python
from agentbay import AgentBay

agent_bay = AgentBay()

# Get context
context = agent_bay.context.get("my-project", create=True).context

# List files in root directory (token-based pagination recommended)
list_result = agent_bay.context.list_files(
    context_id=context.id,
    parent_folder_path="/",
    max_results=50,
)

if list_result.success:
    print(f"Found {len(list_result.entries)} files")
    
    for entry in list_result.entries:
        print(f"File: {entry.file_name}")
        print(f"  Path: {entry.file_path}")
        print(f"  Size: {entry.size} bytes")
        print(f"  Type: {entry.file_type}")
        print(f"  Created: {entry.gmt_create}")
        print(f"  Modified: {entry.gmt_modified}")
else:
    print(f"Failed to list files: {list_result.error_message}")

# List files with token-based pagination
next_token = None
page_index = 1

while True:
    list_result = agent_bay.context.list_files(
        context_id=context.id,
        parent_folder_path="/data",
        max_results=10,
        next_token=next_token,
    )
    
    if not list_result.success:
        print(f"Failed to list files: {list_result.error_message}")
        break
    
    if not list_result.entries:
        print("No more files")
        break
    
    print(f"Page {page_index}: {len(list_result.entries)} files")
    for entry in list_result.entries:
        print(f"  - {entry.file_name} ({entry.size} bytes)")
    
    if not list_result.next_token:
        break
    next_token = list_result.next_token
    page_index += 1
```

### Deleting Files

Delete specific files from a context:

```python
from agentbay import AgentBay

agent_bay = AgentBay()

# Get context
context = agent_bay.context.get("my-project", create=True).context

# Delete a single file
delete_result = agent_bay.context.delete_file(
    context_id=context.id,
    file_path="/data/old_report.txt"
)

if delete_result.success:
    print("File deleted successfully")
else:
    print(f"Failed to delete file: {delete_result.error_message}")

# Delete multiple files
files_to_delete = ["/logs/debug.log", "/temp/cache.dat", "/old/data.json"]

for file_path in files_to_delete:
    delete_result = agent_bay.context.delete_file(
        context_id=context.id,
        file_path=file_path
    )
    
    if delete_result.success:
        print(f"Deleted: {file_path}")
    else:
        print(f"Failed to delete {file_path}: {delete_result.error_message}")
```

## 🗑️ Context Data Clearing

Context clearing removes all files from a context while keeping the context itself intact. This is useful when you want to reset a context's data without deleting and recreating it.

### Clear vs Delete

| Operation | Context | Context ID | Files | Use Case |
|-----------|---------|------------|-------|----------|
| **Clear** | Preserved | Unchanged | Deleted | Reset data, keep configuration |
| **Delete** | Removed | Lost | Deleted | Complete cleanup, remove context |

**When to use Clear:**
- Reset a context for a new workflow run
- Clean up temporary data periodically
- Prepare a context for fresh data
- Keep context references in your code valid

**When to use Delete:**
- Remove a context completely
- Clean up unused contexts
- Context is no longer needed

### Synchronous Clear (Recommended)

The simplest way to clear a context is using the synchronous `clear()` method, which waits for the operation to complete:

```python
from agentbay import AgentBay
from agentbay import ClearanceTimeoutError

agent_bay = AgentBay()

# Get context
context = agent_bay.context.get("my-project", create=True).context

# Clear context data (synchronous - waits for completion)
try:
    clear_result = agent_bay.context.clear(
        context_id=context.id,
        timeout=60,  # Wait up to 60 seconds
        poll_interval=2.0  # Check status every 2 seconds
    )
    
    if clear_result.success:
        print(f"Context cleared successfully")
        print(f"Final status: {clear_result.status}")  # Should be "available"
    else:
        print(f"Failed to clear context: {clear_result.error_message}")
        
except ClearanceTimeoutError as e:
    print(f"Clearing timed out: {e}")
    # Context may still be clearing in the background
    # You can check status later using get_clear_status()
```

### Asynchronous Clear with Manual Polling

For more control over the clearing process, you can use the asynchronous approach:

```python
from agentbay import AgentBay
import time

agent_bay = AgentBay()

# Get context
context = agent_bay.context.get("my-project", create=True).context

# Start clearing asynchronously
clear_result = agent_bay.context.clear_async(context_id=context.id)

if clear_result.success:
    print(f"Clearing started, status: {clear_result.status}")  # Should be "clearing"
    
    # Poll for completion
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        time.sleep(2)  # Wait 2 seconds between checks
        attempt += 1
        
        # Check status
        status_result = agent_bay.context.get_clear_status(context_id=context.id)
        
        if not status_result.success:
            print(f"Failed to get status: {status_result.error_message}")
            break
        
        print(f"Status: {status_result.status} (attempt {attempt}/{max_attempts})")
        
        if status_result.status == "available":
            print("Context cleared successfully!")
            break
        elif status_result.status == "clearing":
            print("Still clearing...")
        else:
            print(f"Unexpected status: {status_result.status}")
    else:
        print("Clearing timed out")
else:
    print(f"Failed to start clearing: {clear_result.error_message}")
```

### Clear Status States

The clearing operation follows this state machine:

| Status | Description | Next State |
|--------|-------------|------------|
| `clearing` | Data is being deleted | `available` |
| `available` | Clearing completed successfully | - (final state) |

### Error Handling

```python
from agentbay import AgentBay
from agentbay import ClearanceTimeoutError, AgentBayError

agent_bay = AgentBay()

context = agent_bay.context.get("my-project", create=True).context

try:
    # Try to clear with a short timeout
    clear_result = agent_bay.context.clear(
        context_id=context.id,
        timeout=30,
        poll_interval=1.0
    )
    
    if clear_result.success:
        print("Context cleared successfully")
    else:
        print(f"Clear failed: {clear_result.error_message}")
        
except ClearanceTimeoutError as e:
    print(f"Timeout: {e}")
    print("The context may still be clearing in the background")
    
    # Check current status
    status_result = agent_bay.context.get_clear_status(context.id)
    if status_result.success:
        print(f"Current status: {status_result.status}")
        
except AgentBayError as e:
    print(f"API error: {e}")
```

### Context with Sessions

```python
from agentbay import ContextSync, CreateSessionParams

# Create context
context_result = agent_bay.context.get("my-project", create=True)
if context_result.success:
    context = context_result.context
    print(f"Context ID: {context.id}")

    # Create context sync configuration
    context_sync = ContextSync.new(
        context_id=context.id,
        path="/tmp/data"  # Mount path in session
    )

    # === Session 1: Write data ===
    print("\n--- Session 1: Writing data ---")
    params = CreateSessionParams(context_syncs=[context_sync])
    session1_result = agent_bay.create(params)
    
    if session1_result.success:
        session1 = session1_result.session
        print(f"Session 1 ID: {session1.session_id}")

        # Write files to persistent storage
        session1.file_system.write_file("/tmp/data/config.json", '{"version": "1.0", "app": "demo"}')
        session1.file_system.write_file("/tmp/data/user_data.txt", "User preferences and settings")
        print("Data written to /tmp/data/")
        
        # End session1 and ensure data is fully synced to Context
        agent_bay.delete(session1, sync_context=True)
        print("Session 1 ended - data fully synced to Context")
    else:
        print(f"Failed to create session 1: {session1_result.error_message}")

    # === Session 2: Read persisted data ===
    print("\n--- Session 2: Reading persisted data ---")
    session2_result = agent_bay.create(params)
    
    if session2_result.success:
        session2 = session2_result.session
        print(f"Session 2 ID: {session2.session_id}")

        # Read data that was persisted from session1
        config_result = session2.file_system.read_file("/tmp/data/config.json")
        user_data_result = session2.file_system.read_file("/tmp/data/user_data.txt")
        
        if config_result.success and user_data_result.success:
            print(f"✅ Config data: {config_result.content}")
            print(f"✅ User data: {user_data_result.content}")
            print("🎉 Data successfully persisted across sessions!")
        else:
            print("❌ Failed to read persisted data")
            
        # Clean up
        agent_bay.delete(session2)
        print("Session 2 ended")
    else:
        print(f"Failed to create session 2: {session2_result.error_message}")
else:
    print(f"Failed to create context: {context_result.error_message}")
```

### 🔍 Important: Session Deletion and Sync Timing

**The `sync_context` parameter is crucial for reliable persistence:**

```python
# ❌ Potential race condition - may return before upload completes
agent_bay.delete(session)

# ✅ Guaranteed sync - waits for upload completion  
agent_bay.delete(session, sync_context=True)
```

**Why this matters:**

1. **Asynchronous Upload**: When a session ends, file upload to OSS happens asynchronously
2. **Race Condition**: `delete()` returns immediately, but upload may still be in progress
3. **Data Consistency**: Creating a new session too quickly might not see the latest data

**When to use `sync_context=True`:**
- When you need to immediately create another session to access the data
- In automated workflows where timing is critical
- When data consistency across sessions is essential

**Technical Details:**
- `sync_context=True` triggers upload and polls until completion
- The SDK waits for OSS upload confirmation before returning
- This ensures the next session will definitely see all persisted data

**⚠️ Auto-upload Completeness:**

Automatic upload runs when the session ends, but it happens asynchronously on the service side. If you delete a session and immediately start another one, the new session might not see the latest changes until the upload finishes.

**Best Practice to Prevent Data Loss:**

```python
# Option 1: Manual sync before session ends (recommended for large datasets)
session.file_system.write_file("/tmp/data/large_file.bin", large_content)
sync_result = session.context.sync()  # Explicit sync; waits for completion
if sync_result.success:
    print("✅ Data fully synced")
agent_bay.delete(session)  # Safe to delete now

# Option 2: Use sync_context=True on delete (recommended for standard workflows)
session.file_system.write_file("/tmp/data/config.json", config_data)
agent_bay.delete(session, sync_context=True)  # Triggers sync and polls until done
```

**Key Differences:**

| Method | Waits for completion | Best For | Notes |
|--------|----------------------|----------|-------|
| Auto-upload only | No | Quick operations | Next session may briefly miss latest changes |
| `session.context.sync()` | Yes | Large files, many files | Polls with exponential backoff (initial 0.5s, max 5s, up to 150 retries; adjustable via args) |
| `delete(sync_context=True)` | Yes | Standard workflows | SDK triggers `sync()` then deletes after sync completes |

**Recommendation:** Use manual `sync()` or `delete(sync_context=True)` when you need immediate consistency, especially with large or numerous files.

<a id="data-synchronization-strategies"></a>

## 🔄 Data Synchronization Strategies

### Sync Policies

#### Default Synchronization Behavior

By default, AgentBay uses **automatic synchronization** when you don't specify a custom policy:

```python
from agentbay import ContextSync, CreateSessionParams

# Default behavior - no policy specified
context_sync = ContextSync.new(context.id, "/tmp/data")  # Uses default policy
session = agent_bay.create(CreateSessionParams(context_syncs=[context_sync])).session

# Equivalent to:
default_policy = SyncPolicy.default()
context_sync = ContextSync.new(context.id, "/tmp/data", default_policy)
```

**Default policy characteristics:**
- **Auto-download**: Context data is automatically downloaded when the session starts
- **Auto-upload**: Local changes are automatically uploaded when the session ends
- **No periodic sync**: During the session, there is no timed background sync; call `session.context.sync()` if you need mid-session consistency

#### When to Use Custom Sync Policies

You should consider custom sync policies in these scenarios:

1. **Manual control**: When you need precise control over when data is synced (use manual sync policy)
2. **Unidirectional sync**: When you only need upload or download (use upload-only or download-only policies)
3. **Large datasets**: When working with large files that don't need immediate sync
4. **Large file synchronization**: When you need to sync large quantities of files, compression mode can significantly reduce sync time and storage costs (use Archive upload mode)


**Note:** Directory-level whitelisting is supported via `BWList`/`WhiteList` (exact paths only, no wildcards). Use it to limit which subdirectories under the mount point are synced.

#### Available Sync Policy Options

```python
from agentbay import SyncPolicy, UploadPolicy, DownloadPolicy, BWList, WhiteList

# 1. Default policy - syncs all files
default_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=True),
    download_policy=DownloadPolicy(auto_download=True)
)

# 2. Manual sync - sync only when explicitly requested
manual_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=False),
    download_policy=DownloadPolicy(auto_download=False)
)

# 3. Upload-only policy (for write-heavy workflows)
upload_only_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=True),
    download_policy=DownloadPolicy(auto_download=False)
)

# 4. Download-only policy (for read-heavy workflows)
download_only_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=False),
    download_policy=DownloadPolicy(auto_download=True)
)
```


#### Compression Mode Configuration

AgentBay SDK provides file compression capabilities to optimize storage space and transfer performance during context synchronization. This is particularly beneficial when working with large text files, source code, or other compressible content.

**Upload Mode Options:**

| Mode | Description | Best For | Compression |
|------|-------------|----------|-------------|
| `UploadMode.FILE` | Default mode - files uploaded as-is | Small files | None |
| `UploadMode.ARCHIVE` | Files compressed before upload | Large text files, source code, logs | Yes |

**When to Use Archive Mode:**

1. **Large text-based files**: Source code, configuration files, logs, documentation
2. **Multiple small files**: Many small files benefit from compression and bundling
3. **Bandwidth optimization**: Slow network connections or limited bandwidth
4. **Storage cost reduction**: Minimize OSS storage usage for compressible content

**Basic Usage:**

```python
from agentbay import AgentBay, CreateSessionParams
from agentbay import ContextSync, SyncPolicy, UploadPolicy, UploadMode

# Initialize AgentBay client
agent_bay = AgentBay(api_key="your-api-key")

# Create context
context_result = agent_bay.context.get("my-project", create=True)
context = context_result.context

# Configure sync policy with Archive upload mode
upload_policy = UploadPolicy(upload_mode=UploadMode.ARCHIVE)  # Enable compression
sync_policy = SyncPolicy(upload_policy=upload_policy)

# Create context sync with compression enabled
context_sync = ContextSync(
    context_id=context.id,
    path="/tmp/data",
    policy=sync_policy
)

# Create session with Archive mode
session_params = CreateSessionParams(
    labels={
        "example": "archive-mode-demo",
        "type": "compression-test",
    },
    context_syncs=[context_sync]
)

session_result = agent_bay.create(session_params)
session = session_result.session

# Files written to /tmp/data will be compressed before upload
session.file_system.write_file("/tmp/data/large-file.txt", large_content, mode="overwrite")
session.file_system.write_file("/tmp/data/config.json", config_data, mode="overwrite")

# Perform context sync before getting info (synchronous operation)
sync_result = session.context.sync()
if sync_result.success:
    print("Context sync successful!")
    
    # Get context status information after sync
    info_result = session.context.info()
    if info_result.success:
        print(f"Context status data count: {len(info_result.context_status_data)}")
        for status in info_result.context_status_data:
            print(f"Context ID: {status.context_id}, Path: {status.path}, Status: {status.status}")

    # List files in context sync directory
    list_result = agent_bay.context.list_files(context.id, "/tmp/data", max_results=10)
    if list_result.success:
        print(f"Total files found: {len(list_result.entries)}")
        for entry in list_result.entries:
            print(f"File: {entry.file_name}, Size: {entry.size} bytes, Type: {entry.file_type}")

# Clean up with sync to ensure compressed upload completes
agent_bay.delete(session, sync_context=True)
```

#### Hybrid Storage with Archive Exclude Paths

When using Archive mode, you may have files that need to be individually accessible via Presigned URLs (e.g., for direct download or preview). The `archiveExcludePaths` option lets you exclude specific paths from the archive — these files are uploaded individually in FILE mode while the rest are bundled into an archive.

**Use cases:**
- Configuration files that agents need to read directly
- Output files that users need to download via URL
- Log files that monitoring systems need to access in real-time

**Performance impact:** Minimal — excluded files are uploaded in parallel with the archive, and the archive is smaller. The upload/download speedup of Archive mode is preserved for the bulk of files.

```python
from agentbay import UploadPolicy, UploadMode, SyncPolicy, ContextSync

# Configure Archive mode with specific paths excluded from archiving
upload_policy = UploadPolicy(
    upload_mode=UploadMode.ARCHIVE,
    archive_exclude_paths=["output/", "config.json", "logs/"]
)
sync_policy = SyncPolicy(upload_policy=upload_policy)

context_sync = ContextSync(
    context_id=context.id,
    path="/tmp/workspace",
    policy=sync_policy
)
```

**Path matching rules:**
- Each entry is a **relative path prefix** (relative to the sync path)
- No wildcards — use exact directory or file prefixes
- Directory prefixes should end with `/` (e.g., `output/`)
- Files matching any prefix are uploaded as individual files in FILE mode
- All other files are compressed into the archive

####  Data Lifecycle Management (RecyclePolicy)

`RecyclePolicy` controls how long your context data is retained in the cloud before automatic cleanup. This is useful for managing storage costs and automatically removing temporary data.

**Key Concepts:**
- **Default Behavior**: Data is kept **FOREVER** (permanently) if no RecyclePolicy is specified
- **Automatic Cleanup**: Data is automatically deleted after the specified duration
- **Path-Specific**: Apply different lifecycles to different directories
- **No Wildcards**: Paths must be exact - wildcard patterns are not supported for safety

**Available Lifecycle Options:**

| Lifecycle | Duration | Use Case |
|-----------|----------|----------|
| `LIFECYCLE_1DAY` | 1 day | Temporary cache, test data |
| `LIFECYCLE_3DAYS` | 3 days | Short-term work files |
| `LIFECYCLE_5DAYS` | 5 days | Weekly data |
| `LIFECYCLE_10DAYS` | 10 days | Sprint data |
| `LIFECYCLE_15DAYS` | 15 days | Bi-weekly data |
| `LIFECYCLE_30DAYS` | 30 days | Monthly archives |
| `LIFECYCLE_90DAYS` | 90 days | Quarterly data |
| `LIFECYCLE_180DAYS` | 180 days | Semi-annual data |
| `LIFECYCLE_360DAYS` | 360 days | Annual archives |
| `LIFECYCLE_FOREVER` | Permanent | Important data (default) |

**Basic Usage:**

```python
from agentbay import RecyclePolicy, Lifecycle, SyncPolicy, ContextSync

# Example 1: Keep data for 1 day
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=[""]  # "" means apply to all paths
)

sync_policy = SyncPolicy(recycle_policy=recycle_policy)
context_sync = ContextSync.new(context.id, "/tmp/cache", sync_policy)

# This creates a RecyclePolicy with:
# - lifecycle: Lifecycle_1Day
# - paths: ['']
```

**Path-Specific Cleanup:**

```python
# Example 2: Different lifespans for different directories
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_3DAYS,
    paths=["/tmp/cache", "/tmp/logs"]  # Only these paths
)

# Important: Use exact paths, NOT wildcards like "/tmp/*"
sync_policy = SyncPolicy(recycle_policy=recycle_policy)

# This applies the 3-day lifecycle only to /tmp/cache and /tmp/logs
```

**Important Restrictions:**

```python
# ❌ WRONG: Wildcard patterns are NOT supported
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp/*", "/var/*.log"]  # Will raise ValueError
)
# Raises: ValueError: Wildcard patterns are not supported in recycle policy paths.
#         Got: /tmp/*. Please use exact directory paths instead.

# ✅ CORRECT: Use exact directory paths
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp/cache", "/var/logs"]  # Exact paths only
)
# Successfully creates RecyclePolicy with exact paths
```

**When to Use RecyclePolicy:**

1. **Temporary Data**: Set short lifecycles (1-3 days) for cache, temp files, or test data
2. **Project Data**: Use medium lifecycles (30-90 days) for project files
3. **Archives**: Use long lifecycles (180-360 days) for important archives
4. **Permanent Data**: Use `LIFECYCLE_FOREVER` (default) for critical data

**Complete Example:**

```python
from agentbay import AgentBay, CreateSessionParams
from agentbay import (
    ContextSync, SyncPolicy, RecyclePolicy, Lifecycle,
    UploadPolicy, DownloadPolicy, BWList, WhiteList
)

# Create context
context = agent_bay.context.get("my-project", create=True).context

# Create RecyclePolicy with 5 days lifecycle
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_5DAYS,  # Note: No LIFECYCLE_7DAYS, use 5 or 10
    paths=[""]  # Apply to all paths
)

# Create comprehensive SyncPolicy
sync_policy = SyncPolicy(
    upload_policy=UploadPolicy.default(),
    download_policy=DownloadPolicy.default(),
    recycle_policy=recycle_policy  # Add lifecycle management
)

# Create session with lifecycle-managed context
context_sync = ContextSync.new(context.id, "/tmp/data", sync_policy)
session = agent_bay.create(CreateSessionParams(context_syncs=[context_sync])).session

# The session is now configured with RecyclePolicy
# Data uploaded to this context will be automatically deleted after 5 days
```

> **Note**: RecyclePolicy applies from the time data is uploaded to the cloud. The timer starts after the session ends and data is synchronized, not when files are created in the session.

#### Selective Directory Sync

Use `bw_list` (blacklist/whitelist) to control which subdirectories within the context mount point are synced:

```python
from agentbay import BWList, WhiteList

# Example: Sync only /src and /config, exclude /src/node_modules
policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=True),
    download_policy=DownloadPolicy(auto_download=True),
    bw_list=BWList(
        white_lists=[
            WhiteList(
                path="/src",
                exclude_paths=["/node_modules"]
            ),
        ]
    )
)

# Mount point: use any directory with write permissions
# In linux_latest image, /home/wuying is recommended
# Whitelisted paths are relative to mount point:
# - "/src" → /home/wuying/src  
# - "/config" → /home/wuying/config
# - "/node_modules" in exclude → /home/wuying/src/node_modules
context_sync = ContextSync.new(context.id, "/home/wuying", policy)
```

**Mount Point Selection:**
- Use any directory where you have write permissions
- In `linux_latest` image: `/home/wuying`, `/tmp`, `/var/tmp` are available
- System directories like `/workspace`, `/opt`, `/usr` typically require elevated privileges

**Path Specifications:**
- `path` in WhiteList is **relative to the context mount point**
- `exclude_paths` are **relative to the whitelist path**
- Example: If mounted at `/home/wuying`, then `path="/src"` refers to `/home/wuying/src`
- By default, wildcard patterns (e.g., `*.json`, `/data/*`) are **not** supported

#### Regex Support in WhiteList (is_path_regex / is_exclude_regex)

`WhiteList` supports two optional boolean flags that switch `path` and `exclude_paths` from exact-match mode to **regex pattern** mode:

| Field | Default | Behaviour when `False` | Behaviour when `True` |
|-------|---------|------------------------|-----------------------|
| `is_path_regex` | `False` | `path` must be an exact directory path; wildcards raise an error | `path` is interpreted as a regex pattern (e.g. `/home/wuying/.*`) |
| `is_exclude_regex` | `False` | each entry in `exclude_paths` must be an exact path; wildcards raise an error | each entry in `exclude_paths` is interpreted as a regex pattern |

**Example – combining regex path with regex exclude patterns:**

```python
from agentbay import BWList, WhiteList, SyncPolicy, UploadPolicy, DownloadPolicy
from agentbay import RecyclePolicy, ExtractPolicy, DeletePolicy

sync_policy = SyncPolicy(
    upload_policy=UploadPolicy.default(),
    download_policy=DownloadPolicy.default(),
    delete_policy=DeletePolicy.default(),
    extract_policy=ExtractPolicy.default(),
    recycle_policy=RecyclePolicy.default(),
    bw_list=BWList(white_lists=[
        WhiteList(
            path=r"project-.*",      # matches any sub-dir starting with "project-" (e.g. project-alpha, project-beta)
            is_path_regex=True,       # path is a regex pattern
            exclude_paths=[
                r"record.*",          # exclude sub-dirs matching "record.*" under each matched project dir
                r"downloads.*",          # exclude sub-dirs matching "downloads.*" under each matched project dir
            ],
            is_exclude_regex=True,    # treat exclude_paths entries as regex patterns
        )
    ]),
)

# Mount the parent directory so the whitelist path resolves correctly:
# is_path_regex=True + path=r"project-.*" → only sub-dirs matching "project-.*" are included
# is_exclude_regex=True + exclude_paths=["record.*","下载.*"] → sub-dirs matching
#   these patterns under each matched project dir are excluded
context_sync = ContextSync.new(context.id, "/home/wuying", sync_policy)
```

> **Note:** `exclude_paths` entries are matched **relative to each white-listed directory**, not as absolute paths.  
> So `"record.*"` excludes any sub-dir starting with `record` inside the matched project dirs, and `"downloads.*"` excludes any sub-dir starting with `downloads`.

**When to use each mode:**

| Use case | Recommended settings |
|----------|---------------------|
| Sync a specific known directory | `is_path_regex=False` (default), exact `path` |
| Sync directories matching a naming pattern | `is_path_regex=True`, regex `path` |
| Exclude specific known sub-directories | `is_exclude_regex=False` (default), exact `exclude_paths` |
| Exclude sub-directories matching a pattern | `is_exclude_regex=True`, regex `exclude_paths` |

**Validation rules:**
- When `is_path_regex=False` (default): wildcard characters (`*`, `?`, `[`, `]`) in `path` raise a `ValueError`
- When `is_exclude_regex=False` (default): wildcard characters in any `exclude_paths` entry raise a `ValueError`
- When the corresponding flag is `True`: the value is passed as-is to the server as a regex pattern — no client-side wildcard validation is performed



### Manual Synchronization

When using manual sync policies, you need to explicitly call `session.context.sync()` to trigger data synchronization:

```python
from agentbay import SyncPolicy, UploadPolicy, DownloadPolicy

agent_bay = AgentBay()
# Create session with manual sync policy
manual_policy = SyncPolicy(
    upload_policy=UploadPolicy(auto_upload=False),
    download_policy=DownloadPolicy(auto_download=False)
)
context = agent_bay.context.get("my-project", create=True).context

context_sync = ContextSync.new(context.id, "/tmp/data", manual_policy)
session_result = agent_bay.create(CreateSessionParams(context_syncs=[context_sync]))

if session_result.success:
    session = session_result.session

    # Write some data
    session.file_system.write_file("/tmp/data/temp.txt", "Temporary data")

    # Manually trigger sync to save data (synchronous call - returns when sync is complete)
    sync_result = session.context.sync()
    if sync_result.success:
        print("Data synchronized successfully")
    else:
        print(f"Sync failed: {sync_result.success}")

    # Data is now persisted even if session ends
else:
    print(f"Failed to create session: {session_result.error_message}")
```


### Bidirectional Sync

By default, `session.context.sync()` triggers file **upload** (mode="upload"). You can explicitly specify the sync direction:

```python
# Default behavior - upload local changes to OSS (mode="upload" is default)
upload_result = session.context.sync()  # Same as sync(mode="upload")
if upload_result.success:
    print("Local changes uploaded to context")
else:
    print(f"Upload failed: {upload_result.error_message}")

# Explicitly download latest data from OSS to session
download_result = session.context.sync(mode="download")
if download_result.success:
    print("Latest data downloaded from context")
else:
    print(f"Download failed: {download_result.error_message}")

# Explicitly upload local changes to OSS
upload_result = session.context.sync(mode="upload")
if upload_result.success:
    print("Local changes uploaded to context")
else:
    print(f"Upload failed: {upload_result.error_message}")
```

<a id="context-mount"></a>
## 📌 Context Mount (Direct-Mount Persistence) [Beta]

> **Image requirement:** Context Mount requires `image_id="aio-ubuntu-2404"`. Other images do not provide a real OSS-backed mount — writes made on a non-supported image are not persisted to the shared context store and are invisible to other sessions, even when the same context ID and mount path are used.

### What is Context Mount?

**Context Mount** provides an alternative persistence model to Context Sync. Instead of downloading and uploading files at session start/end, Context Mount presents the context's storage as a **live mounted filesystem** — writes are persisted immediately, and reads always reflect the latest state.

**Key difference from Context Sync:**

| Aspect | Context Sync | Context Mount |
|--------|-------------|---------------|
| **Persistence model** | Batch: download on start, upload on end | Write-through: changes persist immediately |
| **Manual sync needed?** | Yes (`sync()`, `delete(sync_context=True)`) | No — all writes are automatically persisted |
| **Data availability** | After sync completes | Immediately after write |
| **Best for** | Large batch operations, offline-first workflows | Real-time persistence, shared state across sessions |
| **Configuration** | `SyncPolicy` (upload/download/recycle) | `AccessMode` + `Strategy` |

### Using Context Mount at Session Creation

The simplest way to use Context Mount is to specify it when creating a session:

```python
from agentbay import AgentBay, BetaContextMount, CreateSessionParams

agent_bay = AgentBay()

# Create or get a context
context = agent_bay.context.get("my-mount-demo", create=True).context

# Create a mount configuration
context_mount = BetaContextMount.new(context.id, "/tmp/mounted")

# Create a session with the mount — image_id is required
params = CreateSessionParams(
    image_id="aio-ubuntu-2404",
    beta_context_mounts=[context_mount],
)
session = agent_bay.create(params).session

# Write data — it is persisted immediately, no sync needed
session.file_system.write_file("/tmp/mounted/hello.txt", "Hello from Context Mount!")

# Read it back
content = session.file_system.read_file("/tmp/mounted/hello.txt")
print(content.content)  # "Hello from Context Mount!"

# No need for sync_context=True — data is already persisted
agent_bay.delete(session)
```

### Dynamic Mounting (Runtime Bind)

You can also mount a context to a running session using `bind()`:

```python
from agentbay import AgentBay, BetaContextMount, CreateSessionParams

agent_bay = AgentBay()

# Create a session without any initial mounts — image_id is required for mount support
session = agent_bay.create(CreateSessionParams(image_id="aio-ubuntu-2404")).session

# Later, dynamically mount a context
context = agent_bay.context.get("runtime-mount", create=True).context
context_mount = BetaContextMount.new(context.id, "/tmp/dynamic-mount")

bind_result = session.context.bind(context_mount)
if bind_result.success:
    print("Context mounted successfully!")
    session.file_system.write_file("/tmp/dynamic-mount/data.txt", "Dynamic mount works!")

agent_bay.delete(session)
```

### Cross-Session Data Persistence

Because Context Mount persists data immediately, it is straightforward to share data across sessions:

```python
from agentbay import AgentBay, BetaContextMount, CreateSessionParams

agent_bay = AgentBay()
context = agent_bay.context.get("cross-session-mount", create=True).context
mount = BetaContextMount.new(context.id, "/tmp/shared")

def mount_params():
    return CreateSessionParams(image_id="aio-ubuntu-2404", beta_context_mounts=[mount])

# Session A: write data
session_a = agent_bay.create(mount_params()).session
session_a.file_system.write_file("/tmp/shared/config.json", '{"version": "2.0"}')
agent_bay.delete(session_a)  # No sync needed

# Session B: read data written by Session A
session_b = agent_bay.create(mount_params()).session
content = session_b.file_system.read_file("/tmp/shared/config.json")
print(content.content)  # '{"version": "2.0"}'
agent_bay.delete(session_b)
```

### Multi-Session Real-Time Sharing

When the same context is mounted in multiple active sessions simultaneously, changes made in one session are **immediately visible** in the other sessions — no sync or refresh needed:

```python
from agentbay import AgentBay, BetaContextMount, CreateSessionParams

agent_bay = AgentBay()
context = agent_bay.context.get("shared-workspace", create=True).context
mount = BetaContextMount.new(context.id, "/tmp/shared")

def mount_params():
    return CreateSessionParams(image_id="aio-ubuntu-2404", beta_context_mounts=[mount])

# Two sessions mount the same context
session_1 = agent_bay.create(mount_params()).session
session_2 = agent_bay.create(mount_params()).session

# Session 1 writes a file
session_1.file_system.write_file("/tmp/shared/status.txt", "ready")

# Session 2 can read it immediately — no sync needed
content = session_2.file_system.read_file("/tmp/shared/status.txt")
print(content.content)  # "ready"

agent_bay.delete(session_1)
agent_bay.delete(session_2)
```

### Access Modes and Strategies

Context Mount supports two configuration dimensions:

**Access Mode** controls read/write permissions:

| Mode | Description |
|------|-------------|
| `READ_WRITE` (default) | Full read and write access |
| `READ_ONLY` | Read-only access — writes will be rejected |

**Strategy** controls the underlying mount technology and POSIX compatibility:

| Strategy | Description | Compatibility | Best For |
|----------|-------------|---------------|----------|
| `STANDARD` (default) | High POSIX compatibility via ossfs 1.0 | Supports random writes; does **not** support file locks | General file storage, project workspaces, configuration persistence |
| `PERFORMANCE` | High-throughput via ossfs 2.0 | Does **not** support file locks, symlinks, random writes, or permission changes | Sequential I/O, large datasets, AI training/inference data |

**Important compatibility notes:**
- Neither strategy supports file locks (`flock`/`fcntl`). Applications that rely on lock files (Git, Chrome, database engines) **will not work** on a mounted path.
- `PERFORMANCE` does not support random writes (`lseek` + `write`). It is optimized for sequential read, sequential append, and random read patterns.
- If your workflow requires file locks or random writes, use **Context Sync** (which operates on local disk) instead.

```python
from agentbay import BetaContextMount, BetaContextMountAccessMode, BetaContextMountStrategy

# Read-only mount with performance strategy
mount = BetaContextMount.new(context.id, "/tmp/readonly-data")
mount.with_access_mode(BetaContextMountAccessMode.READ_ONLY)
mount.with_strategy(BetaContextMountStrategy.PERFORMANCE)
```

### Partial Mount with `source_path`

By default, a `BetaContextMount` mounts the **entire** context to the target path. Use `source_path` to mount only a subdirectory of the context. The selected subdirectory's contents are projected to the mount root.

(`image_id="aio-ubuntu-2404"` is already required by Context Mount itself — see the section header.)

**Mount a subdirectory:**

```python
from agentbay import AgentBay, BetaContextMount, CreateSessionParams

agent_bay = AgentBay()
context = agent_bay.context.get("dataset-collection", create=True).context

# Mount only the /datasets/train subdirectory to /mnt/train
mount = BetaContextMount.new(
    context_id=context.id,
    path="/mnt/train",
    source_path="/datasets/train",
)

params = CreateSessionParams(image_id="aio-ubuntu-2404", beta_context_mounts=[mount])
session = agent_bay.create(params).session
# /mnt/train/ now contains the contents of <context>/datasets/train/ projected to the root
# e.g., a file at <context>/datasets/train/foo.csv is visible at /mnt/train/foo.csv
```

**Mount multiple subpaths (use multiple `BetaContextMount` instances):**

```python
params = CreateSessionParams(
    image_id="aio-ubuntu-2404",
    beta_context_mounts=[
        BetaContextMount.new(context.id, "/mnt/train", source_path="/datasets/train"),
        BetaContextMount.new(context.id, "/mnt/val", source_path="/datasets/val"),
    ],
)
```

**Builder-style alternative:**

```python
mount = (
    BetaContextMount.new(context.id, "/mnt/train")
    .with_source_path("/datasets/train")
)
```

**Notes:**

- Default value is empty string `""`, which mounts the entire context (preserves existing behavior).
- The mount path appears as a symlink to the CSI mount root (e.g., `/run/csi/mount-root/oss/<hash>`). When listing files, use `find -L` to follow symlinks.
- The SDK does not validate `source_path` syntax; the backend validates path existence and rejects unsafe paths (`..`, wildcards, etc.).
- Each mount entry is independent — you can give each subpath its own `path`, `access_mode`, and `strategy`.

### Limitations and Restrictions

| Restriction | Description |
|-------------|-------------|
| **Mount path must be empty** | If the target path already contains files, the mount will fail. Use an empty or non-existent directory. |
| **No duplicate mount paths** | You cannot mount two different contexts to the same path in one session. |
| **Max mount count** | Each session supports up to **3** mounted contexts. Exceeding this limit may degrade performance. |
| **No file locks** | Both strategies use OSS-backed FUSE; file locking is not supported. |
| **No unmount** | Dynamic unmounting during a session is not currently supported; mounted contexts remain until the session ends. |

**Applications known to fail on mounted paths:**

| Application | Reason |
|-------------|--------|
| Chrome / browser user data | Creates file locks and symlinks on startup |
| Git operations | Relies on lock files (`.git/index.lock`) |
| VS Code / IDE projects | Build tooling uses file locks |
| npm / yarn install | Uses symlinks for `node_modules` |

For these use cases, use **Context Sync** which operates on local disk with full POSIX semantics.

### Choosing Between Context Sync and Context Mount

#### Quick Decision Guide

- **Need file locks, symlinks, or random writes?** → Use **Context Sync** (local disk, full POSIX)
- **Need real-time persistence or multi-session sharing?** → Use **Context Mount (Standard)**
- **High-throughput sequential I/O on large datasets?** → Use **Context Mount (Performance)**

#### Three-Mode Comparison

|  | Context Sync | Context Mount (Standard) | Context Mount (Performance) |
|--|-------------|--------------------------|------------------------------|
| **How it works** | Download on start, upload on end | Live mounted filesystem | Live mounted filesystem (high-throughput) |
| **Persistence** | Batch — manual `sync()` or `delete(sync_context=True)` | Write-through — immediate | Write-through — immediate |
| **File lock (`flock`)** | ✅ Supported | ❌ Not supported | ❌ Not supported |
| **Symlinks** | ✅ Supported | ✅ Supported | ❌ Not supported |
| **Random writes (`lseek`)** | ✅ Supported | ✅ Supported | ❌ Not supported |
| **Permission changes** | ✅ Supported | ✅ Supported | ❌ Not supported |
| **Compression (Archive mode)** | ✅ Supported | ❌ N/A | ❌ N/A |
| **Selective sync (whitelist)** | ✅ Supported | ❌ N/A | ❌ N/A |
| **Recycle policy (auto-delete)** | ✅ Supported | ❌ N/A | ❌ N/A |
| **Multi-session real-time sharing** | ❌ Requires re-sync | ✅ Immediate visibility | ✅ Immediate visibility |
| **Risk of data loss on crash** | ⚠️ Unsaved changes lost | ✅ No risk | ✅ No risk |

#### Typical Use Cases

| Use Case | Recommended Mode |
|----------|-----------------|
| Browser cookie / user data persistence | **Context Sync** — Chrome requires file locks and symlinks |
| Git repository workspace | **Context Sync** — Git relies on lock files |
| IDE / build toolchain projects | **Context Sync** — compilers and package managers use file locks |
| Agent working directory (general files) | **Context Mount (Standard)** — good compatibility, real-time persistence |
| Shared read-only dataset across sessions | **Context Mount (Standard)** with `READ_ONLY` mode |
| AI training data / large sequential reads | **Context Mount (Performance)** — highest throughput |
| npm / pip package cache | **Context Sync** — package managers use symlinks and lock files |

> **Tip:** You can use both Context Sync and Context Mount in the same session on different paths. For example, mount a shared dataset at `/tmp/data` while syncing a Git workspace at `/home/wuying/project`.

<a id="troubleshooting"></a>
## 🔧 Troubleshooting

### Issue 1: Permission Denied When Creating Files

**Error Message:**
```
Permission denied
Failed to create directory: /workspace, error: Permission denied
```

**Cause:** Mount point directory lacks write permissions for the current user.

**Solution:**
```python
# ❌ Wrong: Using directory without write permission
context_sync = ContextSync.new(context.id, "/workspace", policy)
context_sync = ContextSync.new(context.id, "/opt/myapp", policy)

# ✅ Correct: Use directory with write permission
context_sync = ContextSync.new(context.id, "/home/wuying", policy)
context_sync = ContextSync.new(context.id, "/tmp/myapp", policy)
```

**Available directories in `linux_latest` image:** `/home/wuying`, `/tmp`, `/var/tmp`

### Issue 2: Files Not Persisted (WhiteList Path Error)

**Symptom:** Files created in session are not found in the next session, even though sync completed.

**Cause:** WhiteList paths are treated as absolute instead of relative to mount point.

**Example of the error:**
```python
# ❌ Wrong: This looks for /home/wuying/home/wuying/src (doesn't exist)
policy = SyncPolicy(
    bw_list=BWList(
        white_lists=[WhiteList(path="/home/wuying/src")]
    )
)
context_sync = ContextSync.new(context.id, "/home/wuying", policy)
```

**Solution:**
```python
# ✅ Correct: Paths are relative to mount point
policy = SyncPolicy(
    bw_list=BWList(
        white_lists=[WhiteList(path="/src")]  # → /home/wuying/src
    )
)
context_sync = ContextSync.new(context.id, "/home/wuying", policy)
```

### Issue 3: Wildcard Patterns Not Supported

**Symptom:** Files are not persisted even though sync completes successfully. No error is reported.

**Cause:** Using wildcard patterns (`*`, `**`) in WhiteList paths or exclude_paths.

**Example of the error:**
```python
# ❌ Wrong: Wildcards silently fail
policy = SyncPolicy(
    bw_list=BWList(
        white_lists=[
            WhiteList(path="*.json"),           # No files synced
            WhiteList(path="/data/*"),          # No files synced
            WhiteList(path="/logs/**/*.txt"),   # No files synced
            WhiteList(path="/src", exclude_paths=["*.log"])  # No files synced
        ]
    )
)
```

**Solution:**
```python
# ✅ Correct: Use exact directory paths
policy = SyncPolicy(
    bw_list=BWList(
        white_lists=[
            WhiteList(path="/data"),  # Syncs all files in /data
            WhiteList(path="/src", exclude_paths=["/temp"])  # Syncs /src except /src/temp
        ]
    )
)
```

### Issue 4: Data Loss After Session Deletion

**Symptom:** Files written in session are not available in the next session.

**Cause:** Session deleted before sync upload completes.

**Solution:**
```python
# ❌ Wrong: May delete before upload finishes
session.file_system.write_file("/home/wuying/data.txt", "content")
agent_bay.delete(session)

# ✅ Correct: Wait for sync to complete
session.file_system.write_file("/home/wuying/data.txt", "content")
agent_bay.delete(session, sync_context=True)
```

### Issue 5: Understanding RecyclePolicy and Data Retention

**Question:** When will my context data be deleted?

**Answer:**
- **Default**: Data is kept **FOREVER** unless you specify a RecyclePolicy
- **With RecyclePolicy**: Data is automatically deleted after the specified period from upload time
- **Timer Start**: The lifecycle countdown begins when data is uploaded to the cloud (after session ends and sync completes)

**Example:**
```python
# Scenario: Set 1 day lifecycle
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=[""]
)

# Timeline:
# Day 0, 10:00 AM - Session created, files written
# Day 0, 11:00 AM - Session deleted, sync uploads data to cloud
# Day 0, 11:00 AM - Lifecycle timer starts
# Day 1, 11:00 AM - Data automatically deleted (24 hours after upload)
```

**Common Mistakes:**

```python
# ❌ Wrong: Using wildcards in paths
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp/*", "/var/*.log"]  # ValueError: wildcards not supported
)

# ✅ Correct: Use exact directory paths
recycle_policy = RecyclePolicy(
    lifecycle=Lifecycle.LIFECYCLE_1DAY,
    paths=["/tmp/cache", "/var/logs"]  # Exact paths only
)
```

**Choosing the Right Lifecycle:**
- **Temporary cache/test data**: `LIFECYCLE_1DAY` or `LIFECYCLE_3DAYS`
- **Development work**: `LIFECYCLE_5DAYS` to `LIFECYCLE_15DAYS`
- **Project archives**: `LIFECYCLE_30DAYS` to `LIFECYCLE_90DAYS`
- **Important data**: `LIFECYCLE_FOREVER` (default)

### Verifying Sync Status

```python
context_info = session.context.info()

if context_info.context_status_data:
    for status in context_info.context_status_data:
        print(f"Context: {status.context_id}")
        print(f"Path: {status.path}")
        print(f"Status: {status.status}")
        if status.error_message:
            print(f"Error: {status.error_message}")
else:
    print("No sync tasks found")
```



## 📚 Related Guides

- [Session Management](session-management.md) - Session lifecycle and configuration
- [File Operations](file-operations.md) - File handling and management
- [OSS Integration](../advanced/oss-integration.md) - Object storage service integration
- [Context Sync Use Case](../use-cases/context-sync-use-case.md) - Context Best Practices

## 🆘 Getting Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation Home](../README.md)
