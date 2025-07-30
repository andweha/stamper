import pytest
from app.forms import RegistrationForm, LoginForm, commentForm
from app.models import User, db


class TestRegistrationForm:
    """Test cases for RegistrationForm"""
    
    def test_valid_registration_form(self, app_instance):
        """Test valid registration form data"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is True
    
    def test_invalid_username_length(self, app_instance):
        """Test username that's too short"""
        with app_instance.app_context():
            form_data = {
                'username': 'a',  # Too short
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is False
            assert any("between 2 and 20 characters" in e for e in form.username.errors)
    
    def test_invalid_username_characters(self, app_instance):
        """Test username with invalid characters"""
        with app_instance.app_context():
            form_data = {
                'username': 'test@user',  # Invalid character @
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is False
            assert 'Letters, numbers, ., and _ only.' in form.username.errors
    
    def test_valid_username_characters(self, app_instance):
        """Test username with valid characters"""
        with app_instance.app_context():
            valid_usernames = ['testuser', 'test_user', 'test.user', 'test123', 'Test_User_123']
            
            for username in valid_usernames:
                form_data = {
                    'username': username,
                    'password': 'ValidPass123!',
                    'confirm_password': 'ValidPass123!'
                }
                form = RegistrationForm(data=form_data)
                assert form.validate() is True, f"Username '{username}' should be valid"
    
    def test_password_too_short(self, app_instance):
        """Test password that's too short"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'Short1!',  # Too short
                'confirm_password': 'Short1!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is False
            assert "at least 8" in form.password.errors[0]
    
    def test_password_missing_requirements(self, app_instance):
        """Test password missing complexity requirements"""
        with app_instance.app_context():
            invalid_passwords = [
                'password123!',     # No uppercase
                'PASSWORD123!',     # No lowercase
                'Password!',        # No digit
                'Password123',      # No special character
            ]
            
            for password in invalid_passwords:
                form_data = {
                    'username': 'testuser',
                    'password': password,
                    'confirm_password': password
                }
                form = RegistrationForm(data=form_data)
                assert form.validate() is False, f"Password '{password}' should be invalid"
                assert 'Use letters, numbers, and special characters.' in form.password.errors
    
    def test_password_mismatch(self, app_instance):
        """Test password confirmation mismatch"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'ValidPass123!',
                'confirm_password': 'DifferentPass123!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is False
            assert 'Passwords must match.' in form.confirm_password.errors
    
    def test_duplicate_username_validation(self, app_instance, sample_users):
        """Test validation fails for existing username"""
        with app_instance.app_context():
            existing_user = sample_users[0]
            form_data = {
                'username': existing_user.username,
                'password': 'ValidPass123!',
                'confirm_password': 'ValidPass123!'
            }
            form = RegistrationForm(data=form_data)
            assert form.validate() is False
            assert 'Username is already taken. Please choose another.' in form.username.errors


class TestLoginForm:
    """Test cases for LoginForm"""
    
    def test_valid_login_form(self, app_instance):
        """Test valid login form data"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'password123'
            }
            form = LoginForm(data=form_data)
            assert form.validate() is True
    
    def test_empty_username(self, app_instance):
        """Test login form with empty username"""
        with app_instance.app_context():
            form_data = {
                'username': '',
                'password': 'password123'
            }
            form = LoginForm(data=form_data)
            assert form.validate() is False
            assert 'This field is required.' in form.username.errors
    
    def test_empty_password(self, app_instance):
        """Test login form with empty password"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': ''
            }
            form = LoginForm(data=form_data)
            assert form.validate() is False
            assert 'This field is required.' in form.password.errors
    
    def test_remember_me_field(self, app_instance):
        """Test remember me checkbox"""
        with app_instance.app_context():
            form_data = {
                'username': 'testuser',
                'password': 'password123',
                'remember': True
            }
            form = LoginForm(data=form_data)
            assert form.validate() is True
            assert form.remember.data is True


class TestCommentForm:
    """Test cases for commentForm"""
    
    def test_valid_comment_form_with_text(self, app_instance):
        """Test valid comment form with text content"""
        with app_instance.app_context():
            form_data = {
                'content': 'This is a great scene!',
                'timestamp': '10:30'
            }
            form = commentForm(data=form_data)
            assert form.validate() is True
    
    def test_valid_comment_form_with_gif(self, app_instance):
        """Test valid comment form with GIF only"""
        with app_instance.app_context():
            form_data = {
                'content': '',
                'timestamp': '05:15',
                'gif_url': 'https://example.com/funny.gif'
            }
            form = commentForm(data=form_data)
            assert form.validate() is True
    
    def test_valid_comment_form_with_both(self, app_instance):
        """Test valid comment form with both text and GIF"""
        with app_instance.app_context():
            form_data = {
                'content': 'LOL this part!',
                'timestamp': '15:45',
                'gif_url': 'https://example.com/laughing.gif'
            }
            form = commentForm(data=form_data)
            assert form.validate() is True
    
    def test_empty_comment_form(self, app_instance):
        """Test comment form with no content or GIF"""
        with app_instance.app_context():
            form_data = {
                'content': '',
                'timestamp': '10:30',
                'gif_url': ''
            }
            form = commentForm(data=form_data)
            assert form.validate() is False
            assert 'Cannot post an empty comment.' in form.content.errors
    
    def test_whitespace_only_content(self, app_instance):
        """Test comment form with whitespace-only content"""
        with app_instance.app_context():
            form_data = {
                'content': '   \n\t  ',
                'timestamp': '10:30',
                'gif_url': ''
            }
            form = commentForm(data=form_data)
            assert form.validate() is False
            assert 'Cannot post an empty comment.' in form.content.errors
    
    def test_valid_timestamp_formats(self, app_instance):
        """Test various valid timestamp formats"""
        with app_instance.app_context():
            valid_timestamps = [
                '5:30',      # M:SS
                '10:45',     # MM:SS
                '1:05:30',   # H:MM:SS
                '10:05:30',  # HH:MM:SS
                '0:30',      # Edge case
                '59:59',     # Maximum minutes/seconds
            ]
            
            for timestamp in valid_timestamps:
                form_data = {
                    'content': 'Test comment',
                    'timestamp': timestamp
                }
                form = commentForm(data=form_data)
                assert form.validate() is True, f"Timestamp '{timestamp}' should be valid"
    
    def test_invalid_timestamp_formats(self, app_instance):
        """Test various invalid timestamp formats"""
        with app_instance.app_context():
            invalid_timestamps = [
                '5',         # Just minutes
                '5:',        # Missing seconds
                ':30',       # Missing minutes
                '60:30',     # Invalid minutes
                '10:60',     # Invalid seconds
                '1:60:30',   # Invalid minutes in H:MM:SS
                '1:10:60',   # Invalid seconds in H:MM:SS
                'abc:def',   # Non-numeric
                '10-30',     # Wrong separator
                '10.30',     # Wrong separator
            ]
            
            for timestamp in invalid_timestamps:
                form_data = {
                    'content': 'Test comment',
                    'timestamp': timestamp
                }
                form = commentForm(data=form_data)
                assert form.validate() is False, f"Timestamp '{timestamp}' should be invalid"
                assert 'Use HH:MM:SS or MM:SS format' in form.timestamp.errors
    
    def test_missing_timestamp(self, app_instance):
        """Test comment form with missing timestamp"""
        with app_instance.app_context():
            form_data = {
                'content': 'Test comment',
                'timestamp': ''
            }
            form = commentForm(data=form_data)
            assert form.validate() is False
            assert 'This field is required.' in form.timestamp.errors