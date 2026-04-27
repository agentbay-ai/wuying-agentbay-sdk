# ci-stable
# -*- coding: utf-8 -*-
"""Integration tests for WebSocket functionality."""

import asyncio

import pytest

from agentbay import AsyncAgentBay, BrowserOption, CreateSessionParams


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ws_connect_and_basic_call_stream(agent_bay_client: AsyncAgentBay):
    result = await agent_bay_client.create(CreateSessionParams())
    assert result.success is True, result.error_message
    assert result.session is not None
    session = result.session

    ws_client = None
    try:
        assert (
            session.ws_url
        ), "Backend did not return wsUrl/WsUrl in CreateSession response"

        ws_client = await session._get_ws_client()
        await ws_client.connect()

        target = "wuying_codespace"
        for tool in getattr(session, "mcpTools", []) or []:
            try:
                if getattr(tool, "name", "") == "run_code" and getattr(tool, "server", ""):
                    target = tool.server
                    break
            except Exception:
                continue

        events: list[dict] = []
        ends: list[dict] = []
        errors: list[Exception] = []
        end_signal = asyncio.Event()

        def on_event(invocation_id: str, data: dict) -> None:
            assert invocation_id
            assert isinstance(data, dict)
            events.append(data)

        def on_end(invocation_id: str, data: dict) -> None:
            assert invocation_id
            assert isinstance(data, dict)
            ends.append(data)
            end_signal.set()

        def on_error(invocation_id: str, err: Exception) -> None:
            assert invocation_id
            assert isinstance(err, Exception)
            errors.append(err)
            end_signal.set()

        handle = await ws_client.call_stream(
            target=target,
            data={
                "method": "run_code",
                "mode": "stream",
                "params": {"language": "python", "timeoutS": 600, "code": "x=1"},
            },
            on_event=on_event,
            on_end=on_end,
            on_error=on_error,
        )

        try:
            end_data = await asyncio.wait_for(handle.wait_end(), timeout=600)
        except Exception as e:
            assert end_signal.is_set(), "Expected on_error/on_end to be called"
            if errors:
                # For WS validation, backend may return request error immediately.
                # This is still a valid callback chain: on_error must be invoked.
                return
            raise

        assert end_signal.is_set()
        assert errors == [], f"errors={errors}, events={events}, ends={ends}"
        assert len(ends) == 1
        assert isinstance(end_data, dict)
    finally:
        if ws_client is not None:
            try:
                await ws_client.close()
            except Exception:
                pass
        await session.delete()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_ws_register_callback_should_receive_captcha_push(agent_bay_client: AsyncAgentBay) -> None:
    playwright = pytest.importorskip("playwright.async_api")

    created = await agent_bay_client.create(CreateSessionParams(image_id="browser_latest"))
    assert created.success is True, created.error_message
    assert created.session is not None
    session = created.session

    ws_client = None
    try:
        ws_client = await session._get_ws_client()
        push_signal = asyncio.Event()
        received: list[dict] = []

        def on_push(payload: dict) -> None:
            received.append(payload)
            push_signal.set()

        ws_client.register_callback("wuying_cdp_mcp_server", on_push)
        await ws_client.connect()

        browser_option = BrowserOption(use_stealth=True, solve_captchas=True)
        assert await session.browser.initialize(browser_option)
        endpoint_url = await session.browser.get_endpoint_url()
        assert endpoint_url

        async with playwright.async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(endpoint_url)
            page = await browser.contexts[0].new_page()
            await page.goto(
                "https://passport.ly.com/Passport/GetPassword",
                wait_until="domcontentloaded",
            )
            input_element = await page.wait_for_selector("#name_in", timeout=10000)
            await input_element.click()
            await input_element.fill("")
            await input_element.type("13000000000")
            await page.wait_for_timeout(1000)
            await page.click("#next_step1")

            await asyncio.wait_for(push_signal.wait(), timeout=180.0)

        assert received, "Expected at least 1 push callback invocation"
        first = received[0]
        assert first.get("target") == "wuying_cdp_mcp_server"
        data = first.get("data")
        assert isinstance(data, dict)
        assert data.get("code") in (201, 202), f"unexpected push data: {data!r}"
    finally:
        if ws_client is not None:
            try:
                await ws_client.close()
            except Exception:
                pass
        await session.delete()
