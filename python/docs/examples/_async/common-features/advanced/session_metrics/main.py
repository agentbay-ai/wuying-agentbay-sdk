
"""
ci-stable
Session Metrics Example

This example demonstrates how to retrieve metrics for a session.
"""
import asyncio
import json

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create(CreateSessionParams(image_id="linux_latest"))
    if not result.success:
        raise RuntimeError(result.error_message)

    session = result.session
    try:
        metrics_result = await session.get_metrics()
        if not metrics_result.success:
            raise RuntimeError(metrics_result.error_message)

        print(json.dumps(metrics_result.raw, ensure_ascii=False, indent=2))
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())


