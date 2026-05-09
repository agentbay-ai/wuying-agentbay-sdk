
import os

import pytest
import pytest_asyncio

from agentbay import AsyncAgentBay, CreateSessionParams


ENV_TEST_IMAGE = "linux_latest"


@pytest_asyncio.fixture
async def agent_session():
    """
    Fixture to create a session with the env-capable image
    and delete it after all tests are done.
    """
    api_key = os.environ.get("AGENTBAY_API_KEY")
    if not api_key:
        pytest.skip("AGENTBAY_API_KEY environment variable not set")

    agent_bay = AsyncAgentBay(api_key=api_key)
    print("Creating a new session for Env testing...")

    params = CreateSessionParams(image_id=ENV_TEST_IMAGE)
    result = await agent_bay.create(params)

    if not result.success or not result.session:
        pytest.fail(f"Failed to create session: {result.error_message}")

    session = result.session
    print(f"Session created with ID: {session.session_id}")

    yield session

    print("Cleaning up: Deleting the session...")
    try:
        delete_result = await session.delete()
        if delete_result.success:
            print("Session successfully deleted")
        else:
            print(f"Warning: Error deleting session: {delete_result.error_message}")
    except Exception as e:
        print(f"Warning: Error deleting session: {e}")


@pytest_asyncio.fixture
def env(agent_session):
    """Fixture to get the env object from the session."""
    return agent_session.env


@pytest.mark.asyncio
async def test_env_set_basic(env):
    """Test setting environment variables."""
    result = await env.set({"TEST_KEY": "test_value", "ANOTHER_KEY": "another_value"})
    assert result.success
    assert result.request_id != ""


@pytest.mark.asyncio
async def test_env_get_all(env):
    """Test getting all environment variables."""
    await env.set({"SDK_TEST_A": "value_a"})
    result = await env.get()
    assert result.success
    assert isinstance(result.envs, dict)
    assert "SDK_TEST_A" in result.envs
    assert result.envs["SDK_TEST_A"] == "value_a"
    assert result.request_id != ""


@pytest.mark.asyncio
async def test_env_get_specific_keys(env):
    """Test getting specific environment variables by keys."""
    await env.set({"GET_KEY_1": "val1", "GET_KEY_2": "val2"})
    result = await env.get(keys=["GET_KEY_1", "GET_KEY_2"])
    assert result.success
    assert result.envs["GET_KEY_1"] == "val1"
    assert result.envs["GET_KEY_2"] == "val2"


@pytest.mark.asyncio
async def test_env_get_nonexistent_key(env):
    """Test getting a key that was never set returns empty dict."""
    result = await env.get(keys=["NONEXISTENT_KEY_XYZ_12345"])
    assert result.success
    assert "NONEXISTENT_KEY_XYZ_12345" not in result.envs or result.envs.get("NONEXISTENT_KEY_XYZ_12345") == ""


@pytest.mark.asyncio
async def test_env_set_overwrite(env):
    """Test that setting an existing key overwrites its value."""
    await env.set({"OVERWRITE_KEY": "original"})
    result1 = await env.get(keys=["OVERWRITE_KEY"])
    assert result1.envs["OVERWRITE_KEY"] == "original"

    await env.set({"OVERWRITE_KEY": "updated"})
    result2 = await env.get(keys=["OVERWRITE_KEY"])
    assert result2.envs["OVERWRITE_KEY"] == "updated"


@pytest.mark.asyncio
async def test_env_visible_in_shell(agent_session):
    """Test that env vars set via env.set are visible in shell commands."""
    await agent_session.env.set({"SHELL_VISIBLE_VAR": "hello_from_env"})

    result = await agent_session.command.execute_command("echo $SHELL_VISIBLE_VAR")
    assert result.success
    assert "hello_from_env" in result.stdout


@pytest.mark.asyncio
async def test_env_set_empty_dict_raises(env):
    """Test that setting an empty dict raises ValueError."""
    with pytest.raises(ValueError):
        await env.set({})


@pytest.mark.asyncio
async def test_env_set_validates_types(env):
    """Test that non-string keys/values raise ValueError."""
    with pytest.raises(ValueError):
        await env.set({123: "value"})
    with pytest.raises(ValueError):
        await env.set({"key": 456})
