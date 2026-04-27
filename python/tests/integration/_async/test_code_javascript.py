"""Integration tests for CodeSpace JavaScript execution functionality."""
# ci-stable

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def session(make_session):
    """Create a session with code_latest image."""
    lc = await make_session(params=CreateSessionParams(image_id="code_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_run_simple_js_code(session):
    """Test simple JavaScript code execution."""
    # Arrange
    print("\nTest: Simple JavaScript code execution...")
    code = "console.log('Hello from JavaScript');\nconst result = 2 + 2;\nconsole.log(`Result: ${result}`);"

    # Act
    result = await session.code.run_code(code, "javascript")

    # Assert
    assert result.success, f"JavaScript execution failed: {result.error_message}"
    assert result.result is not None, "Result should not be None"
    print(f"JavaScript output:\n{result.result}")


@pytest.mark.asyncio
async def test_js_with_requires(session):
    """Test JavaScript code with requires."""
    # Arrange
    print("\nTest: JavaScript with requires...")
    code = """
const os = require('os');
const data = {
    platform: os.platform(),
    arch: os.arch(),
    nodeVersion: process.version
};
console.log(JSON.stringify(data, null, 2));
"""

    # Act
    result = await session.code.run_code(code, "javascript")

    # Assert
    assert result.success, f"JavaScript with requires failed: {result.error_message}"
    assert result.result is not None, "Result should not be None"
    assert "platform" in result.result, "Output should contain platform"
    print(f"JavaScript output:\n{result.result}")


@pytest.mark.asyncio
async def test_js_file_operations(session):
    """Test JavaScript file operations."""
    # Arrange
    print("\nTest: JavaScript file operations...")

    # Write a file first
    write_result = await session.file_system.write_file(
        "/tmp/test_js.txt", "Hello from JS test"
    )
    assert write_result.success, "Failed to write test file"

    # Read the file with JavaScript
    code = """
const fs = require('fs');
const content = fs.readFileSync('/tmp/test_js.txt', 'utf8');
console.log(`File content: ${content}`);
"""

    # Act
    result = await session.code.run_code(code, "javascript")

    # Assert
    assert result.success, f"JavaScript file operations failed: {result.error_message}"
    assert "Hello from JS test" in result.result, "Output should contain file content"
    print(f"JavaScript output:\n{result.result}")


@pytest.mark.asyncio
async def test_js_error_handling(session):
    """Test JavaScript error handling."""
    # Arrange
    print("\nTest: JavaScript error handling...")
    code = "throw new Error('Test error');"

    # Act
    result = await session.code.run_code(code, "javascript")

    # Assert
    # The execution should fail or return error in result
    if not result.success:
        print(f"Expected error: {result.error_message}")
        assert (
            "Error" in result.error_message or "error" in result.error_message.lower()
        )
    assert not result.success


@pytest.mark.asyncio
async def test_js_with_timeout(session):
    """Test JavaScript execution with reasonable timeout."""
    # Arrange
    print("\nTest: JavaScript with timeout...")
    code = """
console.log('Starting...');
setTimeout(() => {
    console.log('This should not appear');
}, 5000);
console.log('Completed immediately');
"""

    # Act
    result = await session.code.run_code(code, "javascript")

    # Assert
    assert result.success, f"JavaScript with timeout failed: {result.error_message}"
    assert "Completed" in result.result, "Should complete within timeout"
    print(f"JavaScript output:\n{result.result}")
