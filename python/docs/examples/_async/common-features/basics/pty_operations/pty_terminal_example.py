# ci-stable
"""PTY Terminal Example

Demonstrates interactive PTY usage:
- Create a PTY with on_data output handling
- Send shell input (echo)
- Resize the terminal and verify dimensions
- List active PTY sessions
- Disconnect locally and reconnect to the same server-side PTY
- Kill a PTY process and read exit code -9
- Exit the shell gracefully and wait for exit code 0

Uses default session image via CreateSessionParams() (no image_id).
Requires AGENTBAY_API_KEY.
"""

import asyncio
import os
import sys

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    if not os.environ.get("AGENTBAY_API_KEY"):
        print("Error: Set AGENTBAY_API_KEY environment variable.")
        sys.exit(1)

    print("=== PTY Terminal Example ===\n")
    client = AsyncAgentBay()
    session = None

    try:
        session_result = await client.create(CreateSessionParams())
        if not session_result.success or session_result.session is None:
            print(f"Failed to create session: {session_result.error_message}")
            return
        session = session_result.session
        print(f"Session: {session.session_id}\n")

        # 1. Create PTY and echo
        chunks: list[bytes] = []

        def on_data(data: bytes) -> None:
            chunks.append(data)

        handle = await session.pty.create(on_data=on_data)
        print(f"1. Created PTY: {handle.pty_session_id}")
        await asyncio.sleep(1)
        await handle.send_input(b"echo 'AGENTBAY_PTY_EXAMPLE_ECHO'\r")
        await asyncio.sleep(2)
        combined = b"".join(chunks).decode("utf-8", errors="replace")
        print(f"   Echo output contains marker: {'AGENTBAY_PTY_EXAMPLE_ECHO' in combined}\n")

        # 2. Resize
        await handle.resize(120, 40)
        await asyncio.sleep(1)
        await handle.send_input(
            b'echo "cols=$(tput cols) lines=$(tput lines)"\r'
        )
        await asyncio.sleep(2)
        combined = b"".join(chunks).decode("utf-8", errors="replace")
        print(f"2. Resize to 120x40; output contains cols=120: {'cols=120' in combined}\n")

        # 3. List PTY sessions
        listed = await session.pty.list()
        ids = [s.pty_session_id for s in listed]
        print(
            f"3. List PTY sessions: count={len(listed)}, "
            f"current id present: {handle.pty_session_id in ids}\n"
        )

        # 4. Disconnect and reconnect
        pty_id = handle.pty_session_id
        handle.disconnect()
        if handle.is_connected:
            print("   Warning: expected handle disconnected after disconnect()")
        out2: list[bytes] = []

        def on_data2(data: bytes) -> None:
            out2.append(data)

        handle2 = await session.pty.connect(pty_id, on_data=on_data2)
        await asyncio.sleep(1)
        await handle2.send_input(b"echo 'AGENTBAY_PTY_EXAMPLE_RECONNECT'\r")
        await asyncio.sleep(2)
        text2 = b"".join(out2).decode("utf-8", errors="replace")
        print(
            f"4. Reconnect OK: {'AGENTBAY_PTY_EXAMPLE_RECONNECT' in text2}\n"
        )
        handle2.disconnect()

        # 5. Kill (separate PTY)
        kill_h = await session.pty.create()
        await asyncio.sleep(1)
        await kill_h.kill()
        kill_code = await kill_h.wait(timeout_s=10)
        print(f"5. Kill exit code: {kill_code} (expected -9)\n")

        # 6. Exit with wait
        exit_h = await session.pty.create()
        await asyncio.sleep(1)
        await exit_h.send_input(b"exit\r")
        exit_code = await exit_h.wait(timeout_s=10)
        print(f"6. Shell exit code: {exit_code} (expected 0)")
        print("\n=== Completed ===")

    finally:
        if session is not None:
            await client.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
