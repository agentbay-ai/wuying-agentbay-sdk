"""
ci-stable
Database Operations Example

This example demonstrates:
1. Setting up SQLite database
2. Creating tables
3. Inserting and querying data
4. Database transactions
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate database operations."""
    print("=== Database Operations Example ===\n")

    # Initialize AgentBay client
    client = AsyncAgentBay()
    session = None

    try:
        # Create a session
        print("Creating session...")
        session_result = await client.create(
            CreateSessionParams(
                image_id="linux_latest"
            )
        )
        session = session_result.session
        print(f"Session created: {session.session_id}")

        # Check SQLite version using Python
        print("\n1. Checking SQLite version...")
        version_script = """import sqlite3; print(f"SQLite version: {sqlite3.sqlite_version}")"""
        result = await session.command.execute_command(f"python3 -c '{version_script}'")
        print(result.output)

        # Create a Python script for database operations
        print("\n2. Creating database operations script...")
        db_script = """#!/usr/bin/env python3
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('/tmp/mydb.sqlite')
cursor = conn.cursor()

# Create table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        age INTEGER
    )
''')

# Insert sample data
users = [
    ('Alice', 'alice@example.com', 30),
    ('Bob', 'bob@example.com', 25),
    ('Charlie', 'charlie@example.com', 35)
]

cursor.executemany('INSERT OR IGNORE INTO users (name, email, age) VALUES (?, ?, ?)', users)
conn.commit()

# Query data
cursor.execute('SELECT * FROM users')
rows = cursor.fetchall()

print("Users in database:")
for row in rows:
    print(f"  ID: {row[0]}, Name: {row[1]}, Email: {row[2]}, Age: {row[3]}")

# Query with condition
cursor.execute('SELECT * FROM users WHERE age >= 30')
rows = cursor.fetchall()

print("\\nUsers aged 30 or older:")
for row in rows:
    print(f"  {row[1]} ({row[3]} years old)")

# Count users
cursor.execute('SELECT COUNT(*) FROM users')
count = cursor.fetchone()[0]
print(f"\\nTotal users: {count}")

# Close connection
conn.close()
print("\\nDatabase operations completed successfully")
"""
        await session.file_system.write_file("/tmp/db_operations.py", db_script)
        print("Database script created: /tmp/db_operations.py")

        # Run the database script
        print("\n3. Running database operations...")
        result = await session.command.execute_command("python3 /tmp/db_operations.py")
        print(f"Script output:\n{result.output}")

        # Verify database file exists
        print("\n4. Verifying database file...")
        result = await session.command.execute_command("ls -lh /tmp/mydb.sqlite")
        print(f"Database file:\n{result.output}")

        # Query database with Python script
        print("\n5. Querying database with Python...")
        query_script = """#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/tmp/mydb.sqlite')
cursor = conn.cursor()
cursor.execute('SELECT name, age FROM users ORDER BY age DESC')
for row in cursor.fetchall():
    print(f"{row[0]}|{row[1]}")
conn.close()"""
        await session.file_system.write_file("/tmp/query_db.py", query_script)
        result = await session.command.execute_command("python3 /tmp/query_db.py")
        print(f"Query result:\n{result.output}")

        # Get table schema with Python
        print("\n6. Getting table schema...")
        schema_script = """#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/tmp/mydb.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='users'")
schema = cursor.fetchone()[0]
print(schema)
conn.close()"""
        await session.file_system.write_file("/tmp/schema_db.py", schema_script)
        result = await session.command.execute_command("python3 /tmp/schema_db.py")
        print(f"Table schema:\n{result.output}")

        # Create an update script
        print("\n7. Creating update script...")
        update_script = """#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('/tmp/mydb.sqlite')
cursor = conn.cursor()

# Update a user
cursor.execute("UPDATE users SET age = ? WHERE name = ?", (31, 'Alice'))
conn.commit()

# Verify update
cursor.execute("SELECT name, age FROM users WHERE name = 'Alice'")
row = cursor.fetchone()
print(f"Updated user: {row[0]}, Age: {row[1]}")

conn.close()
"""
        await session.file_system.write_file("/tmp/update_db.py", update_script)
        print("Update script created")

        # Run the update script
        print("\n8. Running update script...")
        result = await session.command.execute_command("python3 /tmp/update_db.py")
        print(f"Update output:\n{result.output}")

        # Verify the update with Python
        print("\n9. Verifying update...")
        verify_script = """#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/tmp/mydb.sqlite')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE name = 'Alice'")
row = cursor.fetchone()
print(f"{row[0]}|{row[1]}|{row[2]}|{row[3]}")
conn.close()"""
        await session.file_system.write_file("/tmp/verify_db.py", verify_script)
        result = await session.command.execute_command("python3 /tmp/verify_db.py")
        print(f"Updated record:\n{result.output}")

        # Export database to SQL
        print("\n10. Exporting database to SQL...")
        export_script = """#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect('/tmp/mydb.sqlite')
with open('/tmp/mydb_backup.sql', 'w') as f:
    for line in conn.iterdump():
        f.write(f"{line}\\n")
conn.close()
print("Database exported successfully")"""
        await session.file_system.write_file("/tmp/export_db.py", export_script)
        result = await session.command.execute_command("python3 /tmp/export_db.py")
        print(f"Export result:\n{result.output}")

        # Verify export
        result = await session.command.execute_command("wc -l /tmp/mydb_backup.sql")
        print(f"Export file size: {result.output}")

        print("\n=== Example completed successfully ===")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        raise

    finally:
        # Clean up
        if session:
            print("\nCleaning up session...")
            await client.delete(session)
            print("Session closed")


if __name__ == "__main__":
    asyncio.run(main())

