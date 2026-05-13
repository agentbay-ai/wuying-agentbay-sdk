"""
ci-stable

Example demonstrating performance monitoring with AgentBay SDK.

This example shows how to:
- Monitor operation latency
- Track resource usage
- Measure throughput
- Identify performance bottlenecks
- Generate performance reports
"""

import asyncio
import os
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@dataclass
class PerformanceMetric:
    """Performance metric data."""
    operation: str
    start_time: float
    end_time: float
    duration: float
    success: bool
    error: str = ""
    
    @property
    def duration_ms(self) -> float:
        """Get duration in milliseconds."""
        return self.duration * 1000


@dataclass
class PerformanceReport:
    """Performance report with statistics."""
    operation_name: str
    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    durations: List[float] = field(default_factory=list)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100
    
    @property
    def avg_duration(self) -> float:
        """Calculate average duration."""
        if not self.durations:
            return 0.0
        return statistics.mean(self.durations)
    
    @property
    def min_duration(self) -> float:
        """Get minimum duration."""
        if not self.durations:
            return 0.0
        return min(self.durations)
    
    @property
    def max_duration(self) -> float:
        """Get maximum duration."""
        if not self.durations:
            return 0.0
        return max(self.durations)
    
    @property
    def p95_duration(self) -> float:
        """Calculate 95th percentile duration."""
        if not self.durations:
            return 0.0
        sorted_durations = sorted(self.durations)
        index = int(len(sorted_durations) * 0.95)
        return sorted_durations[index] if index < len(sorted_durations) else sorted_durations[-1]


class PerformanceMonitor:
    """Monitor and track performance metrics."""
    
    def __init__(self):
        self.metrics: List[PerformanceMetric] = []
        self.reports: Dict[str, PerformanceReport] = {}
    
    async def measure(self, operation_name: str, func, *args, **kwargs):
        """Measure operation performance."""
        start_time = time.time()
        error = ""
        success = False
        result = None
        
        try:
            result = await func(*args, **kwargs)
            success = True
        except Exception as e:
            error = str(e)
            raise
        finally:
            end_time = time.time()
            duration = end_time - start_time
            
            # Record metric
            metric = PerformanceMetric(
                operation=operation_name,
                start_time=start_time,
                end_time=end_time,
                duration=duration,
                success=success,
                error=error
            )
            self.metrics.append(metric)
            
            # Update report
            if operation_name not in self.reports:
                self.reports[operation_name] = PerformanceReport(operation_name=operation_name)
            
            report = self.reports[operation_name]
            report.total_operations += 1
            if success:
                report.successful_operations += 1
                report.durations.append(duration)
            else:
                report.failed_operations += 1
        
        return result
    
    def print_summary(self):
        """Print performance summary."""
        print("\n" + "=" * 60)
        print("Performance Summary")
        print("=" * 60)
        
        for operation_name, report in self.reports.items():
            print(f"\n📊 {operation_name}")
            print(f"   Total Operations: {report.total_operations}")
            print(f"   Successful: {report.successful_operations}")
            print(f"   Failed: {report.failed_operations}")
            print(f"   Success Rate: {report.success_rate:.1f}%")
            
            if report.durations:
                print(f"   Avg Duration: {report.avg_duration*1000:.2f}ms")
                print(f"   Min Duration: {report.min_duration*1000:.2f}ms")
                print(f"   Max Duration: {report.max_duration*1000:.2f}ms")
                print(f"   P95 Duration: {report.p95_duration*1000:.2f}ms")
    
    def get_slowest_operations(self, limit: int = 5) -> List[PerformanceMetric]:
        """Get the slowest operations."""
        sorted_metrics = sorted(self.metrics, key=lambda m: m.duration, reverse=True)
        return sorted_metrics[:limit]
    
    def print_slowest_operations(self, limit: int = 5):
        """Print the slowest operations."""
        print(f"\n🐌 Top {limit} Slowest Operations:")
        slowest = self.get_slowest_operations(limit)
        
        for i, metric in enumerate(slowest, 1):
            status = "✅" if metric.success else "❌"
            print(f"   {i}. {status} {metric.operation}: {metric.duration_ms:.2f}ms")


async def benchmark_command_execution(session, monitor: PerformanceMonitor, num_iterations: int = 10):
    """Benchmark command execution performance."""
    print(f"\n⚡ Benchmarking command execution ({num_iterations} iterations)...")
    
    commands = [
        "echo 'test'",
        "hostname",
        "date",
        "whoami"
    ]
    
    for cmd in commands:
        for i in range(num_iterations):
            await monitor.measure(
                f"command_{cmd.split()[0]}",
                session.command.execute_command,
                cmd
            )
    
    print(f"✅ Benchmark completed")


async def benchmark_file_operations(session, monitor: PerformanceMonitor, num_iterations: int = 10):
    """Benchmark file operations performance."""
    print(f"\n📁 Benchmarking file operations ({num_iterations} iterations)...")
    
    for i in range(num_iterations):
        file_path = f"/tmp/perf_test_{i}.txt"
        content = f"Performance test content {i}" * 100
        
        # Benchmark write
        await monitor.measure(
            "file_write",
            session.file_system.write_file,
            file_path,
            content
        )
        
        # Benchmark read
        await monitor.measure(
            "file_read",
            session.file_system.read_file,
            file_path
        )
    
    print(f"✅ Benchmark completed")


async def benchmark_parallel_operations(session, monitor: PerformanceMonitor):
    """Benchmark parallel operations."""
    print(f"\n⚡ Benchmarking parallel operations...")
    
    async def parallel_commands():
        tasks = [
            session.command.execute_command("echo 'test 1'"),
            session.command.execute_command("echo 'test 2'"),
            session.command.execute_command("echo 'test 3'"),
        ]
        await asyncio.gather(*tasks)
    
    await monitor.measure("parallel_commands", parallel_commands)
    
    print(f"✅ Benchmark completed")


async def main():
    """Main function demonstrating performance monitoring."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    
    try:
        print("=" * 60)
        print("Performance Monitoring Example")
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
        
        # Initialize performance monitor
        monitor = PerformanceMonitor()
        
        # Benchmark 1: Command execution
        print("\n" + "=" * 60)
        print("Benchmark 1: Command Execution")
        print("=" * 60)
        
        await benchmark_command_execution(session, monitor, num_iterations=5)
        
        # Benchmark 2: File operations
        print("\n" + "=" * 60)
        print("Benchmark 2: File Operations")
        print("=" * 60)
        
        await benchmark_file_operations(session, monitor, num_iterations=5)
        
        # Benchmark 3: Parallel operations
        print("\n" + "=" * 60)
        print("Benchmark 3: Parallel Operations")
        print("=" * 60)
        
        await benchmark_parallel_operations(session, monitor)
        
        # Print results
        monitor.print_summary()
        monitor.print_slowest_operations(limit=10)
        
        print("\n✅ Performance monitoring examples completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if session:
            print("\n🧹 Cleaning up session...")
            await agent_bay.delete(session)
            print("✅ Session deleted")


if __name__ == "__main__":
    asyncio.run(main())

