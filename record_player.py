import json
import os
import RPi.GPIO as GPIO
import sys
import time
import spotipy
from dotenv import load_dotenv
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from mfrc522 import SimpleMFRC522
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

HALL_SENSOR_PIN = 17
RFID_FILE = "rfid.json"

class SpotifyController:
    def __init__(self):
        self.init_spotify_client()
        self.init_rfid_map()
        self.playback_cache = {}

    def init_spotify_client(self):
        load_dotenv()

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

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

    def init_rfid_map(self):
        rfid_map = {}
        try:
            with open(RFID_FILE, 'r') as file:
                rfid_map = json.load(file)
            if not rfid_map:
                print("Warning: RFID map is empty.")
        except FileNotFoundError:
            print(f"Warning: RFID map file {RFID_FILE} not found.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        self.rfid_map = rfid_map

    def play(self, rfid_id):
        print(f"Starting playback")
        uri = self.rfid_map.get(str(rfid_id))
        if not uri:
            print(f"No Spotify URI mapped to RFID {rfid_id}")
            return

        spotify_args = {}
        if uri.startswith("spotify:track:"):
            spotify_args["uris"] = [uri]
            if uri == self.playback_cache.get("track_uri"):
                print("Track URI is same, resuming playback")
                spotify_args["position_ms"] = self.playback_cache.get("progress_ms")
        else:
            spotify_args["context_uri"] = uri
            if uri == self.playback_cache.get("context_uri"):
                if uri.startswith("spotify:artist:"):
                    print("Context URI is artist, unable to resume playback ")
                else:
                    print("Context URI is same, resuming playback")
                    spotify_args["offset"] = { "uri": self.playback_cache.get("track_uri") }
                    spotify_args["position_ms"] = self.playback_cache.get("progress_ms")
        print(f"Start playback args: {spotify_args}")
        try:
            self.sp.start_playback(**spotify_args)
        except Exception as e:
            print(f"Failed to start playback: {e}")

    def pause(self):
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

        self.current_rfid = None

    def update(self):
        magnet_detected = self.hall_sensor.value

        if magnet_detected:
            print("Magnet detected → start")
            self.motor.start()

        elif not magnet_detected:
            print("Magnet lost → stop")
            self.current_rfid = None
            self.spotify.pause()

        if self.spinning:
            rfid_id = self.rfid.read_id_no_block()
            if rfid_id and rfid_id != self.current_rfid:
                print(f"RFID changed: {rfid_id}")
                self.current_rfid = rfid_id
                self.spotify.play(rfid_id)

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

    try:
        while True:
            player.update()
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
