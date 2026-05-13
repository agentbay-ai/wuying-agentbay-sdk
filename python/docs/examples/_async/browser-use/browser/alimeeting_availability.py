"""
示例：会议室快速查询
打开 Alimeeting
自然语言查询“下周三 朝阳科技园C3 六楼 10:00-12:00”的可用会议室，并关闭弹窗
重点：变量注入（用户名/密码）、模糊指令、弹窗处理
ci-skip

"""

import asyncio
import os
from agentbay import AsyncAgentBay as AgentBay
from agentbay import CreateSessionParams
from agentbay import BrowserOption
from agentbay import ActOptions


async def main():
    api_key = os.getenv("AGENTBAY_API_KEY")
    agent_bay = AgentBay(api_key=api_key)
    params = CreateSessionParams(image_id="browser_latest")
    session_result = await agent_bay.create(params)
    assert session_result.success and session_result.session is not None
    session = session_result.session
    try:
        assert await session.browser.initialize(BrowserOption())
        operator = session.browser.operator
        await operator.navigate("https://meeting.alibaba-inc.com/")
        await operator.act(
            ActOptions(
                action="帮我登陆",
                variables={"用户名": "xxxx", "密码": "123456"},
            )
        )
        await operator.act(
            ActOptions(
                action="帮我找下下周三朝阳科技园C3六楼10点到12点有没有可用的会议室，如果有弹窗，帮我关掉",
            )
        )
        await asyncio.sleep(2)
    finally:
        await session.browser.operator.close()
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
