import logging
from time import sleep
from app.ant import Metrics, Sensor, SensorScanner, SensorType


def metrics(sensors=[]):
    m = Metrics(sensors=sensors)
    m.start()
    try:
        while True:
            # m.display()
            print(f" devices: {m.get_devices()}")
            print(f" metrics: {m.get_metrics()}")
            sleep(0.5)
    except KeyboardInterrupt:
        m.stop()


def list_sensors():
    m = SensorScanner()
    m.start()
    try:
        while True:
            print(f" devices: {m.get_devices()}")
            sleep(0.5)
    except KeyboardInterrupt:
        m.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("app.ant").setLevel(logging.INFO)

    option = (
        input("Enter option (a: auto detect, c: custom, l: list): ").lower().strip()
    )
    if option == "a":
        metrics()
    elif option == "c":
        sensors = [
            Sensor(device_id=10936, sensor_type=SensorType.POWER_METER),
            Sensor(device_id=10936, sensor_type=SensorType.BIKE_SPEED_CADENCE),
            Sensor(device_id=59241, sensor_type=SensorType.HEART_RATE),
        ]
        metrics(sensors=sensors)
    elif option == "l":
        list_sensors()
