#!/usr/bin/env python3
"""
ci-stable
AgentBay SDK - Enhanced Code Execution Example

This example demonstrates the new enhanced code execution features:
- Multi-format result support (text, HTML, JSON, images, etc.)
- Detailed execution logs (stdout/stderr separation)
- Rich error information
- Execution timing and metadata
- Backward compatibility with existing code
"""

import asyncio
import os
from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def demonstrate_basic_usage(session):
    """Demonstrate basic usage with backward compatibility."""
    print("\n===== BASIC USAGE (BACKWARD COMPATIBLE) =====")
    
    code = """
print('Hello, Enhanced AgentBay!')
result = 2 + 2
print(f'2 + 2 = {result}')
result
"""
    
    result = await session.code.run_code(code, "python")
    print(f"Success: {result.success}")
    print(f"Result: {result.result}")  # Backward compatible property
    print(f"Request ID: {result.request_id}")
    return result


async def demonstrate_rich_outputs(session):
    """Demonstrate various output formats."""
    print("\n===== RICH OUTPUT FORMATS =====")
    
    # Test multiple output types
    code = """
import json
import sys

# Standard output
print("This goes to stdout")

# Error output (if supported)
print("This might go to stderr", file=sys.stderr)

# JSON data
data = {"name": "AgentBay", "version": "2.0", "features": ["enhanced", "multi-format"]}
json_str = json.dumps(data, indent=2)
print("JSON data:")
print(json_str)

# Return structured data
data
"""
    
    result = await session.code.run_code(code, "python")
    
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time}s")
    
    # New enhanced features
    print(f"Number of results: {len(result.results)}")
    print(f"Stdout logs: {len(result.logs.stdout)} entries")
    print(f"Stderr logs: {len(result.logs.stderr)} entries")
    
    # Show results details
    for i, res in enumerate(result.results):
        print(f"Result {i}: formats={res.formats()}, is_main={res.is_main_result}")
        if res.text:
            print(f"  Text: {res.text[:100]}...")
        if res.json:
            print(f"  JSON: {res.json}")
    
    return result


async def demonstrate_data_analysis(session):
    """Demonstrate data analysis with rich outputs."""
    print("\n===== DATA ANALYSIS EXAMPLE =====")
    
    code = """
# Simulate data analysis workflow
data = [
    {"name": "Alice", "age": 25, "score": 85},
    {"name": "Bob", "age": 30, "score": 92},
    {"name": "Charlie", "age": 35, "score": 78},
    {"name": "Diana", "age": 28, "score": 96}
]

print("Analyzing user data...")

# Calculate statistics
total_score = sum(person["score"] for person in data)
avg_score = total_score / len(data)
avg_age = sum(person["age"] for person in data) / len(data)

print(f"Total participants: {len(data)}")
print(f"Average score: {avg_score:.2f}")
print(f"Average age: {avg_age:.2f}")

# Create summary report
report = {
    "summary": {
        "total_participants": len(data),
        "average_score": round(avg_score, 2),
        "average_age": round(avg_age, 2),
        "highest_score": max(person["score"] for person in data),
        "lowest_score": min(person["score"] for person in data)
    },
    "participants": data
}

print("Analysis complete!")
report
"""
    
    result = await session.code.run_code(code, "python")
    
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time}s")
    
    # Check for JSON output
    for res in result.results:
        if res.json:
            print("Found JSON result:")
            print(f"  Participants: {res.json.get('summary', {}).get('total_participants', 'N/A')}")
            print(f"  Average score: {res.json.get('summary', {}).get('average_score', 'N/A')}")
        if res.is_main_result:
            print(f"Main result format: {res.formats()}")
    
    return result


async def demonstrate_error_handling(session):
    """Demonstrate enhanced error handling."""
    print("\n===== ERROR HANDLING =====")
    
    # Test with intentional error
    code = """
print("Starting calculation...")
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f"Caught error: {e}")
    error_info = {
        "error_type": type(e).__name__,
        "error_message": str(e),
        "handled": True
    }
    print("Error handled gracefully")
    error_info
"""
    
    result = await session.code.run_code(code, "python")
    
    print(f"Success: {result.success}")
    
    if result.error:
        print("Error details:")
        print(f"  Name: {result.error.name}")
        print(f"  Value: {result.error.value}")
        print(f"  Traceback: {result.error.traceback[:100]}...")
    else:
        print("No error object (error was handled in code)")
    
    # Check results
    for res in result.results:
        if res.json and "error_type" in res.json:
            print(f"Handled error type: {res.json['error_type']}")
    
    return result


async def demonstrate_execution_logs(session):
    """Demonstrate detailed execution logging."""
    print("\n===== EXECUTION LOGS =====")
    
    code = """
import sys
import time

print("Step 1: Starting process")
time.sleep(0.1)

print("Step 2: Processing data")
for i in range(3):
    print(f"  Processing item {i+1}")
    time.sleep(0.05)

print("Step 3: Finalizing", file=sys.stdout)
print("Warning: This is a test warning", file=sys.stderr)

print("Process completed successfully")
"Final result: SUCCESS"
"""
    
    result = await session.code.run_code(code, "python")
    
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time}s")
    
    print("\nStdout logs:")
    for i, log in enumerate(result.logs.stdout):
        print(f"  {i+1}: {log.strip()}")
    
    print("\nStderr logs:")
    for i, log in enumerate(result.logs.stderr):
        print(f"  {i+1}: {log.strip()}")
    
    print(f"\nFinal result: {result.result}")
    
    return result


async def demonstrate_javascript_enhanced(session):
    """Demonstrate enhanced JavaScript execution."""
    print("\n===== ENHANCED JAVASCRIPT EXECUTION =====")
    
    code = """
console.log("Starting JavaScript enhanced execution");

// Create some data
const users = [
    {id: 1, name: "Alice", active: true},
    {id: 2, name: "Bob", active: false},
    {id: 3, name: "Charlie", active: true}
];

console.log(`Total users: ${users.length}`);

// Process data
const activeUsers = users.filter(u => u.active);
console.log(`Active users: ${activeUsers.length}`);

// Create summary
const summary = {
    total: users.length,
    active: activeUsers.length,
    inactive: users.length - activeUsers.length,
    activeUserNames: activeUsers.map(u => u.name)
};

console.log("Summary created:", JSON.stringify(summary, null, 2));

// Return the summary
summary;
"""
    
    result = await session.code.run_code(code, "javascript")
    
    print(f"Success: {result.success}")
    print(f"Execution time: {result.execution_time}s")
    
    # Show logs
    if result.logs.stdout:
        print("Console output:")
        for log in result.logs.stdout:
            print(f"  {log.strip()}")
    
    # Show results
    for res in result.results:
        if res.json:
            print("JavaScript returned JSON:")
            print(f"  Active users: {res.json.get('active', 'N/A')}")
            print(f"  Active names: {res.json.get('activeUserNames', [])}")
    
    return result


async def main():
    """Main function demonstrating enhanced code execution features."""
    print("🚀 AgentBay Enhanced Code Execution Example")
    
    # Initialize AgentBay client
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    
    # Create session with code_latest image
    print("\n📱 Creating session with code_latest image...")
    params = CreateSessionParams(image_id="code_latest")
    session_result = await agent_bay.create(params)
    
    if not session_result.success:
        print(f"❌ Session creation failed: {session_result.error_message}")
        return
    
    session = session_result.session
    print(f"✅ Session created successfully: {session.session_id}")
    
    try:
        # Demonstrate various enhanced features
        await demonstrate_basic_usage(session)
        await demonstrate_rich_outputs(session)
        await demonstrate_data_analysis(session)
        await demonstrate_error_handling(session)
        await demonstrate_execution_logs(session)
        await demonstrate_javascript_enhanced(session)
        
        print("\n🎉 All enhanced features demonstrated successfully!")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
    
    finally:
        # Clean up session
        print(f"\n🧹 Cleaning up session: {session.session_id}")
        delete_result = await agent_bay.delete(session)
        if delete_result.success:
            print("✅ Session deleted successfully")
        else:
            print(f"❌ Failed to delete session: {delete_result.error_message}")


if __name__ == "__main__":
    asyncio.run(main())