#!/usr/bin/env python3
"""Generate API reference documentation for the Python SDK using pydoc-markdown APIs."""

from __future__ import annotations

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import docspec
import yaml
from pydoc_markdown import PydocMarkdown
from pydoc_markdown.contrib.loaders.python import PythonLoader
from pydoc_markdown.contrib.processors.crossref import CrossrefProcessor
from pydoc_markdown.contrib.processors.filter import FilterProcessor
from pydoc_markdown.contrib.processors.smart import SmartProcessor
from pydoc_markdown.contrib.renderers.markdown import MarkdownRenderer


@dataclass(frozen=True)
class DocMapping:
    target: str
    title: str
    modules: Sequence[str]


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = PROJECT_ROOT / "docs" / "api"
METADATA_PATH = PROJECT_ROOT.parent / "scripts" / "doc-metadata.yaml"

# Sync API docs
DOC_MAPPINGS: Sequence[DocMapping] = (
    DocMapping("sync/agentbay.md", "AgentBay", ("agentbay._sync.agentbay",)),
    DocMapping("sync/network.md", "Network", ("agentbay._sync.beta_network",)),
    DocMapping("sync/session.md", "Session", ("agentbay._sync.session",)),
    DocMapping("sync/command.md", "Command", ("agentbay._sync.command",)),
    DocMapping("sync/context.md", "Context", ("agentbay._sync.context",)),
    DocMapping("sync/context-manager.md", "Context Manager", ("agentbay._sync.context_manager",)),
    DocMapping("sync/filesystem.md", "File System", ("agentbay._sync.filesystem",)),
    DocMapping("sync/agent.md", "Agent", ("agentbay._sync.agent",)),
    DocMapping("sync/oss.md", "OSS", ("agentbay._sync.oss",)),
    DocMapping("sync/browser.md", "Browser", ("agentbay._sync.browser",)),
    DocMapping("sync/browser-operator.md", "BrowserOperator", ("agentbay._sync.browser_operator",)),
    DocMapping("sync/extension.md", "Extension", ("agentbay._sync.extension",)),
    DocMapping("sync/code.md", "Code", ("agentbay._sync.code",)),
    DocMapping("sync/computer.md", "Computer", ("agentbay._sync.computer",)),
    DocMapping("sync/mobile.md", "Mobile", ("agentbay._sync.mobile",)),
    DocMapping("sync/fingerprint.md", "BrowserFingerprint", ("agentbay._sync.fingerprint",)),
    DocMapping("sync/mobile-simulate.md", "MobileSimulate", ("agentbay._sync.mobile_simulate",)),
    DocMapping("sync/session-params.md", "SessionParams", ("agentbay._common.params.session_params",)),
    DocMapping("sync/git.md", "Git", ("agentbay._sync.git.git",)),
    DocMapping("sync/pty.md", "Pty", ("agentbay._sync.pty",)),
    DocMapping("sync/env.md", "Env", ("agentbay._sync.env",)),
)

# Async API docs
ASYNC_DOC_MAPPINGS: Sequence[DocMapping] = (
    DocMapping("async/async-agentbay.md", "AsyncAgentBay", ("agentbay._async.agentbay",)),
    DocMapping("async/async-network.md", "AsyncNetwork", ("agentbay._async.beta_network",)),
    DocMapping("async/async-session.md", "AsyncSession", ("agentbay._async.session",)),
    DocMapping("async/async-command.md", "AsyncCommand", ("agentbay._async.command",)),
    DocMapping("async/async-context.md", "AsyncContext", ("agentbay._async.context",)),
    DocMapping("async/async-context-manager.md", "AsyncContextManager", ("agentbay._async.context_manager",)),
    DocMapping("async/async-filesystem.md", "AsyncFileSystem", ("agentbay._async.filesystem",)),
    DocMapping("async/async-agent.md", "AsyncAgent", ("agentbay._async.agent",)),
    DocMapping("async/async-oss.md", "AsyncOss", ("agentbay._async.oss",)),
    DocMapping("async/async-browser.md", "AsyncBrowser", ("agentbay._async.browser",)),
    DocMapping("async/async-browser-operator.md", "AsyncBrowserOperator", ("agentbay._async.browser_operator",)),
    DocMapping("async/async-extension.md", "AsyncExtension", ("agentbay._async.extension",)),
    DocMapping("async/async-code.md", "AsyncCode", ("agentbay._async.code",)),
    DocMapping("async/async-computer.md", "AsyncComputer", ("agentbay._async.computer",)),
    DocMapping("async/async-mobile.md", "AsyncMobile", ("agentbay._async.mobile",)),
    DocMapping("async/async-fingerprint.md", "AsyncBrowserFingerprint", ("agentbay._async.fingerprint",)),
    DocMapping("async/async-mobile-simulate.md", "AsyncMobileSimulate", ("agentbay._async.mobile_simulate",)),
    DocMapping("async/async-session-params.md", "AsyncSessionParams", ("agentbay._common.params.session_params",)),
    DocMapping("async/async-git.md", "AsyncGit", ("agentbay._async.git.git",)),
    DocMapping("async/async-pty.md", "AsyncPty", ("agentbay._async.pty",)),
    DocMapping("async/async-env.md", "AsyncEnv", ("agentbay._async.env",)),
)

# Common/Shared docs (Config, Exceptions, etc.)
COMMON_DOC_MAPPINGS: Sequence[DocMapping] = (
    DocMapping("common/config.md", "Configuration", ("agentbay._common.config",)),
    DocMapping("common/exceptions.md", "Exceptions", ("agentbay._common.exceptions",)),
    DocMapping("common/logging.md", "Logging", ("agentbay._common.logger",)),
    DocMapping("common/context-sync.md", "Context Sync", ("agentbay._common.params.context_sync",)),
    DocMapping("common/context-mount.md", "Context Mount [Beta]", ("agentbay._common.params.beta_context_mount",)),
    DocMapping("common/lifecycle-policy.md", "Lifecycle Policy", ("agentbay._common.params.lifecycle_policy",)),
    DocMapping("common/code-models.md", "Code Execution Models", ("agentbay._common.models.code",)),
    DocMapping("common/browser-models.md", "Browser Models", ("agentbay._common.models.browser",)),
    DocMapping("common/response-models.md", "Response Models", ("agentbay._common.models.response",)),
    DocMapping("common/browser-operator-models.md", "Browser Operator Models", ("agentbay._common.models.browser_operator",)),
)


def ensure_clean_docs_root() -> None:
    if DOCS_ROOT.exists():
        shutil.rmtree(DOCS_ROOT)
    DOCS_ROOT.mkdir(parents=True, exist_ok=True)


def should_exclude_method(method: docspec.Function, exclude_methods: list = None, global_rules: dict = None) -> bool:
    """
    Determine if a method should be excluded from documentation based on smart rules.

    Args:
        method: The method to check
        exclude_methods: Explicit list of method names to exclude
        global_rules: Global auto-filtering rules from metadata

    Returns:
        bool: True if the method should be excluded
    """
    if exclude_methods is None:
        exclude_methods = []
    if global_rules is None:
        global_rules = {}

    method_name = method.name

    # Rule 1: Explicit exclusion list (module-specific)
    if method_name in exclude_methods:
        return True

    # Rule 2: Simple getter methods from global config
    simple_getters = global_rules.get('exclude_simple_getters', [])
    if method_name in simple_getters:
        return True

    # Rule 3: VPC helper methods from global config
    vpc_helpers = global_rules.get('exclude_vpc_helpers', [])
    if method_name in vpc_helpers:
        return True

    # Rule 4: Validation methods
    if global_rules.get('exclude_validation_methods', False):
        if method_name.startswith('_validate_') or method_name.endswith('_validate'):
            return True

    # Rule 5: Internal helper methods (find/search with "internal" in docstring)
    if global_rules.get('exclude_internal_helpers', False):
        if method_name.startswith('find_') or method_name.startswith('search_'):
            # Extract docstring content (handle both string and Docstring object)
            docstring = ''
            if method.docstring:
                if isinstance(method.docstring, str):
                    docstring = method.docstring
                elif hasattr(method.docstring, 'content'):
                    docstring = method.docstring.content or ''
            if 'internal' in docstring.lower() or 'helper' in docstring.lower():
                return True

    # Rule 6: Serialization methods (to_map, from_map, to_dict, from_dict)
    serialization_methods = global_rules.get('exclude_serialization_methods', [])
    if method_name in serialization_methods:
        return True

    # Rule 7: Marshal/Unmarshal methods (MarshalJSON, UnmarshalJSON, etc.)
    marshal_methods = global_rules.get('exclude_marshal_methods', [])
    if method_name in marshal_methods:
        return True

    return False


def is_dataclass_result_type(cls: docspec.Class) -> bool:
    """
    Check if a class is a dataclass result type that should have its fields hidden.

    Args:
        cls: The class to check

    Returns:
        bool: True if the class is a dataclass result type
    """
    # Check if class name ends with "Result"
    if not cls.name.endswith("Result"):
        return False

    # Check if class has @dataclass decorator
    if cls.decorations:
        for decoration in cls.decorations:
            if decoration.name == "dataclass":
                return True

    return False


def prune_members(container, module_name: str, exclude_methods: list = None, global_rules: dict = None) -> None:
    """
    Prune members from the documentation tree using smart filtering rules.

    Args:
        container: The docspec container to prune
        module_name: Name of the module being processed
        exclude_methods: List of method names to exclude from documentation
        global_rules: Global auto-filtering rules from metadata
    """
    members = getattr(container, "members", None)
    if not members:
        return

    if exclude_methods is None:
        exclude_methods = []
    if global_rules is None:
        global_rules = {}

    filtered = []
    for member in members:
        if isinstance(member, docspec.Indirection):
            continue

        # Apply smart filtering for methods
        if isinstance(member, docspec.Function):
            if should_exclude_method(member, exclude_methods, global_rules):
                continue

        # Hide fields of dataclass result types (e.g., UploadResult, DownloadResult)
        # These are internal data structures whose fields don't need detailed documentation
        if isinstance(container, docspec.Class) and is_dataclass_result_type(container):
            if isinstance(member, docspec.Variable):
                # Skip all field variables in dataclass result types
                continue

        prune_members(member, module_name, exclude_methods, global_rules)
        filtered.append(member)

    members[:] = filtered


def render_markdown(module_names: Iterable[str], exclude_methods: list = None, global_rules: dict = None) -> str:
    """
    Render markdown documentation for the given modules.

    Args:
        module_names: List of module names to document
        exclude_methods: List of method names to exclude from documentation
        global_rules: Global auto-filtering rules from metadata

    Returns:
        str: The rendered markdown content
    """
    loader = PythonLoader(search_path=[str(PROJECT_ROOT)], modules=list(module_names))
    pydoc = PydocMarkdown(
        loaders=[loader],
        processors=[
            # Keep __init__ so constructor signatures appear in docs; hide other private members
            FilterProcessor(expression="name == '__init__' or not name.startswith('_')"),
            SmartProcessor(),
            CrossrefProcessor(),
        ],
        renderer=MarkdownRenderer(
            render_module_header=False,
            render_typehint_in_data_header=True,
            data_code_block=True,
            insert_header_anchors=False,
            header_level_by_type={'Module': 1, 'Class': 2, 'Method': 3, 'Function': 3, 'Variable': 4},
        ),
    )

    modules = pydoc.load_modules()
    for module in modules:
        prune_members(module, module.name, exclude_methods, global_rules)

    pydoc.process(modules)
    markdown = pydoc.renderer.render_to_string(modules)
    if markdown is None:
        raise RuntimeError("Markdown renderer returned no content")
    return markdown.strip()


def load_metadata() -> dict[str, Any]:
    """Load metadata from the configuration file."""
    if not METADATA_PATH.exists():
        return {}
    with open(METADATA_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_module_name_from_path(module_path: str) -> str:
    """Extract module name from Python module path (e.g., agentbay.session -> session)."""
    # Special handling for common models
    if module_path == "agentbay._common.models.code":
        return "code-models"
    if module_path.endswith(".beta_network"):
        return "network"
    return module_path.split('.')[-1]


def get_async_note_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate async version note at the top of sync API docs with link to async docs."""
    if module_name == "logger":
        return ""

    async_class_map = {
        "agentbay": ("AsyncAgentBay", "../async/async-agentbay.md"),
        "network": ("AsyncNetwork", "../async/async-network.md"),
        "session": ("AsyncSession", "../async/async-session.md"),
        "command": ("AsyncCommand", "../async/async-command.md"),
        "context": ("AsyncContextService", "../async/async-context.md"),
        "context_manager": ("AsyncContextManager", "../async/async-context-manager.md"),
        "filesystem": ("AsyncFileSystem", "../async/async-filesystem.md"),
        "agent": ("AsyncAgent", "../async/async-agent.md"),
        "oss": ("AsyncOss", "../async/async-oss.md"),
        "browser": ("AsyncBrowser", "../async/async-browser.md"),
        "extension": ("AsyncExtensionsService", "../async/async-extension.md"),
        "code": ("AsyncCode", "../async/async-code.md"),
        "computer": ("AsyncComputer", "../async/async-computer.md"),
        "mobile": ("AsyncMobile", "../async/async-mobile.md"),
        "pty": ("AsyncPty", "../async/async-pty.md"),
    }

    async_info = async_class_map.get(module_name)
    if not async_info:
        return ""

    async_class_name, async_doc_path = async_info
    return f"""> **💡 Async Version**: This documentation covers the synchronous API. For async/await support, see [`{async_class_name}`]({async_doc_path}) which provides the same functionality with async methods.

"""


def get_sync_note_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate sync version note at the top of async API docs with link to sync docs."""
    # Map async module names back to sync
    sync_class_map = {
        "agentbay": ("AgentBay", "../sync/agentbay.md"),
        "network": ("Network", "../sync/network.md"),
        "session": ("Session", "../sync/session.md"),
        "command": ("Command", "../sync/command.md"),
        "context": ("ContextService", "../sync/context.md"),
        "context_manager": ("ContextManager", "../sync/context-manager.md"),
        "filesystem": ("FileSystem", "../sync/filesystem.md"),
        "agent": ("Agent", "../sync/agent.md"),
        "oss": ("Oss", "../sync/oss.md"),
        "browser": ("Browser", "../sync/browser.md"),
        "extension": ("ExtensionsService", "../sync/extension.md"),
        "code": ("Code", "../sync/code.md"),
        "computer": ("Computer", "../sync/computer.md"),
        "mobile": ("Mobile", "../sync/mobile.md"),
        "pty": ("Pty", "../sync/pty.md"),
    }

    sync_info = sync_class_map.get(module_name)
    if not sync_info:
        return ""

    sync_class_name, sync_doc_path = sync_info
    return f"""> **💡 Sync Version**: This documentation covers the asynchronous API. For synchronous operations, see [`{sync_class_name}`]({sync_doc_path}).
>
> ⚡ **Performance Advantage**: Async API enables concurrent operations with 4-6x performance improvements for parallel tasks.

"""


def get_tutorial_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate tutorial section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    tutorial = module_config.get('tutorial')
    if not tutorial:
        return ""

    emoji = module_config.get('emoji', '📖')

    # Calculate correct relative path based on flat structure
    # From: python/docs/api/sync/{file}.md or python/docs/api/async/{file}.md
    # To: project_root/docs/guides/...
    # Need to go up: 1 (sync/async) + 2 (api, docs) + 1 (python) = 4 levels
    depth = 4
    up_levels = '../' * depth

    # Replace the hardcoded path with dynamically calculated one
    tutorial_url = tutorial['url']
    # Extract the part after 'docs/' from the URL
    import re
    docs_match = re.search(r'docs/(.+)$', tutorial_url)
    if docs_match:
        tutorial_url = f"{up_levels}docs/{docs_match.group(1)}"

    return f"""## {emoji} Related Tutorial

- [{tutorial['text']}]({tutorial_url}) - {tutorial['description']}

"""


def get_overview_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate overview section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    overview = module_config.get('overview')
    if not overview:
        return ""

    return f"""## Overview

{overview}

"""


def get_properties_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate properties section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    properties = module_config.get('properties', [])
    if not properties:
        return ""

    lines = ["## Properties\n"]
    lines.append("```python")
    for prop in properties:
        lines.append(f"{prop['name']}  # {prop['description']}")
    lines.append("```\n")

    return "\n".join(lines) + "\n"


def get_requirements_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate requirements section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    requirements = module_config.get('requirements', [])
    if not requirements:
        return ""

    lines = ["## Requirements\n"]
    for req in requirements:
        lines.append(f"- {req}")
    lines.append("\n")

    return "\n".join(lines)


def get_data_types_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate data types section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    data_types = module_config.get('data_types', [])
    if not data_types:
        return ""

    lines = ["## Data Types\n"]
    for data_type in data_types:
        lines.append(f"### {data_type['name']}\n")
        lines.append(f"{data_type['description']}\n")
    lines.append("")

    return "\n".join(lines)


def get_important_notes_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate important notes section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    important_notes = module_config.get('important_notes', [])
    if not important_notes:
        return ""

    lines = ["## Important Notes\n"]
    for note in important_notes:
        lines.append(f"- {note}")
    lines.append("\n")

    return "\n".join(lines)


def get_best_practices_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate best practices section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    best_practices = module_config.get('best_practices', [])
    if not best_practices:
        return ""

    lines = ["## Best Practices\n"]
    for i, practice in enumerate(best_practices, 1):
        lines.append(f"{i}. {practice}")
    lines.append("\n")

    return "\n".join(lines)


def calculate_resource_path(resource: dict[str, Any], module_config: dict[str, Any]) -> str:
    """Calculate relative path for a related resource."""
    target_category = resource.get('category', 'common-features/basics')
    current_category = module_config.get('category', 'common-features/basics')
    module = resource['module']

    # If same category, just use module name
    if target_category == current_category:
        return f"{module}.md"

    # Calculate relative path from current category to target category
    current_parts = current_category.split('/')
    target_parts = target_category.split('/')

    # Go up from current directory
    relative_path = '../' * len(current_parts)

    # Go down to target directory
    relative_path += '/'.join(target_parts) + '/' + module + '.md'

    return relative_path


SYNC_ASYNC_MODULES = {
    'agentbay',
    'session',
    'command',
    'filesystem',
    'context',
    'context-manager',
    'browser',
    'extension',
    'oss',
    'agent',
    'code',
    'computer',
    'mobile',
    'session-params',
    'network',
    'pty',
}


def unescape_underscores_in_headings(content: str) -> str:
    """
    Remove backslash escaping for underscores in markdown headings.

    pydoc-markdown escapes underscores (e.g., `beta\\_take\\_screenshot`) which makes headings
    harder to read. We only change heading lines, leaving inline/code content unchanged.
    """
    lines = content.splitlines()
    for i, line in enumerate(lines):
        match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if not match:
            continue
        hashes, title = match.group(1), match.group(2)
        # NOTE: Keep backslashes out of f-string expression for Python 3.10 compatibility.
        cleaned_title = title.replace(r"\\_", "_").replace(r"\_", "_")
        lines[i] = f"{hashes} {cleaned_title}"
    return "\n".join(lines)


def get_see_also_section(module_name: str, metadata: dict[str, Any], doc_group: str = "sync") -> str:
    """
    Generate See Also section with links to guides and related APIs.

    Args:
        module_name: The current module being documented.
        metadata: Documentation metadata containing related resources.
        doc_group: Which doc set is being generated: "sync", "async", or "common".
    """
    # Flat structure: api/sync/{file}.md or api/async/{file}.md
    # Go up 4 levels to reach project root: sync/async -> api -> docs -> python -> root
    depth = 4
    up_levels = '../' * depth

    lines = ["## See Also\n"]

    # Add link to sync vs async guide
    lines.append(f"- [Synchronous vs Asynchronous API](../../../docs/guides/async-programming/sync-vs-async.md)")

    # Add related resources (other API references)
    module_config = metadata.get('modules', {}).get(module_name, {})
    resources = module_config.get('related_resources', [])
    if resources:
        lines.append("")
        lines.append("**Related APIs:**")
        for resource in resources:
            resource_module = resource.get("module", "")

            # First check if a custom path is specified
            if "path" in resource:
                resource_path = resource["path"]
            elif doc_group == "async" and resource_module in SYNC_ASYNC_MODULES:
                resource_path = f"./async-{resource_module}.md"
            elif doc_group == "common" and resource_module in SYNC_ASYNC_MODULES:
                # Common docs should link to the canonical sync docs for core APIs
                resource_path = f"../sync/{resource_module}.md"
            elif resource_module in SYNC_ASYNC_MODULES:
                resource_path = f"./{resource_module}.md"
            else:
                # For other modules, use default path
                resource_path = f"./{resource_module}.md"
            lines.append(f"- [{resource['name']}]({resource_path})")

    return "\n".join(lines) + "\n\n"


def get_related_resources_section(module_name: str, metadata: dict[str, Any]) -> str:
    """Generate related resources section markdown."""
    module_config = metadata.get('modules', {}).get(module_name, {})
    resources = module_config.get('related_resources', [])
    if not resources:
        return ""

    lines = ["## Related Resources\n"]
    for resource in resources:
        path = calculate_resource_path(resource, module_config)
        lines.append(f"- [{resource['name']}]({path})")

    return "\n".join(lines) + "\n\n"


def remove_logger_definitions(content: str) -> str:
    """
    Remove logger initialization code blocks from the beginning of documentation.
    These are module-level code that should not appear in API reference.
    """
    import re

    # Pattern to match logger code block at the beginning
    # Matches: ```python\nlogger = get_logger("...")\n```
    pattern = r'^```python\nlogger = get_logger\(["\'].*?["\']\)\n```\n\n'

    content = re.sub(pattern, '', content, flags=re.MULTILINE)
    return content


def remove_sessioninfo_class(content: str) -> str:
    """
    Remove SessionInfo Objects section as it provides little value.
    This is a data class with no methods, only shown in Session.info() return type.
    """
    import re

    # Pattern to match SessionInfo Objects section
    # Matches from "## SessionInfo Objects" to the next "##" heading
    pattern = r'## SessionInfo Objects\n\n```python\nclass SessionInfo\(\)\n```\n\nSessionInfo contains information about a session\.\n\n'

    content = re.sub(pattern, '', content, flags=re.MULTILINE)
    return content


def fix_code_block_indentation(content: str) -> str:
    """
    Fix code block indentation in Example sections.
    pydoc-markdown adds indentation before code fences in examples, which breaks rendering.
    This function removes that extra indentation.

    Handles two patterns:
    1. **Example**:\n\n    ```python (4 spaces)
    2. **Example**:\n\n        ```python (8 spaces)
    """
    import re

    # Pattern 1: 4-space indentation (most common)
    # Matches: "**Example**:\n\n    ```python"
    pattern1 = r'(\*\*Example\*\*:)\n\n(    ```python\n(?:.*\n)*?    ```)'

    # Pattern 2: 8-space indentation (when source has blank line after Example:)
    # Matches: "**Example**:\n\n  \n        ```python" (with an extra line containing 2 spaces)
    pattern2 = r'(\*\*Example\*\*:)\n\n  \n(        ```python\n(?:.*\n)*?        ```)'

    def fix_block_4_spaces(match):
        header = match.group(1)  # "**Example**:"
        code_block = match.group(2)  # The indented code block

        # Remove 4 spaces from each line that has them
        fixed_lines = []
        for line in code_block.split('\n'):
            if line.startswith('    '):  # 4 spaces
                fixed_lines.append(line[4:])  # Remove the 4 spaces
            else:
                fixed_lines.append(line)

        return header + '\n\n' + '\n'.join(fixed_lines)

    def fix_block_8_spaces(match):
        header = match.group(1)  # "**Example**:"
        code_block = match.group(2)  # The indented code block

        # Remove 8 spaces from each line that has them
        fixed_lines = []
        for line in code_block.split('\n'):
            if line.startswith('        '):  # 8 spaces
                fixed_lines.append(line[8:])  # Remove the 8 spaces
            else:
                fixed_lines.append(line)

        return header + '\n\n' + '\n'.join(fixed_lines)

    # Apply both patterns
    content = re.sub(pattern2, fix_block_8_spaces, content, flags=re.MULTILINE)
    content = re.sub(pattern1, fix_block_4_spaces, content, flags=re.MULTILINE)

    return content


def fix_example_with_descriptions(content: str) -> str:
    """
    Fix Example sections that have description lines followed by code blocks.

    Pattern to fix:
    **Example**:

      Description line:
        ```python
        code
        ```

    This should become:
    **Example**:

    Description line:
    ```python
    code
    ```
    """
    import re

    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect Example section start
        if line.strip() == '**Example**:':
            fixed_lines.append(line)
            i += 1

            # Skip empty line after Example:
            if i < len(lines) and not lines[i].strip():
                fixed_lines.append(lines[i])
                i += 1

            # Process all content until next section (marked by ### or end of file)
            while i < len(lines):
                current = lines[i]

                # Stop at next section header
                if current.startswith('###') or current.startswith('##') or current.strip() == '---':
                    break

                # Handle indented description lines (2 spaces)
                if current.startswith('  ') and not current.strip().startswith('```'):
                    # Check if this is an RST code block marker (ends with ::)
                    if current.strip().endswith('::'):
                        # Remove :: and the 2-space indentation from description
                        description = current[2:].rstrip(':').rstrip()
                        if description:
                            fixed_lines.append(description)
                        i += 1

                        # Skip empty lines after ::
                        while i < len(lines) and lines[i].strip() in ('', '  '):
                            i += 1

                        # Add code fence for the following indented code block
                        if i < len(lines) and lines[i].startswith('  '):
                            fixed_lines.append('')
                            fixed_lines.append('```python')

                            # Process all indented code lines (2 spaces)
                            while i < len(lines):
                                code_line = lines[i]

                                # Stop at section headers or unindented content
                                if code_line.startswith('###') or code_line.startswith('##') or code_line.strip() == '---':
                                    break

                                # Empty line - keep it
                                if not code_line.strip():
                                    fixed_lines.append('')
                                    i += 1
                                    continue

                                # Indented line (part of code block)
                                if code_line.startswith('  '):
                                    # Remove 2-space indentation, preserving any additional indentation
                                    fixed_lines.append(code_line[2:])
                                    i += 1
                                else:
                                    # Unindented line - end of code block
                                    break

                            # Close code fence
                            fixed_lines.append('```')
                    else:
                        # Regular description line - remove 2-space indentation
                        fixed_lines.append(current[2:])
                        i += 1
                # Handle indented code blocks (4 spaces before ```)
                elif current.strip().startswith('```'):
                    # Check if it has leading spaces
                    leading_spaces = len(current) - len(current.lstrip())
                    if leading_spaces > 0:
                        # Remove all leading spaces from code fence
                        fixed_lines.append(current.lstrip())
                        i += 1

                        # Process code block content
                        while i < len(lines) and not lines[i].strip().startswith('```'):
                            code_line = lines[i]
                            # Remove the same amount of indentation from code lines
                            if code_line.startswith(' ' * leading_spaces):
                                fixed_lines.append(code_line[leading_spaces:])
                            elif not code_line.strip():  # Empty line
                                fixed_lines.append(code_line)
                            else:
                                fixed_lines.append(code_line)
                            i += 1

                        # Add closing fence (remove indentation)
                        if i < len(lines):
                            closing_fence = lines[i]
                            fixed_lines.append(closing_fence.lstrip())
                            i += 1
                    else:
                        fixed_lines.append(current)
                        i += 1
                else:
                    fixed_lines.append(current)
                    i += 1
        else:
            fixed_lines.append(line)
            i += 1

    return '\n'.join(fixed_lines)


def fix_dict_formatting(content: str) -> str:
    """
    Fix dictionary formatting errors in code blocks.
    pydoc-markdown sometimes incorrectly renders Python dictionary lines as markdown list items.

    This fixes patterns like:
    - `"key"` - "value",

    Back to proper Python dict syntax:
        "key": "value",
    """
    import re

    # Pattern: matches lines like '- `"key"` - "value",' or '- `{"key"` - ...'
    # Captures the key and value parts
    pattern = r'^(\s*)- `([^`]+)` - (.+)$'

    def fix_dict_line(match):
        indent = match.group(1)  # Preserve indentation
        key = match.group(2)     # The key part (e.g., "username")
        value = match.group(3)   # The value part (e.g., "john_doe",)

        # Reconstruct as proper Python dict syntax
        return f'{indent}    {key}: {value}'

    # Apply the fix line by line
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        fixed_line = re.sub(pattern, fix_dict_line, line)
        fixed_lines.append(fixed_line)

    return '\n'.join(fixed_lines)


def fix_restructuredtext_code_blocks(content: str) -> str:
    """
    Fix reStructuredText-style code blocks that weren't converted to markdown.

    pydoc-markdown sometimes fails to convert RST code blocks (marked with :: and indentation)
    to proper markdown code blocks, leaving indented code without fencing.
    This causes Python comments (starting with #) to be interpreted as markdown headers.

    This function wraps such indented code blocks with proper markdown code fences.
    """
    import re

    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect pattern: line ends with :: followed by indented code without code fence
        if line.strip().endswith('::'):
            # This is an RST code block marker
            # Remove the :: suffix and keep the description
            if line.strip() == '::':
                # Standalone :: - skip it
                i += 1
                # Skip empty lines
                while i < len(lines) and not lines[i].strip():
                    i += 1
            else:
                # Description with :: at the end - keep the description without ::
                description = line.rstrip(':').rstrip()
                if description:
                    fixed_lines.append(description)
                i += 1
                # Skip empty lines immediately after
                while i < len(lines) and not lines[i].strip():
                    fixed_lines.append(lines[i])
                    i += 1

            # Check if next line is indented code (starts with spaces) but not a code fence
            if i < len(lines) and lines[i].startswith('  ') and not lines[i].strip().startswith('```'):
                # Found indented code block without fence - need to wrap it
                fixed_lines.append('')
                fixed_lines.append('```python')

                # Collect all indented lines (code block)
                indent_level = len(lines[i]) - len(lines[i].lstrip())
                while i < len(lines):
                    current_line = lines[i]

                    # Empty line - keep it
                    if not current_line.strip():
                        fixed_lines.append('')
                        i += 1
                        continue

                    # Line with same or more indentation - part of code block
                    current_indent = len(current_line) - len(current_line.lstrip())
                    if current_indent >= indent_level:
                        # Remove the base indentation
                        fixed_lines.append(current_line[indent_level:])
                        i += 1
                    else:
                        # Less indentation - end of code block
                        break

                # Close the code fence
                fixed_lines.append('```')
                fixed_lines.append('')

            continue

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def normalize_class_headers(content: str) -> str:
    """
    Normalize class header format to ensure consistent structure.

    This function addresses two issues:
    1. Classes without headers (just code block followed by description)
    2. Classes with "## ClassName Objects" style headers

    Both are normalized to "## ClassName" format for consistency.

    Pattern 1 (no header):
        ```python
        class CommandResult(ApiResponse)
        ```

        Result of command execution operations.

    Pattern 2 (with "Objects" suffix):
        ## Command Objects

        ```python
        class Command(BaseService)
        ```

    Both become:
        ## ClassName

        ```python
        class ClassName(...)
        ```

        Description text.
    """
    import re

    lines = content.split('\n')
    fixed_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Pattern 2: Fix "## ClassName Objects" -> "## ClassName"
        # This must be checked FIRST to avoid creating duplicate headers
        class_objects_match = re.match(r'^##\s+(\w+)\s+Objects\s*$', line)
        if class_objects_match:
            class_name = class_objects_match.group(1)
            fixed_lines.append(f'## {class_name}')
            i += 1
            continue

        # Pattern 1: Detect class definition without header
        # Look for: ```python\nclass ClassName(...)\n```
        if line.strip() == '```python' and i + 1 < len(lines):
            next_line = lines[i + 1]
            class_match = re.match(r'^class\s+(\w+)\(', next_line)

            if class_match:
                class_name = class_match.group(1)

                # Check if there's a header before this code block in the FIXED output
                # Look back through recently added lines (not original lines)
                has_header = False
                for j in range(len(fixed_lines) - 1, max(-1, len(fixed_lines) - 6), -1):
                    if j < 0:
                        break
                    prev_line_content = fixed_lines[j].strip()
                    if not prev_line_content:
                        continue
                    # Check if it's a level-2 header matching this class name
                    if re.match(r'^##\s+' + re.escape(class_name) + r'\s*$', prev_line_content):
                        has_header = True
                        break
                    # If we hit a different ## header, stop looking but don't mark as having header
                    if prev_line_content.startswith('##') and not prev_line_content.startswith('###'):
                        break
                    # Stop if we hit other content
                    break

                # If no header, add one
                if not has_header:
                    fixed_lines.append(f'## {class_name}')
                    fixed_lines.append('')

                # Add the code block
                fixed_lines.append(line)
                i += 1
                continue

        fixed_lines.append(line)
        i += 1

    return '\n'.join(fixed_lines)


def fix_async_references_in_sync_docs(content: str) -> str:
    """
    Fix async references in sync documentation.
    Since sync code is generated from async code, docstrings still reference async classes.
    This function replaces those references with sync equivalents.
    """
    import re

    # Replace AsyncAgentBay -> AgentBay (but not in the async note section)
    # We need to be careful not to replace it in the note at the top
    lines = content.split('\n')
    fixed_lines = []
    in_async_note = False

    for i, line in enumerate(lines):
        # Detect async note section (starts with "> **💡 Async Version**")
        if line.strip().startswith('> **💡 Async Version**'):
            in_async_note = True
            fixed_lines.append(line)
            continue

        # End of async note (empty line after the note)
        if in_async_note and not line.strip():
            in_async_note = False
            fixed_lines.append(line)
            continue

        # Don't modify lines in async note section
        if in_async_note:
            fixed_lines.append(line)
            continue

        # Replace async class references with sync equivalents
        # Use word boundaries to avoid partial matches
        modified_line = line
        modified_line = re.sub(r'AsyncAgentBay', 'AgentBay', modified_line)
        modified_line = re.sub(r'AsyncSession', 'Session', modified_line)
        modified_line = re.sub(r'AsyncCommand', 'Command', modified_line)
        modified_line = re.sub(r'AsyncFileSystem', 'FileSystem', modified_line)
        modified_line = re.sub(r'AsyncContextService', 'ContextService', modified_line)
        modified_line = re.sub(r'AsyncContextManager', 'ContextManager', modified_line)
        modified_line = re.sub(r'AsyncAgent', 'Agent', modified_line)
        modified_line = re.sub(r'AsyncOss', 'Oss', modified_line)
        modified_line = re.sub(r'AsyncBrowser', 'Browser', modified_line)
        modified_line = re.sub(r'AsyncExtensionsService', 'ExtensionsService', modified_line)
        modified_line = re.sub(r'AsyncCode', 'Code', modified_line)
        modified_line = re.sub(r'AsyncComputer', 'Computer', modified_line)
        modified_line = re.sub(r'AsyncMobile', 'Mobile', modified_line)

        # Replace "await " in code examples
        modified_line = re.sub(r'\bawait\s+', '', modified_line)

        fixed_lines.append(modified_line)

    return '\n'.join(fixed_lines)


def ensure_init_signatures_include_self(content: str) -> str:
    """
    Pydoc-markdown sometimes omits `self` in rendered __init__ signatures.
    Add it back when missing to keep constructor docs accurate.
    """
    return re.sub(r"(def __init__\()(?!self)", r"\1self, ", content)


def format_markdown(
    raw_content: str,
    title: str,
    module_name: str,
    metadata: dict[str, Any],
    is_async: bool = False,
    doc_group: str = "sync",
) -> str:
    """Enhanced markdown formatting with metadata injection."""
    content = raw_content.lstrip()

    # Remove unwanted content
    content = remove_logger_definitions(content)
    content = remove_sessioninfo_class(content)

    # Fix code block indentation in Example sections
    content = fix_code_block_indentation(content)

    # Fix Example sections with description lines
    content = fix_example_with_descriptions(content)

    # Fix dictionary formatting errors
    content = fix_dict_formatting(content)

    # Fix reStructuredText-style code blocks
    content = fix_restructuredtext_code_blocks(content)

    # Normalize class headers to consistent format
    content = normalize_class_headers(content)

    # Ensure constructor signatures keep the self parameter
    content = ensure_init_signatures_include_self(content)

    # Standardize Deprecated sections into a consistent markdown block
    content = standardize_deprecated_sections(content)

    # Unescape underscores in headings (e.g., beta_take_screenshot)
    content = unescape_underscores_in_headings(content)

    # Only fix async references for sync docs
    if not is_async:
        content = fix_async_references_in_sync_docs(content)

    # 1. Add title
    # Only replace if the first line is a level-1 header (starts with "# " not "##")
    if content.startswith("# ") and not content.startswith("## "):
        lines = content.splitlines()
        lines[0] = f"# {title} API Reference"
        content = "\n".join(lines)
    else:
        content = f"# {title} API Reference\n\n{content}"

    # 2. Collect all sections to insert after title
    sections_after_title = []

    # Add appropriate note based on whether this is sync or async docs
    if is_async:
        sync_note = get_sync_note_section(module_name, metadata)
        if sync_note:
            sections_after_title.append(sync_note)
    else:
        async_note = get_async_note_section(module_name, metadata)
        if async_note:
            sections_after_title.append(async_note)

    # Tutorial section
    tutorial_section = get_tutorial_section(module_name, metadata)
    if tutorial_section:
        sections_after_title.append(tutorial_section)

    # Overview section
    overview_section = get_overview_section(module_name, metadata)
    if overview_section:
        sections_after_title.append(overview_section)

    # Properties section
    properties_section = get_properties_section(module_name, metadata)
    if properties_section:
        sections_after_title.append(properties_section)

    # Requirements section
    requirements_section = get_requirements_section(module_name, metadata)
    if requirements_section:
        sections_after_title.append(requirements_section)

    # Data types section
    data_types_section = get_data_types_section(module_name, metadata)
    if data_types_section:
        sections_after_title.append(data_types_section)

    # Important notes section
    important_notes_section = get_important_notes_section(module_name, metadata)
    if important_notes_section:
        sections_after_title.append(important_notes_section)

    # Insert all sections after title at once
    if sections_after_title:
        lines = content.split('\n', 1)
        if len(lines) >= 2:
            title_line = lines[0]
            rest_content = lines[1]
            combined_sections = ''.join(sections_after_title)
            content = f"{title_line}\n\n{combined_sections}\n{rest_content}"

    # Add best practices before see also
    best_practices_section = get_best_practices_section(module_name, metadata)
    if best_practices_section:
        content = content.rstrip() + "\n\n" + best_practices_section

    # Add see also section (replaces related resources)
    see_also_section = get_see_also_section(module_name, metadata, doc_group)
    if see_also_section:
        content = content.rstrip() + "\n\n" + see_also_section

    # Add footer
    content = content.rstrip() + "\n\n---\n\n*Documentation generated automatically from source code using pydoc-markdown.*\n"
    return content


def standardize_deprecated_sections(content: str) -> str:
    """
    Convert "Deprecated:" sections rendered by pydoc-markdown into a consistent markdown block.

    We keep this conservative to avoid unintended formatting changes:
    - Match a line that is exactly "Deprecated:" with optional indentation
    - Collect subsequent bullet lines (indented) until a blank line
    - Render as a blockquote:
        > **Deprecated**
        > - ...
    """
    import re

    lines = content.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*Deprecated:\s*$", line):
            bullets: list[str] = []
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if nxt.strip() == "":
                    break
                if re.match(r"^\s*-\s+", nxt):
                    bullets.append(re.sub(r"^\s*", "", nxt))
                    i += 1
                    continue
                # Stop if the next section starts (e.g. "Example:" / "Args:" / "Returns:")
                if re.match(r"^\s*[A-Z][A-Za-z ]+:\s*$", nxt):
                    break
                # Otherwise, treat as a continuation line for the previous bullet
                if bullets:
                    bullets[-1] = bullets[-1] + " " + nxt.strip()
                    i += 1
                    continue
                break

            out.append("> **Deprecated**")
            for b in bullets:
                out.append(f"> {b}")
            out.append("")
            # Do not consume the blank line here; let the main loop handle it.
            continue

        out.append(line)
        i += 1

    return "\n".join(out)


def write_readme() -> None:
    lines = [
        "# AgentBay Python SDK API Reference",
        "",
        "This directory contains auto-generated API reference documentation.",
        "",
        "## Quick Links",
        "",
        "- [📁 Synchronous API (`sync/`)](#synchronous-api)",
        "- [⚡ Asynchronous API (`async/`)](#asynchronous-api)",
        "- [📦 Common Classes (`common/`)](#common-classes)",
        "",
        "## Synchronous vs Asynchronous",
        "",
        "AgentBay provides both synchronous and asynchronous APIs with identical interfaces:",
        "",
        "| Feature | Sync API | Async API |",
        "|-|-|-|",
        "| **Use Case** | Simple scripts, linear workflows | Concurrent operations, high performance |",
        "| **Performance** | Sequential execution | 4-6x faster for parallel tasks |",
        "| **Syntax** | `result = agent.create()` | `result = await agent.create()` |",
        "| **Import** | `from agentbay import AgentBay` | `from agentbay import AsyncAgentBay` |",
        "",
        "See [Synchronous vs Asynchronous Guide](../guides/async-programming/sync-vs-async.md) for detailed comparison.",
        "",
        "---",
        "",
        "## Synchronous API",
        "",
        "All synchronous API classes are in the `sync/` directory:",
        "",
    ]

    # Add sync API list
    for mapping in DOC_MAPPINGS:
        class_name = mapping.modules[0].replace('agentbay._sync.', '')
        lines.append(f"- [{mapping.title}]({mapping.target}) - `agentbay.{class_name}`")

    lines.extend([
        "",
        "## Asynchronous API",
        "",
        "All asynchronous API classes are in the `async/` directory:",
        "",
    ])

    # Add async API list
    for mapping in ASYNC_DOC_MAPPINGS:
        class_name = mapping.modules[0].replace('agentbay._async.', '')
        lines.append(f"- [{mapping.title}]({mapping.target}) - `agentbay.{class_name}`")

    lines.extend([
        "",
        "## Common Classes",
        "",
        "Shared classes used by both sync and async APIs are in the `common/` directory:",
        "",
    ])

    # Add common API list
    for mapping in COMMON_DOC_MAPPINGS:
        lines.append(f"- [{mapping.title}]({mapping.target}) - `{mapping.modules[0]}`")

    lines.extend([
        "",
        "---",
        "",
        "**Note**: This documentation is auto-generated from source code. Run `python scripts/generate_api_docs.py` to regenerate.",
    ])

    README = DOCS_ROOT / "README.md"
    README.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    metadata = load_metadata()
    ensure_clean_docs_root()

    global_rules = metadata.get('global', {}).get('auto_filter_rules', {})

    # Generate sync API docs
    print("Generating sync API documentation...")
    for mapping in DOC_MAPPINGS:
        module_name = get_module_name_from_path(mapping.modules[0])
        module_config = metadata.get('modules', {}).get(module_name, {})
        exclude_methods = module_config.get('exclude_methods', [])

        markdown = render_markdown(mapping.modules, exclude_methods, global_rules)
        formatted = format_markdown(markdown, mapping.title, module_name, metadata, is_async=False, doc_group="sync")
        output_path = DOCS_ROOT / mapping.target
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        print(f"  ✓ {mapping.target}")

    # Generate async API docs
    print("\nGenerating async API documentation...")
    for mapping in ASYNC_DOC_MAPPINGS:
        module_name = get_module_name_from_path(mapping.modules[0])
        module_config = metadata.get('modules', {}).get(module_name, {})
        exclude_methods = module_config.get('exclude_methods', [])

        markdown = render_markdown(mapping.modules, exclude_methods, global_rules)
        formatted = format_markdown(markdown, mapping.title, module_name, metadata, is_async=True, doc_group="async")
        output_path = DOCS_ROOT / mapping.target
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        print(f"  ✓ {mapping.target}")

    # Generate common/shared docs
    print("\nGenerating common API documentation...")
    for mapping in COMMON_DOC_MAPPINGS:
        module_name = get_module_name_from_path(mapping.modules[0])
        module_config = metadata.get('modules', {}).get(module_name, {})
        exclude_methods = module_config.get('exclude_methods', [])

        markdown = render_markdown(mapping.modules, exclude_methods, global_rules)
        # Common docs don't need sync/async notes (is_async=False will skip async section)
        formatted = format_markdown(markdown, mapping.title, module_name, metadata, is_async=False, doc_group="common")
        output_path = DOCS_ROOT / mapping.target
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(formatted, encoding="utf-8")
        print(f"  ✓ {mapping.target}")

    write_readme()
    print("\n✅ API documentation generation complete!")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        print(error, file=sys.stderr)
        sys.exit(1)
