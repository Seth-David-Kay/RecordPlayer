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
        self.default_device_id = None
        self.init_spotify_client()

    def init_spotify_client(self):
        load_dotenv()

        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")
        self.default_device_id = os.getenv("DEFAULT_DEVICE_ID")

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
        if not uri:
            return
        spotify_args = {}
        spotify_args["device_id"] = self.default_device_id
        if uri.startswith("spotify:track:"):
            spotify_args['uris'] = [uri]
        else:
            spotify_args['context_uri'] = uri
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

class RecordPlayer:
    def __init__(self, spotify, rfid, hall_sensor):
        self.spotify = spotify
        self.rfid = rfid
        self.hall_sensor = hall_sensor
        self.last_rfid = None
        self.last_time_paused = None

    def update_on(self):
        rfid_id, URI = self.rfid.read()
        clean_uri = URI.strip().replace('\x00', '')
        doresume = False
        if self.last_rfid == URI:
            if self.last_time_paused:
                if datetime.now() - self.last_time_paused < timedelta(minutes=5):
                    doresume = True
        self.spotify.play(clean_uri, doresume)
        self.last_rfid = URI

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
