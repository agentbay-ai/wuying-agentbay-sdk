"""Integration tests for AgentBay async client and session operations."""

import time

import pytest

from agentbay import (
    BWList,
    DeletePolicy,
    DownloadPolicy,
    ExtractPolicy,
    Lifecycle,
    RecyclePolicy,
    SyncPolicy,
    UploadPolicy,
    WhiteList,
)

# make_session factory fixture is provided by conftest.py (auto-loaded by pytest)


# ---------------------------------------------------------------------------
# TestAsyncAgentBay – create / delete
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_list_delete(make_session):
    """Test create and delete methods."""
    print("Creating a new session...")
    lc = await make_session("linux_latest")

    s = lc._result.session
    print(f"Session created with ID: {s.session_id}")
    assert s.session_id is not None
    assert s.session_id != ""
    # Session cleanup is handled by the make_session factory in conftest.py


# ---------------------------------------------------------------------------
# TestSession – properties and basic operations
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_session_properties(make_session):
    """Test session properties and methods."""
    lc = await make_session("linux_latest")
    session = lc._result.session

    assert session.session_id is not None
    assert session.session_id != ""

    api_key = session.agent_bay.api_key
    assert api_key is not None

    client = session.agent_bay.client
    assert client is not None


# ---------------------------------------------------------------------------
# RecyclePolicy – session creation (network)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_session_with_custom_recycle_policy(make_session):
    """Test creating session with custom recyclePolicy using Lifecycle_1Day."""
    pytest.skip("Skipping recycle policy test for now")
    recycle_policy = RecyclePolicy(lifecycle=Lifecycle.LIFECYCLE_1DAY, paths=[""])
    custom_sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=recycle_policy,
        bw_list=BWList(white_lists=[WhiteList(path="", exclude_paths=[])]),
    )

    lc = await make_session(
        "linux_latest",
        context_name="test-recycle-context",
        context_path="/test/recycle/path",
        context_policy=custom_sync_policy,
    )
    s = lc._result.session
    assert s is not None
    assert s.session_id is not None
    assert len(s.session_id) > 0
    print(f"Session created successfully with ID: {s.session_id}")


# ---------------------------------------------------------------------------
# WhiteList pattern (BWList is_path_regex + is_exclude_regex)
# ---------------------------------------------------------------------------


async def _collect_all_files(agent_bay, context_id: str, folder_path: str, sep: str = "\\") -> list:
    """Recursively collect only FILE entries under folder_path.

    Works for both Windows-style (sep="\\") and Linux-style (sep="/") paths.
    list_files accepts the local path and returns entries whose file_path is an OSS-style path.
    For FOLDER entries: extract the last segment from entry.file_path and
      build the next local path = folder_path + sep + last_segment, then recurse.
    For FILE entries: extract the last segment (file name) and store it.
    Returns a flat list of file name strings collected under folder_path.
    """
    result = await agent_bay.context.list_files(
        context_id=context_id,
        parent_folder_path=folder_path,
        page_size=200,
    )
    if not result.success or not result.entries:
        return []
    file_paths = []
    for entry in result.entries:
        ftype = (entry.file_type or "").upper()
        # Extract the last segment from the OSS path
        last_segment = entry.file_path.rstrip("/").rsplit("/", 1)[-1]
        if ftype in ("FOLDER", "DIR", "DIRECTORY"):
            # Build local sub-path and recurse
            sub_path = folder_path.rstrip(sep) + sep + last_segment
            file_paths.extend(
                await _collect_all_files(agent_bay, context_id, sub_path, sep=sep)
            )
        else:
            # FILE: store the file name
            file_paths.append(last_segment)
    return file_paths


def _make_bwlist_sync_policy() -> SyncPolicy:
    """Build a SyncPolicy with BWList: include 'project-.*' dirs, exclude 'cache.*' sub-dirs."""
    return SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=RecyclePolicy.default(),
        bw_list=BWList(white_lists=[
            WhiteList(
                path=r"project-.*",
                is_path_regex=True,
                exclude_paths=[r"cache.*"],
                is_exclude_regex=True,
            )
        ]),
    )


async def _verify_bwlist_oss_files(agent_bay, context_id: str, base: str, sep: str = "\\") -> None:
    """Verify OSS file list after a BWList-filtered upload.

    Asserts:
      - Exactly 3 files uploaded (main.py, README.txt, config.json)
      - temp.log is absent (excluded by BWList)
    """
    print("\n=== Verifying OSS content via context.list_files ===")
    probe = await agent_bay.context.list_files(
        context_id=context_id, parent_folder_path=base, page_size=200
    )
    entry_count = len(probe.entries) if probe.entries else 0
    print(f"  list_files({base!r}) -> success={probe.success}, entries={entry_count}")

    all_files: list = []
    if probe.entries:
        for e in probe.entries:
            ftype = (e.file_type or "").upper()
            last_segment = e.file_path.rstrip("/").rsplit("/", 1)[-1]
            print(f"    [{ftype}] {e.file_path!r}  -> last_segment={last_segment!r}")
            if ftype in ("FOLDER", "DIR", "DIRECTORY"):
                sub_path = base.rstrip(sep) + sep + last_segment
                print(f"      Recursing into {sub_path!r}...")
                sub_files = await _collect_all_files(agent_bay, context_id, sub_path, sep=sep)
                all_files.extend(sub_files)
            else:
                all_files.append(e.file_path)
    else:
        print("  WARNING: No entries found in OSS.")

    print(f"  Collected {len(all_files)} file(s) total")
    print(f"\n  === All files in OSS ({len(all_files)} total) ===")
    assert len(all_files) == 3, f"Expected 3 files in OSS, got {len(all_files)}: {all_files}"
    for p in all_files:
        print(f"    {p}")

    for name in ["main.py", "README.txt", "config.json"]:
        found = any(name in p for p in all_files)
        print(f"  {'FOUND' if found else 'NOT FOUND'}: {name}")
        assert found, f"Expected '{name}' in OSS after BWList upload filter, not found in: {all_files}"
    print("\u2705 Expected files present in OSS")

    for name in ["temp.log"]:
        found = any(name in p for p in all_files)
        print(f"  {'FOUND (should be absent!)' if found else 'correctly absent'}: {name}")
        assert not found, f"Expected '{name}' ABSENT (excluded by BWList), but found in: {all_files}"
    print("\u2705 Excluded files correctly absent from OSS")


@pytest.mark.asyncio
async def test_create_session_with_pattern_bwlist_windows(make_session):
    """Test ContextSync BWList with is_path_regex=True and is_exclude_regex=True.

    Single-session strategy:
      1. Create session WITH BWList configured (upload filter).
      2. Write test files onto the session's local FS.
      3. delete(sync_context=True) triggers upload; BWList filters which files go to OSS.
      4. Poll context.list_files(base) to find OSS entries.
      5. Recursively collect all FILE entries from OSS root.
      6. Assert expected files present, excluded files absent.

    File structure:
        testdata/project-alpha/main.py
        testdata/project-alpha/README.txt
        testdata/project-beta/config.json
        testdata/project-beta/cache/temp.log  <- excluded by exclude_paths regex

    BWList (upload filter):
        path=r"project-.*"  (is_path_regex=True)
        exclude_paths=[r"cache.*"]  (is_exclude_regex=True)

    Expected in OSS:
        PRESENT:  project-alpha/main.py, project-alpha/README.txt, project-beta/config.json
        ABSENT:   project-beta/cache/temp.log
    """
    print("Testing BWList is_path_regex + is_exclude_regex via single-session strategy...")

    pytest.skip("Skipping BWList test for now")
    base = "C:\\Users\\Administrator\\testdata"
    context_name = f"bwlist-ctx-{int(time.time())}"

    sync_policy = SyncPolicy(
        upload_policy=UploadPolicy.default(),
        download_policy=DownloadPolicy.default(),
        delete_policy=DeletePolicy.default(),
        extract_policy=ExtractPolicy.default(),
        recycle_policy=RecyclePolicy.default(),
        bw_list=BWList(white_lists=[
            WhiteList(
                path=r"project-.*",
                is_path_regex=True,
                exclude_paths=[r"cache.*"],
                is_exclude_regex=True,
            )
        ]),
    )

    # ── Create session WITH BWList ─────────────────────────────────────────────
    lc = await make_session(
        "computer-use-ubuntu-2204",
        context_name=context_name,
        context_path=base,
        context_policy=sync_policy,
    )
    s = lc._result.session
    agent_bay = lc.agent_bay
    context_id = lc._owned_contexts[0].id
    print(f"Session ID: {s.session_id}, Context ID: {context_id}")

    # ── Write test files onto local FS ────────────────────────────────────────
    fs = s.file_system
    for d in [base, f"{base}\\project-alpha", f"{base}\\project-beta", f"{base}\\project-beta\\cache"]:
        r = await fs.create_directory(d)
        print(f"  mkdir {d}: {'OK' if r.success else r.error_message}")

    test_files = [
        (f"{base}\\project-alpha\\main.py",       "# main entry point\nprint('hello')\n"),
        (f"{base}\\project-alpha\\README.txt",     "Project Alpha README\n"),
        (f"{base}\\project-beta\\config.json",     '{"env": "test"}\n'),
        (f"{base}\\project-beta\\cache\\temp.log", "temporary log\n"),
    ]
    for fpath, content in test_files:
        r = await fs.write_file(fpath, content)
        print(f"  write {fpath}: {'OK' if r.success else r.error_message}")

    # ── delete via lifecycle (sync_context=True is set automatically) ──────────
    print("  Deleting session with sync_context=True (BWList upload filter applied)...")
    del_result = await lc.delete()
    assert del_result.success, f"Session delete failed: {del_result.error_message}"
    print("  Session deleted. Filtered upload triggered.")

    # ── Verify OSS content ──────────────────────────────────────────────────
    await _verify_bwlist_oss_files(agent_bay, context_id, base, sep="\\")
    print("BWList with is_path_regex + is_exclude_regex verified successfully (Windows)")


@pytest.mark.asyncio
async def test_create_session_with_pattern_bwlist_linux(make_session):
    """Test ContextSync BWList with is_path_regex=True and is_exclude_regex=True (Linux path).

    Same BWList strategy as the Windows counterpart, but runs on a Linux session
    with paths under /home/wuying/testdata.

    File structure:
        /home/wuying/testdata/project-alpha/main.py
        /home/wuying/testdata/project-alpha/README.txt
        /home/wuying/testdata/project-beta/config.json
        /home/wuying/testdata/project-beta/cache/temp.log  <- excluded by exclude_paths regex

    BWList (upload filter):
        path=r"project-.*"  (is_path_regex=True)
        exclude_paths=[r"cache.*"]  (is_exclude_regex=True)

    Expected in OSS:
        PRESENT:  project-alpha/main.py, project-alpha/README.txt, project-beta/config.json
        ABSENT:   project-beta/cache/temp.log
    """
    print("Testing BWList is_path_regex + is_exclude_regex via single-session strategy (Linux)...")
    pytest.skip("Skipping BWList test for now")
    base = "/home/wuying/testdata"
    context_name = f"bwlist-linux-ctx-{int(time.time())}"

    # ── Create session WITH BWList ─────────────────────────────────────────────
    lc = await make_session(
        "linux_latest",
        context_name=context_name,
        context_path=base,
        context_policy=_make_bwlist_sync_policy(),
    )
    s = lc._result.session
    agent_bay = lc.agent_bay
    context_id = lc._owned_contexts[0].id
    print(f"Session ID: {s.session_id}, Context ID: {context_id}")

    # ── Write test files onto local FS ────────────────────────────────────────
    fs = s.file_system
    for d in [base, f"{base}/project-alpha", f"{base}/project-beta", f"{base}/project-beta/cache"]:
        r = await fs.create_directory(d)
        print(f"  mkdir {d}: {'OK' if r.success else r.error_message}")

    test_files = [
        (f"{base}/project-alpha/main.py",       "# main entry point\nprint('hello')\n"),
        (f"{base}/project-alpha/README.txt",     "Project Alpha README\n"),
        (f"{base}/project-beta/config.json",     '{"env": "test"}\n'),
        (f"{base}/project-beta/cache/temp.log", "temporary log\n"),
    ]
    for fpath, content in test_files:
        r = await fs.write_file(fpath, content)
        print(f"  write {fpath}: {'OK' if r.success else r.error_message}")

    # ── delete via lifecycle (sync_context=True is set automatically) ──────────
    print("  Deleting session with sync_context=True (BWList upload filter applied)...")
    del_result = await lc.delete()
    assert del_result.success, f"Session delete failed: {del_result.error_message}"
    print("  Session deleted. Filtered upload triggered.")

    # ── Verify OSS content ──────────────────────────────────────────────────
    await _verify_bwlist_oss_files(agent_bay, context_id, base, sep="/")
    print("BWList with is_path_regex + is_exclude_regex verified successfully (Linux)")



# ---------------------------------------------------------------------------
# BrowserContext – session creation (network)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_session_with_browser_context_default_recycle_policy(make_session):
    """Test creating session with BrowserContext using default RecyclePolicy."""
    print("Testing session creation with BrowserContext (default RecyclePolicy)...")

    context_name = f"test-browser-context-default-{int(time.time())}"
    lc = await make_session(
        "linux_latest",
        browser_name=context_name,
        browser_kwargs={"auto_upload": True},
    )
    s = lc._result.session
    assert s is not None
    assert s.session_id is not None
    assert len(s.session_id) > 0
    print(f"Session created successfully with ID: {s.session_id}")
    print(
        "Session with BrowserContext (default RecyclePolicy) created and verified successfully"
    )
    # Session and browser context cleanup is handled by the make_session factory in conftest.py

