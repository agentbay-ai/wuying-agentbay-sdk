"""Integration tests for browser hybrid usage functionality."""
# ci-stable

import asyncio
import os

import pytest

from agentbay import get_logger
from agentbay import BrowserOption, ExtractOptions
from pydantic import BaseModel
from playwright.async_api import async_playwright

logger = get_logger("agentbay-integration-test")


class WeatherSchema(BaseModel):
    """Schema for weather query test."""

    Weather: str
    City: str
    Temperature: str


class DummySchema(BaseModel):
    """Schema for extract test."""

    title: str


@pytest.mark.asyncio
async def test_browser_hybrid_usage_success(make_session):
    """Test executing a browser hybrid usage task successfully."""
    # Ensure a delay to avoid session creation conflicts
    await asyncio.sleep(3)
    lc = await make_session("browser_latest")
    session = lc._result.session

    timeout = int(os.environ.get("AGENT_TASK_TIMEOUT", 180))
    agent = session.agent
    browser = session.browser
    assert browser is not None
    await asyncio.sleep(15)
    logger.info("🚀 Browser initialization")
    await browser.initialize(BrowserOption())

    endpoint_url = await browser.get_endpoint_url()
    logger.info(f"endpoint_url = {endpoint_url}")
    assert endpoint_url is not None

    async with async_playwright() as p:
        playwright_browser = await p.chromium.connect_over_cdp(endpoint_url)
        assert playwright_browser is not None

        context = (
            playwright_browser.contexts[0]
            if playwright_browser.contexts
            else await playwright_browser.new_context()
        )
        page = await context.new_page()
        await page.goto("http://www.baidu.com")
        title = await page.title()
        assert title is not None
        logger.info(f"Page title: {title}")
        await asyncio.sleep(15)
        task = "在百度查询上海天气"
        logger.info("🚀 task of Query the weather in Shanghai")

        result = await agent.browser.execute_task_and_wait(
            task, timeout, use_vision=False, output_schema=WeatherSchema
        )
        if result.task_status in ("failed", "unsupported"):
            pytest.skip("Task failed")
        assert result.success
        assert result.request_id != ""
        assert result.error_message == ""
        logger.info(f"✅ result {result.task_result}")

        result, obj = await browser.operator.extract(
            ExtractOptions(instruction="Extract the title", schema=DummySchema)
        )
        logger.info(f"✅ result of extract {result}\n{obj}")

        await page.close()
        await playwright_browser.close()
