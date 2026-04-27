import os
import asyncio

import pytest

from agentbay import MobileExtraConfig, MobileSimulateMode
from agentbay import CreateSessionParams, ExtraConfigs
from agentbay import AsyncMobileSimulateService


MOBILE_INFO_MODEL_A = "SM-A505F"
MOBILE_INFO_MODEL_B = "moto g stylus 5G - 2024"


@pytest.mark.asyncio
async def test_mobile_simulate_for_model_a(agent_bay_client):
    """
    Test device properties after mobile simulate for model a.
    """
    global mobile_sim_persistence_context_id
    # Get a mobile dev info file from DumpSDK or real device library
    print("Upload mobile dev info file...")
    mobile_sim_persistence_context_id = None
    mobile_info_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
            "resource", "mobile_info_model_a.json"
    )
    with open(mobile_info_file_path, "r") as f:
        mobile_info_content = f.read()
    
    # Create mobile simulate service and set simulate params
    simulate_service = AsyncMobileSimulateService(agent_bay_client)
    simulate_service.set_simulate_enable(True)
    simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
    
    upload_result = await simulate_service.upload_mobile_info(mobile_info_content)
    assert upload_result.success, f"Failed to upload mobile dev info file: {upload_result.error_message}"
    mobile_sim_persistence_context_id = upload_result.mobile_simulate_context_id
    print(f"Mobile dev info uploaded successfully: {mobile_sim_persistence_context_id}")

    params = CreateSessionParams(
        image_id="mobile_latest",
        extra_configs=ExtraConfigs(
            mobile=MobileExtraConfig(
                simulate_config=simulate_service.get_simulate_config()
            )
        )
    )
    result = await agent_bay_client.create(params)
    session = None
    if not result.success and "no authorized app" in result.error_message:
        pytest.skip(f"The user has no authorized app instance: {result.error_message}")
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None, "Session should not be None"
    session = result.session
    print(f"Session created successfully: {session.session_id}")

    # Wait for mobile simulate to complete
    await asyncio.sleep(5)
    print("Getting device model after mobile simulate for model a...")
    result = await session.command.execute_command("getprop ro.product.model")
    assert result.success, "Failed to get device model"
    model_a_product_model = result.output.strip()
    print(f"Simulated model a mobile product model: {model_a_product_model}")
    assert model_a_product_model == MOBILE_INFO_MODEL_A, f"Device model should be {MOBILE_INFO_MODEL_A}"

    await asyncio.sleep(2)
    print("Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success, "Failed to delete session"
    print(f"Session deleted successfully (RequestID: {delete_result.request_id})")



@pytest.mark.asyncio
async def test_mobile_simulate_for_model_b(agent_bay_client):
    """
    Test device properties after mobile simulate for model b.
    """
    # Get a mobile dev info file from DumpSDK or real device library
    print("Upload mobile model b dev info file...")
    mobile_sim_context_id = None
    mobile_info_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
            "resource", "mobile_info_model_b.json"
    )
    with open(mobile_info_file_path, "r") as f:
        mobile_info_content = f.read()
    
    # Create mobile simulate service and set simulate params
    simulate_service = AsyncMobileSimulateService(agent_bay_client)
    simulate_service.set_simulate_enable(True)
    simulate_service.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
    
    upload_result = await simulate_service.upload_mobile_info(mobile_info_content)
    assert upload_result.success, f"Failed to upload mobile dev info file: {upload_result.error_message}"
    mobile_sim_context_id = upload_result.mobile_simulate_context_id
    print(f"Mobile model b dev info uploaded successfully: {mobile_sim_context_id}")

    params = CreateSessionParams(
        image_id="mobile_latest",
        extra_configs=ExtraConfigs(
            mobile=MobileExtraConfig(
                simulate_config=simulate_service.get_simulate_config()
            )
        )
    )
    result = await agent_bay_client.create(params)
    session = None
    if not result.success and "no authorized app" in result.error_message:
        pytest.skip(f"The user has no authorized app instance: {result.error_message}")
    assert result.success, f"Failed to create session {result.error_message}"
    assert result.session is not None, "Session should not be None"
    session = result.session
    print(f"Session created successfully: {session.session_id}")

    # Wait for mobile simulate to complete
    await asyncio.sleep(5)
    print("Getting device model after mobile simulate for model b...")
    result = await session.command.execute_command("getprop ro.product.model")
    assert result.success, "Failed to get device model"
    model_b_product_model = result.output.strip()
    print(f"Simulated model b mobile product model: {model_b_product_model}")
    assert model_b_product_model == MOBILE_INFO_MODEL_B, f"Device model should be {MOBILE_INFO_MODEL_B}"

    await asyncio.sleep(2)
    print("Deleting session...")
    delete_result = await agent_bay_client.delete(session)
    assert delete_result.success, "Failed to delete session"
    print(f"Session deleted successfully (RequestID: {delete_result.request_id})")



@pytest.mark.asyncio
async def test_mobile_simulate_persistence(agent_bay_client):
    """
    Using model a simulate context to test persistence mobile simulate across sessions.
    """
    # In Session 1
    # Get a mobile dev info file from DumpSDK or real device library
    print("Upload mobile dev info file...")
    mobile_sim_persistence_context_id = None
    mobile_info_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), 
            "resource", "mobile_info_model_a.json"
    )
    with open(mobile_info_file_path, "r") as f:
        mobile_info_content = f.read()
    
    # Create mobile simulate service and set simulate params
    simulate_service_1 = AsyncMobileSimulateService(agent_bay_client)
    simulate_service_1.set_simulate_enable(True)
    simulate_service_1.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
    
    upload_result = await simulate_service_1.upload_mobile_info(mobile_info_content)
    assert upload_result.success, f"Failed to upload mobile dev info file: {upload_result.error_message}"
    mobile_sim_persistence_context_id = upload_result.mobile_simulate_context_id
    print(f"Mobile dev info uploaded successfully: {mobile_sim_persistence_context_id}")

    params_1 = CreateSessionParams(
        image_id="mobile_latest",
        extra_configs=ExtraConfigs(
            mobile=MobileExtraConfig(
                simulate_config=simulate_service_1.get_simulate_config()
            )
        )
    )
    result = await agent_bay_client.create(params_1)
    if not result.success and "no authorized app" in result.error_message:
        pytest.skip(f"The user has no authorized app instance: {result.error_message}")
    assert result.success, f"Failed to create session: {result.error_message}"
    assert result.session is not None, "Session should not be None"
    session_1 = result.session
    print(f"Session 1 created successfully: {session_1.session_id}")

    # Wait for mobile simulate to complete
    await asyncio.sleep(5)
    print("Getting device model after mobile simulate for model a...")
    result = await session_1.command.execute_command("getprop ro.product.model")
    assert result.success, "Failed to get device model"
    model_a_product_model = result.output.strip()
    print(f"Simulated model a mobile product model: {model_a_product_model}")
    assert model_a_product_model == MOBILE_INFO_MODEL_A, f"Device model should be {MOBILE_INFO_MODEL_A}"

    await asyncio.sleep(2)
    print("Deleting session 1...")
    delete_result = await agent_bay_client.delete(session_1)
    assert delete_result.success, "Failed to delete session"
    print(f"Session 1 deleted successfully (RequestID: {delete_result.request_id})")


    # In Session 2
    # Directly use model a simulate context id to do mobile simulate across sessions.
    # Create mobile simulate service and set simulate params
    simulate_service_2 = AsyncMobileSimulateService(agent_bay_client)
    simulate_service_2.set_simulate_enable(True)
    simulate_service_2.set_simulate_mode(MobileSimulateMode.PROPERTIES_ONLY)
    simulate_service_2.set_simulate_context_id(mobile_sim_persistence_context_id)
    
    params_2 = CreateSessionParams(
        image_id="mobile_latest",
        extra_configs=ExtraConfigs(
            mobile=MobileExtraConfig(
                simulate_config=simulate_service_2.get_simulate_config()
            )
        )
    )
    result = await agent_bay_client.create(params_2)
    assert result.success, "Failed to create session"
    assert result.session is not None, "Session should not be None"
    session_2 = result.session
    print(f"Session 2 created successfully: {session_2.session_id}")

    # Wait for mobile simulate to complete
    await asyncio.sleep(5)
    print("Getting device model after mobile simulate...")
    result = await session_2.command.execute_command("getprop ro.product.model")
    assert result.success, "Failed to get device model"
    persistence_product_model = result.output.strip()
    print(f"Persistent simulated mobile product model: {persistence_product_model}")
    assert persistence_product_model == MOBILE_INFO_MODEL_A, f"Device model should be {MOBILE_INFO_MODEL_A}"

    await asyncio.sleep(2)

    print("Deleting session 2...")
    delete_result = await agent_bay_client.delete(session_2)
    assert delete_result.success, "Failed to delete session"
    print(f"Session 2 deleted successfully (RequestID: {delete_result.request_id})")
