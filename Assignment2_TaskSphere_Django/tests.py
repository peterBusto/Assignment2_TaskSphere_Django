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


class UserRegistrationAPITests(TestCase):
    """Tests for user registration API endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        self.assertIn('email', response.data)
        self.assertIn('username', response.data)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
        
        # Verify user was created in database
        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_registration_missing_fields(self):
        """Test registration with missing required fields."""
        # Test missing username
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
        
        # Test missing first_name
        data = {
            'username': 'testuser',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.data)
        
        # Test missing last_name
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('last_name', response.data)
        
        # Test missing email
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'differentpass'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertIn("Password fields didn't match", str(response.data))
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email."""
        # Create first user
        User.objects.create_user(
            username='existinguser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Try to register with same email
        data = {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username."""
        # Create first user
        User.objects.create_user(
            username='testuser',
            email='existing@example.com',
            password='testpass123'
        )
        
        # Try to register with same username
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'new@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('username', response.data)
    
    def test_user_registration_invalid_email(self):
        """Test registration with invalid email format."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid-email',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)


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
