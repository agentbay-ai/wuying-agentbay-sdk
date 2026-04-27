# ci-stable
import time

import pytest


@pytest.mark.asyncio
async def test_delete_file_integration(make_session):
    lc = await make_session("linux_latest")
    session = lc._result.session
    remote_path = f"/tmp/agentbay_delete_file_{int(time.time())}.txt"

    write_result = await session.file_system.write_file(remote_path, "hello delete_file")
    assert write_result.success, f"write_file failed: {write_result.error_message}"

    info_before = await session.file_system.get_file_info(remote_path)
    assert info_before.success, f"get_file_info failed: {info_before.error_message}"
    assert info_before.file_info.get("isDirectory") is False

    delete_result = await session.file_system.delete_file(remote_path)
    assert delete_result.success, f"delete_file failed: {delete_result.error_message}"

    info_after = await session.file_system.get_file_info(remote_path)
    assert info_after.success is False, "file should not exist after delete_file"
    assert info_after.error_message


