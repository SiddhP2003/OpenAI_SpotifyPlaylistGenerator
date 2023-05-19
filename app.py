import spotipy
from dotenv import dotenv_values
from spotipy.oauth2 import SpotifyOAuth
import pprint
import openai
import json
import argparse
import datetime
 # Sign up as a developer and register your app at https://developer.spotify.com/dashboard/applications

    # Step 1. Create an Application.

    # Step 2. Copy your Client ID and Client Secret.

	# Step 3. Click `Edit Settings`, add `http://localhost:9999` as as a "Redirect URI" 
	
	# Step 4. Click `Users and Access`. Add your Spotify account to the list of users (identified by your email address)

    # Spotipy Documentation
    # https://spotipy.readthedocs.io/en/2.22.1/#getting-started

def get_playlist(prompt, count=8):
	example_json = """
	[{"song": "Yesterday", "artist": "The Beatles"},
	{"song": "Someone Like You", "artist": "Adele"},
	{"song": "All I Want", "artist": "Kodaline"},
	{"song": "Everybody Hurts", "artist": "R.E.M."},
	{"song": "Hurt", "artist": "Johnny Cash"},
	{"song": "Miss You", "artist": "Blink-182"},
	{"song": "How to Save a Life", "artist": "The Fray"},
	{"song": "Fix You", "artist": "Coldplay"},
	{"song": "Tears in Heaven", "artist": "Eric Clapton"},
	{"song": "My Heart Will Go On", "artist": "Celine Dion"}]"""
	messages = [
		{"role": "system", "content": """You are a helpful playlist generating assistant. You should generate a list of songs and their artists according to a text prompt. 
		You should return a JSON array, where each element follows this format: {"song": <song_title>, "artist":<artist_name>}"""},
		{"role": "user", "content": "Generate a playlist of 10 songs based on this prompt: super sad songs"},
		{"role": "assistant", "content" : example_json},
		{"role": "user", "content": f"Generate a playlist of {count} songs based on this prompt: {prompt}"},
	]

	response = openai.ChatCompletion.create(
		messages=messages,
		model = "gpt-3.5-turbo",
		max_tokens=400


	)

	playlist = json.loads(response["choices"][0]["message"]["content"])
	return playlist

def add_songs_to_spotify(prompt, playlist):
	sp = spotipy.Spotify(
	auth_manager = SpotifyOAuth(
		client_id= config["SPOTIFY_CLIENT_ID"],
		client_secret= config["SPOTIFY_CLIENT_SECRET"],
		redirect_uri="http://localhost:9999",
		scope="playlist-modify-private"

	)
	)

	current_user = sp.current_user()
	track_ids = []
	assert current_user is not None

	for item in playlist:
		artist, song = item["artist"], item["song"]
		query = f"{song} {artist}"
		search_results = sp.search(q=query, type="track", limit=10)
		track_ids.append(search_results["tracks"]["items"][0]["id"])

	# search_results = sp.search(q="Uptown Funk", type="track", limit=10)

	# tracks = [search_results["tracks"]["items"][0]["id"]]

	created_playlist = sp.user_playlist_create(
		current_user["id"],
		public=False,
		name=f"{prompt} ({datetime.datetime.now().strftime('%c')})",
	)
	sp.user_playlist_add_tracks(current_user["id"], created_playlist["id"], track_ids)
	print(playlist)

parser = argparse.ArgumentParser(description="Simple command line song utility")
parser.add_argument("-p", type=str, help="The prompt to describe the playlist")
parser.add_argument("-n", type=int, help="The number of songs to add to the playlist", default=8)
parser.add_argument("-envfile", type=str, default=".env", required=False, help='"A dotenv file with your environment variables: "SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "OPENAI_API_KEY"')
args = parser.parse_args()
config = dotenv_values(".env")
if any([x not in config for x in ("SPOTIFY_CLIENT_ID", "SPOTIFY_CLIENT_SECRET", "OPENAI_API_KEY")]):
	raise ValueError("Error: missing environment variables. Please check your env file.")
if args.n not in range (1,50):
	raise ValueError("Error: n should be between 0 and 50")

openai.api_key = config["OPENAI_API_KEY"]

playlist_prompt = args.p
count = args.n
playlist = get_playlist(playlist_prompt,count)
add_songs_to_spotify(playlist_prompt, playlist)





