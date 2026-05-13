"""
ci-stable
Environment Setup Example
"""
import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    print("=== Environment Setup ===\n")
    client = AsyncAgentBay()
    session = None

    try:
        session_result = await client.create(CreateSessionParams(image_id="linux_latest"))
        session = session_result.session

        # Set environment variable
        result = await session.command.execute_command("export MY_VAR='test' && echo $MY_VAR")
        print(f"1. Set var: {result.output}")

        # Check PATH
        result = await session.command.execute_command("echo $PATH | head -c 100")
        print(f"2. PATH: {result.output}...")

        # Check HOME
        result = await session.command.execute_command("echo $HOME")
        print(f"3. HOME: {result.output}")

        print("\n=== Completed ===")

    finally:
        if session:
            await client.delete(session)


if __name__ == "__main__":
    asyncio.run(main())

