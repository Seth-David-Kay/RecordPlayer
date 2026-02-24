import sys
from dotenv import set_key
from mfrc522 import SimpleMFRC522
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler
import spotify_uri

ENV_FILE = ".env"

def set_up_spotify_credentials():
    client_id = input("Enter Spotify Client ID: ").strip()
    client_secret = input("Enter Spotify Client Secret: ").strip()
    redirect_uri = input("Enter Redirect URI: ").strip()

    cache_handler = MemoryCacheHandler()
    auth = SpotifyOAuth(
        scope = 'user-read-playback-state,user-modify-playback-state,user-read-recently-played',
        client_id = client_id,
        client_secret = client_secret,
        redirect_uri = redirect_uri,
        open_browser = False,
        cache_handler = cache_handler
    )
    auth.get_access_token(as_dict=False)
    token_info = cache_handler.get_cached_token()
    if not token_info or not token_info.get('refresh_token'):
        sys.exit("Error: Unable to get Spotify refresh token.")
    refresh_token = token_info['refresh_token']

    set_key(ENV_FILE, "SPOTIFY_CLIENT_ID", client_id)
    set_key(ENV_FILE, "SPOTIFY_CLIENT_SECRET", client_secret)
    set_key(ENV_FILE, "SPOTIFY_REFRESH_TOKEN", refresh_token)
    set_key(ENV_FILE, "SPOTIFY_REDIRECT_URI", redirect_uri)
    print("Spotify credentials set.")
    # This is the name on the spotify app that spotify will default play to if no other device is currently active
    default_device_id = input("Enter Your Preffered Default Device ID")
    set_key(ENV_FILE, "DEFAULT_DEVICE_ID", default_device_id)
    sonos_ip = input("Enter Your Preffered Sonos Device Name")
    set_key(ENV_FILE, "SONOS_DEVICE_IP", sonos_ip)

def write_rfid_tags():
    rfid = SimpleMFRC522()

    while True:
        print(f"Enter spotify track, artist, album, or playlist uri:")
        # Get user input as a string
        uri = input("Spotify URI: ")

        if not uri or not uri.startswith("spotify:") or uri.split(":")[1] not in ["track", "album", "playlist", "artist"]:
            print("Invalid URI, spotify URI's must be in the format spotify:{track/album/playlist/artist}:{id}")
        else:
            print(f"Place the tag on the reader")
            rfid.write(uri)
            print(f"Write finished")

        print("Please choose an option:")
        print("1. Add another RFID tag")
        print("2. Exit")
        choice = input("Enter your choice: ")
        if choice == "2":
            break

def spotify_uri_from_url():
    url = input("Enter the spotify link: ")
    try:
        spotify_object = spotify_uri.parse(url)
        uri = spotify_object.toURI()
        print(uri)
    except Exception as e:
        print(f"Incorrect url {e}")

def read_rfid_tags():
    rfid = SimpleMFRC522()

    while True:
        print("Please scan RFID tag:")
        rfid_id, rfid_text = rfid.read()

        if not rfid_text or not rfid_text.startswith("spotify:") or rfid_text.split(":")[1] not in ["track", "album", "playlist", "artist"]:
            print(f"URI {rfid_text} is not valid.")
        else:
            print(f"URI {rfid_text} is valid.")

        print("Please choose an option:")
        print("1. Read another RFID tag")
        print("2. Exit")
        choice = input("Enter your choice: ")
        if choice == "2":
            break

def get_user_choice():
    actions = {
        "1": ("Setup Spotify credentials", set_up_spotify_credentials),
        "2": ("Write RFID tags", write_rfid_tags),
        "3": ("Read RFID tags", read_rfid_tags),
        "4": ("Get spotify uri", spotify_uri_from_url)
    }

    exit_key = str(len(actions) + 1)

    while True:
        print("\nPlease choose an option:")
        for key, (label, _) in actions.items():
            print(f"{key}. {label}")
        print(f"{exit_key}. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == exit_key:
            print("Exiting the program.")
            break

        action = actions.get(choice)
        if not action:
            print("Invalid choice. Please try again.")
            continue

        label, func = action
        print(f"You selected: {label}")
        func()


if __name__ == "__main__":
    get_user_choice()
