import logging
from time import sleep
from app.ant import Metrics, Sensor, SensorType


def metrics(sensors=[]):
    m = Metrics(sensors=sensors)
    m.start()
    try:
        while True:
            m.display()
            sleep(0.1)
    except KeyboardInterrupt:
        m.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    option = input("Enter option (a: auto, c: custom, l: list): ").lower().strip()
    if option == "a":
        metrics()
    elif option == "c":
        sensors = [
            Sensor(device_id=59241, sensor_type=SensorType.HEART_RATE),
        ]
        metrics(sensors=sensors)
    elif option == "l":
        pass
