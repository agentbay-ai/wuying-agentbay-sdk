import asyncio
import concurrent.futures
import json
import os
import sys
import uuid
from typing import Any, Dict

from mcp import ClientSession, StdioServerParameters, stdio_client

try:
    from playwright.async_api import async_playwright
except ImportError:
    async_playwright = None  # type: ignore[misc, assignment]

from agentbay import get_logger

_PLAYWRIGHT_REQUIRED_MSG = (
    "Playwright is required for local browser. "
    "Install it with: pip install wuying-agentbay-sdk[playwright] or poetry install --with playwright"
)
from agentbay import AsyncBrowser as Browser
from agentbay import AsyncSession as Session
from agentbay.api.base_service import OperationResult

from agentbay import AsyncBrowserAgent as BrowserAgent
from agentbay import BrowserOption

# Use the AgentBay _logger instead of the standard _logger
_logger = get_logger("local_page_agent")


class LocalMCPClient:
    def __init__(self, server: str, command: str, args: list[str], env: dict[str, str] | None = None) -> None:
        self.server = server
        self.command = command
        self.args = args
        self.env = env
        self.session: ClientSession | None = None
        self.worker_thread: concurrent.futures.Future | None = None
        self._tool_call_queue: asyncio.Queue | None = None
        self._loop: asyncio.AbstractEventLoop | None = None

    def connect(self) -> None:
        if self.worker_thread is None:
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()

            def thread_target() -> None:
                async def _connect_and_list_tools() -> None:
                    success = False
                    _logger.info("Start connect to mcp server")
                    try:
                        _logger.debug(f"command = {self.command}, args = {self.args}")
                        try:
                            if self.env is not None:
                                server_params = StdioServerParameters(
                                    command=self.command, args=self.args, env=self.env
                                )
                            else:
                                server_params = StdioServerParameters(
                                    command=self.command, args=self.args
                                )
                        except TypeError:
                            _logger.debug("StdioServerParameters does not support env parameter, using default inheritance")
                            server_params = StdioServerParameters(
                                command=self.command, args=self.args
                            )
                        async with stdio_client(server_params) as (
                            read_stream,
                            write_stream,
                        ):
                            async with ClientSession(
                                read_stream, write_stream
                            ) as session:
                                # Setup queue and event loop reference
                                self._tool_call_queue = asyncio.Queue()
                                self._loop = asyncio.get_running_loop()

                                self.session = session
                                _logger.info("Initialize MCP client session")
                                await self.session.initialize()
                                _logger.info(
                                    "Client initialized. Listing available tools..."
                                )
                                tools = await self.session.list_tools()
                                _logger.info(f"Tools: {tools}")
                                success = True
                                promise.set_result(success)
                                await self._interactive_loop()
                    except Exception as e:
                        _logger.error(f"Failed to connect to MCP server: {e}")
                        success = False
                        promise.set_result(success)

                asyncio.run(_connect_and_list_tools())

            self.worker_thread = concurrent.futures.ThreadPoolExecutor().submit(
                thread_target
            )
            promise.result()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        if not self.session or not self._tool_call_queue or not self._loop:
            raise RuntimeError(
                "MCP client is not connected. Call connect() and ensure it returns True before calling callTool."
            )
        caller_loop = asyncio.get_running_loop()
        fut = caller_loop.create_future()
        await self._tool_call_queue.put((tool_name, arguments, fut))
        return await fut

    async def _interactive_loop(self):
        """Run interactive loop."""
        while True:
            if self._tool_call_queue is not None:
                try:
                    tool_name, arguments, future = await asyncio.wait_for(
                        self._tool_call_queue.get(), timeout=1.0
                    )
                    try:
                        _logger.info(
                            f"Call tool {tool_name} with arguments {arguments}"
                        )
                        if self.session is not None:
                            response = await self.session.call_tool(
                                tool_name, arguments
                            )
                            is_successful = not response.isError

                            mcp_response = OperationResult(
                                request_id="local_request_dummy_id",
                                success=is_successful,
                            )

                            # Extract text content from response
                            text_content = ""
                            if hasattr(response, "content") and response.content:
                                for content_item in response.content:
                                    if (
                                        hasattr(content_item, "text")
                                        and content_item.text
                                    ):
                                        text_content = content_item.text
                                        break
                                if is_successful:
                                    mcp_response.data = text_content
                                    _logger.info(
                                        f"MCP tool text response (data): {str(text_content)[:2000]}"
                                    )
                                else:
                                    mcp_response.error_message = text_content
                                    _logger.info(
                                        f"MCP tool text response (error): {str(text_content)[:2000]}"
                                    )

                            if asyncio.isfuture(future):
                                fut_loop = future.get_loop()
                                fut_loop.call_soon_threadsafe(
                                    future.set_result, mcp_response
                                )
                            elif isinstance(future, concurrent.futures.Future):
                                future.set_result(mcp_response)
                            else:
                                raise TypeError(
                                    f"Unexpected future type: {type(future)}"
                                )
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


class LocalPageAgent(BrowserAgent):
    def __init__(self, session, browser):
        super().__init__(session, browser)

        mcp_script = os.environ.get("PAGE_TASK_MCP_SERVER_SCRIPT", "")

        if mcp_script:
            env = dict(os.environ)
            self.mcp_client: LocalMCPClient | None = LocalMCPClient(
                server="PageUseAgent", command=sys.executable, args=[mcp_script], env=env
            )
        else:
            self.mcp_client = None
            _logger.warning(
                "PAGE_TASK_MCP_SERVER_SCRIPT not set. MCP client will not be initialized."
            )

    def initialize(self):
        if self.mcp_client:
            self.mcp_client.connect()

    def _call_mcp_tool(
        self,
        name: str,
        args: dict,
        read_timeout: int = None,
        connect_timeout: int = None,
    ) -> OperationResult:
        # If MCP client is not available or local mode, return a failed OperationResult
        # This avoids issues when no actual MCP server is running
        error_message = f"Local mode - cannot execute tool: {name}. Browser evaluation is running in local mode."

        return OperationResult(
            request_id="local_request_mock_id",
            success=False,
            data=None,
            error_message=error_message,
        )

    async def _call_mcp_tool_async(self, name: str, args: dict) -> OperationResult:
        if not self.mcp_client:
            raise RuntimeError("mcp_client is not set on LocalBrowserAgent.")
        return await self.mcp_client.call_tool(name, args)


class LocalBrowser(Browser):
    def __init__(self, session=None):
        # Optionally skip calling super().__init__ if not needed for tests
        self.contexts = []
        self._cdp_port = 9222
        self.agent: LocalPageAgent = LocalPageAgent(session, self)
        self._worker_thread = None

    async def initialize(self, options: BrowserOption) -> bool:
        if self._worker_thread is None:
            promise: concurrent.futures.Future[bool] = concurrent.futures.Future()

            def thread_target() -> None:
                async def _launch_local_browser() -> None:
                    success = False
                    _logger.info("Start launching local browser")
                    try:
                        if async_playwright is None:
                            raise RuntimeError(_PLAYWRIGHT_REQUIRED_MSG)
                        async with async_playwright() as p:
                            # Define CDP port
                            # Recreate /tmp/chrome_cdp_ports.json with the required content
                            chrome_cdp_ports_path = "/tmp/chrome_cdp_ports.json"
                            with open(chrome_cdp_ports_path, "w") as f:
                                json.dump(
                                    {
                                        "chrome": str(self._cdp_port),
                                        "router": str(self._cdp_port),
                                        "local": str(self._cdp_port),
                                    },
                                    f,
                                )
                            cwd = os.getcwd()
                            user_data_dir = os.path.join(
                                cwd,
                                "tmp",
                                f"browser_user_data_{os.getpid()}_{uuid.uuid4().hex}",
                            )

                            # Read env variable HEADLESS_MODE
                            headless_mode = os.environ.get("HEADLESS", "false")
                            headless = headless_mode.lower() == "true"

                            self._browser = await p.chromium.launch_persistent_context(
                                headless=headless,
                                viewport={"width": 1280, "height": 1200},
                                args=[
                                    f"--remote-debugging-port={self._cdp_port}",
                                ],
                                user_data_dir=user_data_dir,
                            )

                            _logger.info("Local browser launched successfully:")
                            success = True
                            promise.set_result(success)
                            await self._playwright_interactive_loop()
                            _logger.info("Local browser interactive loop completed")
                    except Exception as e:
                        _logger.error(f"Failed to connect to browser: {e}")
                        success = False
                        promise.set_result(success)

                asyncio.run(_launch_local_browser())

            self._worker_thread = concurrent.futures.ThreadPoolExecutor().submit(
                thread_target
            )
            if not promise.result():
                _logger.error("Failed to launch local browser")
                return False

        self.agent.initialize()
        return True

    def is_initialized(self) -> bool:
        return True

    async def get_endpoint_url(self) -> str:
        return f"http://localhost:{self._cdp_port}"

    async def _playwright_interactive_loop(self) -> None:
        """Run interactive loop."""
        while True:
            await asyncio.sleep(3)


class LocalSession(Session):
    def __init__(self):
        # Create a mock agent_bay with the required attributes
        mock_agent_bay = type(
            "MockAgentBay",
            (),
            {
                "api_key": os.environ.get("AGENTBAY_API_KEY", ""),
                "api_key_configured": bool(os.environ.get("AGENTBAY_API_KEY", "")),
            },
        )()
        mock_client = type(
            "MockClient",
            (),
            {
                "api_base_url": "",
                "get_session_status": lambda request: type(
                    "MockSessionStatus",
                    (),
                    {
                        "to_map": lambda: {
                            "success": True,
                            "data": {"status": "running"},
                        }
                    },
                )(),
                "call_mcp_tool": lambda name, args, **kwargs: type(
                    "MockMcpToolResult",
                    (),
                    {
                        "request_id": "mock_request_id",
                        "success": False,
                        "data": None,
                        "error_message": "Mock mode: Cannot execute tool calls without proper API connection",
                    },
                )(),
            },
        )()

        # Assign the mock client to the mock agent bay
        mock_agent_bay.client = mock_client

        super().__init__(mock_agent_bay, "local_session")
        self.browser = LocalBrowser(self)

    async def call_mcp_tool(
        self,
        name: str,
        args: dict,
        read_timeout: int = None,
        connect_timeout: int = None,
    ):
        """
        Async stub for local mode. Keeps call signature compatible with the async
        browser agent, which awaits session.call_mcp_tool. We return a real
        OperationResult instance to avoid 'await OperationResult' errors.
        """
        return await self.browser.agent._call_mcp_tool_async(name, args)

    def delete(self, sync_context: bool = False) -> None:
        pass
