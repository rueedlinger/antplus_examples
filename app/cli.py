import logging
from time import sleep
from app.ant import Metrics, Sensor, SensorScanner, SensorType


def stream_metrics(selected_sensors=None):
    """Stream metrics from sensors."""
    selected_sensors = selected_sensors or []

    metrics_collector = Metrics(sensors=selected_sensors)
    metrics_collector.start()

    try:
        while True:
            print(f"Devices : {metrics_collector.get_devices()}")
            print(f"Metrics : {metrics_collector.get_metrics()}")
            sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        metrics_collector.stop()


def scan_available_sensors():
    """Continuously scan for available sensors."""
    scanner = SensorScanner()
    scanner.start()

    try:
        while True:
            print(f"Devices : {scanner.get_devices()}")
            sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        scanner.stop()


def get_custom_sensors():
    """Return predefined custom sensor configuration."""
    return [
        Sensor(device_id=10936, sensor_type=SensorType.POWER_METER),
        Sensor(device_id=10936, sensor_type=SensorType.BIKE_SPEED_CADENCE),
        Sensor(device_id=59241, sensor_type=SensorType.HEART_RATE),
    ]


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("app.ant").setLevel(logging.INFO)

    options = {
        "auto": lambda: stream_metrics(),
        "a": lambda: stream_metrics(),
        "custom": lambda: stream_metrics(get_custom_sensors()),
        "c": lambda: stream_metrics(get_custom_sensors()),
        "list": scan_available_sensors,
        "l": scan_available_sensors,
    }

    user_choice = (
        input(
            "\nSelect mode:\n"
            "  auto   - Auto detect sensors\n"
            "  custom - Use predefined sensors\n"
            "  list   - List available sensors\n"
            "\nEnter choice: "
        )
        .lower()
        .strip()
    )

    action = options.get(user_choice)

    if action:
        action()
    else:
        print("Invalid option.")
