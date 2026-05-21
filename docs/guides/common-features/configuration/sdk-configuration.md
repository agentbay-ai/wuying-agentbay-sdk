# SDK Configuration Guide

This guide explains how to configure the AgentBay SDK for different environments and requirements.

> **Multi-language support:** Configuration concepts (API key, endpoint, region) apply to all SDKs. Code examples use Python. See: [Python](../../../../python/README.md) | [TypeScript](../../../../typescript/README.md) | [Golang](../../../../golang/README.md) | [Java](../../../../java/README.md)

> **Important:** Configure the SDK by **region**. The endpoint is no longer a user input — it is derived from `region_id` via direct pattern substitution (Hangzhou / Singapore / Virginia).

## Configuration Parameters

| Parameter | Environment Variable | Description | Default Value |
|-----------|---------------------|-------------|---------------|
| API Key | `AGENTBAY_API_KEY` | Authentication key for API access | Required |
| Region ID | `AGENTBAY_REGION_ID` | Region for sessions and endpoint derivation (see Supported Regions below) | `cn-hangzhou` |
| Timeout | `AGENTBAY_TIMEOUT_MS` | Request timeout in milliseconds | `60000` |
| Log Format | `AGENTBAY_LOG_FORMAT` | Log output format (`pretty`, `sls`) | `pretty` |

> **Note:** `AGENTBAY_ENDPOINT` is no longer read by the SDK. Setting it has no effect — use `AGENTBAY_REGION_ID` instead.

## Supported Regions

`region_id` drives the endpoint via direct pattern substitution
(`agentbay.{region_id}.aliyuncs.com`). Choose the region closest to your
users for optimal network performance:

| Region ID | Derived Endpoint | Notes |
|-----------|------------------|-------|
| `cn-hangzhou` | `agentbay.cn-hangzhou.aliyuncs.com` | Default |
| `ap-southeast-1` | `agentbay.ap-southeast-1.aliyuncs.com` |  |
| `us-east-1` | `agentbay.us-east-1.aliyuncs.com` |  |

Unknown `region_id` values are not rejected — they are composed into the
pattern and a warning is logged at SDK initialization. This lets newly
onboarded regions work without an SDK upgrade, while still flagging typos
(the request will fail at DNS resolution if the host does not exist).
Validate `region_id` at the caller if you need fail-fast behavior.

## Log Configuration

### Log Formats

The SDK supports two log output formats:

1.  **Pretty (Default)**: Designed for human readability in terminal. Uses multi-line output, emojis, and colors.
    ```text
    ✅ API Response: GetContext, RequestId=E11EF0D5...
       └─ context_id=SdkCtx-04ml...
       └─ name=context-name
    ```

2.  **SLS (Compact)**: Designed for Simple Log Service (SLS) or other log aggregators. Uses single-line output, no emojis, no colors, and key-value pairs.
    ```text
    API Response: GetContext, RequestId=E11EF0D5..., context_id=SdkCtx-04ml..., name=context-name
    ```

To enable SLS format, set the environment variable:
```bash
export AGENTBAY_LOG_FORMAT=sls
```

You can also set this in your `.env` file (recommended for local development).

## Default Configuration

If no configuration is provided, the SDK uses the following default values:

```json
{
    "region_id": "cn-hangzhou",
    "endpoint": "agentbay.cn-hangzhou.aliyuncs.com",
    "timeout_ms": 60000
}
```

`endpoint` is shown for reference — it is derived internally from `region_id` and cannot be set directly.

## Configuration Priority

Configuration values are resolved in the following order (highest to lowest priority):

1. **Hard-coded configuration** (passed directly to SDK)
2. **Environment variables**
3. **`.env` configuration file** (searched upward from current directory)
4. **Default configuration**

## Configuration Methods

### Method 1: Environment Variables

Set configuration using shell commands:

**Linux/macOS:**
```bash
export AGENTBAY_API_KEY=your-api-key-here
export AGENTBAY_REGION_ID=ap-southeast-1
```

**Windows:**
```cmd
set AGENTBAY_API_KEY=your-api-key-here
set AGENTBAY_REGION_ID=ap-southeast-1
```

### Method 2: .env File

The SDK automatically searches for `.env` files using the following strategy:

1. **Current directory** - starts from where your program runs
2. **Parent directories** - searches upward until it finds a `.env` file or reaches the root
3. **First match wins** - stops searching when the first `.env` file is found

**Basic usage:**
```env
# .env file (can be placed in project root or any parent directory)
AGENTBAY_API_KEY=your-api-key-here
AGENTBAY_REGION_ID=ap-southeast-1
AGENTBAY_LOG_FORMAT=sls
```

**File locations examples:**
```
my-project/
├── .env                    # ✅ Found from any subdirectory
└── src/
    └── app/
        └── main.py         # Searches upward: app/ → src/ → my-project/ ✅
```

**Custom .env file path (Sync):**

```python
from agentbay import AgentBay
client = AgentBay(env_file="/path/to/custom.env")
```

**Custom .env file path (Async):**

```python
import asyncio
from agentbay import AsyncAgentBay

async def main():
    client = AsyncAgentBay(env_file="/path/to/custom.env")
    # Use client...

asyncio.run(main())
```

### Method 3: Hard-coded Configuration (Debug Only)

For debugging purposes, you can pass configuration directly in code.

**Sync API:**

```python
from agentbay import AgentBay, Config

# Hard-coded configuration (not recommended for production)
config = Config(region_id="ap-southeast-1")
agent_bay = AgentBay(api_key="your-api-key-here", cfg=config)
```

**Async API:**

```python
import asyncio
from agentbay import AsyncAgentBay, Config

async def main():
    # Hard-coded configuration (not recommended for production)
    config = Config(region_id="ap-southeast-1")
    agent_bay = AsyncAgentBay(api_key="your-api-key-here", cfg=config)
    # Use agent_bay...

asyncio.run(main())
```

> **Warning:** Hard-coding API keys and configuration is not recommended for production environments due to security risks.

### SDK Initialization

After setting configuration, initialize the SDK:

```python
from agentbay import AgentBay
agent_bay = AgentBay()  # Automatically searches for .env files
```

## Common Scenarios

### Switching Region

Setting `AGENTBAY_REGION_ID` selects both the cloud resource region **and** the SDK endpoint (the SDK derives the endpoint from the region):

```bash
export AGENTBAY_REGION_ID=ap-southeast-1   # Singapore unit
# or
export AGENTBAY_REGION_ID=us-east-1        # Virginia unit
# or
export AGENTBAY_REGION_ID=cn-hangzhou      # Hangzhou unit (default)
```

**Notes:**
- If `region_id` is not set, the SDK defaults to `cn-hangzhou` (Hangzhou unit).
- The `region_id` is automatically passed to session and context creation APIs as `LoginRegionId`.
- An unknown `region_id` logs a warning at SDK initialization and falls back to the pattern; if the resulting hostname does not exist, the request fails at DNS resolution.


### Development vs Production

**Development:** 
- Use `.env` file in project root for local configuration
- SDK automatically finds configuration regardless of execution directory
- For different environments, use custom paths: `AgentBay(env_file=".env.development")`

**Production:** 
- Use environment variables for secure deployment
- Environment variables always take precedence over `.env` files

## Troubleshooting

### Check Configuration

```bash
env | grep AGENTBAY  # Verify environment variables
```

**Debug .env file discovery:**
```bash
# Check if .env file exists in current directory or parent directories
find . -name ".env" -o -name ".git" -type d 2>/dev/null | head -10
```

### Common Error Messages

#### 1. Missing API Key
**Error:** `ValueError: API key is required. Provide it as a parameter or set the AGENTBAY_API_KEY environment variable`

**Solution:** 
- Set the `AGENTBAY_API_KEY` environment variable
- Or pass `api_key` parameter when creating AgentBay instance

#### 2. Invalid API Key
**Error:** `NOT_LOGIN code: 400, You are not logged in or your login token has expired`

**Solution:**
- Verify your API key is correct and not expired
- Check if your API key has proper permissions
- Contact support if the key should be valid

#### 3. API Key and Region Mismatch
**Error:** `NOT_LOGIN code: 400` with unexpected `HostId` in error response

**Example:** Error shows `'HostId': 'agentbay.ap-southeast-1.aliyuncs.com'` but you expected the Hangzhou unit.

**Solution:**
- Check that your API key is authorized in the region selected by `AGENTBAY_REGION_ID`.
- Domestic (China) API keys typically work with `cn-hangzhou`.
- International API keys typically work with `ap-southeast-1` or `us-east-1`.
- API keys are region-specific and cannot be used across different unit regions.

#### 4. Wrong Endpoint/Network Issues
**Error:** `Failed to resolve 'invalid-endpoint.com'` or `NameResolutionError`

**Solution:**
- Verify the gateway endpoint URL is correct
- Ensure your network can reach the gateway endpoint
- Check if you're behind a corporate firewall
- Confirm gateway location and endpoint match (see supported gateway regions table above)

#### 5. .env File Not Found
**Symptom:** SDK uses default configuration despite having a `.env` file

**Solution:**
- Ensure `.env` file is in your project root or a parent directory
- Check file permissions (must be readable)
- Verify file format (no spaces around `=`, proper line endings)
- Use absolute path if needed: `AgentBay(env_file="/full/path/to/.env")`
- Debug with: `find . -name ".env" -type f` to locate your `.env` files

### Quick Diagnosis

```python
from agentbay import AgentBay

try:
    agent_bay = AgentBay()  # Test basic initialization
    result = agent_bay.create()  # Test API connectivity
    print("Configuration is working correctly")
except ValueError as e:
    print(f"Configuration issue: {e}")
except Exception as e:
    print(f"Network/API issue: {e}")
```

## Best Practices

- **Region Selection:** Pick the region closest to your users (`cn-hangzhou`, `ap-southeast-1`, `us-east-1`) for optimal network performance
- **Security:** Use environment variables in production (not hardcoded values)
- **Validation:** Test configuration during application startup — an unsupported `region_id` raises immediately

## 📚 Related Guides

- [Getting Started](../../../quickstart/installation.md) - Installation and initial setup
- [Session Management](../basics/session-management.md) - Session lifecycle and configuration
- [Logging](logging.md) - Log levels, output formats, and data masking

## 🆘 Getting Help

- [GitHub Issues](https://github.com/agentbay-ai/wuying-agentbay-sdk/issues)
- [Documentation Home](../../README.md)
