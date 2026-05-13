"""
ci-stable
Basic Extension Management Example

This example demonstrates the fundamental usage of browser extensions with AgentBay SDK.
"""

import os
from agentbay import AsyncAgentBay, AsyncExtensionsService, CreateSessionParams
from agentbay import BrowserContext


async def basic_extension_example():
    """Basic extension upload and browser session creation."""

    # Initialize AgentBay client
    agent_bay = AsyncAgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

    # Initialize extensions service (auto-creates context)
    extensions_service = AsyncExtensionsService(agent_bay)

    try:
        print("🚀 Starting basic extension example...")

        # Upload extension (using test extension)
        extension_path = "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip"  # Test extension path

        if not os.path.exists(extension_path):
            print(f"⚠️ Extension file not found: {extension_path}")
            print("📦 Creating a minimal test extension ZIP in the current directory...")
            import zipfile
            extension_path = os.path.join(os.path.dirname(__file__), "test-extension.zip")
            with zipfile.ZipFile(extension_path, "w") as zf:
                zf.writestr("manifest.json", '{"manifest_version": 2, "name": "test-extension", "version": "1.0"}')
            print(f"✅ Created test extension: {extension_path}")

        # Upload extension to cloud
        print(f"📦 Uploading extension: {extension_path}")
        extension = await extensions_service.create(extension_path)
        print(f"✅ Extension uploaded successfully!")
        print(f"   - Name: {extension.name}")
        print(f"   - ID: {extension.id}")

        # Create extension option for browser session
        print("🔧 Creating extension configuration...")
        ext_option = await extensions_service.create_extension_option([extension.id])
        print(f"✅ Extension option created: {ext_option}")

        # Create browser session with extension
        print("🌐 Creating browser session with extension...")
        context_result = await agent_bay.context.get("cookie-demo-context", create=True)
        if not context_result.success or not context_result.context:
            print(f"❌ Failed to create context: {getattr(context_result, 'error_message', 'unknown')}")
            return False
        context = context_result.context
        browser_context = BrowserContext(
            context_id=context.id,
            auto_upload=True,
            extension_option=ext_option
        )
        params = CreateSessionParams(
            image_id="browser_latest",
            labels={"purpose": "basic_extension_example", "type": "demo"},
            browser_context=browser_context
        )

        session_result = await agent_bay.create(params)
        if not session_result.success:
            print(f"❌ Failed to create session: {session_result.error_message}")
            return False

        session = session_result.session
        print(f"✅ Browser session created successfully!")
        print(f"   - Session ID: {session.session_id}")
        print(f"   - Extensions synchronized to: /tmp/extensions/")

        # List available extensions in context
        print("\n📋 Listing available extensions:")
        extensions = await extensions_service.list()
        for ext in extensions:
            print(f"   - {ext.name} (ID: {ext.id})")

        print("\n🎉 Extension example completed successfully!")
        print("💡 The extension is now available in the browser session at /tmp/extensions/")

        return True

    except Exception as e:
        print(f"❌ Error during extension example: {e}")
        return False
    finally:
        # Clean up resources
        print("\n🧹 Cleaning up resources...")
        await extensions_service.cleanup()
        print("✅ Cleanup completed")
        if os.path.exists(extension_path):
            os.remove(extension_path)


async def multiple_extensions_example():
    """Example with multiple extensions."""

    agent_bay = AsyncAgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))
    extensions_service = AsyncExtensionsService(agent_bay, "multi_ext_demo")

    try:
        print("🚀 Starting multiple extensions example...")

        # List of extension paths (using test extensions)
        extension_paths = [
            "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip",
            "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension-v2.zip"
        ]

        # Filter existing files
        existing_paths = [path for path in extension_paths if os.path.exists(path)]
        created_paths = []
        if not existing_paths:
            print("⚠️ No extension files found. Creating test extension ZIPs in the current directory...")
            import zipfile
            ext_dir = os.path.dirname(__file__)
            for i, path in enumerate(extension_paths):
                name = f"test-extension-v{i+1}.zip"
                local_path = os.path.join(ext_dir, name)
                with zipfile.ZipFile(local_path, "w") as zf:
                    zf.writestr("manifest.json", f'{{"manifest_version": 2, "name": "test-extension-v{i+1}", "version": "1.0"}}')
                existing_paths.append(local_path)
                created_paths.append(local_path)
                print(f"✅ Created test extension: {local_path}")

        print(f"📦 Uploading {len(existing_paths)} extensions...")

        # Upload all extensions
        extension_ids = []
        for path in existing_paths:
            ext = await extensions_service.create(path)
            extension_ids.append(ext.id)
            print(f"   ✅ {ext.name} uploaded (ID: {ext.id})")

        # Create session with all extensions
        print("🔧 Creating configuration for all extensions...")
        ext_option = await extensions_service.create_extension_option(extension_ids)

        context_result = await agent_bay.context.get("cookie-demo-context", create=True)
        if not context_result.success or not context_result.context:
            print(f"❌ Failed to create context: {getattr(context_result, 'error_message', 'unknown')}")
            return False
        context = context_result.context
        browser_context = BrowserContext(
            context_id=context.id,
            auto_upload=True,
            extension_option=ext_option
        )
        params = CreateSessionParams(
            image_id="browser_latest",
            labels={"purpose": "multiple_extensions", "count": str(len(extension_ids))},
            browser_context=browser_context
        )

        print("🌐 Creating browser session...")
        session_result = await agent_bay.create(params)
        session = session_result.session

        print(f"✅ Session created with {len(extension_ids)} extensions!")
        print(f"   - Session ID: {session.session_id}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await extensions_service.cleanup()
        # 清理本地创建的测试 ZIP 文件
        for path in created_paths:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    import asyncio

    async def main():
        print("AgentBay Extension Examples")
        print("=" * 50)

        # Check API key
        if not os.getenv("AGENTBAY_API_KEY"):
            print("❌ Please set AGENTBAY_API_KEY environment variable")
            exit(1)

        print("\n1. Basic Extension Example")
        print("-" * 30)
        await basic_extension_example()

        print("\n2. Multiple Extensions Example")
        print("-" * 30)
        await multiple_extensions_example()

        print("\n🎯 Examples completed!")
        print("\n💡 Next steps:")
        print("   - Update extension paths with your actual ZIP files")
        print("   - Check extension_development_workflow.py for advanced usage")
        print("   - See browser automation examples for integration patterns")

    asyncio.run(main())