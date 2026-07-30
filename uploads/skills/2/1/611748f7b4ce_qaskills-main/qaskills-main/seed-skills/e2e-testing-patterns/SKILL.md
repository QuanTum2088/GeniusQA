---
name: E2E Testing Patterns
description: Comprehensive end-to-end testing methodologies and best practices covering architecture, test design, data management, flakiness prevention, and cross-browser strategies.
version: 1.0.0
author: thetestingacademy
license: MIT
tags: [e2e, testing-patterns, automation, best-practices, test-architecture, cross-browser]
testingTypes: [e2e]
frameworks: [playwright, cypress, selenium]
languages: [typescript, javascript]
domains: [web, api]
agents: [claude-code, cursor, github-copilot, windsurf, codex, aider, continue, cline, zed, bolt]
---

# E2E Testing Patterns Skill

You are an expert QA architect specializing in end-to-end testing patterns and methodologies. When the user asks you to design, review, or improve E2E testing strategies, follow these detailed instructions.

## Core Principles

1. **Test user journeys, not implementation** -- E2E tests should mirror real user behavior.
2. **Fast feedback over exhaustive coverage** -- Critical paths first, edge cases later.
3. **Flakiness is a bug** -- Unreliable tests are worse than no tests.
4. **Isolate test data** -- Each test should create and clean up its own data.
5. **Test at the right level** -- Not everything needs an E2E test.

## Testing Pyramid and E2E Tests

```
         /\
        /  \       E2E Tests (10-20%)
       /____\      - Critical user journeys
      /      \     - High-value scenarios
     /        \    - Smoke tests
    /__________\   Integration Tests (20-30%)
   /            \
  /              \ Unit Tests (50-70%)
 /________________\
```

**E2E tests should focus on:**
- Happy path user journeys (login → purchase → checkout)
- Critical business flows (payment processing, data submission)
- Cross-browser compatibility on core features
- Integration between major system components

**E2E tests should NOT test:**
- Edge cases better covered by unit tests
- Every permutation of form validation
- Internal implementation details
- Third-party service internals

## Test Architecture Patterns

### 1. Page Object Model (POM)

**Structure:**
```
pages/
  base.page.ts          # Shared base functionality
  login.page.ts         # Login page actions and selectors
  dashboard.page.ts     # Dashboard page actions
  components/
    header.component.ts # Reusable header component
    modal.component.ts  # Reusable modal component
```

**Implementation:**
```typescript
// base.page.ts
export abstract class BasePage {
  constructor(protected page: Page) {}

  async navigate(path: string): Promise<void> {
    await this.page.goto(path);
  }

  async waitForLoad(): Promise<void> {
    await this.page.waitForLoadState('networkidle');
  }

  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({ path: `screenshots/${name}.png` });
  }
}

// login.page.ts
export class LoginPage extends BasePage {
  private readonly emailInput = this.page.getByLabel('Email');
  private readonly passwordInput = this.page.getByLabel('Password');
  private readonly submitButton = this.page.getByRole('button', { name: 'Sign in' });

  async goto(): Promise<void> {
    await this.navigate('/login');
  }

  async login(email: string, password: string): Promise<void> {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    await this.waitForLoad();
  }

  async expectError(message: string): Promise<void> {
    await expect(this.page.getByRole('alert')).toContainText(message);
  }
}
```

**Pros:**
- Clear separation of concerns
- Easy to maintain selectors in one place
- Reusable across multiple tests

**Cons:**
- Can become bloated if not organized well
- May encourage creating methods for every tiny action

### 2. Screenplay Pattern (Actor-Task Model)

**Structure:**
```typescript
// actors/user.actor.ts
export class User {
  constructor(private page: Page) {}

  async attemptsTo(...tasks: Task[]): Promise<void> {
    for (const task of tasks) {
      await task.perform(this.page);
    }
  }

  async shouldSee(...assertions: Assertion[]): Promise<void> {
    for (const assertion of assertions) {
      await assertion.verify(this.page);
    }
  }
}

// tasks/login.task.ts
export class Login implements Task {
  constructor(
    private email: string,
    private password: string
  ) {}

  async perform(page: Page): Promise<void> {
    await page.getByLabel('Email').fill(this.email);
    await page.getByLabel('Password').fill(this.password);
    await page.getByRole('button', { name: 'Sign in' }).click();
  }
}

// Usage
test('user can login and view dashboard', async ({ page }) => {
  const user = new User(page);

  await user.attemptsTo(
    new NavigateTo('/login'),
    new Login('user@example.com', 'password123')
  );

  await user.shouldSee(
    new PageTitle('Dashboard'),
    new Element('welcome-message').isVisible()
  );
});
```

**Pros:**
- Highly readable, business-focused tests
- Great for complex user journeys
- Easy to compose tasks

**Cons:**
- More upfront setup
- Can be overkill for simple apps

### 3. Journey-Based Testing

Organize tests by complete user journeys rather than by pages:

```typescript
describe('Purchase Journey', () => {
  test('guest user can complete full purchase flow', async ({ page }) => {
    // Journey: Browse → Add to Cart → Checkout → Payment → Confirmation

    // Step 1: Browse products
    await page.goto('/products');
    await page.getByRole('link', { name: 'Laptops' }).click();

    // Step 2: Add to cart
    const product = page.getByTestId('product-123');
    await product.getByRole('button', { name: 'Add to Cart' }).click();
    await expect(page.getByTestId('cart-count')).toHaveText('1');

    // Step 3: Checkout
    await page.getByRole('button', { name: 'Checkout' }).click();
    await fillCheckoutForm(page, guestUserData);

    // Step 4: Payment
    await fillPaymentForm(page, testPaymentData);
    await page.getByRole('button', { name: 'Place Order' }).click();

    // Step 5: Confirmation
    await expect(page.getByRole('heading', { name: 'Order Confirmed' })).toBeVisible();
    const orderNumber = await page.getByTestId('order-number').textContent();
    expect(orderNumber).toMatch(/^ORD-\d{6}$/);
  });
});
```

**Pros:**
- Tests mirror real user behavior
- Easy to understand business value
- Catches integration issues

**Cons:**
- Longer test execution time
- Harder to debug when failures occur mid-journey

## Test Data Management Patterns

### 1. Test Data Factory Pattern

```typescript
// factories/user.factory.ts
export class UserFactory {
  private static counter = 0;

  static createUser(overrides: Partial<User> = {}): User {
    const id = ++this.counter;
    return {
      id: `user-${id}`,
      email: `testuser${id}@example.com`,
      name: `Test User ${id}`,
      role: 'user',
      ...overrides,
    };
  }

  static createAdmin(): User {
    return this.createUser({ role: 'admin' });
  }
}

// Usage in tests
test('admin can delete users', async ({ page }) => {
  const admin = UserFactory.createAdmin();
  await loginAs(page, admin);
  // ... rest of test
});
```

### 2. Database Seeding Strategy

```typescript
// fixtures/db-seed.fixture.ts
export async function seedDatabase(): Promise<SeedData> {
  const users = await db.users.createMany([
    { email: 'user1@example.com', name: 'User 1' },
    { email: 'user2@example.com', name: 'User 2' },
  ]);

  const products = await db.products.createMany([
    { name: 'Product A', price: 29.99 },
    { name: 'Product B', price: 49.99 },
  ]);

  return { users, products };
}

export async function cleanDatabase(): Promise<void> {
  await db.orders.deleteMany();
  await db.products.deleteMany();
  await db.users.deleteMany();
}

// Use in test setup
test.beforeEach(async () => {
  await cleanDatabase();
  await seedDatabase();
});
```

### 3. API-Based Data Setup

```typescript
// helpers/test-data.ts
export async function createUserViaAPI(userData: CreateUserDto): Promise<User> {
  const response = await request.post('/api/users', {
    data: userData,
  });
  return response.json();
}

test('user can update profile', async ({ page }) => {
  // Setup: Create user via API (faster than UI)
  const user = await createUserViaAPI({
    email: 'test@example.com',
    password: 'password123',
  });

  // Test: Update profile via UI
  await page.goto('/profile');
  await page.getByLabel('Name').fill('Updated Name');
  await page.getByRole('button', { name: 'Save' }).click();

  // Assertion
  await expect(page.getByText('Updated Name')).toBeVisible();
});
```

## Handling Test Flakiness

### 1. Explicit Waits Over Implicit Waits

```typescript
// ❌ BAD: Hardcoded wait
await page.waitForTimeout(5000);

// ✅ GOOD: Wait for specific condition
await page.waitForSelector('[data-testid="results"]');
await page.waitForLoadState('networkidle');

// ✅ BETTER: Use auto-waiting assertions
await expect(page.getByTestId('results')).toBeVisible();
```

### 2. Retry-able Assertions

```typescript
// ✅ Automatically retries until condition is met (or timeout)
await expect(page.getByRole('alert')).toHaveText('Success', { timeout: 10000 });

// ✅ Wait for element count to stabilize
await expect(page.getByRole('listitem')).toHaveCount(5);

// ✅ Wait for element to be in the right state
await expect(page.getByRole('button', { name: 'Submit' })).toBeEnabled();
```

### 3. Stabilizing Network Requests

```typescript
// Wait for specific API call to complete
test('should load user data', async ({ page }) => {
  const responsePromise = page.waitForResponse(
    (response) => response.url().includes('/api/users') && response.status() === 200
  );

  await page.goto('/users');

  await responsePromise;

  await expect(page.getByRole('heading')).toContainText('Users');
});
```

### 4. Handling Race Conditions

```typescript
// ❌ BAD: Assumes element exists immediately
await page.click('button');
await page.fill('input', 'text');

// ✅ GOOD: Wait for element before interaction
await page.waitForSelector('button');
await page.click('button');
await page.waitForSelector('input');
await page.fill('input', 'text');

// ✅ BETTER: Use built-in auto-waiting
await page.getByRole('button').click();
await page.getByRole('textbox').fill('text');
```

## Cross-Browser Testing Strategies

### 1. Browser Matrix Configuration

```typescript
// playwright.config.ts
export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'mobile-safari',
      use: { ...devices['iPhone 13'] },
    },
  ],
});
```

### 2. Browser-Specific Test Skipping

```typescript
test('should support advanced CSS features', async ({ page, browserName }) => {
  test.skip(browserName === 'webkit', 'Safari does not support this CSS feature yet');

  await page.goto('/advanced-styles');
  // ... test advanced CSS behavior
});
```

### 3. Visual Regression Across Browsers

```typescript
test('homepage renders consistently across browsers', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveScreenshot('homepage.png', {
    fullPage: true,
    maxDiffPixels: 100, // Allow minor rendering differences
  });
});
```

## Test Organization Patterns

### 1. Feature-Based Organization

```
tests/
  e2e/
    auth/
      login.spec.ts
      signup.spec.ts
      password-reset.spec.ts
    shopping/
      browse-products.spec.ts
      cart-operations.spec.ts
      checkout.spec.ts
    admin/
      user-management.spec.ts
      analytics.spec.ts
```

### 2. Smoke, Regression, and Full Suites

```typescript
// Tag tests by priority
test('user can login @smoke', async ({ page }) => {
  // Critical path
});

test('user can reset password @regression', async ({ page }) => {
  // Less critical, run in nightly builds
});

test('admin can export analytics @full', async ({ page }) => {
  // Run only in full test suite
});

// Run subsets
// npx playwright test --grep @smoke
// npx playwright test --grep @regression
```

### 3. Parallel vs Serial Execution

```typescript
// Run tests in parallel (default)
test.describe.configure({ mode: 'parallel' });

// Run tests serially when they share state
test.describe.configure({ mode: 'serial' });

test.describe('User onboarding flow', () => {
  test.describe.configure({ mode: 'serial' });

  test('step 1: create account', async ({ page }) => {
    // ...
  });

  test('step 2: verify email', async ({ page }) => {
    // ...
  });

  test('step 3: complete profile', async ({ page }) => {
    // ...
  });
});
```

## Authentication and Session Management

### 1. Reusable Authentication State

```typescript
// auth.setup.ts
import { test as setup } from '@playwright/test';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByLabel('Email').fill('admin@example.com');
  await page.getByLabel('Password').fill('admin123');
  await page.getByRole('button', { name: 'Sign in' }).click();

  await page.context().storageState({ path: 'playwright/.auth/user.json' });
});

// playwright.config.ts
export default defineConfig({
  projects: [
    { name: 'setup', testMatch: /.*\.setup\.ts/ },
    {
      name: 'chromium',
      use: {
        storageState: 'playwright/.auth/user.json',
      },
      dependencies: ['setup'],
    },
  ],
});
```

### 2. Role-Based Authentication Fixtures

```typescript
// fixtures/auth.fixture.ts
export const test = base.extend<{
  authenticatedPage: Page;
  adminPage: Page;
}>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/user.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  adminPage: async ({ browser }, use) => {
    const context = await browser.newContext({
      storageState: 'playwright/.auth/admin.json',
    });
    const page = await context.newPage();
    await use(page);
    await context.close();
  },
});

// Usage
test('admin can access admin panel', async ({ adminPage }) => {
  await adminPage.goto('/admin');
  await expect(adminPage.getByRole('heading')).toHaveText('Admin Dashboard');
});
```

## Performance Testing Patterns

### 1. Measure Page Load Metrics

```typescript
test('homepage loads within 3 seconds', async ({ page }) => {
  const startTime = Date.now();

  await page.goto('/');
  await page.waitForLoadState('networkidle');

  const loadTime = Date.now() - startTime;
  expect(loadTime).toBeLessThan(3000);
});
```

### 2. Lighthouse Integration

```typescript
import { playAudit } from 'playwright-lighthouse';

test('homepage meets performance standards', async ({ page }) => {
  await page.goto('/');

  await playAudit({
    page,
    thresholds: {
      performance: 90,
      accessibility: 95,
      'best-practices': 90,
      seo: 90,
    },
  });
});
```

## Best Practices

1. **Keep tests independent** -- Each test should run in isolation.
2. **Use realistic test data** -- Avoid "test" or "foo" in production-like tests.
3. **Prioritize stability over speed** -- Flaky fast tests are useless.
4. **Test critical paths first** -- 80/20 rule: cover 80% of usage with 20% of tests.
5. **Use Page Object Model** -- Centralize selectors and actions.
6. **Avoid sleep/wait timers** -- Use explicit waits for conditions.
7. **Clean up test data** -- Don't pollute the database or state.
8. **Run tests in CI/CD** -- Automate on every commit or PR.
9. **Monitor test flakiness** -- Track and fix unreliable tests immediately.
10. **Use visual regression wisely** -- Critical UI only, not everything.

## Anti-Patterns to Avoid

1. **Testing every edge case in E2E** -- Use unit tests for edge cases.
2. **Relying on hardcoded waits** -- `sleep(5000)` is a code smell.
3. **Sharing state between tests** -- Tests must be isolated.
4. **Testing third-party code** -- Trust external libraries, test integration only.
5. **Overly complex Page Objects** -- Keep them focused and simple.
6. **Testing implementation details** -- Test user-visible behavior.
7. **Ignoring flaky tests** -- Fix or delete, never skip indefinitely.
8. **Too many E2E tests** -- Balance with faster unit/integration tests.
9. **Not using test reporters** -- Visibility into failures is critical.
10. **Committing with .only or .skip** -- Clean up before committing.

## Test Reporting and Debugging

### 1. Rich HTML Reports

```typescript
// playwright.config.ts
export default defineConfig({
  reporter: [
    ['html', { open: 'never', outputFolder: 'test-results/html' }],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
});
```

### 2. Trace Viewer for Debugging

```typescript
// Enable tracing on failure
export default defineConfig({
  use: {
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
});

// View trace:
// npx playwright show-trace trace.zip
```

### 3. Custom Test Annotations

```typescript
test('critical payment flow', async ({ page }) => {
  test.info().annotations.push({ type: 'priority', description: 'critical' });
  test.info().annotations.push({ type: 'ticket', description: 'JIRA-1234' });

  // ... test implementation
});
```

## Continuous Improvement

- **Review test failures weekly** -- Identify patterns and fix root causes.
- **Track test execution time** -- Optimize slow tests or split them.
- **Monitor flakiness rates** -- Set thresholds (e.g., < 1% flaky).
- **Update tests with product changes** -- Keep tests in sync with features.
- **Refactor Page Objects** -- Keep them DRY and maintainable.

E2E testing is an investment in confidence. Done well, it catches critical bugs before production. Done poorly, it wastes time and erodes trust in automation.
