try:
    import pytest
except ImportError:
    pytest = None

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

def create_user(username="testuser", email="test@example.com", password="testpass123", **kwargs):
    """Create and return a test user."""
    defaults = {"username": username, "email": email}
    defaults.update(kwargs)
    return User.objects.create_user(password=password, **defaults)


def create_admin(username="admin", email="admin@example.com", password="adminpass123", **kwargs):
    """Create and return a test superuser."""
    defaults = {"username": username, "email": email}
    defaults.update(kwargs)
    return User.objects.create_superuser(password=password, **defaults)


def api_client(user=None):
    """Return APIClient, optionally authenticated as user."""
    client = APIClient()
    if user:
        client.force_authenticate(user=user)
    return client


# Pytest fixtures (only work if pytest is installed)
if pytest:
    @pytest.fixture
    def user():
        """Create a test user fixture."""
        return create_user()


    @pytest.fixture
    def admin():
        """Create an admin user fixture."""
        return create_admin()


    @pytest.fixture
    def client():
        """Return unauthenticated API client."""
        return api_client()


    @pytest.fixture
    def auth_client(user):
        """Return authenticated API client as regular user."""
        return api_client(user)


    @pytest.fixture
    def admin_client(admin):
        """Return authenticated API client as admin."""
        return api_client(admin)
