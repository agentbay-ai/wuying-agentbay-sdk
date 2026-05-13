"""
Browser Authentication Flow Example

This example demonstrates:
1. Handling login forms
2. Managing authentication state
3. Working with authenticated sessions
4. Handling logout
ci-skip
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from agentbay import AsyncAgentBay, CreateSessionParams
from agentbay import BrowserOption
from agentbay import ActOptions, ExtractOptions
from pydantic import BaseModel, Field


class TextContent(BaseModel):
    """Simple model to extract text content."""
    content: str = Field(description="The extracted text content")


async def main():
    """Demonstrate browser authentication flow."""
    print("=== Browser Authentication Flow Example ===\n")

    # Initialize AgentBay client
    client = AsyncAgentBay()
    session = None

    try:
        # Create a session with browser enabled
        print("Creating session with browser...")
        session_result = await client.create(
            CreateSessionParams(image_id="browser_latest")
        )
        if not session_result.success or not session_result.session:
            raise Exception(f"Failed to create session: {session_result.error_message}")
        session = session_result.session
        print(f"Session created: {session.session_id}")

        # Initialize browser
        print("Initializing browser...")
        if not await session.browser.initialize(BrowserOption()):
            raise Exception("Failed to initialize browser")
        print("Browser initialized")

        # Navigate to a test login page (using httpbin for demonstration)
        print("\n1. Navigating to login form...")
        await session.browser.operator.navigate("https://httpbin.org/forms/post")

        # Fill in login credentials (demonstration only)
        print("\n2. Filling in authentication form...")
        await session.browser.operator.act(ActOptions(action="Fill in the customer name field with 'testuser'"))
        await session.browser.operator.act(ActOptions(action="Fill in the email field with 'test@example.com'"))
        print("Form filled with test credentials")

        # Take screenshot of filled form
        print("\n3. Taking screenshot of filled form...")
        screenshot_path = await session.browser.operator.screenshot()
        print(f"Screenshot saved: {screenshot_path}")

        # Verify form state
        print("\n4. Verifying form state...")
        success, form_result = await session.browser.operator.extract(
            ExtractOptions(
                instruction="What values are filled in the form fields?",
                schema=TextContent
            )
        )
        if success:
            print(f"Form state:\n{form_result.content}")
        else:
            print("Failed to extract form state")

        # Simulate checking authentication state
        print("\n5. Checking authentication state...")
        success, auth_result = await session.browser.operator.extract(
            ExtractOptions(
                instruction="Is there a submit button on this form?",
                schema=TextContent
            )
        )
        if success:
            print(f"Authentication form status: {auth_result.content}")
        else:
            print("Failed to check authentication state")

        # Navigate to a page that might require authentication
        print("\n6. Testing authenticated navigation...")
        await session.browser.operator.navigate("https://httpbin.org/basic-auth/user/passwd")
        
        # Check if authentication is required
        success, auth_check = await session.browser.operator.extract(
            ExtractOptions(
                instruction="Does this page require authentication? What is displayed?",
                schema=TextContent
            )
        )
        if success:
            print(f"Authentication check: {auth_check.content}")
        else:
            print("Failed to check authentication requirement")

        # Demonstrate cookie-based authentication
        print("\n7. Setting authentication cookie...")
        await session.browser.operator.act(ActOptions(
            action="Execute JavaScript to set a cookie: "
            "document.cookie = 'auth_token=demo_token_12345; path=/'"
        ))
        print("Authentication cookie set")

        # Verify cookie was set
        print("\n8. Verifying cookie...")
        success, cookie_result = await session.browser.operator.extract(
            ExtractOptions(
                instruction="What cookies are set for this page?",
                schema=TextContent
            )
        )
        if success:
            print(f"Cookies: {cookie_result.content}")
        else:
            print("Failed to verify cookies")

        # Navigate back to main page
        print("\n9. Navigating to main page...")
        await session.browser.operator.navigate("https://httpbin.org")

        # Verify authentication persists
        print("\n10. Verifying authentication persistence...")
        success, persist_result = await session.browser.operator.extract(
            ExtractOptions(
                instruction="Are there any cookies set for this domain?",
                schema=TextContent
            )
        )
        if success:
            print(f"Persistent authentication: {persist_result.content}")
        else:
            print("Failed to verify authentication persistence")

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

