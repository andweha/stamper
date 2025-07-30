import pytest
from unittest.mock import patch, MagicMock
from app.flask_app import parse_timestamp_string, seconds_to_hours_minutes
from app.anilist import format_start_date, extract_ep_num, parse_anime
from app.tmdb import parse_tmdb_items
from app.google_ai import get_comments, summarize_comments
from app.history import add_to_history
from app.models import History, db


class TestTimestampUtilities:
    """Test timestamp parsing and conversion utilities"""
    
    def test_parse_timestamp_string_mm_ss(self):
        """Test parsing MM:SS format"""
        assert parse_timestamp_string("05:30") == 330  # 5*60 + 30
        assert parse_timestamp_string("10:45") == 645  # 10*60 + 45
        assert parse_timestamp_string("00:15") == 15   # 0*60 + 15
    
    def test_parse_timestamp_string_hh_mm_ss(self):
        """Test parsing HH:MM:SS format"""
        assert parse_timestamp_string("1:05:30") == 3930   # 1*3600 + 5*60 + 30
        assert parse_timestamp_string("2:10:15") == 7815   # 2*3600 + 10*60 + 15
        assert parse_timestamp_string("0:05:30") == 330    # 0*3600 + 5*60 + 30
    
    def test_parse_timestamp_string_invalid(self):
        """Test parsing invalid timestamp formats"""
        with pytest.raises(ValueError):
            parse_timestamp_string("5")
        
        with pytest.raises(ValueError):
            parse_timestamp_string("5:")
        
        with pytest.raises(ValueError):
            parse_timestamp_string("5:30:15:10")
        
        with pytest.raises(ValueError):
            parse_timestamp_string("abc:def")
    
    def test_seconds_to_hours_minutes(self):
        """Test converting seconds to hours and minutes"""
        # Test various second values
        assert seconds_to_hours_minutes(3600) == (1, 0)    # 1 hour
        assert seconds_to_hours_minutes(3660) == (1, 1)    # 1 hour 1 minute
        assert seconds_to_hours_minutes(7230) == (2, 0)    # 2 hours 30 seconds -> (2, 0)
        assert seconds_to_hours_minutes(90) == (0, 1)      # 1 minute 30 seconds -> (0, 1)
        assert seconds_to_hours_minutes(30) == (0, 0)      # 30 seconds -> (0, 0)
        assert seconds_to_hours_minutes(0) == (0, 0)       # 0 seconds
    
    def test_seconds_to_hours_minutes_none(self):
        """Test converting None to hours and minutes"""
        assert seconds_to_hours_minutes(None) == (0, 0)
    
    def test_seconds_to_hours_minutes_large_values(self):
        """Test converting large second values"""
        assert seconds_to_hours_minutes(36000) == (10, 0)   # 10 hours
        assert seconds_to_hours_minutes(90000) == (25, 0)   # 25 hours


class TestAnilistUtilities:
    """Test AniList-related utility functions"""
    
    def test_format_start_date_complete(self):
        """Test formatting complete start date"""
        start_date = {"year": 2023, "month": 4, "day": 15}
        assert format_start_date(start_date) == "04-15-2023"
    
    def test_format_start_date_year_month(self):
        """Test formatting start date with year and month only"""
        start_date = {"year": 2023, "month": 4, "day": None}
        assert format_start_date(start_date) == "04-2023"
    
    def test_format_start_date_year_only(self):
        """Test formatting start date with year only"""
        start_date = {"year": 2023, "month": None, "day": None}
        assert format_start_date(start_date) == "2023"
    
    def test_format_start_date_no_year(self):
        """Test formatting start date with no year"""
        start_date = {"year": None, "month": 4, "day": 15}
        assert format_start_date(start_date) == ""
    
    def test_extract_ep_num_standard(self):
        """Test extracting episode numbers from standard titles"""
        assert extract_ep_num("Episode 1") == 1
        assert extract_ep_num("Episode 12") == 12
        assert extract_ep_num("Ep 5") == 5
        assert extract_ep_num("ep 23") == 23
    
    def test_extract_ep_num_leading_number(self):
        """Test extracting episode numbers from titles with leading numbers"""
        assert extract_ep_num("1 - The Beginning") == 1
        assert extract_ep_num("12 - The End") == 12
        assert extract_ep_num("5") == 5
    
    def test_extract_ep_num_no_number(self):
        """Test extracting episode numbers from titles without numbers"""
        assert extract_ep_num("The Beginning") == 0
        assert extract_ep_num("Special Episode") == 0
        assert extract_ep_num("") == 0
        assert extract_ep_num(None) == 0
    
    def test_parse_anime_basic(self):
        """Test parsing basic anime data"""
        anime_raw = [{
            "id": 12345,
            "title": {"romaji": "Test Anime", "english": "Test Anime EN"},
            "episodes": 24,
            "averageScore": 85,
            "trending": 100,
            "genres": ["Action", "Drama"],
            "description": "A test anime description",
            "coverImage": {"large": "https://example.com/cover.jpg"},
            "startDate": {"year": 2023, "month": 4, "day": 15}
        }]
        
        parsed = parse_anime(anime_raw)
        assert len(parsed) == 1
        
        anime = parsed[0]
        assert anime["anilist_id"] == 12345
        assert anime["title_romaji"] == "Test Anime"
        assert anime["title_english"] == "Test Anime EN"
        assert anime["episodes"] == 24
        assert anime["average_score"] == "8.5"
        assert anime["trending"] == 100
        assert anime["genres"] == "Action, Drama"
        assert anime["description"] == "A test anime description"
        assert anime["cover_url"] == "https://example.com/cover.jpg"
        assert anime["start_date"] == "04-15-2023"
    
    def test_parse_anime_html_description(self):
        """Test parsing anime with HTML in description"""
        anime_raw = [{
            "id": 12345,
            "title": {"romaji": "Test", "english": "Test"},
            "episodes": 12,
            "averageScore": 80,
            "trending": 50,
            "genres": ["Comedy"],
            "description": "<p>A test with <b>HTML</b> tags.<br>Second line.</p>(Source: Test Source)<br>Notes: Some notes",
            "coverImage": {"large": "https://example.com/cover.jpg"},
            "startDate": {"year": 2023, "month": 1, "day": 1}
        }]
        
        parsed = parse_anime(anime_raw)
        description = parsed[0]["description"]
        
        # Should remove HTML tags, source info, and notes
        assert "<p>" not in description
        assert "<b>" not in description
        assert "<br>" not in description
        assert "Source:" not in description
        assert "Notes:" not in description
        assert "A test with HTML tags." in description


class TestTMDBUtilities:
    """Test TMDB-related utility functions"""
    
    def test_parse_tmdb_items_movies(self):
        """Test parsing TMDB movie items"""
        items = [{
            "id": 12345,
            "title": "Test Movie",
            "poster_path": "/poster.jpg",
            "overview": "A test movie",
            "release_date": "2023-01-01",
            "vote_average": 8.5
        }]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"runtime": 120}
            mock_get.return_value = mock_response
            
            parsed = parse_tmdb_items(items, "movie")
            
            assert len(parsed) == 1
            movie = parsed[0]
            assert movie["tmdb_id"] == 12345
            assert movie["title"] == "Test Movie"
            assert movie["media_type"] == "movie"
            assert movie["runtime"] == 120
            assert movie["vote_average"] == 8.5
    
    def test_parse_tmdb_items_tv_shows(self):
        """Test parsing TMDB TV show items"""
        items = [{
            "id": 67890,
            "name": "Test TV Show",
            "poster_path": "/tv_poster.jpg",
            "overview": "A test TV show",
            "first_air_date": "2023-01-01",
            "vote_average": 7.8
        }]
        
        parsed = parse_tmdb_items(items, "tv")
        
        assert len(parsed) == 1
        show = parsed[0]
        assert show["tmdb_id"] == 67890
        assert show["title"] == "Test TV Show"
        assert show["media_type"] == "tv"
        assert show["runtime"] is None  # TV shows don't get runtime in this function
        assert show["vote_average"] == 7.8
    
    def test_parse_tmdb_items_with_rank(self):
        """Test parsing TMDB items with ranking"""
        items = [
            {"id": 1, "title": "Movie 1", "overview": "", "vote_average": 8.0},
            {"id": 2, "title": "Movie 2", "overview": "", "vote_average": 7.5}
        ]
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.ok = True
            mock_response.json.return_value = {"runtime": 120}
            mock_get.return_value = mock_response
            
            parsed = parse_tmdb_items(items, "movie", include_rank=True)
            
            assert parsed[0]["rank"] == 1
            assert parsed[1]["rank"] == 2


class TestGoogleAIUtilities:
    """Test Google AI utility functions"""
    
    def test_get_comments_with_data(self, test_db, sample_comments):
        """Test getting comments from database"""
        # Use the actual database path from the test
        db_path = test_db.get_bind().url.database
        
        comment_block = get_comments(12345, db_path)
        
        assert comment_block != ""
        assert "[05:00]" in comment_block  # 300 seconds = 5:00
        assert "[10:00]" in comment_block  # 600 seconds = 10:00
        assert "This is a test comment" in comment_block
    
    def test_get_comments_no_data(self, test_db):
        """Test getting comments when no comments exist"""
        db_path = test_db.get_bind().url.database
        
        comment_block = get_comments(99999, db_path)  # Non-existent media ID
        
        assert comment_block == ""
    
    def test_get_comments_time_formatting(self, test_db, sample_users):
        """Test comment timestamp formatting"""
        user = sample_users[0]
        
        # Create comment with different timestamp formats
        from app.models import Comment
        comment1 = Comment(
            content="Short timestamp",
            timestamp=65,  # 1:05
            user_id=user.id,
            episode_id=11111,
            media_title="Test"
        )
        comment2 = Comment(
            content="Long timestamp", 
            timestamp=3665,  # 1:01:05
            user_id=user.id,
            episode_id=11111,
            media_title="Test"
        )
        
        db.session.add_all([comment1, comment2])
        db.session.commit()
        
        db_path = test_db.get_bind().url.database
        comment_block = get_comments(11111, db_path)
        
        assert "[01:05]" in comment_block  # MM:SS format
        assert "[01:01:05]" in comment_block  # HH:MM:SS format
    
    @patch('app.google_ai.genai.Client')
    def test_summarize_comments(self, mock_client):
        """Test comment summarization"""
        mock_instance = MagicMock()
        mock_instance.models.generate_content.return_value.text = "😊😍🎉👏"
        mock_client.return_value = mock_instance
        
        comment_block = "[05:00] Great scene!\n[10:00] Amazing!"
        result = summarize_comments(comment_block)
        
        assert result == "😊😍🎉👏"
        mock_client.assert_called_once()


class TestHistoryUtilities:
    """Test history-related utility functions"""
    
    def test_add_to_history_new_entry(self, test_db, sample_users):
        """Test adding new history entry"""
        user = sample_users[0]
        
        add_to_history(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie",
            poster_url="https://example.com/poster.jpg"
        )
        
        history = History.query.filter_by(user_id=user.id, media_id=12345).first()
        assert history is not None
        assert history.media_type == "movie"
        assert history.title == "Test Movie"
        assert history.poster_url == "https://example.com/poster.jpg"
    
    def test_add_to_history_update_existing(self, test_db, sample_users):
        """Test updating existing history entry"""
        user = sample_users[0]
        
        # Add initial history entry
        initial_history = History(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie"
        )
        db.session.add(initial_history)
        db.session.commit()
        
        initial_time = initial_history.watched_at
        
        # Update the history
        add_to_history(
            user_id=user.id,
            media_type="movie",
            media_id=12345,
            title="Test Movie",
            poster_url="https://example.com/poster.jpg"
        )
        
        # Should update existing entry, not create new one
        history_count = History.query.filter_by(user_id=user.id, media_id=12345).count()
        assert history_count == 1
        
        updated_history = History.query.filter_by(user_id=user.id, media_id=12345).first()
        assert updated_history.watched_at > initial_time
    
    def test_add_to_history_different_media_types(self, test_db, sample_users):
        """Test adding history for different media types"""
        user = sample_users[0]
        
        # Add different media types
        add_to_history(user.id, "movie", 12345, "Movie", None)
        add_to_history(user.id, "tv", 67890, "TV Show", None)
        add_to_history(user.id, "anime", 11111, "Anime", None)
        
        history_entries = History.query.filter_by(user_id=user.id).all()
        assert len(history_entries) == 3
        
        media_types = [h.media_type for h in history_entries]
        assert "movie" in media_types
        assert "tv" in media_types
        assert "anime" in media_types


class TestDataValidationUtilities:
    """Test data validation and sanitization utilities"""
    
    def test_parse_anime_null_values(self):
        """Test parsing anime data with null values"""
        anime_raw = [{
            "id": 12345,
            "title": {"romaji": "Test", "english": None},
            "episodes": None,
            "averageScore": None,
            "trending": 50,
            "genres": [],
            "description": None,
            "coverImage": {"large": "https://example.com/cover.jpg"},
            "startDate": {"year": 2023, "month": None, "day": None}
        }]
        
        parsed = parse_anime(anime_raw)
        anime = parsed[0]
        
        assert anime["title_english"] is None
        assert anime["episodes"] is None
        assert anime["average_score"] is None
        assert anime["genres"] == ""  # Empty list becomes empty string
    
    def test_format_start_date_edge_cases(self):
        """Test start date formatting edge cases"""
        # Test with zero values
        assert format_start_date({"year": 2023, "month": 0, "day": 1}) == "2023"
        
        # Test with missing dictionary keys
        partial_date = {"year": 2023}
        assert format_start_date(partial_date) == "2023"
        
        # Test with empty dictionary
        assert format_start_date({}) == ""
    
    def test_extract_ep_num_edge_cases(self):
        """Test episode number extraction edge cases"""
        # Test with complex titles
        assert extract_ep_num("Episode 1: The Beginning") == 1
        assert extract_ep_num("Ep. 12 - Final Battle") == 12
        assert extract_ep_num("Special: Episode 0") == 0
        
        # Test case insensitive
        assert extract_ep_num("EPISODE 5") == 5
        assert extract_ep_num("episode 3") == 3
        
        # Test with extra spaces
        assert extract_ep_num("  Episode  10  ") == 10
    
    def test_seconds_to_hours_minutes_edge_cases(self):
        """Test time conversion edge cases"""
        # Test with float values (should convert to int)
        assert seconds_to_hours_minutes(3600.7) == (1, 0)
        assert seconds_to_hours_minutes(3660.9) == (1, 1)
        
        # Test with string that can be converted to int
        assert seconds_to_hours_minutes("3600") == (1, 0)


class TestErrorHandling:
    """Test error handling in utility functions"""
    
    def test_parse_timestamp_string_error_handling(self):
        """Test timestamp parsing error cases"""
        invalid_inputs = [
            "",           # Empty string
            ":",          # Just separator
            "60:30",      # Invalid minutes
            "10:60",      # Invalid seconds
            "abc:def",    # Non-numeric
            "10:30:45:20" # Too many parts
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises(ValueError):
                parse_timestamp_string(invalid_input)
    
    @patch('sqlite3.connect')
    def test_get_comments_database_error(self, mock_connect):
        """Test get_comments with database connection error"""
        mock_connect.side_effect = Exception("Database connection failed")
        
        with pytest.raises(Exception):
            get_comments(12345, "fake_path.db")
    
    @patch('app.google_ai.genai.Client')
    def test_summarize_comments_api_error(self, mock_client):
        """Test comment summarization with API error"""
        mock_client.side_effect = Exception("API connection failed")
        
        with pytest.raises(Exception):
            summarize_comments("Some comments")
    
    def test_add_to_history_database_error(self, test_db):
        """Test add_to_history with database commit error"""
        # This test would need to mock the database session to simulate an error
        # For now, we'll test with invalid data
        with pytest.raises(Exception):
            add_to_history(
                user_id=None,  # Invalid user_id
                media_type="movie",
                media_id=12345,
                title="Test Movie",
                poster_url=None
            )