#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ci-stable
Example demonstrating session pause and resume functionality with AgentBay SDK.
This example shows how to:
- Create a session
- Pause a session to save resources
- Resume a session to continue work
- Use both synchronous and asynchronous pause/resume methods
"""

import os
import time
import asyncio

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams
from dotenv import load_dotenv
load_dotenv()

async def main_sync():
    """Demonstrate synchronous pause and resume operations."""
    print("=== Synchronous Pause/Resume Example ===")

    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="linux_latest",  # Specify the image ID
        labels={"example": "pause_resume_sync", "environment": "demo"}
    )
    session_result = await agent_bay.create(params)

    if not session_result.success:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"Session created with ID: {session.session_id}")
    print(f"Request ID: {session_result.request_id}")

    try:
        # Run some initial commands to establish work
        print("\nRunning initial setup commands...")
        cmd_result = await session.command.execute_command("echo 'Initial setup complete' && sleep 2")
        if cmd_result.success:
            print(f"Setup output: {cmd_result.output}")
        else:
            print(f"Setup failed: {cmd_result.error_message}")

        # Pause the session
        print("\nPausing the session...")
        pause_result = await agent_bay.beta_pause(session, timeout=300)  # 5 minute timeout
        if pause_result.success:
            print(f"Session paused successfully with status: {pause_result.status}")
            print(f"Request ID: {pause_result.request_id}")
        else:
            print(f"Failed to pause session: {pause_result.error_message}")
            return

        # Simulate some time passing while session is paused (e.g., waiting for user input)
        print("\nSession is paused. Simulating work being done elsewhere...")
        await asyncio.sleep(5)
        print("Work completed. Resuming session...")

        # Resume the session
        print("\nResuming the session...")
        resume_result = await agent_bay.beta_resume(session, timeout=300)  # 5 minute timeout
        if resume_result.success:
            print(f"Session resumed successfully with status: {resume_result.status}")
            print(f"Request ID: {resume_result.request_id}")
        else:
            print(f"Failed to resume session: {resume_result.error_message}")
            return

        # Run commands after resume to verify session is working
        print("\nRunning commands after resume...")
        cmd_result = await session.command.execute_command("echo 'Session is active again' && date")
        if cmd_result.success:
            print(f"Post-resume output: {cmd_result.output}")
        else:
            print(f"Post-resume command failed: {cmd_result.error_message}")

    finally:
        # Clean up: Delete the session
        print("\nCleaning up: Deleting the session...")
        delete_result = await agent_bay.delete(session)
        if delete_result.success:
            print(f"Session deleted successfully. Request ID: {delete_result.request_id}")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")


async def main_async():
    """Demonstrate asynchronous pause and resume operations."""
    print("\n=== Asynchronous Pause/Resume Example ===")

    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="linux_latest",  # Specify the image ID
        labels={"example": "pause_resume_async", "environment": "demo"}
    )
    session_result = await agent_bay.create(params)

    if not session_result.success:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"Session created with ID: {session.session_id}")
    print(f"Request ID: {session_result.request_id}")

    try:
        # Run some initial commands to establish work
        print("\nRunning initial setup commands...")
        cmd_result = await session.command.execute_command("echo 'Async initial setup complete' && sleep 2")
        if cmd_result.success:
            print(f"Setup output: {cmd_result.output}")
        else:
            print(f"Setup failed: {cmd_result.error_message}")

        # Pause the session asynchronously
        print("\nPausing the session asynchronously...")
        pause_result = await agent_bay.beta_pause_async(session)
        if pause_result.success:
            print(f"Session pause request submitted successfully")
            print(f"Request ID: {pause_result.request_id}")
        else:
            print(f"Failed to pause session: {pause_result.error_message}")
            return

        # Wait for pause to complete
        print("Waiting for session to pause...")
        await asyncio.sleep(1)

        # Simulate some time passing while session is paused
        print("\nSession is paused. Simulating async work being done elsewhere...")
        await asyncio.sleep(2)
        print("Async work completed. Resuming session...")

        # Resume the session asynchronously
        print("\nResuming the session asynchronously...")
        resume_result = await agent_bay.beta_resume_async(session)
        if resume_result.success:
            print(f"Session resume request submitted successfully")
            print(f"Request ID: {resume_result.request_id}")
        else:
            print(f"Failed to resume session: {resume_result.error_message}")
            return

        # Wait for resume to complete
        print("Waiting for session to resume...")
        await asyncio.sleep(2)

        # Run commands after resume to verify session is working
        print("\nRunning commands after resume...")
        cmd_result = await session.command.execute_command("echo 'Async session is active again' && date")
        if cmd_result.success:
            print(f"Post-resume output: {cmd_result.output}")
        else:
            print(f"Post-resume command failed: {cmd_result.error_message}")

    finally:
        # Clean up: Delete the session
        print("\nCleaning up: Deleting the session...")
        delete_result = await agent_bay.delete(session)
        if delete_result.success:
            print(f"Session deleted successfully. Request ID: {delete_result.request_id}")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")


async def main_direct():
    """Demonstrate direct pause and resume operations on session object."""
    print("\n=== Direct Session Pause/Resume Example ===")

    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    print("Initializing AgentBay client...")
    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    print("Creating a new session...")
    params = CreateSessionParams(
        image_id="linux_latest",  # Specify the image ID
        labels={"example": "pause_resume_direct", "environment": "demo"}
    )
    session_result = await agent_bay.create(params)

    if not session_result.success:
        print(f"Failed to create session: {session_result.error_message}")
        return

    session = session_result.session
    print(f"Session created with ID: {session.session_id}")
    print(f"Request ID: {session_result.request_id}")

    try:
        # Run some initial commands to establish work
        print("\nRunning initial setup commands...")
        cmd_result = await session.command.execute_command("echo 'Direct pause/resume setup complete' && sleep 2")
        if cmd_result.success:
            print(f"Setup output: {cmd_result.output}")
        else:
            print(f"Setup failed: {cmd_result.error_message}")

        # Pause the session directly using session methods
        print("\nPausing the session directly...")
        pause_result = await session.beta_pause(timeout=300)  # 5 minute timeout
        if pause_result.success:
            print(f"Session paused successfully with status: {pause_result.status}")
            print(f"Request ID: {pause_result.request_id}")
        else:
            print(f"Failed to pause session: {pause_result.error_message}")
            return

        # Simulate some time passing while session is paused
        print("\nSession is paused. Simulating work being done elsewhere...")
        await asyncio.sleep(5)
        print("Work completed. Resuming session...")

        # Resume the session directly using session methods
        print("\nResuming the session directly...")
        resume_result = await session.beta_resume(timeout=300)  # 5 minute timeout
        if resume_result.success:
            print(f"Session resumed successfully with status: {resume_result.status}")
            print(f"Request ID: {resume_result.request_id}")
        else:
            print(f"Failed to resume session: {resume_result.error_message}")
            return

        # Run commands after resume to verify session is working
        print("\nRunning commands after resume...")
        cmd_result = await session.command.execute_command("echo 'Direct session is active again' && date")
        if cmd_result.success:
            print(f"Post-resume output: {cmd_result.output}")
        else:
            print(f"Post-resume command failed: {cmd_result.error_message}")

    finally:
        # Clean up: Delete the session
        print("\nCleaning up: Deleting the session...")
        delete_result = await agent_bay.delete(session)
        if delete_result.success:
            print(f"Session deleted successfully. Request ID: {delete_result.request_id}")
        else:
            print(f"Failed to delete session: {delete_result.error_message}")



if __name__ == "__main__":
    asyncio.run(main_sync())
    # main_direct()
    # asyncio.run(main_async())