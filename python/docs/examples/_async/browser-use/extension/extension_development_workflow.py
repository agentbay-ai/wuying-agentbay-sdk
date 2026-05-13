"""
ci-stable
Extension Development Workflow Example

This example demonstrates a complete development workflow for browser extensions,
including uploading, testing, updating, and iterative development.
"""

import os
import time
from typing import Optional
from agentbay import AsyncAgentBay, AsyncExtensionsService, CreateSessionParams
from agentbay import BrowserContext


class ExtensionDevelopmentWorkflow:
    """
    A helper class for extension development and testing workflow.
    
    This class provides methods to:
    - Upload extensions for development
    - Create test sessions with extensions
    - Update extensions during development
    - Manage development lifecycle
    """
    
    def __init__(self, api_key: str, project_name: str = "dev_extensions"):
        """Initialize the development workflow."""
        self.agent_bay = AsyncAgentBay(api_key=api_key)
        self.extensions_service = AsyncExtensionsService(self.agent_bay, project_name)
        self.extension_id: Optional[str] = None
        self.project_name = project_name
        
        print(f"🛠️  Extension Development Workflow initialized")
        print(f"   - Project: {project_name}")
    
    async def upload_extension(self, extension_path: str) -> str:
        """
        Upload an extension for development testing.
        
        Args:
            extension_path: Path to the extension ZIP file
            
        Returns:
            Extension ID
        """
        try:
            print(f"📦 Uploading extension: {os.path.basename(extension_path)}")
            
            if not os.path.exists(extension_path):
                raise FileNotFoundError(f"Extension file not found: {extension_path}")
            
            # Upload extension
            extension = await self.extensions_service.create(extension_path)
            self.extension_id = extension.id
            
            print(f"✅ Extension uploaded successfully!")
            print(f"   - Name: {extension.name}")
            print(f"   - ID: {extension.id}")
            
            return extension.id
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            raise
    
    async def update_extension(self, new_extension_path: str) -> str:
        """
        Update existing extension during development.
        
        Args:
            new_extension_path: Path to the updated extension ZIP file
            
        Returns:
            Extension ID
        """
        if not self.extension_id:
            raise ValueError("No extension uploaded yet. Call upload_extension() first.")
        
        try:
            print(f"🔄 Updating extension: {os.path.basename(new_extension_path)}")
            
            # Update extension with new file
            updated_ext = await self.extensions_service.update(self.extension_id, new_extension_path)
            
            print(f"✅ Extension updated successfully!")
            print(f"   - Name: {updated_ext.name}")
            print(f"   - ID: {self.extension_id}")
            
            return self.extension_id
            
        except Exception as e:
            print(f"❌ Update failed: {e}")
            raise
    
    async def create_test_session(self, session_name: Optional[str] = None) -> 'Session':
        """
        Create a browser session with the current extension for testing.
        
        Args:
            session_name: Optional name for the test session
            
        Returns:
            Session object
        """
        if not self.extension_id:
            raise ValueError("No extension available. Upload an extension first.")
        
        try:
            # Generate session name if not provided
            if not session_name:
                timestamp = int(time.time())
                session_name = f"dev_session_{timestamp}"
            
            print(f"🌐 Creating test session: {session_name}")
            
            # Create extension option
            ext_option = await self.extensions_service.create_extension_option([self.extension_id])
            
            # Create session parameters
            session_params = CreateSessionParams(
                labels={
                    "purpose": "extension_development",
                    "project": self.project_name,
                    "extension_id": self.extension_id
                },
                browser_context=BrowserContext(
                    context_id=session_name,
                    auto_upload=True,
                    extension_option=ext_option
                )
            )
            
            # Create session
            session_result = await self.agent_bay.create(session_params)
            if not session_result.success:
                raise Exception(f"Session creation failed: {session_result.error_message}")
            
            session = session_result.session
            
            print(f"✅ Test session created successfully!")
            print(f"   - Session ID: {session.session_id}")
            print(f"   - Extension available at: /tmp/extensions/{self.extension_id}/")
            
            return session
            
        except Exception as e:
            print(f"❌ Session creation failed: {e}")
            raise
    
    async def run_development_cycle(self, initial_extension_path: str, updated_extension_path: str):
        """
        Run a complete development cycle: upload -> test -> update -> test.
        
        Args:
            initial_extension_path: Path to initial extension version
            updated_extension_path: Path to updated extension version
        """
        try:
            print("🚀 Starting development cycle...")
            print("=" * 50)
            
            # Step 1: Upload initial version
            print("\n📋 Step 1: Upload initial extension")
            await self.upload_extension(initial_extension_path)
            
            # Step 2: Create test session for v1
            print("\n📋 Step 2: Create test session for initial version")
            session1 = await self.create_test_session("initial_version_test")
            
            print("💡 You can now test the initial version of your extension")
            print("   Extension files are available in the session at /tmp/extensions/")
            
            # Step 3: Update extension
            print("\n📋 Step 3: Update extension to new version")
            await self.update_extension(updated_extension_path)
            
            # Step 4: Create test session for v2
            print("\n📋 Step 4: Create test session for updated version")
            session2 = await self.create_test_session("updated_version_test")
            
            print("💡 You can now test the updated version of your extension")
            print("   Both sessions are available for comparison testing")
            
            print("\n🎉 Development cycle completed successfully!")
            
            return session1, session2
            
        except Exception as e:
            print(f"❌ Development cycle failed: {e}")
            raise
    
    async def list_extensions(self):
        """List all extensions in the development context."""
        try:
            extensions = await self.extensions_service.list()
            
            print(f"📋 Extensions in '{self.project_name}' context:")
            if not extensions:
                print("   (No extensions found)")
            else:
                for ext in extensions:
                    status = "🟢 Current" if ext.id == self.extension_id else "⚪ Available"
                    print(f"   {status} {ext.name} (ID: {ext.id})")
            
            return extensions
            
        except Exception as e:
            print(f"❌ Failed to list extensions: {e}")
            return []
    
    async def cleanup(self):
        """Clean up development resources."""
        try:
            print("🧹 Cleaning up development resources...")
            
            # Delete current extension if exists
            if self.extension_id:
                deleted = await self.extensions_service.delete(self.extension_id)
                if deleted:
                    print(f"   ✅ Deleted extension: {self.extension_id}")
                else:
                    print(f"   ⚠️  Failed to delete extension: {self.extension_id}")
            
            # Cleanup context
            await self.extensions_service.cleanup()
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")


async def development_workflow_example():
    """Example of using the development workflow."""
    
    # Check API key
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Please set AGENTBAY_API_KEY environment variable")
        return False
    
    # Initialize workflow
    workflow = ExtensionDevelopmentWorkflow(api_key, "my_extension_project")
    
    try:
        # Example extension paths (using test files)
        initial_extension = "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip"
        updated_extension = "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension-v2.zip"
        
        import zipfile
        ext_dir = os.path.dirname(__file__)
        created_paths = []

        # Create initial extension ZIP if not found
        if not os.path.exists(initial_extension):
            print(f"⚠️ Initial extension not found: {initial_extension}")
            print("📦 Creating a test extension ZIP in the current directory...")
            initial_extension = os.path.join(ext_dir, "test-extension.zip")
            with zipfile.ZipFile(initial_extension, "w") as zf:
                zf.writestr("manifest.json", '{"manifest_version": 2, "name": "test-extension", "version": "1.0"}')
            created_paths.append(initial_extension)
            print(f"✅ Created test extension: {initial_extension}")
        
        # Create updated extension ZIP if not found
        if not os.path.exists(updated_extension):
            print(f"⚠️ Updated extension not found: {updated_extension}")
            print("📦 Creating a test extension ZIP in the current directory...")
            updated_extension = os.path.join(ext_dir, "test-extension-v2.zip")
            with zipfile.ZipFile(updated_extension, "w") as zf:
                zf.writestr("manifest.json", '{"manifest_version": 2, "name": "test-extension-v2", "version": "2.0"}')
            created_paths.append(updated_extension)
            print(f"✅ Created test extension: {updated_extension}")

        # Full development cycle
        session1, session2 = await workflow.run_development_cycle(
            initial_extension, 
            updated_extension
        )
        
        print("\n🎯 Full development cycle completed!")
        print(f"   - Initial version session: {session1.session_id}")
        print(f"   - Updated version session: {session2.session_id}")
        
        # List all extensions
        print("\n📋 Current extensions:")
        await workflow.list_extensions()
        
        return True
        
    except Exception as e:
        print(f"❌ Development workflow failed: {e}")
        return False
    finally:
        # Always cleanup
        await workflow.cleanup()
        # 清理本地创建的测试 ZIP 文件
        for path in created_paths:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Extension Development Workflow Example")
        print("=" * 60)
        
        print("\n1. Full Development Cycle Example")
        print("-" * 40)
        await development_workflow_example()
        
        print("\n🎯 Development workflow example completed!")
        print("\n💡 Tips for extension development:")
        print("   - Use descriptive project names for different extensions")
        print("   - Test each version thoroughly before updating")
        print("   - Keep backup copies of working extension versions")
        print("   - Use the cleanup() method to manage resources properly")
    
    asyncio.run(main())