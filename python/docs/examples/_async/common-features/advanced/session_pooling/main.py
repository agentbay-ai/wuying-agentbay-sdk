"""
ci-stable
Example demonstrating session pooling with AgentBay SDK.

This example shows how to:
- Create a pool of reusable sessions
- Acquire and release sessions from the pool
- Manage pool size and limits
- Handle session lifecycle in a pool
- Implement connection pooling patterns
"""

import asyncio
import os
from typing import Optional, List
from dataclasses import dataclass
from datetime import datetime

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


@dataclass
class PooledSession:
    """Wrapper for a pooled session."""
    session: any
    created_at: datetime
    last_used: datetime
    in_use: bool = False


class SessionPool:
    """Pool manager for AgentBay sessions."""
    
    def __init__(
        self,
        agent_bay: AsyncAgentBay,
        min_size: int = 2,
        max_size: int = 5,
        image_id: str = "linux_latest"
    ):
        self.agent_bay = agent_bay
        self.min_size = min_size
        self.max_size = max_size
        self.image_id = image_id
        self.pool: List[PooledSession] = []
        self.lock = asyncio.Lock()
    
    async def initialize(self):
        """Initialize the pool with minimum number of sessions."""
        print(f"\n🏊 Initializing session pool (min={self.min_size}, max={self.max_size})...")
        
        for i in range(self.min_size):
            session = await self._create_session()
            if session:
                print(f"  ✅ Created session {i+1}/{self.min_size}")
    
    async def _create_session(self) -> Optional[any]:
        """Create a new session."""
        try:
            params = CreateSessionParams(image_id=self.image_id)
            result = await self.agent_bay.create(params)
            
            if result.success and result.session:
                pooled_session = PooledSession(
                    session=result.session,
                    created_at=datetime.now(),
                    last_used=datetime.now(),
                    in_use=False
                )
                self.pool.append(pooled_session)
                return result.session
        except Exception as e:
            print(f"  ❌ Failed to create session: {e}")
        
        return None
    
    async def acquire(self) -> Optional[any]:
        """Acquire a session from the pool."""
        async with self.lock:
            # Find available session
            for pooled_session in self.pool:
                if not pooled_session.in_use:
                    pooled_session.in_use = True
                    pooled_session.last_used = datetime.now()
                    print(f"  ✅ Acquired session from pool: {pooled_session.session.session_id}")
                    return pooled_session.session
            
            # No available session, create new one if under max_size
            if len(self.pool) < self.max_size:
                print(f"  📈 Pool at capacity, creating new session...")
                session = await self._create_session()
                if session:
                    # Mark as in use
                    for pooled_session in self.pool:
                        if pooled_session.session == session:
                            pooled_session.in_use = True
                            return session
            
            print(f"  ⚠️  Pool exhausted, waiting for available session...")
            return None
    
    async def release(self, session: any):
        """Release a session back to the pool."""
        async with self.lock:
            for pooled_session in self.pool:
                if pooled_session.session == session:
                    pooled_session.in_use = False
                    print(f"  ✅ Released session back to pool: {session.session_id}")
                    return
    
    async def cleanup(self):
        """Clean up all sessions in the pool."""
        print(f"\n🧹 Cleaning up session pool ({len(self.pool)} sessions)...")
        
        for pooled_session in self.pool:
            try:
                result = await self.agent_bay.delete(pooled_session.session)
                if result.success:
                    print(f"  ✅ Deleted session: {pooled_session.session.session_id}")
            except Exception as e:
                print(f"  ❌ Failed to delete session: {e}")
        
        self.pool.clear()
    
    def get_stats(self) -> dict:
        """Get pool statistics."""
        total = len(self.pool)
        in_use = sum(1 for ps in self.pool if ps.in_use)
        available = total - in_use
        
        return {
            "total_sessions": total,
            "in_use": in_use,
            "available": available,
            "utilization": (in_use / total * 100) if total > 0 else 0
        }
    
    def print_stats(self):
        """Print pool statistics."""
        stats = self.get_stats()
        print(f"\n📊 Pool Statistics:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   In Use: {stats['in_use']}")
        print(f"   Available: {stats['available']}")
        print(f"   Utilization: {stats['utilization']:.1f}%")


async def worker_task(pool: SessionPool, task_id: int, num_operations: int):
    """Worker task that uses sessions from the pool."""
    print(f"\n🔧 Worker {task_id} starting ({num_operations} operations)...")
    
    for i in range(num_operations):
        session = await pool.acquire()
        
        if session:
            try:
                # Perform some work with the session
                command = f"echo 'Worker {task_id}, Operation {i+1}'"
                result = await session.command.execute_command(command)
                
                if result.success:
                    print(f"  ✅ Worker {task_id}, Op {i+1}: {result.output.strip()}")
                
                # Simulate some work
                await asyncio.sleep(0.5)
                
            finally:
                await pool.release(session)
        else:
            print(f"  ⚠️  Worker {task_id}, Op {i+1}: No session available")
            await asyncio.sleep(1)
    
    print(f"  ✅ Worker {task_id} completed")


async def main():
    """Main function demonstrating session pooling."""
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Error: AGENTBAY_API_KEY environment variable not set")
        return
    
    agent_bay = AsyncAgentBay(api_key=api_key)
    pool = None
    
    try:
        print("=" * 60)
        print("Session Pooling Example")
        print("=" * 60)
        
        # Create and initialize pool
        pool = SessionPool(
            agent_bay=agent_bay,
            min_size=2,
            max_size=4,
            image_id="linux_latest"
        )
        
        await pool.initialize()
        pool.print_stats()
        
        # Example 1: Sequential session usage
        print("\n" + "=" * 60)
        print("Example 1: Sequential Session Usage")
        print("=" * 60)
        
        for i in range(3):
            session = await pool.acquire()
            if session:
                result = await session.command.execute_command(f"echo 'Sequential operation {i+1}'")
                if result.success:
                    print(f"✅ Operation {i+1}: {result.output.strip()}")
                await pool.release(session)
        
        pool.print_stats()
        
        # Example 2: Concurrent workers using the pool
        print("\n" + "=" * 60)
        print("Example 2: Concurrent Workers")
        print("=" * 60)
        
        workers = [
            worker_task(pool, 1, 3),
            worker_task(pool, 2, 3),
            worker_task(pool, 3, 3),
        ]
        
        await asyncio.gather(*workers)
        
        pool.print_stats()
        
        print("\n✅ Session pooling examples completed")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
    finally:
        if pool:
            await pool.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

