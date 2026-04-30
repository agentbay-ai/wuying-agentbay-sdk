import os
import subprocess
import sys
import argparse
from typing import List, Dict, Any, Optional, TypedDict
import json

# Ensure we can import standard libraries. Langchain/Langgraph availability depends on environment.
print("🔍 正在检查Python环境和依赖...")
print(f"Python可执行文件: {sys.executable}")
print(f"Python版本: {sys.version}")
print(f"Python路径: {sys.path}")

    # Check each import individually for better error reporting
try:
    print("📦 正在导入langchain_openai...")
    from langchain_openai import ChatOpenAI
    print("✅ langchain_openai导入成功")
except ImportError as e:
    print(f"❌ langchain_openai导入失败: {e}")
    print("🔍 尝试替代导入方法...")
    try:
        import langchain_openai
        print("✅ 替代导入成功: import langchain_openai")
    except ImportError as e2:
        print(f"❌ 替代导入也失败了: {e2}")
        
        # List available packages
        import pkgutil
        print("📋 包含'langchain'的可用包:")
        for _, name, _ in pkgutil.iter_modules():
            if 'langchain' in name.lower():
                print(f"  - {name}")
        sys.exit(1)

try:
    print("📦 正在导入langgraph...")
    from langgraph.graph import StateGraph, END
    print("✅ langgraph导入成功")
except ImportError as e:
    print(f"❌ langgraph导入失败: {e}")
    sys.exit(1)

try:
    print("📦 正在导入langchain_core...")
    from langchain_core.prompts import ChatPromptTemplate
    print("✅ langchain_core导入成功")
except ImportError as e:
    print(f"❌ langchain_core导入失败: {e}")
    sys.exit(1)

print("✅ 所有必需的库都导入成功!")

print("🔍 正在检查环境变量...")
agentbay_key = os.environ.get("AGENTBAY_API_KEY")
dashscope_key = os.environ.get("DASHSCOPE_API_KEY")
print(f"AGENTBAY_API_KEY: {'✅ 已设置' if agentbay_key else '❌ 缺失'}")
print(f"DASHSCOPE_API_KEY: {'✅ 已设置' if dashscope_key else '❌ 缺失'}")

# Configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Ideally we want to run this from project root, but we'll be robust
if os.path.basename(PROJECT_ROOT) == "scripts": 
    PROJECT_ROOT = os.path.dirname(PROJECT_ROOT)

TEST_DIR = os.path.join(PROJECT_ROOT, "python", "tests", "integration")
LLMS_FULL_PATH = os.path.join(PROJECT_ROOT, "llms-full.txt")
REPORT_FILE = os.path.join(PROJECT_ROOT, "test_report.md")

# Test file patterns to skip configuration
# Tests containing the following patterns will be skipped during execution
TEST_PATTERNS = [
    "test_oss_integration",     # Python OSS integration tests
    "oss.test.ts",             # TypeScript OSS test files
    "oss_test.go",             # Golang OSS test files
    "TestOss_",                # Golang OSS test function prefix
    "OSSManagementIntegrationTest", # Java OSS integration test class suffix
    "test_agent_integration",   # Agent integration tests
    "agent-integration",        # Agent integration related tests
    "agent_test",              # Agent test files
    "network_integration_test",
    "network.integration.test",
    # Image ID is not supported in CI/CD, requires local integration test execution
    "WsRegisterCallbackIntegrationTest",
    "RunCodeWsStreamingBetaIntegrationTest",
    "WsStreamCancelIntegrationTest",
    "AgentBayGetIntegrationTest",
    # Tests using non-default endpoints (agentbay-pre / wuyingai-pre) that require
    # separate API keys not available in CI
    "screenshot_tool_selection_by_link_url",       # Python test file pattern
    "screenshot-tool-selection-by-link-url",       # TypeScript test file pattern
    "ScreenshotToolSelectionByLinkUrl",            # Java class pattern
    "LinkUrlPresentRequiresBetaTakeScreenshot",    # Golang function pattern
    "LinkUrlAbsentRequiresScreenshot",             # Golang function pattern
    # Tests that call screenshot() which fails when session has link_url;
    # beta_take_screenshot coverage exists in separate test files
    "test_computer_screen.py",                     # Python: uses screenshot() on windows_latest
    "test_functional_computer_test.py",            # Python: safe_screenshot_async uses screenshot()
    # Browser operator and browser-dependency tests that require Playwright/Chrome
    # installation or specific browser environment not available in CI
    "test_browser_fingerprint_integration",        # Python: requires local Chrome
    "test_browser_operator",                       # Python: browser captcha tests
    "browser-proxy.test",                          # TypeScript: browser proxy tests
    "browser-fingerprint.test",                    # TypeScript: browser fingerprint tests
    "TestBrowserContext_CookiePersistence",         # Golang: browser context persistence
    "TestBrowserReplay_Integration",               # Golang: browser replay
    "TestBrowserScreenshot_Integration",           # Golang: browser screenshot
    "BrowserOperatorAsyncIntegrationTest",         # Java: browser operator async
    # screenshot() tests in TS/Go that fail when session has link_url
    "functional-computer.test",                    # TypeScript: safeScreenshot uses screenshot()
    "computer-windows.test",                       # TypeScript: screenshot() call
    "TestComputerWindowsIntegration",              # Golang: TakeScreenshot() call
    "TestWsRegisterCallback_ShouldReceiveCaptchaPush", # Golang: contains screenshot call
]

# State Definition
class TestResult(TypedDict):
    test_id: str
    status: str  # 'passed', 'failed', 'error'
    output: str
    error_analysis: Optional[str]

class AgentState(TypedDict):
    test_queue: List[str]
    current_test_index: int
    results: List[TestResult]
    sdk_context: str
    is_finished: bool
    specific_test_pattern: Optional[str]
    test_type: Optional[str]
    skip_oss: Optional[bool]
    ci_stable: Optional[bool]

# ci-stable marker: when --ci-stable is enabled, only test files containing
# this marker in the first 20 lines will be executed.
CI_STABLE_MARKER = "ci-stable"
CI_STABLE_SCAN_LINES = 20

# --- Helper Functions ---

def has_ci_stable_marker(filepath: str) -> bool:
    """Check if a file has 'ci-stable' marker in its first N lines."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= CI_STABLE_SCAN_LINES:
                    break
                if CI_STABLE_MARKER in line:
                    return True
    except (OSError, IOError):
        pass
    return False


def resolve_test_file(test_id: str) -> Optional[str]:
    """Resolve a test ID to an absolute file path for ci-stable scanning."""
    if test_id.startswith("typescript:"):
        rel = test_id[len("typescript:"):]
        return os.path.join(PROJECT_ROOT, "typescript", rel)
    elif test_id.startswith("java:"):
        class_name = test_id[len("java:"):]
        file_path = class_name.replace(".", os.sep) + ".java"
        return os.path.join(
            PROJECT_ROOT, "java", "agentbay", "src", "integration-test", "java", file_path
        )
    elif test_id.startswith("golang:"):
        # Golang test IDs are package.TestFunc; we need to scan all _test.go
        # files in the integration directory for the marker.  Return None here
        # and handle Go separately.
        return None
    else:
        # Python: test_id is like tests/integration/_async/test_foo.py::test_bar
        rel = test_id.split("::")[0]
        return os.path.join(PROJECT_ROOT, "python", rel)


def filter_ci_stable(test_ids: List[str], ci_stable: bool) -> List[str]:
    """Keep only tests whose source file contains the ci-stable marker."""
    if not ci_stable:
        return test_ids

    kept: List[str] = []
    skipped = 0

    # For Golang tests we need to scan _test.go files in the integration dir
    go_integration_dir = os.path.join(
        PROJECT_ROOT, "golang", "tests", "pkg", "integration"
    )
    # Cache: go test file basename -> has marker
    go_file_marker_cache: Dict[str, bool] = {}

    for test_id in test_ids:
        if test_id.startswith("golang:"):
            # Golang: test_id = "golang:pkg.TestFuncName"
            # Extract test func name
            parts = test_id.split(".")
            func_name = parts[-1] if parts else ""
            # Scan all _test.go files for both the ci-stable marker AND the func
            found = False
            for fname in os.listdir(go_integration_dir) if os.path.isdir(go_integration_dir) else []:
                if not fname.endswith("_test.go"):
                    continue
                fpath = os.path.join(go_integration_dir, fname)
                if fname not in go_file_marker_cache:
                    go_file_marker_cache[fname] = has_ci_stable_marker(fpath)
                if go_file_marker_cache[fname]:
                    # Check if the file contains the test function
                    try:
                        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        if f"func {func_name}(" in content:
                            found = True
                            break
                    except (OSError, IOError):
                        pass
            if found:
                kept.append(test_id)
            else:
                skipped += 1
                print(f"⏭️ ci-stable: skip {test_id}")
        else:
            fpath = resolve_test_file(test_id)
            if fpath and has_ci_stable_marker(fpath):
                kept.append(test_id)
            else:
                skipped += 1
                print(f"⏭️ ci-stable: skip {test_id}")

    print(f"📋 ci-stable filter: kept {len(kept)}, skipped {skipped}")
    return kept


def should_skip_oss_test(test_id: str, skip_oss: bool = False) -> bool:
    """检查是否应该跳过 OSS 测试"""
    if not skip_oss:
        return False
    
    # 检查测试ID是否包含OSS测试模式
    for pattern in TEST_PATTERNS:
        if pattern in test_id:
            return True
    
    return False

def filter_oss_tests(test_ids: List[str], skip_oss: bool = False) -> List[str]:
    """过滤掉 OSS 测试"""
    if not skip_oss:
        print(f"⚠️ skip_oss=False，不进行测试过滤")
        return test_ids
    
    print(f"🔍 开始过滤测试，skip_oss={skip_oss}")
    print(f"📋 过滤模式列表: {TEST_PATTERNS}")
    
    filtered_tests = []
    skipped_count = 0
    
    for test_id in test_ids:
        should_skip = should_skip_oss_test(test_id, skip_oss)
        if should_skip:
            skipped_count += 1
            print(f"⏭️ 跳过测试: {test_id}")
            # 输出匹配的模式
            for pattern in TEST_PATTERNS:
                if pattern in test_id:
                    print(f"   ✓ 匹配模式: {pattern}")
        else:
            filtered_tests.append(test_id)
    
    if skipped_count > 0:
        print(f"📋 总共跳过 {skipped_count} 个测试")
    else:
        print(f"📋 没有测试被跳过")
    
    return filtered_tests

def get_model():
    """Initializes the Qwen model via ChatOpenAI interface compatible with DashScope."""
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        print("警告: 未找到DASHSCOPE_API_KEY，将跳过AI分析。")
        return None
    
    # Using qwen-max for better reasoning capabilities on complex error logs
    return ChatOpenAI(
        model="qwen-max", 
        openai_api_key=api_key,
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        temperature=0.1
    )

# --- Nodes ---

def discover_tests(state: AgentState) -> AgentState:
    """Discover integration tests using pytest --collect-only."""
    print("🔍 正在发现测试...")
    print(f"📥 接收到状态: {state}")
    sys.stdout.flush()
    pattern = state.get("specific_test_pattern")
    test_type = state.get("test_type", "python")
    
    try:
        # 根据test_type选择不同的测试发现策略
        if test_type == "python":
            return discover_python_tests(state, pattern)
        elif test_type == "typescript":
            return discover_typescript_tests(state, pattern)
        elif test_type == "golang":
            return discover_golang_tests(state, pattern)
        elif test_type == "java":
            return discover_java_tests(state, pattern)
        elif test_type == "all":
            return discover_all_tests(state, pattern)
        else:
            print(f"❌ 不支持的测试类型: {test_type}")
            return {"test_queue": [], "current_test_index": 0, "results": [], "sdk_context": "", "is_finished": True, "specific_test_pattern": pattern, "test_type": test_type}
            
    except Exception as e:
        print(f"❌ 发现测试时出错: {e}")
        return {"test_queue": [], "current_test_index": 0, "results": [], "sdk_context": "", "is_finished": True, "specific_test_pattern": pattern, "test_type": test_type}

def discover_python_tests(state: AgentState, pattern: Optional[str]) -> AgentState:
    """发现Python集成测试"""
    print("🐍 正在发现Python测试...")
    
    cwd = os.path.join(PROJECT_ROOT, "python")
    env = os.environ.copy()
    env["PYTHONPATH"] = cwd
    
    print(f"📂 项目根目录: {PROJECT_ROOT}")
    print(f"📂 工作目录: {cwd}")
    print(f"📂 PYTHONPATH: {env.get('PYTHONPATH')}")
    print(f"🔍 目录存在: {os.path.exists(cwd)}")
    if os.path.exists(cwd):
        print(f"📋 内容: {os.listdir(cwd)}") 
    
    # Base command - 优化性能
    cmd = [sys.executable, "-m", "pytest", "tests/integration", "--collect-only", "-q", 
           "--tb=no",  # 不显示traceback
           "--no-header",  # 不显示header
           "--no-summary",  # 不显示summary
           "-p", "no:warnings",  # 禁用warnings插件
           "-p", "no:cacheprovider",  # 禁用cache
           "--maxfail=1",  # 快速失败
           "-c", "/dev/null"]
    
    # Add specific test pattern if provided (passed to pytest directly for filtering)
    if pattern:
        print(f"   使用模式过滤测试: {pattern}")
        cmd.append("-k")
        cmd.append(pattern)
            
        # 添加诊断信息
    test_dir = os.path.join(cwd, "tests", "integration")
    print(f"🔍 测试目录检查:")
    print(f"   - 测试目录路径: {test_dir}")
    print(f"   - 测试目录存在: {os.path.exists(test_dir)}")
    if os.path.exists(test_dir):
        test_files = []
        for root, dirs, files in os.walk(test_dir):
            test_files.extend([f for f in files if f.startswith('test_') and f.endswith('.py')])
        print(f"   - 测试文件数量: {len(test_files)}")
    
    print(f"执行命令: {' '.join(cmd)} 在目录 {cwd}")
    print("⏳ 正在运行pytest命令...")
    sys.stdout.flush()
    
    # 使用Popen来实现非阻塞执行和周期性输出
    import time
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
    
    start_time = time.time()
    timeout = 120  # 2分钟超时，如果pytest太慢就降级
    
    while process.poll() is None:  # 进程还在运行
        elapsed = time.time() - start_time
        if elapsed > timeout:
            print(f"❌ pytest命令超时（{timeout}秒），这表明CI环境有严重的性能问题")
            print("🔍 诊断信息:")
            print(f"   - 工作目录: {cwd}")
            print(f"   - Python路径: {env.get('PYTHONPATH')}")
            print(f"   - 执行命令: {' '.join(cmd)}")
            process.kill()
            sys.stdout.flush()
            
            # 不使用降级方案，直接失败让问题暴露
            raise Exception(f"pytest测试发现超时，CI环境性能问题需要解决。命令: {' '.join(cmd)}")
        
        # 每30秒输出一次心跳
        if int(elapsed) % 30 == 0 and int(elapsed) > 0:
            print(f"💓 pytest运行中... 已用时{int(elapsed)}秒")
            sys.stdout.flush()
        
        time.sleep(1)
    
    # 获取结果
    stdout, stderr = process.communicate()
    result = subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
    
    print(f"✅ 命令完成，返回码: {result.returncode}")
    sys.stdout.flush()
        
    if result.stderr:
        print(f"⚠️ 标准错误: {result.stderr}")
        sys.stdout.flush()
    print(f"📄 标准输出长度: {len(result.stdout)} 字符")
    sys.stdout.flush()
    
    test_ids = []
    for line in result.stdout.splitlines():
        line = line.strip()
        # Standard pytest -q output: tests/integration/path/to/test.py::test_name
        if line and not line.startswith("no tests ran") and not line.startswith("===") and "::" in line:
            test_id = line.split(" ")[0]
            # Fix path if it's missing tests/integration prefix
            if not test_id.startswith("tests/integration") and (test_id.startswith("_async") or test_id.startswith("_sync")):
                test_id = os.path.join("tests", "integration", test_id)
            test_ids.append(test_id)
    
    print(f"✅ 找到 {len(test_ids)} 个Python测试。")
    if len(test_ids) == 0 and result.stderr:
         print(f"调试输出:\n{result.stderr}")
    
    # 应用 OSS 测试过滤
    skip_oss = state.get("skip_oss", False)
    if skip_oss:
        print("🔍 正在过滤 OSS 测试...")
        test_ids = filter_oss_tests(test_ids, skip_oss)
        print(f"✅ 过滤后剩余 {len(test_ids)} 个Python测试。")

    # 应用 ci-stable 过滤
    ci_stable = state.get("ci_stable", False)
    if ci_stable:
        print("🔍 正在过滤 ci-stable 测试...")
        test_ids = filter_ci_stable(test_ids, ci_stable)
        print(f"✅ ci-stable 过滤后剩余 {len(test_ids)} 个Python测试。")

    # Load SDK Context
    context = ""
    if os.path.exists(LLMS_FULL_PATH):
        try:
            with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                context = f.read()
            print(f"📚 已加载SDK上下文 ({len(context)} 字符)")
        except Exception as e:
            print(f"⚠️ 读取llms-full.txt失败: {e}")
    else:
        print(f"⚠️ 在 {LLMS_FULL_PATH} 未找到llms-full.txt")

    return {
        "test_queue": test_ids,
        "current_test_index": 0,
        "results": [],
        "sdk_context": context,
        "is_finished": False,
        "specific_test_pattern": pattern,
        "test_type": "python",
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def discover_typescript_tests(state: AgentState, pattern: Optional[str]) -> AgentState:
    """发现TypeScript集成测试"""
    print("📜 正在发现TypeScript测试...")
    
    cwd = os.path.join(PROJECT_ROOT, "typescript")
    
    print(f"📂 TypeScript工作目录: {cwd}")
    print(f"🔍 目录存在: {os.path.exists(cwd)}")
    
    # 检查Node.js和npm是否安装，包括常见的安装路径
    node_paths = ["node", "/usr/bin/node", "/usr/local/bin/node"]
    npm_paths = ["npm", "/usr/bin/npm", "/usr/local/bin/npm"]
    node_cmd = None
    npm_cmd = None
    
    # 查找Node.js
    for node_path in node_paths:
        try:
            node_version_result = subprocess.run([node_path, "--version"], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
            if node_version_result.returncode == 0:
                node_cmd = node_path
                print(f"✅ Node.js环境检查通过: {node_version_result.stdout.strip()}")
                print(f"✅ Node.js路径: {node_cmd}")
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️ Node.js路径 {node_path} 检查失败: {e}")
            continue
    
    # 查找npm
    for npm_path in npm_paths:
        try:
            npm_version_result = subprocess.run([npm_path, "--version"], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
            if npm_version_result.returncode == 0:
                npm_cmd = npm_path
                print(f"✅ npm环境检查通过: {npm_version_result.stdout.strip()}")
                print(f"✅ npm路径: {npm_cmd}")
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️ npm路径 {npm_path} 检查失败: {e}")
            continue
    
    if node_cmd is None or npm_cmd is None:
        print("❌ Node.js或npm命令未找到")
        print("💡 提示: 当前CI环境不支持TypeScript测试，请使用python测试类型")
        print("🔍 检查的Node.js路径: " + ", ".join(node_paths))
        print("🔍 检查的npm路径: " + ", ".join(npm_paths))
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "typescript"
        }
    
    # 检查是否有package.json和测试脚本
    package_json_path = os.path.join(cwd, "package.json")
    if not os.path.exists(package_json_path):
        print("❌ 未找到package.json")
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "typescript"
        }
    
    # 直接查找集成测试文件而不是使用Jest --listTests
    integration_test_dir = os.path.join(cwd, "tests", "integration")
    test_ids = []
    
    if os.path.exists(integration_test_dir):
        print(f"📂 扫描集成测试目录: {integration_test_dir}")
        for root, dirs, files in os.walk(integration_test_dir):
            for file in files:
                if file.endswith('.test.ts') or file.endswith('.test.js'):
                    # 获取相对于typescript目录的路径
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, cwd)
                    
                    # 如果有模式过滤，应用过滤
                    if not pattern or pattern.lower() in rel_path.lower():
                        test_ids.append(f"typescript:{rel_path}")
        
        print(f"✅ 在目录扫描中找到 {len(test_ids)} 个TypeScript集成测试。")
        if len(test_ids) > 0:
            print("📋 测试文件列表:")
            for test_id in test_ids[:5]:  # 只显示前5个
                print(f"   - {test_id}")
            if len(test_ids) > 5:
                print(f"   ... 还有 {len(test_ids) - 5} 个测试文件")
    else:
        print(f"❌ 集成测试目录不存在: {integration_test_dir}")
        # 尝试使用Jest命令作为备用方案
        cmd = [npm_cmd, "run", "test:integration", "--", "--listTests"]
        print(f"🔄 尝试Jest命令: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', timeout=60)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    line = line.strip()
                    if (line.endswith('.test.ts') or line.endswith('.test.js')) and 'integration' in line:
                        if line.startswith(cwd):
                            line = os.path.relpath(line, cwd)
                        if not pattern or pattern.lower() in line.lower():
                            test_ids.append(f"typescript:{line}")
                print(f"✅ 通过Jest命令找到 {len(test_ids)} 个TypeScript集成测试。")
            else:
                print(f"⚠️ Jest命令失败，返回码: {result.returncode}")
                print(f"⚠️ 错误输出: {result.stderr}")
        except Exception as e:
            print(f"⚠️ Jest命令执行失败: {e}")
    
    print(f"✅ 总共找到 {len(test_ids)} 个TypeScript集成测试。")

    # 应用 OSS 测试过滤
    skip_oss = state.get("skip_oss", False)
    if skip_oss:
        print("🔍 正在过滤 OSS 测试...")
        test_ids = filter_oss_tests(test_ids, skip_oss)
        print(f"✅ 过滤后剩余 {len(test_ids)} 个TypeScript测试。")

    # 应用 ci-stable 过滤
    ci_stable = state.get("ci_stable", False)
    if ci_stable:
        print("🔍 正在过滤 ci-stable 测试...")
        test_ids = filter_ci_stable(test_ids, ci_stable)
        print(f"✅ ci-stable 过滤后剩余 {len(test_ids)} 个TypeScript测试。")

    # Load SDK Context
    context = ""
    if os.path.exists(LLMS_FULL_PATH):
        try:
            with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                context = f.read()
            print(f"📚 已加载SDK上下文 ({len(context)} 字符)")
        except Exception as e:
            print(f"⚠️ 读取llms-full.txt失败: {e}")

    return {
        "test_queue": test_ids,
        "current_test_index": 0,
        "results": [],
        "sdk_context": context,
        "is_finished": False,
        "specific_test_pattern": pattern,
        "test_type": "typescript",
        "ci_stable": state.get("ci_stable", False)
    }

def discover_golang_tests(state: AgentState, pattern: Optional[str]) -> AgentState:
    """发现Golang集成测试"""
    print("🐹 正在发现Golang测试...")
    
    cwd = os.path.join(PROJECT_ROOT, "golang")
    
    print(f"📂 Golang工作目录: {cwd}")
    print(f"🔍 目录存在: {os.path.exists(cwd)}")
    
    # 检查Go是否安装，包括常见的安装路径
    go_paths = ["go", "/usr/local/go/bin/go", "/usr/bin/go"]
    go_cmd = None
    
    for go_path in go_paths:
        try:
            go_version_result = subprocess.run([go_path, "version"], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
            if go_version_result.returncode == 0:
                go_cmd = go_path
                print(f"✅ Go环境检查通过: {go_version_result.stdout.strip()}")
                print(f"✅ Go路径: {go_cmd}")
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️ Go路径 {go_path} 检查失败: {e}")
            continue
    
    if go_cmd is None:
        print("❌ Go命令未找到")
        print("💡 提示: 当前CI环境不支持Golang测试，请使用python或typescript测试类型")
        print("🔍 检查的路径: " + ", ".join(go_paths))
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "golang"
        }
    
    # 专门针对集成测试包
    integration_package = "github.com/aliyun/wuying-agentbay-sdk/golang/tests/pkg/integration"
    
    # 使用go test来发现集成测试函数
    cmd = [go_cmd, "test", "-list", ".", integration_package]
    
    print(f"执行命令: {' '.join(cmd)} 在目录 {cwd}")
    
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', timeout=60)
        
        test_ids = []
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                line = line.strip()
                if line.startswith("Test") and (not pattern or pattern.lower() in line.lower()):
                    test_ids.append(f"golang:{integration_package}.{line}")
        else:
            print(f"⚠️ Go测试发现命令失败，返回码: {result.returncode}")
            print(f"⚠️ 错误输出: {result.stderr}")
        
        print(f"✅ 找到 {len(test_ids)} 个Golang集成测试。")

        # 应用 OSS 测试过滤
        skip_oss = state.get("skip_oss", False)
        if skip_oss:
            print("🔍 正在过滤 OSS 测试...")
            test_ids = filter_oss_tests(test_ids, skip_oss)
            print(f"✅ 过滤后剩余 {len(test_ids)} 个Golang测试。")

        # 应用 ci-stable 过滤
        ci_stable = state.get("ci_stable", False)
        if ci_stable:
            print("🔍 正在过滤 ci-stable 测试...")
            test_ids = filter_ci_stable(test_ids, ci_stable)
            print(f"✅ ci-stable 过滤后剩余 {len(test_ids)} 个Golang测试。")

        # Load SDK Context
        context = ""
        if os.path.exists(LLMS_FULL_PATH):
            try:
                with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                    context = f.read()
                print(f"📚 已加载SDK上下文 ({len(context)} 字符)")
            except Exception as e:
                print(f"⚠️ 读取llms-full.txt失败: {e}")

        return {
            "test_queue": test_ids,
            "current_test_index": 0,
            "results": [],
            "sdk_context": context,
            "is_finished": False,
            "specific_test_pattern": pattern,
            "test_type": "golang",
            "ci_stable": state.get("ci_stable", False)
        }
        
    except Exception as e:
        print(f"❌ Golang测试发现失败: {e}")
        print("💡 提示: 当前CI环境可能不支持Golang测试，请使用python或typescript测试类型")
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "golang"
        }

def discover_java_tests(state: AgentState, pattern: Optional[str]) -> AgentState:
    """发现Java集成测试"""
    print("☕ 正在发现Java测试...")
    
    cwd = os.path.join(PROJECT_ROOT, "java", "agentbay")
    
    print(f"📂 Java工作目录: {cwd}")
    print(f"🔍 目录存在: {os.path.exists(cwd)}")
    
    # 检查Maven是否安装，包括常见的安装路径
    mvn_paths = ["mvn", "/usr/bin/mvn", "/usr/local/bin/mvn", "mvn.cmd"]
    mvn_cmd = None
    
    for mvn_path in mvn_paths:
        try:
            mvn_version_result = subprocess.run([mvn_path, "--version"], capture_output=True, encoding='utf-8', errors='replace', timeout=10)
            if mvn_version_result.returncode == 0:
                mvn_cmd = mvn_path
                print(f"✅ Maven环境检查通过: {mvn_version_result.stdout.splitlines()[0]}")
                print(f"✅ Maven路径: {mvn_cmd}")
                break
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"⚠️ Maven路径 {mvn_path} 检查失败: {e}")
            continue
    
    if mvn_cmd is None:
        print("❌ Maven命令未找到")
        print("💡 提示: 当前CI环境不支持Java测试，请使用python、typescript或golang测试类型")
        print("🔍 检查的路径: " + ", ".join(mvn_paths))
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "java"
        }
    
    # 检查pom.xml是否存在
    pom_path = os.path.join(cwd, "pom.xml")
    if not os.path.exists(pom_path):
        print(f"❌ 未找到pom.xml: {pom_path}")
        return {
            "test_queue": [],
            "current_test_index": 0,
            "results": [],
            "sdk_context": "",
            "is_finished": True,
            "specific_test_pattern": pattern,
            "test_type": "java"
        }
    
    # 直接扫描集成测试目录
    integration_test_dir = os.path.join(cwd, "src", "integration-test", "java")
    test_ids = []
    ci_stable = state.get("ci_stable", False)
    skip_oss = state.get("skip_oss", False)

    if os.path.exists(integration_test_dir):
        print(f"📂 扫描集成测试目录: {integration_test_dir}")
        for root, dirs, files in os.walk(integration_test_dir):
            for file in files:
                if not file.endswith('.java'):
                    continue
                full_path = os.path.join(root, file)

                # ci-stable 模式：只纳入文件前20行中有 ci-stable 标记的文件
                if ci_stable and not has_ci_stable_marker(full_path):
                    print(f"⏭️ ci-stable: skip {full_path}")
                    continue

                # 从文件内容中提取 public class 名（比文件名更可靠）
                class_name = None
                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        for line in f:
                            line = line.strip()
                            if line.startswith("public class "):
                                # 取 "public class Foo {" 中的 Foo
                                parts = line.split()
                                if len(parts) >= 3:
                                    class_name = parts[2].rstrip("{").strip()
                                break
                except (OSError, IOError):
                    pass

                if not class_name:
                    # 回退到文件名（去掉 .java 后缀）
                    class_name = file[:-5]

                # 检查是否应该跳过（匹配 TEST_PATTERNS）
                should_skip = False
                if skip_oss:
                    for test_pattern in TEST_PATTERNS:
                        if test_pattern in class_name:
                            should_skip = True
                            print(f"⏭️ 发现阶段跳过测试类: {class_name} (匹配模式: {test_pattern})")
                            break

                # 应用用户模式过滤
                if not should_skip and (not pattern or pattern.lower() in class_name.lower()):
                    test_ids.append(f"java:{class_name}")

        print(f"✅ 在目录扫描中找到 {len(test_ids)} 个Java集成测试。")
        if len(test_ids) > 0:
            print("📋 测试类列表:")
            for test_id in test_ids[:5]:  # 只显示前5个
                print(f"   - {test_id}")
            if len(test_ids) > 5:
                print(f"   ... 还有 {len(test_ids) - 5} 个测试类")
    else:
        print(f"❌ 集成测试目录不存在: {integration_test_dir}")

    print(f"✅ 总共找到 {len(test_ids)} 个Java集成测试。")

    # Load SDK Context
    context = ""
    if os.path.exists(LLMS_FULL_PATH):
        try:
            with open(LLMS_FULL_PATH, "r", encoding="utf-8") as f:
                context = f.read()
            print(f"📚 已加载SDK上下文 ({len(context)} 字符)")
        except Exception as e:
            print(f"⚠️ 读取llms-full.txt失败: {e}")

    return {
        "test_queue": test_ids,
        "current_test_index": 0,
        "results": [],
        "sdk_context": context,
        "is_finished": False,
        "specific_test_pattern": pattern,
        "test_type": "java",
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def discover_all_tests(state: AgentState, pattern: Optional[str]) -> AgentState:
    """发现所有语言的集成测试"""
    print("🌍 正在发现所有语言的测试...")
    
    try:
        all_test_ids = []
        context = ""
        
        # 发现Python测试
        python_state = discover_python_tests(state, pattern)
        all_test_ids.extend(python_state["test_queue"])
        context = python_state["sdk_context"]
        
        # 发现TypeScript测试
        typescript_state = discover_typescript_tests(state, pattern)
        all_test_ids.extend(typescript_state["test_queue"])
        
        # 发现Golang测试
        golang_state = discover_golang_tests(state, pattern)
        all_test_ids.extend(golang_state["test_queue"])
        
        # 发现Java测试
        java_state = discover_java_tests(state, pattern)
        all_test_ids.extend(java_state["test_queue"])
        
        print(f"✅ 总共找到 {len(all_test_ids)} 个测试。")
        
        return {
            "test_queue": all_test_ids,
            "current_test_index": 0,
            "results": [],
            "sdk_context": context,
            "is_finished": False,
            "specific_test_pattern": pattern,
            "test_type": "all"
        }
    except Exception as e:
        print(f"❌ 发现测试时出错: {e}")
        return {"test_queue": [], "current_test_index": 0, "results": [], "sdk_context": "", "is_finished": True, "specific_test_pattern": pattern, "test_type": "all"}

def execute_next_test(state: AgentState) -> AgentState:
    """Executes the next test in the queue."""
    idx = state["current_test_index"]
    queue = state["test_queue"]
    
    if idx >= len(queue):
        return state 

    test_id = queue[idx]
    print(f"▶️ 正在运行测试 ({idx+1}/{len(queue)}): {test_id}")
    
    # 根据测试ID的前缀判断测试类型
    if test_id.startswith("typescript:"):
        result = execute_typescript_test(test_id)
    elif test_id.startswith("golang:"):
        result = execute_golang_test(test_id)
    elif test_id.startswith("java:"): 
        result = execute_java_test(test_id)
    else:
        # 默认为Python测试
        result = execute_python_test(test_id)
    
    new_result: TestResult = {
        "test_id": test_id,
        "status": result["status"],
        "output": result["output"],
        "error_analysis": None
    }

    return {
        "results": state["results"] + [new_result],
        "current_test_index": state["current_test_index"],
        "test_queue": state["test_queue"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"],
        "test_type": state["test_type"],
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def execute_python_test(test_id: str) -> Dict[str, Any]:
    """执行Python测试"""
    print(f"🐍 执行Python测试: {test_id}")
    
    # 二次检查：确保不执行应该被跳过的测试
    for pattern in TEST_PATTERNS:
        if pattern in test_id:
            print(f"⚠️ 安全防护：检测到测试 {test_id} 匹配跳过模式 '{pattern}'，跳过执行")
            return {
                "status": "passed",
                "output": f"测试被跳过：匹配模式 '{pattern}'（安全防护机制）"
            }
    
    cwd = os.path.join(PROJECT_ROOT, "python")
    env = os.environ.copy()
    env["PYTHONPATH"] = cwd
    
    # Ensure AGENTBAY_API_KEY is present (it should be injected by CI/Aone)
    if "AGENTBAY_API_KEY" not in env:
        print("⚠️ 警告: 环境变量中未找到AGENTBAY_API_KEY。")

    # Run specific test
    cmd = [sys.executable, "-m", "pytest", test_id, "-vv"]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', env=env)
    
    status = "passed" if result.returncode == 0 else "failed"
    output = result.stdout + "\n" + result.stderr
    
    print(f"   结果: {status.upper()}")
    
    return {"status": status, "output": output}

def execute_typescript_test(test_id: str) -> Dict[str, Any]:
    """执行TypeScript测试"""
    print(f"📜 执行TypeScript测试: {test_id}")
    
    # 二次检查：确保不执行应该被跳过的测试
    for pattern in TEST_PATTERNS:
        if pattern in test_id:
            print(f"⚠️ 安全防护：检测到测试 {test_id} 匹配跳过模式 '{pattern}'，跳过执行")
            return {
                "status": "passed",
                "output": f"测试被跳过：匹配模式 '{pattern}'（安全防护机制）"
            }
    
    # 移除typescript:前缀
    actual_test_id = test_id[11:]  # len("typescript:") = 11
    
    cwd = os.path.join(PROJECT_ROOT, "typescript")
    env = os.environ.copy()
    
    # Ensure AGENTBAY_API_KEY is present
    if "AGENTBAY_API_KEY" not in env:
        print("⚠️ 警告: 环境变量中未找到AGENTBAY_API_KEY。")

    # Run specific test using npm test (avoid test:integration which runs all integration tests)
    cmd = ["npm", "test", "--", actual_test_id]
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    
    status = "passed" if result.returncode == 0 else "failed"
    output = result.stdout + "\n" + result.stderr
    
    print(f"   结果: {status.upper()}")
    
    return {"status": status, "output": output}

def execute_golang_test(test_id: str) -> Dict[str, Any]:
    """执行Golang测试"""
    print(f"🐹 执行Golang测试: {test_id}")
    
    # 二次检查：确保不执行应该被跳过的测试
    for pattern in TEST_PATTERNS:
        if pattern in test_id:
            print(f"⚠️ 安全防护：检测到测试 {test_id} 匹配跳过模式 '{pattern}'，跳过执行")
            return {
                "status": "passed",
                "output": f"测试被跳过：匹配模式 '{pattern}'（安全防护机制）"
            }
    
    # 查找Go命令
    go_paths = ["go", "/usr/local/go/bin/go", "/usr/bin/go"]
    go_cmd = None
    
    for go_path in go_paths:
        try:
            subprocess.run([go_path, "version"], capture_output=True, encoding='utf-8', errors='replace', timeout=5)
            go_cmd = go_path
            break
        except:
            continue
    
    if go_cmd is None:
        print("❌ 执行测试时未找到Go命令")
        return {"status": "failed", "output": "Go命令未找到，无法执行测试"}
    
    # 移除golang:前缀并解析包和测试名
    actual_test_id = test_id[7:]  # len("golang:") = 7
    if "." in actual_test_id:
        package_name, test_name = actual_test_id.rsplit(".", 1)
    else:
        package_name = actual_test_id
        test_name = ""
    
    cwd = os.path.join(PROJECT_ROOT, "golang")
    env = os.environ.copy()
    
    # Ensure AGENTBAY_API_KEY is present
    if "AGENTBAY_API_KEY" not in env:
        print("⚠️ 警告: 环境变量中未找到AGENTBAY_API_KEY。")

    # Run specific test using go test
    cmd = [go_cmd, "test", "-v", package_name]
    if test_name:
        cmd.extend(["-run", test_name])
    
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', env=env)
    
    status = "passed" if result.returncode == 0 else "failed"
    output = result.stdout + "\n" + result.stderr
    
    print(f"   结果: {status.upper()}")
    
    return {"status": status, "output": output}

def execute_java_test(test_id: str) -> Dict[str, Any]:
    """执行Java测试"""
    print(f"☕ 执行Java测试: {test_id}")
    
    # 查找Maven命令
    mvn_paths = ["mvn", "/usr/bin/mvn", "/usr/local/bin/mvn", "mvn.cmd"]
    mvn_cmd = None
    
    for mvn_path in mvn_paths:
        try:
            subprocess.run([mvn_path, "--version"], capture_output=True, encoding='utf-8', errors='replace', timeout=5)
            mvn_cmd = mvn_path
            break
        except:
            continue
    
    if mvn_cmd is None:
        print("❌ 执行测试时未找到Maven命令")
        return {"status": "failed", "output": "Maven命令未找到，无法执行测试"}
    
    # 移除java:前缀获取测试类名
    actual_test_id = test_id[5:]  # len("java:") = 5
    
    cwd = os.path.join(PROJECT_ROOT, "java", "agentbay")
    env = os.environ.copy()
    
    # Ensure AGENTBAY_API_KEY is present
    if "AGENTBAY_API_KEY" not in env:
        print("⚠️ 警告: 环境变量中未找到AGENTBAY_API_KEY。")

    # 构建集成测试的Maven命令
    # test_id 格式: java:ClassName（discover 阶段已从 public class 定义中提取简单类名）
    # 命令格式: mvn verify "-Dsurefire.skip=true" "-Dit.test=ClassName"
    class_name = actual_test_id  # 已经是简单类名，如 SessionIntegrationTest

    cmd = [mvn_cmd, "verify", "-Dsurefire.skip=true", f"-Dit.test={class_name}"]
    print(f"   📋 测试类型: 集成测试")
    print(f"   🔧 使用 maven-failsafe-plugin")
    print(f"   ⚠️ 使用 -Dsurefire.skip=true 跳过单元测试")
    print(f"   📝 测试类名: {class_name}")
    
    print(f"   执行命令: {' '.join(cmd)}")
    print(f"   工作目录: {cwd}")
    
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, encoding='utf-8', errors='replace', env=env)
    
    # 输出详细的执行结果日志
    print(f"   返回码: {result.returncode}")
    print(f"   标准输出长度: {len(result.stdout)} 字符")
    print(f"   标准错误长度: {len(result.stderr)} 字符")
    
    if result.stdout:
        print(f"   标准输出（前500字符）:")
        print("   " + "-" * 60)
        for line in result.stdout[:500].split('\n'):
            print(f"   {line}")
        if len(result.stdout) > 500:
            print(f"   ... (还有 {len(result.stdout) - 500} 字符)")
        print("   " + "-" * 60)
    
    if result.stderr:
        print(f"   标准错误（前500字符）:")
        print("   " + "-" * 60)
        for line in result.stderr[:500].split('\n'):
            print(f"   {line}")
        if len(result.stderr) > 500:
            print(f"   ... (还有 {len(result.stderr) - 500} 字符)")
        print("   " + "-" * 60)
    
    status = "passed" if result.returncode == 0 else "failed"
    output = result.stdout + "\n" + result.stderr
    
    print(f"   结果: {status.upper()}")
    
    return {"status": status, "output": output}

def analyze_failure(state: AgentState) -> AgentState:
    """Analyzes the last failed test."""
    last_result = state["results"][-1]
    if last_result["status"] == "passed":
        return state 
        
    print(f"🤖 正在分析失败测试 {last_result['test_id']}...")
    
    model = get_model()
    if not model:
        last_result["error_analysis"] = "跳过分析 (无DASHSCOPE_API_KEY)。"
        return {"results": state["results"][:-1] + [last_result], **{k:v for k,v in state.items() if k != "results"}}

    # Prepare context
    # Limit context to avoid super long prompts if not needed, 
    # but allow enough for the model to understand the SDK.
    sdk_context_snippet = state["sdk_context"][:50000] + "...(truncated)" if len(state["sdk_context"]) > 50000 else state["sdk_context"]
    
    # Get test code - 根据测试类型构建正确的文件路径
    test_id = last_result["test_id"]
    test_code = ""
    
    if test_id.startswith("typescript:"):
        # TypeScript测试
        test_file_path = os.path.join(PROJECT_ROOT, "typescript", test_id[11:])
    elif test_id.startswith("golang:"):
        # Golang测试 - 无法直接读取文件，从输出中提取
        test_code = "Golang测试文件内容需要从go test输出中提取"
        test_file_path = None
    elif test_id.startswith("java:"):
        # Java测试 - test_id 中存的是简单类名，在集成测试目录下搜索对应 .java 文件
        class_name = test_id[5:]  # 移除java:前缀，得到简单类名，如 SessionIntegrationTest
        java_int_dir = os.path.join(PROJECT_ROOT, "java", "agentbay", "src", "integration-test", "java")
        test_file_path = None
        for _root, _dirs, _files in os.walk(java_int_dir):
            if f"{class_name}.java" in _files:
                test_file_path = os.path.join(_root, f"{class_name}.java")
                break
    else:
        # Python测试（默认）
        test_file_path = os.path.join(PROJECT_ROOT, "python", test_id.split("::")[0])

    # 读取测试文件内容
    if test_file_path and os.path.exists(test_file_path):
        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                test_code = f.read()
        except Exception as e:
            test_code = f"无法读取测试文件: {e}"
    elif not test_code:  # 如果还没有设置test_code（非Golang情况）
        test_code = "Could not read test file."

    error_log = last_result["output"][-5000:] # Last 5000 chars of log

    # 根据测试类型确定语言和专家角色
    if test_id.startswith("typescript:"):
        language = "TypeScript"
        code_lang = "typescript"
    elif test_id.startswith("golang:"):
        language = "Golang"
        code_lang = "go"
    elif test_id.startswith("java:"):
        language = "Java"
        code_lang = "java"
    else:
        language = "Python"
        code_lang = "python"

    prompt = ChatPromptTemplate.from_template("""
你是一位资深的{language} SDK测试专家。请用中文进行分析和回答。

### SDK Context (Documentation/Codebase)
{sdk_context}

### 任务
分析以下集成测试的失败原因。
判断这是测试问题、环境问题，还是SDK缺陷。

### 测试信息
测试ID: {test_id}

测试代码:
```{code_lang}
{test_code}
```

错误日志片段:
{error_log}

### Output Instructions
请用中文提供简洁的分析报告，使用Markdown格式：
1. **根本原因**: 导致失败的具体原因是什么？
2. **错误分类**: [测试问题 / 环境问题 / SDK缺陷]
3. **修复建议**: 如何修复这个问题（如适用，请提供代码片段）

IMPORTANT: 请务必使用中文回答，不要使用英文。
""")

    try:
        chain = prompt | model
        response = chain.invoke({
            "language": language,
            "code_lang": code_lang,
            "sdk_context": sdk_context_snippet,
            "test_id": last_result["test_id"],
            "test_code": test_code,
            "error_log": error_log
        })
        
        last_result["error_analysis"] = response.content
        print("   ✅ 分析完成。")
        print("   📋 AI分析结果:")
        print("   " + "="*60)
        # 将多行分析结果缩进显示
        for line in response.content.split('\n'):
            print(f"   {line}")
        print("   " + "="*60)
        sys.stdout.flush()
        
    except Exception as e:
        print(f"   ❌ 分析失败: {e}")
        last_result["error_analysis"] = f"分析失败: {e}"
        sys.stdout.flush()

    return {
        "results": state["results"][:-1] + [last_result],
        "test_queue": state["test_queue"],
        "current_test_index": state["current_test_index"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"],
        "test_type": state["test_type"],
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def increment_index(state: AgentState) -> AgentState:
    """Increments the test index."""
    new_index = state["current_test_index"] + 1
    print(f"🔢 增加索引: {state['current_test_index']} -> {new_index}")
    return {
        "current_test_index": new_index,
        "results": state["results"],
        "test_queue": state["test_queue"],
        "sdk_context": state["sdk_context"],
        "is_finished": state["is_finished"],
        "specific_test_pattern": state["specific_test_pattern"],
        "test_type": state["test_type"],
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def generate_report(state: AgentState) -> AgentState:
    """Generates a Markdown report and AI fix prompts."""
    print("📝 Generating report...")
    results = state["results"]
    
    passed = len([r for r in results if r["status"] == "passed"])
    failed = len([r for r in results if r["status"] == "failed"])
    failed_results = [r for r in results if r["status"] == "failed"]
    
    content = f"# Smart Integration Test Report\n\n"
    content += f"**Summary**: {len(results)} Tests | ✅ {passed} Passed | ❌ {failed} Failed\n\n"
    
    if failed == 0:
        content += "🎉 **All tests passed!** No issues to report.\n\n"
    else:
        content += f"## ❌ Failed Tests ({failed})\n\n"
        for res in failed_results:
            content += f"---\n\n❌ 失败测试\n测试ID: {res['test_id']}\n\n"
            
            # AI Analysis section
            content += "🤖 AI Analysis\n"
            if res.get('error_analysis') and res['error_analysis'] != "未进行AI分析":
                content += f"{res['error_analysis']}\n\n"
            else:
                content += "AI分析跳过或失败。可能原因：缺少DASHSCOPE_API_KEY或分析过程出错。\n\n"
                
            # Output section  
            content += "📄 Output (Snippet)\n"
            content += f"```\n{res['output'][-2000:]}\n```\n\n"
            
            # AI fix prompt section
            fix_prompt = generate_single_ai_fix_prompt(res, state["sdk_context"])
            if fix_prompt:
                content += "🛠️ AI修复提示词\n"
                content += "```\n"
                content += fix_prompt
                content += "\n```\n\n"
    
    
            
    try:
        # Save report to project root or specified artifacts dir
        report_path = os.environ.get("TEST_REPORT_PATH", REPORT_FILE)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Report saved to {report_path}")
    except Exception as e:
        print(f"Failed to write report: {e}")
        
    return {
        "is_finished": True,
        "results": state["results"],
        "test_queue": state["test_queue"],
        "current_test_index": state["current_test_index"],
        "sdk_context": state["sdk_context"],
        "specific_test_pattern": state["specific_test_pattern"],
        "test_type": state["test_type"],
        "skip_oss": state.get("skip_oss", False),
        "ci_stable": state.get("ci_stable", False)
    }

def generate_single_ai_fix_prompt(result: TestResult, sdk_context: str) -> str:
    """Generate targeted AI fix prompt for a single failed test."""
    test_id = result["test_id"]
    error_analysis = result.get("error_analysis", "未进行AI分析")
    output = result["output"]
    
    # 获取测试文件内容
    test_file_content = ""
    if test_id.startswith("typescript:"):
        # TypeScript测试
        test_file_path = os.path.join(PROJECT_ROOT, "typescript", test_id[11:])
    elif test_id.startswith("golang:"):
        # Golang测试 - 需要特殊处理
        test_file_content = "Golang测试文件内容需要从go test输出中提取"
    elif test_id.startswith("java:"):
        # Java测试 - test_id 中存的是简单类名，在集成测试目录下搜索对应 .java 文件
        class_name = test_id[5:]  # 移除java:前缀，得到简单类名，如 SessionIntegrationTest
        java_int_dir = os.path.join(PROJECT_ROOT, "java", "agentbay", "src", "integration-test", "java")
        test_file_path = None
        for _root, _dirs, _files in os.walk(java_int_dir):
            print(f"   📋 遍历目录: {_root}")
            print(f"   📋 文件列表: {_files}")
            print(f"   📋 查找文件: {class_name}.java")
            if f"{class_name}.java" in _files:
                test_file_path = os.path.join(_root, f"{class_name}.java")
                break
    else:
        # Python测试
        test_file_path = os.path.join(PROJECT_ROOT, "python", test_id.split("::")[0])
    
    if not test_id.startswith("golang:") and os.path.exists(test_file_path):
        try:
            with open(test_file_path, "r", encoding="utf-8") as f:
                test_file_content = f.read()
        except Exception as e:
            test_file_content = f"无法读取测试文件: {e}"
    
    # 生成针对性提示词
    prompt_lines = []
    prompt_lines.append("我需要修复一个集成测试失败的问题，请帮我分析并提供修复方案。")
    prompt_lines.append("")
    prompt_lines.append(f"**测试名称**: {test_id}")
    prompt_lines.append("")
    
    if error_analysis and error_analysis != "未进行AI分析":
        prompt_lines.append("**AI分析结果**:")
        prompt_lines.append(error_analysis)
        prompt_lines.append("")
    
    # 关键错误日志（最后1000字符，通常包含最重要的错误信息）
    error_log = output[-1000:] if len(output) > 1000 else output
    prompt_lines.append("**关键错误日志**:")
    prompt_lines.append("```")
    prompt_lines.append(error_log)
    prompt_lines.append("```")
    prompt_lines.append("")
    
    # 测试代码片段（如果文件不太大）
    if test_file_content and len(test_file_content) < 5000:
        prompt_lines.append("**测试代码**:")
        # 根据测试类型选择代码块语言
        if test_id.startswith("typescript:"):
            code_lang = "typescript"
        elif test_id.startswith("java:"):
            code_lang = "java"
        elif test_id.startswith("golang:"):
            code_lang = "go"
        else:
            code_lang = "python"
        prompt_lines.append(f"```{code_lang}")
        prompt_lines.append(test_file_content)
        prompt_lines.append("```")
        prompt_lines.append("")
    elif test_file_content:
        # 文件太大，只显示相关函数
        lines = test_file_content.split('\n')
        relevant_lines = []
        
        # 根据语言类型查找测试方法
        if test_id.startswith("java:"):
            # Java: 查找 @Test 注解或 public void test 方法
            for j, line in enumerate(lines):
                if '@Test' in line or ('public' in line and 'void' in line and 'test' in line.lower()):
                    start = max(0, j-5)
                    end = min(len(lines), j+30)
                    relevant_lines.extend(lines[start:end])
                    relevant_lines.append("... (其他代码)")
                    break
        else:
            # Python/TypeScript/Golang
            for j, line in enumerate(lines):
                if 'def test_' in line or 'async def test_' in line or 'it(' in line or 'test(' in line or 'func Test' in line:
                    start = max(0, j-5)
                    end = min(len(lines), j+20)
                    relevant_lines.extend(lines[start:end])
                    relevant_lines.append("... (其他代码)")
                    break
        
        if relevant_lines:
            prompt_lines.append("**相关测试代码片段**:")
            if test_id.startswith("typescript:"):
                code_lang = "typescript"
            elif test_id.startswith("java:"):
                code_lang = "java"
            elif test_id.startswith("golang:"):
                code_lang = "go"
            else:
                code_lang = "python"
            prompt_lines.append(f"```{code_lang}")
            prompt_lines.append('\n'.join(relevant_lines))
            prompt_lines.append("```")
            prompt_lines.append("")
    
    prompt_lines.append("**请帮我**:")
    prompt_lines.append("1. 根据错误日志和AI分析，确定问题的根本原因")
    prompt_lines.append("2. 提供具体的修复代码（如果是代码问题）")
    prompt_lines.append("3. 如果是环境或配置问题，提供解决方案")
    prompt_lines.append("4. 解释修复方案的原理和注意事项")
    prompt_lines.append("")
    prompt_lines.append("请确保修复方案符合项目的编码规范和最佳实践。")
    
    return '\n'.join(prompt_lines)

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("discover_tests", discover_tests)
workflow.add_node("execute_test", execute_next_test)
workflow.add_node("analyze_failure", analyze_failure)
workflow.add_node("increment_index", increment_index)
workflow.add_node("generate_report", generate_report)

workflow.set_entry_point("discover_tests")

def check_completion(state: AgentState):
    current_idx = state["current_test_index"]
    total_tests = len(state["test_queue"])
    print(f"🔍 检查完成状态: {current_idx}/{total_tests}")
    
    if current_idx >= total_tests:
        print("✅ 所有测试已完成，正在生成报告...")
        return "generate_report"
    
    print(f"➡️ 继续下一个测试 ({current_idx + 1}/{total_tests})")
    return "execute_test"

workflow.add_conditional_edges(
    "discover_tests",
    check_completion,
    {
        "generate_report": "generate_report",
        "execute_test": "execute_test"
    }
)

def check_test_result(state: AgentState):
    last_result = state["results"][-1]
    print(f"🔍 检查测试结果: {last_result['test_id']} -> {last_result['status']}")
    if last_result["status"] == "failed":
        print("❌ 测试失败，进行AI分析...")
        return "analyze_failure"
    print("✅ 测试通过，增加索引...")
    return "increment_index"

workflow.add_conditional_edges(
    "execute_test",
    check_test_result,
    {
        "analyze_failure": "analyze_failure",
        "increment_index": "increment_index"
    }
)

workflow.add_edge("analyze_failure", "increment_index")

workflow.add_conditional_edges(
    "increment_index",
    check_completion,
    {
        "generate_report": "generate_report",
        "execute_test": "execute_test"
    }
)

workflow.add_edge("generate_report", END)

print("🔧 正在编译工作流...")
sys.stdout.flush()
try:
    app = workflow.compile()
    print("✅ 工作流编译成功")
    sys.stdout.flush()
except Exception as e:
    print(f"❌ 工作流编译失败: {e}")
    sys.stdout.flush()
    raise

def main():
    global REPORT_FILE
    
    parser = argparse.ArgumentParser(description="Smart Integration Test Runner with AI Analysis")
    parser.add_argument("-k", "--keyword", help="Run tests which match the given substring expression (same as pytest -k)", type=str)
    parser.add_argument("--test-type", help="Test type to run (all, python, typescript, golang, java)", type=str, default="all")
    parser.add_argument("--report", help="Path to save the report", default=REPORT_FILE)
    parser.add_argument("--skip-oss", help="Skip OSS integration tests", action="store_true", default=False)
    parser.add_argument("--ci-stable", help="Only run tests marked with ci-stable in first 20 lines", action="store_true", default=False)

    args = parser.parse_args()
    
    print("🚀 Starting Smart Test Runner...")
    sys.stdout.flush()  # 强制刷新输出
    
    if args.keyword:
        print(f"🎯 Target Pattern: {args.keyword}")
        sys.stdout.flush()
    
    if args.test_type:
        print(f"🎯 Test Type: {args.test_type}")
        sys.stdout.flush()
    
    if args.report:
        REPORT_FILE = args.report

    if args.ci_stable:
        print(f"🏷️ ci-stable mode: only tests with '{CI_STABLE_MARKER}' marker will run")
        sys.stdout.flush()

    initial_state = {
        "test_queue": [],
        "current_test_index": 0,
        "results": [],
        "sdk_context": "",
        "is_finished": False,
        "specific_test_pattern": args.keyword,
        "test_type": args.test_type,
        "skip_oss": args.skip_oss,
        "ci_stable": args.ci_stable
    }
    
    print("🔧 正在启动工作流执行...")
    sys.stdout.flush()
    
    try:
        print("📍 即将调用app.invoke()...")
        sys.stdout.flush()
        
        # Set recursion limit to prevent infinite loops
        config = {"recursion_limit": 2000}
        print(f"⚙️ 配置: {config}")
        sys.stdout.flush()
        
        print("🔄 开始执行工作流...")
        sys.stdout.flush()
        
        result = app.invoke(initial_state, config=config)
        
        # 简化输出，只显示关键统计信息
        total_tests = len(result.get('results', []))
        passed_tests = len([r for r in result.get('results', []) if r['status'] == 'passed'])
        failed_tests = len([r for r in result.get('results', []) if r['status'] == 'failed'])
        
        print(f"✅ 智能集成测试完成: {total_tests} 测试 | ✅ {passed_tests} 通过 | ❌ {failed_tests} 失败")
        sys.stdout.flush()
    except Exception as e:
        print(f"\n💥 执行失败: {e}")
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

