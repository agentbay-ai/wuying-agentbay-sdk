"""
示例：后台新增商品（表单填报）
打开管理后台
通过变量注入填写表单并提交
重点：ActOptions.variagentbayles 批量字段
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

        await operator.navigate("http://116.62.195.152:3000")
        await operator.act(
            ActOptions(
                action="填写表单",
                variables={
                    "商品": "iPhone 16 Pro",
                    "品牌": "iphone",
                    "价格": "7999.0",
                    "URL": "https://streaming-tests-h5.oss-cn-hangzhou.aliyuncs.com/image/iPhone-16-Pro.jpg",
                    "描述": "6.3英寸显示，A18 Pro，4800万像素摄像头，120Hz ProMotion",
                    "库存": "230.0",
                },
            )
        )
        await operator.act(ActOptions(action="点击提交/保存按钮"))
        await asyncio.sleep(2)
        await operator.close()
    finally:
        await agent_bay.delete(session)


if __name__ == "__main__":
    asyncio.run(main())
