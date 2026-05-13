"""
ci-skip
Extension Testing Automation Example

This example demonstrates automated testing workflows for browser extensions,
including test suite execution, multi-extension testing, and CI/CD integration patterns.
"""

import os
import asyncio
import time
from typing import List, Dict, Any
from dataclasses import dataclass
from agentbay import AsyncAgentBay, AsyncExtensionsService, CreateSessionParams
from agentbay import BrowserContext


@dataclass
class TestResult:
    """Test result data structure."""
    extension_name: str
    extension_id: str
    test_name: str
    passed: bool
    duration: float
    error_message: str = ""


@dataclass
class TestSuite:
    """Test suite configuration."""
    name: str
    extension_paths: List[str]
    test_cases: List[str]
    timeout: int = 300


class ExtensionTestRunner:
    """
    Automated test runner for browser extensions.
    
    This class provides methods to:
    - Run automated test suites on extensions
    - Test multiple extensions in parallel
    - Generate test reports
    - Integrate with CI/CD pipelines
    """
    
    def __init__(self, api_key: str, test_project_name: str = "extension_tests"):
        """Initialize the test runner."""
        self.agent_bay = AsyncAgentBay(api_key=api_key)
        self.extensions_service = AsyncExtensionsService(self.agent_bay, test_project_name)
        self.test_results: List[TestResult] = []
        self.project_name = test_project_name
        
        print(f"🧪 Extension Test Runner initialized")
        print(f"   - Project: {test_project_name}")
    
    async def upload_test_extensions(self, extension_paths: List[str]) -> List[str]:
        """
        Upload multiple extensions for testing.
        
        Args:
            extension_paths: List of paths to extension ZIP files
            
        Returns:
            List of extension IDs
        """
        print(f"📦 Uploading {len(extension_paths)} test extensions...")
        
        extension_ids = []
        for path in extension_paths:
            try:
                if not os.path.exists(path):
                    print(f"⚠️  Extension not found: {path}")
                    continue
                
                ext = await self.extensions_service.create(path)
                extension_ids.append(ext.id)
                print(f"   ✅ {ext.name} uploaded (ID: {ext.id})")
                
            except Exception as e:
                print(f"   ❌ Failed to upload {os.path.basename(path)}: {e}")
        
        print(f"✅ Successfully uploaded {len(extension_ids)} extensions")
        return extension_ids
    
    async def create_test_session(self, extension_ids: List[str], session_name: str) -> 'Session':
        """
        Create a test session with specified extensions.
        
        Args:
            extension_ids: List of extension IDs to include
            session_name: Name for the test session
            
        Returns:
            Session object
        """
        try:
            print(f"🌐 Creating test session: {session_name}")
            
            # Create extension option
            ext_option = await self.extensions_service.create_extension_option(extension_ids)
            
            # Create session parameters
            session_params = CreateSessionParams(
                labels={
                    "purpose": "automated_testing",
                    "project": self.project_name,
                    "test_session": session_name,
                    "extension_count": str(len(extension_ids))
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
            print(f"✅ Test session created: {session.session_id}")
            
            return session
            
        except Exception as e:
            print(f"❌ Failed to create test session: {e}")
            raise
    
    async def run_extension_test(self, session: 'Session', extension_id: str, test_case: str) -> TestResult:
        """
        Run a single test case on an extension.
        
        Args:
            session: Browser session with extensions loaded
            extension_id: ID of the extension to test
            test_case: Name of the test case to run
            
        Returns:
            TestResult object
        """
        start_time = time.time()
        
        try:
            print(f"   🧪 Running test: {test_case}")
            
            # Get extension info
            extensions = await self.extensions_service.list()
            extension_name = next((ext.name for ext in extensions if ext.id == extension_id), extension_id)
            
            # Simulate test execution (replace with actual test logic)
            success = await self._execute_test_case(session, extension_id, test_case)
            
            duration = time.time() - start_time
            
            result = TestResult(
                extension_name=extension_name,
                extension_id=extension_id,
                test_name=test_case,
                passed=success,
                duration=duration
            )
            
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status} {test_case} ({duration:.2f}s)")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            result = TestResult(
                extension_name=extension_id,
                extension_id=extension_id,
                test_name=test_case,
                passed=False,
                duration=duration,
                error_message=str(e)
            )
            
            print(f"   ❌ ERROR {test_case}: {e}")
            return result
    
    async def _execute_test_case(self, session: 'Session', extension_id: str, test_case: str) -> bool:
        """
        Execute a specific test case (placeholder implementation).
        
        Replace this method with your actual test logic.
        """
        # Example test cases - replace with real implementation
        if test_case == "extension_loaded":
            # Check if extension files exist in session
            result = session.command.execute(f"ls /tmp/extensions/{extension_id}/")
            return result.success and "manifest.json" in result.output
        
        elif test_case == "manifest_valid":
            # Validate extension manifest
            result = session.command.execute(f"cat /tmp/extensions/{extension_id}/manifest.json")
            return result.success and '"manifest_version"' in result.output
        
        elif test_case == "extension_functional":
            # Simulate functional test
            # In real implementation, you would:
            # - Initialize browser
            # - Navigate to test pages
            # - Interact with extension
            # - Verify expected behavior
            await asyncio.sleep(1)  # Simulate test time
            return True
        
        else:
            print(f"   ⚠️  Unknown test case: {test_case}")
            return False
    
    async def run_test_suite(self, test_suite: TestSuite) -> Dict[str, Any]:
        """
        Run a complete test suite on multiple extensions.
        
        Args:
            test_suite: TestSuite configuration
            
        Returns:
            Dictionary with test results and summary
        """
        print(f"🚀 Running test suite: {test_suite.name}")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Upload test extensions
            extension_ids = await self.upload_test_extensions(test_suite.extension_paths)
            if not extension_ids:
                raise Exception("No extensions uploaded successfully")
            
            # Create test session
            session_name = f"test_{test_suite.name}_{int(time.time())}"
            session = await self.create_test_session(extension_ids, session_name)
            
            # Wait for extension synchronization
            print("⏳ Waiting for extension synchronization...")
            await asyncio.sleep(5)  # Give time for extensions to sync
            
            # Run tests for each extension
            suite_results = []
            for extension_id in extension_ids:
                print(f"\n📋 Testing extension: {extension_id}")
                
                for test_case in test_suite.test_cases:
                    result = await self.run_extension_test(session, extension_id, test_case)
                    suite_results.append(result)
                    self.test_results.append(result)
            
            # Calculate summary
            total_tests = len(suite_results)
            passed_tests = sum(1 for r in suite_results if r.passed)
            failed_tests = total_tests - passed_tests
            success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
            total_duration = time.time() - start_time
            
            summary = {
                "test_suite": test_suite.name,
                "session_id": session.session_id,
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": success_rate,
                "duration": total_duration,
                "results": suite_results
            }
            
            # Print summary
            print(f"\n📊 Test Suite Summary: {test_suite.name}")
            print("-" * 40)
            print(f"   Total Tests: {total_tests}")
            print(f"   Passed: {passed_tests}")
            print(f"   Failed: {failed_tests}")
            print(f"   Success Rate: {success_rate:.1f}%")
            print(f"   Duration: {total_duration:.2f}s")
            
            status = "✅ PASSED" if failed_tests == 0 else "❌ FAILED"
            print(f"   Status: {status}")
            
            return summary
            
        except Exception as e:
            print(f"❌ Test suite failed: {e}")
            return {
                "test_suite": test_suite.name,
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    async def run_multiple_test_suites(self, test_suites: List[TestSuite]) -> Dict[str, Any]:
        """
        Run multiple test suites.
        
        Args:
            test_suites: List of TestSuite configurations
            
        Returns:
            Combined test results and summary
        """
        print(f"🚀 Running {len(test_suites)} test suites")
        print("=" * 70)
        
        start_time = time.time()
        suite_summaries = []
        
        for i, test_suite in enumerate(test_suites, 1):
            print(f"\n📋 Test Suite {i}/{len(test_suites)}: {test_suite.name}")
            print("-" * 50)
            
            summary = await self.run_test_suite(test_suite)
            suite_summaries.append(summary)
            
            # Brief pause between suites
            if i < len(test_suites):
                await asyncio.sleep(2)
        
        # Overall summary
        total_duration = time.time() - start_time
        total_tests = sum(s.get("total_tests", 0) for s in suite_summaries)
        total_passed = sum(s.get("passed", 0) for s in suite_summaries)
        total_failed = sum(s.get("failed", 0) for s in suite_summaries)
        overall_success_rate = (total_passed / total_tests) * 100 if total_tests > 0 else 0
        
        overall_summary = {
            "total_suites": len(test_suites),
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "overall_success_rate": overall_success_rate,
            "total_duration": total_duration,
            "suite_summaries": suite_summaries
        }
        
        print(f"\n🎯 Overall Test Summary")
        print("=" * 30)
        print(f"   Test Suites: {len(test_suites)}")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        print(f"   Total Duration: {total_duration:.2f}s")
        
        overall_status = "✅ ALL PASSED" if total_failed == 0 else "❌ SOME FAILED"
        print(f"   Status: {overall_status}")
        
        return overall_summary
    
    def generate_test_report(self, output_file: str = "extension_test_report.txt"):
        """Generate a detailed test report."""
        try:
            with open(output_file, 'w') as f:
                f.write("Extension Test Report\n")
                f.write("=" * 50 + "\n\n")
                
                for result in self.test_results:
                    status = "PASS" if result.passed else "FAIL"
                    f.write(f"[{status}] {result.extension_name} - {result.test_name}\n")
                    f.write(f"   Duration: {result.duration:.2f}s\n")
                    if result.error_message:
                        f.write(f"   Error: {result.error_message}\n")
                    f.write("\n")
            
            print(f"📄 Test report generated: {output_file}")
            
        except Exception as e:
            print(f"❌ Failed to generate report: {e}")
    
    async def cleanup(self):
        """Clean up test resources."""
        try:
            print("🧹 Cleaning up test resources...")
            await self.extensions_service.cleanup()
            print("✅ Test cleanup completed")
        except Exception as e:
            print(f"❌ Cleanup failed: {e}")


async def basic_test_automation_example():
    """Basic automated testing example."""
    
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Please set AGENTBAY_API_KEY environment variable")
        return False
    
    test_runner = ExtensionTestRunner(api_key, "basic_test_project")
    
    try:
        # Define test suite
        test_suite = TestSuite(
            name="basic_extension_tests",
            extension_paths=[
                "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip",  # Test extension paths
                "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension-v2.zip"
            ],
            test_cases=[
                "extension_loaded",
                "manifest_valid",
                "extension_functional"
            ]
        )
        
        # Create missing extension ZIPs if not found
        import zipfile
        ext_dir = os.path.dirname(__file__)
        created_paths = []
        resolved_paths = []
        for i, path in enumerate(test_suite.extension_paths):
            if os.path.exists(path):
                resolved_paths.append(path)
            else:
                name = f"test-extension-v{i+1}.zip"
                local_path = os.path.join(ext_dir, name)
                print(f"📦 Creating test extension ZIP: {local_path}")
                with zipfile.ZipFile(local_path, "w") as zf:
                    zf.writestr("manifest.json", f'{{"manifest_version": 2, "name": "test-extension-v{i+1}", "version": "1.0"}}')
                resolved_paths.append(local_path)
                created_paths.append(local_path)
        
        # Update test suite with resolved extensions
        test_suite.extension_paths = resolved_paths
        
        # Run test suite
        summary = await test_runner.run_test_suite(test_suite)
        
        # Generate report
        test_runner.generate_test_report("basic_test_report.txt")
        
        return summary.get("failed", 1) == 0
        
    except Exception as e:
        print(f"❌ Test automation failed: {e}")
        return False
    finally:
        await test_runner.cleanup()
        # 清理本地创建的测试 ZIP 文件
        for path in created_paths:
            if os.path.exists(path):
                os.remove(path)


async def ci_cd_integration_example():
    """Example for CI/CD integration."""
    
    api_key = os.getenv("AGENTBAY_API_KEY")
    if not api_key:
        print("❌ Please set AGENTBAY_API_KEY environment variable")
        return False
    
    test_runner = ExtensionTestRunner(api_key, "ci_cd_tests")
    
    try:
        # Define multiple test suites for different scenarios
        test_suites = [
            TestSuite(
                name="smoke_tests",
                extension_paths=["/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip"],
                test_cases=["extension_loaded", "manifest_valid"],
                timeout=60
            ),
            TestSuite(
                name="functional_tests",
                extension_paths=["/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip"],
                test_cases=["extension_functional"],
                timeout=300
            ),
            TestSuite(
                name="compatibility_tests",
                extension_paths=[
                    "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension.zip",
                    "/Users/liyuebing/Projects/wuying-agentbay-sdk/tmp/test-extension-v2.zip"
                ],
                test_cases=["extension_loaded", "manifest_valid"],
                timeout=180
            )
        ]
        
        # Resolve extension paths: create missing ZIPs
        import zipfile
        ext_dir = os.path.dirname(__file__)
        created_paths = []
        all_extension_paths = set()
        for suite in test_suites:
            for path in suite.extension_paths:
                all_extension_paths.add(path)

        # Create missing ZIPs once
        path_map = {}
        for i, path in enumerate(sorted(all_extension_paths)):
            if os.path.exists(path):
                path_map[path] = path
            else:
                name = f"test-extension-v{i+1}.zip"
                local_path = os.path.join(ext_dir, name)
                print(f"📦 Creating test extension ZIP: {local_path}")
                with zipfile.ZipFile(local_path, "w") as zf:
                    zf.writestr("manifest.json", f'{{"manifest_version": 2, "name": "test-extension-v{i+1}", "version": "1.0"}}')
                path_map[path] = local_path
                created_paths.append(local_path)

        # Update suites with resolved paths
        for suite in test_suites:
            suite.extension_paths = [path_map.get(p, p) for p in suite.extension_paths]
        
        # Run all test suites
        overall_summary = await test_runner.run_multiple_test_suites(test_suites)
        
        # Generate CI/CD compatible report
        test_runner.generate_test_report("ci_test_report.txt")
        
        # Return exit code for CI/CD
        success = overall_summary.get("total_failed", 1) == 0
        exit_code = 0 if success else 1
        
        print(f"\n🎯 CI/CD Result: Exit code {exit_code}")
        return success
        
    except Exception as e:
        print(f"❌ CI/CD test failed: {e}")
        return False
    finally:
        await test_runner.cleanup()
        # 清理本地创建的测试 ZIP 文件
        for path in created_paths:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    import asyncio
    
    async def main():
        print("Extension Testing Automation Examples")
        print("=" * 70)
        
        print("\n1. Basic Test Automation Example")
        print("-" * 50)
        basic_success = await basic_test_automation_example()
        
        print("\n2. CI/CD Integration Example")
        print("-" * 50)
        ci_success = await ci_cd_integration_example()
        
        print("\n🎯 Testing automation examples completed!")
        print(f"   Basic tests: {'✅ PASSED' if basic_success else '❌ FAILED'}")
        print(f"   CI/CD tests: {'✅ PASSED' if ci_success else '❌ FAILED'}")
        
        print("\n💡 Tips for extension testing:")
        print("   - Update extension paths with your actual test files")
        print("   - Customize test cases based on your extension functionality")
        print("   - Use meaningful test suite names for better organization")
        print("   - Integrate with your CI/CD pipeline using exit codes")
    
    asyncio.run(main())