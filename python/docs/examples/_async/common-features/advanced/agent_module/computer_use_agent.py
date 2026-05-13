"""
ci-stable
Basic example of using the Agent module to execute tasks.
This example demonstrates:
- Creating a session with Agent capabilities
- Executing a simple task using natural language
- Handling task results
"""

import asyncio
import os
from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams

from agentbay import get_logger

logger = get_logger("agentbay-agent-example")


async def main():
    from dotenv import load_dotenv
    load_dotenv()
    # Get API key from environment variable
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        logger.error("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return

    # Initialize AgentBay client
    logger.info("Initializing AgentBay client...")
    agent_bay = AsyncAgentBay(api_key=api_key)

    # Create a session
    logger.info("Creating a new session...")
    params = CreateSessionParams()
    params.image_id = "windows_latest"
    session_result = await agent_bay.create(params)

    if session_result.success:
        session = session_result.session
        logger.info(f"🆔 Session created with ID: {session.session_id}")

        # Execute a task using the Agent
        task_description = "创建一个word文件，输入“无影Agentbay”,保存并关闭。"
        logger.info(f"🚀 Executing task: {task_description}")

        execution_result = await session.agent.computer.execute_task_and_wait(
            task_description, timeout=150
        )

        if execution_result.success:
            logger.info("✅ Task completed successfully!")
            logger.info(f"✅ Task ID: {execution_result.task_id}")
            logger.info(f"✅ Task status: {execution_result.task_status}")
            logger.info(f"✅ Task result: {execution_result.task_result}")
        else:
            logger.warning(f"⚠️ Task failed: {execution_result.error_message}")
            if execution_result.task_id:
                logger.info(f"Task ID: {execution_result.task_id}")

        # Clean up - delete the session
        delete_result = await agent_bay.delete(session)
        if delete_result.success:
            logger.info("Session deleted successfully")
        else:
            logger.warning(f"Failed to delete session: {delete_result.error_message}")
    else:
        logger.warning(f"Failed to create session: {session_result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())
