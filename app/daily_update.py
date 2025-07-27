import subprocess

print("Fetching new media data from TMDb and Anilist...")
subprocess.run(["python3", "app/create_media_db.py"], check=True)

print("Media database successfully updated.")