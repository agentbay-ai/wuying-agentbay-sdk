"""
ci-stable
Example demonstrating logging and monitoring with AgentBay SDK.

This example shows how to:
- Set up structured logging
- Monitor session metrics
- Track operation performance
- Log errors and warnings
- Create monitoring dashboards
- Export logs for analysis
"""

import asyncio
import os
import time
import json
from typing import Dict, Any, List
from datetime import datetime

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


class SessionLogger:
    """Logger for session operations."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.logs: List[Dict[str, Any]] = []
    
    def log(self, level: str, message: str, **kwargs):
        """Log a message with additional context."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "level": level,
            "message": message,
            **kwargs
        }
        self.logs.append(log_entry)
        
        # Print to console
        emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "SUCCESS": "✅"}.get(level, "📝")
        print(f"{emoji} [{level}] {message}")
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.log("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.log("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.log("ERROR", message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message."""
        self.log("SUCCESS", message, **kwargs)
    
    def export_logs(self, filename: str):
        """Export logs to JSON file."""
        with open(filename, 'w') as f:
            json.dump(self.logs, f, indent=2)
        print(f"\n💾 Logs exported to {filename}")


class PerformanceMonitor:
    """Monitor performance metrics."""
    
    def __init__(self):
        self.metrics: List[Dict[str, Any]] = []
    
    async def measure(self, operation_name: str, func, *args, **kwargs):
        """Measure operation performance."""
        start_time = time.time()
        error = None
        result = None
        
        try:
            result = await func(*args, **kwargs)
        except Exception as e:
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            metric = {
                "operation": operation_name,
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
                "success": error is None,
                "error": error
            }
            self.metrics.append(metric)
            
            status = "✅" if error is None else "❌"
            print(f"{status} {operation_name}: {duration:.3f}s")
        
        return result
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        if not self.metrics:
            return {}
        
        total_operations = len(self.metrics)
        successful_operations = sum(1 for m in self.metrics if m["success"])
        total_duration = sum(m["duration"] for m in self.metrics)
        avg_duration = total_duration / total_operations
        
        return {
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": total_operations - successful_operations,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "success_rate": (successful_operations / total_operations) * 100
        }
    
    def print_summary(self):
        """Print performance summary."""
        summary = self.get_summary()
        
        print("\n" + "=" * 60)
        print("Performance Summary")
        print("=" * 60)
        print(f"Total Operations: {summary.get('total_operations', 0)}")
        print(f"Successful: {summary.get('successful_operations', 0)}")
        print(f"Failed: {summary.get('failed_operations', 0)}")
        print(f"Total Duration: {summary.get('total_duration', 0):.3f}s")
        print(f"Average Duration: {summary.get('average_duration', 0):.3f}s")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")


async def monitored_command_execution(session, command: str, logger: SessionLogger, monitor: PerformanceMonitor):
    """Execute command with logging and monitoring."""
    logger.info(f"Executing command: {command}")
    
    async def execute():
        result = await session.command.execute_command(command)
        if result.success:
            logger.success(f"Command completed", output_length=len(result.output))
            return result
        else:
            logger.error(f"Command failed: {result.error_message}")
            raise Exception(result.error_message)
    
    return await monitor.measure(f"command: {command[:30]}", execute)


async def monitored_file_operation(session, file_path: str, content: str, logger: SessionLogger, monitor: PerformanceMonitor):
    """Perform file operation with logging and monitoring."""
    logger.info(f"Writing file: {file_path}", size=len(content))
    
    async def write():
        result = await session.file_system.write_file(file_path, content)
        if result.success:
            logger.success(f"File written successfully")
            return result
        else:
            logger.error(f"File write failed: {result.error_message}")
            raise Exception(result.error_message)
    
    return await monitor.measure(f"file_write: {file_path}", write)


async def main():
    """Main function demonstrating logging and monitoring."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    session = None
    
    try:
        print("=" * 60)
        print("Logging and Monitoring Example")
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
        
        # Initialize logger and monitor
        logger = SessionLogger(session.session_id)
        monitor = PerformanceMonitor()
        
        logger.info("Session initialized", image_id="linux_latest")
        
        # Example 1: Monitored command execution
        print("\n" + "=" * 60)
        print("Example 1: Monitored Command Execution")
        print("=" * 60)
        
        commands = [
            "hostname",
            "whoami",
            "date",
            "uname -a"
        ]
        
        for cmd in commands:
            try:
                await monitored_command_execution(session, cmd, logger, monitor)
            except Exception as e:
                logger.error(f"Command execution failed", command=cmd, error=str(e))
        
        # Example 2: Monitored file operations
        print("\n" + "=" * 60)
        print("Example 2: Monitored File Operations")
        print("=" * 60)
        
        for i in range(3):
            file_path = f"/tmp/monitored_file_{i}.txt"
            content = f"This is test file {i} with monitoring"
            
            try:
                await monitored_file_operation(session, file_path, content, logger, monitor)
            except Exception as e:
                logger.error(f"File operation failed", file_path=file_path, error=str(e))
        
        # Example 3: Performance summary
        print("\n" + "=" * 60)
        print("Example 3: Performance Summary")
        print("=" * 60)
        
        monitor.print_summary()
        
        # Example 4: Export logs
        print("\n" + "=" * 60)
        print("Example 4: Export Logs")
        print("=" * 60)
        
        logger.export_logs("/tmp/session_logs.json")
        
        print("\n✅ Logging and monitoring examples completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if session:
            print("\n🧹 Cleaning up session...")
            await agent_bay.delete(session)
            print("✅ Session deleted")


if __name__ == "__main__":
    asyncio.run(main())

