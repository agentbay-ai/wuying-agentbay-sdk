#!/usr/bin/env python3
"""
ci-stable

Mobile BoundsRect Example (Async)

This example demonstrates the recommended `bounds_rect` field on UI elements returned by:
- session.mobile.get_clickable_ui_elements()
- session.mobile.get_all_ui_elements()

Notes:
- `element["bounds"]` is deprecated because its type may vary across backends.
- Prefer `element["bounds_rect"]` (stable dict: left/top/right/bottom).
"""

import asyncio
import os

from agentbay import AsyncAgentBay, CreateSessionParams


async def main() -> None:
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        raise ValueError("AGENTBAY_API_KEY environment variable is required")

    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    try:
        session_result = await agent_bay.create(CreateSessionParams(image_id="mobile_latest"))
        assert session_result.success, session_result.error_message
        session = session_result.session

        clickable = await session.mobile.get_clickable_ui_elements(timeout_ms=5000)
        print(f"clickable.success={clickable.success}, count={len(clickable.elements)}")
        for e in clickable.elements[:5]:
            print(
                {
                    "text": e.get("text"),
                    "className": e.get("className"),
                    "bounds": e.get("bounds"),  # deprecated
                    "bounds_rect": e.get("bounds_rect"),  # recommended
                }
            )

        all_ui = await session.mobile.get_all_ui_elements(timeout_ms=8000)
        print(f"all_ui.success={all_ui.success}, count={len(all_ui.elements)}")
        for e in all_ui.elements[:3]:
            print(
                {
                    "text": e.get("text"),
                    "className": e.get("className"),
                    "bounds": e.get("bounds"),  # deprecated
                    "bounds_rect": e.get("bounds_rect"),  # recommended
                }
            )
    finally:
        if session is not None:
            await session.delete()


if __name__ == "__main__":
    asyncio.run(main())


