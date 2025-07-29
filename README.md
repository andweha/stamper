# Stamper

### Table of Contents
- [General Info](#general-info)
- [Features](#features)
- [Technologies](#technologies)
- [Setup](#setup)
- [Usage](#usage)
- [Workflows](#workflows)

### General Info
**Stamper** is a social platform where users can post timestamped comments while watching a movie, show, or anime, creating a space
to share reactions in real time. Whether it's shock at a plot twist or laughter at a particular scene, these moment-specific comments
create a shared experience that enhances rather than interrupts what you're watching.
    
### Features
- **Timestamped Comments** - Comments appear at the moment they were written, synced to runtime.
- **Emoji Summaries** - Powered by Gemini, summarizing comment sentiment and mood.
- **Simulated Playback** - A custom playback system to sync comment display.
- **User Authentication** - Users must log in to post comments.
- **Toggle Comments** - Show or hide comments.

### Technologies
This project is created with:
- Python (Flask)
- HTML/CSS/JavaScript
- Jinja2
- [TMDb API](https://developer.themoviedb.org/docs/getting-started)
- [Google GenAI API](https://ai.google.dev/)
- [AniList API](https://docs.anilist.co/)
- [Tenor API](https://tenor.com/gifapi)
- SQLite3
- dotenv


### Setup
In the terminal:
``` bash
# Clone the repository
git clone https://github.com/jalenjaloney/stamper.git
cd stamper/

# Install Python dependencies
pip install -r requirements.txt
```

Create a .env file in the root directory and add your API keys
```env
# Example .env file
TMDB_API_KEY=your_tmdb_key
GENAI_KEY=your_genai_key
TENOR_API_KEY=your_tenor_key
```

### Usage
The project is deployed on PythonAnywhere: https://jalenseotechdev.pythonanywhere.com/

### Workflows
[![Check Style](https://github.com/jalenjaloney/Civic-Compass/actions/workflows/stylecheck.yaml/badge.svg)](https://github.com/jalenjaloney/Civic-Compass/actions/workflows/stylecheck.yaml)
[![Tests](https://github.com/jalenjaloney/Civic-Compass/actions/workflows/tests.yaml/badge.svg)](https://github.com/jalenjaloney/Civic-Compass/actions/workflows/tests.yaml)
