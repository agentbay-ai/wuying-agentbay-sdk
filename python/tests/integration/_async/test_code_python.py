"""Integration tests for CodeSpace Python execution functionality."""
# ci-stable

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def session(make_session):
    """Create a session with code_latest image."""
    lc = await make_session(params=CreateSessionParams(image_id="code_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_run_simple_python_code(session):
    """Test simple Python code execution."""
    # Arrange
    print("\nTest: Simple Python code execution...")
    code = "print('Hello from Python')\nresult = 2 + 2\nprint(f'Result: {result}')"

    # Act
    result = await session.code.run_code(code, "python")

    # Assert
    assert result.success, f"Python execution failed: {result.error_message}"
    assert result.result is not None, "Result should not be None"
    print(f"Python output:\n{result.result}")


@pytest.mark.asyncio
async def test_python_with_imports(session):
    """Test Python code with imports."""
    # Arrange
    print("\nTest: Python with imports...")
    code = """
import sys
import json
from datetime import datetime

data = {
    'python_version': sys.version.split()[0],
    'timestamp': datetime.now().isoformat()
}
print(json.dumps(data, indent=2))
"""

    # Act
    result = await session.code.run_code(code, "python")

    # Assert
    assert result.success, f"Python with imports failed: {result.error_message}"
    assert result.result is not None, "Result should not be None"
    assert "python_version" in result.result, "Output should contain python_version"
    print(f"Python output:\n{result.result}")


@pytest.mark.asyncio
async def test_python_file_operations(session):
    """Test Python file operations."""
    # Arrange
    print("\nTest: Python file operations...")

    # Write a file first
    write_result = await session.file_system.write_file(
        "/tmp/test_python.txt", "Hello from Python test"
    )
    assert write_result.success, "Failed to write test file"

    # Read the file with Python
    code = """
with open('/tmp/test_python.txt', 'r') as f:
    content = f.read()
print(f'File content: {content}')
"""

    # Act
    result = await session.code.run_code(code, "python")

    # Assert
    assert result.success, f"Python file operations failed: {result.error_message}"
    assert (
        "Hello from Python test" in result.result
    ), "Output should contain file content"
    print(f"Python output:\n{result.result}")


@pytest.mark.asyncio
async def test_python_error_handling(session):
    """Test Python error handling."""
    # Arrange
    print("\nTest: Python error handling...")
    code = "x = 1 / 0"  # This will cause a ZeroDivisionError

    # Act
    result = await session.code.run_code(code, "python")

    # Assert
    # The execution should fail or return error in result
    if not result.success:
        print(f"Expected error: {result.error_message}")
        assert (
            "ZeroDivisionError" in result.error_message
            or "division" in result.error_message.lower()
        )
    assert not result.success


@pytest.mark.asyncio
async def test_python_with_timeout(session):
    """Test Python execution with reasonable timeout."""
    # Arrange
    print("\nTest: Python with timeout...")
    code = """
import time
print('Starting...')
time.sleep(1)
print('Completed after 1 second')
"""

    # Act
    result = await session.code.run_code(code, "python")

    # Assert
    assert result.success, f"Python with timeout failed: {result.error_message}"
    assert "Completed" in result.result, "Should complete within timeout"
    print(f"Python output:\n{result.result}")


@pytest.mark.asyncio
async def test_python_context_persistence_within_same_session(session):
    """Test that Python execution context is preserved within the same session (Jupyter-like behavior)."""
    print("\nTest: Python context persistence within the same session...")

    setup_code = """
x = 41

def add(a, b):
    return a + b

print("CONTEXT_SETUP_DONE")
""".strip()

    setup_result = await session.code.run_code(setup_code, "python")
    assert setup_result.success, f"Setup failed: {setup_result.error_message}"
    assert "CONTEXT_SETUP_DONE" in setup_result.result

    use_code = """
print(f"CONTEXT_VALUE:{x + 1}")
print(f"CONTEXT_FUNC:{add(1, 2)}")
""".strip()

    use_result = await session.code.run_code(use_code, "python")
    assert use_result.success, f"Context use failed: {use_result.error_message}"
    assert "CONTEXT_VALUE:42" in use_result.result
    assert "CONTEXT_FUNC:3" in use_result.result

    if setup_result.execution_count is not None and use_result.execution_count is not None:
        assert use_result.execution_count == setup_result.execution_count + 1
