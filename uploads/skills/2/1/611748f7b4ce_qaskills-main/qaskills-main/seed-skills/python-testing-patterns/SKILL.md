---
name: Python Testing Patterns
description: Comprehensive Python testing best practices with pytest, covering unit testing, integration testing, mocking, fixtures, property-based testing, and test architecture.
version: 1.0.0
author: thetestingacademy
license: MIT
tags: [python, pytest, unit-testing, integration-testing, mocking, fixtures, property-testing]
testingTypes: [unit, integration]
frameworks: [pytest]
languages: [python]
domains: [api, web]
agents: [claude-code, cursor, github-copilot, windsurf, codex, aider, continue, cline, zed, bolt]
---

# Python Testing Patterns Skill

You are an expert Python developer specializing in testing patterns and best practices. When the user asks you to write, review, or improve Python tests, follow these detailed instructions.

## Core Principles

1. **Test behavior, not implementation** -- Focus on what the code does, not how it does it.
2. **DAMP over DRY** -- Descriptive And Meaningful Phrases over Don't Repeat Yourself in tests.
3. **Arrange-Act-Assert** -- Clear structure in every test.
4. **Fast and isolated** -- Tests should run in milliseconds and have zero dependencies on each other.
5. **Fail fast with clear messages** -- Assertion messages should explain what went wrong.

## Project Structure

```
project/
  src/
    myapp/
      __init__.py
      services/
        user_service.py
        order_service.py
      models/
        user.py
        order.py
      utils/
        validators.py
        formatters.py
  tests/
    __init__.py
    conftest.py
    unit/
      test_user_service.py
      test_validators.py
    integration/
      test_api_endpoints.py
      test_database.py
    fixtures/
      user_fixtures.py
      order_fixtures.py
  pytest.ini
  pyproject.toml
```

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks integration tests
    unit: marks unit tests
    smoke: marks smoke tests
    skip_ci: marks tests to skip in CI
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-report=term-missing",
]

[tool.coverage.run]
source = ["src"]
omit = ["tests/*", "*/__init__.py"]

[tool.coverage.report]
fail_under = 80
show_missing = true
skip_covered = false
```

## Unit Testing Patterns

### 1. Testing Pure Functions

```python
# validators.py
from typing import Optional

def is_valid_email(email: str) -> bool:
    """Validate email address format."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def calculate_discount(price: float, discount_percent: float) -> float:
    """Calculate discounted price."""
    if not 0 <= discount_percent <= 100:
        raise ValueError("Discount must be between 0 and 100")
    return price * (1 - discount_percent / 100)
```

```python
# test_validators.py
import pytest
from myapp.utils.validators import is_valid_email, calculate_discount

class TestEmailValidation:
    """Test suite for email validation."""

    @pytest.mark.parametrize("email", [
        "user@example.com",
        "first.last@domain.co.uk",
        "user+tag@example.com",
        "user123@test-domain.com",
    ])
    def test_valid_emails(self, email):
        """Should accept valid email addresses."""
        assert is_valid_email(email) is True

    @pytest.mark.parametrize("email", [
        "",
        "not-an-email",
        "@missing-local.com",
        "missing-at.com",
        "spaces here@bad.com",
        "missing@domain",
    ])
    def test_invalid_emails(self, email):
        """Should reject invalid email addresses."""
        assert is_valid_email(email) is False


class TestDiscountCalculation:
    """Test suite for discount calculation."""

    def test_no_discount(self):
        """Should return original price when discount is 0."""
        assert calculate_discount(100.0, 0) == 100.0

    def test_full_discount(self):
        """Should return 0 when discount is 100%."""
        assert calculate_discount(100.0, 100) == 0.0

    def test_partial_discount(self):
        """Should calculate correct discounted price."""
        assert calculate_discount(100.0, 20) == 80.0
        assert calculate_discount(50.0, 10) == 45.0

    def test_invalid_discount_raises_error(self):
        """Should raise ValueError for invalid discount percentage."""
        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            calculate_discount(100.0, 101)

        with pytest.raises(ValueError, match="Discount must be between 0 and 100"):
            calculate_discount(100.0, -10)
```

### 2. Testing Classes and Services

```python
# user_service.py
from typing import Optional
from myapp.models.user import User
from myapp.repositories.user_repository import UserRepository
from myapp.services.email_service import EmailService

class UserService:
    """Service for managing users."""

    def __init__(
        self,
        user_repository: UserRepository,
        email_service: EmailService,
    ):
        self.user_repository = user_repository
        self.email_service = email_service

    async def create_user(self, email: str, name: str) -> User:
        """Create a new user and send welcome email."""
        existing = await self.user_repository.find_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        user = await self.user_repository.create(email=email, name=name)
        await self.email_service.send_welcome_email(user.email, user.name)
        return user

    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return await self.user_repository.find_by_id(user_id)

    async def delete_user(self, user_id: str) -> None:
        """Delete user by ID."""
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        await self.user_repository.delete(user_id)
```

```python
# test_user_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from myapp.services.user_service import UserService
from myapp.models.user import User

@pytest.fixture
def mock_user_repository():
    """Create a mock UserRepository."""
    return AsyncMock()

@pytest.fixture
def mock_email_service():
    """Create a mock EmailService."""
    return AsyncMock()

@pytest.fixture
def user_service(mock_user_repository, mock_email_service):
    """Create UserService with mocked dependencies."""
    return UserService(
        user_repository=mock_user_repository,
        email_service=mock_email_service,
    )

class TestUserService:
    """Test suite for UserService."""

    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service,
        mock_user_repository,
        mock_email_service,
    ):
        """Should create user and send welcome email."""
        # Arrange
        mock_user_repository.find_by_email.return_value = None
        new_user = User(id="123", email="new@example.com", name="New User")
        mock_user_repository.create.return_value = new_user

        # Act
        result = await user_service.create_user("new@example.com", "New User")

        # Assert
        assert result == new_user
        mock_user_repository.find_by_email.assert_called_once_with("new@example.com")
        mock_user_repository.create.assert_called_once_with(
            email="new@example.com",
            name="New User",
        )
        mock_email_service.send_welcome_email.assert_called_once_with(
            "new@example.com",
            "New User",
        )

    @pytest.mark.asyncio
    async def test_create_user_duplicate_email_raises_error(
        self,
        user_service,
        mock_user_repository,
        mock_email_service,
    ):
        """Should raise error when user with email already exists."""
        # Arrange
        existing_user = User(id="456", email="existing@example.com", name="Existing")
        mock_user_repository.find_by_email.return_value = existing_user

        # Act & Assert
        with pytest.raises(ValueError, match="User with this email already exists"):
            await user_service.create_user("existing@example.com", "Duplicate")

        mock_user_repository.create.assert_not_called()
        mock_email_service.send_welcome_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_user_found(self, user_service, mock_user_repository):
        """Should return user when found."""
        # Arrange
        user = User(id="123", email="user@example.com", name="User")
        mock_user_repository.find_by_id.return_value = user

        # Act
        result = await user_service.get_user("123")

        # Assert
        assert result == user
        mock_user_repository.find_by_id.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, user_service, mock_user_repository):
        """Should return None when user not found."""
        # Arrange
        mock_user_repository.find_by_id.return_value = None

        # Act
        result = await user_service.get_user("nonexistent")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_user_success(self, user_service, mock_user_repository):
        """Should delete existing user."""
        # Arrange
        user = User(id="123", email="user@example.com", name="User")
        mock_user_repository.find_by_id.return_value = user

        # Act
        await user_service.delete_user("123")

        # Assert
        mock_user_repository.delete.assert_called_once_with("123")

    @pytest.mark.asyncio
    async def test_delete_user_not_found_raises_error(
        self,
        user_service,
        mock_user_repository,
    ):
        """Should raise error when deleting non-existent user."""
        # Arrange
        mock_user_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="User not found"):
            await user_service.delete_user("nonexistent")

        mock_user_repository.delete.assert_not_called()
```

## Advanced Fixture Patterns

### 1. Fixture Factories

```python
# conftest.py
import pytest
from typing import Callable
from myapp.models.user import User

@pytest.fixture
def make_user() -> Callable:
    """Factory fixture for creating test users."""
    created_users = []

    def _make_user(
        email: str = None,
        name: str = "Test User",
        role: str = "user",
    ) -> User:
        if email is None:
            email = f"test{len(created_users)}@example.com"

        user = User(id=str(len(created_users) + 1), email=email, name=name, role=role)
        created_users.append(user)
        return user

    yield _make_user

    # Cleanup happens here if needed
    created_users.clear()

# Usage
def test_user_permissions(make_user):
    """Test different user roles."""
    admin = make_user(role="admin")
    viewer = make_user(role="viewer")

    assert admin.can_delete_users() is True
    assert viewer.can_delete_users() is False
```

### 2. Fixture Dependency Chain

```python
@pytest.fixture(scope="session")
def database_url():
    """Provide test database URL."""
    return "postgresql://test:test@localhost:5432/test_db"

@pytest.fixture(scope="session")
def database_engine(database_url):
    """Create database engine."""
    from sqlalchemy import create_engine
    engine = create_engine(database_url)
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def database_session(database_engine):
    """Create a database session for each test."""
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=database_engine)
    session = Session()

    yield session

    session.rollback()
    session.close()

@pytest.fixture
def user_repository(database_session):
    """Create UserRepository with test database session."""
    from myapp.repositories.user_repository import UserRepository
    return UserRepository(database_session)
```

### 3. Autouse Fixtures

```python
@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables before each test."""
    import os
    original_env = os.environ.copy()

    yield

    os.environ.clear()
    os.environ.update(original_env)

@pytest.fixture(autouse=True)
def mock_datetime(mocker):
    """Mock datetime.now() for all tests."""
    from datetime import datetime
    fixed_now = datetime(2024, 6, 15, 12, 0, 0)
    mocker.patch("myapp.services.datetime")
    mocker.patch("myapp.services.datetime.now", return_value=fixed_now)
```

## Mocking Patterns

### 1. Using unittest.mock

```python
from unittest.mock import Mock, MagicMock, patch, call

def test_api_client_with_mock():
    """Test API client with mocked requests."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": 1, "name": "Test"}

    with patch("requests.get", return_value=mock_response) as mock_get:
        from myapp.api_client import fetch_user
        user = fetch_user("1")

        assert user["name"] == "Test"
        mock_get.assert_called_once_with("/api/users/1")
```

### 2. Using pytest-mock

```python
def test_user_service_with_mocker(mocker):
    """Test using pytest-mock plugin."""
    # Patch class method
    mock_send = mocker.patch("myapp.services.EmailService.send_welcome_email")

    # Patch function
    mocker.patch("myapp.services.generate_id", return_value="test-123")

    # Create service and test
    service = UserService()
    service.send_welcome("user@example.com")

    mock_send.assert_called_once()
```

### 3. Spy Pattern

```python
def test_function_calls_with_spy(mocker):
    """Test that function was called with correct arguments."""
    from myapp.services import process_data

    spy = mocker.spy(process_data, "validate_input")

    process_data({"key": "value"})

    spy.assert_called_once_with({"key": "value"})
```

## Property-Based Testing with Hypothesis

```python
from hypothesis import given, strategies as st
import pytest

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition should be commutative."""
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_list_length_invariant(lst):
    """List length should be preserved after operations."""
    original_length = len(lst)
    reversed_list = list(reversed(lst))
    assert len(reversed_list) == original_length

@given(st.text(min_size=1), st.text(min_size=1))
def test_string_concatenation(s1, s2):
    """String concatenation properties."""
    result = s1 + s2
    assert result.startswith(s1)
    assert result.endswith(s2)
    assert len(result) == len(s1) + len(s2)

# Custom strategies
@given(st.emails())
def test_email_validator_with_real_emails(email):
    """Email validator should accept valid emails."""
    from myapp.utils.validators import is_valid_email
    assert is_valid_email(email) is True
```

## Integration Testing Patterns

### 1. Database Integration Tests

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def test_database():
    """Create a test database for integration tests."""
    engine = create_engine("postgresql://test:test@localhost:5432/test_db")

    # Create tables
    from myapp.models.base import Base
    Base.metadata.create_all(engine)

    yield engine

    # Drop tables
    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def db_session(test_database):
    """Create a database session with automatic rollback."""
    Session = sessionmaker(bind=test_database)
    session = Session()

    yield session

    session.rollback()
    session.close()

@pytest.mark.integration
def test_user_crud_operations(db_session):
    """Test complete CRUD operations on User model."""
    from myapp.models.user import User

    # Create
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()

    assert user.id is not None

    # Read
    fetched_user = db_session.query(User).filter_by(email="test@example.com").first()
    assert fetched_user.name == "Test User"

    # Update
    fetched_user.name = "Updated Name"
    db_session.commit()

    updated_user = db_session.query(User).filter_by(id=user.id).first()
    assert updated_user.name == "Updated Name"

    # Delete
    db_session.delete(updated_user)
    db_session.commit()

    deleted_user = db_session.query(User).filter_by(id=user.id).first()
    assert deleted_user is None
```

### 2. API Integration Tests

```python
import pytest
from fastapi.testclient import TestClient
from myapp.main import app

@pytest.fixture
def client():
    """Create test client for FastAPI app."""
    return TestClient(app)

@pytest.mark.integration
class TestUserAPI:
    """Integration tests for User API."""

    def test_create_user(self, client):
        """Should create a new user via API."""
        response = client.post(
            "/api/users",
            json={"email": "new@example.com", "name": "New User"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "new@example.com"
        assert data["name"] == "New User"
        assert "id" in data

    def test_get_user(self, client):
        """Should retrieve user by ID."""
        # Create user first
        create_response = client.post(
            "/api/users",
            json={"email": "get@example.com", "name": "Get User"},
        )
        user_id = create_response.json()["id"]

        # Get user
        response = client.get(f"/api/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "get@example.com"

    def test_get_nonexistent_user_returns_404(self, client):
        """Should return 404 for non-existent user."""
        response = client.get("/api/users/nonexistent-id")
        assert response.status_code == 404
```

## Test Organization Patterns

### 1. Nested Test Classes

```python
class TestUserManagement:
    """Test suite for user management functionality."""

    class TestUserCreation:
        """Tests for user creation."""

        def test_create_user_with_valid_data(self):
            pass

        def test_create_user_with_duplicate_email_fails(self):
            pass

    class TestUserRetrieval:
        """Tests for user retrieval."""

        def test_get_user_by_id(self):
            pass

        def test_get_all_users(self):
            pass

    class TestUserDeletion:
        """Tests for user deletion."""

        def test_delete_existing_user(self):
            pass

        def test_delete_nonexistent_user_fails(self):
            pass
```

### 2. Markers for Test Organization

```python
@pytest.mark.unit
def test_email_validation():
    """Unit test for email validation."""
    pass

@pytest.mark.integration
@pytest.mark.slow
def test_database_migration():
    """Integration test that takes time."""
    pass

@pytest.mark.smoke
def test_app_starts():
    """Smoke test to verify app can start."""
    pass

# Run subsets:
# pytest -m unit
# pytest -m "not slow"
# pytest -m "integration and not slow"
```

## Best Practices

1. **Follow AAA pattern** -- Arrange, Act, Assert in every test.
2. **Use descriptive test names** -- Test names should explain what they verify.
3. **One logical assertion per test** -- Multiple `assert` statements are fine if testing one concept.
4. **Use fixtures for setup** -- Avoid duplicating setup code.
5. **Mock at boundaries** -- Mock external services, not internal functions.
6. **Test behavior, not implementation** -- Tests should survive refactoring.
7. **Use parametrize for similar tests** -- Reduce code duplication.
8. **Keep tests fast** -- Unit tests should run in milliseconds.
9. **Clean up resources** -- Use yield fixtures or context managers.
10. **Use type hints in tests** -- Makes tests more maintainable.

## Anti-Patterns to Avoid

1. **Testing private methods directly** -- Test through public API.
2. **Shared mutable state** -- Each test must be independent.
3. **Over-mocking** -- Don't mock everything; test real code paths.
4. **Ignoring test failures** -- Fix or delete, never skip indefinitely.
5. **Hardcoded values everywhere** -- Use fixtures and factories.
6. **Giant test files** -- Split by feature or functionality.
7. **Not using pytest features** -- Don't write `unittest.TestCase` classes.
8. **Testing framework code** -- Don't test that `list.append()` works.
9. **No cleanup** -- Always clean up database, files, network resources.
10. **Cryptic assertion messages** -- Add custom messages to assertions.

## Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/unit/test_user_service.py

# Run specific test
pytest tests/unit/test_user_service.py::test_create_user

# Run by marker
pytest -m unit
pytest -m "not slow"

# Run with coverage
pytest --cov=src --cov-report=html

# Run in parallel (requires pytest-xdist)
pytest -n auto

# Run with verbose output
pytest -v

# Run and stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run with debugging
pytest --pdb
```

Python testing is about confidence. Write tests that give you the courage to refactor and the safety net to catch bugs early.
