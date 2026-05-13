"""
Example demonstrating retry mechanisms with AgentBay SDK.

This example shows how to:
- Implement exponential backoff retry
- Handle transient failures
- Configure retry policies
- Track retry attempts
- Implement circuit breaker pattern
"""

import asyncio
import os
import time
from typing import Callable, Any, Optional
from dataclasses import dataclass

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams
from agentbay import AgentBayError


@dataclass
class RetryPolicy:
    """Configuration for retry behavior."""
    max_attempts: int = 3
    initial_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


async def retry_with_exponential_backoff(
    func: Callable,
    policy: RetryPolicy,
    *args,
    **kwargs
) -> Any:
    """Retry a function with exponential backoff."""
    
    for attempt in range(policy.max_attempts):
        try:
            print(f"  Attempt {attempt + 1}/{policy.max_attempts}...")
            result = await func(*args, **kwargs)
            print(f"  ✅ Success on attempt {attempt + 1}")
            return result
            
        except Exception as e:
            print(f"  ❌ Attempt {attempt + 1} failed: {e}")
            
            if attempt < policy.max_attempts - 1:
                # Calculate delay with exponential backoff
                delay = min(
                    policy.initial_delay * (policy.exponential_base ** attempt),
                    policy.max_delay
                )
                
                # Add jitter to prevent thundering herd
                if policy.jitter:
                    import random
                    delay = delay * (0.5 + random.random())
                
                print(f"  ⏳ Waiting {delay:.2f} seconds before retry...")
                await asyncio.sleep(delay)
            else:
                print(f"  ❌ All {policy.max_attempts} attempts failed")
                raise


async def retry_command_execution(session, command: str, policy: RetryPolicy):
    """Execute a command with retry logic."""
    print(f"\n🔄 Executing command with retry: {command}")
    
    async def execute():
        result = await session.command.execute_command(command)
        if not result.success:
            raise Exception(f"Command failed: {result.error_message}")
        return result
    
    try:
        result = await retry_with_exponential_backoff(execute, policy)
        print(f"✅ Command output: {result.output.strip()[:50]}")
        return result
    except Exception as e:
        print(f"❌ Command failed after all retries: {e}")
        return None


async def retry_file_operation(session, file_path: str, content: str, policy: RetryPolicy):
    """Perform file operation with retry logic."""
    print(f"\n📁 Writing file with retry: {file_path}")
    
    async def write_file():
        result = await session.file_system.write_file(file_path, content)
        if not result.success:
            raise Exception(f"File write failed: {result.error_message}")
        return result
    
    try:
        result = await retry_with_exponential_backoff(write_file, policy)
        print(f"✅ File written successfully")
        return result
    except Exception as e:
        print(f"❌ File operation failed after all retries: {e}")
        return None


class CircuitBreaker:
    """Circuit breaker pattern implementation."""
    
    def __init__(self, failure_threshold: int = 3, timeout: float = 60.0):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    def is_open(self) -> bool:
        """Check if circuit is open."""
        if self.state == "open":
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = "half-open"
                print("  🔄 Circuit breaker: half-open (testing)")
                return False
            return True
        return False
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        if self.is_open():
            print("  ⛔ Circuit breaker: open (blocking call)")
            raise Exception("Circuit breaker is open")
        
        try:
            result = await func(*args, **kwargs)
            
            # Success - reset failure count
            if self.state == "half-open":
                self.state = "closed"
                print("  ✅ Circuit breaker: closed (recovered)")
            self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                print(f"  ⛔ Circuit breaker: open (threshold reached: {self.failure_count})")
            
            raise


async def demonstrate_circuit_breaker(session):
    """Demonstrate circuit breaker pattern."""
    print("\n⚡ Demonstrating Circuit Breaker Pattern...")
    
    circuit_breaker = CircuitBreaker(failure_threshold=3, timeout=5.0)
    
    # Use a counter to simulate an operation that initially fails then recovers
    call_count = 0

    async def unreliable_operation():
        nonlocal call_count
        call_count += 1
        # First 4 calls fail, then recover
        if call_count <= 4:
            raise Exception(f"Simulated failure (call {call_count})")
        return f"Success on call {call_count}"
    
    # Phase 1: Trigger circuit breaker with failures
    print("\n  Phase 1: Triggering failures...")
    for i in range(5):
        print(f"\n  Call {i + 1}:")
        try:
            result = await circuit_breaker.call(unreliable_operation)
            print(f"  ✅ Result: {result}")
        except Exception as e:
            print(f"  ❌ Call failed: {e}")
        
        await asyncio.sleep(0.5)
    
    # Phase 2: Wait for circuit breaker timeout, then test recovery
    print("\n  Phase 2: Waiting for circuit breaker timeout (5s)...")
    await asyncio.sleep(5.5)
    
    print(f"\n  Circuit breaker state: {circuit_breaker.state}")
    print("\n  Testing recovery after timeout:")
    for i in range(3):
        print(f"\n  Recovery call {i + 1}:")
        try:
            result = await circuit_breaker.call(unreliable_operation)
            print(f"  ✅ Result: {result}")
        except Exception as e:
            print(f"  ❌ Call failed: {e}")
        
        await asyncio.sleep(0.5)
    
    print(f"\n  Final circuit breaker state: {circuit_breaker.state}")


async def main():
    """Main function demonstrating retry mechanisms."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    
    try:
        print("=" * 60)
        print("Retry Mechanism Example")
        print("=" * 60)
        
        # Create session
        print("\nCreating session...")
        params = CreateSessionParams(image_id="linux_latest")
        result = await agent_bay.create(params)
        
        if not result.success or not result.session:
            print(f"❌ Failed to create session: {result.error_message}")
            return
        
        session = result.session
        print(f"✅ Session created: {session.session_id}")
        
        # Example 1: Basic retry with exponential backoff
        print("\n" + "=" * 60)
        print("Example 1: Exponential Backoff Retry")
        print("=" * 60)
        
        policy = RetryPolicy(max_attempts=3, initial_delay=1.0)
        await retry_command_execution(session, "echo 'Hello World'", policy)
        
        # Example 2: Retry file operation
        print("\n" + "=" * 60)
        print("Example 2: Retry File Operation")
        print("=" * 60)
        
        await retry_file_operation(
            session,
            "/tmp/retry_test.txt",
            "This is a test with retry",
            policy
        )
        
        # Example 3: Custom retry policy
        print("\n" + "=" * 60)
        print("Example 3: Custom Retry Policy")
        print("=" * 60)
        
        custom_policy = RetryPolicy(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=10.0,
            exponential_base=2.0,
            jitter=True
        )
        
        await retry_command_execution(session, "date", custom_policy)
        
        # Example 4: Circuit breaker pattern
        print("\n" + "=" * 60)
        print("Example 4: Circuit Breaker Pattern")
        print("=" * 60)
        
        await demonstrate_circuit_breaker(session)
        
        print("\n✅ Retry mechanism examples completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if session:
            print("\n🧹 Cleaning up session...")
            await agent_bay.delete(session)
            print("✅ Session deleted")


if __name__ == "__main__":
    asyncio.run(main())

