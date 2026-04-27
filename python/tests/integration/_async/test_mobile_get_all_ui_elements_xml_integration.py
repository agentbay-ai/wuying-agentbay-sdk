"""Integration test for get_all_ui_elements XML format (no mocks)."""

import pytest
import pytest_asyncio

from agentbay import CreateSessionParams


IMAGE_ID = "mobile-use-android-12-gw"


@pytest_asyncio.fixture
async def session(make_session):
    params = CreateSessionParams(image_id=IMAGE_ID)
    lc = await make_session(params=params)
    return lc._result.session


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_ui_elements_xml_format_contract(session):
    ui = await session.mobile.get_all_ui_elements(timeout_ms=10000, format="xml")
    assert ui.success, f"get_all_ui_elements(xml) failed: {ui.error_message}"
    assert ui.format == "xml"
    assert isinstance(ui.raw, str)
    assert ui.raw.strip() != ""
    assert ui.raw.lstrip().startswith("<?xml")
    assert "<hierarchy" in ui.raw
    assert isinstance(ui.elements, list)
    assert ui.elements == []
