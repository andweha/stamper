import requests
import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

BASE_URL = "https://api.themoviedb.org/3"
IMG_BASE_URL = "https://image.tmdb.org/t/p/w780"

# Fetch multiple pages of popular movies or TV shows
def fetch_popular(media_type="movie", pages=1):
    results = []
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/{media_type}/popular"
        response = requests.get(
            url, params={"api_key": TMDB_API_KEY, "page": page})
        response.raise_for_status()
        results.extend(response.json()["results"])
        
    return results

def fetch_featured(media_type="movie", pages=2, count=100):
    results = []
    for page in range(1, pages + 1):
        url = f"{BASE_URL}/trending/{media_type}/day"
        response = requests.get(
            url, params={"api_key": TMDB_API_KEY, "page": page})
        response.raise_for_status()
        results.extend(response.json()["results"][:count])

    return results

# Extract necessary fields from TMDb movie/TV show data
def parse_tmdb_items(items, media_type, include_rank=False):
    parsed = []

    # For movies, get the runtime
    for i, item in enumerate(items):
        runtime = None
        if media_type == "movie":
            movie_url = f"{BASE_URL}/movie/{item['id']}"
            response = requests.get(
                movie_url, params={"api_key": TMDB_API_KEY})
            if response.ok:
                details = response.json()
                runtime = details.get("runtime")

        entry = {
                "tmdb_id": item["id"],
                "title": item.get("title") or item.get("name"),
                "media_type": media_type,
                "poster_url": (
                    IMG_BASE_URL +
                    item["poster_path"] if item.get("poster_path") else None),
                "overview": item.get(
                    "overview",
                    ""),
                "release_date": item.get("release_date") or item.get("first_air_date"),
                "runtime": runtime,
                "vote_average": item.get("vote_average"),
            }
        
        if include_rank:
            entry["rank"] = i+1  # Rank starts from 1

        parsed.append(entry)
    return parsed

# Fetch all seasons of a particular TV show
def fetch_tv_seasons(tv_id):
    url = f"{BASE_URL}/tv/{tv_id}"
    response = requests.get(url, params={"api_key": TMDB_API_KEY})
    response.raise_for_status()
    return response.json().get("seasons", [])

# Extract necessary fields from TV show seasons data
def parse_seasons(tv_id, title, seasons_raw):
    seasons = []
    for season in seasons_raw:
        seasons.append(
            {
                "season_id": f"{tv_id}-{season['season_number']}",
                "tv_id": tv_id,
                "title": title,
                "season_number": season["season_number"],
                "name": season.get("name"),
                "overview": season.get("overview"),
                "poster_url": (
                    IMG_BASE_URL + season["poster_path"]
                    if season.get("poster_path")
                    else None
                ),
                "air_date": season.get("air_date"),
                "episode_count": season.get("episode_count"),
                "vote_average": season.get("vote_average"),
            }
        )
    return seasons

# Fetch all episodes for a particular TV show season
def fetch_season_episodes(tv_id, season_number):
    url = f"{BASE_URL}/tv/{tv_id}/season/{season_number}"
    response = requests.get(url, params={"api_key": TMDB_API_KEY})
    response.raise_for_status()
    return response.json().get("episodes", [])

# Extract necessary fields from TV show episodes data
def parse_episodes(tv_id, season_num, season_id, episodes_raw):
    episodes = []
    for episode in episodes_raw:
        episodes.append(
            {
                "episode_id": episode["id"],
                "season_id": season_id,
                "tv_id": tv_id,
                "season_number": season_num,
                "episode_number": episode["episode_number"],
                "episode_name": episode.get("name"),
                "overview": episode.get("overview"),
                "air_date": episode.get("air_date"),
                "runtime": episode.get("runtime"),
                "vote_average": episode.get("vote_average"),
                "still_url": (
                    IMG_BASE_URL + episode["still_path"]
                    if episode.get("still_path")
                    else None
                ),
            }
        )
    return episodes

# Take all the episode data and store them in db
def generate_episode_entries(tv):
    season_data = []
    episode_data = []
    for show in tv:
        tv_id = show["tmdb_id"]
        title = show["title"]

        seasons_raw = fetch_tv_seasons(tv_id)
        seasons = parse_seasons(tv_id, title, seasons_raw)
        season_data.extend(seasons)

        for season in seasons:
            season_num = season["season_number"]
            season_id = season["season_id"]

            episodes_raw = fetch_season_episodes(tv_id, season_num)
            episodes = parse_episodes(tv_id, season_num, season_id, episodes_raw)
            episode_data.extend(episodes)
            
    return season_data, episode_data

def main():
    featured_movies = parse_tmdb_items(fetch_featured("movie", 3), "movie", include_rank=True)
    featured_tv = parse_tmdb_items(fetch_featured("tv", 3), "tv", include_rank=True)

    popular_movies = parse_tmdb_items(fetch_popular("movie", 1), "movie")
    popular_tv_shows = parse_tmdb_items(fetch_popular("tv", 1), "tv")

    seasons_data, episodes_data = generate_episode_entries(popular_tv_shows)

    return featured_movies, featured_tv, popular_movies, popular_tv_shows, seasons_data, episodes_data

if __name__ == "__main__":
    main()
