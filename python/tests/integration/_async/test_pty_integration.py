import asyncio
import os
import pytest

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

IMAGE_ID = "imgc-0ab5takiyxtc4h5bn"


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def agent_bay():
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY not set")
    from agentbay import AsyncAgentBay
    return AsyncAgentBay()


@pytest.fixture
async def pty_session(agent_bay):
    from agentbay import CreateSessionParams
    result = await agent_bay.create(CreateSessionParams(image_id=IMAGE_ID))
    assert result.success, f"Failed to create session: {result}"
    session = result.session
    yield session
    try:
        await session.delete()
    except Exception as e:
        print(f"Warning: failed to delete session: {e}")


class TestPtyCreateAndEcho:
    async def test_create_and_echo(self, pty_session):
        """Create PTY, run echo, verify output."""
        output_chunks = []

        def on_data(data: bytes):
            output_chunks.append(data)

        handle = await pty_session.pty.create(on_data=on_data)
        assert handle.pty_session_id
        assert handle.is_connected

        await asyncio.sleep(1)

        await handle.send_input(b"echo 'PTY_TEST_OK_98765'\r")
        await asyncio.sleep(2)

        combined = b"".join(output_chunks).decode("utf-8", errors="replace")
        assert "PTY_TEST_OK_98765" in combined

        handle.disconnect()


class TestPtyCtrlC:
    async def test_ctrl_c(self, pty_session):
        """Send Ctrl+C to interrupt a running command."""
        output_chunks = []

        def on_data(data: bytes):
            output_chunks.append(data)

        handle = await pty_session.pty.create(on_data=on_data)
        await asyncio.sleep(1)

        await handle.send_input(b"sleep 100\r")
        await asyncio.sleep(1)

        await handle.send_input(b"\x03")
        await asyncio.sleep(2)

        combined = b"".join(output_chunks).decode("utf-8", errors="replace")
        assert "^C" in combined or "$" in combined

        handle.disconnect()


class TestPtyResize:
    async def test_resize(self, pty_session):
        """Resize terminal to 120x40."""
        handle = await pty_session.pty.create()
        await asyncio.sleep(1)

        await handle.resize(120, 40)
        await asyncio.sleep(1)

        handle.disconnect()


class TestPtyList:
    async def test_list(self, pty_session):
        """List should include the created PTY."""
        handle = await pty_session.pty.create()
        await asyncio.sleep(1)

        sessions = await pty_session.pty.list()
        ids = [s.pty_session_id for s in sessions]
        assert handle.pty_session_id in ids

        handle.disconnect()


class TestPtyConnect:
    async def test_disconnect_and_reconnect(self, pty_session):
        """Disconnect then reconnect, verify I/O works."""
        output1 = []
        handle1 = await pty_session.pty.create(
            on_data=lambda d: output1.append(d)
        )
        await asyncio.sleep(1)

        await handle1.send_input(b"echo 'BEFORE_DISCONNECT'\r")
        await asyncio.sleep(1)

        pty_id = handle1.pty_session_id
        handle1.disconnect()
        assert not handle1.is_connected

        output2 = []
        handle2 = await pty_session.pty.connect(
            pty_id, on_data=lambda d: output2.append(d)
        )
        assert handle2.is_connected

        await handle2.send_input(b"echo 'AFTER_RECONNECT'\r")
        await asyncio.sleep(2)

        combined = b"".join(output2).decode("utf-8", errors="replace")
        assert "AFTER_RECONNECT" in combined

        handle2.disconnect()


class TestPtyExit:
    async def test_exit_event(self, pty_session):
        """Send exit, verify pty.exit event and wait() returns exit code 0."""
        handle = await pty_session.pty.create()
        await asyncio.sleep(1)

        await handle.send_input(b"exit\r")
        exit_code = await handle.wait(timeout_s=10)
        assert exit_code == 0
        assert handle.exit_code == 0
        assert not handle.is_connected


class TestPtyKill:
    async def test_kill(self, pty_session):
        """Kill PTY and verify exit code is -9."""
        handle = await pty_session.pty.create()
        await asyncio.sleep(1)

        await handle.kill()
        exit_code = await handle.wait(timeout_s=10)
        assert exit_code == -9


class TestPtyMultiple:
    async def test_multiple_ptys(self, pty_session):
        """Create 2 PTYs, each works independently."""
        output1 = []
        output2 = []
        handle1 = await pty_session.pty.create(
            on_data=lambda d: output1.append(d)
        )
        handle2 = await pty_session.pty.create(
            on_data=lambda d: output2.append(d)
        )
        await asyncio.sleep(1)

        await handle1.send_input(b"echo 'FROM_PTY_1'\r")
        await handle2.send_input(b"echo 'FROM_PTY_2'\r")
        await asyncio.sleep(2)

        combined1 = b"".join(output1).decode("utf-8", errors="replace")
        combined2 = b"".join(output2).decode("utf-8", errors="replace")
        assert "FROM_PTY_1" in combined1
        assert "FROM_PTY_2" in combined2

        handle1.disconnect()
        handle2.disconnect()


class TestPtyDisconnectError:
    async def test_send_input_after_disconnect_raises(self, pty_session):
        """Send input after disconnect should raise PtyNotConnectedError."""
        from agentbay import PtyNotConnectedError

        handle = await pty_session.pty.create()
        await asyncio.sleep(1)

        handle.disconnect()
        assert not handle.is_connected

        with pytest.raises(PtyNotConnectedError):
            await handle.send_input(b"should fail\r")


class TestPtyResizeVerify:
    async def test_resize_columns_lines(self, pty_session):
        """Resize terminal and verify COLUMNS/LINES via tput."""
        output_chunks = []

        def on_data(data: bytes):
            output_chunks.append(data)

        handle = await pty_session.pty.create(
            cols=80, rows=24, on_data=on_data
        )
        await asyncio.sleep(1)

        await handle.resize(150, 50)
        await asyncio.sleep(1)

        await handle.send_input(b"tput cols; tput lines\r")
        await asyncio.sleep(2)

        combined = b"".join(output_chunks).decode("utf-8", errors="replace")
        assert "150" in combined
        assert "50" in combined

        handle.disconnect()
