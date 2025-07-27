import sqlite3
import os  
from dotenv import load_dotenv
from tmdb import main as fetch_media_data
from anilist import main as fetch_anime_data

MEDIA_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "media.db"))

def insert_many_rows(conn, table, columns, rows):
    #rows: list of tuples representing each row's data

    if not rows:
        return
    
    # Create a string of '?' placeholders matching the number of columns
    # Used for safely inserting values into the SQL query
    placeholders = ', '.join(['?'] * len(columns))
    column_names = ', '.join(columns)

    conn.executemany(
        f"INSERT OR REPLACE INTO {table} ({column_names}) VALUES ({placeholders})",
        rows
    )
    conn.commit()

def create_media_db(
    featured_movies, # featured movies
    featured_tv,     # featured tv shows
    media_data,      # movies + tv shows
    seasons_data,    # all seasons
    episodes_data,   # all episodes
    anime_data,      # anime list
    anime_eps_data,  # anime episodes
    db_path=MEDIA_DB_PATH
):

    # Function to convert a API response data into tuples for SQL insertion
    def dicts_to_rows(data, columns):
        rows = []
        for item in data:
            row = []
            for col in columns:
                row.append(item.get(col))
            rows.append(tuple(row))
        return rows
    
    # If the database already exists, remove it to start fresh
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)

    # FEATURED_MOVIES table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS featured_movies (
        tmdb_id INTEGER PRIMARY KEY,
        title TEXT,
        poster_url TEXT,
        rank INTEGER
    )
    """)
    featured_movie_cols = ["tmdb_id", "title", "poster_url", "rank"]
    featured_movie_rows = dicts_to_rows(featured_movies, featured_movie_cols)
    insert_many_rows(conn, "featured_movies", featured_movie_cols, featured_movie_rows)

    # FEATURED_TV table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS featured_tv (
        tmdb_id INTEGER PRIMARY KEY,
        title TEXT,
        poster_url TEXT,
        rank INTEGER
    )
    """)
    featured_tv_cols = ["tmdb_id", "title", "poster_url", "rank"]
    featured_tv_rows = dicts_to_rows(featured_tv, featured_tv_cols)
    insert_many_rows(conn, "featured_tv", featured_tv_cols, featured_tv_rows)

    # MEDIA table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS media (
        tmdb_id INTEGER PRIMARY KEY,
        title TEXT,
        media_type TEXT,
        poster_url TEXT,
        overview TEXT,
        release_date TEXT,
        runtime INTEGER,
        vote_average REAL
    )
    """)
    media_cols = ["tmdb_id", "title", "media_type", "poster_url", "overview", "release_date", "runtime", "vote_average"]
    media_rows = dicts_to_rows(media_data, media_cols)
    insert_many_rows(conn, "media", media_cols, media_rows)

    # SEASONS table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS seasons (
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
    )
    """)
    season_cols = ["season_id", "tv_id", "title", "season_number", "name", "overview", "poster_url", "air_date", "episode_count", "vote_average"]
    season_rows = dicts_to_rows(seasons_data, season_cols)
    insert_many_rows(conn, "seasons", season_cols, season_rows)

    # EPISODES table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS episodes (
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
    )
    """)
    episode_cols = ["episode_id", "season_id", "tv_id", "season_number", "episode_number", "episode_name", "overview", "air_date", "runtime", "vote_average", "still_url"]
    episode_rows = dicts_to_rows(episodes_data, episode_cols)
    insert_many_rows(conn, "episodes", episode_cols, episode_rows)

    # ANIME table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS anime (
        anilist_id INTEGER PRIMARY KEY,
        title_romaji TEXT,
        title_english TEXT,
        episodes INTEGER,
        duration INTEGER,
        averageScore INTEGER,
        trending INTEGER,
        genres TEXT,
        description TEXT,
        coverImage TEXT,
        start_date TEXT
    )
    """)
    anime_cols = ["anilist_id", "title_romaji", "title_english", "episodes", "duration", "averageScore", "trending", "genres", "description", "coverImage", "start_date"]
    anime_rows = dicts_to_rows(anime_data, anime_cols)
    insert_many_rows(conn, "anime", anime_cols, anime_rows)

    # ANIME_EP table
    conn.execute("""
    CREATE TABLE IF NOT EXISTS anime_ep (
        episode_id INTEGER PRIMARY KEY,
        anilist_id INTEGER,
        episode_title TEXT,
        air_date TEXT,
        description TEXT
    )
    """)
    anime_ep_cols = ["episode_id", "anilist_id", "episode_title", "air_date", "description"]
    anime_ep_rows = dicts_to_rows(anime_eps_data, anime_ep_cols)
    insert_many_rows(conn, "anime_ep", anime_ep_cols, anime_ep_rows)

    conn.close()



def main():
    featured_movies, featured_tv, popular_movies, popular_tv_shows, seasons_data, episodes_data = fetch_media_data()
    anime_data, anime_eps_data = fetch_anime_data()

    create_media_db(
        featured_movies=featured_movies,
        featured_tv=featured_tv,
        media_data=popular_movies + popular_tv_shows,
        seasons_data=seasons_data,
        episodes_data=episodes_data,
        anime_data=anime_data,
        anime_eps_data=anime_eps_data
    )

if __name__ == "__main__":
    main()
