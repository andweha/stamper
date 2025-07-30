import pytest
from unittest.mock import patch, MagicMock
import requests
from app.tmdb import fetch_popular, fetch_featured, fetch_tv_seasons, fetch_season_episodes
from app.anilist import fetch_anime, fetch_episodes
from app.tenor import search_gif, featured_gifs
from app.cache_tmdb import fetch_and_cache_movie, fetch_and_cache_show


class TestTMDBAPI:
    """Test TMDB API integration"""
    
    @patch('requests.get')
    def test_fetch_popular_movies_success(self, mock_get):
        """Test successful fetch of popular movies"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 12345,
                    "title": "Popular Movie",
                    "overview": "A popular movie",
                    "poster_path": "/poster.jpg",
                    "release_date": "2023-01-01",
                    "vote_average": 8.5
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_popular("movie", pages=1)
        
        assert len(result) == 1
        assert result[0]["id"] == 12345
        assert result[0]["title"] == "Popular Movie"
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_fetch_popular_multiple_pages(self, mock_get):
        """Test fetching multiple pages of popular content"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [{"id": 1, "title": "Movie 1"}]
        }
        mock_get.return_value = mock_response
        
        result = fetch_popular("movie", pages=3)
        
        # Should make 3 API calls for 3 pages
        assert mock_get.call_count == 3
        assert len(result) == 3  # One result per page
    
    @patch('requests.get')
    def test_fetch_popular_api_error(self, mock_get):
        """Test handling of TMDB API errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            fetch_popular("movie", pages=1)
    
    @patch('requests.get')
    def test_fetch_featured_trending(self, mock_get):
        """Test fetching featured/trending content"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [
                {"id": 1, "title": "Trending Movie 1"},
                {"id": 2, "title": "Trending Movie 2"}
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_featured("movie", pages=1, count=2)
        
        assert len(result) == 2
        mock_get.assert_called_once()
        # Verify the correct endpoint is called
        args, kwargs = mock_get.call_args
        assert "trending/movie/day" in args[0]
    
    @patch('requests.get')
    def test_fetch_tv_seasons_success(self, mock_get):
        """Test fetching TV show seasons"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "seasons": [
                {
                    "season_number": 1,
                    "name": "Season 1",
                    "overview": "First season",
                    "poster_path": "/season1.jpg",
                    "air_date": "2023-01-01",
                    "episode_count": 10
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_tv_seasons(12345)
        
        assert len(result) == 1
        assert result[0]["season_number"] == 1
        assert result[0]["name"] == "Season 1"
    
    @patch('requests.get')
    def test_fetch_season_episodes_success(self, mock_get):
        """Test fetching season episodes"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "episodes": [
                {
                    "id": 111,
                    "episode_number": 1,
                    "name": "Pilot",
                    "overview": "First episode",
                    "air_date": "2023-01-01",
                    "runtime": 45,
                    "still_path": "/still1.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = fetch_season_episodes(12345, 1)
        
        assert len(result) == 1
        assert result[0]["id"] == 111
        assert result[0]["episode_number"] == 1


class TestAniListAPI:
    """Test AniList API integration"""
    
    @patch('requests.post')
    def test_fetch_anime_success(self, mock_post):
        """Test successful fetch of anime data"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "Page": {
                    "media": [
                        {
                            "id": 11111,
                            "title": {
                                "romaji": "Test Anime",
                                "english": "Test Anime EN"
                            },
                            "episodes": 24,
                            "averageScore": 85,
                            "trending": 100,
                            "genres": ["Action", "Drama"],
                            "description": "Test anime description",
                            "coverImage": {
                                "large": "https://example.com/cover.jpg"
                            },
                            "startDate": {
                                "year": 2023,
                                "month": 4,
                                "day": 15
                            }
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = fetch_anime(pages=1)
        
        assert len(result) == 1
        assert result[0]["id"] == 11111
        assert result[0]["title"]["romaji"] == "Test Anime"
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_fetch_anime_multiple_pages(self, mock_post):
        """Test fetching multiple pages of anime"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "Page": {
                    "media": [{"id": 1, "title": {"romaji": "Anime 1"}}]
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = fetch_anime(pages=2)
        
        # Should make 2 API calls
        assert mock_post.call_count == 2
        assert len(result) == 2
    
    @patch('requests.post')
    def test_fetch_anime_api_error(self, mock_post):
        """Test handling of AniList API errors"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("API Error")
        mock_post.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            fetch_anime(pages=1)
    
    @patch('requests.post')
    def test_fetch_episodes_success(self, mock_post):
        """Test fetching anime episodes"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "Media": {
                    "id": 11111,
                    "duration": 24,
                    "streamingEpisodes": [
                        {
                            "title": "Episode 1",
                            "thumbnail": "https://example.com/ep1.jpg"
                        },
                        {
                            "title": "Episode 2", 
                            "thumbnail": "https://example.com/ep2.jpg"
                        }
                    ]
                }
            }
        }
        mock_post.return_value = mock_response
        
        result = fetch_episodes(11111)
        
        assert result["duration"] == 24
        assert len(result["streamingEpisodes"]) == 2
        assert result["streamingEpisodes"][0]["title"] == "Episode 1"
    
    @patch('requests.post')
    def test_fetch_episodes_no_data(self, mock_post):
        """Test fetching episodes when no data available"""
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "Media": None
            }
        }
        mock_post.return_value = mock_response
        
        result = fetch_episodes(11111)
        
        assert result["streamingEpisodes"] == []
        assert result["duration"] is None


class TestTenorAPI:
    """Test Tenor GIF API integration"""
    
    @patch('requests.get')
    def test_search_gif_success(self, mock_get):
        """Test successful GIF search"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "media_formats": {
                        "gif": {
                            "url": "https://tenor.com/gif1.gif"
                        }
                    }
                },
                {
                    "media_formats": {
                        "gif": {
                            "url": "https://tenor.com/gif2.gif"
                        }
                    }
                }
            ],
            "next": "next_page_token"
        }
        mock_get.return_value = mock_response
        
        result = search_gif("funny", limit=2)
        
        assert "gifs" in result
        assert "next" in result
        assert len(result["gifs"]) == 2
        assert result["gifs"][0] == "https://tenor.com/gif1.gif"
        assert result["next"] == "next_page_token"
    
    @patch('requests.get')
    def test_search_gif_api_error(self, mock_get):
        """Test GIF search API error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_get.return_value = mock_response
        
        result = search_gif("funny")
        
        assert result == {"gifs": [], "next": None}
    
    @patch('requests.get')
    def test_search_gif_empty_query(self, mock_get):
        """Test GIF search with empty query"""
        result = search_gif("")
        
        assert result == []
        mock_get.assert_not_called()
    
    @patch('requests.get')
    def test_featured_gifs_success(self, mock_get):
        """Test fetching featured GIFs"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {
                    "media_formats": {
                        "gif": {
                            "url": "https://tenor.com/featured1.gif"
                        }
                    }
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = featured_gifs(limit=1)
        
        assert len(result) == 1
        assert result[0] == "https://tenor.com/featured1.gif"
    
    @patch('requests.get')
    def test_featured_gifs_api_error(self, mock_get):
        """Test featured GIFs API error"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        result = featured_gifs()
        
        assert result == []


class TestCachingFunctions:
    """Test database caching functions"""
    '''
    @patch('requests.get')
    def test_fetch_and_cache_movie_success(self, mock_get, media_db):
        """Test fetching and caching movie data"""
        import sqlite3
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "id": 12345,
            "title": "Test Movie",  # Change this to match your test data
            "poster_path": "/poster.jpg",
            "overview": "A test movie",
            "release_date": "2023-01-01",
            "runtime": 120,
            "vote_average": 8.5
        }
        mock_get.return_value = mock_response

        conn = sqlite3.connect(media_db)
        result = fetch_and_cache_movie(12345, conn)
        
        # Verify movie was cached in database
        cursor = conn.execute("SELECT * FROM media WHERE tmdb_id = 12345")
        cached_movie = cursor.fetchone()
        assert cached_movie is not None
        assert cached_movie[1] == "Test Movie"  # Changed expectation
        assert cached_movie[2] == "movie"
        conn.close()
    
    @patch('requests.get')
    def test_fetch_and_cache_show_success(self, mock_get, media_db):
        """Test fetching and caching TV show data"""
        import sqlite3
        
        # Mock main TV show response
        tv_response = MagicMock()
        tv_response.raise_for_status.return_value = None
        tv_response.json.return_value = {
            "id": 67890,
            "name": "Cached TV Show",
            "poster_path": "/tv_poster.jpg",
            "overview": "A cached TV show",
            "first_air_date": "2023-01-01",
            "vote_average": 7.8,
            "seasons": [
                {
                    "season_number": 1,
                    "name": "Season 1",
                    "overview": "First season",
                    "poster_path": "/s1.jpg",
                    "air_date": "2023-01-01",
                    "episode_count": 10
                }
            ]
        }
        
        # Mock season episodes response
        season_response = MagicMock()
        season_response.ok = True
        season_response.json.return_value = {
            "episodes": [
                {
                    "id": 111,
                    "episode_number": 1,
                    "name": "Pilot",
                    "overview": "First episode",
                    "air_date": "2023-01-01",
                    "runtime": 45,
                    "vote_average": 8.0,
                    "still_path": "/still1.jpg"
                }
            ]
        }
        
        # Configure mock to return different responses for different URLs
        def mock_get_side_effect(url, **kwargs):
            if "/tv/67890/season/" in url:
                return season_response
            else:
                return tv_response
        
        mock_get.side_effect = mock_get_side_effect
        
        conn = sqlite3.connect(media_db)
        result = fetch_and_cache_show(67890, conn)
        
        # Verify show was cached
        cursor = conn.execute("SELECT * FROM media WHERE tmdb_id = 67890")
        cached_show = cursor.fetchone()
        assert cached_show is not None
        assert cached_show[1] == "Cached TV Show"
        
        # Verify season was cached
        cursor = conn.execute("SELECT * FROM seasons WHERE tv_id = 67890")
        cached_season = cursor.fetchone()
        assert cached_season is not None
        
        # Verify episode was cached
        cursor = conn.execute("SELECT * FROM episodes WHERE tv_id = 67890")
        cached_episode = cursor.fetchone()
        assert cached_episode is not None
        
        conn.close()
    '''


class TestAPIRateLimit:
    """Test API rate limiting and error handling"""
    
    @patch('time.sleep')
    @patch('requests.post')
    def test_anilist_rate_limiting(self, mock_post, mock_sleep):
        """Test AniList API respects rate limits"""
        from app.anilist import generate_episodes
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "data": {
                "Media": {
                    "streamingEpisodes": []
                }
            }
        }
        mock_post.return_value = mock_response
        
        # Test data with multiple anime
        anime_data = [
            {"anilist_id": 1, "title_romaji": "Anime 1"},
            {"anilist_id": 2, "title_romaji": "Anime 2"}
        ]
        
        generate_episodes(anime_data)
        
        # Should sleep between requests for rate limiting
        assert mock_sleep.call_count == 2  # Once per anime
        mock_sleep.assert_called_with(1.8)
    
    @patch('requests.get')
    def test_tmdb_api_timeout(self, mock_get):
        """Test TMDB API timeout handling"""
        mock_get.side_effect = requests.Timeout("Request timed out")
        
        with pytest.raises(requests.Timeout):
            fetch_popular("movie", pages=1)
    
    @patch('requests.post')
    def test_anilist_connection_error(self, mock_post):
        """Test AniList connection error handling"""
        mock_post.side_effect = requests.ConnectionError("Connection failed")
        
        with pytest.raises(requests.ConnectionError):
            fetch_anime(pages=1)