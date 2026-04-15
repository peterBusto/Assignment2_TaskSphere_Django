import sys
import os
import subprocess
import argparse


def setup_django():
    """Set up Django settings for testing."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Assignment2_TaskSphere_Django.settings')
    import django
    django.setup()


def run_pytest(test_paths=None, verbose=False, failfast=False):
    """Run pytest with specified options."""
    cmd = ['pytest']
    
    if verbose:
        cmd.append('-v')
    if failfast:
        cmd.append('-x')
    
    # Default to running all tests if no paths specified
    if test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append('.')
    
    return subprocess.call(cmd)


def run_django_tests(test_paths=None, verbose=False, failfast=False):
    """Run Django's test runner."""
    setup_django()
    
    cmd = [sys.executable, 'manage.py', 'test']
    
    if verbose:
        cmd.append('--verbosity=2')
    if failfast:
        cmd.append('--failfast')
    
    if test_paths:
        cmd.extend(test_paths)
    
    return subprocess.call(cmd)


def run_coverage(test_paths=None):
    """Run tests with coverage report."""
    cmd = ['pytest', '--cov=.', '--cov-report=term-missing']
    
    if test_paths:
        cmd.extend(test_paths)
    else:
        cmd.append('.')
    
    return subprocess.call(cmd)


def main():
    parser = argparse.ArgumentParser(
        description='Run tests for TaskSphere Django project'
    )
    parser.add_argument(
        'paths', 
        nargs='*', 
        help='Test paths to run (default: all tests)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '-x', '--failfast',
        action='store_true',
        help='Stop on first failure'
    )
    parser.add_argument(
        '--django',
        action='store_true',
        help='Use Django test runner instead of pytest'
    )
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run with coverage report'
    )
    
    args = parser.parse_args()
    
    # Change to project root
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    if args.coverage:
        exit_code = run_coverage(args.paths)
    elif args.django:
        exit_code = run_django_tests(args.paths, args.verbose, args.failfast)
    else:
        exit_code = run_pytest(args.paths, args.verbose, args.failfast)
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()


# =============================================================================
# ACTUAL DJANGO TEST CASES
# =============================================================================

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class UserCreationTests(TestCase):
    """Tests for user creation utilities."""
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(admin.username, 'admin')
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)


class APICLientTests(TestCase):
    """Tests for API client utilities."""
    
    def test_unauthenticated_client(self):
        """Test creating unauthenticated API client."""
        client = APIClient()
        # Just verify client is created successfully
        self.assertIsNotNone(client)
    
    def test_authenticated_client(self):
        """Test creating authenticated API client."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        client = APIClient()
        client.force_authenticate(user=user)
        self.assertIsNotNone(client)


class DjangoSetupTests(TestCase):
    """Tests to verify Django is properly configured."""
    
    def test_settings_loaded(self):
        """Test that Django settings are loaded."""
        from django.conf import settings
        self.assertTrue(settings.configured)
        # DEBUG is False during testing by default
    
    def test_database_configured(self):
        """Test that database is configured."""
        from django.conf import settings
        self.assertIn('default', settings.DATABASES)
