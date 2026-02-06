import asyncio
import concurrent.futures
import os
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union

try:
    from playwright.async_api import Page, async_playwright, Playwright
except ImportError:
    Page = None  # type: ignore[misc, assignment]
    async_playwright = None  # type: ignore[misc, assignment]
    Playwright = None  # type: ignore[misc, assignment]

from pydantic import BaseModel

_PLAYWRIGHT_REQUIRED_MSG = (
    "Playwright is required for browser agent. "
    "Install it with: pip install wuying-agentbay-sdk[playwright] or poetry install --with playwright"
)

from agentbay import AsyncAgentBay
from agentbay import get_logger
from agentbay import SessionResult
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import (
    ActOptions,
    ActResult,
    ExtractOptions,
    ObserveOptions,
    ObserveResult,
)

from .local_page_agent import LocalSession

# Initialize _logger for this module
_logger = get_logger("page_agent")

T = TypeVar("T", bound=BaseModel)


class PageAgent:
    def __init__(
        self, cdp_url: Optional[str] = None, enable_metrics: Optional[bool] = False
    ):
        self._metrics_enabled = enable_metrics
        self._metrics: Dict[str, int] = {}
        self.reset_metrics()
        self.session: Optional[Any] = None
        self.agent_bay: Optional[AsyncAgentBay] = None
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Any] = None
        self.current_page: Optional[Page] = None
        self._worker_thread: Optional[concurrent.futures.Future] = None
        self._task_queue: Optional[asyncio.Queue] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._run_local: bool = False

    def get_test_api_key(self) -> str:
        """Get API key for testing"""
        api_key = os.environ.get("AGENTBAY_API_KEY")
        if not api_key:
            api_key = "akm-xxx"
            _logger.warning(
                "Using default API key. Set AGENTBAY_API_KEY environment variable for testing."
            )
        return api_key

    async def initialize(self) -> None:
        try:
            self._run_local = os.environ.get("RUN_PAGE_TASK_LOCAL", "false") == "true"
            result = SessionResult(success=False)
            if not self._run_local:
                api_key = self.get_test_api_key()
                self.agent_bay = AsyncAgentBay(api_key=api_key)
                _logger.info("Creating a new session for browser agent testing...")
                params = CreateSessionParams(image_id="browser_latest")
                result = await self.agent_bay.create(params)
            else:
                result.session = LocalSession()
                result.success = True

            if result.success and result.session is not None:
                self.session = result.session
                if await self.session.browser.initialize(BrowserOption()):
                    _logger.info("Browser initialized successfully")
                    endpoint_url = await self.session.browser.get_endpoint_url()
                    _logger.info(f"endpoint_url = {endpoint_url}")

                    if async_playwright is None:
                        raise RuntimeError(_PLAYWRIGHT_REQUIRED_MSG)
                    self.playwright = await async_playwright().start()
                    self.browser = await self.playwright.chromium.connect_over_cdp(
                        endpoint_url
                    )

                    if not self.browser.contexts:
                        context = await self.browser.new_context()
                    else:
                        context = self.browser.contexts[0]
                    self.current_page = await context.new_page()
                    _logger.info(
                        "PageAgent initialized successfully with a browser and a page."
                    )

                    # Get the directory of the current script to find the page_tasks directory
                    # Since we've already updated module paths above to use relative imports,
                    # we can skip this replacement or update it to keep relative imports
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    page_tasks_dir = os.path.join(script_dir, "page_tasks")
                    for file in os.listdir(page_tasks_dir):
                        if file.endswith(".py") and file != "__init__.py":
                            file_path = os.path.join(page_tasks_dir, file)
                            with open(file_path, "r") as f:
                                content = f.read()
                            # Replace old import style with relative import to maintain consistency
                            content = content.replace(
                                "mcp_server.page_agent",  # The original import
                                "agentbay.browser.eval.page_agent",  # But we want relative: "..page_agent"
                            )
                            # Actually keep relative imports to avoid circular import issues in this context
                            content = content.replace(
                                "agentbay.browser.eval.page_agent",  # Our earlier update
                                "..page_agent",  # Use relative reference instead
                            )
                            with open(file_path, "w") as f:
                                f.write(content)

                    _logger.info("Import page_tasks successfully")
                else:
                    _logger.error("Failed to initialize browser")
                    raise RuntimeError("Failed to initialize browser")
            else:
                _logger.error("Failed to create session")
                raise RuntimeError("Failed to create session")
        except Exception as e:
            _logger.error(f"Error in initialize: {e}", exc_info=True)
            raise
        _logger.info("Initialize browser agent successfully")

    async def _interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            if self._tool_call_queue is not None:
                try:
                    tool_name, arguments, future = await asyncio.wait_for(
                        self._tool_call_queue.get(), timeout=1.0
                    )
                    try:
                        _logger.debug(
                            f"Call tool {tool_name} with arguments {arguments}"
                        )
                        if self.session is not None:
                            response = await self.session.call_tool(
                                tool_name, arguments
                            )
                            _logger.debug(f"MCP tool response: {response}")

                            # Extract text content from response
                            if hasattr(response, "content") and response.content:
                                for content_item in response.content:
                                    if (
                                        hasattr(content_item, "text")
                                        and content_item.text
                                    ):
                                        future.set_result(content_item.text)
                                        break
                                else:
                                    # If no text content found, use the original response
                                    future.set_result(response)
                            else:
                                # Fallback to original response if no content structure
                                future.set_result(response)
                        else:
                            future.set_exception(
                                RuntimeError("MCP client session is not initialized.")
                            )
                    except Exception as e:
                        future.set_exception(e)
                except asyncio.TimeoutError:
                    pass
            else:
                await asyncio.sleep(1)

    async def get_current_page(self) -> Page:
        if self.current_page is None:
            raise RuntimeError(
                "Current page is not available. Make sure to navigate to a page first."
            )

        cdp_session = None
        try:
            cdp_session = await self.current_page.context.new_cdp_session(
                self.current_page
            )
            # _logger.info(f"get_current_page: {self.current_page}")
        finally:
            if cdp_session:
                await cdp_session.detach()
        return self.current_page

    def reset_metrics(self) -> None:
        """
        initialize metrics
        """
        self._metrics = {
            "llm_duration_s": 0,
            "llm_call_count": 0,
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0,
        }

    def get_metrics(self) -> Dict[str, int]:
        """
        get metrics
        """
        return self._metrics

    async def goto(
        self,
        url: str,
        wait_until: Optional[
            Literal["load", "domcontentloaded", "networkidle", "commit"]
        ] = "load",
        timeout_ms: Optional[int] = 180000,
    ) -> str:
        _logger.info(f"goto {url}")
        if self.current_page is None or self.current_page.is_closed():
            raise RuntimeError("Browser is not initialized. Call initialize() first.")
        try:
            await self.current_page.goto(url, wait_until=wait_until, timeout=timeout_ms)
            return f"Successfully navigated to {url}"
        except Exception as e:
            _logger.error(f"Error in goto: {e}", exc_info=True)
            return f"goto {url} failed: {str(e)}"

    async def navigate(self, url: str) -> str:
        _logger.info(f"navigate {url}")
        try:
            if self.session is None:
                raise RuntimeError(
                    "Session is not initialized. Call initialize() first."
                )

            await self.session.browser.agent.navigate(url)
            return f"Successfully navigated to {url}"
        except Exception as e:
            _logger.error(f"Error in navigate: {e}", exc_info=True)
            return f"navigate {url} failed: {str(e)}"

    async def screenshot(self) -> str:
        try:
            if self.session is None:
                raise RuntimeError(
                    "Session is not initialized. Call initialize() first."
                )

            data_url_or_error = await self.session.browser.agent.screenshot()
            if data_url_or_error.startswith("screenshot failed:"):
                _logger.error(data_url_or_error)
                return data_url_or_error
            if not data_url_or_error.startswith("data:image/png;base64,"):
                error_msg = f"screenshot failed: Unexpected format from SDK: {data_url_or_error[:100]}"
                _logger.error(error_msg)
                return error_msg

            base64_data = data_url_or_error.split(",", 1)[1]
            return base64_data

        except Exception as e:
            _logger.error(f"Error in screenshot: {e}", exc_info=True)
            return f"screenshot failed: {str(e)}"

    async def extract(
        self,
        instruction: str,
        schema: Type[T],
        use_text_extract: Optional[bool] = False,
        use_vision: Optional[bool] = False,
        selector: Optional[str] = None,
    ) -> T:
        """
        Extracts structured data from the current webpage based on an instruction.

        Args:
            instruction (str): The natural language instruction for extraction.
            schema (Type[T]): The Pydantic schema for the expected output data structure.
            use_text_extract (Optional[bool]): If True, uses text-based extraction; otherwise, uses DOM-based.
            use_vision (Optional[bool]): If True, uses visual (screenshot) information for extraction.
            selector (Optional[str]): Optional CSS selector to narrow down extraction area.

        Returns:
            T: An instance of the provided Pydantic schema with extracted data.
        """
        try:
            if self.session is None:
                raise RuntimeError(
                    "Session is not initialized. Call initialize() first."
                )

            options = ExtractOptions(
                instruction=instruction,
                schema=schema,
                use_text_extract=use_text_extract,
                use_vision=use_vision,
                selector=selector,
            )

            success, extracted_data = await self.session.browser.agent.extract(
                options=options, page=self.current_page
            )
            if not success or extracted_data is None:
                raise RuntimeError("Failed to extract data from the page")
            return extracted_data
        except Exception as e:
            _logger.error(f"Error in extract: {e}", exc_info=True)
            raise

    async def observe(
        self,
        instruction: str,
        use_vision: bool = False,
    ) -> List[ObserveResult]:
        """
        Observes the current webpage to identify and describe elements.

        Args:
            instruction (Optional[str]): Natural language goal for observation.
            use_vision (bool): If True, uses visual (screenshot) information for observation.

        Returns:
            List[ObservedElement]: A list of identified and described elements.
        """
        try:
            if self.session is None:
                raise RuntimeError(
                    "Session is not initialized. Call initialize() first."
                )

            _logger.info("Starting observation...")
            options = ObserveOptions(
                instruction=instruction,
                use_vision=use_vision,
            )
            _, observed_elements = await self.session.browser.agent.observe(
                options=options, page=self.current_page
            )
            return observed_elements
        except Exception as e:
            _logger.error(f"Error in observe: {e}", exc_info=True)
            raise

    async def act(
        self,
        action_input: Union[str, ActOptions, ObserveResult],
        use_vision: bool = False,
    ) -> ActResult:
        """
        Performs an action on the current webpage, either inferred from an instruction
        or directly on an ObservedElement.

        Args:
            action_input (Union[str, ActOptions, ObservedElement]):
                - str: A natural language instruction for the action.
                - ActOptions: Action config with timeouts, DOM settle wait, and variable placeholders.
                - ObservedElement: A pre-identified element to act on directly.
            use_vision (bool): If True, uses visual (screenshot) information for action inference.

        Returns:
            ActionResult: The result of the action, indicating success or failure.
        """
        try:
            if self.session is None:
                raise RuntimeError(
                    "Session is not initialized. Call initialize() first."
                )

            _logger.info(f"Attempting to execute action: {action_input}")
            if isinstance(action_input, str):
                options = ActOptions(
                    action=action_input,
                    use_vision=use_vision,
                )
                return await self.session.browser.agent.act(
                    action_input=options, page=self.current_page
                )
            else:
                return await self.session.browser.agent.act(
                    action_input=action_input, page=self.current_page
                )
        except Exception as e:
            _logger.error(f"Error in act: {e}", exc_info=True)
            raise

    async def close(self) -> None:
        """Closes the browser session if it exists."""
        if self.browser and self.browser.is_connected():
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        self.session = self.playwright = self.browser = self.current_page = None
        if not self._run_local:
            if self.agent_bay and self.session:
                await self.agent_bay.delete(self.session)
