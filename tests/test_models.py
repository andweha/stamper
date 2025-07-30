import pytest
from datetime import datetime, timezone
from app.models import User, Comment, Favorite, History, db


class TestUserModel:
    """Test cases for User model"""
    
    def test_user_creation(self, test_db):
        """Test creating a new user"""
        user = User(username="testuser", password="password123")
        db.session.add(user)
        db.session.commit()
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.password == "password123"
        assert user.total_movie_seconds == 0
        assert user.total_show_seconds == 0
        assert user.total_anime_seconds == 0
    
    def test_user_repr(self, test_db):
        """Test user string representation"""
        user = User(username="testuser", password="password123")
        assert str(user) == "User('testuser')"
    
    def test_user_unique_username(self, test_db):
        """Test that usernames must be unique"""
        user1 = User(username="testuser", password="password123")
        user2 = User(username="testuser", password="password456")
        
        db.session.add(user1)
        db.session.commit()
        
        db.session.add(user2)
        with pytest.raises(Exception):  # Should raise integrity error
            db.session.commit()
    
    def test_user_watch_time_tracking(self, test_db):
        """Test watch time tracking functionality"""
        user = User(username="testuser", password="password123")
        user.total_movie_seconds = 3600  # 1 hour
        user.total_show_seconds = 7200   # 2 hours
        user.total_anime_seconds = 1800  # 30 minutes
        
        db.session.add(user)
        db.session.commit()
        
        assert user.total_movie_seconds == 3600
        assert user.total_show_seconds == 7200
        assert user.total_anime_seconds == 1800


class TestCommentModel:
    """Test cases for Comment model"""
    
    def test_comment_creation(self, test_db, sample_users):
        """Test creating a new comment"""
        user = sample_users[0]
        comment = Comment(
            content="This is a test comment",
            timestamp=300.5,
            user_id=user.id,
            episode_id=12345,
            media_title="Test Movie"
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.id is not None
        assert comment.content == "This is a test comment"
        assert comment.timestamp == 300.5
        assert comment.user_id == user.id
        assert comment.episode_id == 12345
        assert comment.media_title == "Test Movie"
        assert isinstance(comment.created_at, datetime)
    
    def test_comment_with_gif(self, test_db, sample_users):
        """Test creating a comment with GIF"""
        user = sample_users[0]
        comment = Comment(
            content="Great scene!",
            timestamp=600,
            user_id=user.id,
            episode_id=12345,
            media_title="Test Movie",
            gif_url="https://example.com/gif.gif"
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.gif_url == "https://example.com/gif.gif"
    
    def test_comment_user_relationship(self, test_db, sample_users):
        """Test comment-user relationship"""
        user = sample_users[0]
        comment = Comment(
            content="Test comment",
            timestamp=100,
            user_id=user.id,
            episode_id=12345,
            media_title="Test Movie"
        )
        db.session.add(comment)
        db.session.commit()
        
        assert comment.user == user
        assert comment in user.comments


class TestFavoriteModel:
    """Test cases for Favorite model"""
    
    def test_favorite_creation(self, test_db, sample_users):
        """Test creating a new favorite"""
        user = sample_users[0]
        favorite = Favorite(user_id=user.id, media_id=12345)
        db.session.add(favorite)
        db.session.commit()
        
        assert favorite.id is not None
        assert favorite.user_id == user.id
        assert favorite.media_id == 12345
    
    def test_favorite_unique_constraint(self, test_db, sample_users):
        """Test that user can't favorite the same media twice"""
        user = sample_users[0]
        favorite1 = Favorite(user_id=user.id, media_id=12345)
        favorite2 = Favorite(user_id=user.id, media_id=12345)
        
        db.session.add(favorite1)
        db.session.commit()
        
        db.session.add(favorite2)
        with pytest.raises(Exception):  # Should raise integrity error
            db.session.commit()


class TestHistoryModel:
    """Test cases for History model"""
    
    def test_history_creation(self, test_db, sample_users):
        """Test creating a new history entry"""
        user = sample_users[0]
        history = History(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie",
            poster_url="https://example.com/poster.jpg"
        )
        db.session.add(history)
        db.session.commit()
        
        assert history.id is not None
        assert history.user_id == user.id
        assert history.media_type == "movie"
        assert history.media_id == 12345
        assert history.title == "Test Movie"
        assert history.poster_url == "https://example.com/poster.jpg"
        assert isinstance(history.watched_at, datetime)
    
    def test_history_repr(self, test_db, sample_users):
        """Test history string representation"""
        user = sample_users[0]
        history = History(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie"
        )
        db.session.add(history)
        db.session.commit()
        
        expected = f"History(User: {user.id}, Media: Test Movie, Type: movie, Watched: {history.watched_at})"
        assert str(history) == expected
    
    def test_history_user_relationship(self, test_db, sample_users):
        """Test history-user relationship"""
        user = sample_users[0]
        history = History(
            user_id=user.id,
            media_type="tv",
            media_id=67890,
            title="Test TV Show"
        )
        db.session.add(history)
        db.session.commit()
        
        assert history.user == user
        assert history in user.history_entries
    
    def test_history_different_media_types(self, test_db, sample_users):
        """Test creating history for different media types"""
        user = sample_users[0]
        
        movie_history = History(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie"
        )
        
        tv_history = History(
            user_id=user.id,
            media_type="tv",
            media_id=67890,
            title="Test TV Show"
        )
        
        anime_history = History(
            user_id=user.id,
            media_type="anime",
            media_id=11111,
            title="Test Anime"
        )
        
        db.session.add_all([movie_history, tv_history, anime_history])
        db.session.commit()
        
        assert movie_history.media_type == "movie"
        assert tv_history.media_type == "tv"
        assert anime_history.media_type == "anime"