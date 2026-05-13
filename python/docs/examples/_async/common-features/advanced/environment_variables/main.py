"""
ci-stable

Example demonstrating environment variables management with AgentBay SDK.

This example shows how to:
- Set environment variables in a session
- Get environment variables
- Use environment variables in commands
- Pass environment variables to scripts
- Manage environment variable persistence
"""

import asyncio
import os

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def set_environment_variable(session, var_name: str, var_value: str):
    """Set an environment variable."""
    print(f"\n🔧 Setting environment variable: {var_name}={var_value}")
    
    command = f"export {var_name}='{var_value}' && echo ${var_name}"
    result = await session.command.execute_command(command)
    
    if result.success:
        print(f"✅ Variable set: {result.output.strip()}")
    else:
        print(f"❌ Failed to set variable: {result.error_message}")


async def get_environment_variable(session, var_name: str):
    """Get an environment variable."""
    print(f"\n🔍 Getting environment variable: {var_name}")
    
    command = f"echo ${var_name}"
    result = await session.command.execute_command(command)
    
    if result.success:
        value = result.output.strip()
        print(f"✅ {var_name}={value}")
        return value
    else:
        print(f"❌ Failed to get variable: {result.error_message}")
        return None


async def list_all_environment_variables(session):
    """List all environment variables."""
    print("\n📋 Listing all environment variables...")
    
    command = "env | sort"
    result = await session.command.execute_command(command)
    
    if result.success:
        env_vars = result.output.strip().split('\n')
        print(f"✅ Found {len(env_vars)} environment variables")
        for var in env_vars[:10]:  # Show first 10
            print(f"   {var}")
        if len(env_vars) > 10:
            print(f"   ... and {len(env_vars) - 10} more")
    else:
        print(f"❌ Failed to list variables: {result.error_message}")


async def use_env_in_script(session):
    """Create and run a script that uses environment variables."""
    print("\n📜 Creating and running a script with environment variables...")
    
    # Create a script that uses environment variables
    script_content = """#!/bin/bash
echo "Application: $APP_NAME"
echo "Version: $APP_VERSION"
echo "Environment: $APP_ENV"
echo "Debug Mode: $DEBUG"
"""
    
    # Write script to file
    write_result = await session.file_system.write_file("/tmp/env_script.sh", script_content)
    if not write_result.success:
        print(f"❌ Failed to write script: {write_result.error_message}")
        return
    
    # Make script executable
    chmod_result = await session.command.execute_command("chmod +x /tmp/env_script.sh")
    if not chmod_result.success:
        print(f"❌ Failed to make script executable: {chmod_result.error_message}")
        return
    
    # Run script with environment variables
    command = """
export APP_NAME="AgentBay SDK"
export APP_VERSION="1.0.0"
export APP_ENV="production"
export DEBUG="true"
/tmp/env_script.sh
"""
    
    result = await session.command.execute_command(command)
    if result.success:
        print("✅ Script output:")
        print(result.output)
    else:
        print(f"❌ Script execution failed: {result.error_message}")


async def demonstrate_env_persistence(session):
    """Demonstrate environment variable persistence across commands."""
    print("\n🔄 Demonstrating environment variable persistence...")
    
    # Set variable in one command
    print("  Setting variable in first command...")
    result1 = await session.command.execute_command("export TEST_VAR='persistent_value'")
    
    # Try to access in another command (will not persist by default)
    print("  Trying to access in second command...")
    result2 = await session.command.execute_command("echo $TEST_VAR")
    
    if result2.success:
        value = result2.output.strip()
        if value:
            print(f"  ✅ Variable persisted: {value}")
        else:
            print("  ⚠️  Variable did not persist (expected behavior)")
            print("  💡 Tip: Use a single command or script for persistent variables")
    
    # Demonstrate workaround: use single command
    print("\n  Using single command for persistence...")
    result3 = await session.command.execute_command(
        "export TEST_VAR='persistent_value' && echo $TEST_VAR"
    )
    if result3.success:
        print(f"  ✅ Variable accessible in same command: {result3.output.strip()}")


async def main():
    """Main function demonstrating environment variables management."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    
    try:
        print("=" * 60)
        print("Environment Variables Management Example")
        print("=" * 60)
        
        # Create session
        print("\nCreating session...")
        params = CreateSessionParams(image_id="linux_latest")
        result = await agent_bay.create(params)
        
        if not result.success or not result.session:
            print(f"❌ Failed to create session: {result.error_message}")
            return
        
        session = result.session
        print(f"✅ Session created: {session.session_id}")
        
        # Example 1: List all environment variables
        print("\n" + "=" * 60)
        print("Example 1: List All Environment Variables")
        print("=" * 60)
        
        await list_all_environment_variables(session)
        
        # Example 2: Get specific environment variables
        print("\n" + "=" * 60)
        print("Example 2: Get Specific Environment Variables")
        print("=" * 60)
        
        await get_environment_variable(session, "PATH")
        await get_environment_variable(session, "HOME")
        await get_environment_variable(session, "USER")
        
        # Example 3: Set and use environment variables
        print("\n" + "=" * 60)
        print("Example 3: Set and Use Environment Variables")
        print("=" * 60)
        
        await set_environment_variable(session, "MY_API_KEY", "secret_key_123")
        await set_environment_variable(session, "MY_APP_NAME", "Test Application")
        
        # Example 4: Use environment variables in scripts
        print("\n" + "=" * 60)
        print("Example 4: Use Environment Variables in Scripts")
        print("=" * 60)
        
        await use_env_in_script(session)
        
        # Example 5: Environment variable persistence
        print("\n" + "=" * 60)
        print("Example 5: Environment Variable Persistence")
        print("=" * 60)
        
        await demonstrate_env_persistence(session)
        
        print("\n✅ Environment variables management examples completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if session:
            print("\n🧹 Cleaning up session...")
            await agent_bay.delete(session)
            print("✅ Session deleted")


if __name__ == "__main__":
    asyncio.run(main())

