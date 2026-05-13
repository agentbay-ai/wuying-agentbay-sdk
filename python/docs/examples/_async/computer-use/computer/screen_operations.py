"""
ci-stable
Computer Screen Operations Example

This example demonstrates:
1. Taking screenshots using computer.beta_take_screenshot()
2. Screen resolution operations
3. Screen capture and analysis
"""

import asyncio
import os

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate computer screen operations."""
    print("=== Computer Screen Operations Example ===\n")

    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY is not set")

    client = AsyncAgentBay(api_key=api_key)
    session = None

    try:
        # Create a computer session
        print("Creating computer session...")
        session_result = await client.create(
            CreateSessionParams(image_id="linux_latest")
        )
        if not session_result.success or not session_result.session:
            raise RuntimeError(f"Failed to create session: {session_result.error_message}")

        session = session_result.session
        print(f"Session created: {session.session_id}")

        # 1. Take a screenshot
        print("\n1. Taking screenshot...")
        screenshot = await session.computer.beta_take_screenshot(format="jpg")
        if not screenshot.success:
            raise RuntimeError(f"Screenshot failed: {screenshot.error_message}")

        os.makedirs("./tmp", exist_ok=True)
        out_path = "./tmp/computer_screenshot.jpg"
        with open(out_path, "wb") as f:
            f.write(screenshot.data)

        print(
            f"Saved screenshot to: {out_path} ({len(screenshot.data)} bytes, "
            f"mime_type={screenshot.mime_type}, size={screenshot.width}x{screenshot.height})"
        )

        # 2. Get screen information via command
        print("\n2. Getting screen information...")
        result = await session.command.execute_command("xrandr --current 2>/dev/null || echo 'xrandr not available'")
        if result.success:
            print(f"Screen info:\n{result.output}")

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

    finally:
        if session:
            print("\nCleaning up session...")
            await client.delete(session)
            print("Session closed")


if __name__ == "__main__":
    asyncio.run(main())

