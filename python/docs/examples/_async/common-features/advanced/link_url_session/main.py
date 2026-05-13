
"""
ci-stable
Link URL Session Example

This example demonstrates how to create a session using a link URL.
"""
import os

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise RuntimeError("AGENTBAY_API_KEY is required")

    agent_bay = AsyncAgentBay(api_key=api_key)

    image_id = os.getenv("AGENTBAY_IMAGE_ID") or "linux_latest"
    params = CreateSessionParams(
        image_id=image_id,
        labels={"example": "link-url-session"},
    )

    create_result = await agent_bay.create(params)
    if not create_result.success or not create_result.session:
        raise RuntimeError(create_result.error_message or "Failed to create session")

    session = create_result.session
    try:
        print(f"session_id={session.session_id}")
        # NOTE: get_token() and get_link_url() are deprecated (internal SDK use only)
        print(f"token={session._get_token()}")
        print(f"link_url={session._get_link_url()}")

        cmd = await session.command.execute_command("echo hello-from-link-url-session")
        if not cmd.success:
            raise RuntimeError(cmd.error_message or "execute_command failed")
        print(cmd.output)
    finally:
        await session.delete()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

