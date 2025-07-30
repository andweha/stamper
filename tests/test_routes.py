import pytest
import json
from unittest.mock import patch, MagicMock
from app.models import User, Comment, Favorite, History, db


class TestAuthRoutes:
    """Test authentication routes"""
    
    def test_register_get(self, client):
        """Test GET request to register page"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'Register' in response.data
    
    def test_register_post_valid(self, client):
        """Test successful user registration"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'ValidPass123!',
            'confirm_password': 'ValidPass123!',
            'submit': 'Sign Up'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Account created' in response.data
        
        # Verify user was created
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.username == 'newuser'
    
    def test_register_post_invalid_password(self, client):
        """Test registration with invalid password"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'weak',
            'confirm_password': 'weak',
            'submit': 'Sign Up'
        })
        
        assert response.status_code == 200
        assert b'Use letters, numbers, and special characters' in response.data
    
    def test_register_duplicate_username(self, client, sample_users):
        """Test registration with existing username"""
        existing_user = sample_users[0]
        response = client.post('/register', data={
            'username': existing_user.username,
            'password': 'ValidPass123!',
            'confirm_password': 'ValidPass123!',
            'submit': 'Sign Up'
        })
        
        assert response.status_code == 200
        assert b'Username is already taken' in response.data
    
    def test_login_get(self, client):
        """Test GET request to login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'Login' in response.data
    
    def test_login_post_valid(self, client, sample_users):
        """Test successful login"""
        user = sample_users[0]
        response = client.post('/login', data={
            'username': user.username,
            'password': user.password,
            'submit': 'Login'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should redirect to catalogue after successful login
    
    def test_login_post_invalid(self, client):
        """Test login with invalid credentials"""
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpassword',
            'submit': 'Login'
        })
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_logout(self, client, auth_user):
        """Test user logout"""
        response = client.post('/logout', follow_redirects=True)
        assert response.status_code == 200
        # Should redirect to login page


class TestMediaRoutes:
    """Test media-related routes"""
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_catalogue_page(self, mock_db_path, client, media_db):
        """Test catalogue page displays content"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.get('/')
        assert response.status_code == 200
        assert b'catalogue' in response.data.lower()
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_movie_page(self, mock_db_path, client, media_db):
        """Test individual movie page"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.get('/movie/12345')
        assert response.status_code == 200
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_tv_show_page(self, mock_db_path, client, media_db):
        """Test TV show page"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.get('/media/67890')
        assert response.status_code == 200
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_anime_page(self, mock_db_path, client, media_db):
        """Test anime page"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.get('/anime/11111')
        assert response.status_code == 200
    
    def test_nonexistent_media(self, client):
        """Test accessing nonexistent media returns 404"""
        response = client.get('/movie/99999')
        assert response.status_code == 404


class TestCommentRoutes:
    """Test comment-related functionality"""
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_add_comment_authenticated(self, mock_db_path, client, auth_user, media_db):
        """Test adding comment when authenticated"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.post('/movie/12345', data={
            'content': 'Great movie!',
            'timestamp': '10:30',
            'submit': 'Comment'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify comment was created
        comment = Comment.query.filter_by(content='Great movie!').first()
        assert comment is not None
        assert comment.user_id == auth_user.id
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_add_comment_unauthenticated(self, mock_db_path, client, media_db):
        """Test adding comment when not authenticated"""
        mock_db_path.__str__ = lambda x: media_db
        
        response = client.post('/movie/12345', data={
            'content': 'Great movie!',
            'timestamp': '10:30',
            'submit': 'Comment'
        }, follow_redirects=True)
        
        # Should redirect to login
        assert response.status_code == 200
    
    def test_add_comment_invalid_timestamp(self, client, auth_user):
        """Test adding comment with invalid timestamp"""
        response = client.post('/movie/12345', data={
            'content': 'Great movie!',
            'timestamp': 'invalid',
            'submit': 'Comment'
        })
        
        assert response.status_code == 200
        assert b'Use HH:MM:SS or MM:SS format' in response.data
    
    def test_delete_comment_owner(self, client, auth_user, sample_comments):
        """Test deleting own comment"""
        comment = sample_comments[0]
        response = client.post(f'/comment/{comment.id}/delete', follow_redirects=True)
        
        assert response.status_code == 200
        
        # Verify comment was deleted
        deleted_comment = Comment.query.get(comment.id)
        assert deleted_comment is None
    
    def test_delete_comment_not_owner(self, client, sample_users, sample_comments):
        """Test deleting someone else's comment"""
        # Login as different user
        other_user = sample_users[1]
        client.post('/login', data={
            'username': other_user.username,
            'password': other_user.password
        })
        
        comment = sample_comments[0]  # Owned by sample_users[0]
        response = client.post(f'/comment/{comment.id}/delete', follow_redirects=True)
        
        assert response.status_code == 200
        assert b"don't have permission" in response.data
        
        # Verify comment still exists
        existing_comment = Comment.query.get(comment.id)
        assert existing_comment is not None


class TestFavoriteRoutes:
    """Test favorite-related functionality"""
    
    def test_toggle_favorite_add(self, client, auth_user):
        """Test adding a favorite"""
        response = client.post('/toggle_favorite/12345')
        assert response.status_code == 204
        
        # Verify favorite was added
        favorite = Favorite.query.filter_by(user_id=auth_user.id, media_id=12345).first()
        assert favorite is not None
    
    def test_toggle_favorite_remove(self, client, auth_user):
        """Test removing a favorite"""
        # First add a favorite
        favorite = Favorite(user_id=auth_user.id, media_id=12345)
        db.session.add(favorite)
        db.session.commit()
        
        response = client.post('/toggle_favorite/12345')
        assert response.status_code == 204
        
        # Verify favorite was removed
        removed_favorite = Favorite.query.filter_by(user_id=auth_user.id, media_id=12345).first()
        assert removed_favorite is None
    
    def test_toggle_favorite_unauthenticated(self, client):
        """Test toggling favorite when not authenticated"""
        response = client.post('/toggle_favorite/12345')
        assert response.status_code == 302  # Redirect to login
    
    @patch('app.flask_app.MEDIA_DB_PATH')
    def test_favorites_page(self, mock_db_path, client, auth_user, media_db):
        """Test favorites page"""
        mock_db_path.__str__ = lambda x: media_db
        
        # Add a favorite
        favorite = Favorite(user_id=auth_user.id, media_id=12345)
        db.session.add(favorite)
        db.session.commit()
        
        response = client.get('/favorites')
        assert response.status_code == 200
    
    def test_favorites_page_unauthenticated(self, client):
        """Test favorites page when not authenticated"""
        response = client.get('/favorites')
        assert response.status_code == 302  # Redirect to login


class TestProfileRoutes:
    """Test profile-related functionality"""
    
    def test_profile_page(self, client, auth_user):
        """Test profile page"""
        response = client.get('/profile')
        assert response.status_code == 200
        assert auth_user.username.encode() in response.data
    
    def test_profile_page_unauthenticated(self, client):
        """Test profile page when not authenticated"""
        response = client.get('/profile')
        assert response.status_code == 302  # Redirect to login
    
    def test_update_watch_time_movie(self, client, auth_user):
        """Test updating movie watch time"""
        response = client.post('/update_watch_time', 
            json={
                'watched_seconds': 1800,
                'media_type': 'movie'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        
        # Verify watch time was updated
        db.session.refresh(auth_user)
        assert auth_user.total_movie_seconds == 1800
    
    def test_update_watch_time_tv(self, client, auth_user):
        """Test updating TV show watch time"""
        response = client.post('/update_watch_time',
            json={
                'watched_seconds': 2400,
                'media_type': 'tv'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify watch time was updated
        db.session.refresh(auth_user)
        assert auth_user.total_show_seconds == 2400
    
    def test_update_watch_time_anime(self, client, auth_user):
        """Test updating anime watch time"""
        response = client.post('/update_watch_time',
            json={
                'watched_seconds': 1440,
                'media_type': 'anime'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # Verify watch time was updated
        db.session.refresh(auth_user)
        assert auth_user.total_anime_seconds == 1440
    
    def test_update_watch_time_invalid_data(self, client, auth_user):
        """Test updating watch time with invalid data"""
        response = client.post('/update_watch_time',
            json={
                'watched_seconds': -100,
                'media_type': 'movie'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_update_watch_time_beacon(self, client, auth_user):
        """Test updating watch time via beacon API"""
        response = client.post('/update_watch_time_beacon', 
            data={
                'watched_seconds': '1200',
                'media_type': 'movie'
            }
        )
        
        assert response.status_code == 204
        
        # Verify watch time was updated
        db.session.refresh(auth_user)
        assert auth_user.total_movie_seconds == 1200


class TestHistoryRoutes:
    """Test history-related functionality"""
    
    def test_history_page(self, client, auth_user):
        """Test history page"""
        # Add some history
        history = History(
            user_id=auth_user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie"
        )
        db.session.add(history)
        db.session.commit()
        
        response = client.get('/history')
        assert response.status_code == 200
        assert b'Test Movie' in response.data
    
    def test_history_page_unauthenticated(self, client):
        """Test history page when not authenticated"""
        response = client.get('/history')
        assert response.status_code == 302  # Redirect to login


class TestAPIRoutes:
    """Test API endpoints"""
    
    def test_comment_timestamps_api(self, client, sample_comments):
        """Test getting comment timestamps"""
        response = client.get('/api/comments/12345')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
    
    @patch('requests.get')
    def test_search_api(self, mock_get, client):
        """Test search API"""
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 12345,
                    "title": "Test Movie",
                    "media_type": "movie",
                    "overview": "A test movie",
                    "poster_path": "/test.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        response = client.get('/api/search?q=test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
        assert data[0]['title'] == 'Test Movie'
    
    def test_search_api_empty_query(self, client):
        """Test search API with empty query"""
        response = client.get('/api/search?q=')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data == []
    
    @patch('app.tenor.search_gif')
    def test_search_gifs_api(self, mock_search_gif, client):
        """Test GIF search API"""
        mock_search_gif.return_value = {
            "gifs": ["https://example.com/gif1.gif", "https://example.com/gif2.gif"],
            "next": "next_token"
        }
        
        response = client.get('/search_gifs?q=funny&limit=10')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'gifs' in data
        assert len(data['gifs']) == 2