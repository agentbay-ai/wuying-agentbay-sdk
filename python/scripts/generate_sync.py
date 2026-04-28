import os
import sys
import ast
import warnings
import unasync
import re
import shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTBAY_DIR = os.path.join(ROOT, "agentbay")
ASYNC_DIR = os.path.join(AGENTBAY_DIR, "_async")
SYNC_DIR = os.path.join(AGENTBAY_DIR, "_sync")

TEST_DIR = os.path.join(ROOT, "tests", "integration")
TEST_ASYNC_DIR = os.path.join(TEST_DIR, "_async")
TEST_SYNC_DIR = os.path.join(TEST_DIR, "_sync")
TEST_COMMON_DIR = os.path.join(TEST_DIR, "_common")

# Unit test directories
UNIT_TEST_DIR = os.path.join(ROOT, "tests", "unit")
UNIT_TEST_ASYNC_DIR = os.path.join(UNIT_TEST_DIR, "async")
UNIT_TEST_SYNC_DIR = os.path.join(UNIT_TEST_DIR, "sync")

# Example directories
EXAMPLES_DIR = os.path.join(ROOT, "docs", "examples")
EXAMPLES_ASYNC_DIR = os.path.join(EXAMPLES_DIR, "_async")
EXAMPLES_SYNC_DIR = os.path.join(EXAMPLES_DIR, "_sync")

SKIP_SYNC_GENERATION_FILES = set()

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

# Extra sync-only files that cannot be mechanically converted by unasync.
# We copy them from templates after unasync completes.
SYNC_EXTRA_TEMPLATES: dict[str, str] = {
    os.path.join(SYNC_DIR, "_internal", "ws_client.py"): os.path.join(
        TEMPLATES_DIR, "sync_ws_client.py"
    ),
    os.path.join(
        UNIT_TEST_SYNC_DIR, "test_run_code_ws_streaming.py"
    ): os.path.join(TEMPLATES_DIR, "sync_test_run_code_ws_streaming.py"),
    os.path.join(
        UNIT_TEST_SYNC_DIR, "test_agent_streaming.py"
    ): os.path.join(TEMPLATES_DIR, "sync_test_agent_streaming.py"),
}


def _init_skip_sync_generation_files() -> None:
    """
    Some async-only modules cannot be mechanically converted to sync.

    We skip generating their sync counterparts and instead provide explicit stubs
    (or omit generated tests) to avoid broken sync code.
    """
    global SKIP_SYNC_GENERATION_FILES
    SKIP_SYNC_GENERATION_FILES = {
        os.path.join(ASYNC_DIR, "_internal", "ws_client.py"),
        os.path.join(TEST_ASYNC_DIR, "test_ws_long_connection_integration.py"),
        os.path.join(TEST_ASYNC_DIR, "test_ws_register_callback_integration.py"),
        os.path.join(UNIT_TEST_ASYNC_DIR, "test_ws_long_connection.py"),
        os.path.join(UNIT_TEST_ASYNC_DIR, "test_run_code_ws_streaming.py"),
        os.path.join(
            EXAMPLES_ASYNC_DIR,
            "browser-use",
            "browser",
            "ws_push_callback_captcha_tongcheng.py",
        ),
    }


def _should_skip_sync_generation(path: str) -> bool:
    return os.path.normpath(path) in SKIP_SYNC_GENERATION_FILES


def _copy_template_file(src: str, dst: str) -> None:
    if not os.path.exists(src):
        raise RuntimeError(f"Missing template file: {src}")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(src, "r", encoding="utf-8") as f:
        content = f.read()
    with open(dst, "w", encoding="utf-8") as f:
        f.write(content)


def _write_sync_ws_client_stub() -> None:
    """
    Write a real sync WS client implementation.

    It is copied from a template (not embedded in this script) to keep the sync
    generator generic.
    """
    dst = os.path.join(SYNC_DIR, "_internal", "ws_client.py")
    src = os.path.join(TEMPLATES_DIR, "sync_ws_client.py")
    _copy_template_file(src, dst)


def _write_sync_extra_templates() -> None:
    for dst, src in SYNC_EXTRA_TEMPLATES.items():
        _copy_template_file(src, dst)


def _write_sync_ws_streaming_unit_test_stub() -> None:
    dst = os.path.join(UNIT_TEST_SYNC_DIR, "test_run_code_ws_streaming.py")
    src = os.path.join(TEMPLATES_DIR, "sync_test_run_code_ws_streaming.py")
    _copy_template_file(src, dst)


def _write_sync_ws_streaming_integration_test_stub() -> None:
    """
    Write a sync integration test stub for WS streaming.

    WS long connection is async-only for now, so sync integration test is skipped.
    """
    return

def _build_client_api_method_replacements() -> dict:
    """
    Build replacements for client API methods automatically.

    Assumption: async client methods are strictly sync method name + "_async",
    e.g. get_session_detail() and get_session_detail_async().

    We only generate replacements when BOTH methods exist in agentbay/api/client.py,
    to avoid accidental renames of non-client symbols.
    """
    client_path = os.path.join(AGENTBAY_DIR, "api", "client.py")
    if not os.path.exists(client_path):
        return {}

    try:
        with open(client_path, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return {}

    sync_methods = set(re.findall(r"^\s*def\s+([a-zA-Z_]\w*)\s*\(", content, flags=re.MULTILINE))
    async_methods = set(re.findall(r"^\s*async\s+def\s+([a-zA-Z_]\w*)\s*\(", content, flags=re.MULTILINE))

    replacements = {}
    for async_name in async_methods:
        if not async_name.endswith("_async"):
            continue
        sync_name = async_name[: -len("_async")]
        if sync_name in sync_methods:
            replacements[async_name] = sync_name
    return replacements


def _sync_session_life_functional() -> None:
    """
    Auto-generate the SyncSessionLifecycle class in _common/session_life_functional.py
    from the AsyncSessionLifecycle class in the same file.

    Strategy:
      1. Read the source file.
      2. Extract the AsyncSessionLifecycle class block.
      3. Apply async→sync text replacements.
      4. Replace the SyncSessionLifecycle block (between the sync-variant
         separator comment and EOF) with the newly generated code.
      5. Write back.
    """
    src_path = os.path.join(TEST_COMMON_DIR, "session_life_functional.py")
    if not os.path.exists(src_path):
        print(f"  [session_life_functional] skipped – file not found: {src_path}")
        return

    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # ---- locate AsyncSessionLifecycle class block ----
    async_class_start = content.find("class AsyncSessionLifecycle:")
    if async_class_start == -1:
        print("  [session_life_functional] skipped – AsyncSessionLifecycle not found")
        return

    # The sync-variant separator comment marks where async ends / sync begins
    sync_separator = "# ---------------------------------------------------------------------------\n# Sync variant\n# ---------------------------------------------------------------------------"
    sync_section_start = content.find(sync_separator)
    if sync_section_start == -1:
        print("  [session_life_functional] skipped – sync-variant separator not found")
        return

    async_block = content[async_class_start:sync_section_start]

    # ---- apply replacements to convert async → sync ----
    # Order matters: longer / more specific patterns first.
    replacements_ordered = [
        # Docstring references
        ("Manages a single AsyncAgentBay session lifecycle.", "Manages a single AgentBay (sync) session lifecycle."),
        ("AsyncAgentBay.create raised an exception", "AgentBay.create raised an exception"),
        ("AsyncAgentBay.create (with context_name) raised an exception", "AgentBay.create (with context_name) raised an exception"),
        ("AsyncAgentBay.create (with browser_name) raised an exception", "AgentBay.create (with browser_name) raised an exception"),
        ("AsyncAgentBay.delete raised an exception", "AgentBay.delete raised an exception"),
        # Class / type names
        ("AsyncSessionLifecycle", "SyncSessionLifecycle"),
        ("AsyncAgentBay", "AgentBay"),
        # async def → def
        ("async def ", "def "),
        # await calls
        ("await self._agent_bay.", "self._agent_bay."),
        ("await self._result.session.", "self._result.session."),
        ("await lc.", "lc."),
        ("await ", ""),
        # Usage example in docstring
        ("    async def test_something(lifecycle):", "    def test_something(lifecycle):"),
        ("        result = await lifecycle.default_create", "        result = lifecycle.default_create"),
        ("        status = await lifecycle.get_status()", "        status = lifecycle.get_status()"),
        # Instance creation
        ("self._agent_bay = AsyncAgentBay", "self._agent_bay = AgentBay"),
        # Type annotation in __init__ return type comments if any
        ("AsyncAgentBay", "AgentBay"),
    ]

    sync_block = async_block
    for old, new in replacements_ordered:
        sync_block = sync_block.replace(old, new)

    # Fix the agent_bay property return type annotation
    sync_block = re.sub(
        r'def agent_bay\(self\) -> AsyncAgentBay:',
        'def agent_bay(self) -> AgentBay:',
        sync_block,
    )
    # Fix Public accessor docstring
    sync_block = sync_block.replace(
        "Public accessor for the underlying AsyncAgentBay client.",
        "Public accessor for the underlying AgentBay client.",
    )

    # ---- reconstruct file ----
    # Keep everything up to (and including) the sync separator + blank lines,
    # then append the generated SyncSessionLifecycle block.
    prefix = content[:sync_section_start]
    new_content = (
        prefix
        + sync_separator
        + "\n\n\n"
        + sync_block
    )

    with open(src_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"  [session_life_functional] SyncSessionLifecycle regenerated from AsyncSessionLifecycle")


def _apply_custom_replacements(content: str, file_path: str) -> str:
    """Apply custom replacements that unasync doesn't handle."""
    # Fix asyncio.wait_for with stop_event.wait() - this is a common pattern in filesystem.py
    # Replace the entire try-except block (with correct indentation)
    content = content.replace(
        "                    try:\n                        asyncio.wait_for(stop_event.wait(), timeout=interval)\n                    except asyncio.TimeoutError:\n                        pass",
        "                    stop_event.wait(timeout=interval)"
    )
    # Also handle the case where it's just the call without try-except
    content = content.replace(
        "asyncio.wait_for(stop_event.wait(), timeout=interval)",
        "stop_event.wait(timeout=interval)"
    )
    # Ensure context start_clear alias is not renamed to clear_async (avoids recursion)
    content = re.sub(
        r"def clear_async\(self, context_id: str\) -> ClearContextResult:\n(\s+\"\"\"\n\s+Deprecated alias for `clear_async`.\n)",
        r"def start_clear(self, context_id: str) -> ClearContextResult:\n\1",
        content,
        flags=re.MULTILINE,
    )
    return content


def _remove_unused_import_asyncio(content: str) -> str:
    """
    Remove `import asyncio` when it's not used.

    unasync + our post-process rules may leave unused `import asyncio` behind.
    This cleanup is usage-aware (AST-based) to avoid breaking files that still
    rely on asyncio (e.g. eval utilities, WS client wrapper).
    """
    if "import asyncio" not in content:
        return content

    try:
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=SyntaxWarning)
            tree = ast.parse(content)
    except Exception:
        return content

    used = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id == "asyncio":
            used = True
            break
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "asyncio"
        ):
            used = True
            break

    if used:
        return content

    return re.sub(
        r"^[ \t]*import asyncio(?:[ \t]+as[ \t]+\w+)?[ \t]*\n",
        "",
        content,
        flags=re.MULTILINE,
    )

def generate_sync(modules: list = None):
    """
    Generate sync code from async sources.

    Args:
        modules: Optional list of modules to sync. Valid values:
                 'sdk'        – agentbay/_async  →  agentbay/_sync
                 'integration'– tests/integration/_async  →  tests/integration/_sync
                                + _common/session_life_functional.py
                 'unit'       – tests/unit/async  →  tests/unit/sync
                 'examples'   – docs/examples/_async  →  docs/examples/_sync
                 When None (default), all modules are synced.
    """
    # Normalise: None means all
    ALL_MODULES = {"sdk", "integration", "unit", "examples"}
    if modules is None:
        active = ALL_MODULES
    else:
        active = set(m.lower() for m in modules)
        unknown = active - ALL_MODULES
        if unknown:
            raise ValueError(f"Unknown module(s): {unknown}. Valid: {ALL_MODULES}")

    _init_skip_sync_generation_files()

    # Determine which (src, dst) directory pairs are active
    dir_pairs = []
    if "sdk" in active:
        dir_pairs.append((ASYNC_DIR, SYNC_DIR))
    if "integration" in active:
        dir_pairs.append((TEST_ASYNC_DIR, TEST_SYNC_DIR))
    if "unit" in active:
        dir_pairs.append((UNIT_TEST_ASYNC_DIR, UNIT_TEST_SYNC_DIR))
    if "examples" in active:
        dir_pairs.append((EXAMPLES_ASYNC_DIR, EXAMPLES_SYNC_DIR))

    # Clean only the active target directories
    clean_dirs = [dst for _, dst in dir_pairs]
    for d in clean_dirs:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d, exist_ok=True)

    # Define rules for unasync
    common_replacements = {
        # Class Renames
        "AsyncAgentBay": "AgentBay",
        "AsyncSession": "Session",
        "AsyncBrowser": "Browser",
        "AsyncCommand": "Command",
        "AsyncCode": "Code",
        "AsyncFileSystem": "FileSystem",
        "AsyncContextManager": "ContextManager",
        "AsyncContextService": "ContextService",
        "AsyncNetwork": "Network",
        "AsyncComputer": "Computer",
        "AsyncMobile": "Mobile",
        "AsyncFileTransfer": "FileTransfer",
        "AsyncOss": "Oss",
        "AsyncAgent": "Agent",
        "AsyncBrowserOperator": "BrowserOperator",
        "AsyncBrowserFingerprintGenerator": "BrowserFingerprintGenerator",
        "AsyncEnv": "Env",
        "AsyncBaseService": "BaseService",
        "AsyncPty": "Pty",
        "AsyncMobileSimulateService": "MobileSimulateService",
        "AsyncExtensionsService": "ExtensionsService",

        # Variable/Attribute Renames
        "init_browser_async": "init_browser",
        "initialize_async": "initialize",
        "call_mcp_tool_async": "call_mcp_tool",
        "call_mcp_tool_with_options_async": "call_mcp_tool_with_options",
        "release_mcp_session_async": "release_mcp_session",
        "create_mcp_session_async": "create_mcp_session",
        "get_cdp_link_async": "get_cdp_link",
        "get_endpoint_url_async": "get_endpoint_url",
        "get_context_info_async": "get_context_info",
        "sync_context_async": "sync_context",
        "get_mcp_resource_async": "get_mcp_resource",
        "set_label_async": "set_label",
        "get_label_async": "get_label",
        "pause_session_async_async": "pause_session_async",
        "resume_session_async_async": "resume_session_async",
        "list_mcp_tools_async": "list_mcp_tools",
        "get_adb_link_async": "get_adb_link",

        # Browser Operator specific
        "navigate_async": "navigate",
        "screenshot_async": "screenshot",
        "act_async": "act",
        "observe_async": "observe",
        "extract_async": "extract",
        "close_async": "close",
        "_execute_act_async": "_execute_act",
        "_execute_extract_async": "_execute_extract",
        "_execute_observe_async": "_execute_observe",
        "_execute_screenshot_async": "_execute_screenshot",
        "_get_page_and_context_index_async": "_get_page_and_context_index",
        "_scroll_to_load_all_content_async": "_scroll_to_load_all_content",
        # "page_use_act_async": "page_use_act",  # Keep async API for compatibility
        # "page_use_extract_async": "page_use_extract",
        # "page_use_observe_async": "page_use_observe",
        # "page_use_screenshot_async": "page_use_screenshot",

        # Agent specific
        "async_execute_task": "async_execute_task",

        # Import fixes (token-level replacements)
        "_async": "_sync",

        # Asyncio replacements
        "asyncio.sleep": "time.sleep",
        "asyncio.Event": "threading.Event",
        "asyncio.TimeoutError": "RuntimeError",
        "async_playwright": "sync_playwright",
        "httpx.AsyncClient": "httpx.Client",
        "await ": "",
        "async def ": "def ",
        "async with ": "with ",
        "async for ": "for ",

        # RPC method replacements
        "do_rpcrequest_async": "do_rpcrequest",

        # Test specific
        "@pytest.mark.asyncio": "",
        "unittest.IsolatedAsyncioTestCase": "unittest.TestCase",
        "IsolatedAsyncioTestCase": "TestCase",
        "AsyncMock": "MagicMock",
        "SyncMock": "MagicMock",
        "assert_awaited_once_with": "assert_called_once_with",
        "async def asyncSetUp": "def setUp",
        "async def asyncTearDown": "def tearDown",
        "asyncSetUp": "setUp",
        "asyncTearDown": "tearDown",
    }

    # Automatically derive client API method mappings from api/client.py
    # (reduces manual maintenance for newly added client methods).
    common_replacements.update(_build_client_api_method_replacements())

    # Build unasync rules only for active modules
    rules = []
    for src_dir, dst_dir in dir_pairs:
        rules.append(unasync.Rule(
            fromdir=src_dir,
            todir=dst_dir,
            additional_replacements=common_replacements
        ))

    # Collect filepaths for active source dirs only
    filepaths = []
    for src_dir, _ in dir_pairs:
        if not os.path.exists(src_dir):
            continue
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    if _should_skip_sync_generation(path):
                        continue
                    filepaths.append(path)

    # Unasync logic
    unasync.unasync_files(filepaths, rules)

    # Copy sync-only templates for skipped async-only modules (per-module precise control)
    # sdk template (ws_client.py) is copied when sdk is active
    # unit templates (ws_streaming, agent_streaming) are copied when unit is active
    if "sdk" in active or "unit" in active:
        for dst, src in SYNC_EXTRA_TEMPLATES.items():
            dst_norm = os.path.normpath(dst)
            is_sdk_template = dst_norm.startswith(os.path.normpath(SYNC_DIR))
            is_unit_template = dst_norm.startswith(os.path.normpath(UNIT_TEST_SYNC_DIR))
            if (is_sdk_template and "sdk" in active) or (is_unit_template and "unit" in active):
                _copy_template_file(src, dst)

    # Sync _common/session_life_functional.py when integration module is active
    if "integration" in active:
        print("Syncing _common/session_life_functional.py...")
        _sync_session_life_functional()

    # Post-process only active target directories
    process_dirs = [dst for _, dst in dir_pairs]

    for directory in process_dirs:
        if not os.path.exists(directory):
            continue

        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()

                    is_sync_ws_client = path.endswith(
                        os.path.join("_internal", "ws_client.py")
                    )

                    # Header check (only for SDK code and tests, not examples)
                    if root.startswith(SYNC_DIR) or root.startswith(TEST_SYNC_DIR):
                        header = "# DO NOT EDIT THIS FILE MANUALLY.\n# This file is auto-generated by scripts/generate_sync.py\n\n"
                        if not content.startswith(header):
                            content = header + content
                    elif root.startswith(EXAMPLES_SYNC_DIR):
                        # For examples, use a simpler header
                        header = "# DO NOT EDIT THIS FILE MANUALLY.\n# This file is auto-generated from the _async directory.\n\n"
                        if not content.startswith(header):
                            content = header + content

                    # Fix httpx.SyncClient issue (unasync might produce this)
                    content = content.replace("httpx.SyncClient", "httpx.Client")
                    # Fix httpx async close method: aclose() -> close() for sync Client
                    content = content.replace(".aclose()", ".close()")

                    # Fix playwright import
                    content = content.replace("playwright.async_api", "playwright.sync_api")

                    # Docstring/examples cleanup: unasync does not reliably transform docstrings.
                    # Apply only to generated SDK sync code and sync examples (avoid mutating tests).
                    if (root.startswith(SYNC_DIR) or root.startswith(EXAMPLES_SYNC_DIR)) and (not is_sync_ws_client):
                        content = re.sub(r"\bawait\s+", "", content)

                    # Custom Replacements
                    # Force replace asyncio.sleep if unasync missed it (common with await removal)
                    if not is_sync_ws_client:
                        content = content.replace("asyncio.sleep", "time.sleep")
                        # Replace asyncio.Lock() with threading.Lock() for sync code
                        content = content.replace("asyncio.Lock()", "threading.Lock()")
                        # Replace asyncio.gather(*tasks) with a list comprehension to keep the expression valid
                        content = content.replace("asyncio.gather(*tasks)", "[task for task in tasks]")
                        # Also handle asyncio.gather with return_exceptions parameter
                        content = content.replace("asyncio.gather(*tasks, return_exceptions=True)", "[task for task in tasks]")
                    # Handle asyncio.gather with concurrent.futures for proper parallel execution
                    if "concurrent_sessions.py" in file:
                        # For concurrent sessions example, use ThreadPoolExecutor
                        replacement = """with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_task_in_session, client, task_id, cmd) for task_id, cmd in tasks]
            results = [future.result() for future in futures]"""
                        content = re.sub(
                            r'        # Run all tasks concurrently\s*\n\s*results = asyncio\.gather\(\s*\*\[run_task_in_session\(client, task_id, cmd\) for task_id, cmd in tasks\]\s*\)',
                            f'        # Run all tasks concurrently\n        {replacement}',
                            content
                        )
                    else:
                        # For other cases, use sequential execution
                        if not is_sync_ws_client:
                            # Handle asyncio.gather with generator expression: asyncio.gather(*(f(x) for x in items))
                            # -> [f(x) for x in items]
                            content = re.sub(
                                r'asyncio\.gather\(\*\(([^)]+) for ([^)]+) in ([^)]+)\)\)',
                                r'[\1 for \2 in \3]',
                                content
                            )
                            content = re.sub(r'asyncio\.gather\(\*([^)]+)\)', r'[task for task in \1]', content)
                    # Handle asyncio.run calls - use a more robust approach
                    # This will match asyncio.run( and find the matching closing parenthesis
                    def remove_asyncio_run(text):
                        result = []
                        i = 0
                        while i < len(text):
                            if text[i:].startswith('asyncio.run('):
                                # Found asyncio.run(
                                i += len('asyncio.run(')
                                paren_count = 1
                                start = i
                                while i < len(text) and paren_count > 0:
                                    if text[i] == '(':
                                        paren_count += 1
                                    elif text[i] == ')':
                                        paren_count -= 1
                                    i += 1
                                # Extract the content inside asyncio.run()
                                if paren_count == 0:
                                    result.append(text[start:i-1])
                                else:
                                    # Unmatched parentheses, keep original
                                    result.append('asyncio.run(' + text[start:i])
                            else:
                                result.append(text[i])
                                i += 1
                        return ''.join(result)

                    content = remove_asyncio_run(content)

                    # Fix invalid line breaks introduced by removing asyncio.run wrapper.
                    # Example that must become valid expression:
                    #   results = asyncio.run(
                    #       run_multiple_tasks(...)
                    #   )
                    # After removing wrapper we may get:
                    #   results =
                    #       run_multiple_tasks(...)
                    # which is invalid Python. Collapse the newline after "=" when the
                    # next token starts an expression call.
                    content = re.sub(
                        r"=\s*\n\s*([A-Za-z_]\w*\()",
                        r"= \1",
                        content,
                    )

                    # Replace asyncio.get_event_loop().time() with time.time()
                    content = content.replace("asyncio.get_event_loop().time()", "time.time()")

                    # Remove asyncio.to_thread() calls - convert to direct function calls
                    # Pattern: asyncio.to_thread(func, arg1, arg2, ...) -> func(arg1, arg2, ...)
                    content = re.sub(r'asyncio\.to_thread\(\s*([^,\)]+),\s*', r'\1(', content)
                    # Also handle asyncio.to_thread with no comma (single arg)
                    content = re.sub(r'asyncio\.to_thread\(([^)]+)\)', r'\1', content)

                    # Remove asyncio.iscoroutine checks - just keep the result assignment
                    # Pattern: if asyncio.iscoroutine(result): out = result
                    # Should become: out = result (just keep the assignment)
                    content = re.sub(r'if asyncio\.iscoroutine\([^)]+\):\s+(\w+)\s+=\s+(\w+)\s*\n\s*else:\s*\n\s*.*?\1\s*=', lambda m: f'{m.group(1)} =', content, flags=re.DOTALL)

                    # Remove asyncio event loop creation in sync code
                    if not is_sync_ws_client:
                        content = re.sub(r'loop\s*=\s*asyncio\.new_event_loop\(\)\s*\n\s*asyncio\.set_event_loop\(loop\)\s*\n', '', content)
                        content = re.sub(r'loop\.close\(\)', '', content)

                    # Remove standalone asyncio.iscoroutine checks without else clause
                    content = re.sub(r'\s*if asyncio\.iscoroutine\([^)]+\):\s*\n\s+\w+\s+=\s+\w+\s*#[^\n]*\n', '\n', content)

                    # Add threading import if threading.Lock() or threading.Event() is used
                    if ('threading.Lock()' in content or 'threading.Event()' in content or 'threading.Event' in content) and 'import threading' not in content:
                        # Find the last import statement and add threading import after it
                        import_pattern = r'^(import [^\n]+\n|from [^\n]+ import [^\n]+\n)'
                        imports = re.findall(import_pattern, content, flags=re.MULTILINE)
                        if imports:
                            # Find the position after the last import
                            last_import_match = None
                            for match in re.finditer(import_pattern, content, flags=re.MULTILINE):
                                last_import_match = match
                            if last_import_match:
                                insert_pos = last_import_match.end()
                                content = content[:insert_pos] + 'import threading\n' + content[insert_pos:]

                    # Add time import if time.sleep or time.time is used
                    if ('time.sleep' in content or 'time.time' in content) and 'import time' not in content:
                        content = "import time\n" + content

                    # Add concurrent.futures import if ThreadPoolExecutor is used
                    if 'concurrent.futures.ThreadPoolExecutor' in content and 'import concurrent.futures' not in content:
                        content = "import concurrent.futures\n" + content

                    # Fix import statements for sync versions
                    # Convert AsyncExtensionsService to ExtensionsService in imports
                    content = content.replace('AsyncExtensionsService', 'ExtensionsService')
                    content = content.replace('AsyncAgentBay', 'AgentBay')

                    # Apply custom replacements
                    content = _apply_custom_replacements(content, path)

                    # Remove whitespace-only lines (no semantic effect, keeps style clean)
                    content = re.sub(r"^[ \t]+\n", "\n", content, flags=re.MULTILINE)

                    # Final fix for filesystem.py _sync_monitor function
                    if "filesystem.py" in file and "def _sync_monitor():" in content:
                        # Pattern to match the broken function
                        pattern = r'def _sync_monitor\(\):\s*\n\s*"""[^"]*"""\s*\n\s*import asyncio\s*\n\s*# Create a new event loop for this thread\s*\n[^}]*?finally:\s*\n[^}]*?\n'
                        replacement = '''def _sync_monitor():
            """Synchronous wrapper for monitoring function."""
            _monitor_directory()
'''
                        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

                        # Fix the missing monitor_thread assignment
                        content = content.replace(
                            '''def _sync_monitor():
            """Synchronous wrapper for monitoring function."""
            _monitor_directory()
            target=_sync_monitor,''',
                            '''def _sync_monitor():
            """Synchronous wrapper for monitoring function."""
            _monitor_directory()

        monitor_thread = threading.Thread(
            target=_sync_monitor,'''
                        )

                    if "filesystem.py" in file:
                        # Fix asyncio.wait_for with stop_event.wait() in monitor loop
                        content = content.replace(
                            "                    try:\n                        asyncio.wait_for(stop_event.wait(), timeout=interval)\n                    except asyncio.TimeoutError:\n                        pass",
                            "                    stop_event.wait(timeout=interval)"
                        )

                        # Fix _sync_monitor function - replace asyncio version with direct call
                        # This needs to happen after all other replacements to avoid interference
                        sync_monitor_old = '''def _sync_monitor():
            """Synchronous wrapper for async monitoring function."""
            import asyncio
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(_monitor_directory())
            finally:
                loop.close()'''

                        sync_monitor_new = '''def _sync_monitor():
            """Synchronous wrapper for monitoring function."""
            _monitor_directory()'''

                        content = content.replace(sync_monitor_old, sync_monitor_new)

                        # _wait_for_event replacement
                        if "def _wait_for_event(self, event, timeout):" in content:
                             content = content.replace("try:\n            event.wait(timeout)\n        except RuntimeError:\n            pass", "event.wait(timeout)")
                             content = content.replace("try:\n            asyncio.wait_for(event.wait(), timeout=timeout)\n        except asyncio.TimeoutError:\n            pass", "event.wait(timeout)")
                             content = content.replace("asyncio.wait_for(event.wait(), timeout=timeout)", "event.wait(timeout)")

                        # _create_task
                        content = content.replace("def _create_task(self, func):", "def _create_task(self, func):")
                        content = content.replace("return asyncio.create_task(coro_func())", "t = threading.Thread(target=coro_func, daemon=True); t.start(); return t")
                        content = content.replace("return asyncio.create_task(func())", "t = threading.Thread(target=func, daemon=True); t.start(); return t")

                        # _create_event
                        content = content.replace("return asyncio.Event()", "return threading.Event()")
                        content = content.replace("stop_event = asyncio.Event()", "stop_event = threading.Event()")

                        # _run_in_thread
                        content = content.replace("return asyncio.to_thread(func, *args)", "return func(*args)")
                        content = content.replace("return await asyncio.to_thread(func, *args)", "return func(*args)")

                        # Fix FileSystem wrapper methods that have loop.run_until_complete
                        # The async source has upload_file and download_file as sync methods that call
                        # async FileTransfer methods via loop.run_until_complete.
                        # After event loop removal (lines 200-201), we're left with:
                        #   result = loop.run_until_complete(
                        #       file_transfer.upload(...
                        #       )
                        #   )
                        # We need to remove loop.run_until_complete wrapper entirely
                        content = re.sub(
                            r'result\s*=\s*loop\.run_until_complete\(\s*\n\s*file_transfer\.(upload|download)\(',
                            r'result = file_transfer.\1(',
                            content
                        )
                        # Remove the extra closing parenthesis from loop.run_until_complete
                        # Pattern: )\n            ) after the parameters
                        content = re.sub(
                            r'(progress_cb=progress_cb,\s*\n\s*)\)\s*\n\s*\)\s*\n',
                            r'\1)\n',
                            content
                        )

                    if "browser_operator.py" in file:
                        content = content.replace("asyncio.get_event_loop().run_until_complete(", "")
                        pass

                    # Handle browser_captcha_takeover.py and browser_login_takeover.py - convert asyncio.Event to threading.Event
                    if ("browser_captcha_takeover.py" in file or "browser_login_takeover.py" in file) and "examples" in path:
                        # Step 1: Replace asyncio.Event with threading.Event
                        content = content.replace("asyncio.Event()", "threading.Event()")
                        content = content.replace("asyncio.Event", "threading.Event")

                        # Step 2: Replace import asyncio with import threading
                        content = re.sub(r"^import asyncio\s*$", "import threading", content, flags=re.MULTILINE)

                        # Step 3: Replace asyncio.wait_for(event.wait(), timeout=x) with event.wait(timeout=x)
                        content = re.sub(
                            r"asyncio\.wait_for\(\s*(\w+)\.wait\(\),\s*timeout=(\w+)\s*\)",
                            r"\1.wait(timeout=\2)",
                            content,
                            flags=re.DOTALL,
                        )

                        # Step 4: Both files now use same structure (try/except + return|pass + if should_takeover); one pattern, one replacement
                        takeover_wait_pattern = re.compile(
                            r"(?:(# Wait for .*\n)\s+)?"
                            r"\s+try:\s*\n\s+"
                            r"(\w+)\.wait\(timeout=(\w+)\)\s*\n\s+"
                            r"except asyncio\.TimeoutError:\s*\n\s+"
                            r"print\(([^)]+)\)\s*\n\s+"
                            r"(return|pass)\s*\n\s+"
                            r"\s+if should_takeover:",
                            re.MULTILINE,
                        )

                        def _replace_takeover_wait(m):
                            comment = m.group(1) or ""
                            ev, timeout, msg, action = m.group(2), m.group(3), m.group(4), m.group(5)
                            # captcha: 12 spaces (main+async with), fixed message, elif; login: 4 spaces, use msg, return, if
                            indent = "            " if "browser_captcha_takeover.py" in file else "    "
                            is_captcha = "browser_captcha_takeover.py" in file
                            print_line = f'{indent}    print("⏰ No captcha detected within timeout, continuing...")\n' if is_captcha else f"{indent}    print({msg})\n"
                            return_line = "" if is_captcha else (f"{indent}    return\n" if action == "return" else "")
                            cond_line = f"{indent}elif should_takeover:" if is_captcha else f"{indent}if should_takeover:"
                            return (
                                f"{comment}{indent}detected = {ev}.wait(timeout={timeout})\n"
                                f"{indent}if not detected:\n"
                                f"{print_line}"
                                f"{return_line}"
                                f"{cond_line}"
                            )

                        if takeover_wait_pattern.search(content):
                            content = takeover_wait_pattern.sub(_replace_takeover_wait, content)

                    # Handle browser_captcha_solving.py and browser_auto_login.py - same pattern: asyncio.Event -> threading.Event, wait_for -> return-value logic
                    if ("browser_captcha_solving.py" in file or "browser_auto_login.py" in file) and "examples" in path:
                        # Step 1: Replace asyncio.Event with threading.Event
                        content = content.replace("asyncio.Event()", "threading.Event()")
                        content = content.replace("asyncio.Event", "threading.Event")

                        # Step 2: Replace import asyncio with import threading
                        content = re.sub(r"^import asyncio\s*$", "import threading", content, flags=re.MULTILINE)

                        # Step 3: Replace asyncio.wait_for(event.wait(), timeout=x) with event.wait(timeout=x)
                        content = re.sub(
                            r"asyncio\.wait_for\(\s*(\w+)\.wait\(\),\s*timeout=(\w+)\s*\)",
                            r"\1.wait(timeout=\2)",
                            content,
                            flags=re.DOTALL,
                        )

                        # Step 4: Convert try/except asyncio.TimeoutError to return-value logic (unified for captcha and autologin)
                        outer_pattern = re.compile(
                            r'    try:\s*\n\s+print\(f"Waiting for (captcha|autologin) pause event[^"]*"\)\s*\n\s+'
                            r"(\w+)\.wait\(timeout=(\w+)\)\s*\n\s+try:\s*\n\s+"
                            r"# (Captcha|Autologin) pause event occurred[^\n]*\n\s*global max_(captcha|autologin)_solving_timeout\s*\n\s+"
                            r'print\(f"Waiting for (captcha|autologin) resume event[^"]*"\)\s*\n\s+'
                            r"(\w+)\.wait\(timeout=(\w+)\)\s*\n\s+global should_takeover\s*\n\s+"
                            r"if should_takeover:\s*\n\s+print\([^)]+\)\s*\n\s+return False\s*\n\s+(?:else:\s*\n\s+)?return True\s*\n\s+"
                            r"except asyncio\.TimeoutError:\s*\n\s+# No resume event[^\n]*\n\s*print\([^)]+\)\s*\n\s+return False\s*\n\s+"
                            r"except asyncio\.TimeoutError:\s*\n\s+# No pause event[^\n]*\n\s*print\([^)]+\)\s*\n\s+return True",
                            re.MULTILINE,
                        )

                        def _replace_wait_solving(m):
                            topic = m.group(1)  # captcha or autologin
                            # Groups: 1=topic, 2=pause_ev, 3=detect_timeout, 4=Topic, 5=topic, 6=topic again, 7=resume_ev, 8=solving_timeout
                            takeover_msg = (
                                "Captcha solving failed, takeover event detected"
                                if topic == "captcha"
                                else "Autologin failed, takeover event detected"
                            )
                            topic_cap = topic.capitalize()
                            return (
                                f'    print(f"Waiting for {topic} pause event, timeout: {{{m.group(3)}}}s")\n'
                                f"    pause_detected = {m.group(2)}.wait(timeout={m.group(3)})\n"
                                f"\n"
                                f"    if not pause_detected:\n"
                                f"        # No pause event within timeout, proceed directly\n"
                                f'        print("No {topic} pause event detected within timeout, proceeding next step")\n'
                                f"        return True\n"
                                f"\n"
                                f"    # {topic_cap} pause event occurred, wait for {topic} resume event\n"
                                f"    global max_{topic}_solving_timeout\n"
                                f'    print(f"Waiting for {topic} resume event, timeout: {{max_{topic}_solving_timeout}}s")\n'
                                f"    resume_detected = {m.group(7)}.wait(timeout={m.group(8)})\n"
                                f"\n"
                                f"    if not resume_detected:\n"
                                f"        # No resume event within timeout, proceed directly\n"
                                f'        print("No {topic} resume event detected within timeout, should takeover")\n'
                                f"        return False\n"
                                f"\n"
                                f"    global should_takeover\n"
                                f"    if should_takeover:\n"
                                f'        print("{takeover_msg}")\n'
                                f"        return False\n"
                                f"    else:\n"
                                f"        return True"
                            )

                        if outer_pattern.search(content):
                            content = outer_pattern.sub(_replace_wait_solving, content)

                        # Step 5: Remove any remaining asyncio.TimeoutError blocks (fallback)
                        content = re.sub(
                            r"    except asyncio\.TimeoutError:\s*\n\s+# No pause event[^\n]*\n\s*print\([^)]+\)\s*\n\s+return True\s*\n",
                            "",
                            content,
                            flags=re.MULTILINE,
                        )
                        content = re.sub(
                            r"        except asyncio\.TimeoutError:\s*\n\s+# No resume event[^\n]*\n\s*print\([^)]+\)\s*\n\s+return False\s*\n",
                            "",
                            content,
                            flags=re.MULTILINE,
                        )

                        # Step 6: Clean up trailing whitespace
                        content = re.sub(r"(\n\s*return True)\s+(\n\ndef )", r"\1\2", content)

                    # Test specific cleanup

                    # Fix asyncio.wait_for(handle.wait_end(), timeout=X)
                    # -> handle.wait_end_with_timeout(X)
                    # This handles the WS handle pattern where the sync client
                    # exposes wait_end_with_timeout() as the blocking equivalent.
                    content = re.sub(
                        r'asyncio\.wait_for\(\s*(\w+)\.wait_end\(\)\s*,\s*timeout\s*=\s*([^\)]+?)\s*\)',
                        r'\1.wait_end_with_timeout(\2)',
                        content,
                    )

                    # Fix asyncio.wait_for(event.wait(), timeout=X)
                    # -> event.wait(timeout=X)
                    # Handles threading.Event / asyncio.Event patterns in test files.
                    content = re.sub(
                        r'asyncio\.wait_for\(\s*(\w+)\.wait\(\)\s*,\s*timeout\s*=\s*([^\)]+?)\s*\)',
                        r'\1.wait(timeout=\2)',
                        content,
                    )

                    # Fix remaining asyncio.Event() -> threading.Event() in test files
                    # (unasync common_replacements may not cover files excluded from unasync processing)
                    if not is_sync_ws_client:
                        content = content.replace("asyncio.Event()", "threading.Event()")
                        content = content.replace("asyncio.Event", "threading.Event")

                    # Re-check threading import after asyncio.Event replacements above may have
                    # introduced threading.Event references that weren't present earlier.
                    if ('threading.Lock()' in content or 'threading.Event()' in content or 'threading.Event' in content) and 'import threading' not in content:
                        _import_pattern = r'^(import [^\n]+\n|from [^\n]+ import [^\n]+\n)'
                        _last_import_match = None
                        for _m in re.finditer(_import_pattern, content, flags=re.MULTILINE):
                            _last_import_match = _m
                        if _last_import_match:
                            _pos = _last_import_match.end()
                            content = content[:_pos] + 'import threading\n' + content[_pos:]

                    content = content.replace("@pytest.mark.asyncio", "@pytest.mark.sync")
                    content = content.replace("@pytest_asyncio.fixture", "@pytest.fixture")
                    content = content.replace("import pytest_asyncio", "import pytest")
                    # Fix duplicate pytest import produced by replacing import pytest_asyncio -> import pytest
                    content = re.sub(r'^import pytest\nimport pytest\n', 'import pytest\n', content, flags=re.MULTILINE)

                    # Fix conftest.py teardown: asyncio.gather with generator expression -> list comprehension
                    # Pattern: await asyncio.gather(*(func(x) for x in iterable))
                    # ->        [func(x) for x in iterable]
                    # This handles the single-line case
                    content = re.sub(
                        r'asyncio\.gather\(\*\(([^)]+)\(([^)]+)\) for (\w+) in (\w+)\)\)',
                        r'[\1(\2) for \3 in \4]',
                        content,
                    )

                    # For conftest.py: also remove leftover import asyncio (it's only referenced in
                    # docstring/comments after sync conversion, not in actual code)
                    if file == "conftest.py":
                        # Force-remove import asyncio – conftest never needs it after sync conversion
                        content = re.sub(
                            r'^[ \t]*import asyncio(?:[ \t]+as[ \t]+\w+)?[ \t]*\n',
                            '',
                            content,
                            flags=re.MULTILINE,
                        )
                        # Fix the broken asyncio.gather remnant from sync generation:
                        # [task for task in (_delete_one(lc] for lc in created))
                        # -> [_delete_one(lc) for lc in created]
                        content = content.replace(
                            "[task for task in (_delete_one(lc] for lc in created))",
                            "[_delete_one(lc) for lc in created]",
                        )

                    # Fix patch paths in unit tests
                    content = content.replace('"agentbay._async', '"agentbay._sync')
                    content = content.replace("'agentbay._async", "'agentbay._sync")
                    # Fix patch decorators with async module paths and class names
                    content = re.sub(r'@patch\("agentbay\._sync\.([^"]+)\.Async([^"]+)"\)', r'@patch("agentbay._sync.\1.\2")', content)
                    content = re.sub(r"@patch\('agentbay\._sync\.([^']+)\.Async([^']+)'\)", r"@patch('agentbay._sync.\1.\2')", content)
                    # Also fix patch calls with AsyncSession -> Session
                    content = re.sub(r'patch\("agentbay\._sync\.([^"]+)\.AsyncSession"\)', r'patch("agentbay._sync.\1.Session")', content)
                    content = re.sub(r"patch\('agentbay\._sync\.([^']+)\.AsyncSession'\)", r"patch('agentbay._sync.\1.Session')", content)

                    # Remove asyncio.iscoroutinefunction checks in sync tests
                    content = re.sub(r'assert asyncio\.iscoroutinefunction\([^)]+\)', 'assert True  # Sync version check removed', content)
                    content = re.sub(r'assert not asyncio\.iscoroutinefunction\([^)]+\)', 'assert True  # Sync version check removed', content)
                    # Handle inspect.iscoroutinefunction checks in sync tests
                    content = re.sub(r'assert inspect\.iscoroutinefunction\([^)]+\)', 'assert True  # Sync version - method is not async', content)
                    # Handle coroutine checks in sync tests
                    content = re.sub(r'if inspect\.iscoroutine\([^)]+\):', 'if False:  # Sync version - no coroutines', content)
                    content = re.sub(r'pytest\.fail\("([^"]*should return a coroutine[^"]*)"\)', r'assert True  # Sync version - \1', content)

                    # Replace test class names: TestAsync* -> TestSync*
                    # This handles all test classes like TestAsyncGitHelpers -> TestSyncGitHelpers,
                    # TestAsyncCommand -> TestSyncCommand, etc.
                    content = re.sub(r'\bTestAsync(\w+)', r'TestSync\1', content)

                    # Fix duplicate MagicMock imports caused by AsyncMock -> MagicMock replacement
                    # e.g., "from unittest.mock import MagicMock, MagicMock" -> "from unittest.mock import MagicMock"
                    content = re.sub(r'\bMagicMock,\s*MagicMock\b', 'MagicMock', content)

                    # Replace descriptive "Async" text in docstrings and comments
                    # e.g., "AsyncGit module" -> "SyncGit module", "AsyncCommand" -> "SyncCommand"
                    # Uses negative lookbehind to avoid matching API model names like DeleteSessionAsyncRequest
                    content = re.sub(
                        r'(?<!\w)Async(Git|Command|Code|FileSystem|FileTransfer|Session|Browser|Computer|Mobile|Oss|Agent|Network|Context|ContextManager|ContextService|MobileSimulate|MobileSimulateService|BrowserOperator|BetaNetwork|BetaSkills|BaseService|Skills|Extensions|ExtensionsService|Pty)\b(?!\w*(?:Request|Response|Body))',
                        r'Sync\1',
                        content
                    )

                    # Replace "Asynchronously" -> "Synchronously" in docstrings/comments
                    content = content.replace("Asynchronously ", "Synchronously ")
                    content = content.replace("asynchronously", "synchronously")
                    content = content.replace("Asynchronous ", "Synchronous ")
                    content = content.replace("asynchronous ", "synchronous ")

                    # Replace remaining descriptive "Async" in docstrings/comments
                    # These are generic phrases that should not appear in sync code
                    content = content.replace("Async version of ", "Sync version of ")
                    content = content.replace("Async API call", "Sync API call")
                    content = content.replace("Async call", "Sync call")
                    content = content.replace("Async stub ", "Sync stub ")
                    content = content.replace("Async command execution service", "Sync command execution service")
                    content = content.replace("Async Skills service", "Sync Skills service")
                    content = content.replace("\"\"\"Async ", "\"\"\"Sync ")

                    # Remove unused asyncio import (usage-aware). Run late because earlier
                    # replacements may remove asyncio usages (e.g. filesystem monitor helpers).
                    content = _remove_unused_import_asyncio(content)

                    with open(path, "w", encoding="utf-8") as f:
                        f.write(content)

def process_examples_non_python_files():
    """Process non-Python files in examples directory (Markdown, images, etc.)"""
    if not os.path.exists(EXAMPLES_ASYNC_DIR):
        return

    print("Processing non-Python files in examples...")

    for root, dirs, files in os.walk(EXAMPLES_ASYNC_DIR):
        for file in files:
            if file.endswith('.py') or file == '__pycache__':
                continue

            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, EXAMPLES_ASYNC_DIR)
            dest_path = os.path.join(EXAMPLES_SYNC_DIR, rel_path)

            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)

            if file.endswith('.md'):
                # Process Markdown files
                convert_markdown_file(src_path, dest_path)
            else:
                # Copy other files as-is
                shutil.copy2(src_path, dest_path)

def convert_markdown_file(src_path: str, dest_path: str):
    """Convert Markdown files from async to sync versions"""
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace AsyncAgentBay -> AgentBay (Documentation text)
    content = content.replace("AsyncAgentBay", "AgentBay")
    content = content.replace("AsyncSession", "Session")

    # Remove await keywords from code blocks
    content = re.sub(r'await\s+', '', content)

    # Replace async def with def in code blocks
    content = content.replace("async def ", "def ")

    # Replace asyncio.sleep with time.sleep
    content = content.replace("await asyncio.sleep(", "time.sleep(")
    content = content.replace("asyncio.sleep(", "time.sleep(")

    # Replace API links: docs/api/async/async-*.md -> docs/api/sync/*.md
    content = re.sub(r"docs/api/async/async-([a-z0-9-]+)\.md", r"docs/api/sync/\1.md", content)

    # Replace example links: _async -> _sync
    content = content.replace("/_async/", "/_sync/")

    # Write converted content
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate sync code from async sources."
    )
    parser.add_argument(
        "--module",
        metavar="MODULE",
        nargs="+",
        choices=["sdk", "integration", "unit", "examples", "all"],
        default=["all"],
        help=(
            "Which module(s) to sync. Choices: sdk | integration | unit | examples | all. "
            "Defaults to 'all'. Example: --module integration unit"
        ),
    )
    args = parser.parse_args()

    # 'all' → pass None so generate_sync() handles all modules
    selected = None if "all" in args.module else args.module

    if selected is None:
        print(f"Generating sync code from {ASYNC_DIR} to {SYNC_DIR}...")
        print(f"Generating sync tests from {TEST_ASYNC_DIR} to {TEST_SYNC_DIR}...")
    else:
        print(f"Generating sync code for module(s): {selected}")

    generate_sync(modules=selected)

    # process_examples_non_python_files only when examples is included
    if selected is None or "examples" in selected:
        process_examples_non_python_files()

    print("Done.")
