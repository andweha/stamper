import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import tempfile
import os
import sqlite3
import yaml
from unittest.mock import patch, MagicMock

# Import your app and models
from app.flask_app import app
from app.models import db, User, Comment, Favorite, History


def load_test_config():
    """Load test configuration from YAML file"""
    config_path = os.path.join(os.path.dirname(__file__), 'test_config.yaml')
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)


@pytest.fixture(scope='session')
def test_config():
    """Load test configuration"""
    return load_test_config()


@pytest.fixture
def app_instance(test_config):
    """Create and configure a new app instance for each test."""
    # Create a temporary file for the test database
    db_fd, db_path = tempfile.mkstemp()
    media_db_fd, media_db_path = tempfile.mkstemp()
    
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test-secret-key",
        "WTF_CSRF_ENABLED": False,  # Disable CSRF protection for testing
    })
    
    # Mock environment variables
    with patch.dict(os.environ, {
        'TMDB_API_KEY': test_config['test_config']['api_keys']['tmdb_api_key'],
        'GENAI_KEY': test_config['test_config']['api_keys']['genai_key'],
        'TENOR_API_KEY': test_config['test_config']['api_keys']['tenor_api_key'],
    }):
        with app.app_context():
            db.create_all()
            yield app
    
    # Clean up
    os.close(db_fd)
    os.unlink(db_path)
    os.close(media_db_fd)
    os.unlink(media_db_path)


@pytest.fixture
def client(app_instance):
    """A test client for the app."""
    return app_instance.test_client()


@pytest.fixture
def runner(app_instance):
    """A test runner for the app's Click commands."""
    return app_instance.test_cli_runner()


@pytest.fixture
def test_db(app_instance):
    """Create test database with sample data"""
    with app_instance.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_users(test_db, test_config):
    """Create sample users for testing"""
    users = []
    for user_data in test_config['test_config']['test_data']['users']:
        user = User(
            username=user_data['username'],
            password=user_data['password']
        )
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    return users


@pytest.fixture
def auth_user(client, sample_users):
    """Create and login a test user"""
    user = sample_users[0]
    
    # Login the user
    response = client.post('/login', data={
        'username': user.username,
        'password': user.password
    }, follow_redirects=True)
    
    return user


@pytest.fixture
def media_db(test_config):
    """Create test media database with sample data"""
    db_fd, db_path = tempfile.mkstemp()
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.executescript('''
        CREATE TABLE media (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            media_type TEXT,
            poster_url TEXT,
            overview TEXT,
            release_date TEXT,
            runtime INTEGER,
            vote_average REAL
        );
        
        CREATE TABLE seasons (
            season_id TEXT PRIMARY KEY,
            tv_id INTEGER,
            title TEXT,
            season_number INTEGER,
            name TEXT,
            overview TEXT,
            poster_url TEXT,
            air_date TEXT,
            episode_count INTEGER,
            vote_average REAL
        );
        
        CREATE TABLE episodes (
            episode_id INTEGER PRIMARY KEY,
            season_id TEXT,
            tv_id INTEGER,
            season_number INTEGER,
            episode_number INTEGER,
            episode_name TEXT,
            overview TEXT,
            air_date TEXT,
            runtime INTEGER,
            vote_average REAL,
            still_url TEXT
        );
        
        CREATE TABLE anime (
            anilist_id INTEGER PRIMARY KEY,
            title_romaji TEXT,
            title_english TEXT,
            episodes INTEGER,
            average_score TEXT,
            trending INTEGER,
            genres TEXT,
            description TEXT,
            cover_url TEXT,
            start_date TEXT
        );
        
        CREATE TABLE anime_ep (
            episode_id INTEGER PRIMARY KEY,
            anilist_id INTEGER,
            episode_title TEXT,
            thumbnail TEXT,
            duration INTEGER
        );
        
        CREATE TABLE featured_movies (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            rank INTEGER
        );
        
        CREATE TABLE featured_tv (
            tmdb_id INTEGER PRIMARY KEY,
            title TEXT,
            rank INTEGER
        );
    ''')
    
    # Insert sample data
    movies = test_config['test_config']['test_data']['movies']
    for movie in movies:
        conn.execute('''
            INSERT INTO media (tmdb_id, title, media_type, poster_url, overview, release_date, runtime, vote_average)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            movie['tmdb_id'], movie['title'], movie['media_type'],
            movie['poster_url'], movie['overview'], movie['release_date'],
            movie['runtime'], movie['vote_average']
        ))
        
        conn.execute('''
            INSERT INTO featured_movies (tmdb_id, title, rank)
            VALUES (?, ?, ?)
        ''', (movie['tmdb_id'], movie['title'], 1))
    
    tv_shows = test_config['test_config']['test_data']['tv_shows']
    for show in tv_shows:
        conn.execute('''
            INSERT INTO media (tmdb_id, title, media_type, poster_url, overview, release_date, vote_average)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            show['tmdb_id'], show['title'], show['media_type'],
            show['poster_url'], show['overview'], show['release_date'],
            show['vote_average']
        ))
        
        conn.execute('''
            INSERT INTO featured_tv (tmdb_id, title, rank)
            VALUES (?, ?, ?)
        ''', (show['tmdb_id'], show['title'], 1))
    
    anime_list = test_config['test_config']['test_data']['anime']
    for anime in anime_list:
        conn.execute('''
            INSERT INTO anime (anilist_id, title_romaji, title_english, episodes, average_score, trending, genres, description, cover_url, start_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            anime['anilist_id'], anime['title_romaji'], anime['title_english'],
            anime['episodes'], anime['average_score'], anime['trending'],
            anime['genres'], anime['description'], anime['cover_url'],
            anime['start_date']
        ))
    
    conn.commit()
    
    yield db_path
    
    # Clean up
    conn.close()
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def mock_requests():
    """Mock requests for external API calls"""
    with patch('requests.get') as mock_get, patch('requests.post') as mock_post:
        # Mock TMDB API responses
        mock_get.return_value.ok = True
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [],
            "page": 1,
            "total_pages": 1
        }
        
        mock_post.return_value.ok = True
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "data": {
                "Page": {
                    "media": []
                }
            }
        }
        
        yield mock_get, mock_post


@pytest.fixture
def mock_genai():
    """Mock Google GenAI client"""
    with patch('app.google_ai.genai.Client') as mock_client:
        mock_instance = MagicMock()
        mock_instance.models.generate_content.return_value.text = "😊😍🎉👏"
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_comments(test_db, sample_users, test_config):
    """Create sample comments for testing"""
    user = sample_users[0]
    comments = []
    
    for comment_data in test_config['test_config']['test_data']['comments']:
        comment = Comment(
            content=comment_data['content'],
            timestamp=comment_data['timestamp'],
            user_id=user.id,
            episode_id=comment_data['episode_id'],
            media_title=comment_data['media_title']
        )
        db.session.add(comment)
        comments.append(comment)
    
    db.session.commit()
    return comments


# Utility fixtures
@pytest.fixture
def authenticated_request(client, auth_user):
    """Helper to make authenticated requests"""
    def _make_request(method, url, **kwargs):
        return getattr(client, method.lower())(url, **kwargs)
    return _make_request
