# Browser Capabilities by Image Type

Different image types provide different levels of browser automation capabilities. Understanding these differences is crucial for choosing the right image for your use case.

> **Multi-language support:** Code examples below cover Python, TypeScript, and Golang. See: [Python](../../../python/README.md) | [TypeScript](../../../typescript/README.md) | [Golang](../../../golang/README.md) | [Java](../../../java/README.md)

## Feature Comparison Table

| Feature | Browser Use Image | Computer Use Image (Linux) | Computer Use Image (Windows) |
|---------|-------------------|---------------------------|------------------------------|
| **Image ID** | `browser_latest` | `linux_latest` | `windows_latest` |
| **Browser Initialization** | ✅ Full Support | ✅ Full Support | ❌ Not Available |
| **CDP Endpoint Access** | ✅ Available | ✅ Available | ❌ Not Available |
| **Playwright/Puppeteer Integration** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Options** (viewport, user agent, fingerprint) | ✅ All Options | ✅ All Options | ❌ Not Available |
| **Browser Type Selection** (Chrome/Chromium) | ❌ Chromium Only | ✅ Chrome or Chromium | ❌ Not Available |
| **Browser Proxies** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Context** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Random Fingerprint** | ✅ Supported | ✅ Supported | ❌ Not Available |
| **Browser Fingerprint Local Sync** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Fingerprint Construct** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Fingerprint Persistence** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Command-line Args** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Browser Default Navigate** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **CAPTCHA Solving** | ✅ Supported | ✅ Supported | ❌ Not Supported |
| **Page Use Agent** (AI-powered automation) | ✅ Supported | ✅ Supported | ❌ Not Available |
| **Desktop UI Automation** | ❌ Not Available | ✅ Supported | ✅ Supported |
| **Window Management** | ❌ Not Available | ✅ Supported | ✅ Supported |
| **Best For** | Pure web automation (best performance) | Web + Desktop automation (Linux apps) | Desktop automation only (Windows apps) |

## When to Use Each Image Type

### 1. Browser Use Image (`browser_latest`)

**Use when you only need web browser automation**

- ✅ Provides full browser capabilities including AI-powered Page Use Agent
- ✅ **Best performance and lowest resource cost** for browser automation
- ✅ Optimized specifically for web automation with minimal overhead
- ✅ Best for web scraping, testing, form filling, and web-based workflows
- ❌ Cannot control desktop applications or windows
- ℹ️ Browser type is fixed to Chromium

**Ideal Use Cases:**
- Web scraping and data extraction
- Automated web testing
- Form filling and submission
- Web-based workflow automation
- AI-powered web interactions (Page Use Agent)

### 2. Computer Use Image - Linux (`linux_latest`)

**Use when you need both browser automation AND Linux desktop application control**

- ✅ Provides most browser features except Page Use Agent
- ✅ Can control Linux desktop applications and windows
- ✅ Supports browser type selection between Chrome and Chromium
- ✅ Best for hybrid workflows (web + desktop automation on Linux)
- ℹ️ Slightly higher resource usage than Browser Use Image

**Ideal Use Cases:**
- Hybrid workflows combining web and desktop automation
- Testing Linux desktop applications
- Browser automation with desktop application integration
- Scenarios requiring both web and window management

### 3. Computer Use Image - Windows (`windows_latest`)

**Use when you only need Windows desktop application automation**

- ✅ Full Windows application and window management
- ✅ Complete desktop UI automation capabilities
- ❌ No browser automation capabilities available
- ❌ Cannot initialize or control browsers via SDK

**Ideal Use Cases:**
- Windows desktop application automation
- Window management and UI testing
- Office automation (Word, Excel, PowerPoint)
- Legacy Windows application testing

## Code Examples

### Python

```python
import os

from agentbay import AgentBay
from agentbay import CreateSessionParams

agent_bay = AgentBay(api_key=os.getenv("AGENTBAY_API_KEY"))

# For pure web automation with AI capabilities
params = CreateSessionParams(image_id="browser_latest")
result = agent_bay.create(params)

# For Linux desktop + browser automation (no Page Use Agent)
params = CreateSessionParams(image_id="linux_latest")
result = agent_bay.create(params)

# For Windows desktop automation only (no browser)
params = CreateSessionParams(image_id="windows_latest")
result = agent_bay.create(params)
```

### TypeScript

```typescript
import { AgentBay, CreateSessionParams } from '@wuying-org/agentbay-sdk';

const apiKey = process.env.AGENTBAY_API_KEY;
const agentBay = new AgentBay(apiKey);

// For pure web automation with AI capabilities
const params = new CreateSessionParams({ imageId: 'browser_latest' });
const result = await agentBay.create(params);

// For Linux desktop + browser automation (no Page Use Agent)
const params = new CreateSessionParams({ imageId: 'linux_latest' });
const result = await agentBay.create(params);

// For Windows desktop automation only (no browser)
const params = new CreateSessionParams({ imageId: 'windows_latest' });
const result = await agentBay.create(params);
```

### Golang

```go
import (
	"os"

	"github.com/aliyun/wuying-agentbay-sdk/golang/pkg/agentbay"
)

apiKey := os.Getenv("AGENTBAY_API_KEY")
agentBay := agentbay.NewAgentBay(apiKey)

// For pure web automation with AI capabilities
params := &agentbay.CreateSessionParams{
	ImageId: "browser_latest",
}
result, err := agentBay.Create(params)

// For Linux desktop + browser automation (no Page Use Agent)
params := &agentbay.CreateSessionParams{
	ImageId: "linux_latest",
}
result, err := agentBay.Create(params)

// For Windows desktop automation only (no browser)
params := &agentbay.CreateSessionParams{
	ImageId: "windows_latest",
}
result, err := agentBay.Create(params)
```

## Decision Guide

### Choose Browser Use Image if:
- ✓ You only need web browser automation
- ✓ You want the best performance and lowest cost
- ✓ You need AI-powered Page Use Agent
- ✓ You don't need desktop application control

### Choose Computer Use Image (Linux) if:
- ✓ You need both web AND desktop automation
- ✓ You need to control Linux applications
- ✓ You want to switch between Chrome and Chromium
- ✓ You need window management alongside browser automation

### Choose Computer Use Image (Windows) if:
- ✓ You only need Windows desktop automation
- ✓ You need to control Windows applications
- ✓ You don't need any browser automation
- ✓ You need full Windows UI automation capabilities

## Important Notes

> **Performance Consideration**: Browser Use Image offers the best performance and lowest resource cost for browser automation, and includes Page Use Agent for AI-powered natural language automation. If you only need manual browser control with Playwright/Puppeteer without desktop features, Browser Use Image is the optimal choice. Use Computer Use Image (Linux) only when you need both browser AND desktop automation capabilities.

> **Page Use Agent Availability**: The AI-powered Page Use Agent is only available in Browser Use Image. If you need natural language browser automation, you must use `browser_latest`.

> **Browser Type Selection**: Only Computer Use Image (Linux) supports choosing between Chrome and Chromium. Browser Use Image is fixed to Chromium, and Computer Use Image (Windows) has no browser support.

## Related Documentation

- [Browser Use Guide](../browser-use/README.md) - Complete browser automation guide
- [Computer Use Guide](README.md) - Desktop automation guide
- [Browser Core Features](../browser-use/core-features.md) - Essential browser features
- [Browser Advanced Features](../browser-use/advance-features.md) - Advanced capabilities
- [Page Use Agent](../browser-use/advance-features/browser-operator.md) - AI-powered automation

