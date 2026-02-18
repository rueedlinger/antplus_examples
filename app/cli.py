import logging
from time import sleep
from app.ant import Metrics


def stream_metrics(filter_device_ids=None):
    """Stream metrics from sensors."""
    filter_device_ids = filter_device_ids or []

    metrics_collector = Metrics(filter_device_ids=filter_device_ids)
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


def get_device_filter():
    return [10936, 10937, 10938]  # Example device IDs to filter


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("app.ant").setLevel(logging.INFO)

    options = {
        "auto": lambda: stream_metrics(),
        "a": lambda: stream_metrics(),
        "custom": lambda: stream_metrics(get_device_filter()),
        "c": lambda: stream_metrics(get_device_filter()),
    }

    user_choice = (
        input(
            "\nSelect mode:\n"
            "  auto   - Auto detect sensors\n"
            "  custom - Use predefined sensors\n"
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
