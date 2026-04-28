# 🌐 Browser API Reference

## Overview

The Browser module provides comprehensive browser automation capabilities including navigation, element interaction,screenshot capture, and content extraction. It enables automated testing and web scraping workflows.


## 📚 Tutorial

[Browser Use Guide](../../../../docs/guides/browser-use/README.md)

Complete guide to browser automation

## 📋 Requirements

- Requires `browser_latest` image for browser automation features

## Browser

Browser provides browser-related operations for the session.

### Constructor

```java
public Browser(Session session)
```

### Methods

### initialize

```java
public boolean initialize(BrowserOption option)
```

Initialize the browser instance with the given options asynchronously.
Returns true if successful, false otherwise.

**Parameters:**
- `option` (BrowserOption): Browser configuration options. If null, default options are used

**Returns:**
- `boolean`: true if initialization was successful, false otherwise

### init

```java
public boolean init(BrowserOption option)
```

Alias for initialize method.

**Parameters:**
- `option` (BrowserOption): Browser initialization options

**Returns:**
- `boolean`: true if successful, false otherwise

### destroy

```java
public void destroy()
```

Destroy the browser instance manually.

### screenshot

```java
public byte[] screenshot(com.microsoft.playwright.Page page, boolean fullPage, Map<String, Object> options) throws BrowserException
```

Takes a screenshot of the specified page with enhanced options and error handling.

**Parameters:**
- `page` (com.microsoft.playwright.Page): The Playwright Page object to take a screenshot of. This is a required parameter.
- `fullPage` (boolean): Whether to capture the full scrollable page
- `options` (Map<String,Object>): Additional screenshot options that will override defaults.
               Common options include:
               - type (ScreenshotType): Image type, either PNG or JPEG (default: PNG)
               - timeout (Double): Maximum time in milliseconds (default: 60000)
               - animations (String): How to handle animations (default: "disabled")
               - caret (String): How to handle the caret (default: "hide")
               - scale (String): Scale setting (default: "css")

**Returns:**
- `byte[]`: Screenshot data as bytes

**Throws:**
- `BrowserException`: if browser is not initialized or page is null
- `IllegalArgumentException`: if page is null

### getEndpointUrl

```java
public String getEndpointUrl() throws BrowserException
```

Returns the endpoint URL if the browser is initialized, otherwise raises an exception.
When initialized, always fetches the latest CDP url from getCdpLink API.

**Returns:**
- `String`: Browser endpoint URL

**Throws:**
- `BrowserException`: if browser is not initialized or endpoint URL cannot be retrieved

### getOption

```java
public BrowserOption getOption()
```

Get the current BrowserOption used to initialize the browser.

**Returns:**
- `BrowserOption`: BrowserOption or null if not set

### isInitialized

```java
public boolean isInitialized()
```

Check if the browser is initialized.

**Returns:**
- `boolean`: true if initialized, false otherwise

### getOperator

```java
public BrowserOperator getOperator()
```

Get the browser operator for browser operations (recommended).

<p>The operator provides AI-powered browser automation capabilities including
navigation, screenshots, actions, observations, and data extraction.</p>

**Returns:**
- `BrowserOperator`: BrowserOperator instance

### getAgent

```java
public BrowserAgent getAgent()
```

Get the browser agent for advanced browser operations.

<p><strong>⚠️ Deprecated</strong>: Use getOperator instead. This method will be removed in a future version.</p>

**Returns:**
- `BrowserAgent`: BrowserAgent instance

### getEndpointRouterPort

```java
public Integer getEndpointRouterPort()
```

Get the endpoint router port.

**Returns:**
- `Integer`: Port number or null if not set

### registerCallback

```java
public boolean registerCallback(BrowserCallback callback)
```

Register a callback function to handle browser-related push notifications from sandbox.

<p>Example usage:</p>
<pre>{@code
BrowserCallback callback = (notifyMsg) -> {
    System.out.println("Type: " + notifyMsg.getType());
    System.out.println("Code: " + notifyMsg.getCode());
    System.out.println("Message: " + notifyMsg.getMessage());
    System.out.println("Action: " + notifyMsg.getAction());
    System.out.println("Extra params: " + notifyMsg.getExtraParams());
};

CreateResult createResult = agentBay.create();
Session session = createResult.getSession();
session.getBrowser().initialize(new BrowserOption());
boolean success = session.getBrowser().registerCallback(callback);
// ... do work ...
session.getBrowser().unregisterCallback();
session.delete();
}</pre>

**Parameters:**
- `callback` (BrowserCallback): Callback function that receives a BrowserNotifyMessage

**Returns:**
- `boolean`: true if the callback was successfully registered

### unregisterCallback

```java
public void unregisterCallback()
```

Unregister the previously registered callback function.

<p>Example usage:</p>
<pre>{@code
session.getBrowser().registerCallback(callback);
// ... do work ...
session.getBrowser().unregisterCallback();
}</pre>

### sendNotifyMessage

```java
public boolean sendNotifyMessage(BrowserNotifyMessage notifyMessage)
```

Send a notify message to sandbox through WebSocket.

<p>Example usage:</p>
<pre>{@code
BrowserNotifyMessage notifyMsg = new BrowserNotifyMessage(
    "call-for-user",
    1,
    199,
    "user handle done",
    "takeoverdone",
    new HashMap<>()
);
boolean success = session.getBrowser().sendNotifyMessage(notifyMsg);
}</pre>

**Parameters:**
- `notifyMessage` (BrowserNotifyMessage): The notification message to send

**Returns:**
- `boolean`: true if the message was successfully sent, false otherwise

### sendTakeoverDone

```java
public boolean sendTakeoverDone(int notifyId)
```

Send a takeoverdone notify message to sandbox.

<p>Example usage:</p>
<pre>{@code
BrowserCallback callback = (notifyMsg) -> {
    if ("takeover".equals(notifyMsg.getAction())) {
        int takeoverNotifyId = notifyMsg.getId();
        // ... do work in other thread...
        session.getBrowser().sendTakeoverDone(takeoverNotifyId);
    }
};

CreateResult createResult = agentBay.create();
Session session = createResult.getSession();
session.getBrowser().initialize(new BrowserOption());
session.getBrowser().registerCallback(callback);
// ... do work ...
session.getBrowser().unregisterCallback();
session.delete();
}</pre>

**Parameters:**
- `notifyId` (int): The notification ID associated with the takeover request message

**Returns:**
- `boolean`: true if the takeoverdone notify message was successfully sent, false otherwise



## BrowserOperator

BrowserOperator handles browser automation and small parts of agentic logic.

<p><strong>⚠️ Note</strong>: Currently, for agent services (including ComputerUseAgent, BrowserUseAgent, and MobileUseAgent), 
we do not provide services for overseas users registered with <strong>alibabacloud.com</strong>.</p>

### Constructor

```java
public BrowserOperator(Session session, Browser browser)
```

### Methods

### navigate

```java
public String navigate(String url) throws BrowserException
```

Navigates a specific page to the given URL.

**Parameters:**
- `url` (String): The URL to navigate to

**Returns:**
- `String`: A string indicating the result of the navigation

**Throws:**
- `BrowserException`: if browser is not initialized

### close

```java
public boolean close() throws BrowserException
```

Closes the remote browser operator session.
This will terminate the browser process managed by the operator.

**Returns:**
- `boolean`: true if successful, false otherwise

**Throws:**
- `BrowserException`: if operation fails

### screenshot

```java
public String screenshot(Page page, boolean fullPage, int quality, Map<String, Double> clip, Integer timeout) throws BrowserException
```

```java
public String screenshot(Page page) throws BrowserException
```

Takes a screenshot of the specified page.

**Parameters:**
- `page` (Page): The Playwright Page object to take a screenshot of. If null, the operator's currently focused page will be used
- `fullPage` (boolean): Whether to capture the full scrollable page
- `quality` (int): The quality of the image (0-100), for JPEG format
- `clip` (Map<String,Double>): An object specifying the clipping region {x, y, width, height}
- `timeout` (Integer): Custom timeout for the operation in seconds

**Returns:**
- `String`: A base64 encoded data URL of the screenshot, or an error message

**Throws:**
- `BrowserException`: if browser is not initialized

### act

```java
public ActResult act(Page page, Object actionInput) throws BrowserException
```

```java
public ActResult act(Object actionInput) throws BrowserException
```

Perform an action on a web page.
Uses synchronous execution.

**Parameters:**
- `page` (Page): The Playwright Page object to act on. If null, the operator's currently focused page will be used automatically
- `actionInput` (Object): The action to perform (either ActOptions or ObserveResult)

**Returns:**
- `ActResult`: The result of the action

**Throws:**
- `BrowserException`: if browser is not initialized

### actAsync

```java
public ActResult actAsync(Object actionInput, Page page) throws BrowserException
```

```java
public ActResult actAsync(Object actionInput) throws BrowserException
```

Perform an action on the page asynchronously - matches Python act_async method
Uses asynchronous execution with task polling for long-running operations

**Parameters:**
- `actionInput` (Object): Either ActOptions or ObserveResult describing the action
- `page` (Page): Playwright page object (null to use currently focused page)

**Returns:**
- `ActResult`: ActResult containing success status and execution details

**Throws:**
- `BrowserException`: if browser is not initialized or action fails

### observe

```java
public ObserveResultTuple observe(Page page, ObserveOptions options) throws BrowserException
```

```java
public ObserveResultTuple observe(ObserveOptions options) throws BrowserException
```

Observe elements or state on a web page.

**Parameters:**
- `page` (Page): The Playwright Page object to observe. If null, the operator's currently focused page will be used
- `options` (ObserveOptions): Options to configure the observation behavior

**Returns:**
- `ObserveResultTuple`: A tuple containing a success boolean and a list of observation results

**Throws:**
- `BrowserException`: if browser is not initialized

### extract

```java
public ExtractResultTuple<T> extract(Page page, ExtractOptions<T> options) throws BrowserException
```

```java
public ExtractResultTuple<T> extract(ExtractOptions<T> options) throws BrowserException
```

Extract information from a web page.
Uses synchronous execution.

**Parameters:**
- `page` (Page): The Playwright Page object to extract from. If null, the operator's currently focused page will be used
- `options` (ExtractOptions<T>): Options to configure the extraction, including schema
- `<T>` (Object): The type of data to extract

**Returns:**
- `ExtractResultTuple<T>`: A tuple containing a success boolean and the extracted data as a Pydantic model instance, or null on failure

**Throws:**
- `BrowserException`: if browser is not initialized

### extractAsync

```java
public ExtractResultTuple<T> extractAsync(ExtractOptions<T> options, Page page) throws BrowserException
```

```java
public ExtractResultTuple<T> extractAsync(ExtractOptions<T> options) throws BrowserException
```

Extract structured data from the page asynchronously - matches Python extract_async method
Uses asynchronous execution with task polling for complex extraction operations

**Parameters:**
- `options` (ExtractOptions<T>): ExtractOptions containing instruction, schema, and extraction parameters
- `page` (Page): Playwright page object (null to use currently focused page)
- `<T>` (Object): The type of data to extract (must match the schema class)

**Returns:**
- `ExtractResultTuple<T>`: ExtractResultTuple containing success status and extracted data of type T

**Throws:**
- `BrowserException`: if browser is not initialized or extraction fails

### observeAsync

```java
public ObserveResultTuple observeAsync(ObserveOptions options, Page page) throws BrowserException
```

```java
public ObserveResultTuple observeAsync(ObserveOptions options) throws BrowserException
```

Observe elements or state on a web page asynchronously - matches Python observe (which uses observe_async internally).
Uses asynchronous execution with task polling.

**Parameters:**
- `options` (ObserveOptions): Options to configure the observation behavior
- `page` (Page): Playwright page object (null to use currently focused page)

**Returns:**
- `ObserveResultTuple`: ObserveResultTuple containing success status and list of observation results

**Throws:**
- `BrowserException`: if browser is not initialized or observation fails

### navigateTo

```java
public ActResult navigateTo(Page page, String url) throws BrowserException
```

Navigate to a URL using act method.

**Parameters:**
- `page` (Page): Playwright page object
- `url` (String): URL to navigate to

**Returns:**
- `ActResult`: ActResult

**Throws:**
- `BrowserException`: if operation fails

### click

```java
public ActResult click(Page page, String selector) throws BrowserException
```

Click on an element using act method.

**Parameters:**
- `page` (Page): Playwright page object
- `selector` (String): Element selector

**Returns:**
- `ActResult`: ActResult

**Throws:**
- `BrowserException`: if operation fails

### type

```java
public ActResult type(Page page, String selector, String text) throws BrowserException
```

Type text into an input field using act method.

**Parameters:**
- `page` (Page): Playwright page object
- `selector` (String): Input field selector
- `text` (String): Text to type

**Returns:**
- `ActResult`: ActResult

**Throws:**
- `BrowserException`: if operation fails

### takeScreenshot

```java
public ActResult takeScreenshot(Page page) throws BrowserException
```

Take a screenshot using act method.

**Parameters:**
- `page` (Page): Playwright page object

**Returns:**
- `ActResult`: ActResult

**Throws:**
- `BrowserException`: if operation fails

## ObserveResultTuple

Tuple class to hold observe operation results.

### Constructor

```java
public ObserveResultTuple(boolean success, List<ObserveResult> results)
```

### Methods

### isSuccess

```java
public boolean isSuccess()
```

### getResults

```java
public List<ObserveResult> getResults()
```

## ExtractResultTuple

Tuple class to hold extract operation results.

### Constructor

```java
public ExtractResultTuple(boolean success, T data)
```

### Methods

### isSuccess

```java
public boolean isSuccess()
```

### getData

```java
public T getData()
```



## 💡 Best Practices

- Wait for page load completion before interacting with elements
- Use appropriate selectors (CSS, XPath) for reliable element identification
- Handle navigation timeouts and errors gracefully
- Take screenshots for debugging and verification
- Clean up browser resources after automation tasks

## 🔗 Related Resources

- [Session API Reference](../../api/common-features/basics/session.md)

