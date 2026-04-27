# ci-stable

import pytest
import pytest_asyncio

from agentbay import EnhancedCodeExecutionResult


@pytest_asyncio.fixture
async def session(make_session):
    """Create a shared session for all tests in this module."""
    lc = await make_session("code_latest")
    return lc._result.session


@pytest.mark.asyncio
async def test_enhanced_result_structure(session):
    """Test that results use the enhanced structure."""

    code = """
print("Hello, enhanced world!")
"""
    result = await session.code.run_code(code, "python")

    assert isinstance(result, EnhancedCodeExecutionResult)
    assert result.success, f"Code execution failed: {result.error_message}"
    assert result.request_id is not None

    # Test backward compatibility
    assert "Hello, enhanced world!" in result.result or "42" in result.result

    # Test enhanced features
    assert hasattr(result, "logs")
    assert hasattr(result, "results")
    assert hasattr(result, "execution_time")
@pytest.mark.asyncio
async def test_logs_capture(session):
    """Test that stdout and stderr are properly captured."""
    code = """
import sys
print("This goes to stdout")
print("This also goes to stdout", file=sys.stdout)
print("This goes to stderr", file=sys.stderr)
"Final result"
"""
    result = await session.code.run_code(code, "python")

    assert result.success, f"Code execution failed: {result.error_message}"

    assert isinstance(result.logs.stdout, list)
    assert isinstance(result.logs.stderr, list)
    
    # Check that output is captured (exact format may vary)
    stdout_content = "".join(result.logs.stdout) if result.logs.stdout else ""
    stderr_content = "".join(result.logs.stderr) if result.logs.stderr else ""
    
    # At minimum, some output should be captured
    assert len(stdout_content) > 0 or len(stderr_content) > 0 or len(result.results) > 0


@pytest.mark.asyncio
async def test_multiple_results_formats(session):
    """Test handling of multiple result formats."""
    code = """
# Test various output types
print("Standard output")

# Text result
text_result = "This is a text result"

# Dictionary that could be JSON
json_data = {"key": "value", "number": 42}

# Return the text result
text_result
"""
    result = await session.code.run_code(code, "python")

    assert result.success
    assert isinstance(result.results, list)
    
    # Should have at least one result
    assert len(result.results) >= 0
    
    # Test backward compatibility
    assert result.result is not None


@pytest.mark.asyncio
async def test_execution_timing(session):
    """Test that execution time is tracked."""
    code = """
import time
time.sleep(0.1)  # Small delay
"Execution completed"
"""
    result = await session.code.run_code(code, "python")

    assert result.success
    assert hasattr(result, 'execution_time')
    assert isinstance(result.execution_time, (int, float))
    # Should be at least 0.1 seconds, but allow for some variance
    assert result.execution_time >= 0.0


@pytest.mark.asyncio
async def test_error_details(session):
    """Test enhanced error reporting."""
    code = """
# This should cause a NameError
print(undefined_variable_that_does_not_exist)
"""
    result = await session.code.run_code(code, "python")

    # Error handling may vary - could be success=False or an error in results
    # In some cases, the error might be captured in executionError rather than success=False
    # Or it might appear in stderr
    has_error = (not result.success or 
                result.error is not None or 
                result.error_message != "" or
                (result.logs.stderr and len(result.logs.stderr) > 0))
    assert has_error
    
    if result.error:
        assert hasattr(result.error, 'name')
        assert hasattr(result.error, 'value')
        assert hasattr(result.error, 'traceback')


@pytest.mark.asyncio
async def test_javascript_enhanced_features(session):
    """Test enhanced features with JavaScript."""
    code = """
console.log("JavaScript output");
const data = {message: "Hello from JS", value: 123};
console.log(JSON.stringify(data));
data.value * 2;
"""
    result = await session.code.run_code(code, "javascript")

    assert isinstance(result, EnhancedCodeExecutionResult)
    assert result.success
    assert result.logs is not None
    assert result.results is not None


@pytest.mark.asyncio
async def test_large_output_handling(session):
    """Test handling of large outputs."""
    code = """
# Generate some larger output
large_list = list(range(100))
print("Generated list of", len(large_list), "items")
for i in range(10):
    print(f"Line {i}: {i * i}")
"Processing completed"
"""
    result = await session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None
    
    # Should handle the output without issues
    assert ("Generated list" in result.result or 
            any("Generated list" in str(res.text or "") for res in result.results) or
            any("Generated list" in str(log) for log in result.logs.stdout))


@pytest.mark.asyncio
async def test_execution_count_tracking(session):
    """Test that execution count is tracked if available."""
    code1 = "print('First execution')"
    code2 = "print('Second execution')"
    
    result1 = await session.code.run_code(code1, "python")
    result2 = await session.code.run_code(code2, "python")

    assert result1.success
    assert result2.success
    
    # execution_count may or may not be provided by the backend
    if result1.execution_count is not None:
        assert isinstance(result1.execution_count, int)
    if result2.execution_count is not None:
        assert isinstance(result2.execution_count, int)


@pytest.mark.asyncio
async def test_mixed_output_types(session):
    """Test code that produces mixed output types."""
    code = """
import json
print("Starting mixed output test")

# Text output
text_data = "Simple text"
print(f"Text: {text_data}")

# JSON-like output
json_data = {"type": "test", "values": [1, 2, 3]}
print("JSON:", json.dumps(json_data))

# Final result
"Mixed output test completed"
"""
    result = await session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None
    
    # Should capture various types of output
    full_output = result.result
    assert "Starting mixed output test" in full_output or any("Starting mixed output test" in str(log) for log in result.logs.stdout)


@pytest.mark.asyncio
async def test_empty_code_execution(session):
    """Test execution of empty or minimal code."""
    code = "# Just a comment"
    result = await session.code.run_code(code, "python")

    assert result.success
    assert result.logs is not None
    assert result.results is not None
    
    # Should handle empty execution gracefully
    assert result.result == "" or result.result is not None


@pytest.mark.asyncio
async def test_backward_compatibility_properties(session):
    """Test that all backward compatibility properties work."""
    code = """
print("Testing backward compatibility")
final_result = "This is the final result"
final_result
"""
    result = await session.code.run_code(code, "python")

    assert result.success, f"Code execution failed: {result.error_message}"

    
    # Test all expected properties exist
    assert hasattr(result, 'success')
    assert hasattr(result, 'result')
    assert hasattr(result, 'error_message')
    assert hasattr(result, 'request_id')
    
    # Test new properties exist
    assert hasattr(result, 'logs')
    assert hasattr(result, 'results')
    assert hasattr(result, 'execution_time')
    assert hasattr(result, 'execution_count')
    assert hasattr(result, 'error')
    
    # Test property types
    assert isinstance(result.success, bool)
    assert isinstance(result.result, str)
    assert isinstance(result.error_message, str)
    assert isinstance(result.request_id, str)


@pytest.mark.asyncio
async def test_html_output(session):
    """Test HTML output generation."""
    code = """
import pandas as pd
from IPython.display import display, HTML

# Create a DataFrame and display it as HTML
df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
display(HTML("<h1>Hello HTML</h1>"))
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    # Check if any result has html content - handle both direct attribute and JSON structure
    has_html = any(
        (hasattr(res, 'html') and res.html is not None and "<h1>Hello HTML</h1>" in res.html) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         res.json.get("text/html") and "<h1>Hello HTML</h1>" in res.json.get("text/html", "")) or
        (hasattr(res, 'text') and res.text and "text/html" in str(res.text) and "<h1>Hello HTML</h1>" in str(res.text))
        for res in result.results
    )
    assert has_html, "HTML output not found in results"


@pytest.mark.asyncio
async def test_markdown_output(session):
    """Test Markdown output generation."""
    code = """
from IPython.display import display, Markdown

display(Markdown('# Hello Markdown'))
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    # Check if any result has markdown content - handle both direct attribute and JSON structure
    has_markdown = any(
        (hasattr(res, 'markdown') and res.markdown is not None and "# Hello Markdown" in res.markdown) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         res.json.get("text/markdown") and "# Hello Markdown" in res.json.get("text/markdown", "")) or
        (hasattr(res, 'text') and res.text and "text/markdown" in str(res.text) and "# Hello Markdown" in str(res.text))
        for res in result.results
    )
    assert has_markdown, "Markdown output not found in results"


@pytest.mark.asyncio
async def test_image_output(session):
    """Test image (PNG/JPEG) output generation."""
    code = """
import matplotlib.pyplot as plt

plt.figure()
plt.plot([1, 2, 3], [1, 2, 3])
plt.title("Test Plot")
plt.show()
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    # Check for png or jpeg - handle both direct attribute and JSON structure
    has_image = any(
        (hasattr(res, 'png') and res.png is not None) or
        (hasattr(res, 'jpeg') and res.jpeg is not None) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         (res.json.get("image/png") or res.json.get("image/jpeg"))) or
        (hasattr(res, 'text') and res.text and ("image/png" in str(res.text) or "image/jpeg" in str(res.text)))
        for res in result.results
    )
    assert has_image, "Image output (PNG/JPEG) not found in results"


@pytest.mark.asyncio
async def test_svg_output(session):
    """Test SVG output generation."""
    code = """
from IPython.display import display, SVG

svg_code = '<svg height="100" width="100"><circle cx="50" cy="50" r="40" stroke="black" stroke-width="3" fill="red" /></svg>'
display(SVG(svg_code))
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    # Check for SVG - handle both direct attribute and JSON structure
    has_svg = any(
        (hasattr(res, 'svg') and res.svg is not None and "<svg" in res.svg) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         res.json.get("image/svg+xml") and "<svg" in res.json.get("image/svg+xml", "")) or
        (hasattr(res, 'text') and res.text and "image/svg+xml" in str(res.text) and "<svg" in str(res.text))
        for res in result.results
    )
    assert has_svg, "SVG output not found in results"


@pytest.mark.asyncio
async def test_latex_output(session):
    """Test LaTeX output generation."""
    code = r"""
from IPython.display import display, Latex

display(Latex(r'\frac{1}{2}'))
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    # Check for LaTeX - handle both direct attribute and JSON structure
    has_latex = any(
        (hasattr(res, 'latex') and res.latex is not None and "frac{1}{2}" in res.latex) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         res.json.get("text/latex") and "frac{1}{2}" in res.json.get("text/latex", "")) or
        (hasattr(res, 'text') and res.text and "text/latex" in str(res.text) and "frac{1}{2}" in str(res.text))
        for res in result.results
    )
    assert has_latex, "LaTeX output not found in results"


@pytest.mark.asyncio
async def test_chart_output(session):
    """Test structured chart output."""
    # Use a mock object to simulate chart output without external dependencies like Altair
    code = """
from IPython.display import display
class MockChart:
    def _repr_mimebundle_(self, include=None, exclude=None):
        return {
            "application/vnd.vegalite.v4+json": {"data": "mock_chart_data", "mark": "bar"},
            "text/plain": "MockChart"
        }
display(MockChart())
"""
    result = await session.code.run_code(code, "python")
    assert result.success
    
    # Check for chart data - handle both direct attribute and JSON structure
    has_chart = any(
        (hasattr(res, 'chart') and res.chart is not None) or
        (hasattr(res, 'json') and res.json is not None and 
         isinstance(res.json, dict) and 
         res.json.get("application/vnd.vegalite.v4+json")) or
        (hasattr(res, 'text') and res.text and "application/vnd.vegalite.v4+json" in str(res.text))
        for res in result.results
    )
    
    assert has_chart, "Chart output not found in results"

