"""
ci-stable
Text Processing Example

This example demonstrates:
1. Text file manipulation
2. Using grep, sed, awk
3. Text analysis and transformation
4. Working with large text files
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate text processing operations."""
    print("=== Text Processing Example ===\n")

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

        # Create a sample text file
        print("\n1. Creating sample text file...")
        sample_text = """Apple,Red,100
Banana,Yellow,150
Cherry,Red,80
Date,Brown,200
Elderberry,Purple,120
Fig,Purple,90
Grape,Green,180
"""
        await session.file_system.write_file("/tmp/fruits.csv", sample_text)
        print("Sample file created: /tmp/fruits.csv")

        # Use grep to search
        print("\n2. Using grep to search for 'Red' fruits...")
        result = await session.command.execute_command("grep 'Red' /tmp/fruits.csv")
        print(f"Grep result:\n{result.output}")

        # Use grep with case-insensitive search
        print("\n3. Case-insensitive search for 'purple'...")
        result = await session.command.execute_command("grep -i 'purple' /tmp/fruits.csv")
        print(f"Grep result:\n{result.output}")

        # Use awk to process columns
        print("\n4. Using awk to extract fruit names and quantities...")
        result = await session.command.execute_command("awk -F',' '{print $1, $3}' /tmp/fruits.csv")
        print(f"Awk result:\n{result.output}")

        # Use awk to calculate sum
        print("\n5. Using awk to calculate total quantity...")
        result = await session.command.execute_command("awk -F',' '{sum += $3} END {print \"Total:\", sum}' /tmp/fruits.csv")
        print(f"Total quantity: {result.output}")

        # Use sed to replace text
        print("\n6. Using sed to replace 'Red' with 'Crimson'...")
        result = await session.command.execute_command("sed 's/Red/Crimson/g' /tmp/fruits.csv")
        print(f"Sed result:\n{result.output}")

        # Sort the file
        print("\n7. Sorting fruits by name...")
        result = await session.command.execute_command("sort /tmp/fruits.csv")
        print(f"Sorted result:\n{result.output}")

        # Sort by quantity (third column)
        print("\n8. Sorting fruits by quantity...")
        result = await session.command.execute_command("sort -t',' -k3 -n /tmp/fruits.csv")
        print(f"Sorted by quantity:\n{result.output}")

        # Count lines, words, characters
        print("\n9. Counting lines, words, and characters...")
        result = await session.command.execute_command("wc /tmp/fruits.csv")
        print(f"Word count: {result.output}")

        # Create a log file for processing
        print("\n10. Creating a log file...")
        log_content = """2024-01-15 10:00:00 INFO Application started
2024-01-15 10:01:00 DEBUG Processing request
2024-01-15 10:02:00 ERROR Failed to connect to database
2024-01-15 10:03:00 INFO Retrying connection
2024-01-15 10:04:00 INFO Connection successful
2024-01-15 10:05:00 WARN High memory usage detected
2024-01-15 10:06:00 ERROR Timeout occurred
2024-01-15 10:07:00 INFO Request completed
"""
        await session.file_system.write_file("/tmp/app.log", log_content)
        print("Log file created: /tmp/app.log")

        # Extract ERROR lines
        print("\n11. Extracting ERROR lines from log...")
        result = await session.command.execute_command("grep 'ERROR' /tmp/app.log")
        print(f"Error lines:\n{result.output}")

        # Count occurrences of each log level
        print("\n12. Counting log levels...")
        result = await session.command.execute_command(
            "awk '{print $3}' /tmp/app.log | sort | uniq -c"
        )
        print(f"Log level counts:\n{result.output}")

        # Extract timestamps of errors
        print("\n13. Extracting error timestamps...")
        result = await session.command.execute_command(
            "grep 'ERROR' /tmp/app.log | awk '{print $1, $2}'"
        )
        print(f"Error timestamps:\n{result.output}")

        # Use cut to extract specific fields
        print("\n14. Using cut to extract colors from fruits.csv...")
        result = await session.command.execute_command("cut -d',' -f2 /tmp/fruits.csv | sort | uniq")
        print(f"Unique colors:\n{result.output}")

        # Combine multiple commands
        print("\n15. Finding fruits with quantity > 100...")
        result = await session.command.execute_command(
            "awk -F',' '$3 > 100 {print $1, $3}' /tmp/fruits.csv"
        )
        print(f"Fruits with quantity > 100:\n{result.output}")

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

