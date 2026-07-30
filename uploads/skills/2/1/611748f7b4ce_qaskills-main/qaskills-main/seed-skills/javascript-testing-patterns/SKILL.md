---
name: JavaScript Testing Patterns
description: Modern JavaScript testing strategies with Jest, Mocha, and testing best practices covering unit testing, integration testing, mocking, async patterns, and DOM testing.
version: 1.0.0
author: thetestingacademy
license: MIT
tags: [javascript, jest, mocha, unit-testing, mocking, async-testing, dom-testing]
testingTypes: [unit, integration]
frameworks: [jest]
languages: [javascript, typescript]
domains: [web]
agents: [claude-code, cursor, github-copilot, windsurf, codex, aider, continue, cline, zed, bolt]
---

# JavaScript Testing Patterns Skill

You are an expert JavaScript developer specializing in testing patterns and methodologies. When the user asks you to write, review, or improve JavaScript tests, follow these detailed instructions.

## Core Principles

1. **Test behavior, not implementation** -- Tests should verify what code does, not how it works internally.
2. **Fast feedback loops** -- Unit tests should run in milliseconds.
3. **Arrange-Act-Assert** -- Clear three-phase structure for every test.
4. **Deterministic tests** -- Same input always produces same output.
5. **Isolated tests** -- No shared state or dependencies between tests.

## Project Structure

```
project/
  src/
    services/
      user.service.js
      user.service.test.js
    utils/
      validators.js
      validators.test.js
    components/
      Button.jsx
      Button.test.jsx
  __tests__/
    integration/
      api.test.js
    e2e/
      checkout.test.js
  __mocks__/
    axios.js
    localStorage.js
  jest.config.js
```

## Jest Configuration

```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(spec|test).js'],
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/**/*.test.{js,jsx}',
    '!src/**/index.js',
  ],
  coverageThresholds: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
  },
  transform: {
    '^.+\\.jsx?$': 'babel-jest',
  },
  clearMocks: true,
  restoreMocks: true,
};
```

## Basic Testing Patterns

### 1. Testing Pure Functions

```javascript
// validators.js
export function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

export function calculateTotal(items) {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

export function formatCurrency(amount, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
}
```

```javascript
// validators.test.js
import { isValidEmail, calculateTotal, formatCurrency } from './validators';

describe('Validators', () => {
  describe('isValidEmail', () => {
    it('should return true for valid emails', () => {
      expect(isValidEmail('user@example.com')).toBe(true);
      expect(isValidEmail('first.last@domain.co.uk')).toBe(true);
      expect(isValidEmail('user+tag@example.com')).toBe(true);
    });

    it('should return false for invalid emails', () => {
      expect(isValidEmail('')).toBe(false);
      expect(isValidEmail('not-an-email')).toBe(false);
      expect(isValidEmail('@missing-local.com')).toBe(false);
      expect(isValidEmail('missing@domain')).toBe(false);
    });
  });

  describe('calculateTotal', () => {
    it('should calculate total for single item', () => {
      const items = [{ price: 10, quantity: 2 }];
      expect(calculateTotal(items)).toBe(20);
    });

    it('should calculate total for multiple items', () => {
      const items = [
        { price: 10, quantity: 2 },
        { price: 5, quantity: 3 },
      ];
      expect(calculateTotal(items)).toBe(35);
    });

    it('should return 0 for empty array', () => {
      expect(calculateTotal([])).toBe(0);
    });
  });

  describe('formatCurrency', () => {
    it('should format USD by default', () => {
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });

    it('should format different currencies', () => {
      expect(formatCurrency(1234.56, 'EUR')).toContain('1,234.56');
      expect(formatCurrency(1234.56, 'GBP')).toContain('1,234.56');
    });
  });
});
```

### 2. Testing Classes and Services

```javascript
// user.service.js
export class UserService {
  constructor(apiClient, cache) {
    this.apiClient = apiClient;
    this.cache = cache;
  }

  async getUser(id) {
    const cached = this.cache.get(`user:${id}`);
    if (cached) return JSON.parse(cached);

    const user = await this.apiClient.get(`/users/${id}`);
    this.cache.set(`user:${id}`, JSON.stringify(user));
    return user;
  }

  async createUser(userData) {
    const user = await this.apiClient.post('/users', userData);
    return user;
  }

  async deleteUser(id) {
    const user = await this.getUser(id);
    if (!user) throw new Error('User not found');
    await this.apiClient.delete(`/users/${id}`);
    this.cache.delete(`user:${id}`);
  }
}
```

```javascript
// user.service.test.js
import { UserService } from './user.service';

describe('UserService', () => {
  let userService;
  let mockApiClient;
  let mockCache;

  beforeEach(() => {
    mockApiClient = {
      get: jest.fn(),
      post: jest.fn(),
      delete: jest.fn(),
    };
    mockCache = {
      get: jest.fn(),
      set: jest.fn(),
      delete: jest.fn(),
    };
    userService = new UserService(mockApiClient, mockCache);
  });

  describe('getUser', () => {
    it('should return cached user if available', async () => {
      const cachedUser = { id: '1', name: 'Cached User' };
      mockCache.get.mockReturnValue(JSON.stringify(cachedUser));

      const result = await userService.getUser('1');

      expect(result).toEqual(cachedUser);
      expect(mockCache.get).toHaveBeenCalledWith('user:1');
      expect(mockApiClient.get).not.toHaveBeenCalled();
    });

    it('should fetch from API if not cached', async () => {
      const apiUser = { id: '1', name: 'API User' };
      mockCache.get.mockReturnValue(null);
      mockApiClient.get.mockResolvedValue(apiUser);

      const result = await userService.getUser('1');

      expect(result).toEqual(apiUser);
      expect(mockApiClient.get).toHaveBeenCalledWith('/users/1');
      expect(mockCache.set).toHaveBeenCalledWith('user:1', JSON.stringify(apiUser));
    });
  });

  describe('createUser', () => {
    it('should create a new user', async () => {
      const newUser = { id: '2', name: 'New User' };
      mockApiClient.post.mockResolvedValue(newUser);

      const result = await userService.createUser({ name: 'New User' });

      expect(result).toEqual(newUser);
      expect(mockApiClient.post).toHaveBeenCalledWith('/users', { name: 'New User' });
    });
  });

  describe('deleteUser', () => {
    it('should delete user and clear cache', async () => {
      const user = { id: '1', name: 'User' };
      mockCache.get.mockReturnValue(JSON.stringify(user));

      await userService.deleteUser('1');

      expect(mockApiClient.delete).toHaveBeenCalledWith('/users/1');
      expect(mockCache.delete).toHaveBeenCalledWith('user:1');
    });

    it('should throw error when user not found', async () => {
      mockCache.get.mockReturnValue(null);
      mockApiClient.get.mockResolvedValue(null);

      await expect(userService.deleteUser('nonexistent')).rejects.toThrow('User not found');
    });
  });
});
```

## Async Testing Patterns

### 1. Promises and Async/Await

```javascript
describe('Async operations', () => {
  it('should handle resolved promises', async () => {
    const result = await fetchData();
    expect(result.status).toBe('success');
  });

  it('should handle rejected promises', async () => {
    await expect(fetchData('invalid')).rejects.toThrow('Invalid ID');
  });

  it('should use resolves matcher', async () => {
    await expect(fetchUser('1')).resolves.toEqual({ id: '1', name: 'User' });
  });

  it('should use rejects matcher', async () => {
    await expect(fetchUser('invalid')).rejects.toThrow('Not found');
  });

  it('should test callback-based async code', (done) => {
    fetchDataCallback('1', (err, data) => {
      expect(err).toBeNull();
      expect(data.id).toBe('1');
      done();
    });
  });
});
```

### 2. Testing Timers

```javascript
describe('Timer functions', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('should debounce function calls', () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 300);

    debounced();
    debounced();
    debounced();

    expect(fn).not.toHaveBeenCalled();

    jest.advanceTimersByTime(300);

    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('should throttle function calls', () => {
    const fn = jest.fn();
    const throttled = throttle(fn, 100);

    throttled();
    expect(fn).toHaveBeenCalledTimes(1);

    throttled();
    expect(fn).toHaveBeenCalledTimes(1);

    jest.advanceTimersByTime(100);
    throttled();
    expect(fn).toHaveBeenCalledTimes(2);
  });
});
```

## Mocking Patterns

### 1. Function Mocking

```javascript
describe('Function mocking', () => {
  it('should mock a simple function', () => {
    const mockFn = jest.fn();
    mockFn.mockReturnValue(42);

    expect(mockFn()).toBe(42);
    expect(mockFn).toHaveBeenCalledTimes(1);
  });

  it('should mock with implementation', () => {
    const mockFn = jest.fn((x) => x * 2);

    expect(mockFn(5)).toBe(10);
    expect(mockFn).toHaveBeenCalledWith(5);
  });

  it('should mock resolved values', async () => {
    const mockFn = jest.fn();
    mockFn.mockResolvedValue({ id: 1, name: 'Test' });

    const result = await mockFn();
    expect(result).toEqual({ id: 1, name: 'Test' });
  });

  it('should mock different return values', () => {
    const mockFn = jest.fn();
    mockFn
      .mockReturnValueOnce(1)
      .mockReturnValueOnce(2)
      .mockReturnValue(3);

    expect(mockFn()).toBe(1);
    expect(mockFn()).toBe(2);
    expect(mockFn()).toBe(3);
    expect(mockFn()).toBe(3);
  });
});
```

### 2. Module Mocking

```javascript
// __mocks__/axios.js
module.exports = {
  get: jest.fn(() => Promise.resolve({ data: {} })),
  post: jest.fn(() => Promise.resolve({ data: {} })),
  put: jest.fn(() => Promise.resolve({ data: {} })),
  delete: jest.fn(() => Promise.resolve({ data: {} })),
};

// api.test.js
jest.mock('axios');
import axios from 'axios';
import { fetchUsers } from './api';

describe('API functions', () => {
  it('should fetch users', async () => {
    const mockUsers = [{ id: 1, name: 'User 1' }];
    axios.get.mockResolvedValue({ data: mockUsers });

    const users = await fetchUsers();

    expect(users).toEqual(mockUsers);
    expect(axios.get).toHaveBeenCalledWith('/api/users');
  });
});
```

### 3. Partial Module Mocking

```javascript
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  fetchData: jest.fn(),
}));

import { fetchData, formatData } from './utils';

test('should use real formatData but mocked fetchData', () => {
  fetchData.mockResolvedValue({ raw: 'data' });
  // formatData uses the real implementation
});
```

### 4. Spying

```javascript
describe('Spying', () => {
  it('should spy on console.error', () => {
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    console.error('Test error');

    expect(spy).toHaveBeenCalledWith('Test error');
    spy.mockRestore();
  });

  it('should spy on object methods', () => {
    const obj = {
      method: (x) => x * 2,
    };

    const spy = jest.spyOn(obj, 'method');
    const result = obj.method(5);

    expect(result).toBe(10);
    expect(spy).toHaveBeenCalledWith(5);
  });
});
```

## DOM Testing with React Testing Library

```javascript
// Button.jsx
export function Button({ onClick, disabled, children, variant = 'primary' }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`btn btn-${variant}`}
    >
      {children}
    </button>
  );
}
```

```javascript
// Button.test.jsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('should render with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('should handle click events', () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));

    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should be disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('should apply variant class', () => {
    render(<Button variant="secondary">Click me</Button>);
    expect(screen.getByRole('button')).toHaveClass('btn-secondary');
  });
});
```

## Snapshot Testing

```javascript
describe('Snapshot tests', () => {
  it('should match snapshot', () => {
    const data = {
      id: 1,
      name: 'Test User',
      roles: ['admin', 'user'],
    };

    expect(data).toMatchSnapshot();
  });

  it('should match inline snapshot', () => {
    const formatted = formatUserName({ first: 'John', last: 'Doe' });

    expect(formatted).toMatchInlineSnapshot(`"John Doe"`);
  });

  it('should snapshot React component', () => {
    const { container } = render(<Button>Click me</Button>);
    expect(container).toMatchSnapshot();
  });
});
```

## Test Organization Patterns

### 1. Describe Blocks

```javascript
describe('UserManager', () => {
  describe('creating users', () => {
    it('should create user with valid data', () => {});
    it('should reject duplicate emails', () => {});
  });

  describe('retrieving users', () => {
    it('should get user by id', () => {});
    it('should return null for non-existent user', () => {});
  });

  describe('deleting users', () => {
    it('should delete existing user', () => {});
    it('should throw error for non-existent user', () => {});
  });
});
```

### 2. Setup and Teardown

```javascript
describe('Test suite with setup', () => {
  let db;

  beforeAll(() => {
    // Runs once before all tests
    db = createDatabase();
  });

  afterAll(() => {
    // Runs once after all tests
    db.close();
  });

  beforeEach(() => {
    // Runs before each test
    db.clear();
  });

  afterEach(() => {
    // Runs after each test
    jest.clearAllMocks();
  });

  it('test 1', () => {});
  it('test 2', () => {});
});
```

## Testing Mocha Style

```javascript
const { expect } = require('chai');
const sinon = require('sinon');

describe('Mocha tests', () => {
  it('should test with Chai assertions', () => {
    expect(true).to.be.true;
    expect([1, 2, 3]).to.have.lengthOf(3);
    expect({ name: 'Test' }).to.have.property('name', 'Test');
  });

  it('should use Sinon spies', () => {
    const callback = sinon.spy();
    const obj = { method: callback };

    obj.method('arg1', 'arg2');

    expect(callback.calledOnce).to.be.true;
    expect(callback.calledWith('arg1', 'arg2')).to.be.true;
  });

  it('should use Sinon stubs', () => {
    const stub = sinon.stub().returns(42);

    expect(stub()).to.equal(42);
    expect(stub.called).to.be.true;
  });
});
```

## Best Practices

1. **Test behavior, not implementation** -- Refactoring should not break tests.
2. **Use descriptive test names** -- Tests should read like specifications.
3. **One assertion focus per test** -- Each test verifies one concept.
4. **Keep tests simple** -- Complex tests are hard to maintain.
5. **Use beforeEach for setup** -- Ensure clean state for every test.
6. **Mock at boundaries** -- Mock external dependencies, not internal functions.
7. **Avoid test interdependence** -- Tests should run in any order.
8. **Use data-driven tests** -- Parametrize similar tests.
9. **Test edge cases** -- Empty arrays, null, undefined, zero.
10. **Keep tests fast** -- Slow tests discourage running them frequently.

## Anti-Patterns to Avoid

1. **Testing private methods** -- Test public API only.
2. **Mocking everything** -- Test real code paths when possible.
3. **Shared mutable state** -- Use beforeEach to reset state.
4. **Giant test files** -- Split by feature or module.
5. **No assertions** -- Every test needs at least one expect.
6. **Using .only or .skip in commits** -- Clean up before pushing.
7. **Hardcoded delays** -- Use fake timers instead.
8. **Testing framework code** -- Don't test that Array.push works.
9. **Ignoring test failures** -- Fix or delete failing tests.
10. **Not using coverage** -- Track what's tested and what's not.

## Running Tests

```bash
# Run all tests
npm test

# Run in watch mode
npm test -- --watch

# Run specific file
npm test user.service.test.js

# Run with coverage
npm test -- --coverage

# Run matching pattern
npm test -- --testNamePattern="user"

# Update snapshots
npm test -- --updateSnapshot

# Run in CI mode
CI=true npm test
```

JavaScript testing is about building confidence in your code. Write tests that give you the freedom to refactor and the safety to ship with confidence.
