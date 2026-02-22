import os
import RPi.GPIO as GPIO
import sys
from datetime import datetime, timedelta
from signal import pause
import spotipy
from dotenv import load_dotenv
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from mfrc522 import SimpleMFRC522
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

HALL_SENSOR_PIN = 17

class SpotifyController:
    def __init__(self):
        self.init_spotify_client()
        self.playback_cache = {}
        self.default_device_name = None

    def init_spotify_client(self):
        load_dotenv()

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.default_device_name = os.getenv("DEFAULT_DEVICE_NAME")

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
        self.sp = spotipy.Spotify(auth_manager=auth)

    def play(self, uri, doresume):
        print(f"Starting playback")
        if not uri:
            print(f"No uri scanned or passed in")
            return

        spotify_args = {}
        if uri.startswith("spotify:track:"):
            spotify_args["uris"] = [uri]
            if uri == self.playback_cache.get("track_uri") and doresume:
                print("Track URI is same, resuming playback")
                spotify_args["position_ms"] = self.playback_cache.get("progress_ms")
        else:
            spotify_args["context_uri"] = uri
            if uri == self.playback_cache.get("context_uri") and doresume:
                if uri.startswith("spotify:artist:"):
                    print("Context URI is artist, unable to resume playback ")
                elif doresume:
                    print("Context URI is same, resuming playback")
                    spotify_args["offset"] = { "uri": self.playback_cache.get("track_uri") }
                    spotify_args["position_ms"] = self.playback_cache.get("progress_ms")

        default_device_name = self.default_device_name
        default_device_id = None
        device_active = False
        devices = self.sp.devices()
        for device in devices['devices']:
            if device['is_active']:
                device_active = True
        if not device_active:
            for device in devices['devices']:
                if device['name'] is not None and default_device_name is not None:
                    if device['name'].strip().lower() == default_device_name.strip().lower():
                        default_device_id = device['id']
        if default_device_id is not None:
            print("defaulting to device id")
            spotify_args["device_id"] = default_device_id

        print(f"Start playback args: {spotify_args}")
        # check here for a non none device option? or just let it error out?
        try:
            self.sp.start_playback(**spotify_args)
        except Exception as e:
            print(f"Failed to start playback: {e}")

    def pause(self):
        # check here for an active device? or just let is error out?
        try:
            self.sp.pause_playback()
        except Exception as e:
            print(f"Failed to pause playback: {e}")
        self.store_playback()

    def store_playback(self):
        playback = self.sp.current_playback()
        context = playback.get("context") or {}
        self.playback_cache = {
            "type": context.get("type"),
            "context_uri": context.get("uri"),
            "progress_ms": playback.get("progress_ms") or 0,
            "track_uri": playback.get("item", {}).get("uri"),
        }
        print(f"Stored playback: {self.playback_cache}")

class RecordPlayer:
    def __init__(self, spotify, rfid, hall_sensor):
        self.spotify = spotify
        self.rfid = rfid
        self.hall_sensor = hall_sensor
        self.last_rfid = None
        self.last_time_paused = None

    def update_on(self):
        print("triggered")
        rfid_id, URI = self.rfid.read()
        clean_uri = URI.strip().replace('\x00', '')
        print("read")
        self.last_rfid = URI
        doresume = False
        if self.last_time_paused:
            if datetime.now() - self.last_time_paused < timedelta(hours=1):
                doresume = True
        self.spotify.play(clean_uri, doresume)

    def update_off(self):
        self.last_time_paused = datetime.now()
        self.spotify.pause()

def main():
    print("Starting Record Player")
    spotify = SpotifyController()
    rfid = SimpleMFRC522()
    hall_sensor = DigitalInputDevice(HALL_SENSOR_PIN, pull_up=True, pin_factory=LGPIOFactory())

    player = RecordPlayer(
        spotify=spotify,
        rfid=rfid,
        hall_sensor=hall_sensor,
    )

    hall_sensor.when_activated = player.update_on
    hall_sensor.when_deactivated = player.update_off

    try:
        pause()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
