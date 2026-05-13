"""
ci-stable

Mobile App Operations Example

This example demonstrates:
1. Launching mobile apps
2. App interaction
3. App state management
"""

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate mobile app operations."""
    print("=== Mobile App Operations Example ===\n")

    client = AsyncAgentBay()
    session = None

    try:
        # Create a mobile session
        print("Creating mobile session...")
        session_result = await client.create(
            CreateSessionParams(image_id="mobile_latest")
        )
        session = session_result.session
        print(f"Session created: {session.session_id}")

        # Get ADB connection info
        print("\n1. Getting ADB connection info...")
        # Note: This would use session.mobile.get_adb_url() in real implementation
        print("ADB connection available through mobile module")

        # List installed packages
        print("\n2. Listing installed packages...")
        result = await session.command.execute_command("pm list packages | head -10")
        print(f"Installed packages (first 10):\n{result.output}")

        # Get device info
        print("\n3. Getting device information...")
        result = await session.command.execute_command("getprop ro.product.model")
        print(f"Device model: {result.output}")

        result = await session.command.execute_command("getprop ro.build.version.release")
        print(f"Android version: {result.output}")

        # Check screen status
        print("\n4. Checking screen status...")
        result = await session.command.execute_command("dumpsys power | grep 'Display Power'")
        print(f"Screen status:\n{result.output}")

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

