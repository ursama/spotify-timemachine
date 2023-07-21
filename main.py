from bs4 import BeautifulSoup
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
import requests
import os
import spotipy

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')

if not CLIENT_SECRET or not CLIENT_ID or not REDIRECT_URI or type(CLIENT_SECRET) != str or type(CLIENT_ID) != str \
        or type(REDIRECT_URI) != str:
    print('error loading env variables')

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-private",
        cache_path="token.txt",
        show_dialog=True
    )
)

user_id = sp.current_user()["id"]

date = input("Which year do you want to travel to? Type the date in this format -> YYYY-MM-DD: ")
URL = f"https://www.billboard.com/charts/hot-100/{date}"
year = date.split("-")[0]
response = requests.get(url=URL).text
soup = BeautifulSoup(response, "html.parser")

song_titles = [song.getText().strip() for song in soup.select("li > h3")[:100]]
song_uris = []

for song in song_titles:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result['tracks']['items'][0]['uri']
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist_info = sp.user_playlist_create(
    user=user_id,
    name=f"{date} Billboard 100",
    public=False,
    description=f"Top 100 songs at {date} based on Billboard"
)

playlist_id = playlist_info["uri"]

sp.playlist_add_items(
    playlist_id=playlist_id,
    items=song_uris
)
