"""
ci-stable
Mobile Beta Screenshot Example

This example demonstrates how to take a screenshot of a mobile device using the AgentBay API.
"""
import asyncio
import os

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import AgentBayError


async def _set_low_android_resolution(session) -> None:
    cmds = [
        "wm size 720x1280",
        "wm density 160",
    ]
    for cmd in cmds:
        r = await session.command.execute_command(cmd)
        if not r.success:
            raise RuntimeError(f"Command failed: {cmd} error={r.error_message}")


async def main() -> None:
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY is not set")

    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    try:
        result = await agent_bay.create(
            CreateSessionParams(image_id="mobile_latest")
        )
        if not result.success or not result.session:
            raise RuntimeError(f"Failed to create session: {result.error_message}")
        session = result.session

        await _set_low_android_resolution(session)

        os.makedirs("./tmp", exist_ok=True)

        start = await session.mobile.start_app("monkey -p com.android.settings 1")
        if not start.success:
            raise RuntimeError(f"Failed to start Settings: {start.error_message}")
        await asyncio.sleep(2)

        s1 = await session.mobile.beta_take_screenshot()
        with open("./tmp/mobile_beta_screenshot.png", "wb") as f:
            f.write(s1.data)
        print(
            f"Saved ./tmp/mobile_beta_screenshot.png ({len(s1.data)} bytes, mime_type={s1.mime_type}, type={s1.type}, size={s1.width}x{s1.height})"
        )

        try:
            s2 = await session.mobile.beta_take_long_screenshot(max_screens=2, format="png")
            with open("./tmp/mobile_beta_long_screenshot.png", "wb") as f:
                f.write(s2.data)
            print(
                f"Saved ./tmp/mobile_beta_long_screenshot.png ({len(s2.data)} bytes, mime_type={s2.mime_type}, type={s2.type}, size={s2.width}x{s2.height})"
            )
        except AgentBayError as e:
            print(f"Long screenshot failed: {e}")
    finally:
        if session is not None:
            await session.delete()


if __name__ == "__main__":
    asyncio.run(main())

