import os
import RPi.GPIO as GPIO
import sys
from signal import pause
import spotipy
from dotenv import load_dotenv
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory
from mfrc522 import SimpleMFRC522
from soco import SoCo

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

    def play(self, uri):
        print(f"Starting playback")
        if not uri:
            print(f"No uri scanned or passed in")
            return
        try:
            self.sonos.play_uri(uri)
        except Exception as e:
            print(f"Sonos playback failed: {e}")

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

    def update_on(self):
        print("triggered")
        rfid_id, URI = self.rfid.read()
        clean_uri = URI.strip().replace('\x00', '')
        print("read")
        self.spotify.play(clean_uri)

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
