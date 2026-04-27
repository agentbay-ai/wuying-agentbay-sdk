"""Integration tests for CodeSpace cross-language interoperability."""
# ci-stable

import pytest

from agentbay import CreateSessionParams


@pytest.fixture
async def session(make_session):
    """Create a session with code_latest image."""
    lc = await make_session(params=CreateSessionParams(image_id="code_latest"))
    return lc._result.session


@pytest.mark.asyncio
async def test_python_js_file_interop(session):
    """Test Python and JavaScript file interaction."""
    # Arrange
    print("\nTest: Python and JavaScript file interop...")

    # Python writes a file
    python_code = """
import json
data = {'message': 'Hello from Python', 'value': 42}
with open('/tmp/interop_data.json', 'w') as f:
    json.dump(data, f)
print('Python wrote data')
"""

    # Act - Python writes
    py_result = await session.code.run_code(python_code, "python")
    assert py_result.success, f"Python write failed: {py_result.error_message}"
    print(f"Python output: {py_result.result}")

    # JavaScript reads
    js_code = """
const fs = require('fs');
const data = JSON.parse(fs.readFileSync('/tmp/interop_data.json', 'utf8'));
console.log(`JavaScript read: ${data.message}, value: ${data.value}`);
"""

    js_result = await session.code.run_code(js_code, "javascript")

    # Assert
    assert js_result.success, f"JavaScript read failed: {js_result.error_message}"
    assert (
        "Hello from Python" in js_result.result
    ), "JavaScript should read Python's data"
    assert "42" in js_result.result, "JavaScript should read Python's value"
    print(f"JavaScript output: {js_result.result}")


@pytest.mark.asyncio
async def test_cross_language_data_exchange(session):
    """Test data exchange between languages."""
    # Arrange
    print("\nTest: Cross-language data exchange...")

    # JavaScript writes
    js_code = """
const fs = require('fs');
const data = {language: 'JavaScript', timestamp: Date.now()};
fs.writeFileSync('/tmp/js_data.json', JSON.stringify(data));
console.log('JavaScript wrote:', JSON.stringify(data));
"""

    # Act - JavaScript writes
    js_result = await session.code.run_code(js_code, "javascript")
    assert js_result.success, f"JavaScript write failed: {js_result.error_message}"
    print(f"JavaScript output: {js_result.result}")

    # Python reads and processes
    python_code = """
import json
with open('/tmp/js_data.json', 'r') as f:
    data = json.load(f)
print(f"Python read: {data['language']}, timestamp: {data['timestamp']}")
"""

    py_result = await session.code.run_code(python_code, "python")

    # Assert
    assert py_result.success, f"Python read failed: {py_result.error_message}"
    assert "JavaScript" in py_result.result, "Python should read JavaScript's data"
    print(f"Python output: {py_result.result}")


@pytest.mark.asyncio
async def test_sequential_execution(session):
    """Test sequential execution of different language codes."""
    # Arrange
    print("\nTest: Sequential execution...")

    # Act - Execute multiple languages in sequence
    # 1. Python
    py_result = await session.code.run_code("print('Step 1: Python')", "python")
    assert py_result.success, "Python step failed"
    print(f"Step 1: {py_result.result}")

    # 2. JavaScript
    js_result = await session.code.run_code(
        "console.log('Step 2: JavaScript')", "javascript"
    )
    assert js_result.success, "JavaScript step failed"
    print(f"Step 2: {js_result.result}")

    # 3. Python again
    py_result2 = await session.code.run_code("print('Step 3: Python again')", "python")
    assert py_result2.success, "Second Python step failed"
    print(f"Step 3: {py_result2.result}")

    # Assert
    print("Sequential execution completed successfully")
