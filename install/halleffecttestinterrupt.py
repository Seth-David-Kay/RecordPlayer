from signal import pause # Keeps the program running
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

HALL_SENSOR_PIN = 17

def magnet_found():
    print("Magnet detected → start")

def magnet_lost():
    print("Magnet lost → stop")

def main():
    print("Starting Hall Effect Sensor Test (Interrupt Driven)")
    # pull_up=True means the pin is HIGH by default.
    # Most Hall sensors pull to GND (LOW) when a magnet is present.
    hall_sensor = DigitalInputDevice(HALL_SENSOR_PIN, pull_up=True, pin_factory=LGPIOFactory())

    # Assign functions to the events
    hall_sensor.when_activated = magnet_found
    hall_sensor.when_deactivated = magnet_lost

    try:
        pause() # This replaces the while loop; it just waits for events
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
