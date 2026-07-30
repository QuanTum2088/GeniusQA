---
name: Agent Browser Automation
description: Fast Rust-based headless browser automation CLI with Node.js fallback for AI agents, featuring navigation, clicking, typing, snapshots, and structured commands optimized for agent workflows.
version: 1.0.0
author: thetestingacademy
license: MIT
tags: [browser-automation, headless-chrome, rust, ai-agents, cli, snapshots, navigation]
testingTypes: [e2e, integration, visual]
frameworks: []
languages: [rust, javascript, typescript]
domains: [web]
agents: [claude-code, cursor, github-copilot, windsurf, codex, aider, continue, cline, zed, bolt]
---

# Agent Browser Automation Skill

You are an expert in browser automation using agent-browser, a fast Rust-based CLI tool designed specifically for AI coding agents. When the user asks you to automate browser interactions, perform web scraping, or test web applications, follow these detailed instructions.

## Core Principles

1. **Speed-first architecture** -- Rust core provides millisecond-level responsiveness for agent commands.
2. **Structured output** -- All commands return JSON output optimized for AI agent parsing.
3. **Fallback resilience** -- Automatically falls back to Node.js implementation when Rust binary is unavailable.
4. **Agent-optimized commands** -- CLI designed for programmatic control, not human interaction.
5. **Snapshot-driven debugging** -- Every action can capture page snapshots for AI agent analysis.

## Installation

```bash
# Install globally via npm
npm install -g agent-browser

# Or use npx without installation
npx agent-browser --version

# Verify installation
agent-browser --help
```

## Project Structure for Agent-Driven Testing

```
tests/
  browser-automation/
    scenarios/
      login-flow.json
      checkout-flow.json
      search-navigation.json
    snapshots/
      login-success.png
      cart-state.png
    scripts/
      run-scenario.sh
      batch-test.sh
  config/
    browser-config.json
    viewport-sizes.json
```

## Core Commands

### Navigation Commands

```bash
# Navigate to URL
agent-browser navigate --url "https://example.com"

# Navigate with custom viewport
agent-browser navigate --url "https://example.com" --viewport "1920x1080"

# Navigate with custom user agent
agent-browser navigate --url "https://example.com" \
  --user-agent "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"

# Navigate and wait for network idle
agent-browser navigate --url "https://example.com" --wait-until "networkidle"
```

**Output:**
```json
{
  "success": true,
  "url": "https://example.com",
  "title": "Example Domain",
  "loadTime": 234,
  "timestamp": "2024-02-12T10:30:00Z"
}
```

### Clicking Elements

```bash
# Click by selector
agent-browser click --selector "button#submit"

# Click by text content
agent-browser click --text "Sign In"

# Click with coordinate offset
agent-browser click --selector ".dropdown" --offset "10,20"

# Wait for element before clicking
agent-browser click --selector "button.load-more" --wait 5000
```

**Output:**
```json
{
  "success": true,
  "element": "button#submit",
  "action": "click",
  "timestamp": "2024-02-12T10:30:01Z"
}
```

### Typing Input

```bash
# Type into input field
agent-browser type --selector "input#email" --text "user@example.com"

# Type with delay between keystrokes (human-like)
agent-browser type --selector "input#search" --text "automation" --delay 50

# Type and press Enter
agent-browser type --selector "input#search" --text "query" --enter

# Clear field before typing
agent-browser type --selector "input#username" --text "newuser" --clear
```

**Output:**
```json
{
  "success": true,
  "element": "input#email",
  "action": "type",
  "length": 17,
  "timestamp": "2024-02-12T10:30:02Z"
}
```

### Taking Snapshots

```bash
# Full page screenshot
agent-browser snapshot --output "screenshot.png"

# Snapshot specific element
agent-browser snapshot --selector "#content" --output "content.png"

# Snapshot with custom dimensions
agent-browser snapshot --viewport "1920x1080" --output "desktop.png"

# Get page HTML
agent-browser snapshot --format "html" --output "page.html"

# Get page as PDF
agent-browser snapshot --format "pdf" --output "document.pdf"
```

**Output:**
```json
{
  "success": true,
  "format": "png",
  "path": "screenshot.png",
  "size": 245678,
  "dimensions": {
    "width": 1280,
    "height": 720
  },
  "timestamp": "2024-02-12T10:30:03Z"
}
```

### Extracting Data

```bash
# Extract text from element
agent-browser extract --selector "h1.title" --attribute "text"

# Extract attribute value
agent-browser extract --selector "a.link" --attribute "href"

# Extract multiple elements
agent-browser extract --selector "li.item" --all

# Extract as JSON
agent-browser extract --selector ".product-card" --json \
  --fields "title:.title,price:.price,image:img@src"
```

**Output:**
```json
{
  "success": true,
  "selector": "h1.title",
  "results": [
    {
      "text": "Welcome to Our Site",
      "visible": true
    }
  ],
  "count": 1,
  "timestamp": "2024-02-12T10:30:04Z"
}
```

### Waiting for Elements

```bash
# Wait for element to appear
agent-browser wait --selector ".loading-complete" --timeout 10000

# Wait for element to disappear
agent-browser wait --selector ".spinner" --hidden --timeout 5000

# Wait for text to appear
agent-browser wait --text "Success" --timeout 3000

# Wait for custom condition
agent-browser wait --script "document.readyState === 'complete'"
```

**Output:**
```json
{
  "success": true,
  "condition": "element_visible",
  "selector": ".loading-complete",
  "waited": 1234,
  "timestamp": "2024-02-12T10:30:05Z"
}
```

## Scenario-Based Automation

### Login Flow Example

```bash
#!/bin/bash
# login-test.sh

# Navigate to login page
agent-browser navigate --url "https://app.example.com/login"

# Fill email
agent-browser type --selector "input#email" --text "user@example.com"

# Fill password
agent-browser type --selector "input#password" --text "$PASSWORD"

# Click submit
agent-browser click --selector "button[type='submit']"

# Wait for dashboard
agent-browser wait --selector ".dashboard" --timeout 5000

# Take success snapshot
agent-browser snapshot --output "login-success.png"

# Extract user info
agent-browser extract --selector ".user-name" --attribute "text"
```

### E2E Shopping Flow

```bash
#!/bin/bash
# checkout-flow.sh

set -e  # Exit on any error

echo "Starting checkout flow test..."

# 1. Navigate to product page
agent-browser navigate --url "https://shop.example.com/products/widget-123"
agent-browser wait --selector ".product-details" --timeout 5000

# 2. Add to cart
agent-browser click --selector "button.add-to-cart"
agent-browser wait --text "Added to cart" --timeout 3000

# 3. Open cart
agent-browser click --selector ".cart-icon"
agent-browser wait --selector ".cart-items" --timeout 2000

# 4. Take cart snapshot
agent-browser snapshot --selector ".cart-summary" --output "cart-state.png"

# 5. Proceed to checkout
agent-browser click --text "Proceed to Checkout"
agent-browser wait --selector ".checkout-form" --timeout 5000

# 6. Fill shipping info
agent-browser type --selector "#shipping-name" --text "John Doe"
agent-browser type --selector "#shipping-address" --text "123 Main St"
agent-browser type --selector "#shipping-city" --text "San Francisco"

# 7. Take final snapshot
agent-browser snapshot --output "checkout-complete.png"

echo "Checkout flow completed successfully"
```

## Integration with AI Agent Workflows

### TypeScript/JavaScript Integration

```typescript
import { execSync } from 'child_process';

interface BrowserResult {
  success: boolean;
  [key: string]: any;
}

class AgentBrowser {
  private baseCommand = 'agent-browser';

  async navigate(url: string, options: { viewport?: string; waitUntil?: string } = {}): Promise<BrowserResult> {
    const args = [`navigate`, `--url`, `"${url}"`];
    if (options.viewport) args.push(`--viewport`, options.viewport);
    if (options.waitUntil) args.push(`--wait-until`, options.waitUntil);

    return this.exec(args);
  }

  async click(selector: string, options: { wait?: number; offset?: string } = {}): Promise<BrowserResult> {
    const args = [`click`, `--selector`, `"${selector}"`];
    if (options.wait) args.push(`--wait`, options.wait.toString());
    if (options.offset) args.push(`--offset`, options.offset);

    return this.exec(args);
  }

  async type(selector: string, text: string, options: { delay?: number; enter?: boolean; clear?: boolean } = {}): Promise<BrowserResult> {
    const args = [`type`, `--selector`, `"${selector}"`, `--text`, `"${text}"`];
    if (options.delay) args.push(`--delay`, options.delay.toString());
    if (options.enter) args.push(`--enter`);
    if (options.clear) args.push(`--clear`);

    return this.exec(args);
  }

  async snapshot(output: string, options: { format?: string; selector?: string; viewport?: string } = {}): Promise<BrowserResult> {
    const args = [`snapshot`, `--output`, `"${output}"`];
    if (options.format) args.push(`--format`, options.format);
    if (options.selector) args.push(`--selector`, `"${options.selector}"`);
    if (options.viewport) args.push(`--viewport`, options.viewport);

    return this.exec(args);
  }

  async extract(selector: string, options: { attribute?: string; all?: boolean; json?: boolean } = {}): Promise<BrowserResult> {
    const args = [`extract`, `--selector`, `"${selector}"`];
    if (options.attribute) args.push(`--attribute`, options.attribute);
    if (options.all) args.push(`--all`);
    if (options.json) args.push(`--json`);

    return this.exec(args);
  }

  private exec(args: string[]): BrowserResult {
    const command = `${this.baseCommand} ${args.join(' ')}`;
    try {
      const output = execSync(command, { encoding: 'utf-8' });
      return JSON.parse(output);
    } catch (error: any) {
      return {
        success: false,
        error: error.message,
        command,
      };
    }
  }
}

// Usage example
async function testLoginFlow() {
  const browser = new AgentBrowser();

  // Navigate
  const navResult = await browser.navigate('https://app.example.com/login', {
    waitUntil: 'networkidle',
  });

  if (!navResult.success) {
    throw new Error(`Navigation failed: ${navResult.error}`);
  }

  // Login
  await browser.type('#email', 'user@example.com');
  await browser.type('#password', process.env.PASSWORD || '', { enter: true });

  // Wait for dashboard
  await browser.wait('.dashboard', { timeout: 5000 });

  // Capture success state
  await browser.snapshot('login-success.png');

  console.log('Login test completed successfully');
}
```

### Python Integration

```python
import json
import subprocess
from typing import Dict, Any, Optional

class AgentBrowser:
    def __init__(self, browser_path: str = "agent-browser"):
        self.browser_path = browser_path

    def navigate(self, url: str, viewport: Optional[str] = None, wait_until: Optional[str] = None) -> Dict[str, Any]:
        args = [self.browser_path, "navigate", "--url", url]
        if viewport:
            args.extend(["--viewport", viewport])
        if wait_until:
            args.extend(["--wait-until", wait_until])
        return self._exec(args)

    def click(self, selector: str, wait: Optional[int] = None, offset: Optional[str] = None) -> Dict[str, Any]:
        args = [self.browser_path, "click", "--selector", selector]
        if wait:
            args.extend(["--wait", str(wait)])
        if offset:
            args.extend(["--offset", offset])
        return self._exec(args)

    def type(self, selector: str, text: str, delay: Optional[int] = None, enter: bool = False, clear: bool = False) -> Dict[str, Any]:
        args = [self.browser_path, "type", "--selector", selector, "--text", text]
        if delay:
            args.extend(["--delay", str(delay)])
        if enter:
            args.append("--enter")
        if clear:
            args.append("--clear")
        return self._exec(args)

    def snapshot(self, output: str, format: Optional[str] = None, selector: Optional[str] = None) -> Dict[str, Any]:
        args = [self.browser_path, "snapshot", "--output", output]
        if format:
            args.extend(["--format", format])
        if selector:
            args.extend(["--selector", selector])
        return self._exec(args)

    def extract(self, selector: str, attribute: Optional[str] = None, all: bool = False) -> Dict[str, Any]:
        args = [self.browser_path, "extract", "--selector", selector]
        if attribute:
            args.extend(["--attribute", attribute])
        if all:
            args.append("--all")
        return self._exec(args)

    def _exec(self, args: list) -> Dict[str, Any]:
        try:
            result = subprocess.run(args, capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": e.stderr,
                "command": " ".join(args)
            }

# Usage example
def test_search_flow():
    browser = AgentBrowser()

    # Navigate to search page
    nav = browser.navigate("https://example.com/search")
    assert nav["success"], f"Navigation failed: {nav.get('error')}"

    # Enter search query
    browser.type("input#search", "automation testing", enter=True)

    # Wait for results
    browser.wait(".search-results", timeout=5000)

    # Extract result titles
    results = browser.extract(".result-item h3", attribute="text", all=True)

    print(f"Found {len(results.get('results', []))} search results")

    # Take snapshot
    browser.snapshot("search-results.png")
```

## Configuration Management

### Browser Config File

```json
{
  "viewport": {
    "width": 1920,
    "height": 1080
  },
  "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
  "timeout": {
    "navigation": 30000,
    "element": 10000,
    "network": 5000
  },
  "screenshot": {
    "format": "png",
    "quality": 80,
    "fullPage": true
  },
  "headless": true,
  "slowMo": 0,
  "devtools": false
}
```

### Load Config in Commands

```bash
# Use config file
agent-browser --config ./browser-config.json navigate --url "https://example.com"

# Override config values
agent-browser --config ./browser-config.json --viewport "1280x720" navigate --url "https://example.com"
```

## Performance Optimization

### Rust vs Node.js Performance

**Rust Implementation Benefits:**
- 10-50x faster command execution
- Lower memory footprint (20-30 MB vs 100+ MB for Node.js)
- Instant startup time (<100ms vs 500-1000ms)
- Compiled binary distribution (no runtime dependencies)

**When Node.js Fallback Activates:**
- Rust binary not available for platform
- Specific browser features requiring Node.js Puppeteer/Playwright
- Debug mode requiring Chrome DevTools Protocol

### Batch Command Optimization

```bash
# Chain commands for efficiency
agent-browser chain \
  "navigate --url https://example.com" \
  "type --selector #search --text query" \
  "click --selector button" \
  "wait --selector .results" \
  "snapshot --output results.png"

# Output includes timing for each step
```

## Best Practices

1. **Use JSON output parsing** -- Always parse JSON responses for reliable AI agent integration.
2. **Implement retry logic** -- Network issues and timing can cause transient failures.
3. **Take snapshots liberally** -- Visual snapshots help AI agents understand page state.
4. **Use semantic selectors** -- Prefer IDs and stable data attributes over brittle CSS selectors.
5. **Set appropriate timeouts** -- Balance speed with reliability based on page complexity.
6. **Chain related commands** -- Use command chaining to reduce overhead.
7. **Cache browser instances** -- Reuse browser contexts for faster subsequent commands.
8. **Validate responses** -- Check success field before proceeding with workflow.
9. **Log all actions** -- Maintain audit trail for debugging and compliance.
10. **Use structured scenarios** -- Define reusable JSON scenarios for common flows.

## Anti-Patterns to Avoid

1. **Hardcoded waits** -- Avoid fixed delays; use element waiting instead.
2. **Ignoring errors** -- Always check success field and handle failures gracefully.
3. **Over-reliance on XPath** -- Prefer CSS selectors for better performance.
4. **Snapshot overload** -- Don't snapshot every step; focus on key states.
5. **Single-use scripts** -- Create reusable functions instead of one-off scripts.
6. **No error recovery** -- Implement retry and fallback mechanisms.
7. **Unvalidated input** -- Sanitize and validate all user input before typing.
8. **Resource leaks** -- Always close browser instances when done.
9. **Ignoring performance** -- Monitor command execution times and optimize.
10. **Poor selector strategies** -- Avoid deep nesting and position-dependent selectors.

## Common Scenarios

### Form Automation

```bash
# Registration form
agent-browser navigate --url "https://app.example.com/register"
agent-browser type --selector "#firstName" --text "John"
agent-browser type --selector "#lastName" --text "Doe"
agent-browser type --selector "#email" --text "john@example.com"
agent-browser type --selector "#password" --text "SecurePass123!"
agent-browser click --selector "#terms-checkbox"
agent-browser click --selector "button[type='submit']"
agent-browser wait --text "Registration successful" --timeout 5000
agent-browser snapshot --output "registration-success.png"
```

### Data Extraction

```bash
# Extract product information
agent-browser navigate --url "https://shop.example.com/products"
agent-browser wait --selector ".product-grid" --timeout 5000
agent-browser extract --selector ".product-card" --json \
  --fields "name:.product-name,price:.product-price,rating:.rating" \
  --all > products.json
```

### Multi-Step Workflow

```bash
# Complex dashboard interaction
agent-browser navigate --url "https://dashboard.example.com"
agent-browser wait --selector ".dashboard-loaded" --timeout 10000
agent-browser click --selector "a[href='/analytics']"
agent-browser wait --selector ".chart-container" --timeout 5000
agent-browser click --selector "button.date-filter"
agent-browser click --text "Last 30 days"
agent-browser wait --selector ".chart-updated" --timeout 3000
agent-browser snapshot --selector ".analytics-panel" --output "analytics.png"
```

## Debugging and Troubleshooting

### Enable Debug Mode

```bash
# Verbose output
agent-browser --debug navigate --url "https://example.com"

# Show browser window (non-headless)
agent-browser --headless false navigate --url "https://example.com"

# Save DevTools logs
agent-browser --console-log ./console.log navigate --url "https://example.com"
```

### Error Handling

```typescript
async function robustBrowserAction(action: () => Promise<BrowserResult>): Promise<BrowserResult> {
  const maxRetries = 3;
  let lastError: any;

  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await action();
      if (result.success) {
        return result;
      }
      lastError = result.error;
    } catch (error) {
      lastError = error;
    }

    // Exponential backoff
    await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
  }

  throw new Error(`Action failed after ${maxRetries} retries: ${lastError}`);
}
```

## Integration with AI Agents

When AI agents use agent-browser, they should:

1. **Parse JSON responses** to understand command results
2. **Analyze snapshots** to verify visual state
3. **Adapt selectors** based on page structure
4. **Handle errors gracefully** with retry logic
5. **Chain commands efficiently** to minimize overhead
6. **Validate outcomes** by checking both JSON and visual snapshots
7. **Maintain context** across multi-step flows
8. **Learn from failures** by analyzing error messages and snapshots

This tool empowers AI agents to interact with web applications at high speed with structured, parseable output optimized for autonomous decision-making.
