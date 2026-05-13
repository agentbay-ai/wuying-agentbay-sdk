"""
ci-stable
Skills feature example: get_metadata + session with skills.

This example demonstrates:
1. Get skills metadata without starting a sandbox
2. Get metadata filtered by group IDs
3. Create session with skills loaded
4. Verify skills directory in sandbox
"""

import asyncio
import os

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    api_key = os.environ.get("AGENTBAY_API_KEY", "").strip()
    if not api_key:
        print("Warning: Set AGENTBAY_API_KEY environment variable.")
        return

    agent_bay = AsyncAgentBay(api_key=api_key)

    # 1. Get skills metadata (no sandbox needed)
    print("Getting skills metadata...")
    metadata = await agent_bay.beta_skills.get_metadata()
    print(f"Skills root path: {metadata.skills_root_path}")
    print(f"Available skills: {len(metadata.skills)}")
    for skill in metadata.skills:
        print(f"  - {skill.name}: {skill.description}")

    # 2. Get metadata filtered by group IDs
    print("\nGetting skills metadata filtered by group...")
    filtered = await agent_bay.beta_skills.get_metadata(skill_names=["5kvAvffm"])
    print(f"Filtered skills: {len(filtered.skills)}")

    # 3. Create session with skills loaded
    print("\nCreating session with skills...")
    params = CreateSessionParams(load_skills=True)
    result = await agent_bay.create(params)
    if not result.success or not result.session:
        print(f"Session creation failed: {result.error_message}")
        return

    session = result.session
    try:
        print(f"Session created: {session.session_id}")

        # 4. Get skills metadata via beta_skills and verify in sandbox
        metadata = await agent_bay.beta_skills.get_metadata(
            image_id=getattr(params, "image_id", None),
            skill_names=getattr(params, "skill_names", None),
        )
        print(f"Skills root: {metadata.skills_root_path}")
        print(f"Skills count: {len(metadata.skills)}")
        if metadata.skills_root_path:
            cmd = await session.command.execute_command(
                f"ls {metadata.skills_root_path}"
            )
            print(f"\nSkills directory contents:\n{cmd.output}")
    finally:
        await session.delete()
        print("\nSession deleted.")


if __name__ == "__main__":
    asyncio.run(main())
