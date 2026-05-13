"""
ci-stable
Web Server Setup Example

This example demonstrates:
1. Setting up a simple HTTP server
2. Creating web content
3. Testing server endpoints
4. Managing server processes
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from agentbay import AsyncAgentBay
from agentbay import CreateSessionParams


async def main():
    """Demonstrate web server setup."""
    print("=== Web Server Setup Example ===\n")

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

        # Create web content directory
        print("\n1. Creating web content directory...")
        await session.command.execute_command("mkdir -p /tmp/www")
        print("Web directory created: /tmp/www")

        # Create HTML index page
        print("\n2. Creating index.html...")
        html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AgentBay Web Server</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f0f0f0;
        }
        h1 {
            color: #333;
        }
        .info {
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>Welcome to AgentBay Web Server</h1>
    <div class="info">
        <h2>Server Information</h2>
        <p>This is a simple web server running in an AgentBay session.</p>
        <p>Server Status: <strong>Running</strong></p>
        <p><a href="/about.html">About</a> | <a href="/api/status">API Status</a></p>
    </div>
</body>
</html>
"""
        await session.file_system.write_file("/tmp/www/index.html", html_content)
        print("index.html created")

        # Create about page
        print("\n3. Creating about.html...")
        about_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>About - AgentBay Web Server</title>
</head>
<body>
    <h1>About This Server</h1>
    <p>This web server is running in an AgentBay codespace session.</p>
    <p><a href="/">Back to Home</a></p>
</body>
</html>
"""
        await session.file_system.write_file("/tmp/www/about.html", about_content)
        print("about.html created")

        # Create a Python web server script
        print("\n4. Creating Python web server script...")
        server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import json
from urllib.parse import urlparse, parse_qs

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)

        if parsed_path.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                'status': 'running',
                'port': PORT,
                'message': 'Server is healthy'
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            super().do_GET()

    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\\nServer stopped")
"""
        await session.file_system.write_file("/tmp/server.py", server_script)
        print("Server script created: /tmp/server.py")

        # Make server script executable
        await session.command.execute_command("chmod +x /tmp/server.py")

        # List web content
        print("\n5. Listing web content...")
        result = await session.command.execute_command("ls -lh /tmp/www/")
        print(f"Web content:\n{result.output}")

        # Test with Python's built-in HTTP server (start in background)
        print("\n6. Starting Python HTTP server in background...")
        # Note: In a real scenario, you would start this in background and test it
        # For this example, we'll just show the command
        print("Command to start server: cd /tmp/www && python3 -m http.server 8000")

        # Create a test script to check if server would work
        print("\n7. Creating server test script...")
        test_script = """#!/bin/bash

echo "Testing web server setup..."

# Check if port 8000 is available
if netstat -tuln 2>/dev/null | grep -q ':8000 '; then
    echo "Port 8000 is already in use"
else
    echo "Port 8000 is available"
fi

# Check if web content exists
if [ -f /tmp/www/index.html ]; then
    echo "index.html exists"
    echo "File size: $(wc -c < /tmp/www/index.html) bytes"
else
    echo "index.html not found"
fi

# Check Python availability
if command -v python3 &> /dev/null; then
    echo "Python3 is available: $(python3 --version)"
else
    echo "Python3 is not available"
fi

echo "Server setup verification complete"
"""
        await session.file_system.write_file("/tmp/test_server.sh", test_script)
        await session.command.execute_command("chmod +x /tmp/test_server.sh")
        print("Test script created: /tmp/test_server.sh")

        # Run the test script
        print("\n8. Running server test script...")
        result = await session.command.execute_command("/tmp/test_server.sh")
        print(f"Test results:\n{result.output}")

        # Create a curl test script
        print("\n9. Creating curl test script...")
        curl_test = """#!/bin/bash

# This script would test the server if it were running
echo "Sample curl commands to test the server:"
echo ""
echo "1. Test home page:"
echo "   curl http://localhost:8000/"
echo ""
echo "2. Test about page:"
echo "   curl http://localhost:8000/about.html"
echo ""
echo "3. Test API endpoint:"
echo "   curl http://localhost:8000/api/status"
echo ""
echo "4. Test with headers:"
echo "   curl -I http://localhost:8000/"
"""
        await session.file_system.write_file("/tmp/curl_test.sh", curl_test)
        await session.command.execute_command("chmod +x /tmp/curl_test.sh")
        print("Curl test script created")

        # Run the curl test script
        print("\n10. Running curl test script...")
        result = await session.command.execute_command("/tmp/curl_test.sh")
        print(f"Curl test commands:\n{result.output}")

        # Create a systemd-style service file (for reference)
        print("\n11. Creating service file template...")
        service_template = """[Unit]
Description=AgentBay Web Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/tmp/www
ExecStart=/usr/bin/python3 -m http.server 8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
"""
        await session.file_system.write_file("/tmp/webserver.service", service_template)
        print("Service file template created: /tmp/webserver.service")

        # Show server setup summary
        print("\n12. Server setup summary...")
        result = await session.command.execute_command(
            "echo 'Web Root: /tmp/www' && echo 'Server Script: /tmp/server.py' && echo 'Port: 8000'"
        )
        print(f"Setup summary:\n{result.output}")

        print("\n=== Example completed successfully ===")
        print("\nNote: To actually run the server, execute:")
        print("  cd /tmp/www && python3 -m http.server 8000")

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

