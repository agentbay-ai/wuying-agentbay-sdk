"""
ci-stable
Python Development Environment Example

This example demonstrates:
1. Setting up a Python development environment
2. Installing packages with pip
3. Creating and running Python scripts
4. Managing virtual environments
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate Python development environment setup."""
    print("=== Python Development Environment Example ===\n")

    # Initialize AgentBay client
    client = AsyncAgentBay()
    session = None

    try:
        # Create a session
        print("Creating session...")
        session_result = await client.create(
            CreateSessionParams(
                image_id="linux_latest"
            )
        )
        session = session_result.session
        print(f"Session created: {session.session_id}")

        # Check Python version
        print("\n1. Checking Python version...")
        result = await session.command.execute_command("python3 --version")
        print(f"Python version: {result.output}")

        # Create a Python script
        print("\n2. Creating a Python script...")
        script_content = """#!/usr/bin/env python3
import sys
import json

def main():
    data = {
        "message": "Hello from AgentBay!",
        "python_version": sys.version,
        "platform": sys.platform
    }
    print(json.dumps(data, indent=2))

if __name__ == "__main__":
    main()
"""
        await session.file_system.write_file("/tmp/hello.py", script_content)
        print("Script created: /tmp/hello.py")

        # Run the Python script
        print("\n3. Running the Python script...")
        result = await session.command.execute_command("python3 /tmp/hello.py")
        print(f"Script output:\n{result.output}")

        # Install a package with pip
        print("\n4. Installing requests package...")
        result = await session.command.execute_command("pip3 install requests --quiet")
        if result.success:
            print("Package installed successfully")

        # Create a script that uses the installed package
        print("\n5. Creating a script that uses requests...")
        requests_script = """#!/usr/bin/env python3
import requests
import json

def main():
    try:
        response = requests.get('https://httpbin.org/json')
        print("Status code:", response.status_code)
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
"""
        await session.file_system.write_file("/tmp/test_requests.py", requests_script)
        print("Script created: /tmp/test_requests.py")

        # Run the requests script
        print("\n6. Running the requests script...")
        result = await session.command.execute_command("python3 /tmp/test_requests.py")
        print(f"Script output:\n{result.output}")

        # List installed packages
        print("\n7. Listing installed packages...")
        result = await session.command.execute_command("pip3 list | head -20")
        print(f"Installed packages:\n{result.output}")

        # Create a requirements.txt
        print("\n8. Creating requirements.txt...")
        requirements = "requests>=2.28.0\n"
        await session.file_system.write_file("/tmp/requirements.txt", requirements)
        print("requirements.txt created")

        # Verify the file
        content = await session.file_system.read_file("/tmp/requirements.txt")
        print(f"requirements.txt content:\n{content.content}")

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

    finally:
        # Clean up
        if session:
            print("\nCleaning up session...")
            await client.delete(session)
            print("Session closed")


if __name__ == "__main__":
    asyncio.run(main())

