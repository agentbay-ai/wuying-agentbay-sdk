import asyncio
from pathlib import Path

from agentbay import AsyncAgentBay, CreateSessionParams


IMAGE_ID = "mobile_latest"


async def main() -> None:
    agent_bay = AsyncAgentBay()
    result = await agent_bay.create(CreateSessionParams(image_id=IMAGE_ID))
    if not result.success or not result.session:
        raise RuntimeError(f"Failed to create session: {result.error_message}")
    session = result.session

    try:
        ui = await session.mobile.get_all_ui_elements(timeout_ms=10000, format="xml")
        if not ui.success:
            raise RuntimeError(f"Failed to get UI elements: {ui.error_message}")

        xml_text = ui.raw
        out_path = Path("ui_dump.xml")
        out_path.write_text(xml_text, encoding="utf-8")

        preview = xml_text.replace("\r\n", "\n")
        print(f"Saved XML to: {out_path.resolve()}")
        print(f"XML length: {len(xml_text)} chars")
        print("Preview:")
        print(preview[:600] + ("\n...(truncated)" if len(preview) > 600 else ""))
    finally:
        await session.delete()


if __name__ == "__main__":
    asyncio.run(main())
