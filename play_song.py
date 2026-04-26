import spotipy
import os
import sys
from dotenv import load_dotenv
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth
from time import sleep

load_dotenv()
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
default_device_id = os.getenv("DEFAULT_DEVICE_ID")

if not all([client_id, client_secret, redirect_uri]):
	print("Error: spotify secrets are not set.")
	sys.exit(1)

if not all([client_id, client_secret, refresh_token, redirect_uri]):
	print("Error: spotify secrets are not set.")
	sys.exit(1)
auth = SpotifyOAuth(
	client_id=client_id,
	client_secret=client_secret,
	redirect_uri=refresh_token,
	scope='user-read-playback-state,user-modify-playback-state',
	open_browser=False,
	cache_handler=MemoryCacheHandler(),
)
auth.refresh_access_token(refresh_token)
sp = spotipy.Spotify(auth_manager=auth)

device_id = default_device_id
for device in sp.devices()['devices']:
	if device['is_active']:
		print(device['name'])
		print(device['id'])
		device_id = device['id']

# start
device_id = input()
sp.start_playback(device_id=device_id, context_uri='https://open.spotify.com/playlist/37i9dQZF1DXe7OsxgbX67u?si=319e33a5119d4933')
# sleep(2)
# pause
# current_song = sp.currently_playing()['item']['uri']
# sp.pause_playback()
# sleep(2)
# # resume
# sp.start_playback(device_id)
