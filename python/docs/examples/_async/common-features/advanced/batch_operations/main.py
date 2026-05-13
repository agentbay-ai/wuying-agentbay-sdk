"""
ci-stable

Example demonstrating batch operations with AgentBay SDK.

This example shows how to:
- Create multiple sessions in parallel
- Execute commands across multiple sessions
- Perform batch file operations
- Aggregate results from multiple sessions
- Clean up multiple sessions efficiently
"""

import asyncio
import os
from typing import List, Dict, Any

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def create_sessions_batch(
    agent_bay: AsyncAgentBay,
    count: int,
    image_id: str = "linux_latest"
) -> List[Any]:
    """Create multiple sessions in parallel."""
    print(f"Creating {count} sessions in parallel...")
    
    params = CreateSessionParams(
        image_id=image_id,
        labels={"batch": "example", "purpose": "batch_operations"}
    )
    
    # Create all sessions concurrently
    tasks = [agent_bay.create(params) for _ in range(count)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    sessions = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Session {i+1} creation failed: {result}")
        elif result.success and result.session:
            print(f"✅ Session {i+1} created: {result.session.session_id}")
            sessions.append(result.session)
        else:
            print(f"❌ Session {i+1} creation failed: {result.error_message}")
    
    return sessions


async def execute_command_on_session(session, command: str, session_index: int):
    """Execute a command on a single session."""
    try:
        result = await session.command.execute_command(command)
        if result.success:
            return {
                "session_id": session.session_id,
                "session_index": session_index,
                "success": True,
                "output": result.output.strip()
            }
        else:
            return {
                "session_id": session.session_id,
                "session_index": session_index,
                "success": False,
                "error": result.error_message
            }
    except Exception as e:
        return {
            "session_id": session.session_id,
            "session_index": session_index,
            "success": False,
            "error": str(e)
        }


async def batch_execute_commands(sessions: List[Any], command: str):
    """Execute the same command on multiple sessions in parallel."""
    print(f"\nExecuting command on {len(sessions)} sessions: {command}")
    
    tasks = [
        execute_command_on_session(session, command, i)
        for i, session in enumerate(sessions)
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Print results
    successful = sum(1 for r in results if r["success"])
    print(f"\n✅ Successful: {successful}/{len(sessions)}")
    
    for result in results:
        if result["success"]:
            print(f"  Session {result['session_index']}: {result['output'][:50]}")
        else:
            print(f"  Session {result['session_index']}: ❌ {result['error']}")
    
    return results


async def batch_file_operations(sessions: List[Any]):
    """Perform file operations on multiple sessions."""
    print(f"\nPerforming file operations on {len(sessions)} sessions...")
    
    async def write_and_read(session, index):
        try:
            content = f"This is test content for session {index}"
            file_path = f"/tmp/batch_test_{index}.txt"
            
            # Write file
            write_result = await session.file_system.write_file(file_path, content)
            if not write_result.success:
                return {"session_index": index, "success": False, "error": write_result.error_message}
            
            # Read file
            read_result = await session.file_system.read_file(file_path)
            if not read_result.success:
                return {"session_index": index, "success": False, "error": read_result.error_message}
            
            # Verify content
            matches = read_result.content == content
            return {
                "session_index": index,
                "success": True,
                "content_matches": matches
            }
        except Exception as e:
            return {"session_index": index, "success": False, "error": str(e)}
    
    tasks = [write_and_read(session, i) for i, session in enumerate(sessions)]
    results = await asyncio.gather(*tasks)
    
    successful = sum(1 for r in results if r.get("success") and r.get("content_matches"))
    print(f"✅ File operations successful: {successful}/{len(sessions)}")
    
    return results


async def delete_sessions_batch(agent_bay: AsyncAgentBay, sessions: List[Any]):
    """Delete multiple sessions in parallel."""
    print(f"\n🧹 Deleting {len(sessions)} sessions...")
    
    tasks = [agent_bay.delete(session) for session in sessions]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    successful = 0
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"❌ Session {i+1} deletion failed: {result}")
        elif result.success:
            successful += 1
        else:
            print(f"❌ Session {i+1} deletion failed: {result.error_message}")
    
    print(f"✅ Successfully deleted: {successful}/{len(sessions)} sessions")


async def main():
    """Main function demonstrating batch operations."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    sessions = []
    
    try:
        print("=" * 60)
        print("Batch Operations Example")
        print("=" * 60)
        
        # Create multiple sessions
        session_count = 3
        sessions = await create_sessions_batch(agent_bay, session_count)
        
        if not sessions:
            print("❌ No sessions created, exiting")
            return
        
        print(f"\n✅ Created {len(sessions)} sessions successfully")
        
        # Execute commands in batch
        await batch_execute_commands(sessions, "hostname")
        await batch_execute_commands(sessions, "whoami")
        await batch_execute_commands(sessions, "date")
        
        # Perform batch file operations
        await batch_file_operations(sessions)
        
        print("\n✅ Batch operations completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error in main: {e}")
        
    finally:
        # Clean up all sessions
        if sessions:
            await delete_sessions_batch(agent_bay, sessions)


if __name__ == "__main__":
    asyncio.run(main())

