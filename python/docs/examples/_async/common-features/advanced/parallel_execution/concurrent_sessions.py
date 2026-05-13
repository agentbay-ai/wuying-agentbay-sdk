"""
ci-stable
Concurrent Sessions Example

This example demonstrates:
1. Creating multiple sessions concurrently
2. Running operations in parallel
3. Managing concurrent session lifecycle
4. Coordinating results from multiple sessions
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def run_task_in_session(client, task_id, command):
    """Run a task in a dedicated session."""
    print(f"Task {task_id}: Starting...")
    session = None

    try:
        # Create session
        session_result = await client.create(
            CreateSessionParams(image_id="linux_latest")
        )
        session = session_result.session
        print(f"Task {task_id}: Session created ({session.session_id})")

        # Execute command
        result = await session.command.execute_command(command)
        print(f"Task {task_id}: Command executed")

        return {
            "task_id": task_id,
            "session_id": session.session_id,
            "output": result.output,
            "success": result.success
        }

    except Exception as e:
        print(f"Task {task_id}: Error - {str(e)}")
        return {
            "task_id": task_id,
            "error": str(e),
            "success": False
        }

    finally:
        if session:
            await client.delete(session)
            print(f"Task {task_id}: Session closed")


async def main():
    """Demonstrate concurrent session management."""
    print("=== Concurrent Sessions Example ===\n")

    # Initialize AgentBay client
    client = AsyncAgentBay()

    try:
        # Define tasks to run concurrently
        tasks = [
            ("1", "echo 'Task 1' && sleep 1 && date"),
            ("2", "echo 'Task 2' && sleep 1 && hostname"),
            ("3", "echo 'Task 3' && sleep 1 && pwd"),
            ("4", "echo 'Task 4' && sleep 1 && whoami"),
            ("5", "echo 'Task 5' && sleep 1 && uname -a"),
        ]

        print(f"Running {len(tasks)} tasks concurrently...\n")

        # Run all tasks concurrently
        results = await asyncio.gather(
            *[run_task_in_session(client, task_id, cmd) for task_id, cmd in tasks]
        )

        # Display results
        print("\n=== Results ===\n")
        for result in results:
            print(f"Task {result['task_id']}:")
            if result['success']:
                print(f"  Output: {result['output'].strip()}")
            else:
                print(f"  Error: {result.get('error', 'Unknown error')}")
            print()

        print("=== Example completed successfully ===")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

