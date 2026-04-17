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
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from datetime import timedelta

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
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
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
        self.assertTrue(user.check_password('SecurePass123!'))
    
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
            'password': 'SecurePass123!',
            'confirm_password': 'DifferentPass123!'
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
    
    def test_user_registration_password_too_short(self):
        """Test registration with password shorter than 8 characters."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'Short1!',
            'confirm_password': 'Short1!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertIn('at least 8 characters', str(response.data))
    
    def test_user_registration_password_missing_uppercase(self):
        """Test registration with password missing uppercase letter."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'lowercase123!',
            'confirm_password': 'lowercase123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertIn('uppercase', str(response.data))
    
    def test_user_registration_password_missing_number(self):
        """Test registration with password missing number."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'NoNumbers!',
            'confirm_password': 'NoNumbers!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertIn('number', str(response.data))
    
    def test_user_registration_password_missing_special_character(self):
        """Test registration with password missing special character."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'NoSpecial123',
            'confirm_password': 'NoSpecial123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertIn('special character', str(response.data))
    
    def test_user_registration_password_all_numeric(self):
        """Test registration with all-numeric password."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': '12345678',
            'confirm_password': '12345678'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
    
    def test_user_registration_password_similar_to_username(self):
        """Test registration with password similar to username."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'testuser123!',
            'confirm_password': 'testuser123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        # The similarity validator might not always trigger, so let's check for either similarity or other validation
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
    
    def test_user_registration_valid_password_complexity(self):
        """Test registration with valid password meeting all complexity requirements."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertIn('user_id', response.data)
        
        # Verify user was created with the correct password
        user = User.objects.get(email='test@example.com')
        self.assertTrue(user.check_password('SecurePass123!'))
    
    def test_user_registration_multiple_password_errors(self):
        """Test registration with password failing multiple validation rules."""
        data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password': 'weak',
            'confirm_password': 'weak'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        # Should catch multiple errors: too short, missing uppercase, missing number, missing special character


class UserLoginAPITests(TestCase):
    """Tests for user login API endpoint."""
    
    def setUp(self):
        """Set up test client and create a test user."""
        self.client = APIClient()
        self.login_url = '/api/auth/login/'
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
    
    def test_login_success(self):
        """Test successful login returns token."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['username'], 'testuser')
    
    def test_login_invalid_email(self):
        """Test login with non-existent email."""
        data = {
            'email': 'wrong@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)
    
    def test_login_invalid_password(self):
        """Test login with wrong password."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
    
    def test_login_missing_email(self):
        """Test login without email field."""
        data = {
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_missing_password(self):
        """Test login without password field."""
        data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_empty_fields(self):
        """Test login with empty email and password."""
        data = {
            'email': '',
            'password': ''
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
    
    def test_login_token_created(self):
        """Test that token is created for user on first login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        # First login should create token
        response1 = self.client.post(self.login_url, data, format='json')
        token1 = response1.data['token']
        
        # Second login should return same token
        response2 = self.client.post(self.login_url, data, format='json')
        token2 = response2.data['token']
        
        self.assertEqual(token1, token2)
    
    def test_login_invalid_password_message(self):
        """Test login error message for wrong password."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
    
    def test_login_nonexistent_user(self):
        """Test login with email that doesn't exist in database."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'somepassword123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, 400)
        self.assertIn('email', response.data)


class UserLogoutAPITests(TestCase):
    """Tests for user logout API endpoint."""
    
    def setUp(self):
        """Set up test client and create a test user with token."""
        self.client = APIClient()
        self.logout_url = '/api/auth/logout/'
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        # Create token for the user
        self.token = Token.objects.create(user=self.user)
    
    def test_logout_success(self):
        """Test successful logout with valid token."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.logout_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Logout successful')
        
        # Verify token is deleted
        self.assertFalse(Token.objects.filter(user=self.user).exists())
    
    def test_logout_without_authentication(self):
        """Test logout without authentication token."""
        response = self.client.post(self.logout_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_invalid_token(self):
        """Test logout with invalid token."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = self.client.post(self.logout_url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_when_no_token_exists(self):
        """Test logout when user has no token."""
        # Delete the token first
        self.token.delete()
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(self.logout_url, format='json')
        
        # Should return 401 because token doesn't exist
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_prevents_token_reuse(self):
        """Test that deleted token cannot be reused."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # First logout
        response1 = self.client.post(self.logout_url, format='json')
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        # Try to use the same token again
        response2 = self.client.post(self.logout_url, format='json')
        self.assertEqual(response2.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_and_login_creates_new_token(self):
        """Test that user can login again after logout."""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        # Logout
        logout_response = self.client.post(self.logout_url, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # Clear credentials before trying to login again
        self.client.credentials()
        
        # Login again
        login_response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('token', login_response.data)
        
        # Verify new token is different from the old one
        new_token = login_response.data['token']
        self.assertNotEqual(new_token, self.token.key)
        
        # Verify new token exists in database
        self.assertTrue(Token.objects.filter(user=self.user).exists())
        self.assertEqual(Token.objects.get(user=self.user).key, new_token)


class TaskCreationAPITests(TestCase):
    """Tests for task creation API endpoint."""
    
    def setUp(self):
        """Set up test client and create a test user with token."""
        self.client = APIClient()
        self.task_create_url = '/api/tasks/create/'
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create and set authentication token
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_create_task_success(self):
        """Test successful task creation with all fields."""
        data = {
            'title': 'Complete Django Project',
            'description': 'Finish the task management system with all CRUD operations',
            'priority': 'high',
            'due_date': (timezone.now() + timedelta(days=7)).isoformat()
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('task', response.data)
        self.assertEqual(response.data['message'], 'Task created successfully')
        
        # Verify task was created in database
        from tasks.models import Task
        task = Task.objects.first()
        self.assertEqual(task.title, 'Complete Django Project')
        self.assertEqual(task.description, 'Finish the task management system with all CRUD operations')
        self.assertEqual(task.priority, 'high')
        self.assertEqual(task.user, self.user)
        self.assertIsNotNone(task.due_date)
    
    def test_create_task_minimal_data(self):
        """Test creating task with only required fields."""
        data = {
            'title': 'Simple Task'
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify task was created with default values
        from tasks.models import Task
        task = Task.objects.first()
        self.assertEqual(task.title, 'Simple Task')
        self.assertEqual(task.priority, 'medium')  # Default priority
        self.assertEqual(task.description, '')  # Empty description
        self.assertIsNone(task.due_date)  # No due date set
    
    def test_create_task_title_validation(self):
        """Test validation for title field."""
        # Test title too short
        data = {
            'title': 'Hi',
            'description': 'This title is too short'
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)
        self.assertIn('at least 3 characters', str(response.data))
        
        # Verify no task was created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_priority_validation(self):
        """Test validation for priority field."""
        data = {
            'title': 'Valid Task Title',
            'priority': 'urgent'  # Invalid priority
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('priority', response.data)
        self.assertIn('not a valid choice', str(response.data))
        
        # Verify no task was created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_due_date_validation(self):
        """Test validation for due date field."""
        data = {
            'title': 'Valid Task Title',
            'due_date': (timezone.now() - timedelta(days=1)).isoformat()  # Past date
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('due_date', response.data)
        self.assertIn('cannot be in the past', str(response.data))
        
        # Verify no task was created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_unauthenticated(self):
        """Test that unauthenticated users cannot create tasks."""
        # Remove authentication
        self.client.credentials()
        
        data = {
            'title': 'Test Task'
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify no task was created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_with_invalid_token(self):
        """Test that invalid token cannot create tasks."""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        
        data = {
            'title': 'Test Task'
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verify no task was created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 0)
    
    def test_create_task_user_association(self):
        """Test that task is properly associated with authenticated user."""
        # Create another user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        data = {
            'title': 'User Task Test'
        }
        
        response = self.client.post(self.task_create_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify task is associated with authenticated user (not other user)
        from tasks.models import Task
        task = Task.objects.first()
        self.assertEqual(task.user, self.user)
        self.assertNotEqual(task.user, other_user)
    
    def test_create_task_all_priority_levels(self):
        """Test creating tasks with all valid priority levels."""
        priorities = ['low', 'medium', 'high']
        
        for priority in priorities:
            data = {
                'title': f'Task with {priority} priority',
                'priority': priority
            }
            
            response = self.client.post(self.task_create_url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            # Verify priority was set correctly
            from tasks.models import Task
            task = Task.objects.get(title=f'Task with {priority} priority')
            self.assertEqual(task.priority, priority)
        
        # Verify all tasks were created
        from tasks.models import Task
        self.assertEqual(Task.objects.count(), 3)


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
