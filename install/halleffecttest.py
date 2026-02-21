
import RPi.GPIO as GPIO
import time
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

HALL_SENSOR_PIN = 17

class HallEffectSensor:
    def __init__(self, hall_sensor):
        self.hall_sensor = hall_sensor

    def update(self):
        magnet_detected = self.hall_sensor.value
        if magnet_detected:
            print("Magnet detected → start")
        elif not magnet_detected:
            print("Magnet lost → stop")

def main():
    print("Starting Hall Effect Sensor Test")
    hall_sensor = DigitalInputDevice(HALL_SENSOR_PIN, pull_up=True, pin_factory=LGPIOFactory())

    player = HallEffectSensor(
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
