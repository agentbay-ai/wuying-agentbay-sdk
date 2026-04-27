"""
Integration tests for AsyncGit module.

End-to-end workflow tests that mirror the TypeScript git.integration.test.ts
test suite. Requires a real AgentBay session with git support.

All steps run inside a single async test function to avoid pytest-asyncio
event-loop-scope issues with module-scoped fixtures.
"""

import pytest

from agentbay import CreateSessionParams
from agentbay._common.exceptions import GitError, GitNotARepoError

IMAGE_ID = "linux_latest"
LOCAL_REPO = "/tmp/test-git-workflow"
REPO_URL = "https://github.com/DingTalk-Real-AI/dingtalk-openclaw-connector.git"


@pytest.mark.asyncio
async def test_git_workflow(make_session):
    """Full git workflow integration test running in a single event loop.

    Covers: init, status, add, commit, log, branches, remote, reset, restore,
    configure_user, config, and clone.
    """
    print(f"\nCreating session (image: {IMAGE_ID}) ...")
    params = CreateSessionParams(image_id=IMAGE_ID)
    lc = await make_session(params=params)
    session = lc._result.session
    print(f"Session created: {session.session_id}")

    try:
        # ---------------------------------------------------------------
        # 1. init
        # ---------------------------------------------------------------
        await session.command.execute_command(f"mkdir -p {LOCAL_REPO}", 10000)
        init_result = await session.git.init(LOCAL_REPO, initial_branch="main")
        assert init_result.path == LOCAL_REPO
        print(f"[1/19] init -> {init_result.path}")

        # ---------------------------------------------------------------
        # 2. status - clean after init
        # ---------------------------------------------------------------
        status = await session.git.status(LOCAL_REPO)
        assert status.current_branch == "main"
        assert status.is_clean
        print(f"[2/19] status clean, branch={status.current_branch}")

        # ---------------------------------------------------------------
        # 3. status - untracked after creating a file
        # ---------------------------------------------------------------
        await session.command.execute_command(
            f"echo 'hello from agentbay test' > {LOCAL_REPO}/test-file.txt",
            30000,
        )
        status = await session.git.status(LOCAL_REPO)
        assert not status.is_clean
        files = [f for f in status.files if f.path == "test-file.txt"]
        assert len(files) == 1
        assert files[0].index_status == "?"
        print("[3/19] untracked file detected")

        # ---------------------------------------------------------------
        # 4. add - stage the file
        # ---------------------------------------------------------------
        await session.git.add(LOCAL_REPO, files=["test-file.txt"])
        status = await session.git.status(LOCAL_REPO)
        files = [f for f in status.files if f.path == "test-file.txt"]
        assert len(files) == 1
        assert files[0].index_status == "A"
        print("[4/19] file staged (A)")

        # ---------------------------------------------------------------
        # 5. commit
        # ---------------------------------------------------------------
        commit_result = await session.git.commit(
            LOCAL_REPO,
            "test: add test file from agentbay",
            author_name="AgentBay Test",
            author_email="test@agentbay.com",
        )
        print(f"[5/19] commit hash: {commit_result.commit_hash}")
        status = await session.git.status(LOCAL_REPO)
        assert status.is_clean
        print("[5/19] repo is clean after commit")

        # ---------------------------------------------------------------
        # 6. log
        # ---------------------------------------------------------------
        log_result = await session.git.log(LOCAL_REPO, max_count=3)
        assert len(log_result.entries) > 0
        latest = log_result.entries[0]
        assert "test: add test file from agentbay" in latest.message
        assert latest.author_name == "AgentBay Test"
        assert latest.author_email == "test@agentbay.com"
        assert latest.hash
        print(f"[6/19] log: {latest.short_hash} | {latest.message}")

        # ---------------------------------------------------------------
        # 7. list_branches
        # ---------------------------------------------------------------
        br = await session.git.list_branches(LOCAL_REPO)
        assert br.current == "main"
        assert len(br.branches) > 0
        current = [b for b in br.branches if b.is_current]
        assert len(current) == 1
        assert current[0].name == "main"
        print(f"[7/19] branches: {[b.name for b in br.branches]}")

        # ---------------------------------------------------------------
        # 8. create_branch
        # ---------------------------------------------------------------
        await session.git.create_branch(LOCAL_REPO, "feature/test-branch")
        br = await session.git.list_branches(LOCAL_REPO)
        assert br.current == "feature/test-branch"
        print("[8/19] created & checked out feature/test-branch")

        # ---------------------------------------------------------------
        # 9. checkout_branch
        # ---------------------------------------------------------------
        await session.git.checkout_branch(LOCAL_REPO, "main")
        br = await session.git.list_branches(LOCAL_REPO)
        assert br.current == "main"
        print("[9/19] checked out main")

        # ---------------------------------------------------------------
        # 10. delete_branch
        # ---------------------------------------------------------------
        await session.git.delete_branch(LOCAL_REPO, "feature/test-branch", force=True)
        br = await session.git.list_branches(LOCAL_REPO)
        names = [b.name for b in br.branches]
        assert "feature/test-branch" not in names
        print(f"[10/19] remaining branches: {names}")

        # ---------------------------------------------------------------
        # 11. remote_add + remote_get
        # ---------------------------------------------------------------
        remote_url = "https://github.com/example/test-remote.git"
        await session.git.remote_add(LOCAL_REPO, "origin", remote_url)
        got = await session.git.remote_get(LOCAL_REPO, "origin")
        assert got == remote_url

        new_url = "https://github.com/example/test-remote-v2.git"
        await session.git.remote_add(LOCAL_REPO, "origin", new_url, overwrite=True)
        got2 = await session.git.remote_get(LOCAL_REPO, "origin")
        assert got2 == new_url

        missing = await session.git.remote_get(LOCAL_REPO, "nonexistent")
        assert missing is None
        print("[11/19] remote_add + remote_get OK")

        # ---------------------------------------------------------------
        # 12. reset (mixed)
        # ---------------------------------------------------------------
        await session.command.execute_command(
            f"echo 'reset test' > {LOCAL_REPO}/reset-test.txt", 10000
        )
        await session.git.add(LOCAL_REPO, files=["reset-test.txt"])
        await session.git.commit(
            LOCAL_REPO,
            "test: add reset-test.txt",
            author_name="AgentBay Test",
            author_email="test@agentbay.com",
        )

        await session.command.execute_command(
            f"echo 'modified' >> {LOCAL_REPO}/reset-test.txt", 10000
        )
        await session.git.add(LOCAL_REPO, files=["reset-test.txt"])

        status = await session.git.status(LOCAL_REPO)
        staged = [
            f
            for f in status.files
            if f.path == "reset-test.txt" and f.index_status == "M"
        ]
        assert len(staged) == 1

        await session.git.reset(LOCAL_REPO, mode="mixed")
        status = await session.git.status(LOCAL_REPO)
        after = [f for f in status.files if f.path == "reset-test.txt"]
        assert len(after) == 1
        assert after[0].index_status == " "
        assert after[0].work_tree_status == "M"
        print("[12/19] mixed reset OK")

        # ---------------------------------------------------------------
        # 13. reset (hard)
        # ---------------------------------------------------------------
        await session.git.reset(LOCAL_REPO, mode="hard")
        status = await session.git.status(LOCAL_REPO)
        assert status.is_clean
        print("[13/19] hard reset OK")

        # ---------------------------------------------------------------
        # 14. restore (worktree)
        # ---------------------------------------------------------------
        await session.command.execute_command(
            f"echo 'restore test' >> {LOCAL_REPO}/reset-test.txt", 10000
        )
        status = await session.git.status(LOCAL_REPO)
        modified = [f for f in status.files if f.path == "reset-test.txt"]
        assert len(modified) == 1
        assert modified[0].work_tree_status == "M"

        await session.git.restore(LOCAL_REPO, ["reset-test.txt"])
        status = await session.git.status(LOCAL_REPO)
        assert status.is_clean
        print("[14/19] restore worktree OK")

        # ---------------------------------------------------------------
        # 15. restore --staged
        # ---------------------------------------------------------------
        await session.command.execute_command(
            f"echo 'staged restore' >> {LOCAL_REPO}/reset-test.txt", 10000
        )
        await session.git.add(LOCAL_REPO, files=["reset-test.txt"])

        status = await session.git.status(LOCAL_REPO)
        staged = [
            f
            for f in status.files
            if f.path == "reset-test.txt" and f.index_status == "M"
        ]
        assert len(staged) == 1

        await session.git.restore(LOCAL_REPO, ["reset-test.txt"], staged=True)
        status = await session.git.status(LOCAL_REPO)
        after = [f for f in status.files if f.path == "reset-test.txt"]
        assert len(after) == 1
        assert after[0].index_status == " "
        assert after[0].work_tree_status == "M"

        await session.git.reset(LOCAL_REPO, mode="hard")
        print("[15/19] restore --staged OK")

        # ---------------------------------------------------------------
        # 16. configure_user
        # ---------------------------------------------------------------
        await session.git.configure_user(
            LOCAL_REPO, "Test Bot", "testbot@example.com", scope="local"
        )
        name = await session.git.get_config(LOCAL_REPO, "user.name", scope="local")
        email = await session.git.get_config(LOCAL_REPO, "user.email", scope="local")
        assert name == "Test Bot"
        assert email == "testbot@example.com"
        print(f"[16/19] configure_user OK: {name} <{email}>")

        # ---------------------------------------------------------------
        # 17. set_config + get_config
        # ---------------------------------------------------------------
        await session.git.set_config(
            LOCAL_REPO, "core.autocrlf", "false", scope="local"
        )
        val = await session.git.get_config(LOCAL_REPO, "core.autocrlf", scope="local")
        assert val == "false"

        missing_config = await session.git.get_config(
            LOCAL_REPO, "nonexistent.key", scope="local"
        )
        assert missing_config is None
        print("[17/19] set_config + get_config OK")

        # ---------------------------------------------------------------
        # 18. reset --paths
        # ---------------------------------------------------------------
        await session.command.execute_command(
            f"echo 'a' > {LOCAL_REPO}/file-a.txt && echo 'b' > {LOCAL_REPO}/file-b.txt",
            10000,
        )
        await session.git.add(LOCAL_REPO)

        status = await session.git.status(LOCAL_REPO)
        assert any(
            f.path == "file-a.txt" and f.index_status == "A"
            for f in status.files
        )
        assert any(
            f.path == "file-b.txt" and f.index_status == "A"
            for f in status.files
        )

        await session.git.reset(LOCAL_REPO, paths=["file-a.txt"])

        status = await session.git.status(LOCAL_REPO)
        file_a = [f for f in status.files if f.path == "file-a.txt"]
        assert len(file_a) == 1
        assert file_a[0].index_status == "?"
        file_b = [f for f in status.files if f.path == "file-b.txt"]
        assert len(file_b) == 1
        assert file_b[0].index_status == "A"

        await session.git.reset(LOCAL_REPO, mode="hard")
        await session.command.execute_command(
            f"rm -f {LOCAL_REPO}/file-a.txt {LOCAL_REPO}/file-b.txt", 10000
        )
        print("[18/19] reset --paths OK")

        # ---------------------------------------------------------------
        # 19. clone (network-dependent)
        # ---------------------------------------------------------------
        try:
            clone_result = await session.git.clone(
                REPO_URL, depth=1, timeout_ms=600000
            )
            assert clone_result.path == "dingtalk-openclaw-connector"

            status = await session.git.status(clone_result.path)
            assert status.is_clean

            log_result = await session.git.log(clone_result.path, max_count=3)
            assert len(log_result.entries) > 0
            print(f"[19/19] clone OK -> {clone_result.path}")
        except Exception as clone_error:
            network_keywords = [
                "GnuTLS",
                "TLS",
                "unable to access",
                "timed out",
                "RPC",
                "HTTP2",
                "curl",
                "framing layer",
                "flush",
            ]
            msg = str(clone_error)
            if any(kw in msg for kw in network_keywords):
                print(f"[19/19] clone skipped (network issue): {msg}")
            else:
                raise

    finally:
        # Session cleanup handled by make_session fixture
        pass


@pytest.mark.asyncio
async def test_git_error_not_a_repo(make_session):
    """Verify GitNotARepoError when status is called on a non-repo path."""
    params = CreateSessionParams(image_id=IMAGE_ID)
    lc = await make_session(params=params)
    session = lc._result.session
    try:
        with pytest.raises(GitNotARepoError):
            await session.git.status("/tmp")
        print("GitNotARepoError raised as expected")
    finally:
        pass


@pytest.mark.asyncio
async def test_git_error_empty_commit(make_session):
    """Verify GitError when committing with no staged changes."""
    params = CreateSessionParams(image_id=IMAGE_ID)
    lc = await make_session(params=params)
    session = lc._result.session
    try:
        repo_path = "/tmp/test-empty-commit"
        await session.command.execute_command(f"mkdir -p {repo_path}", 10000)
        await session.git.init(repo_path)
        await session.git.configure_user(repo_path, "Test", "test@test.com")
        with pytest.raises(GitError):
            await session.git.commit(repo_path, "empty commit")
        print("GitError raised for empty commit as expected")
    finally:
        pass
