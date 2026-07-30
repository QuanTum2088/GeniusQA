---
name: Website Audit
description: Comprehensive website auditing skill using Lighthouse, PageSpeed Insights, and web performance APIs to audit performance, accessibility, SEO, best practices, and security.
version: 1.0.0
author: thetestingacademy
license: MIT
tags: [audit, lighthouse, performance, accessibility, seo, web-vitals, pagespeed]
testingTypes: [performance, accessibility, seo]
frameworks: [lighthouse, playwright]
languages: [typescript, javascript]
domains: [web]
agents: [claude-code, cursor, github-copilot, windsurf, codex, aider, continue, cline, zed, bolt]
---

# Website Audit Skill

You are an expert web performance and quality engineer specializing in comprehensive website audits. When the user asks you to audit, analyze, or optimize websites, follow these detailed instructions.

## Core Principles

1. **Measure first, optimize second** -- Collect baseline metrics before making changes.
2. **Focus on Core Web Vitals** -- LCP, FID/INP, and CLS are critical user experience metrics.
3. **Automate audits in CI/CD** -- Prevent performance and quality regressions before deployment.
4. **Test on real devices** -- Lab tests are useful, but field data is the truth.
5. **Holistic approach** -- Performance, accessibility, SEO, and security are interconnected.

## Project Structure

```
audits/
  scripts/
    lighthouse-audit.ts
    performance-budget.ts
    accessibility-audit.ts
    seo-audit.ts
    security-audit.ts
  config/
    lighthouse.config.ts
    budgets.json
  reports/
    html/
    json/
    csv/
  utils/
    metrics-collector.ts
    report-generator.ts
    threshold-checker.ts
  tests/
    audit.spec.ts
playwright.config.ts
package.json
```

## Installation

```bash
npm install --save-dev lighthouse lighthouse-ci playwright @playwright/test
npm install --save-dev web-vitals puppeteer chrome-launcher
```

## Lighthouse Audit with Playwright

### Basic Lighthouse Audit

```typescript
import { test } from '@playwright/test';
import { playAudit } from 'playwright-lighthouse';
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';

test.describe('Lighthouse Audits', () => {
  test('should pass Lighthouse audit for homepage', async ({ page }) => {
    await page.goto('https://example.com');

    await playAudit({
      page,
      thresholds: {
        performance: 90,
        accessibility: 100,
        'best-practices': 90,
        seo: 90,
        pwa: 50,
      },
      port: 9222,
    });
  });

  test('should audit with custom Lighthouse config', async () => {
    const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
    const options = {
      logLevel: 'info' as const,
      output: 'json' as const,
      onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
      port: chrome.port,
    };

    const runnerResult = await lighthouse('https://example.com', options);
    await chrome.kill();

    const { categories } = runnerResult.lhr;

    expect(categories.performance.score).toBeGreaterThan(0.9);
    expect(categories.accessibility.score).toBe(1);
    expect(categories['best-practices'].score).toBeGreaterThan(0.9);
    expect(categories.seo.score).toBeGreaterThan(0.9);
  });
});
```

### Lighthouse Configuration

```typescript
// config/lighthouse.config.ts
import { Config } from 'lighthouse';

export const lighthouseConfig: Config = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    formFactor: 'mobile',
    throttling: {
      rttMs: 150,
      throughputKbps: 1638.4,
      cpuSlowdownMultiplier: 4,
    },
    screenEmulation: {
      mobile: true,
      width: 375,
      height: 667,
      deviceScaleFactor: 2,
      disabled: false,
    },
  },
};

export const desktopConfig: Config = {
  extends: 'lighthouse:default',
  settings: {
    onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
    formFactor: 'desktop',
    throttling: {
      rttMs: 40,
      throughputKbps: 10240,
      cpuSlowdownMultiplier: 1,
    },
    screenEmulation: {
      mobile: false,
      width: 1920,
      height: 1080,
      deviceScaleFactor: 1,
      disabled: false,
    },
  },
};
```

## Performance Auditing

### Core Web Vitals

```typescript
import { test, expect } from '@playwright/test';

test.describe('Core Web Vitals', () => {
  test('should measure and validate Core Web Vitals', async ({ page }) => {
    await page.goto('https://example.com');

    // Measure LCP (Largest Contentful Paint)
    const lcp = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          resolve(lastEntry.renderTime || lastEntry.loadTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        setTimeout(() => resolve(0), 10000);
      });
    });

    // Measure CLS (Cumulative Layout Shift)
    const cls = await page.evaluate(() => {
      return new Promise((resolve) => {
        let clsValue = 0;
        new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!(entry as any).hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
        }).observe({ entryTypes: ['layout-shift'] });

        setTimeout(() => resolve(clsValue), 5000);
      });
    });

    // Measure FID (First Input Delay) - requires real interaction
    await page.click('body');
    const fid = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          if (entries.length > 0) {
            resolve((entries[0] as any).processingStart - (entries[0] as any).startTime);
          }
        }).observe({ entryTypes: ['first-input'] });

        setTimeout(() => resolve(0), 5000);
      });
    });

    // Assert Core Web Vitals thresholds
    expect(lcp).toBeLessThan(2500); // Good LCP < 2.5s
    expect(cls).toBeLessThan(0.1);  // Good CLS < 0.1
    expect(fid).toBeLessThan(100);  // Good FID < 100ms

    console.log(`LCP: ${lcp}ms, CLS: ${cls}, FID: ${fid}ms`);
  });

  test('should measure Time to First Byte (TTFB)', async ({ page }) => {
    const ttfb = await page.evaluate(() => {
      const perfData = window.performance.timing;
      return perfData.responseStart - perfData.requestStart;
    });

    expect(ttfb).toBeLessThan(600); // Good TTFB < 600ms
    console.log(`TTFB: ${ttfb}ms`);
  });

  test('should measure First Contentful Paint (FCP)', async ({ page }) => {
    await page.goto('https://example.com');

    const fcp = await page.evaluate(() => {
      const perfEntries = performance.getEntriesByType('paint');
      const fcpEntry = perfEntries.find((entry) => entry.name === 'first-contentful-paint');
      return fcpEntry ? fcpEntry.startTime : 0;
    });

    expect(fcp).toBeLessThan(1800); // Good FCP < 1.8s
    console.log(`FCP: ${fcp}ms`);
  });
});
```

### Performance Budget

```json
// config/budgets.json
{
  "budgets": [
    {
      "resourceSizes": [
        { "resourceType": "script", "budget": 300 },
        { "resourceType": "image", "budget": 500 },
        { "resourceType": "stylesheet", "budget": 100 },
        { "resourceType": "font", "budget": 100 },
        { "resourceType": "total", "budget": 1000 }
      ],
      "resourceCounts": [
        { "resourceType": "script", "budget": 10 },
        { "resourceType": "stylesheet", "budget": 5 },
        { "resourceType": "font", "budget": 3 },
        { "resourceType": "third-party", "budget": 10 }
      ],
      "timings": [
        { "metric": "interactive", "budget": 3000 },
        { "metric": "first-contentful-paint", "budget": 1800 },
        { "metric": "largest-contentful-paint", "budget": 2500 },
        { "metric": "cumulative-layout-shift", "budget": 0.1 }
      ]
    }
  ]
}
```

### Performance Audit Script

```typescript
// scripts/performance-budget.ts
import { test, expect } from '@playwright/test';

test.describe('Performance Budget', () => {
  test('should respect JavaScript bundle size budget', async ({ page }) => {
    await page.goto('https://example.com');

    const jsSize = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const jsResources = resources.filter((r) => r.name.endsWith('.js'));
      return jsResources.reduce((total, r) => total + r.transferSize, 0);
    });

    const jsKB = jsSize / 1024;
    expect(jsKB).toBeLessThan(300); // Budget: 300 KB
    console.log(`Total JS size: ${jsKB.toFixed(2)} KB`);
  });

  test('should respect image size budget', async ({ page }) => {
    await page.goto('https://example.com');

    const imageSize = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const images = resources.filter(
        (r) => r.initiatorType === 'img' || /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(r.name)
      );
      return images.reduce((total, r) => total + r.transferSize, 0);
    });

    const imageKB = imageSize / 1024;
    expect(imageKB).toBeLessThan(500); // Budget: 500 KB
    console.log(`Total image size: ${imageKB.toFixed(2)} KB`);
  });

  test('should not load excessive third-party resources', async ({ page }) => {
    await page.goto('https://example.com');

    const thirdPartyCount = await page.evaluate(() => {
      const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];
      const origin = window.location.origin;
      return resources.filter((r) => !r.name.startsWith(origin)).length;
    });

    expect(thirdPartyCount).toBeLessThan(10);
    console.log(`Third-party requests: ${thirdPartyCount}`);
  });
});
```

## Accessibility Auditing

```typescript
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility Audit', () => {
  test('should have no WCAG 2.1 AA violations', async ({ page }) => {
    await page.goto('https://example.com');

    const accessibilityResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
      .analyze();

    expect(accessibilityResults.violations).toEqual([]);
  });

  test('should have no critical accessibility issues', async ({ page }) => {
    await page.goto('https://example.com');

    const results = await new AxeBuilder({ page }).analyze();
    const criticalIssues = results.violations.filter(
      (v) => v.impact === 'critical' || v.impact === 'serious'
    );

    if (criticalIssues.length > 0) {
      console.log('Critical accessibility issues found:');
      criticalIssues.forEach((issue) => {
        console.log(`- ${issue.id}: ${issue.description}`);
        console.log(`  Impact: ${issue.impact}`);
        console.log(`  Nodes: ${issue.nodes.length}`);
      });
    }

    expect(criticalIssues).toEqual([]);
  });

  test('should have proper document structure', async ({ page }) => {
    await page.goto('https://example.com');

    // Check for proper heading hierarchy
    const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', (elements) =>
      elements.map((el) => ({ tag: el.tagName, text: el.textContent?.trim() }))
    );

    // Should have exactly one h1
    const h1Count = headings.filter((h) => h.tag === 'H1').length;
    expect(h1Count).toBe(1);

    // Check for landmark regions
    const landmarks = await page.$$eval('[role], header, nav, main, footer', (elements) =>
      elements.map((el) => el.getAttribute('role') || el.tagName.toLowerCase())
    );

    expect(landmarks).toContain('main');
    expect(landmarks.some((l) => l === 'navigation' || l === 'nav')).toBe(true);
  });

  test('should have proper ARIA labels', async ({ page }) => {
    await page.goto('https://example.com');

    // Check that all buttons have accessible names
    const unlabeledButtons = await page.$$eval('button', (buttons) =>
      buttons.filter(
        (btn) =>
          !btn.textContent?.trim() &&
          !btn.getAttribute('aria-label') &&
          !btn.getAttribute('aria-labelledby') &&
          !btn.title
      )
    );

    expect(unlabeledButtons.length).toBe(0);
  });
});
```

## SEO Auditing

```typescript
test.describe('SEO Audit', () => {
  test('should have essential meta tags', async ({ page }) => {
    await page.goto('https://example.com');

    // Title tag
    const title = await page.title();
    expect(title).toBeTruthy();
    expect(title.length).toBeGreaterThan(10);
    expect(title.length).toBeLessThan(60);

    // Meta description
    const description = await page.$eval('meta[name="description"]', (el) =>
      el.getAttribute('content')
    );
    expect(description).toBeTruthy();
    expect(description!.length).toBeGreaterThan(50);
    expect(description!.length).toBeLessThan(160);

    // Canonical URL
    const canonical = await page.$eval('link[rel="canonical"]', (el) => el.getAttribute('href'));
    expect(canonical).toBeTruthy();

    // Open Graph tags
    const ogTitle = await page.$eval('meta[property="og:title"]', (el) =>
      el.getAttribute('content')
    );
    expect(ogTitle).toBeTruthy();

    const ogDescription = await page.$eval('meta[property="og:description"]', (el) =>
      el.getAttribute('content')
    );
    expect(ogDescription).toBeTruthy();

    const ogImage = await page.$eval('meta[property="og:image"]', (el) =>
      el.getAttribute('content')
    );
    expect(ogImage).toBeTruthy();

    // Twitter Card
    const twitterCard = await page.$eval('meta[name="twitter:card"]', (el) =>
      el.getAttribute('content')
    );
    expect(twitterCard).toBeTruthy();
  });

  test('should have proper heading structure', async ({ page }) => {
    await page.goto('https://example.com');

    const h1 = await page.$eval('h1', (el) => el.textContent?.trim());
    expect(h1).toBeTruthy();
    expect(h1!.length).toBeGreaterThan(10);

    // Should not skip heading levels
    const headings = await page.$$eval('h1, h2, h3, h4, h5, h6', (elements) =>
      elements.map((el) => parseInt(el.tagName[1]))
    );

    for (let i = 1; i < headings.length; i++) {
      const diff = headings[i] - headings[i - 1];
      expect(diff).toBeLessThanOrEqual(1);
    }
  });

  test('should have robots meta tag', async ({ page }) => {
    await page.goto('https://example.com');

    const robots = await page.$eval(
      'meta[name="robots"]',
      (el) => el.getAttribute('content'),
      { timeout: 1000 }
    ).catch(() => null);

    // If robots tag exists, it should not be "noindex"
    if (robots) {
      expect(robots).not.toContain('noindex');
    }
  });

  test('should have valid structured data', async ({ page }) => {
    await page.goto('https://example.com');

    const structuredData = await page.$$eval('script[type="application/ld+json"]', (scripts) =>
      scripts.map((script) => {
        try {
          return JSON.parse(script.textContent || '');
        } catch {
          return null;
        }
      })
    );

    expect(structuredData.length).toBeGreaterThan(0);
    expect(structuredData.every((data) => data !== null)).toBe(true);
  });

  test('all images should have alt attributes', async ({ page }) => {
    await page.goto('https://example.com');

    const imagesWithoutAlt = await page.$$eval('img:not([alt])', (images) => images.length);

    expect(imagesWithoutAlt).toBe(0);
  });

  test('should have mobile viewport meta tag', async ({ page }) => {
    await page.goto('https://example.com');

    const viewport = await page.$eval('meta[name="viewport"]', (el) =>
      el.getAttribute('content')
    );

    expect(viewport).toBeTruthy();
    expect(viewport).toContain('width=device-width');
  });
});
```

## Security Auditing

```typescript
test.describe('Security Audit', () => {
  test('should have security headers', async ({ page }) => {
    const response = await page.goto('https://example.com');
    const headers = response!.headers();

    // Content Security Policy
    expect(headers['content-security-policy'] || headers['x-content-security-policy']).toBeTruthy();

    // X-Frame-Options
    expect(headers['x-frame-options']).toBeTruthy();

    // X-Content-Type-Options
    expect(headers['x-content-type-options']).toBe('nosniff');

    // Strict-Transport-Security (if HTTPS)
    if (page.url().startsWith('https://')) {
      expect(headers['strict-transport-security']).toBeTruthy();
    }

    // X-XSS-Protection
    expect(headers['x-xss-protection']).toBeTruthy();
  });

  test('should not expose sensitive information', async ({ page }) => {
    const response = await page.goto('https://example.com');
    const headers = response!.headers();

    // Should not expose server details
    if (headers['server']) {
      expect(headers['server']).not.toMatch(/\d+\.\d+/); // No version numbers
    }

    // Should not expose X-Powered-By
    expect(headers['x-powered-by']).toBeFalsy();
  });

  test('should use HTTPS', async ({ page }) => {
    await page.goto('https://example.com');
    expect(page.url()).toMatch(/^https:\/\//);
  });

  test('should not have mixed content warnings', async ({ page }) => {
    const mixedContentWarnings: string[] = [];

    page.on('console', (msg) => {
      if (msg.type() === 'warning' && msg.text().includes('Mixed Content')) {
        mixedContentWarnings.push(msg.text());
      }
    });

    await page.goto('https://example.com');
    await page.waitForLoadState('networkidle');

    expect(mixedContentWarnings).toHaveLength(0);
  });

  test('should have secure cookies', async ({ page, context }) => {
    await page.goto('https://example.com');
    const cookies = await context.cookies();

    cookies.forEach((cookie) => {
      if (cookie.name.toLowerCase().includes('session') || cookie.name.toLowerCase().includes('token')) {
        expect(cookie.secure).toBe(true);
        expect(cookie.httpOnly).toBe(true);
        expect(cookie.sameSite).toMatch(/Strict|Lax/);
      }
    });
  });
});
```

## Lighthouse CI Configuration

```json
// .lighthouserc.json
{
  "ci": {
    "collect": {
      "url": [
        "http://localhost:3000/",
        "http://localhost:3000/products",
        "http://localhost:3000/about"
      ],
      "numberOfRuns": 3,
      "settings": {
        "preset": "desktop"
      }
    },
    "assert": {
      "preset": "lighthouse:recommended",
      "assertions": {
        "categories:performance": ["error", { "minScore": 0.9 }],
        "categories:accessibility": ["error", { "minScore": 1 }],
        "categories:best-practices": ["error", { "minScore": 0.9 }],
        "categories:seo": ["error", { "minScore": 0.9 }],
        "first-contentful-paint": ["error", { "maxNumericValue": 2000 }],
        "largest-contentful-paint": ["error", { "maxNumericValue": 2500 }],
        "cumulative-layout-shift": ["error", { "maxNumericValue": 0.1 }],
        "total-blocking-time": ["error", { "maxNumericValue": 300 }],
        "speed-index": ["error", { "maxNumericValue": 3400 }]
      }
    },
    "upload": {
      "target": "temporary-public-storage"
    }
  }
}
```

## Comprehensive Audit Report

```typescript
// utils/report-generator.ts
import { test } from '@playwright/test';
import lighthouse from 'lighthouse';
import * as chromeLauncher from 'chrome-launcher';
import fs from 'fs';
import path from 'path';

export async function generateComprehensiveReport(url: string) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });

  const options = {
    logLevel: 'info' as const,
    output: ['html', 'json'] as const,
    port: chrome.port,
  };

  const runnerResult = await lighthouse(url, options);

  // Extract key metrics
  const { lhr, report } = runnerResult;
  const categories = lhr.categories;
  const audits = lhr.audits;

  const reportData = {
    url,
    timestamp: new Date().toISOString(),
    scores: {
      performance: categories.performance.score * 100,
      accessibility: categories.accessibility.score * 100,
      bestPractices: categories['best-practices'].score * 100,
      seo: categories.seo.score * 100,
      pwa: categories.pwa?.score ? categories.pwa.score * 100 : null,
    },
    metrics: {
      firstContentfulPaint: audits['first-contentful-paint'].numericValue,
      largestContentfulPaint: audits['largest-contentful-paint'].numericValue,
      totalBlockingTime: audits['total-blocking-time'].numericValue,
      cumulativeLayoutShift: audits['cumulative-layout-shift'].numericValue,
      speedIndex: audits['speed-index'].numericValue,
      timeToInteractive: audits['interactive'].numericValue,
    },
    opportunities: Object.values(audits)
      .filter((audit) => audit.details?.type === 'opportunity')
      .map((audit) => ({
        title: audit.title,
        description: audit.description,
        score: audit.score,
      })),
  };

  // Save reports
  const reportsDir = path.join(process.cwd(), 'audits', 'reports');
  fs.mkdirSync(reportsDir, { recursive: true });

  const timestamp = new Date().toISOString().replace(/:/g, '-');
  fs.writeFileSync(
    path.join(reportsDir, `html/lighthouse-${timestamp}.html`),
    report[0]
  );
  fs.writeFileSync(
    path.join(reportsDir, `json/lighthouse-${timestamp}.json`),
    JSON.stringify(reportData, null, 2)
  );

  await chrome.kill();

  return reportData;
}
```

## Best Practices

1. **Run audits in CI/CD** -- Fail builds that violate performance or accessibility thresholds.
2. **Test on real devices** -- Emulation is useful, but test on actual mobile devices when possible.
3. **Set realistic budgets** -- Performance budgets should reflect real user expectations.
4. **Monitor field data** -- Use Real User Monitoring (RUM) alongside lab audits.
5. **Test multiple pages** -- Audit representative pages from each template type.
6. **Test different network conditions** -- Slow 3G, Fast 3G, 4G, and WiFi.
7. **Audit before and after changes** -- Compare metrics to measure impact.
8. **Document exceptions** -- If you must violate a threshold, document why.
9. **Prioritize user-centric metrics** -- Core Web Vitals directly impact user experience.
10. **Combine automated and manual testing** -- Automated audits catch common issues; manual testing finds edge cases.

## Anti-Patterns to Avoid

1. **Auditing only production** -- Run audits on staging and local builds too.
2. **Ignoring mobile performance** -- Mobile users often have slower connections.
3. **Testing only the homepage** -- Audit critical user journeys and conversion paths.
4. **No performance budgets** -- Without budgets, performance will regress over time.
5. **Disabling throttling** -- Lab tests should simulate real network conditions.
6. **Focusing only on scores** -- Understand the underlying metrics, not just the Lighthouse score.
7. **Not tracking trends** -- One-time audits are less useful than continuous monitoring.
8. **Optimizing for synthetic tests only** -- Real user metrics (RUM) are the ultimate truth.
9. **Skipping accessibility** -- Accessibility is not optional; it is a requirement.
10. **Not acting on results** -- Audits are useless if you do not fix identified issues.

## Running Audits

```bash
# Run Lighthouse CLI
lighthouse https://example.com --output html --output-path ./report.html

# Run Lighthouse CI
npm install -g @lhci/cli
lhci autorun

# Run Playwright tests with Lighthouse
npx playwright test audits/

# Run with specific Lighthouse categories
lighthouse https://example.com --only-categories=performance,accessibility

# Run on mobile
lighthouse https://example.com --preset=mobile

# Run on desktop
lighthouse https://example.com --preset=desktop

# Run with throttling
lighthouse https://example.com --throttling-method=simulate --throttling.cpuSlowdownMultiplier=4

# Generate JSON report
lighthouse https://example.com --output json --output-path ./report.json
```

## CI/CD Integration

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse Audit

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20

      - name: Install dependencies
        run: npm ci

      - name: Build site
        run: npm run build

      - name: Serve site
        run: npm run serve &

      - name: Wait for server
        run: npx wait-on http://localhost:3000

      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun

      - name: Upload Lighthouse results
        uses: actions/upload-artifact@v4
        with:
          name: lighthouse-results
          path: .lighthouseci
```

## Monitoring and Alerts

Set up continuous monitoring:

- **Google PageSpeed Insights API** -- Programmatic access to performance data
- **Lighthouse CI Server** -- Store and trend Lighthouse scores over time
- **Web Vitals Chrome Extension** -- Real-time Core Web Vitals in the browser
- **Datadog RUM** -- Real User Monitoring for field data
- **New Relic Browser** -- Performance monitoring and alerting
- **Sentry Performance** -- Track performance regressions in production

## Key Metrics Summary

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5s - 4.0s | > 4.0s |
| FID (First Input Delay) | < 100ms | 100ms - 300ms | > 300ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 |
| FCP (First Contentful Paint) | < 1.8s | 1.8s - 3.0s | > 3.0s |
| TTFB (Time to First Byte) | < 600ms | 600ms - 1800ms | > 1800ms |
| TTI (Time to Interactive) | < 3.8s | 3.8s - 7.3s | > 7.3s |
| Speed Index | < 3.4s | 3.4s - 5.8s | > 5.8s |
| TBT (Total Blocking Time) | < 200ms | 200ms - 600ms | > 600ms |

## Resources

- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse)
- [Web Vitals](https://web.dev/vitals/)
- [PageSpeed Insights](https://pagespeed.web.dev/)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [WebPageTest](https://www.webpagetest.org/)
