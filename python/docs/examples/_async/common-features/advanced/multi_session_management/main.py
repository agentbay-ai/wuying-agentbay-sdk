"""
ci-stable
Example demonstrating multi-session management with AgentBay SDK.

This example shows how to:
- Manage multiple sessions with different configurations
- Switch between sessions
- Share data between sessions
- Monitor session states
- Coordinate operations across sessions
"""

import asyncio
import os
from typing import Dict, Any, List

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


class SessionManager:
    """Manager for multiple AgentBay sessions."""
    
    def __init__(self, agent_bay: AsyncAgentBay):
        self.agent_bay = agent_bay
        self.sessions: Dict[str, Any] = {}
        self.session_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def create_session(self, name: str, image_id: str, labels: Dict[str, str] = None):
        """Create and register a new session."""
        print(f"Creating session '{name}' with image '{image_id}'...")
        
        params = CreateSessionParams(
            image_id=image_id,
            labels=labels or {"name": name}
        )
        
        result = await self.agent_bay.create(params)
        
        if result.success and result.session:
            self.sessions[name] = result.session
            self.session_metadata[name] = {
                "session_id": result.session.session_id,
                "image_id": image_id,
                "created_at": asyncio.get_event_loop().time(),
                "labels": labels or {}
            }
            print(f"✅ Session '{name}' created: {result.session.session_id}")
            return result.session
        else:
            print(f"❌ Failed to create session '{name}': {result.error_message}")
            return None
    
    def get_session(self, name: str):
        """Get a session by name."""
        return self.sessions.get(name)
    
    def list_sessions(self) -> List[str]:
        """List all managed session names."""
        return list(self.sessions.keys())
    
    async def execute_on_session(self, name: str, command: str):
        """Execute a command on a specific session."""
        session = self.get_session(name)
        if not session:
            print(f"❌ Session '{name}' not found")
            return None
        
        result = await session.command.execute_command(command)
        if result.success:
            print(f"✅ [{name}] Command executed: {result.output.strip()[:50]}")
            return result.output
        else:
            print(f"❌ [{name}] Command failed: {result.error_message}")
            return None
    
    async def transfer_file_between_sessions(
        self,
        source_name: str,
        dest_name: str,
        file_path: str
    ):
        """Transfer a file from one session to another."""
        source_session = self.get_session(source_name)
        dest_session = self.get_session(dest_name)
        
        if not source_session or not dest_session:
            print("❌ Source or destination session not found")
            return False
        
        print(f"Transferring file '{file_path}' from '{source_name}' to '{dest_name}'...")
        
        # Read from source
        read_result = await source_session.file_system.read_file(file_path)
        if not read_result.success:
            print(f"❌ Failed to read from source: {read_result.error_message}")
            return False
        
        # Write to destination
        write_result = await dest_session.file_system.write_file(file_path, read_result.content)
        if not write_result.success:
            print(f"❌ Failed to write to destination: {write_result.error_message}")
            return False
        
        print(f"✅ File transferred successfully")
        return True
    
    async def cleanup(self):
        """Clean up all managed sessions."""
        print(f"\n🧹 Cleaning up {len(self.sessions)} sessions...")
        
        for name, session in self.sessions.items():
            try:
                result = await self.agent_bay.delete(session)
                if result.success:
                    print(f"✅ Session '{name}' deleted")
                else:
                    print(f"❌ Failed to delete session '{name}': {result.error_message}")
            except Exception as e:
                print(f"❌ Error deleting session '{name}': {e}")
        
        self.sessions.clear()
        self.session_metadata.clear()


async def main():
    """Main function demonstrating multi-session management."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    manager = SessionManager(agent_bay)
    
    try:
        print("=" * 60)
        print("Multi-Session Management Example")
        print("=" * 60)
        
        # Create multiple sessions with different configurations
        await manager.create_session(
            "dev-session",
            "linux_latest",
            {"environment": "development", "purpose": "testing"}
        )
        
        await manager.create_session(
            "prod-session",
            "linux_latest",
            {"environment": "production", "purpose": "deployment"}
        )
        
        await manager.create_session(
            "test-session",
            "linux_latest",
            {"environment": "testing", "purpose": "qa"}
        )
        
        print(f"\n📋 Active sessions: {manager.list_sessions()}")
        
        # Execute commands on different sessions
        print("\n" + "=" * 60)
        print("Executing Commands on Different Sessions")
        print("=" * 60)
        
        await manager.execute_on_session("dev-session", "echo 'Development environment'")
        await manager.execute_on_session("prod-session", "echo 'Production environment'")
        await manager.execute_on_session("test-session", "echo 'Testing environment'")
        
        # Create a file in one session
        print("\n" + "=" * 60)
        print("File Transfer Between Sessions")
        print("=" * 60)
        
        dev_session = manager.get_session("dev-session")
        if dev_session:
            content = "This is a shared configuration file"
            write_result = await dev_session.file_system.write_file("/tmp/config.txt", content)
            if write_result.success:
                print("✅ File created in dev-session")
                
                # Transfer to other sessions
                await manager.transfer_file_between_sessions(
                    "dev-session",
                    "prod-session",
                    "/tmp/config.txt"
                )
                
                await manager.transfer_file_between_sessions(
                    "dev-session",
                    "test-session",
                    "/tmp/config.txt"
                )
        
        # Verify file exists in all sessions
        print("\n" + "=" * 60)
        print("Verifying File in All Sessions")
        print("=" * 60)
        
        for session_name in manager.list_sessions():
            await manager.execute_on_session(session_name, "cat /tmp/config.txt")
        
        print("\n✅ Multi-session management example completed")
        
    except Exception as e:
        print(f"\n❌ Error in main: {e}")
        
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

