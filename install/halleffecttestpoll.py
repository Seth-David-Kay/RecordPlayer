
import time
from gpiozero import DigitalInputDevice
from gpiozero.pins.lgpio import LGPIOFactory

HALL_SENSOR_PIN = 17

class HallEffectSensor:
    def __init__(self, hall_sensor):
        self.hall_sensor = hall_sensor
        self.last_state = self.hall_sensor.value

    def update(self):
        current_state = self.hall_sensor.value
        if current_state != self.last_state:
            if current_state:
                print("Magnet detected → start")
            elif not current_state:
                print("Magnet lost → stop")
            self.last_state = current_state

def main():
    print("Starting Hall Effect Sensor Test (Poll Driven)")
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

if __name__ == "__main__":
    main()
