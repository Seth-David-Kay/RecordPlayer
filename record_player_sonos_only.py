import sys
import os
from datetime import datetime, timedelta
import RPi.GPIO as GPIO
from signal import pause
from dotenv import load_dotenv
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from mfrc522 import SimpleMFRC522
from soco import SoCo
import spotipy
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth

HALL_SENSOR_PIN = 17

class SpotifyController:
    def __init__(self):
        self.default_device_id = None
        self.sonos = None
        self.init_spotify_client()
        self.playback_cache = {}

    def init_spotify_client(self):
        load_dotenv()

        self.default_device_id = os.getenv("DEFAULT_DEVICE_ID")
        sonos_ip = os.getenv("SONOS_DEVICE_IP")
        self.sonos = SoCo(sonos_ip)

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

    def play(self, uri, doresume):
        print("Starting playback")
        if doresume:
            self.sonos.play()
        if not uri:
            print("No uri scanned or passed in")
            return

        if "album" in uri:
            results = self.sp.album_tracks(uri, limit=50)
            tracks = []
            while results:
                tracks.extend(results['items'])
                if results['next']:
                    results = self.sp.next(results)
                else:
                    results = None
            self.sonos.clear_queue()
            try:
                for track in tracks:
                    self.sonos.add_uri_to_queue(f"x-sonos-spotify:{track['uri']}?sid=12&flags=32")
                self.sonos.play_from_queue(index=0)
            except Exception as e:
                print(f"Sonos playback failed: {e}")

        if "track" in uri:
            try:
                self.sonos.play_uri(f"x-sonos-spotify:{uri}?sid=12&flags=32")
            except Exception as e:
                print(f"Sonos playback failed: {e}")

        if "playlist" in uri:
            print("not implemented yet")

    def pause(self):
        try:
            self.sonos.pause()
        except Exception as e:
            print(f"Failed to pause playback: {e}")

class RecordPlayer:
    def __init__(self, spotify, rfid, hall_sensor):
        self.spotify = spotify
        self.rfid = rfid
        self.hall_sensor = hall_sensor
        self.last_rfid_id = None
        self.last_time_paused = None

    def update_on(self):
        print("triggered")
        rfid_id, URI = self.rfid.read()
        clean_uri = URI.strip().replace('\x00', '')
        print("read")
        doresume = False
        if self.last_time_paused and self.last_rfid_id:
            if datetime.now() - self.last_time_paused < timedelta(hours=1):
                if (rfid_id == self.last_rfid_id):
                    doresume = True
        self.spotify.play(clean_uri, doresume)
        self.last_rfid_id = rfid_id
        self.last_time_paused = datetime.now()

    def update_off(self):
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
